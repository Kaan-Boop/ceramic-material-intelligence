"""Run optional real-water benchmark; save clearly synthetic specimen output."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.thermal.drying import simulate, water_properties

if __name__ == '__main__':
    props = water_properties()
    # Broad sanity checks, NOT independent equation-of-state validation.
    assert 372 < props['saturation_temperature_k'] < 374
    assert 2.2e6 < props['vapor_enthalpy_j_kg']-props['liquid_enthalpy_j_kg'] < 2.3e6
    report = simulate(dry_mass_kg=1, water_mass_kg=.1, solid_cp_j_kg_k=900,
                      initial_temperature_k=293.15, net_power_w=100,
                      times_s=list(range(0, 4001, 100)), properties=props)
    report['specimen_kind'] = 'SYNTHETIC_NOT_A_COMMERCIAL_CLAY'
    path = ROOT/'data/manifests/ideal-drying-probe-2026-09-23.json'
    path.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(path=str(path), samples=len(report['series']),
                         maximum_energy_residual_j=max(abs(s['energy_residual_j']) for s in report['series']))))
