"""Ideal lumped warm-up/boiling benchmark; NOT porous-clay drying kinetics."""
import math

VERSION = 'ideal-drying/0.1.0'


def _number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name)
    if value < 0 or (positive and value == 0):
        raise ValueError(name)
    return float(value)


def simulate(*, dry_mass_kg, water_mass_kg, solid_cp_j_kg_k,
             initial_temperature_k, net_power_w, times_s, properties):
    """properties: saturation T, liquid h(T), saturated h_l/h_v at one pressure.

    Constant positive NET heat, no pre-boiling evaporation, constant solid cp.
    Ends at water exhaustion; excess energy is reported, never lost silently.
    """
    dry = _number(dry_mass_kg, 'dry_mass_kg', True)
    water = _number(water_mass_kg, 'water_mass_kg', True)
    cp = _number(solid_cp_j_kg_k, 'solid_cp_j_kg_k', True)
    initial = _number(initial_temperature_k, 'initial_temperature_k', True)
    power = _number(net_power_w, 'net_power_w')
    times = [_number(t, 'time_s') for t in times_s]
    if not times or len(times) > 10001 or times[0] != 0 or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('INVALID_TIME_GRID')
    saturation = _number(properties['saturation_temperature_k'], 'saturation_temperature_k', True)
    if not 273.16 <= initial <= saturation <= 473.15:
        raise ValueError('TEMPERATURE_OUT_OF_SCOPE')
    h_liquid = properties['liquid_enthalpy']
    h0 = h_liquid(initial)
    latent = properties['vapor_enthalpy_j_kg'] - properties['liquid_enthalpy_j_kg']
    _number(latent, 'latent_heat', True)

    def sensible(t):
        h = properties['liquid_enthalpy_j_kg'] if t == saturation else h_liquid(t)
        return dry * cp * (t - initial) + water * (h - h0)

    warmup = _number(sensible(saturation), 'warmup_energy')
    capacity = warmup + water * latent
    series = []
    for time in times:
        supplied = power * time
        _number(supplied, 'supplied_energy')
        used = min(supplied, capacity)
        if used < warmup:
            lo, hi = initial, saturation
            for _ in range(60):
                mid = (lo + hi) / 2
                if sensible(mid) < used:
                    lo = mid
                else:
                    hi = mid
            temperature = (lo + hi) / 2
            evaporated = 0.0
            sensible_energy = sensible(temperature)
            stage = 'WARMUP'
        else:
            temperature = saturation
            evaporated = min(water, (used - warmup) / latent)
            sensible_energy = warmup
            stage = 'WATER_EXHAUSTED_MODEL_END' if supplied >= capacity else 'BOILING'
        latent_energy = evaporated * latent
        residual = supplied - sensible_energy - latent_energy - (supplied - used)
        if abs(residual) > 1e-7 * max(1.0, supplied):
            raise ValueError('ENERGY_BALANCE_FAILED')
        series.append(dict(time_s=time, temperature_k=temperature, stage=stage,
                           remaining_water_kg=water-evaporated, emitted_water_kg=evaporated,
                           supplied_energy_j=supplied, sensible_energy_j=sensible_energy,
                           latent_energy_j=latent_energy, outside_model_energy_j=supplied-used,
                           energy_residual_j=residual))
    return dict(method_version=VERSION, evidence_kind='PREDICTED', method_kind='DETERMINISTIC',
                qualifier='IDEAL_ENERGY_LIMITED_BENCHMARK', physical_validation='NOT_PERFORMED',
                property_method=properties['method'], uncertainty=None,
                inputs=dict(dry_mass_kg=dry, water_mass_kg=water, solid_cp_j_kg_k=cp,
                            initial_temperature_k=initial, net_power_w=power, times_s=times),
                warmup_energy_j=warmup, latent_heat_j_kg=latent, series=series,
                limitations=['No evaporation below boiling: not ambient or porous drying.',
                             'Net power is prescribed, not kiln electrical power.',
                             'Uniform temperature, free water only, constant solid heat capacity.',
                             'No bound water, pressure buildup, cracks or ceramic reaction kinetics.',
                             'Stops at water exhaustion; further energy is outside model.'])


def water_properties(pressure_pa=101325.0):
    """Optional pure-water HEOS provider, 10 kPa--1 MPa absolute pressure."""
    from research.thermal.water import finite
    pressure = finite(pressure_pa, 'pressure_pa', 10000, 1000000)
    import CoolProp
    from CoolProp.CoolProp import PropsSI
    if CoolProp.__version__ != '8.0.0':
        raise ValueError('UNREVIEWED_COOLPROP_VERSION')
    ts = float(PropsSI('T', 'P', pressure, 'Q', 0, 'Water'))
    hl = float(PropsSI('Hmass', 'P', pressure, 'Q', 0, 'Water'))
    hv = float(PropsSI('Hmass', 'P', pressure, 'Q', 1, 'Water'))
    def liquid(t):
        finite(t, 'temperature_k', 273.16, ts)
        return hl if t == ts else float(PropsSI('Hmass', 'P', pressure, 'T|liquid', t, 'Water'))
    return dict(saturation_temperature_k=ts, liquid_enthalpy_j_kg=hl,
                vapor_enthalpy_j_kg=hv, liquid_enthalpy=liquid,
                method=dict(backend='CoolProp HEOS Water', version=CoolProp.__version__, pressure_pa=pressure))
