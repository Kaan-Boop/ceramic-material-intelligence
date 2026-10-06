"""Local numerical run: python -m scripts.run_kiln_thermal_1d CASE --output-root DIR.

Writes a unique directory with full report, scalar and spatial CSVs and hashes.
No network, material lookup, new dependencies or implicit physical calibration.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import time
import uuid

from research.thermal import kiln_1d


def run(case_path: Path, output_root: Path):
    case = json.loads(case_path.read_text(encoding="utf-8-sig"))
    start = time.perf_counter()
    report = kiln_1d.simulate(case)
    elapsed = time.perf_counter() - start
    target = output_root / (report["input_hash"][:12] + "-" + uuid.uuid4().hex[:8])
    target.mkdir(parents=True, exist_ok=False)
    (target / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    scalar_keys = [key for key in report["series"][0] if key not in ("cell_temperature_c", "layer_midpoint_c")]
    # Numbered columns avoid spreadsheet formula injection from user layer IDs.
    probes = [f"layer_{i}_midpoint_c" for i in range(len(case["layers"]))]
    with (target / "timeline.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=scalar_keys + probes)
        writer.writeheader()
        for row in report["series"]:
            record = {key: row[key] for key in scalar_keys}
            record.update({key: row["layer_midpoint_c"][layer["layer_id"]] for key, layer in zip(probes, case["layers"])})
            writer.writerow(record)
    with (target / "temperature-field.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["time_s", "cell_index", "layer_index", "position_m", "temperature_c"])
        for row in report["series"]:
            for i, value in enumerate(row["cell_temperature_c"]):
                writer.writerow([row["time_s"], i, report["mesh"]["layer_indices"][i], report["mesh"]["cell_centers_m"][i], value])
    receipt = {
        "schema_version": "kiln-thermal-run-receipt-v1",
        "engine_version": kiln_1d.VERSION,
        "input_hash": report["input_hash"],
        "engine_file_sha256": hashlib.sha256(Path(kiln_1d.__file__).read_bytes()).hexdigest(),
        "python_version": platform.python_version(),
        "elapsed_seconds": elapsed,
        "physical_validation": report["physical_validation"],
        "csv_layer_columns": dict(zip(probes, [layer["layer_id"] for layer in case["layers"]])),
        "files": {name: hashlib.sha256((target / name).read_bytes()).hexdigest()
                  for name in ("report.json", "timeline.csv", "temperature-field.csv")},
    }
    (target / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target, report, elapsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("--output-root", type=Path, default=Path("storage/simulation/kiln-thermal-1d"))
    args = parser.parse_args()
    target, report, elapsed = run(args.case, args.output_root)
    print(json.dumps({"output": str(target.resolve()), "elapsed_seconds": elapsed,
                      "diagnostics": report["diagnostics"],
                      "contains_synthetic_inputs": report["contains_synthetic_inputs"],
                      "physical_validation": report["physical_validation"]}, ensure_ascii=False))
