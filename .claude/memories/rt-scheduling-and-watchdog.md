# RT Scheduling and Hardware Watchdog Gotchas

## Topic: PREEMPT_RT does not remove RT starvation risk (2026-10-24)

**Context:** Security review of `rt-tuning.nix`.
**Learning:** On PREEMPT_RT, interrupt handlers run as threads at SCHED_FIFO 50, below PipeWire (88) and GraphManager (80). With `sched_rt_runtime_us = -1`, a runaway RT thread can starve its core's IRQ threads, sshd and the web UI. The claim "PREEMPT_RT removes the starvation risk" is wrong.
**Source:** security-specialist.
**Tags:** PREEMPT_RT, sched_rt_runtime_us, IRQ threads, FIFO, starvation, rt-tuning

## Topic: BCM2835 hardware watchdog is not fed (2026-10-24)

**Learning:** The BCM2835 watchdog driver is compiled in, but nothing in `nix/` sets `systemd.watchdog.runtimeTime`, so nothing feeds it. Docs that describe it as a backstop are wrong until that is configured. (Earlier T3/T5 lockups where it "failed" may be explained by this.) Tracked: F-317 (no backstop), F-325 (configure and test). A watchdog reboot drops the USBStreamer stream with no owner warning (transient risk, safety.md §1), so enabling it is an owner tradeoff (O-24).
**Source:** security-specialist.
**Tags:** watchdog, BCM2835, systemd, runtimeTime, lockup, nixos

## Topic: node.autoconnect=false does not protect a default sink (2026-10-24)

**Learning:** `node.autoconnect = false` on a sink only stops that node from autoconnecting itself. If the sink is the default sink, WirePlumber is expected to auto-link OTHER streams to it. This is expected from WirePlumber's default policy, pending Pi confirmation via F-318 (amps-off test).
**Source:** security-specialist.
**Tags:** wireplumber, autoconnect, default sink, linking, policy
