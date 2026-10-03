"""One explicit pure-calcite mass balance; no temperature-to-conversion model."""
import math
from .foundation import formula_report, reaction_balance, digest, ChemistryInputError

VERSION = 'calcite-explorer/0.1.0'
SOURCES = [
    'https://www.nist.gov/publications/precision-calcination-mechanism-caco-3-high-porosity-nanoscale-cao-co-2-sorbent',
    'https://www.sciencedirect.com/science/article/pii/S0009250902001379',
]

def explore(mass_g, conversion):
    for value, low, high in ((mass_g, 0.000001, 1000000), (conversion, 0, 1)):
        if isinstance(value, bool) or not isinstance(value, (int,float)) or not low <= value <= high or not math.isfinite(value):
            raise ChemistryInputError('INVALID_EXPLORER_INPUT')
    formulas = {f: formula_report(f,1) for f in ('CaCO3','CaO','CO2')}
    initial_moles = mass_g / formulas['CaCO3']['molar_mass_g_mol']
    def state(x):
        return {'conversion':x, 'CaCO3_g':mass_g*(1-x),
                'CaO_g':initial_moles*x*formulas['CaO']['molar_mass_g_mol'],
                'CO2_g':initial_moles*x*formulas['CO2']['molar_mass_g_mol']}
    current=state(conversion)
    return {'method_version':VERSION, 'evidence_kind':'CALCULATED', 'qualifier':'ASSUMED_CONVERSION_PURE_CALCITE',
            'input_snapshot':{'mass_g':mass_g,'conversion':conversion},
            'input_hash':digest({'mass_g':mass_g,'conversion':conversion,'version':VERSION,'constants':formulas['CaCO3']['constant_set_sha256']}),
            'constants_version':formulas['CaCO3']['constant_set_id'],
            'balance':reaction_balance({'CaCO3':1},{'CaO':1,'CO2':1}),
            'current':current,'series':[state(i/20) for i in range(21)],
            'mass_residual_g':math.fsum([current['CaCO3_g'],current['CaO_g'],current['CO2_g']])-mass_g,
            'conversion_from_temperature':{'status':'UNAVAILABLE','reason':'KINETICS_ATMOSPHERE_AND_SAMPLE_DATA_REQUIRED'},
            'source_refs':SOURCES+formulas['CaCO3']['source_refs'],
            'limitations':['Pure CaCO3, single assumed decomposition pathway.',
                           'Conversion is supplied, not predicted from temperature or time.',
                           'CO2 amount is produced mass, not gas volume, trapped gas or defect probability.',
                           'CaO product may react further in a glaze; subsequent reactions are not calculated.',
                           'No arbitrary material-pair prediction or kiln operating recommendation.']}
