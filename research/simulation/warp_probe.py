"""CPU/CUDA float64 agreement probe. This is NOT the ceramic FEM solver."""
import argparse
import json
from pathlib import Path
import numpy as np
import warp as wp


@wp.kernel
def thermal_strain(alpha: wp.array(dtype=wp.float64), delta_t: wp.array(dtype=wp.float64), result: wp.array(dtype=wp.float64)):
    i = wp.tid()
    result[i] = alpha[i] * delta_t[i]


def probe(cache):
    cache.mkdir(parents=True, exist_ok=True)
    wp.config.kernel_cache_dir = str(cache.resolve())
    wp.init()
    alpha = np.linspace(4e-6, 10e-6, 1024, dtype=np.float64)
    dt = np.linspace(-60, 20, 1024, dtype=np.float64)
    devices = wp.get_devices()
    records = []
    for device in devices:
        a = wp.array(alpha, dtype=wp.float64, device=device)
        b = wp.array(dt, dtype=wp.float64, device=device)
        out = wp.empty(1024, dtype=wp.float64, device=device)
        wp.launch(thermal_strain, dim=1024, inputs=[a, b, out], device=device)
        wp.synchronize_device(device)
        error = float(np.abs(out.numpy() - alpha * dt).max())
        records.append({"device": str(device), "name": device.name, "is_cuda": device.is_cuda,
                        "max_absolute_strain_error": error, "passed": error < 1e-14})
    return {"warp_version": wp.__version__, "test": "epsilon=alpha*delta_T; 1024 float64 values",
            "scope": "Runtime/kernel agreement only. Not GPU FEM or physical validation.",
            "gpu_available": any(r["is_cuda"] for r in records), "devices": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = probe(Path("storage/simulation/00_environment/warp-cache"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not all(r["passed"] for r in result["devices"]):
        raise SystemExit(1)
