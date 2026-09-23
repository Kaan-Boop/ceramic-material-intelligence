"""Reproducible synthetic outcome examples, never commercial product claims."""
import json
from copy import deepcopy
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.process.outcomes import assess_outcomes

if __name__ == '__main__':
    data = json.loads((ROOT/'data/fixtures/outcome-indicators-synthetic.json').read_text())
    results = {'baseline_synthetic': assess_outcomes(data)}
    thick = deepcopy(data)
    thick['flow']['thickness_mm'] = 1
    results['double_thickness_synthetic'] = assess_outcomes(thick)
    viscous = deepcopy(data)
    viscous['flow']['viscosity_pa_s'] = 2000
    results['double_viscosity_synthetic'] = assess_outcomes(viscous)
    target = ROOT/'data/manifests/outcome-examples-2026-09-23.json'
    target.write_text(json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    for name, report in results.items():
        print(name, report['sections']['flow']['values']['ideal_mean_travel_mm'])
