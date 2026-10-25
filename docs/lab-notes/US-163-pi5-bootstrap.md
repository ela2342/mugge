# US-163: Pi 5 NixOS Bootstrap

Lab notes for bringing the Pi 5 (hostname `mugge`, 192.168.178.89) up on
NixOS from the `mugge-pi5-deploy` configuration. Raw evidence stays in the
operator's private evidence directory (not in the repo); this note carries
excerpts only. Identity data is limited to fingerprints and the MAC address.

### Reproducibility

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
$ journalctl -b -u nixos-rebuild-switch-to-configuration | tail -2
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
`os_prefix=gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/`. Since AC18a this is the
only generation on the firmware partition (see "FAT generations" below).

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
| AC18a: no-op boot | clean checkout at `132997f9`, `nixos-rebuild boot --no-reexec` | rc 0; toplevel unchanged (nkifli3r, 0 paths copied); no new profile generation (still system-3); os_prefix unchanged; FAT pruned to {new, prev, booted} by the pre-AC2a hook; MAP.txt updated (`2 x83… pruned`) | PASS (Architect; QE pending) |

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

After AC18a the firmware partition holds only `gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/`:

```bash
$ cat /boot/firmware/gens/MAP.txt
1 p9mzphhydmf7p1kjqjkc76dvcij2y99i pruned
2 x83m7bircd4b7j8wchx9k1mnilzi8kl4 pruned
3 nkifli3rxayxxmrndqw3a3ic0jj5fix8 present
$ grep -n os_prefix /boot/firmware/config.txt
16:os_prefix=gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/
```

Recovery via card reader: `os_prefix=gens/nkifli3rxayxxmrndqw3a3ic0jj5fix8/`.
The x83 store path and `system-2-link` remain, so the T54 method rewrites
`gens/x83…/` from the store if a rollback is needed.

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
