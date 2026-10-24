# Pi 5 Bootstrap and aarch64 Builder — mugge

## Topic: Stock Raspberry Pi OS kernel on Pi 5 has no kexec (2026-10-24)

**Context:** US-163 P1, planning the nixos-anywhere install onto the Pi 5 at ela@192.168.178.88.
**Learning:** The Pi 5's stock Raspberry Pi OS kernel (`6.12.47+rpt-rpi-2712`) has no kexec support. In its config (`grep -E "KEXEC|CRASH_DUMP" /boot/config-$(uname -r)`, CM OBSERVE session CM-OBS-.88-1), `CONFIG_KEXEC_FILE` reads `# CONFIG_KEXEC_FILE is not set`, and there is no line at all for `CONFIG_KEXEC`, `CONFIG_KEXEC_CORE`, `CONFIG_ARCH_SUPPORTS_KEXEC` or any `CRASH_DUMP` symbol. `/sys/kernel/kexec*` does not exist, so there is no `kexec_loaded`: kexec support is not built in. worker-1 infers that kexec_load cannot even be selected in this build (unverified). kexec-tools is not installed, and `kexec` itself was not run. So nixos-anywhere's standard kexec bootstrap cannot run on a stock Raspberry Pi OS Pi 5. nixos-anywhere uses `kexec_load` (CONFIG_KEXEC), so `CONFIG_KEXEC_FILE` alone proves nothing. Before planning a nixos-anywhere install on any Pi, check both CONFIG_KEXEC and CONFIG_KEXEC_FILE in `/boot/config-$(uname -r)`, and check for `/sys/kernel/kexec_loaded` (an OBSERVE-tier read).
**Source:** worker-1, US-163 P1; evidence wording QE and AD (#47 review).
**Tags:** pi5, nixos-anywhere, kexec, raspbian, bootstrap, US-163

## Topic: Pi 5 boot chain: stock Raspberry Pi OS vs mugge's kernel (2026-10-24)

**Context:** US-163 P1, the same investigation.
**Learning:** The 16K pages and `kernel_2712.img` are properties of the stock Raspberry Pi OS kernel, not Pi 5 requirements. In the stock boot chain there is no U-Boot: by default the EEPROM firmware loads `kernel_2712.img` and `initramfs_2712` directly, and that kernel (`rpi-2712`) uses 16K pages. mugge's Pi 5 build uses `bcm2711_defconfig` (4K pages, the `kernel8.img` equivalent) by architect decision (US-163). It is built from the same pinned commit through the same kernel-config pipeline, and worker-1 verified that it supports RP1, MACB, PCIe and the bcm2712 DTBs. So nixos-kernel-config.md applies to the Pi 5 too, except that BLK_DEV_NVME stays enabled on the Pi 5. The firmware prefers `kernel_2712.img` when that file is present, so `config.txt` must always set `kernel=` explicitly. Test T51 checks that `getconf PAGESIZE` is 4096. PREEMPT_RT on the stock rpi-2712 config with 16K pages is unverified (AE); mugge's build does not use that config.
**Source:** worker-1, US-163 P1; stock defaults QE and AD, mugge kernel and `kernel=` rule Architect, T51 QE, RT note AE (#47 review).
**Tags:** pi5, bcm2712, bcm2711_defconfig, page-size, 16k, 4k, boot-chain, eeprom, u-boot, config-txt, kernel8, nvme, preempt-rt, US-163

## Topic: Pi HAT EEPROMs auto-load audio overlays (2026-10-24)

**Context:** US-163, the Pi 5 at .88 has a HiFiBerry DAC+ HAT.
**Learning:** A Pi HAT's EEPROM makes the firmware auto-load its device-tree overlay. On .88 the HiFiBerry DAC+ auto-loads pcm512x, which creates a second ALSA card. Nothing gates that card (it is outside the D-063 gate), and WirePlumber may pick it as the default sink. On any new Pi target, list `/proc/asound/cards` and any fitted HATs before the first PipeWire start. Block an unwanted card in layers: `force_eeprom_read=0` in `config.txt`, a kernel module blacklist and a WirePlumber disable rule. Then verify that the card is gone.
**Source:** Audio Engineer (#47 review).
**Tags:** pi5, hat, eeprom, device-tree, overlay, hifiberry, pcm512x, alsa, wireplumber, default-sink, safety, US-163

## Topic: nix-darwin linux-builder can crash-loop silently (2026-10-24)

**Context:** US-163, aarch64 builds from the Mac.
**Learning:** The Mac's nix-darwin linux-builder can crash-loop with no visible error. launchd showed runs=40k and exit code 1, while `nix store info --store ssh-ng://builder@linux-builder` gave "connection refused" on port 31022. Before assuming aarch64 builds work, run that `nix store info` command and check the launchd run count.
**Source:** worker-1, US-163.
**Tags:** nix, nix-darwin, linux-builder, aarch64, launchd, build-infra
