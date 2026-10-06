"""Pure comparison logic for internal and external chemistry reports.

The comparator deliberately compares only fields with a shared meaning. It
does not decide which calculator is correct and does not turn a disagreement
into a prediction or confidence score.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from research.chemistry.foundation import digest


def comparison_input_hash(internal_hash: str, external_ingredients: Sequence[Mapping], cone: int) -> str:
    """Hash the exact cross-engine input envelope used by a comparison run."""
    return digest({
        "internal": internal_hash,
        "external": list(external_ingredients),
        "cone": cone,
    })


def value_delta(internal: float | None, external: float | None) -> dict:
    """Return a stable numeric difference payload without inventing zeros."""
    if internal is None or external is None:
        return {
            "status": "UNAVAILABLE",
            "internal": internal,
            "external": external,
            "delta": None,
            "delta_pct": None,
        }
    delta = external - internal
    return {
        "status": "AVAILABLE",
        "internal": internal,
        "external": external,
        "delta": delta,
        "delta_pct": (delta / internal * 100) if internal else None,
    }


def compare_calculated_reports(
    internal: Mapping,
    external: Mapping,
    *,
    external_ingredients: Sequence[Mapping],
    cone: int,
) -> dict:
    """Build a reproducible ``comparison-run-v1`` result.

    ``internal`` is the project chemistry-engine report and ``external`` is
    the wrapper returned by :func:`run_umf_reference`. The two material
    analyses are not assumed to be identical; that limitation is always
    included in the output.
    """
    external_report = external.get("report") or {}
    internal_umf = (internal.get("umf") or {}).get("values") or {}
    external_umf = external_report.get("umf_formula") or {}
    oxide_keys = sorted(set(internal_umf) | set(external_umf))
    umf_differences = {
        oxide: value_delta(internal_umf.get(oxide), external_umf.get(oxide))
        for oxide in oxide_keys
    }
    internal_ratio = ((internal.get("ratios") or {}).get("SiO2_to_Al2O3_molar") or {}).get("value")
    external_ratio = (external_report.get("ratios") or {}).get("sio2_al2o3")
    status = (
        "COMPARED"
        if external_report.get("success") and not external_report.get("missing_materials")
        else "PARTIAL"
    )
    warnings = [
        "İki motorun malzeme adları aynı fiziksel ürünü temsil etmiyorsa sayısal fark anlamlı bir doğrulama değildir.",
        "OpenGlaze çıktısı yaklaşık/harici referanstır; ölçülmüş sır, CTE veya yüzey sonucu değildir.",
    ]
    if external_report.get("missing_materials"):
        warnings.append(
            "OpenGlaze bazı malzemeleri tanımadı: "
            + ", ".join(external_report["missing_materials"])
        )
    if external.get("status") == "UNAVAILABLE":
        warnings.append(
            "Harici OpenGlaze kaynağı bu çalıştırmada erişilebilir değildi; fark tablosu oluşturulmadı."
        )
    return {
        "schema_version": "comparison-run-v1",
        "status": status,
        "evidence_kind": "CALCULATED",
        "method_kind": "DETERMINISTIC",
        "input_hash": comparison_input_hash(internal.get("input_hash"), external_ingredients, cone),
        "input_snapshot": {
            "external_ingredients": list(external_ingredients),
            "cone": cone,
        },
        "internal": {
            "engine_version": internal.get("engine_version"),
            "input_hash": internal.get("input_hash"),
            "input_snapshot": internal.get("input_snapshot"),
            "umf_convention": internal.get("umf_convention"),
            "umf": internal.get("umf"),
            "ratios": internal.get("ratios"),
        },
        "external": external,
        "differences": {
            "umf": umf_differences,
            "SiO2_to_Al2O3_molar": value_delta(internal_ratio, external_ratio),
            "thermal_expansion": {
                "status": "UNAVAILABLE",
                "reason": "Çekirdek motorumuzda bu karşılaştırma için doğrulanmış CTE değeri yok.",
            },
        },
        "warnings": warnings,
        "limitations": [
            "Fark tablosu yalnızca seçilmiş sayısal alanları karşılaştırır; hangi motorun doğru olduğunu ilan etmez.",
            "Gerçek doğrulama için aynı hammaddelerle test karosu ve ölçüm gerekir.",
        ],
    }


def replay_comparison_snapshot(snapshot: Mapping) -> dict:
    """Recompute comparison arithmetic from a downloaded snapshot.

    This verifies report integrity only. It does not rerun OpenGlaze or claim
    that the historical external source is still available.
    """
    if snapshot.get("schema_version") != "comparison-run-v1":
        return {"status": "UNAVAILABLE", "reason": "UNSUPPORTED_SCHEMA"}
    internal = snapshot.get("internal")
    external = snapshot.get("external")
    input_snapshot = snapshot.get("input_snapshot") or {}
    external_ingredients = input_snapshot.get("external_ingredients")
    cone = input_snapshot.get("cone")
    if not isinstance(internal, Mapping) or not isinstance(external, Mapping):
        return {"status": "UNAVAILABLE", "reason": "MISSING_ENGINE_REPORT"}
    if not isinstance(external_ingredients, list) or not isinstance(cone, int):
        return {"status": "UNAVAILABLE", "reason": "MISSING_INPUT_SNAPSHOT"}
    rebuilt = compare_calculated_reports(
        internal,
        external,
        external_ingredients=external_ingredients,
        cone=cone,
    )
    hash_matches = rebuilt["input_hash"] == snapshot.get("input_hash")
    differences_match = rebuilt["differences"] == snapshot.get("differences")
    status = "PASS" if hash_matches and differences_match else "FAIL"
    return {
        "status": status,
        "input_hash_matches": hash_matches,
        "differences_match": differences_match,
        "recomputed_input_hash": rebuilt["input_hash"],
        "limitations": [
            "Bu kontrol snapshot aritmetiğini doğrular; harici OpenGlaze kaynağını yeniden çalıştırmaz.",
            "Kaynak/ref/checksum bulunmadan tarihsel harici hesaplayıcı erişilebilirliği kanıtlanmaz.",
        ],
    }
