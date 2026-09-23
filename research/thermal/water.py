"""Optional CoolProp adapter for an intentionally narrow drying research domain.

Pure water only. Not pore pressure, humid air, bound water or a kiln model.
Dependencies are loaded lazily; the chemistry core does not require CoolProp.
"""
import math

VERSION = 'water-properties/0.1.0-research'


def finite(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'OUT_OF_SCOPE:{name}')
    return float(value)


def pure_water(temperature_k, pressure_pa):
    temperature_k = finite(temperature_k, 'temperature_k', 273.16, 473.15)
    pressure_pa = finite(pressure_pa, 'pressure_pa', 10000, 1000000)
    import CoolProp
    from CoolProp.CoolProp import PropsSI, PhaseSI
    if CoolProp.__version__ != '8.0.0':
        raise ValueError('UNREVIEWED_COOLPROP_VERSION')
    try:
        phase = PhaseSI('T', temperature_k, 'P', pressure_pa, 'Water')
        if phase not in ('liquid', 'gas'):
            raise ValueError('UNSUPPORTED_OR_AMBIGUOUS_PHASE')
        outputs = {name: float(PropsSI(key, 'T', temperature_k, 'P', pressure_pa, 'Water'))
                   for name, key in [('density_kg_m3','Dmass'),('enthalpy_j_kg','Hmass'),
                                     ('internal_energy_j_kg','Umass'),('cp_j_kg_k','Cpmass')]}
    except ValueError as error:
        raise ValueError('WATER_STATE_UNAVAILABLE') from error
    if not all(math.isfinite(v) for v in outputs.values()):
        raise ValueError('NONFINITE_PROPERTY')
    return {'method_version': VERSION, 'backend': 'CoolProp HEOS Water',
            'backend_version': CoolProp.__version__, 'phase': phase,
            'evidence_kind': 'PREDICTED', 'method_kind': 'DETERMINISTIC',
            'qualifier': 'EQUATION_OF_STATE_ESTIMATE', 'uncertainty': None,
            'temperature_k': temperature_k, 'pressure_pa': pressure_pa, 'values': outputs,
            'limitations': ['Pure homogeneous water; not a porous clay drying simulation.',
                            'No energy/mass coupling or experiment validation.',
                            'Enthalpy reference convention belongs to this backend; do not mix baselines.']}
