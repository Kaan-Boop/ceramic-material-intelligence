"""Source-specific, offline S3/S4 transcription; never a physics model.

Only the reviewed PDF hash is accepted. Coordinates are PDF points measured
from the top-left corner. No normalization, imputation, or curve fitting.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

VERSION = "conte-s3-s4-transcription-v1"
PDF_HASH = "43fb9ce2b12683b1563978a315f44da45a2e28e784f41b059be9f28e5308f0ce"
MANIFEST = Path("data/manifests/melt-evidence-2026-09-21-batch2.json")
DEFAULT_OUTPUT = Path("data/reference/conte-2018-viscosity-staging.json")
OXIDES = "SiO2 TiO2 Al2O3 FeO MgO CaO Na2O K2O MnO P2O5".split()
REFERENCES = {"IGC": 33, "MNV": 33, "MST": 34, "CI_OF": 34, "MDV": 34,
              "G.2000": 32, "AMS-B1": 35, "AMS-D1": 35, "Trachyte": 36, "Phonolite": 36}
EXPECTED_COUNTS = {"IGC": 18, "MNV": 18, "MST": 21, "CI_OF": 20, "MDV": 17,
                   "G.2000": 22, "AMS-B1": 11, "AMS-D1": 14, "Trachyte": 24, "Phonolite": 20}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def cell(word):
    raw = word["text"]
    require(raw == "—" or re.fullmatch(r"\d+(?:\.\d+)?", raw), "INVALID_CELL")
    return {"raw_text": raw, "value": None if raw == "—" else float(raw),
            "missing_reason": "SOURCE_DASH_UNDEFINED" if raw == "—" else None,
            "bbox_pdf_points": [round(word[k], 3) for k in ("x0", "top", "x1", "bottom")]}


def lines(words):
    groups = []
    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if not groups or abs(word["top"] - groups[-1][0]["top"]) > 2:
            groups.append([])
        groups[-1].append(word)
    return [sorted(group, key=lambda w: w["x0"]) for group in groups]


def parse_s3(page):
    records = []
    for group in lines([w for w in page.extract_words() if 440 < w["top"] < 575]):
        tokens = [w["text"] for w in group]
        require(len(tokens) == 12 and tokens[0] in REFERENCES, "S3_LAYOUT_CHANGED")
        sample = tokens[0]
        require(tokens[-1] == f"[{REFERENCES[sample]}]", "S3_REFERENCE_CHANGED")
        composition = {oxide: cell(w) for oxide, w in zip(OXIDES, group[1:-1])}
        numeric = [Decimal(v["raw_text"]) for v in composition.values() if v["value"] is not None]
        records.append({"sample_id": sample, "reference_in_parent": REFERENCES[sample],
                        "source_locator": {"table": "S3", "physical_page": 3, "row": len(records) + 1},
                        "evidence_kind": "OBSERVED", "method_kind": "EMPIRICAL", "qualifier": "REPORTED",
                        "unit": None, "analysis_basis": "UNKNOWN",
                        "unit_status": "NOT_EXPLICIT_IN_TABLE_HEADER_OR_CAPTION",
                        "composition": composition, "reported_numeric_sum": float(sum(numeric)),
                        "normalization_applied": False})
    require(len(records) == 10 and {r["sample_id"] for r in records} == set(REFERENCES), "S3_SAMPLES_CHANGED")
    return records


def parse_s4(pages):
    records = []
    # Separate panel state; physical page numbering avoids the source's repeated footer numbers.
    for panel, bounds in (("left", (76, 304)), ("right", (304, 520))):
        current = None
        for physical_page in (4, 5, 6):
            top, bottom = (420, 778) if physical_page == 4 else (75, 780) if physical_page == 5 else (75, 290)
            words = [w for w in pages[physical_page - 1].extract_words()
                     if bounds[0] <= w["x0"] < bounds[1] and top < w["top"] < bottom]
            for row_number, group in enumerate(lines(words), 1):
                first = group[0]["text"]
                if first in REFERENCES or first == "Phono":
                    current = "Phonolite" if first == "Phono" else first
                    group = group[1:]
                elif first == "lite":
                    require(current == "Phonolite", "UNEXPECTED_SPLIT_LABEL")
                    group = group[1:]
                elif first.startswith("["):
                    require(current is not None and first == f"[{REFERENCES[current]}]", "S4_REFERENCE_CHANGED")
                    group = group[1:]
                require(current is not None and len(group) == 4, "S4_LAYOUT_CHANGED")
                values = [cell(w) for w in group]
                require(all(v["value"] is not None for v in values), "S4_MISSING_VALUE")
                temp = values[0]
                require(temp["value"].is_integer(), "TEMPERATURE_NOT_INTEGER")
                outputs = {}
                for name, value in zip(("experimental", "giordano", "fluegel"), values[1:]):
                    observed = name == "experimental"
                    outputs[name] = {**value, "unit": "log10(Pa.s)",
                                     "evidence_kind": "OBSERVED" if observed else "PREDICTED",
                                     "method_kind": "EMPIRICAL",
                                     "qualifier": "REPORTED",
                                     "uncertainty": None,
                                     "uncertainty_missing_reason": "NOT_REPORTED_IN_TABLE",
                                     "method_id": "literature_measurement_not_yet_resolved" if observed else name + "_as_reported_by_conte_2018",
                                     "method_version": None}
                records.append({"id": f"S4-p{physical_page}-{panel}-r{row_number:02}",
                                "sample_id": current, "reference_in_parent": REFERENCES[current],
                                "source_locator": {"table": "S4", "physical_page": physical_page,
                                                   "panel": panel, "row": row_number},
                                "temperature": {**temp, "unit": "degC"}, "viscosity": outputs})
    require(dict(Counter(r["sample_id"] for r in records)) == EXPECTED_COUNTS, "S4_ROW_COUNTS_CHANGED")
    require(len({(r["sample_id"], r["temperature"]["value"]) for r in records}) == len(records), "DUPLICATE_SAMPLE_TEMPERATURE")
    return records


def build(pdf_path):
    import pdfplumber
    from pypdf import PdfReader
    raw_hash = hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest()
    require(raw_hash == PDF_HASH, "UNREVIEWED_PDF_HASH")
    with pdfplumber.open(pdf_path) as pdf:
        composition = parse_s3(pdf.pages[2])
        viscosity = parse_s4(pdf.pages)
    # A different text extractor checks every numeric row against the same PDF.
    # This is extraction agreement, not independent scientific validation.
    texts = [re.sub(r"\s+", " ", p.extract_text()) for p in PdfReader(pdf_path).pages]
    for row in composition:
        sequence = " ".join(row["composition"][o]["raw_text"] for o in OXIDES)
        require(sequence in texts[2], "S3_TEXT_EXTRACTOR_DISAGREEMENT")
    for row in viscosity:
        sequence = " ".join([row["temperature"]["raw_text"]] +
                            [row["viscosity"][n]["raw_text"] for n in ("experimental", "giordano", "fluegel")])
        require(sequence in texts[row["source_locator"]["physical_page"] - 1], "S4_TEXT_EXTRACTOR_DISAGREEMENT")
    return {"schema_version": VERSION,
            "source": {"doi": "10.3390/ma11122475", "source_id": "stoneware-melt-2018-supplement",
                       "authors": "Sonia Conte; Chiara Zanelli; Matteo Ardit; Giuseppe Cruciani; Michele Dondi",
                       "pdf_sha256": PDF_HASH, "license": "CC-BY-4.0",
                       "license_basis": "Parent JATS links supplement; see melt-evidence-review-2026-09-27.json",
                       "acquisition_manifest": MANIFEST.as_posix(), "retrieval_date": "2026-09-21"},
            "transcription": {"version": VERSION, "review_date": "2026-09-27",
                              "parser_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                              "pdfplumber_version": pdfplumber.__version__,
                              "visual_review_physical_pages": [3, 4, 5, 6],
                              "numeric_rows_cross_checked_with_pypdf": True,
                              "independent_second_reviewer": False,
                              "original_measurement_references_checked": False},
            "status": "RESEARCH_QUARANTINE", "core_engine_eligible": False,
            "product_release_approved": False, "training_enabled": False,
            "limitations": ["S3 unit and analysis basis are unresolved; no material analysis promoted.",
                            "Model columns are transcribed predictions, not locally recomputed results.",
                            "Original references 32-36 and calibration overlap require review.",
                            "No independent validation of NBS 710 or real clay-glaze wetting.",
                            "Rows are temperatures within sample families, not independent experiments."],
            "counts": {"compositions": len(composition), "temperature_rows": len(viscosity),
                       "reported_experimental_values": len(viscosity), "reported_model_values": 2 * len(viscosity),
                       "by_sample": EXPECTED_COUNTS},
            "compositions": composition, "viscosity_rows": viscosity}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Rebuild in memory and compare; never overwrite")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next(f for f in manifest["files"] if f["sha256"] == PDF_HASH)
    doc = build(Path(manifest["storage_root"]) / entry["readable_path"])
    if args.check:
        require(json.loads(args.output.read_text(encoding="utf-8")) == doc, "STAGED_OUTPUT_DIFFERS")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(doc, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    main()
