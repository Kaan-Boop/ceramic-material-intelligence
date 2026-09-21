"""Bounded stoichiometry adapter for the reviewed periodictable package.

No network, database, reaction kinetics, thermodynamic or safety predictions.
"""
from importlib.metadata import version
import hashlib
import json
import math
import re

import periodictable as pt
from periodictable.mass import element_mass

ENGINE_VERSION = "chemistry-foundation/0.1.0"
PACKAGE_VERSION = "2.1.0"
SOURCE = "https://github.com/python-periodictable/periodictable/tree/182ef63a9ec118ef725aae5bb81860f4ba0fb573"
CONSTANT_SET = "periodictable-2.1.0-published-element-masses"
SOURCE_METADATA = {
    "source_name": "periodictable 2.1.0 mass table", "source_url": SOURCE,
    "source_type": "VERSIONED_OPEN_SOURCE_REFERENCE", "source_author": "Paul Kienzle and contributors",
    "source_license": "Public-domain mass/formula modules; package retains file-specific BSD notices",
    "commercial_use_allowed": "ALLOWED_WITH_LICENSE_CONDITIONS", "attribution_required": True,
    "share_alike_required": False, "retrieval_date": "2026-09-22",
    "license_evidence": SOURCE.replace("/tree/", "/blob/") + "/LICENSE.txt",
    "acquisition_manifest": "data/manifests/chemistry-sources-2026-09-22.json",
}
OXIDES = ("SiO2", "Al2O3", "B2O3", "Li2O", "Na2O", "K2O", "CaO", "MgO", "SrO", "BaO", "ZnO",
          "FeO", "Fe2O3", "Fe3O4", "CuO", "Cu2O", "CoO", "Co3O4", "MnO", "MnO2", "Mn2O3",
          "Cr2O3", "NiO", "TiO2", "ZrO2", "SnO2", "P2O5", "PbO", "CdO", "Sb2O3", "V2O5", "Bi2O3",
          "CeO2", "Pr6O11", "Nd2O3")
# This is a chemical representation list, NOT a recommended set of ingredients.
PRIORITY_ELEMENTS = set("H C N O F S Cl Si Al B Li Na K Ca Mg Sr Ba Zn Fe Cu Co Mn Cr Ni Ti Zr Sn P Pb Cd Se Sb V Bi Ce Pr Nd".split())


class ChemistryInputError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def require_version():
    if version("periodictable") != PACKAGE_VERSION:
        raise ChemistryInputError("UNREVIEWED_PACKAGE_VERSION")


def element_catalog():
    require_version()
    # The pinned package retains nominal isotope masses for radioactive elements.
    # Only entries in its published standard-element table are mass-capable here.
    published = {line.split()[1]: line.split()[3] for line in element_mass.splitlines()
                 if line.strip() and line.split()[3] != "-"}
    source_lines = {line.split()[1]: line for line in element_mass.splitlines() if line.strip()}
    rows = []
    for element in pt.elements:
        mass = float(element.mass) if element.symbol in published else None
        rows.append({"atomic_number": element.number, "symbol": element.symbol, "name": element.name,
                     "selected_molar_mass_g_mol": mass, "reported_mass_notation": published.get(element.symbol),
                     "reported_table_line": source_lines.get(element.symbol),
                     "status": "AVAILABLE" if mass is not None else "UNAVAILABLE",
                     "unavailable_reason": None if mass is not None else "NO_STANDARD_WEIGHT_IN_SELECTED_TABLE_ISOTOPE_SELECTION_NOT_SUPPORTED",
                     "priority_for_ceramics": element.symbol in PRIORITY_ELEMENTS,
                     "source_url": SOURCE.replace("/tree/", "/blob/") + "/periodictable/mass.py", "constant_set_id": CONSTANT_SET,
                     "source_metadata": dict(SOURCE_METADATA),
                     "evidence_kind": "OBSERVED", "qualifier": "REPORTED_REFERENCE_VALUE",
                     "uncertainty": None,
                     "limitations": "Pinned package selection, not latest CIAAW or sample-specific isotope composition; no ceramic thermal properties"})
    return rows


def atom_counts(formula):
    require_version()
    if not isinstance(formula, str) or not 1 <= len(formula) <= 128:
        raise ChemistryInputError("FORMULA_LENGTH_1_TO_128_REQUIRED")
    tokens = re.findall(r"[A-Z][a-z]?|[1-9][0-9]{0,3}|[()]", formula)
    if "".join(tokens) != formula:
        raise ChemistryInputError("ONLY_NEUTRAL_INTEGER_FORMULAS_SUPPORTED")
    depth, previous = 0, None
    for token in tokens:
        if token == "(":
            depth += 1
            if depth > 8:
                raise ChemistryInputError("FORMULA_NESTING_LIMIT")
        elif token == ")":
            if depth == 0 or previous == "(":
                raise ChemistryInputError("INVALID_PARENTHESES")
            depth -= 1
        elif token.isdigit() and (previous is None or previous in ("(",) or previous.isdigit()):
            raise ChemistryInputError("INVALID_MULTIPLIER")
        previous = token
    if depth:
        raise ChemistryInputError("INVALID_PARENTHESES")
    try:
        atoms = pt.formula(formula).atoms
    except (ValueError, KeyError, TypeError) as exc:
        raise ChemistryInputError("INVALID_FORMULA") from exc
    if not atoms or sum(atoms.values()) > 10000:
        raise ChemistryInputError("FORMULA_ATOM_LIMIT")
    counts = {}
    for element, count in atoms.items():
        if element.number < 1 or element.number > 118 or element.symbol not in {e.symbol for e in pt.elements}:
            raise ChemistryInputError("UNSUPPORTED_CHEMICAL_ENTITY")
        if not float(count).is_integer() or count <= 0:
            raise ChemistryInputError("POSITIVE_INTEGER_ATOM_COUNTS_REQUIRED")
        counts[element.symbol] = int(count)
    return dict(sorted(counts.items()))


def nonnegative(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ChemistryInputError("FINITE_NONNEGATIVE_MASS_REQUIRED")
    try:
        value = float(value)
    except OverflowError:
        raise ChemistryInputError("FINITE_NONNEGATIVE_MASS_REQUIRED") from None
    if not math.isfinite(value) or not 0 <= value <= 1e12:
        raise ChemistryInputError("MASS_OUTSIDE_RESEARCH_SCOPE_0_TO_1E12_G")
    return value


def formula_report(formula, amount_g=100.0):
    amount_g = nonnegative(amount_g)
    atoms = atom_counts(formula)
    rows = element_catalog()
    catalog = {row["symbol"]: row for row in rows}
    unavailable = [symbol for symbol in atoms if catalog[symbol]["status"] != "AVAILABLE"]
    if unavailable:
        raise ChemistryInputError("STANDARD_MASS_UNAVAILABLE: " + ",".join(unavailable))
    contributions = {symbol: count * catalog[symbol]["selected_molar_mass_g_mol"] for symbol, count in atoms.items()}
    mass = math.fsum(contributions.values())
    return {"formula": formula, "amount_g": amount_g, "atom_counts": atoms,
            "molar_mass_g_mol": mass, "amount_mol": amount_g / mass,
            "element_mass_g": {symbol: amount_g * value / mass for symbol, value in contributions.items()},
            "engine_version": ENGINE_VERSION, "constant_set_id": CONSTANT_SET,
            "constant_set_sha256": digest(rows), "package_version": PACKAGE_VERSION,
            "input_hash": digest({"formula": formula, "amount_g": amount_g, "constants": digest(rows), "engine": ENGINE_VERSION}),
            "evidence_kind": "CALCULATED", "method_kind": "DETERMINISTIC", "qualifier": "THEORETICAL_STOICHIOMETRY",
            "source_refs": [SOURCE], "source_metadata": dict(SOURCE_METADATA),
            "warnings": ["Pure formula arithmetic, not a manufacturer analysis or firing prediction",
            "Pinned constants are not advertised as CIAAW 2024; Zr/Gd/Lu changes require a separate constant-set revision"]}


def oxide_equivalent(element, element_mass_g, oxide_formula):
    """Explicit analytical reporting basis, NOT a redox/phase conversion model."""
    element_mass_g = nonnegative(element_mass_g)
    if not isinstance(element, str) or not re.fullmatch(r"[A-Z][a-z]?", element):
        raise ChemistryInputError("ELEMENT_SYMBOL_REQUIRED")
    report = formula_report(oxide_formula, 1.0)
    if element == "O" or set(report["atom_counts"]) != {element, "O"}:
        raise ChemistryInputError("EXPLICIT_MATCHING_BINARY_OXIDE_REQUIRED")
    factor = 1 / report["element_mass_g"][element]
    return {"element": element, "element_mass_g": element_mass_g, "oxide_formula": oxide_formula,
            "oxide_equivalent_g": element_mass_g * factor, "factor": factor,
            "oxygen_assigned_g": element_mass_g * (factor - 1),
            "evidence_kind": "CALCULATED", "method_kind": "DETERMINISTIC", "qualifier": "ASSUMED_REPORTING_BASIS",
            "constant_set_id": report["constant_set_id"], "constant_set_sha256": report["constant_set_sha256"],
            "source_refs": report["source_refs"], "engine_version": ENGINE_VERSION,
            "source_metadata": dict(SOURCE_METADATA),
            "input_hash": digest({"element": element, "mass_g": element_mass_g, "oxide_formula": oxide_formula,
                                  "constants": report["constant_set_sha256"], "engine": ENGINE_VERSION}),
            "warning": "Does not identify actual oxidation state or phase; cannot close a partial analysis to 100%"}


def reaction_balance(reactants, products):
    """Verify a supplied equation. Do not predict feasibility, onset or extent."""
    def totals(side):
        if not isinstance(side, dict) or not 1 <= len(side) <= 32:
            raise ChemistryInputError("REACTION_SIDE_1_TO_32_SPECIES_REQUIRED")
        result = {}
        for formula, coefficient in side.items():
            if type(coefficient) is not int or not 1 <= coefficient <= 10000:
                raise ChemistryInputError("POSITIVE_INTEGER_COEFFICIENT_REQUIRED")
            for symbol, count in atom_counts(formula).items():
                result[symbol] = result.get(symbol, 0) + count * coefficient
        return result
    left, right = totals(reactants), totals(products)
    residual = {symbol: right.get(symbol, 0) - left.get(symbol, 0) for symbol in sorted(left.keys() | right.keys())}
    return {"reactants": dict(reactants), "products": dict(products), "atom_residual_products_minus_reactants": residual,
            "balanced": all(value == 0 for value in residual.values()), "evidence_kind": "CALCULATED",
            "method_kind": "DETERMINISTIC", "engine_version": ENGINE_VERSION,
            "input_hash": digest({"reactants": reactants, "products": products, "engine": ENGINE_VERSION}),
            "physical_reaction": {"status": "UNAVAILABLE", "reason": "No phase thermodynamics, kinetics or atmosphere model"}}
