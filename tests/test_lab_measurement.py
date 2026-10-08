import json
import tempfile
import unittest
from pathlib import Path

from research.process.lab_measurement import (
    LabMeasurementError,
    build_measurement,
    list_measurements,
    load_measurement,
    save_measurement,
)


RECORD_ID = "a" * 64


def quantitative(**changes):
    value = {
        "observable": "firing_linear_shrinkage_pct",
        "value": 7.4,
        "unit": "%",
        "specimen_id": "tile-01",
        "source_ref": "lab:session-01",
        "method": "dry and fired dimensions; same marked axis",
        "status": "MEASURED",
        "uncertainty": 0.2,
        "uncertainty_kind": "REPEAT_SD",
        "replicate_id": "replicate-01",
        "conditions": {"dimension_axis": "length", "firing_run_id": "run-01"},
    }
    value.update(changes)
    return value


class LabMeasurementTests(unittest.TestCase):
    def test_quantitative_record_is_reproducible_and_marks_observed(self):
        first = build_measurement(RECORD_ID, quantitative())
        second = build_measurement(RECORD_ID, quantitative())
        self.assertEqual(first, second)
        self.assertEqual(first["evidence_kind"], "OBSERVED")
        self.assertEqual(first["method_kind"], "EMPIRICAL")
        self.assertEqual(first["measurement"]["value"], 7.4)
        self.assertEqual(first["measurement"]["uncertainty"], 0.2)

    def test_negative_shrinkage_can_represent_expansion_without_relabeling(self):
        measurement = build_measurement(RECORD_ID, quantitative(value=-0.3, uncertainty=0.1))
        self.assertEqual(measurement["measurement"]["value"], -0.3)

    def test_uncertainty_requires_a_declared_interpretation(self):
        with self.assertRaisesRegex(LabMeasurementError, "UNCERTAINTY_VALUE_AND_KIND_MUST_MATCH"):
            build_measurement(RECORD_ID, quantitative(uncertainty_kind=None))
        with self.assertRaisesRegex(LabMeasurementError, "UNCERTAINTY_VALUE_AND_KIND_MUST_MATCH"):
            build_measurement(RECORD_ID, quantitative(uncertainty=None))

    def test_defect_absence_and_not_assessed_are_distinct(self):
        absent = {
            "observable": "defect_observation", "value": "CRAZING", "unit": None,
            "specimen_id": "tile-01", "source_ref": "lab:session-01", "method": "visual inspection",
            "status": "OBSERVED_ABSENT",
        }
        not_assessed = dict(absent, status="NOT_ASSESSED")
        self.assertEqual(build_measurement(RECORD_ID, absent)["measurement"]["status"], "OBSERVED_ABSENT")
        self.assertEqual(build_measurement(RECORD_ID, not_assessed)["measurement"]["status"], "NOT_ASSESSED")

    def test_surface_and_adhesion_are_categorical_observations(self):
        surface = {
            "observable": "glaze_surface_class", "value": "SATIN", "unit": None,
            "specimen_id": "tile-01", "source_ref": "lab:session-01", "method": "visual assessment",
            "status": "OBSERVED",
        }
        adhesion = dict(surface, observable="glaze_adhesion_assessment", value="PARTIAL_PEELING")
        transmission = dict(surface, observable="optical_transmission_class", value="OPAQUE")
        self.assertEqual(build_measurement(RECORD_ID, surface)["measurement"]["value"], "SATIN")
        self.assertEqual(build_measurement(RECORD_ID, adhesion)["measurement"]["value"], "PARTIAL_PEELING")
        self.assertEqual(build_measurement(RECORD_ID, transmission)["measurement"]["value"], "OPAQUE")

    def test_rejects_unit_mismatch_unknown_label_and_bad_status(self):
        cases = [
            (quantitative(unit="mm"), "UNIT_MISMATCH"),
            (quantitative(observable="glaze_surface_class", value="VERY_GLOSSY", unit=None, status="OBSERVED", uncertainty=None), "INVALID_CATEGORICAL_VALUE"),
            (quantitative(status="OBSERVED_ABSENT"), "INVALID_QUANTITATIVE_STATUS"),
            (quantitative(value=True), "INVALID_NUMBER:VALUE"),
            (quantitative(value=float("nan")), "INVALID_NUMBER:VALUE"),
            (quantitative(uncertainty=-0.1), "OUT_OF_RANGE:UNCERTAINTY"),
        ]
        for payload, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(LabMeasurementError, expected):
                    build_measurement(RECORD_ID, payload)

    def test_rejects_unknown_fields_and_non_json_conditions(self):
        with self.assertRaisesRegex(LabMeasurementError, "UNKNOWN_MEASUREMENT_FIELDS"):
            build_measurement(RECORD_ID, quantitative(units="%"))
        with self.assertRaisesRegex(LabMeasurementError, "INVALID_CONDITIONS"):
            build_measurement(RECORD_ID, quantitative(conditions={"bad": float("inf")}))

    def test_archive_is_idempotent_lists_by_record_and_detects_tampering(self):
        measurement = build_measurement(RECORD_ID, quantitative())
        with tempfile.TemporaryDirectory() as directory:
            first = save_measurement(measurement, directory)
            second = save_measurement(measurement, directory)
            loaded = load_measurement(measurement["measurement_id"], directory)
            rows = list_measurements(RECORD_ID, directory)
            self.assertEqual(first["status"], "CREATED")
            self.assertEqual(second["status"], "EXISTS")
            self.assertEqual(loaded["measurement"], measurement)
            self.assertEqual(len(rows), 1)

            path = Path(directory) / f"{measurement['measurement_id']}.json"
            envelope = json.loads(path.read_text(encoding="utf-8"))
            envelope["measurement"]["measurement"]["value"] = 88.0
            path.write_text(json.dumps(envelope), encoding="utf-8")
            with self.assertRaisesRegex(LabMeasurementError, "MEASUREMENT_CHECKSUM_MISMATCH"):
                load_measurement(measurement["measurement_id"], directory)

    def test_forged_identity_is_rejected_before_storage(self):
        measurement = build_measurement(RECORD_ID, quantitative())
        measurement['measurement_id'] = 'b' * 64
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(LabMeasurementError, 'MEASUREMENT_SNAPSHOT_MISMATCH'):
                save_measurement(measurement, directory)
            self.assertEqual(list(Path(directory).glob('*.json')), [])

    def test_archive_cannot_be_renamed_to_a_different_identity(self):
        measurement = build_measurement(RECORD_ID, quantitative())
        with tempfile.TemporaryDirectory() as directory:
            save_measurement(measurement, directory)
            path = Path(directory) / f"{measurement['measurement_id']}.json"
            path.rename(Path(directory) / ('b' * 64 + '.json'))
            with self.assertRaisesRegex(LabMeasurementError, 'MEASUREMENT_FILENAME_MISMATCH'):
                load_measurement('b' * 64, directory)


if __name__ == "__main__":
    unittest.main()
