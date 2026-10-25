# HOWTO: NixOS Deployment and Upgrades

This guide covers initial installation and incremental upgrades of the
audio workstation's NixOS system. The flake has one configuration set per
board, and the procedures differ:

| Board | Status | Configurations | Sections |
|-------|--------|----------------|----------|
| Raspberry Pi 5 (`mugge`, `ela@192.168.178.89`) | Current deployment target since 2026-10-24 (US-163) | `mugge-pi5-bootstrap`, `mugge-pi5-deploy`, `pi5-installer` | [Section 8](#8-raspberry-pi-5) |
| Raspberry Pi 4B (`ela@192.168.178.185`) | Unreachable since 2026-10-24; configuration kept as the US-164 baseline | `mugge`, `mugge-deploy` | Sections 2-7 |

**Do not apply Sections 2-7 to the Pi 5.** The Pi 5 cannot use the kexec
install, has no U-Boot, and is deployed with `boot` plus an announced
reboot, not `switch`.

T-072-19a (US-072: NixOS Build), US-163 (Pi 5)


## 1. Prerequisites

- Nix with flakes enabled on the build host
- SSH access to the target Pi as user `ela` (key-based, passwordless sudo)
- The Pi must be network-reachable from the build host
- For nixos-anywhere: the Pi must be running some Linux with SSH access
  (DietPi, Raspberry Pi OS, or an existing NixOS install)


## 2. Initial Installation (nixos-anywhere, Pi 4B)

Use `nixos-anywhere` for the first NixOS install on a Pi that is currently
running another OS (e.g., DietPi, Raspberry Pi OS). This wipes the SD card,
repartitions it via disko, and installs NixOS.

**WARNING:** This is destructive. The entire SD card will be reformatted.
Back up any data on the Pi first.

**SAFETY:** The USBStreamer will lose its audio stream during the reboot.
Ensure amplifiers are OFF before proceeding. See `docs/operations/safety.md`.

```sh
# From the project root on the build host:
nix run github:nix-community/nixos-anywhere -- \
    --flake .#mugge-deploy \
    root@<target-host>
```

What nixos-anywhere does:
1. Boots a minimal NixOS installer via kexec on the target
2. Runs disko to partition the SD card (256M FAT32 firmware + ext4 root)
3. Installs the NixOS system closure
4. Runs activation scripts (including firmware population to /boot/firmware)
5. Reboots into the new NixOS system

After installation, run the smoke test to verify:

```sh
scp scripts/nixos-smoke-test.sh ela@<target-host>:/tmp/
ssh ela@<target-host> sudo bash /tmp/nixos-smoke-test.sh
```


## 3. Incremental Upgrades (nixos-rebuild, Pi 4B)

For ongoing updates after the initial NixOS installation, use `nixos-rebuild`.
This is the standard NixOS upgrade path: it builds the new system closure,
switches to it, and runs activation scripts. No repartitioning, no data loss.

```sh
# From the project root on the build host:
nix run nixpkgs#nixos-rebuild -- switch \
    --flake .#mugge-deploy \
    --target-host ela@<target-host> \
    --sudo
```

The `--sudo` flag runs activation commands via `sudo` on the
target. This works because user `ela` has passwordless sudo configured
in the NixOS config (`security.sudo.wheelNeedsPassword = false`). Root
SSH login is disabled for security (`PermitRootLogin = "no"`).

What nixos-rebuild does:
1. Evaluates the NixOS configuration on the build host
2. Builds all derivations (cross-compiled for aarch64-linux if building
   on x86_64, or natively if building on aarch64)
3. Copies the closure to the target via SSH
4. Activates the new system configuration on the target
5. Updates the bootloader (extlinux) to point at the new generation
6. Runs activation scripts (firmware update, tmpfiles, etc.)

**No reboot required** for most changes. The new configuration takes effect
immediately. Services are restarted as needed by NixOS's activation logic.

### When a reboot IS required

- Kernel changes (PREEMPT_RT version, kernel config)
- Boot firmware changes (config.txt, U-Boot)
- Changes to early-boot services

**SAFETY:** Warn the owner before rebooting. Amplifiers must be OFF.


## 4. Which Method to Use (Pi 4B)

| Scenario | Method | Command |
|----------|--------|---------|
| First install (non-NixOS Pi) | nixos-anywhere | `nix run github:nix-community/nixos-anywhere -- --flake .#mugge-deploy root@<ip>` |
| Incremental config/code change | nixos-rebuild | `nixos-rebuild switch --flake .#mugge-deploy --target-host ela@<ip> --use-remote-sudo` |
| Wipe and reinstall | nixos-anywhere | Same as first install |
| Kernel/firmware update | nixos-rebuild + reboot | `nixos-rebuild switch ...` then `ssh ela@<ip> sudo reboot` |

**Note:** `nixos-anywhere` requires root SSH on the **source** OS (before
NixOS is installed). After NixOS installation, root SSH is disabled —
all subsequent operations use `ela` with `--use-remote-sudo`.

**Always use `mugge-deploy`** (not `mugge`). The `mugge` configuration is
for building SD card images; `mugge-deploy` includes the disko partitioning
module needed for an installed system.


## 5. Build Host Options

### Building on the same architecture (aarch64)

If the build host is aarch64-linux (e.g., another Pi, an ARM cloud VM, or
the nix-builder), the build is native and straightforward.

### Cross-building from x86_64

If the build host is x86_64-linux, Nix will cross-compile for aarch64.
This requires either:

- **binfmt/QEMU:** `boot.binfmt.emulatedSystems = [ "aarch64-linux" ];`
  on the NixOS build host. Slower but works everywhere.
- **Remote builder:** Configure a remote aarch64-linux builder in
  `nix.buildMachines`. The build host offloads aarch64 builds to the
  remote machine.

The project's nix-builder (if available) handles this transparently.


## 6. Rollback (Pi 4B)

NixOS keeps previous generations. To roll back after a bad upgrade:

```sh
# On the Pi:
nixos-rebuild switch --rollback

# Or boot the previous generation via the bootloader menu
# (if using U-Boot with extlinux, select the previous entry)
```

To list available generations:

```sh
nix-env --list-generations --profile /nix/var/nix/profiles/system
```


## 7. Flake Input Updates

To update nixpkgs or other flake inputs (e.g., for PipeWire version bumps):

```sh
# Update all inputs
nix flake update

# Update only nixpkgs
nix flake update nixpkgs

# Then deploy (Pi 4B command; for the Pi 5 use Section 8.3)
nixos-rebuild switch --flake .#mugge-deploy --target-host ela@<ip> --use-remote-sudo
```

After updating inputs, run the full test suite before deploying:

```sh
nix run .#test-all
```


## 8. Raspberry Pi 5

The Pi 5 (hostname `mugge`) runs NixOS since 2026-10-24 (US-163). The full
record of the bootstrap, with raw output, is the lab note
[`US-163-pi5-bootstrap.md`](../../lab-notes/US-163-pi5-bootstrap.md).

**Image status:** bootstrap/dev image, **not gig-capable**. See
`docs/operations/safety.md`, "Pi 5 Platform Status", before connecting
anything to any Pi output.

### 8.1 Target identity

| Property | Value |
|----------|-------|
| Address | `192.168.178.89` (DHCP lease pinned to the MAC); this IP is canonical |
| DNS alias | `mugge.lab.andreas.org` (LAN DNS `192.168.178.1` only; it does not resolve through VPN resolvers) |
| MAC | `88:a2:9e:8c:8d:4e` |
| SSH host key | ED25519 `SHA256:a5kILUyr7XhT3D5Vdm4Z0lBDtitGOW2gb33socC/xSE` |
| Login | `ela`, key-only, passwordless sudo; root login disabled |

Identify the Pi by host key plus MAC, not by IP. Every SSH connection uses a
pinned `known_hosts` file with `StrictHostKeyChecking=yes`; never
`accept-new`. If you connect by the DNS alias, map it to the same
`known_hosts` entry with `HostKeyAlias`.

### 8.2 Configurations

| Configuration | Purpose |
|---------------|---------|
| `pi5-installer` | RAM-only NixOS installer, booted once via firmware tryboot. Key-only root login for nixos-anywhere (owner-approved, installer only). |
| `mugge-pi5-bootstrap` | First install: cached non-RT nixpkgs kernel, no audio stack. |
| `mugge-pi5-deploy` | Production configuration: PREEMPT_RT 6.12.62 (`bcm2711_defconfig`, 4K pages), full audio stack. |

Builds run on the Mac's aarch64-linux builder (nix-darwin `linux-builder`).

### 8.3 Deploy (incremental upgrade)

Run from a clean checkout at the commit you want to deploy, on the Mac:

```sh
NIX_SSHOPTS="-o UserKnownHostsFile=<pinned known_hosts> -o StrictHostKeyChecking=yes -o BatchMode=yes -o ForwardAgent=no" \
  <nixos-rebuild-ng 26.11 store path>/bin/nixos-rebuild boot --no-reexec \
  --flake .#mugge-pi5-deploy --target-host ela@192.168.178.89 --sudo
```

Then **one announced reboot** (Section 8.6) into the new generation.

- Use `boot`, never `switch`. `switch` restarts PipeWire live, which
  interrupts the USBStreamer stream. `boot` only installs the generation
  and points the firmware at it; the change takes effect at the reboot.
- `--no-reexec` is required on the Mac. Without it, the tool re-execs into
  the target's aarch64 binary, which cannot run on darwin.
- The darwin `nixpkgs#nixos-rebuild-ng` 26.11 package names its binary
  `nixos-rebuild`, not `nixos-rebuild-ng`. Call it by its explicit store
  path so that you know which tool runs.
- Use `--sudo`; `--use-remote-sudo` (Sections 3-7) is the old flag name.
- The Mac's own system profile is not touched. Confirm on the Pi that the
  new generation exists: `readlink -f /nix/var/nix/profiles/system`.

After the reboot, check:

- `readlink -f /run/current-system` is the toplevel you built, and
  `nixos-version --configuration-revision` is the commit SHA you deployed.
- `systemctl --failed` and `systemctl --user --failed` are empty.
- Gains: every convolver gain (Mult and Add of all 8 gain nodes, 16
  values) reads exactly 0, checked from `pw-dump` JSON, not from `pw-cli`'s
  six-decimal output. Any other value after a boot is a FAIL; stop and
  report it (`docs/operations/safety.md`).
- PipeWire runs at SCHED_FIFO 88: `ps -L -o tid,cls,rtprio,comm -p $(pgrep -x pipewire)`
  shows `FF 88` for `data-loop.0`.
- After any PipeWire restart, restart pcm-bridge and level-bridge and
  confirm live meters (open amps-on precondition F2, see safety.md).

### 8.4 Boot chain and FAT generations

There is no U-Boot and no boot menu. The EEPROM firmware reads
`/boot/firmware/config.txt`, whose `os_prefix=` line selects one generation
directory on the FAT:

```
/boot/firmware/config.txt        os_prefix=gens/<id>/   (the pointer)
/boot/firmware/gens/<id>/        Image, initrd, cmdline.txt, DTBs, overlays/, .complete
/boot/firmware/gens/MAP.txt      system profile generation number -> <id>, present or pruned
```

`<id>` is the 32-character store hash of the system toplevel. Every deploy
writes the new generation completely, marks it `.complete`, and only then
rewrites `config.txt`. A power loss mid-deploy therefore leaves the previous
generation bootable (residual risk: vfat has no atomic rename, so a power
loss during the `config.txt` write itself can leave it unbootable; recover
as in Section 8.5).

Retention (AC2a): the FAT keeps the new, previous, booted and newest other
complete generation, so at least two remain whenever at least two exist.
All other generation directories are pruned. A pruned generation is not
lost: its store path and `system-N-link` remain, and a rollback (8.5)
writes its directory again.

The firmware currently merges none of the `dtoverlay=` lines in
`config.txt` (known deviation, fix in US-172): there is no DRM device and
Bluetooth stays on.

### 8.5 Rollback and recovery

**Rollback over SSH** (the Pi boots and is reachable). On the Pi, with N the
system profile generation to return to (`ls -l /nix/var/nix/profiles/`):

```sh
sudo nix-env --profile /nix/var/nix/profiles/system --switch-generation N
sudo /nix/var/nix/profiles/system/bin/switch-to-configuration boot
grep -n '^os_prefix=' /boot/firmware/config.txt   # must name the gens/<id>/ of generation N
```

Then one announced reboot. `switch-to-configuration boot` rewrites the
generation directory if it was pruned and points `os_prefix` at it. Do not
use `nixos-rebuild switch --rollback` or `switch-to-configuration switch`:
both activate live and restart PipeWire. Return to the newer generation the
same way. This procedure was tested in US-163 T54 and T54b.

**Recovery with a card reader** (the Pi does not boot):

1. Power the Pi off and mount the SD card's FAT partition on another
   machine.
2. Read `gens/MAP.txt` and list `gens/`. Pick a generation that is marked
   `present` and whose directory contains `.complete`.
3. Edit the `os_prefix=` line in `config.txt` to `os_prefix=gens/<id>/` for
   that generation. If `config.txt` is missing or truncated, restore it
   with that line (any recent copy of a working `config.txt` is a good
   base).
4. Put the card back and power on.

The current recovery line for the deployed generations is recorded in the
lab note ("FAT generations").

### 8.6 Safety

- Every reboot, power cycle, tryboot and PipeWire restart interrupts the
  USBStreamer stream. Announce it to the owner first (CLAUDE.md "Warn
  before reboots"). While the owner's standing statement "nothing is
  connected to any Pi output" holds, an announcement is enough; if
  anything has been connected since, wait for the owner.
- All access goes through the change manager's session tiers (OBSERVE,
  CHANGE, DEPLOY). A deploy needs a DEPLOY session with the commit SHA.
- Thermal: the Pi 5 has passive cooling only. During load runs, stop at
  80 °C.

### 8.7 First install (from Raspberry Pi OS)

The stock Raspberry Pi OS kernel on the Pi 5 has no kexec, so the standard
nixos-anywhere bootstrap (Section 2) cannot run. US-163 used install path D
(architect ruling): a RAM-only installer booted once through the Pi
firmware's tryboot, then nixos-anywhere without its kexec phase.

**WARNING:** Step 4 erases the SD card. Everything before it is reversible:
a power cycle brings Raspberry Pi OS back.

The commands below are the ones run in US-163 on 2026-10-24 (Raspberry Pi
OS on `.88`; the installer and NixOS came up on `.89`). Store paths and
SHAs are examples from that run. `<installer known_hosts>` and
`<pinned known_hosts>` are the files described in step 6.

**1. Build the tryboot bundle.** It contains `nixos-installer/` (Image,
initrd, `cmdline.txt`, bcm2712 DTBs, overlays), `tryboot.txt` and
`SHA256SUMS`. The installer is defined in
`nix/nixos/boards/pi5/installer.nix`.

```sh
nix build -L --out-link ./pi5-out \
  .#nixosConfigurations.pi5-installer.config.system.build.pi5TrybootBundle \
  .#nixosConfigurations.mugge-pi5-bootstrap.config.system.build.toplevel
```

In US-163 this ran on the Pi itself, under a temporary single-user Nix on
Raspberry Pi OS, from a git bundle checked out at a declared commit. That
builder no longer exists. Building the bundle on the Mac's aarch64-linux
builder and copying it over has not been tried yet.

**2. Stage the bundle on Raspberry Pi OS's `/boot/firmware`.** On the Pi,
with `F=/boot/firmware` and `B=<bundle path>`:

```sh
cp $F/config.txt ~/config.txt.pre-install          # keep a copy
sudo cp -r --no-preserve=mode,ownership,timestamps $B/nixos-installer $B/tryboot.txt $F/
sync
cd $F && sha256sum -c $B/SHA256SUMS                # every file OK; config.txt unchanged
```

`config.txt` is not modified, so the normal boot is still Raspberry Pi OS.
If the FAT partition is too small for the bundle, the planned fallback was
the same installer on a USB stick. That was never needed, and no commands
for it were written or run.

**3. Tryboot into the RAM installer (announced reboot).** On the Pi:

```sh
sudo systemd-run --on-active=2 /usr/sbin/reboot "0 tryboot"
```

The firmware boots `tryboot.txt` once. The installer runs from RAM and
permits key-only root login (owner-approved, installer only). A plain
reboot or power cycle returns to Raspberry Pi OS; US-163 tested this.

**4. Install with nixos-anywhere. This erases the SD card.** From the Mac,
in a clean checkout:

```sh
nix run --inputs-from . nixpkgs#nixos-anywhere -- \
  --build-on remote \
  --phases disko,install \
  --flake .#mugge-pi5-bootstrap \
  --ssh-option UserKnownHostsFile=<installer known_hosts> \
  --ssh-option StrictHostKeyChecking=yes \
  --ssh-option ForwardAgent=no \
  root@<installer IP>
```

- `--phases disko,install` skips kexec: the installer is already running.
  This is why the command connects as `root@`.
- `--build-on remote`: the installer builds the closure itself, from signed
  caches.
- nixos-anywhere's `reboot` phase is not used; reboot manually (step 5).
- US-163: nixos-anywhere 1.13.0, rc 0, 181 s.

**5. First boot, then switch to the RT configuration.** On the installer,
as root: `systemd-run --no-block systemctl reboot` (announced). The
`mugge-pi5-bootstrap` system boots with the non-RT kernel. Pin its host key
(step 6), then deploy `mugge-pi5-deploy` as in Section 8.3 and do one
announced reboot. After every reboot, compare
`/proc/sys/kernel/random/boot_id` and `uname -r` with the values from
before, to confirm that the Pi really booted again.

**6. Host keys.**

- **Installer hop:** the installer's host key exists only in RAM. In
  US-163 it was recorded trust-on-first-use (`accept-new`) into a fresh,
  throwaway file, `<installer known_hosts>`.
- **Installed system:** at the first NixOS boot, record the host key once
  (`accept-new`) into `<pinned known_hosts>`. From then on, every connection uses that
  file with `StrictHostKeyChecking=yes`, `BatchMode=yes` and
  `ForwardAgent=no` (Section 8.1).
- **Observed in the US-163 install log:** nixos-anywhere passes its own
  `-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no` ahead of
  the `--ssh-option` values. OpenSSH uses the first value it gets, so the
  installer-hop pin was most likely not in effect for nixos-anywhere's own
  connections. This affects only the throwaway installer hop and is on the
  backlog.
