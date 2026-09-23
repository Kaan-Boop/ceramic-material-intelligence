"""Cantera installation benchmark, not a clay/glaze reaction mechanism.

Fixed illustrative H/O/Ar gas only. Equilibrium is not a reaction time prediction.
No network, no kiln control, no material recipe inference.
"""
import hashlib
import json
from pathlib import Path

VERSION='reaction-probe/0.1.0'


def run_probe():
    import cantera as ct
    if ct.__version__!='3.2.0': raise ValueError('UNREVIEWED_CANTERA_VERSION')
    mechanism=Path(ct.__file__).parent/'data/h2o2.yaml'
    if not mechanism.is_file(): raise ValueError('MECHANISM_NOT_FOUND')
    case={'temperature_k':1000.0,'pressure_pa':101325.0,'mole_parts':{'H2':2.0,'O2':1.0,'AR':7.0}}
    def gas():
        phase=ct.Solution(str(mechanism))
        phase.TPX=case['temperature_k'],case['pressure_pa'],case['mole_parts']
        return phase
    def state(phase):
        if not phase.min_temp <= phase.T <= phase.max_temp:
            raise ValueError('THERMO_TEMPERATURE_OUT_OF_RANGE')
        return {'temperature_k':float(phase.T),'pressure_pa':float(phase.P),
                'enthalpy_j_kg':float(phase.enthalpy_mass),'gibbs_j_kg':float(phase.gibbs_mass),
                'mass_fractions':{name:float(y) for name,y in zip(phase.species_names,phase.Y)},
                'element_mass_fractions':{name:float(phase.elemental_mass_fraction(name)) for name in phase.element_names}}
    initial=state(gas())
    equilibrium={}
    for mode in ('TP','HP'):
        phase=gas()
        phase.equilibrate(mode,rtol=1e-10,max_steps=1000)
        equilibrium[mode]=state(phase)
    reactor=ct.IdealGasConstPressureReactor(gas(),clone=True)
    network=ct.ReactorNet([reactor])
    network.rtol=1e-10
    network.atol=1e-18
    series=[]
    for i in range(11):
        target=i*0.0001
        if i: network.advance(target)
        series.append({'time_s':target,**state(reactor.phase)})
    states=list(equilibrium.values())+series
    element_error=max(abs(s['element_mass_fractions'][e]-initial['element_mass_fractions'][e]) for s in states for e in initial['element_mass_fractions'])
    energy_error=max(abs(s['enthalpy_j_kg']-initial['enthalpy_j_kg']) for s in [equilibrium['HP'],*series])/max(abs(initial['enthalpy_j_kg']),1.0)
    mass_error=max(abs(sum(s['mass_fractions'].values())-1.0) for s in states)
    checks={'element_mass_fraction_max_abs_error':element_error,'adiabatic_enthalpy_max_relative_error':energy_error,
            'mass_fraction_sum_max_abs_error':mass_error,'tp_gibbs_decreased':equilibrium['TP']['gibbs_j_kg']<=initial['gibbs_j_kg']}
    if element_error>1e-8 or energy_error>1e-7 or mass_error>1e-10 or not checks['tp_gibbs_decreased']:
        raise ValueError('CONSERVATION_CHECK_FAILED')
    return {'schema_version':VERSION,'backend_version':ct.__version__,
            'mechanism':'bundled h2o2.yaml','mechanism_sha256':hashlib.sha256(mechanism.read_bytes()).hexdigest(),
            'input':case,'input_sha256':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest(),
            'evidence_kind':'PREDICTED','method_kind':'DETERMINISTIC','qualifier':'ILLUSTRATIVE_GAS_BENCHMARK',
            'physical_validation':'NOT_PERFORMED','checks':checks,'initial':initial,'equilibrium':equilibrium,'kinetic_series':series,
            'limitations':['No ceramic oxides, melt, clay dehydration or interface reaction model.',
                           'No furnace geometry, heat losses, humid porous transport or material fit prediction.',
                           'Bundled mechanism example is not approved as a production ceramics dataset.',
                           'Equilibrium TP and HP constraints differ; neither predicts time to equilibrium.']}


if __name__=='__main__':
    result=run_probe()
    root=Path(__file__).resolve().parents[2]
    output=root/'data/manifests/cantera-probe-2026-09-23.json'
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(output),'checks':result['checks'],'samples':len(result['kinetic_series'])}))
