"""
Unit tests for speaker driver YAML validation module (US-039).

Tests cover:
  - Valid driver records pass validation
  - Missing required fields produce errors
  - Invalid types produce errors
  - Invalid enum values produce errors
  - Physical consistency checks (Qts, Vd, EBP)
  - Warnings for missing optional fields
  - Data file existence checks
  - Schema version validation
  - Real driver records from configs/drivers/ pass validation
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

sys_path = os.path.join(os.path.dirname(__file__), "..")
import sys
sys.path.insert(0, sys_path)

from validate_driver import (
    ValidationResult,
    validate_driver,
    validate_all_drivers,
    DRIVER_TYPES,
    TS_PARAMETER_SOURCES,
    MAGNET_TYPES,
    CONE_MATERIALS,
    SURROUND_MATERIALS,
    CONDITIONS,
    MEASUREMENT_SOURCES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_valid_driver():
    """Return a minimal valid driver record dict."""
    return {
        "schema_version": 1,
        "metadata": {
            "id": "test-driver-01",
            "manufacturer": "TestCo",
            "model": "TD-01",
            "driver_type": "woofer",
            "nominal_diameter_in": 6.5,
            "actual_diameter_mm": None,
            "magnet_type": None,
            "cone_material": None,
            "surround_material": None,
            "voice_coil_diameter_mm": None,
            "weight_kg": None,
            "mounting": {
                "cutout_diameter_mm": 145.0,
                "bolt_circle_diameter_mm": 166.0,
                "bolt_count": 6,
                "overall_depth_mm": 90.0,
                "flange_diameter_mm": 176.0,
            },
            "datasheet_url": None,
            "datasheet_file": None,
            "ts_parameter_source": "manufacturer",
            "ts_measurement_date": None,
            "ts_measurement_notes": "",
            "notes": "",
            "quantity_owned": None,
            "serial_numbers": [],
            "purchase_date": None,
            "condition": None,
        },
        "thiele_small": {
            "fs_hz": 33.0,
            "re_ohm": 3.7,
            "z_nom_ohm": 4,
            "qts": round((0.27 * 6.3) / (0.27 + 6.3), 4),  # Consistent with Qes/Qms
            "qes": 0.27,
            "qms": 6.3,
            "vas_liters": 28.9,
            "cms_m_per_n": 0.0011,
            "xmax_mm": 5.9,
            "xmech_mm": None,
            "le_mh": 0.32,
            "bl_tm": 7.7,
            "mms_g": 21.1,
            "mmd_g": None,
            "sd_cm2": 132.7,
            "sensitivity_db_1w1m": None,
            "sensitivity_db_2v83_1m": 90.3,
            "pe_max_watts": 250.0,
            "pe_peak_watts": None,
            "power_handling_note": "",
            "eta0_percent": None,
            "vd_cm3": None,
        },
        "measurements": {
            "impedance_curve": {
                "source": None,
                "date": None,
                "conditions": "",
                "data_file": None,
            },
            "frequency_response": {
                "source": None,
                "date": None,
                "conditions": "",
                "reference_distance_m": None,
                "data_file": None,
            },
            "nearfield_response": {
                "source": None,
                "date": None,
                "data_file": None,
            },
            "distortion": {
                "data_file": None,
                "test_level_db_spl": None,
            },
        },
        "application_notes": [],
    }


def _write_driver(tmpdir, driver_id, data):
    """Write a driver YAML to a temp directory and return the path."""
    driver_dir = Path(tmpdir) / driver_id
    driver_dir.mkdir(parents=True, exist_ok=True)
    (driver_dir / "data").mkdir(exist_ok=True)
    driver_path = driver_dir / "driver.yml"
    with open(driver_path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False)
    return driver_path


# ---------------------------------------------------------------------------
# Basic valid/invalid tests
# ---------------------------------------------------------------------------

class TestValidDriverPasses:
    def test_minimal_valid(self, tmp_path):
        data = _minimal_valid_driver()
        path = _write_driver(tmp_path, "test-driver-01", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid, got errors: {result.errors}"

    def test_valid_with_all_optional_fields(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["magnet_type"] = "neodymium"
        data["metadata"]["cone_material"] = "aluminum"
        data["metadata"]["surround_material"] = "rubber"
        data["metadata"]["weight_kg"] = 1.5
        data["metadata"]["condition"] = "new"
        data["metadata"]["quantity_owned"] = 2
        data["thiele_small"]["xmech_mm"] = 12.0
        data["thiele_small"]["mmd_g"] = 18.0
        data["thiele_small"]["sensitivity_db_1w1m"] = 87.5
        data["thiele_small"]["pe_peak_watts"] = 500.0
        path = _write_driver(tmp_path, "test-driver-01", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid, got errors: {result.errors}"

    def test_tweeter_no_ts_params(self, tmp_path):
        """Tweeters often have no T/S params -- should be valid."""
        data = _minimal_valid_driver()
        data["metadata"]["driver_type"] = "tweeter"
        data["thiele_small"] = {
            "fs_hz": None,
            "re_ohm": None,
            "z_nom_ohm": 4,
            "qts": None,
            "qes": None,
            "qms": None,
            "vas_liters": None,
            "cms_m_per_n": None,
            "xmax_mm": None,
            "xmech_mm": None,
            "le_mh": None,
            "bl_tm": None,
            "mms_g": None,
            "mmd_g": None,
            "sd_cm2": None,
            "sensitivity_db_1w1m": None,
            "sensitivity_db_2v83_1m": 96.0,
            "pe_max_watts": 20.0,
            "pe_peak_watts": 40.0,
            "power_handling_note": "",
            "eta0_percent": None,
            "vd_cm3": None,
        }
        path = _write_driver(tmp_path, "test-tweeter-01", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid, got errors: {result.errors}"


class TestRequiredFields:
    def test_missing_metadata_id(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["id"] = None
        path = _write_driver(tmp_path, "test-bad-01", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("metadata.id" in e for e in result.errors)

    def test_empty_metadata_id(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["id"] = ""
        path = _write_driver(tmp_path, "test-bad-01", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("metadata.id" in e for e in result.errors)

    def test_missing_manufacturer(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["manufacturer"] = None
        path = _write_driver(tmp_path, "test-bad-02", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("metadata.manufacturer" in e for e in result.errors)

    def test_missing_model(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["model"] = None
        path = _write_driver(tmp_path, "test-bad-03", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("metadata.model" in e for e in result.errors)

    def test_missing_recommended_ts_when_others_present(self, tmp_path):
        """If fs_hz is present, missing core T/S fields produce warnings."""
        data = _minimal_valid_driver()
        data["thiele_small"]["qts"] = None  # Remove one recommended field
        path = _write_driver(tmp_path, "test-bad-04", data)
        result = validate_driver(path, check_files=False)
        # Should still be valid (warning, not error) but warn about missing qts
        assert result.valid, f"Expected valid, got errors: {result.errors}"
        assert any("thiele_small.qts" in w for w in result.warnings)

    def test_missing_schema_version(self, tmp_path):
        data = _minimal_valid_driver()
        del data["schema_version"]
        path = _write_driver(tmp_path, "test-bad-05", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("schema_version" in e for e in result.errors)

    def test_wrong_schema_version(self, tmp_path):
        data = _minimal_valid_driver()
        data["schema_version"] = 99
        path = _write_driver(tmp_path, "test-bad-06", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("schema_version" in e for e in result.errors)


class TestTypeValidation:
    def test_fs_hz_string_rejected(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"]["fs_hz"] = "thirty-three"
        path = _write_driver(tmp_path, "test-type-01", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("fs_hz" in e and "expected" in e for e in result.errors)

    def test_negative_pe_max_rejected(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"]["pe_max_watts"] = -10
        path = _write_driver(tmp_path, "test-type-02", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("pe_max_watts" in e for e in result.errors)

    def test_zero_re_ohm_rejected(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"]["re_ohm"] = 0
        path = _write_driver(tmp_path, "test-type-03", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("re_ohm" in e for e in result.errors)

    def test_metadata_not_dict(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"] = "not a dict"
        path = _write_driver(tmp_path, "test-type-04", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("metadata" in e and "mapping" in e for e in result.errors)

    def test_thiele_small_not_dict(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"] = "not a dict"
        path = _write_driver(tmp_path, "test-type-05", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("thiele_small" in e and "mapping" in e for e in result.errors)

    def test_serial_numbers_not_list(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["serial_numbers"] = "SN12345"
        path = _write_driver(tmp_path, "test-type-06", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("serial_numbers" in e for e in result.errors)

    def test_application_notes_not_list(self, tmp_path):
        data = _minimal_valid_driver()
        data["application_notes"] = "some text"
        path = _write_driver(tmp_path, "test-type-07", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("application_notes" in e for e in result.errors)

    def test_quantity_owned_negative(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["quantity_owned"] = -1
        path = _write_driver(tmp_path, "test-type-08", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("quantity_owned" in e for e in result.errors)


class TestEnumValidation:
    def test_invalid_driver_type(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["driver_type"] = "speaker"
        path = _write_driver(tmp_path, "test-enum-01", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("driver_type" in e for e in result.errors)

    def test_invalid_ts_parameter_source(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["ts_parameter_source"] = "guessed"
        path = _write_driver(tmp_path, "test-enum-02", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("ts_parameter_source" in e for e in result.errors)

    def test_invalid_magnet_type(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["magnet_type"] = "ceramic"
        path = _write_driver(tmp_path, "test-enum-03", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("magnet_type" in e for e in result.errors)

    def test_invalid_condition(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["condition"] = "broken"
        path = _write_driver(tmp_path, "test-enum-04", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("condition" in e for e in result.errors)

    def test_invalid_measurement_source(self, tmp_path):
        data = _minimal_valid_driver()
        data["measurements"]["impedance_curve"]["source"] = "unknown"
        path = _write_driver(tmp_path, "test-enum-05", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("source" in e for e in result.errors)

    def test_all_valid_driver_types(self, tmp_path):
        for dtype in DRIVER_TYPES:
            data = _minimal_valid_driver()
            data["metadata"]["driver_type"] = dtype
            path = _write_driver(tmp_path, f"test-dtype-{dtype}", data)
            result = validate_driver(path, check_files=False)
            assert result.valid, f"driver_type={dtype} should be valid: {result.errors}"


class TestPhysicalConsistency:
    def test_qts_consistent(self, tmp_path):
        """Qts = (Qes * Qms) / (Qes + Qms) -- should pass when consistent."""
        data = _minimal_valid_driver()
        qes = 0.27
        qms = 6.3
        data["thiele_small"]["qes"] = qes
        data["thiele_small"]["qms"] = qms
        data["thiele_small"]["qts"] = (qes * qms) / (qes + qms)
        path = _write_driver(tmp_path, "test-qts-ok", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid: {result.errors}"

    def test_qts_inconsistent(self, tmp_path):
        """Qts far from expected value should fail."""
        data = _minimal_valid_driver()
        data["thiele_small"]["qes"] = 0.5
        data["thiele_small"]["qms"] = 5.0
        # Expected: (0.5 * 5.0) / (0.5 + 5.0) = 0.4545
        data["thiele_small"]["qts"] = 0.8  # Way off
        path = _write_driver(tmp_path, "test-qts-bad", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("Qts consistency" in e for e in result.errors)

    def test_qts_within_10_percent(self, tmp_path):
        """Qts within 10% tolerance should pass (manufacturer rounding)."""
        data = _minimal_valid_driver()
        qes = 0.5
        qms = 5.0
        expected_qts = (qes * qms) / (qes + qms)
        data["thiele_small"]["qes"] = qes
        data["thiele_small"]["qms"] = qms
        data["thiele_small"]["qts"] = expected_qts * 1.09  # 9% off
        path = _write_driver(tmp_path, "test-qts-margin", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid (within 10%): {result.errors}"

    def test_vd_consistent(self, tmp_path):
        """Vd = Sd * Xmax (in correct units)."""
        data = _minimal_valid_driver()
        sd = 132.7  # cm^2
        xmax = 5.9  # mm
        data["thiele_small"]["sd_cm2"] = sd
        data["thiele_small"]["xmax_mm"] = xmax
        data["thiele_small"]["vd_cm3"] = sd * (xmax / 10.0)  # Convert mm to cm
        path = _write_driver(tmp_path, "test-vd-ok", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid: {result.errors}"

    def test_vd_inconsistent(self, tmp_path):
        """Vd far from Sd * Xmax should fail."""
        data = _minimal_valid_driver()
        data["thiele_small"]["sd_cm2"] = 100.0
        data["thiele_small"]["xmax_mm"] = 10.0
        # Expected: 100 * (10/10) = 100 cm^3
        data["thiele_small"]["vd_cm3"] = 200.0  # 100% off
        path = _write_driver(tmp_path, "test-vd-bad", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("Vd consistency" in e for e in result.errors)

    def test_ebp_consistent(self, tmp_path):
        """EBP = Fs / Qes."""
        data = _minimal_valid_driver()
        data["thiele_small"]["fs_hz"] = 33.0
        data["thiele_small"]["qes"] = 0.27
        data["thiele_small"]["efficiency_bandwidth_product"] = 33.0 / 0.27
        path = _write_driver(tmp_path, "test-ebp-ok", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid: {result.errors}"

    def test_ebp_inconsistent(self, tmp_path):
        """EBP far from Fs/Qes should fail."""
        data = _minimal_valid_driver()
        data["thiele_small"]["fs_hz"] = 33.0
        data["thiele_small"]["qes"] = 0.27
        data["thiele_small"]["efficiency_bandwidth_product"] = 200.0  # Expected ~122
        path = _write_driver(tmp_path, "test-ebp-bad", data)
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("EBP consistency" in e for e in result.errors)

    def test_consistency_skipped_when_fields_missing(self, tmp_path):
        """No consistency error when required fields are null."""
        data = _minimal_valid_driver()
        data["thiele_small"]["qes"] = None
        data["thiele_small"]["qms"] = None
        path = _write_driver(tmp_path, "test-skip-consistency", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid: {result.errors}"


class TestWarnings:
    def test_warns_on_missing_xmax(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"]["xmax_mm"] = None
        path = _write_driver(tmp_path, "test-warn-01", data)
        result = validate_driver(path, check_files=False)
        assert result.valid  # Warnings don't fail
        assert any("xmax_mm" in w for w in result.warnings)

    def test_warns_on_missing_le(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"]["le_mh"] = None
        path = _write_driver(tmp_path, "test-warn-02", data)
        result = validate_driver(path, check_files=False)
        assert result.valid
        assert any("le_mh" in w for w in result.warnings)

    def test_warns_on_missing_sd(self, tmp_path):
        data = _minimal_valid_driver()
        data["thiele_small"]["sd_cm2"] = None
        path = _write_driver(tmp_path, "test-warn-03", data)
        result = validate_driver(path, check_files=False)
        assert result.valid
        assert any("sd_cm2" in w for w in result.warnings)


class TestDataFileChecks:
    def test_missing_datasheet_file_warns(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["datasheet_file"] = "nonexistent.pdf"
        path = _write_driver(tmp_path, "test-file-01", data)
        result = validate_driver(path, check_files=True)
        # Data file warning, not error
        assert any("datasheet_file" in w for w in result.warnings)

    def test_existing_datasheet_file_no_warn(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["datasheet_file"] = "spec.pdf"
        path = _write_driver(tmp_path, "test-file-02", data)
        # Create the file
        data_dir = path.parent / "data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "spec.pdf").write_text("dummy")
        result = validate_driver(path, check_files=True)
        assert result.valid
        assert not any("datasheet_file" in w for w in result.warnings)

    def test_missing_measurement_data_file_warns(self, tmp_path):
        data = _minimal_valid_driver()
        data["measurements"]["impedance_curve"]["data_file"] = "impedance.zma"
        path = _write_driver(tmp_path, "test-file-03", data)
        result = validate_driver(path, check_files=True)
        assert any("impedance_curve" in w and "data_file" in w for w in result.warnings)

    def test_no_file_check_skips_warnings(self, tmp_path):
        data = _minimal_valid_driver()
        data["metadata"]["datasheet_file"] = "nonexistent.pdf"
        path = _write_driver(tmp_path, "test-file-04", data)
        result = validate_driver(path, check_files=False)
        assert result.valid
        assert not any("datasheet_file" in w for w in result.warnings)


class TestValidateAll:
    def test_validate_multiple_drivers(self, tmp_path):
        good_data = _minimal_valid_driver()
        bad_data = _minimal_valid_driver()
        bad_data["metadata"]["id"] = None  # Invalid

        _write_driver(tmp_path, "driver-a", good_data)
        bad_data_copy = dict(bad_data)
        bad_data_copy["metadata"] = dict(bad_data["metadata"])
        _write_driver(tmp_path, "driver-b", bad_data)

        results = validate_all_drivers(tmp_path, check_files=False)
        assert len(results) == 2
        assert sum(1 for r in results if r.valid) == 1
        assert sum(1 for r in results if not r.valid) == 1

    def test_skips_non_driver_entries(self, tmp_path):
        """Files without driver.yml should be skipped."""
        good_data = _minimal_valid_driver()
        _write_driver(tmp_path, "driver-a", good_data)
        # Create a non-driver directory
        (tmp_path / "TEMPLATE.yml").write_text("not a driver")
        # Create a directory without driver.yml
        (tmp_path / "random-dir").mkdir()

        results = validate_all_drivers(tmp_path, check_files=False)
        assert len(results) == 1


class TestEdgeCases:
    def test_invalid_yaml(self, tmp_path):
        path = tmp_path / "bad" / "driver.yml"
        path.parent.mkdir(parents=True)
        path.write_text("{ invalid yaml: [")
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("YAML parse error" in e for e in result.errors)

    def test_nonexistent_file(self, tmp_path):
        result = validate_driver(tmp_path / "nope" / "driver.yml", check_files=False)
        assert not result.valid
        assert any("File not found" in e for e in result.errors)

    def test_top_level_not_dict(self, tmp_path):
        path = tmp_path / "bad" / "driver.yml"
        path.parent.mkdir(parents=True)
        path.write_text("just a string")
        result = validate_driver(path, check_files=False)
        assert not result.valid
        assert any("mapping" in e for e in result.errors)

    def test_integer_diameter_accepted(self, tmp_path):
        """Integer values for float fields should be accepted."""
        data = _minimal_valid_driver()
        data["metadata"]["nominal_diameter_in"] = 8  # int, not float
        data["thiele_small"]["z_nom_ohm"] = 8
        path = _write_driver(tmp_path, "test-int-01", data)
        result = validate_driver(path, check_files=False)
        assert result.valid, f"Expected valid: {result.errors}"


def _qts_error(qts, expected, deviation):
    """The exact Qts error string _check_qts_consistency produces."""
    return (
        f"thiele_small: Qts consistency check failed. Qts={qts}, "
        f"expected (Qes*Qms)/(Qes+Qms)={expected}, deviation={deviation} (>10%)"
    )


# Records exempt from the Qts consistency check only (F-363). Each record
# keeps its stored values and carries metadata.ts_consistency equal to the
# entry's mark:
#   datasheet-inconsistent  the manufacturer datasheet itself prints an
#                           inconsistent Qts/Qes/Qms triple; the record
#                           stores it exactly and the quote cites it.
#   unverifiable            the source is unavailable; the triple is our
#                           own record's values and there is no quote.
# The record's error list must equal exactly [error], and its (qts, qes,
# qms) must equal the triple. Any change to the record, the mark or the
# validator makes test_exemptions_are_current fail, so an entry cannot
# outlive what it documents. All sources were retrieved 2026-10-25.
TS_CONSISTENCY_EXEMPTIONS = {
    "coast-buyouts-eas12d531a2": {
        "mark": "unverifiable",
        "triple": (1.717, 2.259, 4.156),  # our record's values, unquoted
        "error": _qts_error(1.717, "1.4635", "17.3%"),
        "quote": None,
    },
    "earthquake-dbxi-12d": {
        "mark": "datasheet-inconsistent",
        "triple": (0.5, 0.45, 4.7),
        "error": _qts_error(0.5, "0.4107", "21.7%"),
        "quote": "https://www.earthquakesound.com/cdn/shop/files/DBXI-12D-Manual.pdf"
                 " (DBXi manual, no revision printed): Qes 0.45, Qms 4.70, Qts .5."
                 " Qts > Qes is physically impossible.",
    },
    "earthquake-dbxi-15d": {
        "mark": "datasheet-inconsistent",
        "triple": (0.45, 1.14, 5.99),
        "error": _qts_error(0.45, "0.9577", "53.0%"),
        "quote": "https://www.earthquakesound.com/cdn/shop/files/DBXI-12D-Manual.pdf"
                 " (DBXi manual, no revision printed), DBXI-15D:"
                 " Qes 1.14, Qms 5.99, Qts .45.",
    },
    "goldwood-gw-206-8": {
        "mark": "datasheet-inconsistent",
        "triple": (0.752, 0.752, 3.386),
        "error": _qts_error(0.752, "0.6153", "22.2%"),
        "quote": "https://www.parts-express.com/pedocs/more-info/"
                 "290-305-goldwood-gw-2068-more-info.pdf (no revision printed):"
                 " Qms 3.386, Qes 0.752, Qts 0.752. Qts = Qes is impossible.",
    },
    "image-dynamics-id12d4-v4": {
        "mark": "datasheet-inconsistent",
        "triple": (0.787, 0.698, 5.582),
        "error": _qts_error(0.787, "0.6204", "26.8%"),
        "quote": "https://www.loudspeakerdatabase.com/ImageDynamics/ID12D4_V4/"
                 "ImageDynamics_ID12D4_V4.pdf (ID Series V4 manual, (c) 2023),"
                 " ID12D4 column: Qms 5.582, Qes 0.698, Qts 0.787. Qes is"
                 " identical to the ID12D2 column.",
    },
    "image-dynamics-idmax10d2-v4": {
        "mark": "datasheet-inconsistent",
        "triple": (0.609, 1.346, 4.548),
        "error": _qts_error(0.609, "1.0386", "41.4%"),
        "quote": "https://imagedynamicsusa.net/media/uploads_file/2024/07/01/"
                 "a6682eec06d8c04.66893277.pdf (IDMAX V4 manual), IDMAX10D2"
                 " column: Qms 4.548, Qes 1.346, Qts 0.609.",
    },
    "monacor-sph-30x-4sw": {
        "mark": "datasheet-inconsistent",
        "triple": (0.42, 0.39, 9.35),
        "error": _qts_error(0.42, "0.3744", "12.2%"),
        "quote": "https://doc.soundimports.nl/pdf/brands/Monacor/SPH-30X4SW/"
                 "pdf_monacor_SPH-30X4SW_1.pdf (Monacor sheet, no revision"
                 " printed): Qms 9.35, Qes 0.39, Qts 0.42. Qts > Qes is"
                 " impossible.",
    },
    "prv-audio-10mr2000-ndy": {
        "mark": "datasheet-inconsistent",
        "triple": (0.21, 0.21, 1.54),
        "error": _qts_error(0.21, "0.1848", "13.6%"),
        "quote": "https://doc.soundimports.nl/pdf/brands/PRV%20Audio/"
                 "10MR2000-NDY/10MR2000-NDY-Datasheet.pdf (Rev 01/20):"
                 " Qts 0.21, Qes 0.21, Qms 1.54. Qts = Qes is impossible.",
    },
}


# Plausibility bounds on the Q values, as (lower, upper), inclusive (F-363).
# AE-set: widening or removing a bound needs an Audio Engineer review.
# Scraped comma decimals ("6,54" read as 654) can produce a record that
# passes the Qts consistency check, because Qts ~ Qes when Qms is huge;
# a 100x error downward is just as wrong. A real record outside these
# bounds needs an entry in TS_PLAUSIBILITY_ALLOWLIST, never a wider bound.
# Independently of the bounds, every Q must be > 0 (no allowlist).
TS_PLAUSIBILITY_BOUNDS = {
    "qts": (0.1, 5.0),
    "qes": (0.1, 10.0),
    "qms": (0.5, 50.0),
}

# Records with a real Q value outside its bounds, as
# {record_id: {"field": name, "value": stored value, "quote": source}}.
# quote None means the value could not be sourced; such a record must
# carry ts_consistency: unverifiable, which keeps it out of the safety math.
TS_PLAUSIBILITY_ALLOWLIST = {
    "factory-buyouts-42-41716g-001": {
        "field": "qes",
        "value": 22.17,
        "quote": None,
    },
    "tang-band-w1-2361s": {
        "field": "qms",
        "value": 0.35,
        "quote": None,
    },
    "visaton-g-50-ffl": {
        "field": "qms",
        "value": 0.48,
        "quote": None,
    },
    "visaton-gs-20-sc": {
        "field": "qms",
        "value": 0.36,
        "quote": "visaton.de G 20 SC 8 Ohm: Mechanical Q factor Qms 0.36, "
        "Electrical Q factor Qes 1.34, Total Q factor Qts 0.28",
    },
}


class TestRealDriverRecords:
    """Validate every real driver record in the project's configs/drivers/.

    Every record is validated, in sorted order, and every failure is
    reported. The only tolerated failures are the documented Qts
    exemptions in TS_CONSISTENCY_EXEMPTIONS. These tests skip if the
    configs/drivers directory is not available.
    """

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    CONFIGS_DIR = PROJECT_ROOT / "configs"
    DRIVERS_DIR = CONFIGS_DIR / "drivers"

    # Record count at F-363 (2026-10-25). Guards against the scan silently
    # shrinking. Lower it only together with a deliberate record removal.
    MIN_RECORDS = 2345

    @pytest.fixture(scope="class")
    def results(self):
        if not self.DRIVERS_DIR.exists():
            pytest.skip("configs/drivers/ not found")
        results = validate_all_drivers(self.DRIVERS_DIR, check_files=False)
        if not results:
            pytest.skip("No driver records found")
        return {Path(r.driver_path).parent.name: r for r in results}

    def _marked_records(self, results):
        """Map each record with any metadata.ts_consistency to its mark."""
        marked = {}
        for record_id, result in results.items():
            with open(result.driver_path) as f:
                data = yaml.safe_load(f)
            metadata = data.get("metadata") or {}
            if metadata.get("ts_consistency") is not None:
                marked[record_id] = metadata["ts_consistency"]
        return marked

    def test_all_real_drivers_pass(self, results):
        """Every record passes, except the exact documented exemptions."""
        expected_count = len(list(self.DRIVERS_DIR.glob("*/driver.yml")))
        assert len(results) == expected_count
        assert len(results) >= self.MIN_RECORDS
        print(f"validated {len(results)} driver records")

        failures = []
        for record_id, result in sorted(results.items()):
            if result.valid:
                continue
            exemption = TS_CONSISTENCY_EXEMPTIONS.get(record_id)
            if exemption is not None and result.errors == [exemption["error"]]:
                continue
            failures.append(str(result))

        assert not failures, (
            f"{len(failures)}/{len(results)} drivers failed:\n"
            + "\n".join(failures)
        )

    def test_exemptions_match_marks(self, results):
        """The marked records and the exemption entries agree, mark for mark."""
        marked = self._marked_records(results)
        exempt = {
            record_id: exemption["mark"]
            for record_id, exemption in TS_CONSISTENCY_EXEMPTIONS.items()
        }
        unsourced = {
            record_id: "unverifiable"
            for record_id, allowed in TS_PLAUSIBILITY_ALLOWLIST.items()
            if allowed["quote"] is None
        }
        assert not exempt.keys() & unsourced.keys()
        assert marked == {**exempt, **unsourced}
        for record_id, exemption in TS_CONSISTENCY_EXEMPTIONS.items():
            if exemption["mark"] == "datasheet-inconsistent":
                assert exemption["quote"], f"{record_id}: quote required"
            else:
                assert exemption["mark"] == "unverifiable", record_id
                assert exemption["quote"] is None, record_id

    @pytest.mark.parametrize(
        "record_id", sorted(TS_CONSISTENCY_EXEMPTIONS)
    )
    def test_exemptions_are_current(self, results, record_id):
        """Each exemption still matches its record's triple and error exactly."""
        exemption = TS_CONSISTENCY_EXEMPTIONS[record_id]
        assert record_id in results, f"{record_id} has no driver record"
        result = results[record_id]
        with open(result.driver_path) as f:
            ts = yaml.safe_load(f)["thiele_small"]
        assert (ts["qts"], ts["qes"], ts["qms"]) == exemption["triple"]
        assert result.errors == [exemption["error"]]

    def test_marked_records_not_referenced_by_profiles(self, results):
        """No speaker or venue config uses a record with either mark."""
        marked = self._marked_records(results)
        references = []
        for path in sorted(self.CONFIGS_DIR.rglob("*.yml")):
            if self.DRIVERS_DIR in path.parents:
                continue
            text = path.read_text()
            references += [
                f"{path.relative_to(self.PROJECT_ROOT)}: {record_id}"
                for record_id in sorted(marked)
                if record_id in text
            ]
        assert not references, "\n".join(references)

    def test_ts_values_plausible(self, results):
        """Every Q is > 0 and within its bounds, except allowlisted ones."""
        violations = []
        for record_id, result in sorted(results.items()):
            with open(result.driver_path) as f:
                ts = yaml.safe_load(f).get("thiele_small") or {}
            for field, (lower, upper) in TS_PLAUSIBILITY_BOUNDS.items():
                value = ts.get(field)
                if value is None:
                    continue
                if value <= 0:
                    violations.append(f"{record_id}: {field}={value} <= 0")
                    continue
                if lower <= value <= upper:
                    continue
                allowed = TS_PLAUSIBILITY_ALLOWLIST.get(record_id)
                if allowed and (allowed["field"], allowed["value"]) == (field, value):
                    continue
                violations.append(
                    f"{record_id}: {field}={value} outside [{lower}, {upper}]"
                )
        assert not violations, "\n".join(violations)

    def test_plausibility_allowlist_is_current(self, results):
        """Each allowlist entry still matches an out-of-bound stored value."""
        for record_id, allowed in sorted(TS_PLAUSIBILITY_ALLOWLIST.items()):
            quote = allowed["quote"]
            assert quote is None or quote.strip(), f"{record_id}: empty quote"
            assert record_id in results, f"{record_id} has no driver record"
            with open(results[record_id].driver_path) as f:
                ts = yaml.safe_load(f)["thiele_small"]
            assert ts[allowed["field"]] == allowed["value"], record_id
            lower, upper = TS_PLAUSIBILITY_BOUNDS[allowed["field"]]
            assert not lower <= allowed["value"] <= upper, (
                f"{record_id}: {allowed['field']}={allowed['value']} is within "
                "bounds, remove the allowlist entry"
            )

    def test_template_is_not_validated(self):
        """TEMPLATE.yml is not inside a {id}/ directory, so it shouldn't be picked up."""
        template = self.DRIVERS_DIR / "TEMPLATE.yml"
        if not template.exists():
            pytest.skip("TEMPLATE.yml not found")
        # validate_all_drivers should not pick up TEMPLATE.yml
        # (it's not in a subdirectory)
        results = validate_all_drivers(self.DRIVERS_DIR, check_files=False)
        paths = [r.driver_path for r in results]
        assert not any("TEMPLATE" in p for p in paths)
