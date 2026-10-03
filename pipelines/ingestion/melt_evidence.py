"""Archive reviewed supplementary viscosity and adjacent wetting evidence.

No physics parameters are promoted and no upstream executable is run.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import stat
from uuid import uuid4
import zipfile

from .acquire import Collector
from .flow_sources import base_metadata, immutable_write, json_bytes, parse_article, save_source_file, verify_receipt

VERSION = "melt-evidence-v1"
SUPPLEMENT = "materials-11-02475-s001.pdf"
ZENODO_RECORD = 15837287
ZENODO_FILES = (
    "ReadMe.txt", "FTIR_Sample_1_Graphite_RAW.CSV", "FTIR_Sample_4_Graphite_RAW.CSV",
    "FTIR_Sample_1_Platinum_RAW.CSV", "FTIR_Sample_4_Platinum_RAW.CSV", "coatings-15-00967.pdf",
)


def selected_pdf_from_zip(raw):
    """No extractall; reject suspicious members before reading the selected PDF."""
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        members = archive.infolist()
        if len(members) > 100 or sum(i.file_size for i in members) > 32 * 1024 * 1024:
            raise ValueError("ARCHIVE_LIMIT")
        names = set()
        for member in members:
            path = PurePosixPath(member.filename.replace("\\", "/"))
            if (path.is_absolute() or ".." in path.parts or ":" in member.filename
                    or stat.S_ISLNK(member.external_attr >> 16) or member.flag_bits & 1):
                raise ValueError("UNSAFE_ARCHIVE_MEMBER")
            if member.filename in names:
                raise ValueError("DUPLICATE_ARCHIVE_MEMBER")
            names.add(member.filename)
        if SUPPLEMENT not in names:
            raise ValueError("EXPECTED_SUPPLEMENT_MISSING")
        info = archive.getinfo(SUPPLEMENT)
        if info.file_size > 8 * 1024 * 1024:
            raise ValueError("SUPPLEMENT_SIZE_LIMIT")
        pdf = archive.read(info)
        if not pdf.startswith(b"%PDF-"):
            raise ValueError("SUPPLEMENT_NOT_PDF")
        return pdf, [{"name": i.filename, "uncompressed_bytes": i.file_size,
                      "selected": i.filename == SUPPLEMENT} for i in members]


def pdf_text(raw):
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(raw))
    return [{"page": i + 1, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages)]


def add_pdf_transcription(collector, source, entry, raw):
    pages = pdf_text(raw)
    result = {"source_id": source, "raw_sha256": entry["sha256"], "pages": pages,
              "status": "TEXT_EXTRACTION_NOT_NORMALIZED_DATA",
              "note": "PDF layout requires visual review; no curves digitized and no missing values filled."}
    payload = json_bytes(result)
    digest = hashlib.sha256(payload).hexdigest()
    path = immutable_write(collector.root, f"staging/{source}/{digest}/pdf-text.json", payload)
    return {"transcription_path": path, "transcription_sha256": digest, "pdf_pages": len(pages)}


def collect_supplement(collector):
    source = "stoneware-melt-2018-supplement"
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6317026/fullTextXML"
    raw, final = collector.fetch(url)
    doc, identity = parse_article(raw, "10.3390/ma11122475")
    links = [n.get("{http://www.w3.org/1999/xlink}href") for n in doc.findall(".//supplementary-material/media")]
    if SUPPLEMENT not in links:
        raise ValueError("SUPPLEMENT_LINK_CHANGED")
    save_source_file(collector, source, "parent-article.xml", url, raw, final)
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6317026/supplementaryFiles?inlineImages=false"
    raw, final = collector.fetch(url)
    pdf, members = selected_pdf_from_zip(raw)
    save_source_file(collector, source, "supplementary-bundle.zip", url, raw, final)
    entry = save_source_file(collector, source, SUPPLEMENT, url, pdf, final)
    entry["archive_member"] = SUPPLEMENT
    entry["parent_archive_sha256"] = hashlib.sha256(raw).hexdigest()
    pages = pdf_text(pdf)
    content = " ".join(p["text"] for p in pages)
    if not all(label in content for label in ("Table S1", "Table S2", "Table S3", "Table S4")):
        raise ValueError("SUPPLEMENT_CONTENT_REVIEW_REQUIRED")
    meta = base_metadata(source, "https://doi.org/10.3390/ma11122475", "ARTICLE_SUPPLEMENT",
                         "CC-BY-4.0", "CC_BY_REFERENCE")
    meta.update(identity)
    meta.update({"layer": "OPEN_DATA", "version": "PMC6317026; archive/member hashes pinned",
                 "same_publication_as": "stoneware-melt-2018", "not_a_new_independent_study": True,
                 "license_basis": "Parent JATS CC BY 4.0; explicitly linked supplementary material. Supplement-specific exception review must be recorded separately; retained in research quarantine.",
                 "archive_members": members, "supplement_tables": ["S1", "S2", "S3", "S4"],
                 "access_method": "OFFICIAL_EUROPE_PMC_SUPPLEMENT_API", "scraping_required": False,
                 "scope": "VITREOUS_PHASE_AND_SILICATE_MELT_MODEL_COMPARISONS_NOT_CLAY_GLAZE_WETTING"})
    meta.update(add_pdf_transcription(collector, source, entry, pdf))
    return meta


def validate_zenodo_record(record):
    meta = record.get("metadata", {})
    if record.get("id") != ZENODO_RECORD or meta.get("doi") != f"10.5281/zenodo.{ZENODO_RECORD}":
        raise ValueError("ZENODO_VERSION_CHANGED")
    if meta.get("access_right") != "open" or meta.get("license", {}).get("id") != "cc-by-4.0":
        raise ValueError("ZENODO_RIGHTS_CHANGED")
    files = record.get("files", [])
    if len({f["key"] for f in files}) != len(files):
        raise ValueError("DUPLICATE_FILE_KEY")
    selected = {f["key"]: f for f in files if f["key"] in ZENODO_FILES}
    if set(selected) != set(ZENODO_FILES):
        raise ValueError("ZENODO_SELECTION_CHANGED")
    for key, file in selected.items():
        cap = 20 * 1024 * 1024 if key.endswith(".pdf") else 1024 * 1024
        if type(file["size"]) is not int or not 0 < file["size"] <= cap:
            raise ValueError("ZENODO_FILE_SIZE_LIMIT")
        if file["links"]["self"] != f"https://zenodo.org/api/records/{ZENODO_RECORD}/files/{key}/content":
            raise ValueError("ZENODO_FILE_URL_CHANGED")
    return selected


def checked_zenodo_file(raw, info):
    if len(raw) != info["size"]:
        raise ValueError("UPSTREAM_SIZE_MISMATCH")
    # Zenodo publishes MD5; retain it for transport verification, add SHA-256 locally.
    if "md5:" + hashlib.md5(raw).hexdigest() != info["checksum"]:
        raise ValueError("UPSTREAM_CHECKSUM_MISMATCH")


def collect_wetting(collector):
    source = "zenodo-borosilicate-wetting-2025"
    url = f"https://zenodo.org/api/records/{ZENODO_RECORD}"
    raw, final = collector.fetch(url)
    record = json.loads(raw)
    selected = validate_zenodo_record(record)
    save_source_file(collector, source, "zenodo-record.json", url, raw, final)
    transcription = {}
    for name in ZENODO_FILES:
        info = selected[name]
        raw, final = collector.fetch(info["links"]["self"],
            max_bytes=20 * 1024 * 1024 if name.endswith(".pdf") else 1024 * 1024)
        checked_zenodo_file(raw, info)
        if name.endswith(".pdf"):
            if not raw.startswith(b"%PDF-") or "coatings15080967" not in "".join(p["text"] for p in pdf_text(raw)):
                raise ValueError("WETTING_ARTICLE_IDENTITY_CHANGED")
        entry = save_source_file(collector, source, name, info["links"]["self"], raw, final)
        entry["upstream_checksum"] = info["checksum"]
        if name.endswith(".pdf"):
            transcription = add_pdf_transcription(collector, source, entry, raw)
    meta = base_metadata(source, f"https://zenodo.org/records/{ZENODO_RECORD}",
                         "SELECTED_RESEARCH_DATASET_FILES", "CC-BY-4.0", "CC_BY_ADJACENT_DOMAIN_REFERENCE")
    meta.update({"source_name": record["metadata"]["title"],
                 "source_author": "; ".join(c["name"] for c in record["metadata"]["creators"]),
                 "version": f"10.5281/zenodo.{ZENODO_RECORD}", "concept_doi": "10.5281/zenodo.15837286",
                 "article_doi": "10.3390/coatings15080967", "layer": "OPEN_DATA",
                 "access_method": "VERSION_PINNED_ZENODO_API", "scraping_required": False,
                 "scope": "OXIDE_MELTS_ON_PLATINUM_AND_GRAPHITE_NOT_CLAY_BODY",
                 "numeric_csv_kind": "FTIR_SPECTRA_NOT_CONTACT_ANGLE_CURVES",
                 "omitted_files": [{"filename": f["key"], "bytes": f["size"],
                                    "reason": "FIGURE_ASSET_NOT_REQUIRED_FOR_THIS_BOUNDED_BATCH"}
                                   for f in record["files"] if f["key"] not in selected], **transcription})
    return meta


def verify_transcriptions(root, receipt):
    result = verify_receipt(root, receipt)
    root = Path(root).resolve()
    for source, meta in receipt["sources"].items():
        path = (root / meta["transcription_path"]).resolve()
        if not path.is_relative_to(root) or hashlib.sha256(path.read_bytes()).hexdigest() != meta["transcription_sha256"]:
            raise ValueError("TRANSCRIPTION_INTEGRITY")
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc["raw_sha256"] not in {f["sha256"] for f in receipt["files"] if f["source_id"] == source}:
            raise ValueError("TRANSCRIPTION_LINEAGE")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("storage/research/melt-evidence"))
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.manifest.exists():
        raise ValueError("MANIFEST_ALREADY_EXISTS")
    collector = Collector(args.root)
    sources, failures = {}, {}
    for source, function in (("stoneware-melt-2018-supplement", collect_supplement),
                             ("zenodo-borosilicate-wetting-2025", collect_wetting)):
        try:
            sources[source] = function(collector)
        except Exception as error:
            failures[source] = f"{type(error).__name__}: {error}"
    for entry in collector.entries:
        entry["source_complete"] = entry["source_id"] in sources
    complete = [f for f in collector.entries if f["source_complete"]]
    receipt = {"schema_version": VERSION, "created_at": datetime.now(timezone.utc).isoformat(),
               "sources": sources, "files": collector.entries, "failures": failures,
               "code_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                               (Path(__file__), Path(__file__).with_name("acquire.py"), Path(__file__).with_name("flow_sources.py"))},
               "counts": {"completed_collections": len(sources), "failed_collections": len(failures),
                          "completed_files": len(complete), "completed_file_bytes": sum(f["bytes"] for f in complete)},
               "note": "Collection count is not independent-study count. Bundle contains selected PDF; parent article repeats prior archive. All remain research-only."}
    receipt_path = immutable_write(collector.root, f"receipts/{uuid4()}.json", json_bytes(receipt))
    integrity = verify_transcriptions(collector.root, receipt)
    archive = collector.root
    manifest = {"storage_root": archive.relative_to(Path.cwd()).as_posix() if archive.is_relative_to(Path.cwd()) else str(archive),
                "receipt_path": receipt_path, "integrity_check": integrity, **receipt}
    immutable_write(args.manifest.parent, args.manifest.name, json_bytes(manifest))
    print(json.dumps({"counts": receipt["counts"], "failures": failures, "integrity": integrity}))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
