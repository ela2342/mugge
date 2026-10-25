# US-163: Pi 5 NixOS Bootstrap

Lab notes for bringing the Pi 5 (hostname `mugge`, 192.168.178.89) up on
NixOS from the `mugge-pi5-deploy` configuration. Raw evidence stays in the
operator's private evidence directory (not in the repo); this note carries
excerpts only. Identity data is limited to fingerprints and the MAC address.

Times marked `Z` or `UTC` are UTC. Journal timestamps (`Oct 25 hh:mm:ss`)
are the Pi's local time, CET (UTC+1): daylight saving time ended on
2026-10-25 at 01:00 UTC, before any of the work below.

## Reproducibility

| Role | Path |
|------|------|
| Configuration | `.#nixosConfigurations.mugge-pi5-deploy` |
| Eval-only guard | `nix build --no-link 'path:.#checks.aarch64-darwin.board-guard'` |
| Raw data | operator's private evidence directory (not committed) |

---

## Task F-358 / F-367: Direct RT scheduling and headless boot (CM-DEP-.89-2)

**Date:** 2026-10-25 08:47-09:03 UTC
**Operator:** Claude (worker-1, under change-manager session CM-DEP-.89-2)
**Host:** mugge (Pi 5), NixOS 25.11.20260320.812b398, kernel 6.12.62 PREEMPT_RT, aarch64

Deployed commits `f87c162b..132997f9` of `story/US-163-pi5-nixos-bootstrap`:

- F-367 (`f87c162b`): skip greetd when there is no DRM card
  (`ConditionPathExistsGlob = "/dev/dri/card*"`), and enable linger for ela
  so the user manager (PipeWire, GraphManager) starts at boot without a
  login.
- F-358 (`c1ff084c`, `132997f9`): `configs/pipewire/05-rt-direct.conf`
  overrides the stock module-rt args with `module.rt.args`.

### Pre-conditions

- Previous system: `x83m7bircd4b7j8wchx9k1mnilzi8kl4` (booted, boot_id `bc3ffb75-…`)
- Before F-358: user@1000 has `LimitNICE=0`, so the stock `nice.level = -11`
  failed with EPERM ("mod.rt: could not set nice-level to -11: Permission
  denied"). module-rt then fell back to RTKit, and the data loop ran at
  SCHED_RR 20 instead of FIFO 88.
- Nothing connected to any Pi output (owner); amps, HP and IEM off.
- Mac: 12 GiB free; kernel unchanged, so only configs and toplevel rebuilt.

### Effective module-rt args

PipeWire 1.6.2 `module_init` calls
`pw_context_conf_update_props(context, "module.rt.args", props)`, which goes
through `pw_properties_update_string` and overwrites only the keys given.
The stock entry keeps its place in `context.modules`, and exactly one
module-rt loads.

| Key | Value | Source |
|-----|-------|--------|
| nice.level | 20 (out of range, set_nice skipped) | 05-rt-direct.conf |
| rt.prio | 88 | 05-rt-direct.conf |
| rt.time.soft / rt.time.hard | 200000 us | 05-rt-direct.conf |
| rtkit.enabled / rtportal.enabled | false | 05-rt-direct.conf |
| uclamp.min / uclamp.max | 0 / 1024 | module default |
| rlimits.enabled | true | module default |

`rt.time` must be explicit: the module default of -1 is stored as
`RLIM_INFINITY`, and with RTKit off `set_rlimit()` applies it, which would
remove the kernel's 200 ms kill of a runaway FIFO 88 loop.

### Procedure

```bash
# Step 1: deploy (from the Mac, clean tree at 132997f9, run detached)
$ export NIX_SSHOPTS="-o UserKnownHostsFile=<pinned known_hosts> -o StrictHostKeyChecking=yes -o BatchMode=yes -o ForwardAgent=no"
$ <nixos-rebuild-ng 26.11 store path>/bin/nixos-rebuild boot --no-reexec \
    --flake .#mugge-pi5-deploy --target-host ela@192.168.178.89 --sudo -v
Done. The new configuration is /nix/store/nkifli3rxayxxmrndqw3a3ic0jj5fix8-nixos-system-mugge-25.11.20260320.812b398
RC=0
```

The darwin `nixpkgs#nixos-rebuild-ng` 26.11 package ships its binary as
`nixos-rebuild`, not `nixos-rebuild-ng`. The first run failed with "unable
to execute 'nixos-rebuild-ng'" before reaching the Pi. `--no-reexec` is
still required: without it the tool re-execs into the target's aarch64
binary on the Mac.

The ng debug log does not print the ssh wrapper around the profile and
switch steps, so both sides were checked:

```bash
# Mac: system profile untouched
$ ls -la /nix/var/nix/profiles/ | grep 'system ->'
system -> system-150-link            # darwin-system, unchanged
# Pi: new profile and switch-to-configuration boot ran there
$ readlink -f /nix/var/nix/profiles/system
/nix/store/nkifli3rxayxxmrndqw3a3ic0jj5fix8-nixos-system-mugge-25.11.20260320.812b398
$ journalctl -b -u nixos-rebuild-switch-to-configuration | tail -2   # local CET
Oct 25 09:50:05 mugge systemd[1]: nixos-rebuild-switch-to-configuration.service: Deactivated successfully.
```

```bash
# Step 2: record the recovery line before the reboot
$ grep -n os_prefix /boot/firmware/config.txt
16:os_prefix=gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/
$ cat /boot/firmware/gens/MAP.txt
1 p9mzphhydmf7p1kjqjkc76dvcij2y99i pruned
2 x83m7bircd4b7j8wchx9k1mnilzi8kl4 present
3 nkifli3rxayxxmrndqw3a3ic0jj5fix8 present
```

Recovery via card reader: set line 16 to
`os_prefix=gens/x83m7bircd4b7j8wchx9k1mnilzi8kl4/`, the generation booted
before this deploy (corrected in #50: originally said `nkifli3r…`, which
was the generation just deployed). For the current
generations and recovery line, see "FAT generations" below.

```bash
# Step 3: one announced reboot (warm, not a power cycle)
$ sudo systemctl reboot          # 08:51:50Z, back after 20 s
$ cat /proc/sys/kernel/random/boot_id
1531f01f-e66f-4f6f-9b15-a5e9c362ee10
```

```bash
# Step 4: F-358 after boot
$ ps -L -o pid,tid,cls,rtprio,pri,ni,comm -p 772
    PID     TID CLS RTPRIO PRI  NI COMMAND
    772     772  FF     88 128   - pipewire
    772     778  FF     88 128   - data-loop.0
$ grep -iE 'realtime|nice|locked' /proc/772/limits
Max locked memory         unlimited            unlimited            bytes
Max nice priority         0                    0
Max realtime priority     95                   95
Max realtime timeout      200000               200000               us
$ pw-cli ls Module | grep -c libpipewire-module-rt
1
$ pw-cli info 1        # module-rt; the args string shows the stock text,
                       # the properties show the merged values
*		nice.level = "20"
*		rt.prio = "88"
*		rt.time.soft = "200000"
*		rt.time.hard = "200000"
*		rtkit.enabled = "false"
*		rtportal.enabled = "false"
$ systemctl --user show pipewire -p NRestarts -p ExecMainStatus -p Result
Result=success
NRestarts=0
ExecMainStatus=0
```

```bash
# Step 5: one announced PipeWire restart, then the same set
$ systemctl --user restart pipewire        # 08:56:26Z
$ ps -L -o pid,tid,cls,rtprio,pri,ni,comm -p 1165
   1165    1165  FF     88 128   - pipewire
   1165    1172  FF     88 128   - data-loop.0
# limits, module count and merged props identical to step 4; NRestarts=0
```

### Validation

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Booted system (T51) | current = booted = built | all `nkifli3r…` | PASS |
| Store integrity (T51) | `nix store verify -r --no-trust` clean | 958 paths, RC=0 | PASS |
| Identity | host key and MAC unchanged | ED25519 `SHA256:a5kILUyr7XhT3D5Vdm4Z0lBDtitGOW2gb33socC/xSE`, MAC `88:a2:9e:8c:8d:4e` | PASS |
| PW threads (A1), both rounds | main and data loops FIFO 88 | FF 88, ni "-" | PASS |
| module-rt instances (A1b) | exactly one | 1 | PASS |
| RLIMIT_RTTIME | 200000/200000 us | 200000/200000 | PASS |
| RTKit / nice errors for PW (A3) | none | none | PASS |
| PW startup kill | NRestarts 0, no SIGKILL/SIGXCPU | 0, none | PASS |
| USB IRQ threads (A2) | recorded | irq/130, irq/135 xhci at FF 50 | recorded |
| greetd (F-367) | condition-skipped, no labwc | inactive, ConditionResult=no, NRestarts=0 | PASS |
| user@1000 at boot | active before any login | active at +9.2 s, first SSH at +18.8 s | PASS |
| Linger | yes | Linger=yes | PASS |
| systemd --user limits | rtprio 95 | 95/95 | PASS |
| T49 at 11 min uptime | NRestarts <= 3, no failed units | max 0, both lists empty | PASS |
| USBStreamer sink | S32LE, 8 ch, 48 kHz | S32LE, 8, 48000 (pw-dump and ALSA hw_params) | PASS |
| USBStreamer capture PCM (AC12) | ALSA capture PCM, 8 ch, 48 kHz | `pcmC1D0c` (card 1); stream0: 8 ch S32_LE 48 kHz (altset 1; altset 2 = 4 ch), not open; PW capture node deferred per F-295 | PASS (QE) |
| Gains (AC14), both rounds | all linear Mult/Add 0 | 24 enumerated, 16 gain-relevant (8 nodes x Mult/Add), all exactly 0 | PASS |
| HiFiBerry blocked | no card, modules, nodes | none in /proc/asound/cards; 4 modules not loaded; 0 objects | PASS |
| Thermal | < 80 °C | max 66.65 °C (21 samples) | PASS |

### Deviations from Plan

- The reboot was `systemctl reboot` (warm). Accepted for AC13 (AE): the RT
  setup is applied fresh at every PipeWire start. The T48 power cycle is
  still open; it records the PipeWire `ps -L` once as a confirmation, not
  a gate.
- `aplay`/`arecord` are not on the image; the HiFiBerry check used
  `/proc/asound/cards` instead (accepted by AE and QE).
- AC14: `pw-cli enum-params` lists 24 values, 8 linear nodes x (Control,
  Mult, Add). Control only feeds the notify port, not the audio path, so
  16 are gain-relevant (AE).
- AC12 capture: PipeWire has no USBStreamer capture node by design (F-295;
  GraphManager adds it for Live mode). The ALSA-level evidence is the static
  USB descriptor, read without opening the PCM (CM-OBS-.89-AC12, same boot
  `1531f01f`):

  ```bash
  $ cat /proc/asound/USBStreamer/stream0      # Capture section
  Capture:
    Status: Stop
    Interface 2
      Altset 1
      Format: S32_LE
      Channels: 8
      Rates: 44100, 48000
    Interface 2
      Altset 2
      Format: S32_LE
      Channels: 4
      Rates: 44100, 48000
  $ cat /proc/asound/USBStreamer/pcm0c/info
  card: 1
  stream: CAPTURE
  subdevices_avail: 1
  ```

  The card-id path and the stream0 header bind it to the USBStreamer;
  "USB Audio" is the generic snd-usb-audio name. Whatever opens capture
  later (Live mode) must use altset 1: altset 2 has only 4 channels.

### Notes

- **No mod.rt journal lines** for PipeWire: `log.level` is 2, so module-rt's
  info lines are not logged. The evidence is the merged module properties
  plus the thread classes from `ps -L` (accepted by QE), and the absence
  of the "could not set nice-level" warning.
- **Gain readings:** `pw-cli enum-params` prints six decimals, so a tiny
  non-zero value would read as `0.000000`. AC14 was checked from `pw-dump`
  JSON against exact 0.
- **APC mini mk2** appears as ALSA card 0 (USB-Audio); it is MIDI-only and
  has no PCM device.
- **WirePlumber** logs "mod.rt: could not set nice-level to -11: Permission
  denied" on every start and activates rtkit-daemon at boot; it loads its own
  module-rt with stock args. Not in the audio data path. Backlog.
- **Metering bridges** (pcm-bridge x2, level-bridge x3) stay active after a
  PipeWire restart but their nodes do not come back (7 nodes instead of 12,
  6 min later). Dead meters look like "no signal". Not a US-163 blocker,
  but an **open amps-on precondition** (AE, Architect; backlog P1). Until
  it is fixed: after any PipeWire restart, restart pcm-bridge and
  level-bridge and confirm live meters before the amps go on.
- **Pi 4:** the fragment is shared by all boards, so Pi 4 drvPaths change.
  Pi 4 runtime is unverified.

---

## Task T53 / T54 / AC1a / AC18a: exposure, rollback and reproducibility

**Date:** 2026-10-25 09:42-12:45 UTC
**Operator:** Claude (worker-1, under change-manager sessions CM-OBS-.89-T53,
CM-OBS-.89-T53b, CM-OBS-.89-T53c, CM-DEP-.89-T54 and CM-DEP-.89-AC18a)
**Host:** mugge (Pi 5), booted `nkifli3rxayxxmrndqw3a3ic0jj5fix8` except
during T54

Every ssh call used `StrictHostKeyChecking=yes` against the pinned
known_hosts file (ED25519 `SHA256:a5kILUyr7XhT3D5Vdm4Z0lBDtitGOW2gb33socC/xSE`).
Listener evidence is on-device `ss`, not an external scan (owner, 2026-10-25).

### Validation

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Identity (T53) | host key and MAC unchanged | `a5kILUyr…`, MAC `88:a2:9e:8c:8d:4e`, boot_id `1531f01f…` | PASS |
| sshd (T53, T53b) | no root login, no password or keyboard-interactive | `sshd -T`: permitrootlogin, passwordauthentication, kbdinteractiveauthentication all `no` | PASS |
| Root keys (T53, T53b) | no root authorized_keys | `/root/.ssh/` empty; `/etc/ssh/authorized_keys.d/` holds only `ela` | PASS |
| Listeners (T53, `sudo ss -ltnup`) | 22 and 8080 on the LAN; RPC and meters on localhost; no 5900 | tcp 22 on `0.0.0.0` and `[::]`; tcp 8080 on `0.0.0.0` only; 4001, 4002, 9090/9091, 9100-9102 and 53 on localhost; udp 5353 and 68; LLMNR 5355 tcp/udp on all addresses; nothing on 5900 | PASS (dispositions below) |
| 8080 owner (T53b) | web UI as ela | uvicorn, user `ela`, cgroup of `user@1000.service` | PASS |
| Firewall (T53, `sudo nft list ruleset`) | inbound default drop | `inet nixos-fw` input policy drop; allows tcp 22 and 8080, udp 5353, ICMP echo, ICMPv6 except redirect and type 139, DHCPv6 client; rpfilter on | PASS |
| IPv6 (T53) | recorded | two global SLAAC addresses (EUI-64 and temporary), link-local, no ULA | recorded |
| AC15 services (T53) | all up | GraphManager, signal-gen, pcm-bridge x2, level-bridge x3, PipeWire, WirePlumber active; web UI `curl -k` from the Mac: 200 | PASS |
| GraphManager gate (T53, T54) | closed | `get_gate`: `gate_open: false`, no pending gains (read-only query) | PASS |
| Undervoltage, T54 boots (T53c) | no undervoltage | 0 lines on each of `8919af16`, `b74bc437`, `45ebdf64` (all in the journal, rc 0); `rpi_volt` `in0_lcrit_alarm` = 0 | PASS |
| T54 step 1-2 | rollback to gen 2 boots x83 | `--switch-generation 2` + `switch-to-configuration boot` rc 0; booted `x83m7bircd4b7j8wchx9k1mnilzi8kl4` (boot_id `8919af16`), system running | PASS |
| T54 step 2b | x83 survives a second reboot | booted x83 (boot_id `b74bc437`) | PASS |
| T54 step 3-4 | forward to gen 3 boots nkifli3r | `--switch-generation 3` + `switch-to-configuration boot` rc 0; booted nkifli3r (boot_id `45ebdf64`) | PASS |
| T54 after return | T51, AC14, check #10, AC13/T49 | current = booted = profile = nkifli3r; 16 gain-relevant values exactly 0 (pw-dump); PW FF 88, one module-rt, RTTIME 200000/200000, NRestarts 0, no failed units | PASS (QE) |
| T54 thermal | < 80 °C, no throttling | max 66.1 °C; `cpuinfo_cur_freq` = max (2.4 GHz) on all 31 samples; governor performance; cooling_device not sampled | PASS |
| AC1a: Pi 4 drvPath | only `05-rt-direct.conf` or configurationRevision differs from main | `nixosConfigurations.mugge`: origin/main `289390bf` and `c34f7da7` both `8nv9psc1mf8da746cxginj021jjs8a5a`; branch `bbff469e` `j2ykkiilld1pfkchxbgrqyqwigrkkd14`; nix-diff: only `pi4audio-pipewire-configs` gains `05-rt-direct.conf` | PASS (criterion met) |
| AC18a: no-op boot | clean checkout at `132997f9`, `nixos-rebuild boot --no-reexec` | rc 0; toplevel unchanged (nkifli3r, 0 paths copied); no new profile generation (still system-3); os_prefix unchanged; FAT pruned to {new, prev, booted} by the pre-AC2a hook; MAP.txt updated (`2 x83… pruned`) | PASS (Architect + QE) |

**T53 dispositions:**

- 8080 open on the LAN: owner ruling ("web ui stays open"), known F-037
  risk. It binds IPv4 only, so nothing answers on IPv6.
- LLMNR 5355 listens on all addresses but is not in the nft allow list, so
  it is unreachable from the network. Backlog: disable LLMNR.
- No VNC listener, as the owner ruled it is not needed now.

**T53c grep:** `journalctl -k -b <boot id> | grep -iE 'under-?voltage|voltage normali'`.
The pattern is case-insensitive and covers "Undervoltage detected" and
"Voltage normalised".

### FAT generations

The FAT keeps new, previous, booted and the newest other complete generation, so ≥2 generations remain whenever ≥2 exist.

This is the AC2a rule (PO ruling after AC18a). The hook that ran in AC18a
kept only {new, previous, booted}, so a no-op deploy (new = previous =
booted) left exactly one FAT generation. The fix is in
`nix/nixos/boards/pi5/prune-gens.nix`. The "newest other" generation is
the highest-numbered `system-N-link` whose id differs from the new one and
whose `gens/<id>/.complete` exists. The prune only ever keeps directories,
it never recreates them, so `gens/x83…/` stays pruned until a deploy
writes it again. The offline check `checks.<system>.pi5-prune-gens` runs
the same script against fake directories.

After AC18a the firmware partition held only
`gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/`. After CM-DEP-.89-3 (deploy of
`f0fbefd1`, AC18b, AC18c and T54b) it holds two complete generations,
`2wf21ydgfyqsz35iqy5hfjlyp37jrsqn` (system-4, booted) and
`nkifli3rxayxxmrndqw3a3ic0jj5fix8` (system-3):

```bash
$ cat /boot/firmware/gens/MAP.txt
1 p9mzphhydmf7p1kjqjkc76dvcij2y99i pruned
2 x83m7bircd4b7j8wchx9k1mnilzi8kl4 pruned
3 nkifli3rxayxxmrndqw3a3ic0jj5fix8 present
4 2wf21ydgfyqsz35iqy5hfjlyp37jrsqn present
$ grep -n os_prefix /boot/firmware/config.txt
16:os_prefix=gens/2wf21ydgfyqsz35iqy5hfjlyp37jrsqn/
```

Recovery via card reader: set line 16 to
`os_prefix=gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/` (the previous
generation). The x83 store path and `system-2-link` remain, so the T54
method rewrites `gens/x83…/` from the store if a rollback to it is needed.

### Deviations from Plan

- **Port scans are not evidence.** An `nmap` run (v4, v6 EUI-64, v6
  temporary) started at 09:55:48Z. The owner directive to stop scanning came
  at about 11:40Z; the v6-temporary scan still ran from 11:38:51Z to
  12:30:10Z, past it. The nmap output files are NOT evidence; the listener
  rows above come from on-device `ss`.
- **Minor scope deviations (T53):** a 3-port nmap probe at 09:54Z and a
  `ping6`, both outside the granted scope.
- **T53c retry:** `journalctl -b` rejects dashed boot ids ("Invalid
  argument"); the undervoltage check was rerun with undashed ids in a second
  ssh session.
- **T54 thermal sampler:** `cpuinfo_cur_freq` is root-only; the first
  sampler run read it without sudo and was restarted with sudo before
  step 0. Its fields are unlabelled, so cooling_device state is recorded as
  not sampled; the undervoltage evidence is the T53c row.
- T54 reboots were warm (`systemd-run --on-active=2 systemctl reboot`),
  each announced to the change-manager first; nothing connected to any Pi
  output.

---

## Task AC17 Session B: USBStreamer re-enumeration (CM-CHG-.89-5)

**Date:** 2026-10-25 13:45-15:29 UTC
**Operator:** Claude (worker-1, under change-manager session CM-CHG-.89-5)
**Host:** mugge (Pi 5), booted `2wf21ydgfyqsz35iqy5hfjlyp37jrsqn` (boot_id `eeddb8b6…`)

Purpose: after the USBStreamer drops off the bus and comes back, nothing
may get louder. The checks cover hardware mixer volumes and switches,
PipeWire volume and mute on the sink and convolver output, the 16 convolver
gains, the gate and the links. No mixer writes were made at any point
(no `amixer set`, no `alsactl`). Nothing was connected to any Pi output.

Steps:

- (a) software re-enumeration: `echo 0`, 5 s, `echo 1` to the USBStreamer's
  sysfs `authorized` file;
- (b) the owner's physical unplug and replug;
- (c) a PipeWire restart, then a restart of the metering bridges (the
  interim rule from the F-358 notes);
- cycles 1 and 2: the owner pulls the Pi's power and plugs it back in. The
  wrapper only reads (no restarts, no writes): it polls SSH every 5 s for a
  new boot_id (up to 900 s), waits 60 s, then takes the read set.

Each step compares a full read set taken after it with the read set taken
before step (a). Each power cycle also reads the USBStreamer's sysfs
`bmAttributes` and `bMaxPower` before and after (AE: expected port 1-1,
`80` = bus-powered), and the scheduling class and RT priority of the
PipeWire main and `data-loop.0` threads plus their `RTTIME` limit.

### Procedure

```bash
# Step (a): device 1-1, devnum 2 (the only USBStreamer on the bus)
$ echo 0 | sudo tee /sys/bus/usb/devices/1-1/authorized    # 13:46:33Z
$ echo 1 | sudo tee /sys/bus/usb/devices/1-1/authorized    # 13:46:38Z
# 30 s wait, then the AFTER-a read set

# Step (c)
$ systemctl --user restart pipewire                          # 15:10:59Z
$ systemctl --user restart level-bridge-hw-in level-bridge-hw-out \
    level-bridge-sw pcm-bridge-capture-usb pcm-bridge-monitor  # 15:11:10Z
# 30 s wait, then the AFTER-c read set

# Cycles 1 and 2 (read-only wrapper, then the owner's power pull)
$ ac17-B-change.sh cycle 1                                   # POLLING 15:18:21Z
$ ac17-B-change.sh cycle 2                                   # POLLING 15:24:51Z
$ cat /sys/bus/usb/devices/1-1/{bmAttributes,bMaxPower}
$ ps -L -o pid,tid,cls,rtprio,comm -p "$(systemctl --user show -p MainPID --value pipewire)"
$ grep 'Max realtime timeout' /proc/<pipewire pid>/limits
```

### Validation

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| (a) nothing louder | volumes not higher, switches unchanged, mutes not released | all hw and PW values identical to BEFORE | PASS (AE) |
| (a) gains (AC14) | 16 values exactly 0 | 16, all 0 (pw-dump) | PASS |
| (a) gate | closed | `gate_open: false`, no pending gains | PASS |
| (a) links | unchanged | 24 before, 24 after, same set by name | PASS |
| (a) sink recovery | recorded | no recovery: PipeWire never reopened the device (F-373, below) | FINDING |
| (b) physical replug | replug seen within 1800 s | not seen: poll 13:54:48-14:25:31Z ended in a timeout | DEFERRED (F-373) |
| (c) nothing louder | as in (a) | all hw and PW values identical to BEFORE | PASS |
| (c) gains, gate, links | 16 x 0, closed, 24 | 16 x 0, closed, 24 (same set by name) | PASS |
| (c) nodes | the same 12 node names as BEFORE, all 5 bridge nodes | 12/12, all 5 bridges | PASS |
| (c) sink | exactly one, running, no error, no `spa.alsa` lines from 5 s after the restart | one (`running`), `spa.alsa` count 0 | PASS |
| (c) PCM open | Playback Channel Map as BEFORE | `3,4,7,8,5,6,12,13` again | PASS |
| (c) services | all active, no restarts | PipeWire, WirePlumber, the 5 bridges, GraphManager, signal-gen active; NRestarts 0; no failed units | PASS |
| Cycles 1, 2: reboot | new boot_id, same generation | down 15:20:20Z / up 15:20:43Z, then down 15:26:12Z / up 15:26:49Z; `eeddb8b6…` → `7f56af91…` → `8c6239cb…`; booted `2wf21ydg` both times; PREEMPT_RT | PASS |
| Cycles 1, 2: nothing louder | as in (a), against the BEFORE-(a) reads | all hw and PW values identical; 16 gains 0; gate closed; 24 links, same set | PASS |
| Cycles 1, 2: USBStreamer | one device at 1-1, bus-powered | `usb 1-1: new high-speed USB device number 2` in each boot; 1-1, `bmAttributes=80`, `bMaxPower=500mA` before and after | PASS |
| Cycles 1, 2: sink and nodes | 12 nodes, one sink running, no `spa.alsa` errors | 12/12, one sink (`running`), `spa.alsa` count 0 | PASS |
| Cycles 1, 2: services, power | no failed units, no throttling | 9/9 user units active, no failed units; `get_throttled=0x0`; no undervoltage | PASS |
| Cycles 1, 2: RT scheduling | `pipewire` and `data-loop.0` FF 88; RTTIME 200000/200000 | FF 88 for both threads in both boots; RTTIME 200000/200000 µs | PASS |
| Thermal | < 75 °C, no throttling | max 65.55 °C (a), 65.0 °C (b), 63.35 °C (c), 63.9 °C (cycle 1), 62.25 °C (cycle 2); 2.4 GHz throughout; no cooling devices; undervoltage alarm 0 | PASS |

**F-373, zombie sink after re-enumeration** (AE: High, availability and
safety-relevant, amps-on item 13; not a US-163 blocker). The AE's timeline:

- 13:46:33Z: `authorized` set to 0. PipeWire starts logging
  `spa.alsa: hw:USBStreamer,0p: snd_pcm_status error: No such device` and
  `snd_pcm_drop: No such device` at once.
- 13:46:38Z: `authorized` set to 1. The kernel logs `usb 1-1: authorized
  to connect` and the card returns as ALSA card 0, but PipeWire never
  reopens it.
- The sink node keeps its id (33) and serial (34) and still reports
  `running`. The hardware Playback Channel Map reads all 0 (it was
  `3,4,7,8,5,6,12,13`), i.e. no PCM is open. It still read all 0 in
  the BEFORE-b reads at 13:54Z.
- The sink is a static adapter from `pipewire.conf.d`, so it has no hotplug
  path (AE). The output stays silent until PipeWire restarts.
- Step (c) recovered it: after the restart the channel map is back to
  `3,4,7,8,5,6,12,13` and the new PipeWire process logs no `spa.alsa`
  errors. The `No such device` lines at 15:10:59Z come from the old
  PipeWire process while it shut down.

Step (a) passes the AC17 safety criterion (AE): the device came back no
louder, and the gate stayed closed.

### Deviations from Plan

- **No GC roots for the AC17 tools.** The `libpi` step copied
  `libraspberrypi` (`vcgencmd`) and `alsa-utils` (`amixer`) from
  cache.nixos.org to the Pi (rc 0). Both `nix-store --add-root` calls under
  `/nix/var/nix/gcroots/per-user/ela/` failed (rc 1, "Permission denied"):
  NixOS does not create per-user gcroots directories, and `ela` cannot
  create one under `/nix/var/nix/gcroots/per-user/`. CM ruling: no new
  roots. The paths are read-only tools, the Pi has no GC timer and nobody
  runs GC by hand; if they are ever collected, a new `nix copy` restores
  them. The planned `unroot` step is dropped.
- **Step (b) not run, deferred to F-373.** The replug poll ran its full
  1800 s (13:54:48Z to 14:25:31Z, rc 4) and saw no unplug. The owner
  request was never relayed, so this is not a Pi finding. The AE and QE
  deferred (b) from US-163 to F-373, and the two power cycles were run
  instead. If (b) runs later, it starts from a healthy sink.
- **Step (b) baseline only.** The BEFORE-b read set (taken at 13:54Z) is
  complete; AC14 16 gains all 0 at that point.
- **The power-cycle reads do not prove a cold power-off.** The USBStreamer
  gets device number 2 on every fresh enumeration, and every boot logs
  `new high-speed USB device`, so a warm reboot would look the same. The
  evidence for a cold cycle is the owner pulling the plug after the CM's go
  (15:19Z for cycle 1) and the 23 s and 37 s down windows.
- **Early-boot journal timestamps are not usable.** In both boots the
  kernel stamps the USBStreamer enumeration before the poll saw the Pi go
  down (15:19:35Z vs 15:20:20Z, 15:24:59Z vs 15:26:12Z). The likely cause
  is a clock that was not yet set at boot. The timeline above uses the
  Mac-side poll times.
- **PipeWire main thread at FF 88 (AE ruling).** Current: PW main thread
  and data-loop.0 both SCHED_FIFO 88 (main thread via F-020 unit, data loop
  via module-rt / 05-rt-direct.conf), verified on 2 cold boots. Backlog P2
  (not US-163): return the main thread to SCHED_OTHER so only the data loop
  runs at 88.
- **Mixer state after a cold boot (AE).** The `amixer` dumps after both
  power cycles are byte-identical to the dump taken before step (a)
  (sha256 `29d42498…`). The USBStreamer powers up at hardware 0 dB, so the
  re-open trigger (iii) stands.
- **Scope of the power cycles (AE).** A cold boot enumerates the
  USBStreamer before PipeWire starts, so the cycles do not exercise the
  F-373 hot-replug path. That is scope, not a gap: hot replug stays with
  F-373.

---

## Task AC19: redeploy of merged main (CM-DEP-.89-AC19)

**Date:** 2026-10-25, run from 19:47Z (Pi down 19:54:29-19:54:47Z, Mac-side
poll times; the Pi 5's early-boot journal runs ahead, see AC17 Session B)
**Operator:** Claude (worker-1, under change-manager session CM-DEP-.89-AC19)
**Host:** mugge (Pi 5), from `2wf21ydg` (f0fbefd1) to `rcyg67wd` (main `07a65f9e`)

Purpose: after #50 merged, deploy the merged main SHA and re-read the
AC17 set against the AC17 (a) BEFORE values. A warm reboot is enough
unless the nix-diff from `2wf21ydg` touches an AC19 cold-cycle trigger
(boot chain, audio device path, audio startup, gain defaults, anything
that sets the USBStreamer hw volume), or the EEPROM changed. Verdict: QE
ACCEPTED, warm reboot sufficient. QE recomputed the sha256 of every
evidence file and read each result in the files themselves.

### Procedure

- Deploy from the Mac (start 19:49:34Z) with the D-069 deploy verb
  (`nixos-rebuild-ng` `boot`, see `docs/guide/howto/nixos-upgrade.md` §8.3),
  from a clean export of `07a65f9e`: `switch-to-configuration boot`, not
  `switch`, with the pinned known_hosts and `StrictHostKeyChecking=yes`.
- One announced warm reboot (issued 19:54:15Z). The down window comes from
  the Mac-side poll, not from the Pi's journal.
- The AC17/AC19 read set before (PRE) and after (POST) the reboot, and a
  second service read at the 10-minute mark (same boot id).

### Validation

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Cold-cycle triggers | none touched | masked nix-diff `5fih61rg` (f0fbefd1) vs `113xl12f` (07a65f9e): one mismatching environment, `nixos-version` (`@configurationRevision@` and `@json@` only); the rest is the expected cascade (etc, dbus-1, system-path, system/user units, X-Restart-Triggers). Same shape vs 22370317 (`ydr9h4xi`); unmasked diffs show only the store-path cascade | PASS (warm) |
| Other outputs | unchanged | Pi 4 drv `j2ykkiil`, `images.sd-card` `r4hqi43b`, both as in the #50 T3 | PASS |
| Reboot and identity | new boot id; booted = main | `8c6239cb` → `ff87ced5`; booted = current = profile = `rcyg67wd`; configurationRevision `07a65f9e`; kernel 6.12.62 PREEMPT_RT; host key `a5kILUyr…`, MAC `88:a2:9e:8c:8d:4e` | PASS |
| Boot generations | ≥2 complete incl. booted | `config.txt:16` `os_prefix=gens/rcyg67wd…/`; MAP 4 `2wf21ydg` and 5 `rcyg67wd` present, 1-3 pruned; both `.complete=yes`; no `*.tmp` dirs | PASS |
| EEPROM | equal to DRM1 baseline | version `000d3ca2…`, timestamp 1756339608, config sha256 `916ce18a…`: all equal, so not a cold trigger | PASS |
| Power | no throttling | `get_throttled=0x0`; no under-voltage lines in the kernel log | PASS |
| HiFiBerry (AC12a) | no module, no card, no node | no hifiberry/pcm512 module loaded; 0 such PW objects; `/proc/asound/cards` lists only the APC mini mk2 and the USBStreamer | PASS |
| Gains and gate (AC14) | 16 x 0, closed | all 16 Mult/Add 0; gate closed, no pending gains | PASS |
| USBStreamer hw mixer | unchanged | `amixer` sha256 `29d42498…` in all three snapshots, as in AC17; hw volume still 0 dB, not a cold trigger | PASS |
| PW graph vs AC17 (a) BEFORE | unchanged | nodes 12/12 and links 24/24, none gone or new; 32 USBStreamer link lines; sink running; PW volume and mute props unchanged; `spa_alsa` journal count 0 | PASS |
| RT scheduling | FF 88; RTTIME 200000/200000 | `pipewire` and `data-loop.0` FF/88; RTTIME 200000/200000 | PASS |
| USB power | as AC17 | `bMaxPower=500mA`, devnum 2 | PASS |
| Services | no failed units, no restarts | no failed system or user units; all 9 audio user units active, NRestarts 0 at 10 min (uptime 0:10, same boot id); no system unit with restarts | PASS |
| Thermal | < 75 °C, no throttling | peak 65.55 °C during the deploy, 66.1 °C at 10 min; 2.4 GHz of 2.4 GHz, `performance` governor; no undervoltage alarm; no cooling devices (passive case, valid) | PASS |
| PRE / POST read sets | PASS | both PASS, 0 recovery findings | PASS |

### Notes

- **deploy-src git metadata (QE, non-blocking).** The eval stderr shows
  "could not read HEAD ref … using 'master'" for the deploy-src export.
  Harmless here because configurationRevision came out correct. If future
  evidence relies on the export's git metadata beyond `self.rev`, the
  export needs a real ref (backlog, PM).
- Evidence: the `ac19-run-20261025T194712Z/` directory (17 files, 0600)
  plus the `ac19-nixdiff-*`, `ac19-evals-pi4-sdcard-07a65f9e.txt` and
  `ac19-drvpath-07a65f9e.txt` files in the operator's private evidence
  directory.
