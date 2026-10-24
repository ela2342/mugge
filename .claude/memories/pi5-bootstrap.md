# Pi 5 Bootstrap and aarch64 Builder — mugge

## Topic: Stock Raspberry Pi OS kernel on Pi 5 has no kexec (2026-10-24)

**Context:** US-163 P1, planning the nixos-anywhere install onto the Pi 5 at ela@192.168.178.88.
**Learning:** The Pi 5's stock Raspberry Pi OS kernel (`6.12.47+rpt-rpi-2712`) is built without kexec. Its config has `# CONFIG_KEXEC_FILE is not set`, and there is no `/sys/kernel/kexec*`. So nixos-anywhere's standard kexec bootstrap cannot run on a stock Raspbian Pi 5. Before planning a nixos-anywhere install on any Pi, check `/boot/config-$(uname -r)` for CONFIG_KEXEC / CONFIG_KEXEC_FILE (an OBSERVE-tier read).
**Source:** worker-1, US-163 P1.
**Tags:** pi5, nixos-anywhere, kexec, raspbian, bootstrap, US-163

## Topic: Pi 5 kernel uses 16K pages; no U-Boot in the boot chain (2026-10-24)

**Context:** US-163 P1, the same investigation.
**Learning:** The stock Pi 5 kernel (`rpi-2712`) uses 16K pages, not 4K. The boot chain has no U-Boot: the EEPROM firmware loads `kernel_2712.img` and `initramfs_2712` directly. A NixOS image for the Pi 5 must account for both points (page size for any software that assumes 4K pages; boot files the firmware loads by name). The Pi 4B notes in nixos-kernel-config.md (bcm2711) do not carry over.
**Source:** worker-1, US-163 P1.
**Tags:** pi5, bcm2712, page-size, 16k, boot-chain, eeprom, u-boot, US-163

## Topic: nix-darwin linux-builder can crash-loop silently (2026-10-24)

**Context:** US-163, aarch64 builds from the Mac.
**Learning:** The Mac's nix-darwin linux-builder can crash-loop with no visible error. launchd showed runs=40k and exit code 1, while `nix store info --store ssh-ng://builder@linux-builder` gave "connection refused" on port 31022. Before assuming aarch64 builds work, run that `nix store info` command and check the launchd run count.
**Source:** worker-1, US-163.
**Tags:** nix, nix-darwin, linux-builder, aarch64, launchd, build-infra
