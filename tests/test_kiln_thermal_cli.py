"""Export integrity and genuinely dependency-free thermal entrypoint."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.run_kiln_thermal_1d import run

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/fixtures/kiln-thermal-1d-synthetic.json"


class KilnThermalCLITests(unittest.TestCase):
    def test_exports_replayable_case_and_numeric_field_with_hashes(self):
        case = json.loads(FIXTURE.read_text(encoding="utf-8"))
        case["schedule"]["points"] = [{"time_s": 0, "gas_c": 20, "wall_c": 20},
                                      {"time_s": 60, "gas_c": 120, "wall_c": 130}]
        case["layers"][0]["layer_id"] = "=not-a-spreadsheet-formula"
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(case), encoding="utf-8")
            first, report, _ = run(source, Path(tmp))
            second, again, _ = run(source, Path(tmp))
            self.assertNotEqual(first, second)
            self.assertEqual(report, again)
            saved = json.loads((first / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["input_snapshot"], case)
            receipt = json.loads((first / "receipt.json").read_text(encoding="utf-8"))
            for name, digest in receipt["files"].items():
                self.assertEqual(hashlib.sha256((first / name).read_bytes()).hexdigest(), digest)
            with (first / "timeline.csv").open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), len(report["series"]))
            self.assertAlmostEqual(float(rows[-1]["layer_0_midpoint_c"]), report["series"][-1]["layer_midpoint_c"][case["layers"][0]["layer_id"]])
            self.assertTrue(all(not k.startswith("=") for k in rows[0]))
            with (first / "temperature-field.csv").open(newline="", encoding="utf-8") as stream:
                cells = list(csv.DictReader(stream))
            self.assertEqual(len(cells), len(rows) * report["diagnostics"]["cells"])

    def test_core_imports_without_site_packages(self):
        result = subprocess.run([sys.executable, "-S", "-c", "from research.thermal.kiln_1d import simulate"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
