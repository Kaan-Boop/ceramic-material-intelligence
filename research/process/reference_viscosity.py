"""Historical NBS 710 reference fit, not a composition-to-viscosity model."""
from research.process.outcomes import flow, num, OutcomeInputError

VERSION = 'nbs710-reference/0.1.0'
MATERIAL_ID = 'NBS-710-1962'
SOURCE = 'https://tsapps.nist.gov/srmext/certificates/archives/710.pdf'
SHA256 = 'a46cb6d423dc4073f23b902aca52bed36a402f5d7d5b232a727364845c6ea59d'


def viscosity(temperature_c, material_id):
    """Combined Fulcher fit on a deliberately restricted high-T table interval.

    Original log10(eta/poise) = -1.626 + 4236.118/(T_C - 266).
    We limit evaluation to 821.5--1434.3 C, Table 1 log-poise 6--2.
    This is a project scope choice, not a newly certified validity interval.
    """
    if material_id != MATERIAL_ID:
        raise OutcomeInputError('REFERENCE_MATERIAL_MISMATCH')
    t = num({'temperature_c': temperature_c}, 'temperature_c', 821.5, 1434.3)
    log_poise = -1.626 + 4236.118 / (t - 266.0)
    return {
        'status': 'AVAILABLE', 'evidence_kind': 'PREDICTED', 'method_kind': 'EMPIRICAL',
        'qualifier': 'HISTORICAL_REFERENCE_FIT_ONLY', 'method_version': VERSION,
        'material_id': MATERIAL_ID, 'temperature_c': t,
        'viscosity_pa_s': 10 ** (log_poise - 1.0),
        'source_ref': SOURCE, 'raw_sha256': SHA256,
        'source_equation_annotation': '+/-0.020 in log10 poise; not assigned a confidence level here',
        'uncertainty': None, 'physical_validation': 'NOT_PERFORMED_BY_PROJECT',
        'limitations': ['Not transferable to another recipe or material.',
                        'Historical fitted reference, not a new measurement or current certification.',
                        'Table agreement checks transcription, not independent physical validation.'],
    }


def reference_flow(*, temperature_c, material_id, density_kg_m3,
                   density_source_ref, density_input_kind, thickness_mm,
                   inclination_deg, duration_s, ideal_film_assumptions):
    """Isothermal bridge. No default density, geometry, time or assumptions.

    Caller must resolve density for this material at this temperature.
    Input kind/source are declarations, not automatic provenance verification.
    """
    eta = viscosity(temperature_c, material_id)
    if not isinstance(density_source_ref, str) or not density_source_ref.strip():
        raise OutcomeInputError('MISSING_DENSITY_PROVENANCE')
    payload = dict(density_kg_m3=density_kg_m3, viscosity_pa_s=eta['viscosity_pa_s'],
                   thickness_mm=thickness_mm, inclination_deg=inclination_deg,
                   duration_s=duration_s, temperature_c=temperature_c,
                   ideal_film_assumptions=ideal_film_assumptions,
                   source_ref=density_source_ref, input_kind=density_input_kind,
                   conditions='Caller-supplied density at reference material temperature; isothermal ideal film.')
    result = flow(payload)
    result.update(method_version=VERSION, viscosity=eta,
                  input_snapshot=payload, material_id=MATERIAL_ID,
                  qualifier=('SYNTHETIC_SCENARIO' if density_input_kind == 'SYNTHETIC'
                             else 'REFERENCE_FIT_WITH_CALLER_SUPPLIED_DENSITY'),
                  physical_validation='NOT_PERFORMED_BY_PROJECT')
    return result
