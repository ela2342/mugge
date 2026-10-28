#!/usr/bin/env python3
"""Pi 5 thermal watch for load runs (US-173 AC9, D-069 thermal rule).

Samples every --interval seconds (default 10) and prints one labeled line
per sample:

    ts=<utc> temp_c=<C> cur_khz=<kHz> max_khz=<kHz> governor=<g>
    cooling=<dev>:<type>:<state>,... undervolt_alarm=<0|1> status=<S>

Status per sample:
    OK       below 75 C and all validity checks pass
    WARN     temp >= 75 C: warn the owner via team-lead, keep running
    STOP     temp >= 80 C: firmware throttling starts here, stop the load
    INVALID  a cooling device is non-zero, the undervoltage alarm is set,
             cur_khz < max_khz, the governor is not "performance", or a
             field could not be read (printed as MISSING). Invalid is a
             finding (repeat the run), not a STOP.

A sample can be both STOP/WARN and INVALID; the line then shows e.g.
status=WARN,INVALID with reason=... naming each failed check.

cpuinfo_cur_freq is root-only (0400) on the Pi 5. If it cannot be read
directly, the watch retries with `sudo -n cat` (passwordless sudo on the
Pi). With --no-sudo it is reported as MISSING instead.

Exit codes:
    0  run completed, every sample OK or WARN
    1  usage or setup error
    2  STOP (exits at the first STOP sample)
    3  run completed but at least one sample was INVALID

--sysfs-root points at a fake tree for tests.
"""

import argparse
import datetime
import glob
import os
import subprocess
import sys
import time

WARN_C = 75.0
STOP_C = 80.0

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_STOP = 2
EXIT_INVALID = 3

MISSING = "MISSING"


class Reader:
    def __init__(self, root="/", use_sudo=True):
        self.root = root
        self.use_sudo = use_sudo

    def path(self, rel):
        return os.path.join(self.root, rel.lstrip("/"))

    def read(self, rel, privileged=False):
        """Return the stripped file content, or None if unreadable."""
        p = self.path(rel)
        try:
            with open(p) as f:
                return f.read().strip()
        except PermissionError:
            if not (privileged and self.use_sudo):
                return None
        except OSError:
            return None
        try:
            out = subprocess.run(
                ["sudo", "-n", "cat", p],
                capture_output=True, text=True, timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if out.returncode != 0:
            return None
        return out.stdout.strip()

    def glob(self, pattern):
        return sorted(glob.glob(self.path(pattern)))


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def sample(reader):
    """Read one sample. Returns a dict; unreadable fields are None."""
    s = {}
    milli = _int(reader.read("/sys/class/thermal/thermal_zone0/temp"))
    s["temp_c"] = None if milli is None else milli / 1000.0
    cpu = "/sys/devices/system/cpu/cpu0/cpufreq/"
    s["cur_khz"] = _int(reader.read(cpu + "cpuinfo_cur_freq", privileged=True))
    s["max_khz"] = _int(reader.read(cpu + "cpuinfo_max_freq"))
    s["governor"] = reader.read(cpu + "scaling_governor")

    cooling = []
    for d in reader.glob("/sys/class/thermal/cooling_device*"):
        name = os.path.basename(d)
        rel = "/sys/class/thermal/" + name + "/"
        cooling.append((name, reader.read(rel + "type"),
                        _int(reader.read(rel + "cur_state"))))
    s["cooling"] = cooling

    s["undervolt_alarm"] = None
    for name_file in reader.glob("/sys/class/hwmon/hwmon*/name"):
        with open(name_file) as f:
            if f.read().strip() != "rpi_volt":
                continue
        hw = os.path.basename(os.path.dirname(name_file))
        s["undervolt_alarm"] = _int(
            reader.read("/sys/class/hwmon/" + hw + "/in0_lcrit_alarm"))
        break
    return s


def classify(s):
    """Return (statuses, reasons) for one sample."""
    statuses = []
    reasons = []
    t = s["temp_c"]
    if t is None:
        reasons.append("temp_missing")
    elif t >= STOP_C:
        statuses.append("STOP")
    elif t >= WARN_C:
        statuses.append("WARN")

    if s["cur_khz"] is None:
        reasons.append("cur_freq_missing")
    if s["max_khz"] is None:
        reasons.append("max_freq_missing")
    if (s["cur_khz"] is not None and s["max_khz"] is not None
            and s["cur_khz"] < s["max_khz"]):
        reasons.append("below_max_freq")
    if s["governor"] is None:
        reasons.append("governor_missing")
    elif s["governor"] != "performance":
        reasons.append("governor_not_performance")
    if not s["cooling"]:
        reasons.append("no_cooling_devices")
    for name, _type, state in s["cooling"]:
        if state is None:
            reasons.append(name + "_missing")
        elif state != 0:
            reasons.append(name + "_active")
    if s["undervolt_alarm"] is None:
        reasons.append("undervolt_alarm_missing")
    elif s["undervolt_alarm"] != 0:
        reasons.append("undervolt_alarm_set")

    if reasons:
        statuses.append("INVALID")
    if not statuses:
        statuses.append("OK")
    return statuses, reasons


def _fmt(value):
    return MISSING if value is None else str(value)


def format_line(ts, s, statuses, reasons):
    temp = MISSING if s["temp_c"] is None else "%.2f" % s["temp_c"]
    cooling = ",".join(
        "%s:%s:%s" % (n, _fmt(t), _fmt(st)) for n, t, st in s["cooling"]
    ) or MISSING
    line = ("ts=%s temp_c=%s cur_khz=%s max_khz=%s governor=%s cooling=%s "
            "undervolt_alarm=%s status=%s" % (
                ts, temp, _fmt(s["cur_khz"]), _fmt(s["max_khz"]),
                _fmt(s["governor"]), cooling, _fmt(s["undervolt_alarm"]),
                ",".join(statuses)))
    if reasons:
        line += " reason=" + ",".join(reasons)
    return line


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def run(reader, interval, count, out, err, clock=_utc_now, sleep=time.sleep):
    """Sample count times (0 = until STOP or Ctrl-C). Returns exit code."""
    invalid = False
    n = 0
    try:
        while count == 0 or n < count:
            if n:
                sleep(interval)
            s = sample(reader)
            statuses, reasons = classify(s)
            out.write(format_line(clock(), s, statuses, reasons) + "\n")
            out.flush()
            n += 1
            if "INVALID" in statuses:
                invalid = True
            if "STOP" in statuses:
                err.write("STOP: %.2f C >= %.0f C, stop the load now\n"
                          % (s["temp_c"], STOP_C))
                return EXIT_STOP
            if "WARN" in statuses:
                err.write("WARN: %.2f C >= %.0f C, tell the owner via "
                          "team-lead\n" % (s["temp_c"], WARN_C))
    except KeyboardInterrupt:
        pass
    return EXIT_INVALID if invalid else EXIT_OK


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--interval", type=float, default=10.0,
                    help="seconds between samples (default 10)")
    ap.add_argument("--count", type=int, default=0,
                    help="number of samples, 0 = until STOP or Ctrl-C")
    ap.add_argument("--duration", type=float, default=None,
                    help="run length in seconds (sets --count)")
    ap.add_argument("--sysfs-root", default="/",
                    help="root of the sysfs tree (tests use a fake tree)")
    ap.add_argument("--no-sudo", action="store_true",
                    help="never retry root-only reads with sudo -n")
    args = ap.parse_args(argv)
    if args.interval <= 0:
        ap.error("--interval must be > 0")
    count = args.count
    if args.duration is not None:
        count = int(round(args.duration / args.interval)) + 1
    reader = Reader(args.sysfs_root, use_sudo=not args.no_sudo)
    return run(reader, args.interval, count, sys.stdout, sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
