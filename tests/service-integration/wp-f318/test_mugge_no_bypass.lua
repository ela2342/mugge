-- Unit tests for configs/wireplumber/scripts/mugge-no-bypass.lua (F-318).
--
-- Loads the script with stubs shaped like the WirePlumber 0.5.12 Lua API
-- (SimpleEventHook, EventInterest/Constraint, Log topics, Json, events
-- with get_source/get_subject/get_data/set_data, session-item object
-- manager with iterate) and asserts on what the hooks do: the target left
-- in the event, removed links, cleared peers, log lines and the filtered
-- default-sink candidates.
--
-- Usage: lua test_mugge_no_bypass.lua <path to mugge-no-bypass.lua>
-- Exit status 0 if all tests pass.

local script_path = assert (arg [1], "usage: lua test_mugge_no_bypass.lua <script>")

-- -- stubs -------------------------------------------------------------

local hooks, logs, flags, clients

local function reset ()
  hooks, logs, flags, clients = {}, {}, {}, {}
end

local topic = {}
for _, level in ipairs { "error", "warning", "notice", "info", "debug" } do
  topic [level] = function (_, a, b)
    table.insert (logs, { level = level, msg = b or a })
  end
end

local function install_stubs ()
  Log = { open_topic = function () return topic end }
  Constraint = function (t) return { constraint = t } end
  EventInterest = function (t) return { interest = t } end
  SimpleEventHook = function (def)
    return { register = function () hooks [def.name] = def end }
  end
  -- Json.Object wraps a table; Json.Array:parse() unwraps it again, as
  -- WpSpaJson:parse() returns plain Lua tables.
  Json = {
    Object = function (t) return { json_object = t } end,
    Array = function (list)
      return {
        parse = function ()
          local out = {}
          for i, v in ipairs (list) do out [i] = v.json_object or v end
          return out
        end,
        list = list,
      }
    end,
  }
  package.loaded ["linking-utils"] = {
    get_flags = function (_, id)
      flags [id] = flags [id] or {}
      return flags [id]
    end,
  }
end

local function load_script ()
  reset ()
  install_stubs ()
  dofile (script_path)
end

local function new_link (out_id, in_id)
  local l = { properties = { ["out.item.id"] = tostring (out_id),
                             ["in.item.id"] = tostring (in_id) } }
  l.remove = function (self) self.removed = true end
  return l
end

local function select_target_event (si_props, target_props, links)
  local data = {}
  if target_props then
    data.target = { id = 99, properties = target_props }
  end
  local om = {
    iterate = function (_, interest)
      assert (interest.type == "SiLink", "unexpected iterate " .. tostring (interest.type))
      local i = 0
      return function ()
        i = i + 1
        return links [i]
      end
    end,
  }
  local clients_om = {
    lookup = function (_, interest)
      local c = interest [1].constraint
      assert (c [1] == "bound-id" and c [2] == "=" and c.type == "gobject")
      local props = clients [tonumber (c [3])]
      return props and { properties = props } or nil
    end,
  }
  local si = { id = 7, properties = si_props }
  return {
    data = data,
    si = si,
    get_source = function ()
      return { call = function (_, what, kind)
        assert (what == "get-object-manager")
        if kind == "client" then
          return clients_om
        end
        assert (kind == "session-item", "unexpected object manager " .. kind)
        return om
      end }
    end,
    get_subject = function () return si end,
    get_data = function (self, k) return self.data [k] end,
    set_data = function (self, k, v) self.data [k] = v end,
  }
end

local function default_node_event (candidates)
  local wrapped = {}
  for i, p in ipairs (candidates) do wrapped [i] = Json.Object (p) end
  return {
    data = { ["available-nodes"] = Json.Array (wrapped) },
    get_data = function (self, k) return self.data [k] end,
    set_data = function (self, k, v) self.data [k] = v end,
  }
end

local function count_logs (level, pattern)
  local n = 0
  for _, l in ipairs (logs) do
    if l.level == level and string.find (l.msg, pattern, 1, true) then
      n = n + 1
    end
  end
  return n
end

local PLAY = {
  ["media.class"] = "Stream/Output/Audio",
  ["node.id"] = "42",
  ["node.name"] = "browser-tab",
  ["application.name"] = "Firefox",
  ["application.process.binary"] = "firefox",
  ["application.process.id"] = "1234",
}
local USB = { ["node.name"] = "alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0" }

local function copy (t, extra)
  local c = {}
  for k, v in pairs (t) do c [k] = v end
  for k, v in pairs (extra or {}) do c [k] = v end
  return c
end

local function run_deny (si_props, target_props, links, final)
  local ev = select_target_event (si_props, target_props, links or {})
  local name = final and "linking/mugge-deny-playback-final"
      or "linking/mugge-deny-playback"
  hooks [name].execute (ev)
  return ev
end

-- -- tests -------------------------------------------------------------

local tests = {}
local function test (name, fn) table.insert (tests, { name = name, fn = fn }) end

test ("load line is logged at notice level", function ()
  load_script ()
  assert (count_logs ("notice", "F-318: mugge-no-bypass loaded") == 1)
end)

test ("deny hook runs after every finder and before prepare-link", function ()
  load_script ()
  local h = hooks ["linking/mugge-deny-playback"]
  assert (h, "hook not registered")
  assert (h.before == "linking/prepare-link")
  local after = {}
  for _, a in ipairs (h.after) do after [a] = true end
  for _, f in ipairs { "linking/find-defined-target",
      "linking/find-audio-group-target", "linking/find-filter-target",
      "linking/find-media-role-target", "linking/find-default-target",
      "linking/find-best-target", "linking/get-filter-from-target" } do
    assert (after [f], "missing after " .. f)
  end
  assert (h.interests [1].interest [1].constraint [3] == "select-target")
end)

test ("final guard sits between prepare-link and link-target", function ()
  load_script ()
  local h = hooks ["linking/mugge-deny-playback-final"]
  assert (h.after == "linking/prepare-link")
  assert (h.before == "linking/link-target")
end)

test ("default-sink filter runs before all default-sink finders", function ()
  load_script ()
  local h = hooks ["default-nodes/mugge-exclude-protected-sinks"]
  local before = {}
  for _, b in ipairs (h.before) do before [b] = true end
  assert (before ["default-nodes/find-selected-default-node"])
  assert (before ["default-nodes/find-stored-default-node"])
  assert (before ["default-nodes/find-best-default-node"])
  local c = h.interests [1].interest
  assert (c [2].constraint [1] == "default-node.type"
      and c [2].constraint [3] == "audio.sink",
      "must only touch the default sink, not the source")
end)

test ("playback to the USBStreamer is denied and logged with all fields", function ()
  load_script ()
  local ev = run_deny (PLAY, USB)
  assert (ev.data.target == nil, "target not cleared")
  assert (count_logs ("warning", "F-318: denied auto-link") == 1)
  local msg = logs [#logs].msg
  for _, s in ipairs { 'node.id="42"', 'node.name="browser-tab"',
      'application.name="Firefox"', 'application.process.binary="firefox"',
      'application.process.id="1234"',
      'to target node.name="alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0"' } do
    assert (string.find (msg, s, 1, true), "deny line lacks " .. s .. ": " .. msg)
  end
end)

test ("deny line takes binary and pids from the owning client", function ()
  load_script ()
  clients [31] = { ["application.process.binary"] = "pw-play",
                   ["application.process.id"] = "555",
                   ["pipewire.sec.pid"] = "556" }
  local props = { ["media.class"] = "Stream/Output/Audio", ["node.id"] = "58",
                  ["node.name"] = "f318-play", ["application.name"] = "pw-play",
                  ["client.id"] = "31" }
  run_deny (props, USB)
  local msg = logs [#logs].msg
  for _, s in ipairs { 'application.process.binary="pw-play"',
      'application.process.id="555"', 'pipewire.sec.pid="556"' } do
    assert (string.find (msg, s, 1, true), "deny line lacks " .. s .. ": " .. msg)
  end
end)

test ("deny line without a known client still names the stream", function ()
  load_script ()
  run_deny (copy (PLAY, { ["client.id"] = "99" }), USB)
  local msg = logs [#logs].msg
  assert (string.find (msg, 'application.process.binary="firefox"', 1, true))
  assert (string.find (msg, 'pipewire.sec.pid="nil"', 1, true), msg)
end)

test ("playback to any other target is denied too", function ()
  load_script ()
  for _, name in ipairs { "pi4audio-convolver", "auto_null", "some-sink" } do
    local ev = run_deny (PLAY, { ["node.name"] = name })
    assert (ev.data.target == nil, "target " .. name .. " not cleared")
  end
end)

test ("missing or non-capture media.class is denied", function ()
  load_script ()
  for _, mc in ipairs { false, "Stream/Output/Audio", "Audio/Sink",
      "Stream/Duplex/Audio", "Stream/Inputs/Audio", "stream/input/audio" } do
    local props = copy (PLAY)
    props ["media.class"] = mc or nil
    local ev = run_deny (props, USB)
    assert (ev.data.target == nil, "not denied: " .. tostring (mc))
  end
end)

test ("capture streams keep their target and their links", function ()
  load_script ()
  for _, mc in ipairs { "Stream/Input/Audio", "Stream/Input/Video" } do
    local link = new_link (99, 7)
    local ev = run_deny (copy (PLAY, { ["media.class"] = mc }), USB, { link })
    assert (ev.data.target and ev.data.target.properties == USB,
        "capture target cleared for " .. mc)
    assert (not link.removed, "capture link removed for " .. mc)
  end
  assert (count_logs ("warning", "denied") == 0)
end)

test ("existing WirePlumber links of a denied stream are removed", function ()
  load_script ()
  local mine_out = new_link (7, 99)
  local mine_in = new_link (99, 7)
  local other = new_link (3, 99)
  flags [7] = { peer_id = 99 }
  run_deny (PLAY, USB, { mine_out, other, mine_in })
  assert (mine_out.removed and mine_in.removed, "own links not removed")
  assert (not other.removed, "foreign link removed")
  assert (flags [7].peer_id == nil, "peer_id not cleared")
end)

test ("links are removed even when no target was found", function ()
  load_script ()
  local link = new_link (7, 99)
  local ev = run_deny (PLAY, nil, { link })
  assert (link.removed)
  assert (ev.data.target == nil)
  assert (count_logs ("warning", "denied") == 0, "deny logged without target")
end)

test ("deny line is logged once per stream and target", function ()
  load_script ()
  run_deny (PLAY, USB)
  run_deny (PLAY, USB)
  assert (count_logs ("warning", "denied") == 1)
  run_deny (PLAY, { ["node.name"] = "pi4audio-convolver" })
  assert (count_logs ("warning", "denied") == 2, "new target not logged")
end)

test ("removing the stream item resets the dedupe", function ()
  load_script ()
  run_deny (PLAY, USB)
  hooks ["linking/mugge-forget-removed-item"].execute {
    get_subject = function () return { id = 7 } end }
  run_deny (PLAY, USB)
  assert (count_logs ("warning", "denied") == 2)
end)

test ("final guard clears a late target and logs an error", function ()
  load_script ()
  local link = new_link (7, 99)
  local ev = run_deny (PLAY, USB, { link }, true)
  assert (ev.data.target == nil)
  assert (link.removed)
  assert (count_logs ("error", "final guard fired") == 1)
  run_deny (PLAY, USB, {}, true)
  assert (count_logs ("error", "final guard fired") == 2,
      "final guard must not be deduplicated")
end)

test ("final guard is silent without a target", function ()
  load_script ()
  local link = new_link (7, 99)
  run_deny (PLAY, nil, { link }, true)
  assert (#logs == 1, "unexpected log")  -- the load line only
  assert (not link.removed)
end)

test ("protected nodes are dropped from default-sink candidates", function ()
  load_script ()
  local ev = default_node_event {
    { ["node.name"] = "alsa_output.usb-MiniDSP_USBStreamer-00.pro-output-0" },
    { ["node.name"] = "alsa_output.usb-miniDSP_USBStreamer_B-01.pro-output-0" },
    { ["node.name"] = "something", ["api.alsa.path"] = "hw:USBStreamer,0" },
    { ["node.name"] = "grouped", ["node.group"] = "pi4audio.usbstreamer" },
    { ["node.name"] = "pi4audio-convolver" },
    { ["node.name"] = "auto_null" },
    { ["node.name"] = "alsa_output.platform-hdmi" , ["api.alsa.path"] = "hw:vc4hdmi0" },
  }
  hooks ["default-nodes/mugge-exclude-protected-sinks"].execute (ev)
  local kept = ev.data ["available-nodes"]:parse ()
  local names = {}
  for _, p in ipairs (kept) do table.insert (names, p ["node.name"]) end
  assert (#kept == 2, "kept: " .. table.concat (names, ","))
  assert (names [1] == "auto_null" and names [2] == "alsa_output.platform-hdmi")
  assert (count_logs ("info", "is not eligible as default.audio.sink") == 5)
end)

test ("default-sink filter leaves the event alone without candidates", function ()
  load_script ()
  local ev = { data = {}, get_data = function (self, k) return self.data [k] end,
               set_data = function () error ("must not set data") end }
  hooks ["default-nodes/mugge-exclude-protected-sinks"].execute (ev)
end)

-- -- runner ------------------------------------------------------------

local passed, failed = 0, 0
for _, t in ipairs (tests) do
  local ok, err = pcall (t.fn)
  if ok then
    passed = passed + 1
    print ("PASS " .. t.name)
  else
    failed = failed + 1
    print ("FAIL " .. t.name .. ": " .. tostring (err))
  end
end
print (string.format ("RESULT lua unit: %d passed, %d failed, of %d",
    passed, failed, passed + failed))
os.exit (failed == 0 and 0 or 1)
