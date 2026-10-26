"""
Deploy generated filters to PipeWire filter-chain.

Handles copying filter WAV files to the PipeWire filter-chain coefficients
directory and deploying the generated PW filter-chain .conf drop-in.

SAFETY: This module refuses to deploy filters that have not passed
verification (run_all_checks). The deploy function requires explicit
confirmation that verification passed.

NOTE: ``reload_convolver()`` is the preferred reload mechanism — it
triggers the Reload control port on the convolver node (US-112 patch),
which reloads coefficients in-place without destroying the node.  All
PW links stay connected, no GM re-linking required, instantaneous
pointer swap with no audio dropout.  ``reload_pipewire()`` is retained for
emergencies but should not be used for normal filter switching (F-221).

TK-166: Supports versioned (timestamped) filenames for deployment
traceability. Each deployment uses unique paths so that deployed versions
can be identified and rolled back if needed.

D-040: All CamillaDSP references replaced with PipeWire filter-chain
equivalents. The .conf drop-in deploys to
~/.config/pipewire/pipewire.conf.d/30-filter-chain-convolver.conf
and WAV coefficients to /etc/pi4audio/coeffs/.

US-174d: venue sets go through check_deployable_set (refuses simulated
sets) and trial_deploy / deploy_venue_set, which swap immutable set dirs
under coeffs/sets/ via the ``current`` and ``previous`` symlinks and keep
the new set only if the measured gate passes. Not wired to the PW conf
yet: the conf still reads the flat coeffs/<name>.wav files.
"""

import contextlib
import glob
import hashlib
import os
import re
import secrets
import shutil
import sys
from datetime import datetime, timezone

import soundfile as sf
import yaml

from .export import (
    CHANNEL_FILENAMES, DEFAULT_TAPS, SAMPLE_RATE, TIMESTAMP_FORMAT, versioned_filename,
)


# Default PipeWire filter-chain coefficients directory on the Pi (D-040).
# Overridable via PI4AUDIO_COEFFS_DIR env var (used by local-demo).
DEFAULT_COEFFS_DIR = os.environ.get(
    "PI4AUDIO_COEFFS_DIR", "/etc/pi4audio/coeffs"
)

# The production coeffs root on the Pi. A simulated set is never deployed
# here, whatever the override (Architect, US-174d Q3).
PRODUCTION_COEFFS_DIR = "/etc/pi4audio/coeffs"

# Default PipeWire config drop-in directory.
# Overridable via PI4AUDIO_PW_CONF_DIR env var (used by local-demo).
DEFAULT_PW_CONF_DIR = os.environ.get(
    "PI4AUDIO_PW_CONF_DIR",
    os.path.expanduser("~/.config/pipewire/pipewire.conf.d"),
)

# Default name for the filter-chain convolver config drop-in
DEFAULT_PW_CONF_NAME = "30-filter-chain-convolver.conf"

# Regex to match versioned coefficient files: combined_{channel}_{YYYYMMDD_HHMMSS}.wav
_VERSIONED_RE = re.compile(
    r"^combined_(.+)_(\d{8}_\d{6})\.wav$"
)

# Regex to extract filename values from PW filter-chain .conf files
_PW_FILENAME_RE = re.compile(r'filename\s*=\s*"([^"]+)"')


def deploy_filters(
    output_dir,
    coeffs_dir=DEFAULT_COEFFS_DIR,
    verified=False,
    dry_run=False,
    timestamp=None,
):
    """
    Deploy filter WAV files from output_dir to the PipeWire coefficients dir.

    Parameters
    ----------
    output_dir : str
        Directory containing the generated filter WAV files.
    coeffs_dir : str
        PipeWire filter-chain coefficients directory on the target system.
    verified : bool
        MUST be True. Deployment is refused if verification has not passed.
    dry_run : bool
        If True, print what would be done without actually copying.
    timestamp : datetime, optional
        If provided, looks for and deploys versioned filenames (TK-166).
        If None, deploys legacy unversioned filenames for backwards
        compatibility.

    Returns
    -------
    list of str
        Paths of deployed files.

    Raises
    ------
    RuntimeError
        If verified is False (safety interlock).
    """
    if not verified:
        raise RuntimeError(
            "DEPLOYMENT REFUSED: Filters have not passed verification. "
            "Run verify.run_all_checks() first and ensure all checks pass."
        )

    if timestamp is not None:
        filter_files = {
            channel: versioned_filename(channel, timestamp)
            for channel in CHANNEL_FILENAMES
        }
    else:
        filter_files = dict(CHANNEL_FILENAMES)

    deployed = []
    for channel, filename in filter_files.items():
        src = os.path.join(output_dir, filename)
        dst = os.path.join(coeffs_dir, filename)

        if not os.path.exists(src):
            print(f"  WARNING: {src} not found, skipping")
            continue

        if dry_run:
            print(f"  [DRY RUN] Would copy {src} -> {dst}")
        else:
            os.makedirs(coeffs_dir, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  Deployed: {dst}")
        deployed.append(dst)

    return deployed


class DeployRefused(RuntimeError):
    """A set failed check_deployable_set; ``issues`` lists every reason."""

    def __init__(self, issues):
        self.issues = list(issues)
        super().__init__("DEPLOYMENT REFUSED: " + "; ".join(self.issues))


def _is_production_root(coeffs_root):
    real = os.path.realpath(coeffs_root)
    return real in {os.path.realpath(PRODUCTION_COEFFS_DIR),
                    os.path.realpath(DEFAULT_COEFFS_DIR)}


def _simulated_issues(set_dir):
    # The venue runner's contract (venue_pipeline module doc, F-399): a set
    # is real only with no SIMULATED marker and a delays.yml that parses to
    # a mapping with ``simulated: false``.
    from .venue_pipeline import DELAYS_FILENAME, SIMULATED_FILENAME

    issues = []
    if os.path.lexists(os.path.join(set_dir, SIMULATED_FILENAME)):
        issues.append(f"{SIMULATED_FILENAME} marker present")
    delays = os.path.join(set_dir, DELAYS_FILENAME)
    if os.path.islink(delays) or not os.path.isfile(delays):
        issues.append(f"{DELAYS_FILENAME} missing or not a regular file")
        return issues
    try:
        with open(delays) as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        issues.append(f"{DELAYS_FILENAME} unparsable: {exc}")
        return issues
    if not isinstance(data, dict) or "simulated" not in data:
        issues.append(f"{DELAYS_FILENAME} has no 'simulated' field")
    elif data["simulated"] is not False:
        issues.append(f"{DELAYS_FILENAME} says simulated: {data['simulated']!r}")
    return issues


def _wav_header_issues(path, name, max_taps):
    try:
        info = sf.info(path)
    except Exception as exc:  # any unreadable header fails closed
        return [f"{name}: unreadable WAV header ({exc})"]
    issues = []
    if info.channels != 1:
        issues.append(f"{name}: {info.channels} channels, expected mono")
    if info.samplerate != SAMPLE_RATE:
        issues.append(f"{name}: {info.samplerate} Hz, expected {SAMPLE_RATE}")
    if info.subtype != "FLOAT":
        issues.append(f"{name}: subtype {info.subtype}, expected FLOAT")
    if not 0 < info.frames <= max_taps:
        issues.append(f"{name}: {info.frames} taps, expected 1..{max_taps}")
    return issues


def check_deployable_set(set_dir, expected_names, coeffs_root, *,
                         allow_simulated=False, max_taps=DEFAULT_TAPS):
    """
    Return every reason ``set_dir`` must not be deployed to ``coeffs_root``.

    An empty list means deployable. Pure: reads only, never raises on a bad
    set. Checks (US-174d AC, Architect Q3):

    - SIMULATED marker, or a delays.yml that is missing, unparsable or not
      ``simulated: false``. ``allow_simulated`` overrides this, except into
      the production coeffs root (compared by realpath).
    - Each expected name is a plain deployable basename and a top-level
      regular file in ``set_dir`` (no symlinks, nothing below it).
    - Each WAV header: mono, 48 kHz, FLOAT, 1..max_taps frames.
    """
    from .venue_pipeline import is_deployable_name

    if os.path.islink(set_dir) or not os.path.isdir(set_dir):
        return [f"set dir {set_dir} is not a plain directory"]

    issues = []
    simulated = _simulated_issues(set_dir)
    if simulated and not allow_simulated:
        issues.extend(simulated)
    elif simulated and _is_production_root(coeffs_root):
        issues.extend(simulated)
        issues.append(f"simulated set into the production coeffs root {coeffs_root}"
                      " (allow_simulated does not apply)")

    try:
        names = sorted(expected_names, key=str)
    except TypeError:
        names = []
    if not names:
        issues.append("no expected files")
    for name in names:
        if (not isinstance(name, str) or os.path.basename(name) != name
                or not is_deployable_name(name)):
            issues.append(f"{name!r}: not a deployable file name")
            continue
        path = os.path.join(set_dir, name)
        if os.path.islink(path) or not os.path.isfile(path):
            issues.append(f"{name}: missing or not a regular file")
            continue
        issues.extend(_wav_header_issues(path, name, max_taps))
    return issues


# Set-swap layout (Architect, US-174d Q2 option b): immutable versioned set
# dirs under <coeffs_root>/sets/<set-id>/, and the relative symlinks
# <coeffs_root>/current and <coeffs_root>/previous -> sets/<set-id>.
# Replacing ``current`` with rename(2) is the commit point.
SETS_DIRNAME = "sets"
CURRENT_LINK = "current"
PREVIOUS_LINK = "previous"
# Unreferenced sets kept besides current and previous.
KEEP_EXTRA_SETS = 3
_SET_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{12}$")
_SET_STAGING_PREFIX = ".staging-"


class RollbackFailed(RuntimeError):
    """Restoring the previous set (or reloading it) failed."""


def _fsync_path(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def make_set_id(set_dir, names, now=None):
    """UTC timestamp + short hash of the names and bytes deployed."""
    h = hashlib.sha256()
    for name in sorted(names):
        h.update(name.encode() + b"\0")
        with open(os.path.join(set_dir, name), "rb") as f:
            h.update(hashlib.sha256(f.read()).digest())
    now = now or datetime.now(timezone.utc)
    return f"{now.strftime('%Y%m%dT%H%M%SZ')}-{h.hexdigest()[:12]}"


def _stage_set(set_dir, names, coeffs_root, now=None):
    """
    Copy the names into sets/<set-id>/ (steps 1-4) and return the set id.

    The id hashes the staged bytes, and the staged copies are header-checked
    again, so what is renamed into place is what was checked. Never reuses
    an id.
    """
    sets = os.path.join(coeffs_root, SETS_DIRNAME)
    os.makedirs(sets, exist_ok=True)
    staging = os.path.join(sets, _SET_STAGING_PREFIX + secrets.token_hex(6))
    os.mkdir(staging)
    try:
        issues = []
        for name in names:
            dst = os.path.join(staging, name)
            shutil.copyfile(os.path.join(set_dir, name), dst, follow_symlinks=False)
            if os.path.islink(dst) or not os.path.isfile(dst):
                issues.append(f"{name}: not a regular file when staged")
                continue
            issues.extend(_wav_header_issues(dst, name, DEFAULT_TAPS))
            _fsync_path(dst)
        if issues:
            raise DeployRefused(issues)
        set_id = make_set_id(staging, names, now)
        final = os.path.join(sets, set_id)
        if os.path.lexists(final):
            raise DeployRefused([f"set id {set_id} already exists"])
        _fsync_path(staging)
        os.rename(staging, final)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    _fsync_path(sets)
    return set_id


def _link_target(coeffs_root, link):
    path = os.path.join(coeffs_root, link)
    return os.readlink(path) if os.path.islink(path) else None


def _point(coeffs_root, link, target):
    """Atomically make <coeffs_root>/<link> -> target, or remove it for None."""
    path = os.path.join(coeffs_root, link)
    if target is None:
        if os.path.lexists(path):
            os.remove(path)
        return
    tmp = os.path.join(coeffs_root, f".{link}.tmp-{os.getpid()}")
    if os.path.lexists(tmp):
        os.remove(tmp)
    os.symlink(target, tmp)
    os.replace(tmp, path)


class _Trial:
    def __init__(self, coeffs_root, set_id):
        self.coeffs_root = coeffs_root
        self.set_id = set_id
        self.committed = False

    def commit(self):
        if self.committed:
            raise RuntimeError(f"trial deploy of {self.set_id} already committed")
        self.committed = True


def _reload_or_raise(reload, what):
    if not reload():
        raise RuntimeError(f"convolver reload failed after {what}")


@contextlib.contextmanager
def trial_deploy(set_dir, expected_names, coeffs_root, *, reload=None,
                 allow_simulated=False, now=None):
    """
    Swap ``set_dir`` in as the current set; keep it only if committed.

    Architect, US-174d Q1/Q2. On enter: check_deployable_set (raises
    DeployRefused), copy into sets/<set-id>/, point ``previous`` at the old
    set and ``current`` at the new one, Reload. The body re-measures and
    calls ``.commit()`` on a pass. On exit without a commit (fail, invalid,
    exception, KeyboardInterrupt) ``current`` and ``previous`` go back to
    what they were and Reload runs again. A failed rollback is printed
    loudly and raised as RollbackFailed. After a commit, old sets are
    pruned (prune_sets). ``reload`` defaults to reload_convolver.
    """
    reload = reload or reload_convolver
    issues = check_deployable_set(set_dir, expected_names, coeffs_root,
                                  allow_simulated=allow_simulated)
    old_current = _link_target(coeffs_root, CURRENT_LINK)
    if old_current is None:
        issues.append(f"no {CURRENT_LINK} set in {coeffs_root} to roll back to")
    if issues:
        raise DeployRefused(issues)

    names = sorted(expected_names)
    old_previous = _link_target(coeffs_root, PREVIOUS_LINK)
    set_id = _stage_set(set_dir, names, coeffs_root, now)
    trial = _Trial(coeffs_root, set_id)
    swapped = False
    try:
        _point(coeffs_root, PREVIOUS_LINK, old_current)
        swapped = True
        _point(coeffs_root, CURRENT_LINK, os.path.join(SETS_DIRNAME, set_id))
        _fsync_path(coeffs_root)
        _reload_or_raise(reload, f"swapping in {set_id}")
        yield trial
    finally:
        if not trial.committed and swapped:
            try:
                _point(coeffs_root, CURRENT_LINK, old_current)
                _point(coeffs_root, PREVIOUS_LINK, old_previous)
                _fsync_path(coeffs_root)
                _reload_or_raise(reload, f"rolling back to {old_current}")
            except BaseException as exc:
                print(f"\n  !!! ROLLBACK FAILED: {coeffs_root}/{CURRENT_LINK} should be "
                      f"{old_current}: {exc}\n  !!! The convolver may be running "
                      f"set {set_id}. Check before any audio.", file=sys.stderr)
                raise RollbackFailed(f"rollback to {old_current} failed: {exc}") from exc
    if trial.committed:
        prune_sets(coeffs_root)


def deploy_venue_set(set_dir, expected_names, coeffs_root, *, measure,
                     reload=None, allow_simulated=False, now=None):
    """
    Deploy a venue set behind the measured gate (US-174d).

    ``measure()`` re-measures with the new set live and returns
    ``(channels, system)`` for closed_loop.measured_gate. Only PASS
    commits; FAIL and INVALID (repeat the measurement) keep the previous
    filters. Returns the MeasuredGateResult.
    """
    from .closed_loop import Verdict, measured_gate

    with trial_deploy(set_dir, expected_names, coeffs_root, reload=reload,
                      allow_simulated=allow_simulated, now=now) as trial:
        channels, system = measure()
        result = measured_gate(channels, system)
        if result.verdict is Verdict.PASS:
            trial.commit()
    return result


def prune_sets(coeffs_root, keep=KEEP_EXTRA_SETS):
    """
    Remove old unreferenced set dirs; return the removed paths.

    Keeps whatever ``current`` and ``previous`` resolve to (by realpath),
    the ``keep`` newest other set ids, and anything that is not a set id
    (e.g. the dirac seed). Leftover staging dirs are removed. Call only
    after a commit, never during a trial.
    """
    sets = os.path.join(coeffs_root, SETS_DIRNAME)
    if not os.path.isdir(sets):
        return []
    referenced = {os.path.realpath(os.path.join(coeffs_root, link))
                  for link in (CURRENT_LINK, PREVIOUS_LINK)
                  if os.path.lexists(os.path.join(coeffs_root, link))}
    ids, removed = [], []
    for entry in os.listdir(sets):
        path = os.path.join(sets, entry)
        if os.path.islink(path) or not os.path.isdir(path):
            continue
        if os.path.realpath(path) in referenced:
            continue
        if entry.startswith(_SET_STAGING_PREFIX):
            removed.append(path)
        elif _SET_ID_RE.match(entry):
            ids.append(entry)
    ids.sort()
    removed.extend(os.path.join(sets, i) for i in ids[:max(len(ids) - keep, 0)])
    for path in removed:
        shutil.rmtree(path)
    if removed:
        _fsync_path(sets)
    return removed


def deploy_pw_config(
    conf_content,
    pw_conf_dir=DEFAULT_PW_CONF_DIR,
    conf_name=DEFAULT_PW_CONF_NAME,
    dry_run=False,
):
    """
    Deploy a PipeWire filter-chain .conf drop-in file.

    Parameters
    ----------
    conf_content : str
        The complete .conf file content (from pw_config_generator).
    pw_conf_dir : str
        PipeWire config drop-in directory.
    conf_name : str
        Filename for the drop-in config.
    dry_run : bool
        If True, print what would be done without writing.

    Returns
    -------
    str
        Path to the deployed config file.
    """
    dst = os.path.join(pw_conf_dir, conf_name)

    if dry_run:
        print(f"  [DRY RUN] Would write PW config to {dst}")
        return dst

    os.makedirs(pw_conf_dir, exist_ok=True)
    with open(dst, "w") as f:
        f.write(conf_content)
    print(f"  Deployed PW config: {dst}")
    return dst


def list_versioned_files(channel, coeffs_dir=DEFAULT_COEFFS_DIR):
    """
    List all versioned coefficient files for a channel, sorted oldest first.

    Parameters
    ----------
    channel : str
        Channel name, e.g. 'left_hp', 'sub1_lp'.
    coeffs_dir : str
        Directory to search.

    Returns
    -------
    list of str
        Absolute paths sorted by timestamp (oldest first).
    """
    pattern = os.path.join(coeffs_dir, f"combined_{channel}_*.wav")
    matches = []
    for path in glob.glob(pattern):
        basename = os.path.basename(path)
        m = _VERSIONED_RE.match(basename)
        if m and m.group(1) == channel:
            matches.append((m.group(2), path))
    matches.sort(key=lambda x: x[0])
    return [path for _, path in matches]


def _get_active_filenames(pw_conf_dir=DEFAULT_PW_CONF_DIR):
    """
    Parse PipeWire filter-chain .conf files for active FIR coefficient filenames.

    Scans all .conf files in the PW config drop-in directory for
    ``filename = "/path/to/file.wav"`` entries in convolver node configs.

    Returns an empty set if the directory doesn't exist or no filenames found.
    """
    active = set()
    if not os.path.isdir(pw_conf_dir):
        return active

    for conf_file in glob.glob(os.path.join(pw_conf_dir, "*.conf")):
        try:
            with open(conf_file, "r") as f:
                content = f.read()
        except OSError:
            continue

        for match in _PW_FILENAME_RE.finditer(content):
            fname = match.group(1)
            if fname:
                active.add(os.path.basename(fname))

    return active


def cleanup_old_coefficients(
    coeffs_dir=DEFAULT_COEFFS_DIR,
    keep=2,
    dry_run=False,
    pw_conf_dir=DEFAULT_PW_CONF_DIR,
):
    """
    Remove old versioned coefficient files, keeping the last N versions.

    Never deletes the currently-active version (checked by parsing PipeWire
    filter-chain config files for referenced filenames).

    Parameters
    ----------
    coeffs_dir : str
        PipeWire filter-chain coefficients directory.
    keep : int
        Number of most recent versions to keep per channel.
    dry_run : bool
        If True, print what would be deleted without actually deleting.
    pw_conf_dir : str
        PipeWire config drop-in directory (for active file detection).

    Returns
    -------
    list of str
        Paths of deleted (or would-be-deleted) files.
    """
    active_basenames = _get_active_filenames(pw_conf_dir)
    deleted = []

    for channel in CHANNEL_FILENAMES:
        versions = list_versioned_files(channel, coeffs_dir)
        if len(versions) <= keep:
            continue

        to_remove = versions[:-keep]
        for path in to_remove:
            basename = os.path.basename(path)
            if basename in active_basenames:
                print(f"  SKIP (active): {basename}")
                continue
            if dry_run:
                print(f"  [DRY RUN] Would delete {path}")
            else:
                os.remove(path)
                print(f"  Deleted: {path}")
            deleted.append(path)

    return deleted


def reload_pipewire():
    """
    Reload the PipeWire filter-chain by restarting PipeWire.

    WARNING: Restarting PipeWire resets the USBStreamer, producing transients
    through the amplifier chain that can damage speakers. The caller MUST
    ensure amplifiers are off or muted before calling this function.

    Reload strategy (checked in order):
    1. PI4AUDIO_PW_RELOAD_CMD env var — custom shell command (used by
       local-demo where PipeWire is not managed by systemd).
    2. systemctl --user restart pipewire.service — production (Pi).
    3. If neither is available, prints instructions and returns False.

    Returns
    -------
    bool
        True if reload succeeded, False if skipped or failed.
    """
    import subprocess

    # Strategy 1: custom reload command (local-demo, CI, etc.)
    # shell=True is safe — env var is set at deployment time
    # (local-demo.sh / systemd unit), never from user/browser input.
    reload_cmd = os.environ.get("PI4AUDIO_PW_RELOAD_CMD")
    if reload_cmd:
        try:
            print(f"\n  Using custom PW reload command: {reload_cmd}")
            result = subprocess.run(
                reload_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                print("  PipeWire reloaded successfully (custom command).")
                return True
            else:
                print(f"  WARNING: Custom PW reload failed: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            print("  WARNING: Custom PW reload timed out after 30s.")
            return False
        except Exception as e:
            print(f"  WARNING: Custom PW reload failed: {e}")
            return False

    # Strategy 2: systemctl (production Pi with systemd)
    if shutil.which("systemctl") is None:
        print(
            "\n  systemctl not available (expected on macOS dev)."
            "\n  To reload PipeWire on the Pi:"
            "\n    systemctl --user restart pipewire.service"
            "\n"
            "\n  WARNING: Restarting PipeWire resets the USBStreamer!"
            "\n  Ensure amplifiers are OFF or MUTED before restarting."
            "\n"
        )
        return False

    try:
        print(
            "\n  WARNING: Restarting PipeWire will reset the USBStreamer."
            "\n  Ensure amplifiers are OFF or MUTED."
        )
        result = subprocess.run(
            ["systemctl", "--user", "restart", "pipewire.service"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            print("  PipeWire restarted successfully.")
            return True
        else:
            print(f"  WARNING: PipeWire restart failed: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print("  WARNING: PipeWire restart timed out after 15s.")
        return False
    except Exception as e:
        print(f"  WARNING: PipeWire restart failed: {e}")
        return False


def _find_node_id(node_name: str) -> str | None:
    """Find the PipeWire object ID for a node by name.

    Parses ``pw-cli list-objects Node`` output for lines like::

        id 42, type PipeWire:Interface:Node/3
          node.name = "pi4audio-convolver"

    Returns the object ID as a string, or None if not found.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["pw-cli", "list-objects", "Node"],
            capture_output=True, text=True, timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    current_id = None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("id ") and "type PipeWire:Interface:Node" in stripped:
            parts = stripped.split(",", 1)
            current_id = parts[0].split()[1] if len(parts[0].split()) >= 2 else None
        elif current_id and f'node.name = "{node_name}"' in stripped:
            return current_id
    return None


def reload_convolver(node_name: str = "pi4audio-convolver",
                     timeout_s: float = 5.0) -> bool:
    """Reload convolver coefficients via the Reload control port (US-112).

    Sets the ``Reload`` control parameter to 1.0 on the convolver node,
    triggering an in-place coefficient reload.  The node stays alive, all
    PipeWire links remain connected, and coefficients are swapped via an
    instantaneous pointer swap with no audio dropout.

    Requires the patched PipeWire with convolver-reload support
    (``nix/patches/pipewire-convolver-reload.patch``).

    Returns
    -------
    bool
        True if the reload was triggered and the node is still alive.
    """
    import subprocess

    node_id = _find_node_id(node_name)
    if node_id is None:
        print(f"  WARNING: Convolver node '{node_name}' not found.")
        return False

    print(f"  Convolver node '{node_name}' has ID {node_id}.")

    try:
        result = subprocess.run(
            ["pw-cli", "s", node_id, "Props",
             '{ params = [ "Reload" 1.0 ] }'],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            print(f"  WARNING: pw-cli set Props failed: {result.stderr.strip()}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        print(f"  WARNING: pw-cli set Props failed: {exc}")
        return False

    verified_id = _find_node_id(node_name)
    if verified_id == node_id:
        print(f"  Convolver '{node_name}' reloaded (node ID {node_id} preserved).")
        return True

    print(f"  WARNING: Convolver node ID changed ({node_id} -> {verified_id}) "
          f"or node disappeared after reload.")
    return False
