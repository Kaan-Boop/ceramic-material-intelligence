"""Reviewed study-scoped candidate extraction, NOT production chemistry intake.

XML tables are parsed; PDF tables are a bounded manual transcription. Only pinned
documents are accepted. No inferred dry basis, unreported zeros or LOI conversion.
"""
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from pipelines.ingestion.acquire import article_authors

VERSION = "study-material-candidates-v1"
REVIEWED = {
    "metakaolin-2024": "8753e50ef07c5473fe1e9f20b3395e9ac84b21e74ce025f1deb5ac44702cbdc0",
    "feldspar-activation-2023": "3c34f5f7829227c9ef2f49cd5d8e8bd9740b335ca1d823309e331135bdea5211",
    "anorthite-2018": "dfe6d64ef2ad96638257422492e83e24fe28a6fcf696c2bb8ca6734679b7e965",
    "sanitary-body-2022": "29df3aa68d410c946d24264e54337eb8b22cf5a92b21cc5d2820c59a2e2f294e",
}


def cell(label, text):
    if text in ("–", "-", ""):
        return {"reported_as": label, "raw_value": text, "value": None,
                "unit": "wt_pct", "missing_reason": "NOT_REPORTED_OR_UNDEFINED_DASH"}
    value = Decimal(text)
    if not value.is_finite() or value < 0 or value > 100:
        raise ValueError("INVALID_REPORTED_VALUE")
    return {"reported_as": label, "raw_value": text, "value": str(value), "unit": "wt_pct"}


def candidate(source, name, labels, values, manufacturer=None, table="Table 1", page=None):
    if len(labels) != len(values) or len(set(labels)) != len(labels):
        raise ValueError("TABLE_SHAPE_CHANGED")
    measures = [cell(k, v) for k, v in zip(labels, values)]
    flags = ["ANALYSIS_BASIS_UNKNOWN", "ANALYSIS_DATE_UNKNOWN", "LOT_UNKNOWN", "OMITTED_SPECIES_UNDEFINED"]
    if any(m["value"] is None for m in measures):
        flags.append("UNDEFINED_DASH")
    if "LOI" not in labels or measures[labels.index("LOI")]["value"] is None:
        flags.append("LOI_WT_PCT_UNAVAILABLE")
    if "Others" in labels:
        flags.append("OTHERS_NOT_IDENTIFIED_OR_LOI")
    if "Cl" in labels or "S" in labels:
        flags.append("MIXED_ELEMENT_AND_OXIDE_REPORTING")
    total = sum((Decimal(m["value"]) for m in measures if m["value"] is not None), Decimal(0))
    if abs(total - 100) > Decimal("0.5"):
        flags.append("REPORTED_COLUMN_SUM_OUTSIDE_100_PLUS_MINUS_0_5")
    return {"id": source + ":" + name, "version": 1, "source_id": source,
            "name_as_reported": name, "manufacturer_as_reported": manufacturer,
            "identity_scope": "STUDY_SAMPLE_NOT_CURRENT_PRODUCT_SPECIFICATION",
            "source_table": table, "source_pdf_page": page, "analysis_basis": "UNKNOWN",
            "analysis_date": None, "lot": None, "uncertainty": None,
            "method": "XRF_REPORTED_BY_AUTHORS", "evidence_kind": "OBSERVED",
            "method_kind": "EMPIRICAL", "qualifier": "REPORTED", "status": "PARTIAL",
            "disposition": "QUARANTINED", "core_engine_eligible": False,
            "measurements": measures, "reported_numeric_column_sum": str(total),
            "sum_note": "Diagnostic only; includes LOI/Others where reported, excludes missing cells. Not mass closure or normalization.",
            "quality_flags": flags}


def xml_rows(raw, table_id, expected_header):
    table = ET.fromstring(raw).find(f".//table-wrap[@id='{table_id}']/table")
    if table is None:
        raise ValueError("TABLE_MISSING")
    rows = [["".join(c.itertext()).strip() for c in row] for row in table.findall(".//tr")]
    for c in table.findall(".//th") + table.findall(".//td"):
        if c.get("colspan", "1") != "1" or c.get("rowspan", "1") != "1":
            raise ValueError("TABLE_SPAN_CHANGED")
    if not rows or rows[0] != expected_header or any(len(r) != len(expected_header) for r in rows):
        raise ValueError("TABLE_SHAPE_CHANGED")
    return rows[1:]


def extract(source, raw):
    if source == "metakaolin-2024":
        labels = ["Al2O3", "SiO2", "Fe2O3", "MgO", "K2O", "Na2O", "Others"]
        rows = xml_rows(raw, "materials-17-00367-t001", ["Varieties"] + labels)
        if [r[0] for r in rows] != ["Devolite", "Shanxi", "M501", "1200S", "Opacilite"]:
            raise ValueError("MATERIAL_IDENTITIES_CHANGED")
        records = [candidate(source, r[0], labels, r[1:], None if r[0] == "Shanxi" else "Imerys") for r in rows]
        for r in records:
            r["exclusion_note"] = "Table 2 labels LOI in g, not wt%; do not convert without initial mass. Calcined descendants are not the raw parent analysis."
        return records
    if source == "feldspar-activation-2023":
        rows = xml_rows(raw, "materials-17-00144-t001", ["Element", "Content (%)"] * 4)
        pairs = [(r[i], r[i + 1]) for r in rows for i in range(0, 8, 2) if r[i] or r[i + 1]]
        if len(pairs) != 22:
            raise ValueError("SPECIES_COUNT_CHANGED")
        result = candidate(source, "Potash feldspar powder", [p[0] for p in pairs], [p[1] for p in pairs],
                           "Lingshou County Shengpeng Mineral Factory, Shijiazhuang, China")
        result["exclusion_note"] = "Cl/S remain elemental. MnO is not MnO2; unsupported species are retained, not discarded."
        for measurement in result["measurements"]:
            measurement["unit"] = "percent_unspecified"
        result["quality_flags"].append("PERCENT_UNIT_BASIS_NOT_EXPLICIT")
        return [result]
    if source == "anorthite-2018":
        labels = ["SiO2", "Al2O3", "Fe2O3", "CaO", "MgO", "Na2O", "K2O", "LOI"]
        data = [
            ("Super Standard Porcelain", "IMERYS Ceramics, UK", "47.1 37.1 0.7 0.26 0.33 – 1.87 12.4"),
            ("Quantum AP200F", "Cibelco–India [source spelling]", "64.9 17 0.28 0.76 0.44 2.42 12.1 0.57"),
            ("Quartz", "Morvarid–Iran", "99.15 0.68 0.03 0.12 – – – –"),
        ]
        return [candidate(source, name, labels, row.split(), manufacturer, page=2) for name, manufacturer, row in data]
    if source == "sanitary-body-2022":
        labels = ["SiO2", "Al2O3", "TiO2", "CaO", "MgO", "K2O", "Na2O", "Fe2O3", "LOI"]
        data = [
            ("Hycast VC", None, "52 31 1 2 0.4 2.1 0.2 1.2 12"),
            ("Parkaolin", "IMERYS Minerals Ltd, UK", "48 37 0.06 0.07 0.3 1.9 0.1 0.19 11.8"),
            ("Remblend (RMB)", "IMERYS Ceramics, Austell, UK", "48 37 0.05 0.07 0.3 1.75 0.1 0.8 12.1"),
            ("Na feldspar, Çine (Aydin, Turkey)", None, "70.74 17.92 0.26 0.5 0.2 0.4 9.6 0.08 0.5"),
            ("K feldspar, Çine (Aydin, Turkey)", None, "69.5 17.3 0 0.5 0.2 9 3.5 0.16 0.4"),
            ("Quartz, Bir el-Ater (Tebessa, Algeria)", None, "96.35 0.52 0.05 1.19 0.08 0.17 0.08 0.24 1.2"),
        ]
        records = [candidate(source, name, labels, row.split(), manufacturer, table="Table 2", page=2) for name, manufacturer, row in data]
        for r in records:
            r["loi_protocol_as_reported"] = "1000°C, 2 h; mass basis not explicitly established"
        return records
    raise ValueError("UNREVIEWED_SOURCE")


def build(root):
    root = Path(root).resolve()
    sources, files = {}, {}
    for path in sorted((root / "receipts").glob("*.json"), key=lambda p: json.loads(p.read_text(encoding="utf-8"))["created_at"]):
        receipt = json.loads(path.read_text(encoding="utf-8"))
        for source, meta in receipt["sources"].items():
            if source not in REVIEWED or source in receipt["failures"]:
                continue
            if meta.get("source_license") != "CC-BY-4.0" or meta.get("rights_partition") != "CC_BY_REFERENCE":
                raise ValueError("SOURCE_RIGHTS_CHANGED")
            sources[source] = meta
            for item in receipt["files"]:
                if item["source_id"] == source and item["filename"] in ("article.xml", "article.pdf"):
                    files[source] = item
    records = []
    for source, item in sorted(files.items()):
        target = (root / item["raw_path"]).resolve()
        if not target.is_relative_to(root):
            raise ValueError("UNSAFE_RAW_PATH")
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"] or item["sha256"] != REVIEWED[source]:
            raise ValueError("SOURCE_REVIEW_REQUIRED")
        if item["filename"].endswith(".xml"):
            sources[source]["source_author"] = article_authors(ET.fromstring(raw).find("./front/article-meta"))
            sources[source]["metadata_review"] = "Author names parsed from pinned article XML; initial receipts preserved unchanged."
        else:
            sources[source]["source_type"] = "PUBLISHED_ARTICLE_DIRECT_DOWNLOAD"
        for record in extract(source, raw):
            record.update(raw_sha256=item["sha256"], source_url=item["source_url"],
                          source_locator=record["source_table"] + ": " + record["name_as_reported"])
            records.append(record)
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_CANDIDATE")
    thermal = thermal_reference(files["anorthite-2018"]) if "anorthite-2018" in files else []
    return {"schema_version": VERSION, "release_kind": "RESEARCH_QUARANTINE_NOT_ENGINE_INPUT",
            "parser_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "core_engine_eligible": False, "external_publication": False, "training_release": False,
            "transcription_review": "Single assistant; no independent second reviewer",
            "sources": sources, "records": records, "thermal_references": thermal,
            "report": {"candidate_count": len(records), "accepted_for_core": 0,
                       "quarantined": len(records), "duplicate_candidate_ids": 0,
                       "thermal_reference_series": len(thermal),
                       "thermal_reference_cells": sum(len(t["intervals"]) for t in thermal),
                       "source_counts": dict(Counter(r["source_id"] for r in records)),
                       "flag_counts": dict(Counter(f for r in records for f in r["quality_flags"])),
                       "missing_reviewed_sources": sorted(set(REVIEWED) - files.keys())}}


def thermal_reference(item):
    """Table 3 S0 subset; deliberately not a ThermalCurve input schema."""
    bounds = [(25, 100), (100, 200), (200, 300), (300, 400), (400, 500), (500, 600)]
    series = []
    for firing, values in [(1250, "5.1932 5.6889 6.1479 6.6729 7.5255 11.0457"),
                           (1340, "4.5047 5.324 5.5183 6.0361 6.7346 9.168")]:
        series.append({"id": f"anorthite-2018:S0:{firing}", "source_id": "anorthite-2018",
                       "raw_sha256": item["sha256"], "source_url": item["source_url"],
                       "source_pdf_page": 5, "source_table": "Table 3, S0 column",
                       "specimen": "S0", "reported_firing_temperature_C": firing,
                       "recipe_table": "Table 2", "recipe_wt_pct": {"kaolin": "50", "quartz": "25", "K-feldspar": "25"},
                       "recipe_material_refs": ["anorthite-2018:Super Standard Porcelain", "anorthite-2018:Quartz", "anorthite-2018:Quantum AP200F"],
                       "quantity_kind": "REPORTED_INTERVAL_MEAN_LINEAR_TEC", "unit": "1e-6/K",
                       "evidence_kind": "OBSERVED", "method_kind": "EMPIRICAL", "qualifier": "REPORTED",
                       "status": "PARTIAL", "measurement_branch": "UNKNOWN", "uncertainty": None,
                       "reference_length_definition": None, "measurement_instrument": None,
                       "model_input_eligible": False,
                       "limitation": "Table says measured; text says average TEC calculated. Measurement protocol/branch/reference length not established. Not instantaneous alpha(T), not a glaze/body pair, no crack probability.",
                       "intervals": [{"from_C": lo, "to_C": hi, "reported_value": value} for (lo, hi), value in zip(bounds, values.split())]})
    return series


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.storage)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps(result["report"], ensure_ascii=False))


if __name__ == "__main__":
    main()
