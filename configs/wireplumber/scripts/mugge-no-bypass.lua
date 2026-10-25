-- mugge-no-bypass.lua — F-318: WirePlumber never auto-links playback
--
-- Non-JACK clients (pw-play, pulse apps, browsers, pw-loopback) arrive as
-- autoconnect streams. Stock WirePlumber links them to the default sink,
-- which on this system is the USBStreamer: the stream then bypasses the
-- convolver, the D-063 gains and the gate. GraphManager owns every link to
-- the USBStreamer and the convolver; WirePlumber must not create any.
--
-- Policy (fail closed, F-318 option A):
--   1. No playback stream is ever linked by WirePlumber, whatever its
--      target. Only subjects whose media.class starts with "Stream/Input/"
--      (capture, including sink-monitor capture) are left to the stock
--      policy. A missing or unknown media.class is denied.
--   2. The USBStreamer and the convolver are never chosen as
--      default.audio.sink, so "the default sink" never names them, even if
--      default.configured.audio.sink does. The default source is untouched.
--
-- Hooks, all in the select-target / select-default-node chains of
-- WirePlumber 0.5.12:
--   linking/mugge-deny-playback        after every target finder, before
--                                      prepare-link. Clears the target and
--                                      removes earlier WirePlumber links;
--                                      prepare-link then sends the client
--                                      "no target node available".
--   linking/mugge-deny-playback-final  after prepare-link, before
--                                      link-target. Same predicate; fires
--                                      only if a hook ran after the first
--                                      one, and logs that as an error.
--   default-nodes/mugge-exclude-protected-sinks
--                                      before the default-sink finders.
--                                      Drops protected nodes from the
--                                      candidates.
--
-- Links made by GraphManager (pw-link / link-factory) are not WirePlumber
-- session items and are never touched here.
--
-- Loaded by: 55-mugge-no-bypass.conf (required).

local log = Log.open_topic ("s-mugge-no-bypass")

local USBSTREAMER_NODE = "alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0"
local USBSTREAMER_GROUP = "pi4audio.usbstreamer"
local CONVOLVER_NODE = "pi4audio-convolver"

-- True for the USBStreamer playback node and the convolver. Matched by
-- name, ALSA path and node group, never by id, so a re-enumerated device
-- stays protected.
local function isProtected (props)
  local name = props ["node.name"] or ""
  local lname = string.lower (name)
  if name == USBSTREAMER_NODE or name == CONVOLVER_NODE then
    return true
  end
  if string.find (lname, "^alsa_output%.usb%-minidsp.*usbstreamer") then
    return true
  end
  local path = string.lower (props ["api.alsa.path"] or "")
  if string.find (path, "usbstreamer", 1, true) then
    return true
  end
  return props ["node.group"] == USBSTREAMER_GROUP
end

-- Capture subjects are the only ones the stock policy may still link.
local function isExempt (si_props)
  local mclass = si_props ["media.class"]
  return type (mclass) == "string" and
      string.find (mclass, "^Stream/Input/") ~= nil
end

-- Deny log lines, once per stream item and target.
local logged = {}

-- Properties of the client that owns the stream. Stream nodes carry
-- application.name but usually not the process binary or pid; those are
-- on the client. pipewire.sec.pid comes from the socket credentials, the
-- application.* ones are what the client claims.
local function clientProps (source, si_props)
  local client_id = si_props ["client.id"]
  if not client_id then
    return {}
  end
  local clients_om = source:call ("get-object-manager", "client")
  local client = clients_om:lookup {
      Constraint { "bound-id", "=", client_id, type = "gobject" }
  }
  return client and client.properties or {}
end

local function logDeny (source, si, si_props, target, final)
  local tname = target and target.properties ["node.name"] or nil
  local key = tostring (si.id) .. "\0" .. tostring (tname)
  if logged [key] and not final then
    return
  end
  logged [key] = true
  local cprops = clientProps (source, si_props)
  local function prop (k)
    return tostring (si_props [k] or cprops [k])
  end
  local msg = string.format (
      "F-318: denied auto-link of stream node.id=%q node.name=%q "
      .. "application.name=%q application.process.binary=%q "
      .. "application.process.id=%q pipewire.sec.pid=%q "
      .. "to target node.name=%q",
      prop ("node.id"), prop ("node.name"), prop ("application.name"),
      prop ("application.process.binary"), prop ("application.process.id"),
      tostring (cprops ["pipewire.sec.pid"]), tostring (tname))
  if final then
    log:error (si, "final guard fired, a hook ran after "
        .. "linking/mugge-deny-playback: " .. msg)
  else
    log:warning (si, msg)
  end
end

-- Removes every WirePlumber link of this item and clears its peer.
local function removeLinks (om, si)
  for silink in om:iterate { type = "SiLink" } do
    local out_id = tonumber (silink.properties ["out.item.id"])
    local in_id = tonumber (silink.properties ["in.item.id"])
    if out_id == si.id or in_id == si.id then
      log:warning (silink, string.format (
          "F-318: removing WirePlumber link of item %d", si.id))
      silink:remove ()
    end
  end
  local lutils = require ("linking-utils")
  lutils:get_flags (si.id).peer_id = nil
end

local function denyPlayback (event, final)
  local source = event:get_source ()
  local si = event:get_subject ()
  local si_props = si.properties
  if isExempt (si_props) then
    return
  end
  -- One line per run of the gate, never deduplicated. The hook-order
  -- check in tests/service-integration/wp-f318 matches on it.
  if not final then
    log:info (si, string.format (
        "F-318: mugge-deny-playback: denied item %d node.name=%q node.id=%q",
        si.id, tostring (si_props ["node.name"]),
        tostring (si_props ["node.id"])))
  end
  local target = event:get_data ("target")
  if target or not final then
    local om = source:call ("get-object-manager", "session-item")
    removeLinks (om, si)
  end
  if target then
    logDeny (source, si, si_props, target, final)
  end
  event:set_data ("target", nil)
end

SimpleEventHook {
  name = "linking/mugge-deny-playback",
  after = { "linking/find-defined-target",
            "linking/find-audio-group-target",
            "linking/find-filter-target",
            "linking/find-media-role-target",
            "linking/find-default-target",
            "linking/find-best-target",
            "linking/get-filter-from-target" },
  before = "linking/prepare-link",
  interests = {
    EventInterest {
      Constraint { "event.type", "=", "select-target" },
    },
  },
  execute = function (event)
    denyPlayback (event, false)
  end
}:register ()

SimpleEventHook {
  name = "linking/mugge-deny-playback-final",
  after = "linking/prepare-link",
  before = "linking/link-target",
  interests = {
    EventInterest {
      Constraint { "event.type", "=", "select-target" },
    },
  },
  execute = function (event)
    denyPlayback (event, true)
  end
}:register ()

SimpleEventHook {
  name = "default-nodes/mugge-exclude-protected-sinks",
  before = { "default-nodes/find-selected-default-node",
             "default-nodes/find-stored-default-node",
             "default-nodes/find-best-default-node" },
  interests = {
    EventInterest {
      Constraint { "event.type", "=", "select-default-node" },
      Constraint { "default-node.type", "=", "audio.sink" },
    },
  },
  execute = function (event)
    local available = event:get_data ("available-nodes")
    available = available and available:parse ()
    if not available then
      return
    end
    local kept = {}
    for _, props in ipairs (available) do
      if isProtected (props) then
        log:info (string.format (
            "F-318: %q is not eligible as default.audio.sink",
            tostring (props ["node.name"])))
      else
        table.insert (kept, Json.Object (props))
      end
    end
    event:set_data ("available-nodes", Json.Array (kept))
  end
}:register ()

SimpleEventHook {
  name = "linking/mugge-forget-removed-item",
  interests = {
    EventInterest {
      Constraint { "event.type", "=", "session-item-removed" },
      Constraint { "event.session-item.interface", "=", "linkable" },
    },
  },
  execute = function (event)
    local prefix = tostring (event:get_subject ().id) .. "\0"
    for key in pairs (logged) do
      if string.sub (key, 1, #prefix) == prefix then
        logged [key] = nil
      end
    end
  end
}:register ()

log:notice ("F-318: mugge-no-bypass loaded, WirePlumber will not "
    .. "auto-link playback streams")
