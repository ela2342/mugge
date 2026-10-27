"""Fake-sysfs tests for pi5_thermal_watch (US-173 AC9, D-069 thermal rule).

Run with plain python3 (stdlib only):
    python3 -m unittest discover -s scripts/stability/tests
"""

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pi5_thermal_watch as tw  # noqa: E402

CPU = "sys/devices/system/cpu/cpu0/cpufreq"


class FakeSysfs:
    """A Pi 5-shaped sysfs tree, healthy by default (60 C, full speed)."""

    def __init__(self, root):
        self.root = Path(root)
        self.set("sys/class/thermal/thermal_zone0/temp", "60000")
        self.set(CPU + "/cpuinfo_cur_freq", "2400000")
        self.set(CPU + "/cpuinfo_max_freq", "2400000")
        self.set(CPU + "/scaling_governor", "performance")
        self.set("sys/class/thermal/cooling_device0/type", "cpufreq-cpu0")
        self.set("sys/class/thermal/cooling_device0/cur_state", "0")
        # rpi_volt is deliberately not hwmon0 to prove the name lookup.
        self.set("sys/class/hwmon/hwmon0/name", "cpu_thermal")
        self.set("sys/class/hwmon/hwmon1/name", "rpi_volt")
        self.set("sys/class/hwmon/hwmon1/in0_lcrit_alarm", "0")

    def set(self, rel, value):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value + "\n")

    def remove(self, rel):
        (self.root / rel).unlink()


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fs = FakeSysfs(self._tmp.name)
        self.reader = tw.Reader(self._tmp.name, use_sudo=False)

    def tearDown(self):
        self._tmp.cleanup()

    def classify(self):
        return tw.classify(tw.sample(self.reader))

    def run_watch(self, count=1, temps=None):
        out, err = io.StringIO(), io.StringIO()
        seq = iter(temps or [])

        def sleep(_):
            t = next(seq, None)
            if t is not None:
                self.fs.set("sys/class/thermal/thermal_zone0/temp", t)

        rc = tw.run(self.reader, 10, count, out, err,
                    clock=lambda: "T", sleep=sleep)
        return rc, out.getvalue().splitlines(), err.getvalue()


class TestThresholds(Base):
    def test_healthy_is_ok(self):
        self.assertEqual(self.classify(), (["OK"], []))

    def test_just_below_warn_is_ok(self):
        self.fs.set("sys/class/thermal/thermal_zone0/temp", "74999")
        self.assertEqual(self.classify()[0], ["OK"])

    def test_75_is_warn(self):
        self.fs.set("sys/class/thermal/thermal_zone0/temp", "75000")
        self.assertEqual(self.classify(), (["WARN"], []))

    def test_80_is_stop(self):
        self.fs.set("sys/class/thermal/thermal_zone0/temp", "80000")
        self.assertEqual(self.classify(), (["STOP"], []))


class TestValidity(Base):
    def assert_invalid(self, reason):
        statuses, reasons = self.classify()
        self.assertIn("INVALID", statuses)
        self.assertIn(reason, reasons)

    def test_below_max_freq(self):
        self.fs.set(CPU + "/cpuinfo_cur_freq", "1500000")
        self.assert_invalid("below_max_freq")

    def test_governor_not_performance(self):
        self.fs.set(CPU + "/scaling_governor", "ondemand")
        self.assert_invalid("governor_not_performance")

    def test_cooling_device_active(self):
        self.fs.set("sys/class/thermal/cooling_device0/cur_state", "1")
        self.assert_invalid("cooling_device0_active")

    def test_every_cooling_device_checked(self):
        self.fs.set("sys/class/thermal/cooling_device1/type", "cpufreq-cpu1")
        self.fs.set("sys/class/thermal/cooling_device1/cur_state", "2")
        statuses, reasons = self.classify()
        self.assertEqual(reasons, ["cooling_device1_active"])

    def test_no_cooling_devices(self):
        self.fs.remove("sys/class/thermal/cooling_device0/cur_state")
        self.fs.remove("sys/class/thermal/cooling_device0/type")
        os.rmdir(self.fs.root / "sys/class/thermal/cooling_device0")
        self.assert_invalid("no_cooling_devices")

    def test_undervolt_alarm_set(self):
        self.fs.set("sys/class/hwmon/hwmon1/in0_lcrit_alarm", "1")
        self.assert_invalid("undervolt_alarm_set")

    def test_no_rpi_volt_hwmon(self):
        self.fs.set("sys/class/hwmon/hwmon1/name", "other")
        self.assert_invalid("undervolt_alarm_missing")

    def test_warn_and_invalid_together(self):
        self.fs.set("sys/class/thermal/thermal_zone0/temp", "76000")
        self.fs.set(CPU + "/cpuinfo_cur_freq", "1800000")
        statuses, reasons = self.classify()
        self.assertEqual(statuses, ["WARN", "INVALID"])
        self.assertEqual(reasons, ["below_max_freq"])


class TestMissingFields(Base):
    """T54 lesson: a missing field must be labeled, never look like 0."""

    @unittest.skipIf(os.geteuid() == 0, "root reads 0400 files anyway")
    def test_root_only_cur_freq_without_sudo_is_missing(self):
        os.chmod(self.fs.root / CPU / "cpuinfo_cur_freq", 0)
        rc, lines, _ = self.run_watch()
        self.assertEqual(rc, tw.EXIT_INVALID)
        self.assertIn("cur_khz=MISSING", lines[0])
        self.assertIn("cur_freq_missing", lines[0])
        self.assertNotIn("below_max_freq", lines[0])

    def test_missing_temp(self):
        self.fs.remove("sys/class/thermal/thermal_zone0/temp")
        rc, lines, _ = self.run_watch()
        self.assertEqual(rc, tw.EXIT_INVALID)
        self.assertIn("temp_c=MISSING", lines[0])
        self.assertIn("temp_missing", lines[0])

    def test_missing_cooling_state_is_labeled(self):
        self.fs.remove("sys/class/thermal/cooling_device0/cur_state")
        rc, lines, _ = self.run_watch()
        self.assertIn("cooling=cooling_device0:cpufreq-cpu0:MISSING", lines[0])
        self.assertIn("undervolt_alarm=0", lines[0])
        self.assertIn("cooling_device0_missing", lines[0])

    def test_garbage_value_is_missing(self):
        self.fs.set(CPU + "/cpuinfo_max_freq", "n/a")
        rc, lines, _ = self.run_watch()
        self.assertIn("max_khz=MISSING", lines[0])


class TestRun(Base):
    def test_line_format(self):
        rc, lines, err = self.run_watch()
        self.assertEqual(rc, tw.EXIT_OK)
        self.assertEqual(lines, [
            "ts=T temp_c=60.00 cur_khz=2400000 max_khz=2400000 "
            "governor=performance cooling=cooling_device0:cpufreq-cpu0:0 "
            "undervolt_alarm=0 status=OK"])
        self.assertEqual(err, "")

    def test_warn_keeps_running(self):
        rc, lines, err = self.run_watch(count=3, temps=["76000", "70000"])
        self.assertEqual(rc, tw.EXIT_OK)
        self.assertEqual(len(lines), 3)
        self.assertIn("status=WARN", lines[1])
        self.assertIn("WARN: 76.00 C", err)

    def test_stop_exits_at_first_stop(self):
        rc, lines, err = self.run_watch(count=5, temps=["80500", "60000"])
        self.assertEqual(rc, tw.EXIT_STOP)
        self.assertEqual(len(lines), 2)
        self.assertIn("status=STOP", lines[1])
        self.assertIn("STOP: 80.50 C", err)

    def test_stop_wins_over_invalid(self):
        self.fs.set(CPU + "/cpuinfo_cur_freq", "1500000")
        rc, lines, _ = self.run_watch(count=3, temps=["81000"])
        self.assertEqual(rc, tw.EXIT_STOP)

    def test_one_invalid_sample_marks_run_invalid(self):
        out, err = io.StringIO(), io.StringIO()
        states = iter(["1", "0"])

        def sleep(_):
            self.fs.set("sys/class/thermal/cooling_device0/cur_state",
                        next(states))

        rc = tw.run(self.reader, 10, 3, out, err,
                    clock=lambda: "T", sleep=sleep)
        self.assertEqual(rc, tw.EXIT_INVALID)
        lines = out.getvalue().splitlines()
        self.assertIn("status=INVALID", lines[1])
        self.assertIn("status=OK", lines[2])

    def test_ctrl_c_keeps_invalid(self):
        self.fs.set(CPU + "/scaling_governor", "powersave")
        out, err = io.StringIO(), io.StringIO()

        def sleep(_):
            raise KeyboardInterrupt

        rc = tw.run(self.reader, 10, 0, out, err,
                    clock=lambda: "T", sleep=sleep)
        self.assertEqual(rc, tw.EXIT_INVALID)

    def test_duration_sets_count(self):
        out = io.StringIO()
        saved = sys.stdout
        sys.stdout = out
        try:
            rc = tw.main(["--sysfs-root", str(self.fs.root), "--no-sudo",
                          "--interval", "0.01", "--duration", "0.03"])
        finally:
            sys.stdout = saved
        self.assertEqual(rc, tw.EXIT_OK)
        self.assertEqual(len(out.getvalue().splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
