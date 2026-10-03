"""Scoped outcome indicators, not a calibrated glaze firing predictor.

Inputs must be resolved properties/measurements, never inferred from product names.
No third-party dependency, network call, database or kiln control.
"""
from copy import deepcopy
import hashlib
import json
import math
import statistics

VERSION = 'outcome-indicators/0.2.0'
REQUIREMENTS = {
    'fit': {
        'required_properties': ['body_mean_cte_per_k', 'glaze_mean_cte_per_k', 'low_c', 'high_c'],
        'compatibility': 'Same temperature interval, material state and cooling basis.',
        'acquisition': 'Matched body and glaze dilatometry; retain curves and measurement method.',
        'not_provided': 'Residual stress, bond strength and crack probability.',
    },
    'flow': {
        'required_properties': ['density_kg_m3', 'viscosity_pa_s', 'thickness_mm', 'inclination_deg', 'duration_s', 'temperature_c'],
        'compatibility': 'Molten-state properties at the modeled temperature; steady Newtonian film assumptions.',
        'acquisition': 'Traceable melt viscosity and density, layer thickness and controlled isothermal conditions.',
        'not_provided': 'Actual advancing glaze edge or runoff during a varying firing schedule.',
    },
    'wetting': {
        'required_properties': ['surface_tension_n_m', 'contact_angle_deg', 'temperature_c'],
        'compatibility': 'Same melt/substrate pair, temperature and atmosphere; equilibrium nonreactive interface.',
        'acquisition': 'High-temperature contact-angle and surface-tension measurements with substrate preparation recorded.',
        'not_provided': 'Fired adhesion strength or percent adhesion.',
    },
    'porosity': {
        'required_properties': ['dry_mass_g', 'saturated_mass_g', 'suspended_mass_g', 'specimen_scope'],
        'compatibility': 'Same specimen and consistent saturation and weighing procedure.',
        'acquisition': 'Dry, saturated and immersed weighings with balance and saturation method recorded.',
        'not_provided': 'Closed pores, isolated glaze porosity or pre-firing pore prediction.',
    },
    'gloss': {
        'required_properties': ['angle_deg', 'readings_gu', 'instrument_id'],
        'compatibility': 'Same measurement geometry and calibrated instrument.',
        'acquisition': 'Gloss-meter readings on fired specimens; distinguish spots from independent specimens.',
        'not_provided': 'Recipe-to-matte/gloss prediction.',
    },
}
SOURCES = {
    'fit': 'https://www.sciencedirect.com/science/article/pii/S0921509307003656',
    'flow': 'https://eng.libretexts.org/Bookshelves/Chemical_Engineering/Chemical_Engineering_Separations%3A_A_Handbook_for_Students_%28Lamm_and_Jarboe%29/01%3A_Chapters/1.02%3A_Mass_Transfer_in_Gas-liquid_Systems',
    'wetting': 'https://pceu.kruss-scientific.com/en/know-how/glossary/adhesion',
    'porosity': 'https://store.astm.org/standards/c373',
    'gloss': 'https://www.byk-instruments.com/en-GB/appearance/micro-gloss',
}


class OutcomeInputError(ValueError):
    pass


def num(d, key, low, high):
    v = d.get(key)
    # Check bounds before float conversion/isfinite: arbitrarily large JSON integers
    # must produce the same controlled domain error as other invalid numbers.
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not low <= v <= high or not math.isfinite(v):
        raise OutcomeInputError('INVALID_NUMBER:' + key)
    return float(v)


def fields(d, keys):
    allowed = set(keys) | {'source_ref', 'conditions', 'input_kind'}
    if not isinstance(d, dict) or set(d) != allowed:
        raise OutcomeInputError('MISSING_OR_UNKNOWN_FIELDS')
    for key in ('source_ref', 'conditions'):
        if not isinstance(d[key], str) or not 1 <= len(d[key].strip()) <= 2000:
            raise OutcomeInputError('MISSING_PROVENANCE:' + key)
    if d['input_kind'] not in ('MEASURED', 'REPORTED', 'SYNTHETIC'):
        raise OutcomeInputError('INVALID_INPUT_KIND')


def result(kind, values, limitations, evidence='PREDICTED'):
    return dict(status='AVAILABLE', evidence_kind=evidence, method_kind='DETERMINISTIC',
                qualifier='SCOPED_INDICATOR_NOT_FAILURE_PROBABILITY', values=values,
                probability=None, uncertainty=None, limitations=limitations,
                method_source=SOURCES[kind])


def fit(d):
    fields(d, ['body_mean_cte_per_k', 'glaze_mean_cte_per_k', 'low_c', 'high_c',
               'same_interval_and_cooling_basis'])
    if d['same_interval_and_cooling_basis'] is not True:
        raise OutcomeInputError('INCOMPATIBLE_CTE_BASIS')
    body = num(d, 'body_mean_cte_per_k', -1e-4, 1e-4)
    glaze = num(d, 'glaze_mean_cte_per_k', -1e-4, 1e-4)
    low, high = num(d, 'low_c', 0, 1000), num(d, 'high_c', 0, 1000)
    if high <= low:
        raise OutcomeInputError('INVERTED_TEMPERATURE_INTERVAL')
    mismatch = (glaze-body)*(high-low)
    direction = 'TENSILE_TENDENCY' if mismatch > 0 else 'COMPRESSIVE_TENDENCY' if mismatch < 0 else 'ZERO_NOMINAL_MISMATCH'
    return result('fit', {'free_contraction_difference_microstrain': mismatch*1e6,
                         'nominal_direction': direction, 'temperature_interval_c': [low, high]},
                  ['Assumes bonding, a thicker constraining body and elastic behavior over the chosen cooling interval.',
                   'Positive: glaze wants to contract more; tensile tendency. Negative: compressive tendency.',
                   'No residual stress, adhesion strength, safe threshold or crazing/shivering probability.',
                   'Mean CTEs must cover the same interval and state; no extrapolation from room-temperature values.',
                   'Relaxation, inversion, gradients, thickness and geometry can change actual stress.'])


def flow(d):
    fields(d, ['density_kg_m3', 'viscosity_pa_s', 'thickness_mm', 'inclination_deg',
               'duration_s', 'temperature_c', 'ideal_film_assumptions'])
    if d['ideal_film_assumptions'] is not True:
        raise OutcomeInputError('FILM_ASSUMPTIONS_REQUIRED')
    rho = num(d, 'density_kg_m3', 100, 20000)
    eta = num(d, 'viscosity_pa_s', .001, 1e15)
    h = num(d, 'thickness_mm', .001, 5)*.001
    angle = num(d, 'inclination_deg', 0, 90)
    time = num(d, 'duration_s', 0, 86400)
    temperature = num(d, 'temperature_c', 0, 1800)
    velocity = rho*9.80665*math.sin(math.radians(angle))*h*h/(3*eta)
    re = rho*velocity*h/eta
    if re > 1:
        raise OutcomeInputError('OUTSIDE_CONSERVATIVE_CREEPING_FLOW_SCOPE')
    return result('flow', {'mean_velocity_mm_s': velocity*1000,
                          'ideal_mean_travel_mm': velocity*time*1000,
                          'reynolds_rho_u_h_over_eta': re, 'temperature_c': temperature},
                  ['Steady, isothermal, fully molten Newtonian film on an infinite flat incline; no slip and no surface shear.',
                   'Angle measured from horizontal. Constant thickness, viscosity and density; no crystallization or bubbles.',
                   'Travel is mean fluid motion, NOT the advancing glaze edge or shelf-run distance.',
                   'Finite glaze patches, capillarity, wetting and changing firing conditions require a different model.'])


def wetting(d):
    fields(d, ['surface_tension_n_m', 'contact_angle_deg', 'temperature_c', 'young_dupre_assumptions'])
    if d['young_dupre_assumptions'] is not True:
        raise OutcomeInputError('WETTING_ASSUMPTIONS_REQUIRED')
    gamma = num(d, 'surface_tension_n_m', .000001, 10)
    theta = num(d, 'contact_angle_deg', 0, 180)
    temperature = num(d, 'temperature_c', 0, 1800)
    work = gamma*(1+math.cos(math.radians(theta)))
    return result('wetting', {'ideal_work_of_adhesion_j_m2': work, 'temperature_c': temperature},
                  ['Young-Dupre reversible interfacial work, not fired bond strength or percent adhesion.',
                   'Requires equilibrium contact angle and surface tension at the same temperature and atmosphere.',
                   'Ideal smooth homogeneous nonreactive substrate; rough porous reacting clay may violate these assumptions.',
                   'Room-temperature water contact angle is not a molten-glaze contact angle.'])


def porosity(d):
    fields(d, ['dry_mass_g', 'saturated_mass_g', 'suspended_mass_g', 'specimen_scope'])
    if d['specimen_scope'] not in ('UNGLAZED_BODY', 'WHOLE_GLAZED_SPECIMEN'):
        raise OutcomeInputError('INVALID_SPECIMEN_SCOPE')
    dry = num(d, 'dry_mass_g', .000001, 1e7)
    sat = num(d, 'saturated_mass_g', .000001, 1e7)
    suspended = num(d, 'suspended_mass_g', 0, 1e7)
    if sat < dry or suspended >= dry:
        raise OutcomeInputError('INCONSISTENT_WEIGHINGS')
    return result('porosity', {'water_absorption_mass_pct': 100*(sat-dry)/dry,
                              'apparent_open_porosity_volume_pct': 100*(sat-dry)/(sat-suspended),
                              'specimen_scope': d['specimen_scope']},
                  ['Derived from supplied dry/saturated/suspended weighings under consistent saturation and fluid conditions.',
                   'Whole-specimen result does not isolate glaze porosity, closed pores or pinholes.',
                   'No ASTM compliance claimed; calibration and a complete test procedure are required.'], 'CALCULATED')


def gloss(d):
    fields(d, ['angle_deg', 'readings_gu', 'instrument_id'])
    angle = num(d, 'angle_deg', 0, 90)
    if angle not in (20, 45, 60, 75, 85) or not isinstance(d['instrument_id'], str) or not d['instrument_id'].strip():
        raise OutcomeInputError('INVALID_GLOSS_METHOD')
    readings = d['readings_gu']
    if not isinstance(readings, list) or not 1 <= len(readings) <= 1000:
        raise OutcomeInputError('INVALID_GLOSS_READINGS')
    values = [num({'v': v}, 'v', 0, 2000) for v in readings]
    return result('gloss', {'mean_gu': statistics.mean(values), 'angle_deg': angle,
                           'reading_count': len(values),
                           'sample_sd_gu': statistics.stdev(values) if len(values)>1 else None},
                  ['Summary of supplied gloss readings, not a recipe-to-gloss prediction.',
                   'Gloss units are not percent reflectance; compare identical geometry and calibration.',
                   'Reading count is not independent specimen count; spread is not instrument uncertainty.',
                   'No universal matte/satin/gloss threshold is applied.'], 'CALCULATED')


METHODS = {'fit': fit, 'flow': flow, 'wetting': wetting, 'porosity': porosity, 'gloss': gloss}


def assess_outcomes(payload):
    if not isinstance(payload, dict) or set(payload)-set(METHODS):
        raise OutcomeInputError('UNKNOWN_OUTCOME_SECTION')
    snapshot = deepcopy(payload)
    sections = {}
    for name, method in METHODS.items():
        data = snapshot.get(name)
        if data is None:
            sections[name] = dict(status='UNAVAILABLE', reason='REQUIRED_PROPERTY_OR_MEASUREMENT_NOT_PROVIDED', probability=None)
        else:
            sections[name] = method(data)
            sections[name]['input_kind'] = data['input_kind']
            sections[name]['source_ref'] = data['source_ref']
        sections[name]['requirements'] = deepcopy(REQUIREMENTS[name])
    encoded = json.dumps({'version': VERSION, 'input': snapshot}, sort_keys=True, allow_nan=False).encode()
    return dict(engine_version=VERSION, input_hash=hashlib.sha256(encoded).hexdigest(),
                input_snapshot=snapshot, sections=sections, physical_validation='NOT_PERFORMED',
                overall_success_probability=None,
                notice='Indicators are not a combined firing simulation or calibrated defect prediction.')
