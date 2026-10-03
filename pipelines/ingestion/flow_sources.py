"""Bounded research archive for melt/flow references; never imports upstream code.

Separate from production materials and ML data. Run with python -m
pipelines.ingestion.flow_sources --root storage/research/flow.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4
import xml.etree.ElementTree as ET

from .acquire import Collector, article_authors

VERSION = "flow-references-v1"
GLASSPY_COMMIT = "ddc06240152749d14d01e0c4f7cec9e4e79c706d"
ARTICLES = {
    "stoneware-melt-2018": ("PMC6317026", "10.3390/ma11122475"),
    "luster-body-2026": ("PMC13514902", "10.3390/ma19163405"),
}
GLASSPY_FILES = (
    "LICENSE", "README.md", "CITATION.cff", "pyproject.toml",
    "glasspy/viscosity/equilibrium.py", "glasspy/viscosity/equilibrium_log.py",
    "glasspy/viscosity/diffusion.py", "glasspy/data/load.py",
)


def text_of(element):
    return "" if element is None else "".join(element.itertext())


def parse_article(raw, expected_doi):
    """Accept only the reviewed identity and unambiguous CC BY 4.0 declaration."""
    doc = ET.fromstring(raw)
    meta = doc.find("./front/article-meta")
    if meta is None or meta.findtext("article-id[@pub-id-type='doi']") != expected_doi:
        raise ValueError("ARTICLE_IDENTITY_CHANGED")
    permissions = meta.find("permissions")
    if permissions is None:
        raise ValueError("LICENSE_REVIEW_REQUIRED")
    links = set()
    for node in permissions.iter():
        links.update(v.strip() for v in node.attrib.values() if v.startswith(("http://", "https://")))
        if node.tag.rsplit("}", 1)[-1] == "license_ref" and node.text:
            links.add(node.text.strip())
    cc = {urlparse(v).path.rstrip("/") for v in links
          if urlparse(v).scheme in ("https", "http") and urlparse(v).hostname == "creativecommons.org"}
    if cc != {"/licenses/by/4.0"}:
        raise ValueError("LICENSE_REVIEW_REQUIRED")
    title = text_of(meta.find("title-group/article-title"))
    if not title:
        raise ValueError("MISSING_TITLE")
    return doc, {"source_name": title, "source_author": article_authors(meta),
                 "doi": expected_doi, "license_urls": sorted(links),
                 "permissions_xml": ET.tostring(permissions, encoding="unicode")}


def table_index(doc):
    """Preserve strings, markup and spans. No numeric inference or zero filling."""
    result = []
    for ordinal, table in enumerate(doc.findall(".//table-wrap"), 1):
        result.append({
            "ordinal": ordinal, "table_id": table.get("id"),
            "label": text_of(table.find("label")),
            "caption": text_of(table.find("caption")),
            "footnotes": text_of(table.find("table-wrap-foot")),
            "rows": [[{"tag": cell.tag, "text": text_of(cell),
                       "rowspan": cell.get("rowspan", "1"),
                       "colspan": cell.get("colspan", "1"),
                       "xml": ET.tostring(cell, encoding="unicode")}
                      for cell in row if cell.tag in ("th", "td")]
                     for row in table.findall(".//tr")],
            "table_xml": ET.tostring(table, encoding="unicode"),
            "scientific_status": "UNREVIEWED_TABLE_TRANSCRIPTION",
            "core_engine_eligible": False,
        })
    return result


def immutable_write(root, relative, raw):
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root) or target == root:
        raise ValueError("PATH_OUTSIDE_ARCHIVE")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() != raw:
            raise ValueError("IMMUTABLE_CONTENT_MISMATCH")
    else:
        with target.open("xb") as stream:
            stream.write(raw)
    return target.relative_to(root).as_posix()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def verify_receipt(root, receipt):
    """Offline integrity check, including readable copies and table-index lineage."""
    root = Path(root).resolve()
    def check(relative, expected):
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("PATH_OUTSIDE_ARCHIVE")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("ARCHIVE_CHECKSUM_MISMATCH")
    identities = set()
    for entry in receipt["files"]:
        key = (entry["source_id"], entry["filename"])
        if key in identities:
            raise ValueError("DUPLICATE_SOURCE_FILE")
        identities.add(key)
        check(entry["raw_path"], entry["sha256"])
        check(entry["readable_path"], entry["sha256"])
        if entry["source_complete"] != (entry["source_id"] in receipt["sources"]):
            raise ValueError("SOURCE_COMPLETENESS_MISMATCH")
    for source, meta in receipt["sources"].items():
        if meta["core_engine_eligible"] or meta["training"] != "NOT_ENABLED":
            raise ValueError("RESEARCH_BOUNDARY_VIOLATION")
        if "profile_path" in meta:
            check(meta["profile_path"], meta["profile_sha256"])
            profile = json.loads((root / meta["profile_path"]).read_text(encoding="utf-8"))
            hashes = {f["sha256"] for f in receipt["files"] if f["source_id"] == source}
            if profile["raw_sha256"] not in hashes:
                raise ValueError("PROFILE_LINEAGE_MISMATCH")
    return {"verified_source_files": len(identities), "verified_sources": len(receipt["sources"])}


def save_source_file(collector, source, filename, url, raw, final):
    collector.save(source, filename, url, raw, final)
    entry = collector.entries[-1]
    # A human-readable copy, preserving the original bytes; hash prevents overwrite.
    relative = f"by_source/{source}/{entry['sha256']}/{filename}"
    entry["readable_path"] = immutable_write(collector.root, relative, raw)
    return entry


def base_metadata(source, url, kind, license_name, partition):
    return {"source_id": source, "source_url": url, "source_type": kind,
            "source_license": license_name, "rights_partition": partition,
            "retrieval_date": datetime.now(timezone.utc).isoformat(),
            "commercial_use_allowed": "ALLOWED", "attribution_required": "REQUIRED",
            "share_alike_required": "NOT_REQUIRED" if license_name == "CC-BY-4.0" else "CONDITIONAL",
            "rights_note": "Subject to the archived license; not a product release clearance.",
            "training": "NOT_ENABLED", "product_release": "NOT_APPROVED",
            "scientific_status": "RESEARCH_QUARANTINE", "core_engine_eligible": False}


def collect_article(collector, source):
    pmc, doi = ARTICLES[source]
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
    raw, final = collector.fetch(url)
    doc, identity = parse_article(raw, doi)
    entry = save_source_file(collector, source, "article.xml", url, raw, final)
    tables = table_index(doc)
    profile = {"schema_version": VERSION, "source_id": source,
               "raw_sha256": entry["sha256"], "source_license": "CC-BY-4.0",
               "source_url": "https://doi.org/" + doi, **identity,
               "table_count": len(tables), "tables": tables,
               "note": "Structural transcription only. Rows are not independent experiments. No units, values or evidence kinds normalized."}
    derived = json_bytes(profile)
    profile_path = immutable_write(collector.root,
        f"staging/{source}/{hashlib.sha256(derived).hexdigest()}/table-index.json", derived)
    meta = base_metadata(source, "https://doi.org/" + doi,
                         "OPEN_ACCESS_ARTICLE_JATS", "CC-BY-4.0", "CC_BY_REFERENCE")
    meta.update(identity)
    meta.update({"version": pmc + "; raw hash pinned", "layer": "OPEN_DATA",
                 "table_count": len(tables), "profile_path": profile_path,
                 "profile_sha256": hashlib.sha256(derived).hexdigest(),
                 "access_method": "OFFICIAL_EUROPE_PMC_API", "scraping_required": False,
                 "evidence_review": "MIXED_REPORTED_AND_MODELLED_PROPERTIES_REQUIRE_FIELD_REVIEW"})
    return meta


def collect_glasspy(collector):
    source = "glasspy-model-reference"
    base = f"https://raw.githubusercontent.com/drcassar/glasspy/{GLASSPY_COMMIT}/"
    raw, final = collector.fetch(base + "LICENSE")
    if b"GlassPy is licensed under the GNU General Public Licence version 3" not in raw:
        raise ValueError("GLASSPY_LICENSE_CHANGED")
    save_source_file(collector, source, "LICENSE", base + "LICENSE", raw, final)
    for filename in GLASSPY_FILES[1:]:
        raw, final = collector.fetch(base + filename)
        save_source_file(collector, source, filename, base + filename, raw, final)
    meta = base_metadata(source, "https://github.com/drcassar/glasspy",
                         "SELECTED_SOURCE_CODE_REFERENCE", "GPL-3.0 (see archived notices)", "COPYLEFT_CODE_REFERENCE")
    meta.update({"source_name": "GlassPy: selected viscosity and data-loader references",
                 "source_author": "Daniel R. Cassar and GlassPy contributors; see CITATION.cff and file notices",
                 "version": GLASSPY_COMMIT, "layer": "OPEN_DATA",
                 "access_method": "COMMIT_PINNED_OFFICIAL_REPOSITORY_FILES", "scraping_required": False,
                 "code_executed": False, "installed": False,
                 "datasets_downloaded": False, "model_weights_downloaded": False,
                 "mixed_license_warning": "Code rights do not license databases or model weights. LICENSE labels SciGlass ODbL but embeds MIT-like text: verify original data release independently before acquisition.",
                 "evidence_review": "EQUATIONS_AND_IMPLEMENTATION_REFERENCE_NOT_EXPERIMENTAL_DATA"})
    return meta


def run(root, sources):
    collector = Collector(root)
    metadata, failures = {}, {}
    for source in sources:
        try:
            if source in ARTICLES:
                metadata[source] = collect_article(collector, source)
            elif source == "glasspy-model-reference":
                metadata[source] = collect_glasspy(collector)
            else:
                raise ValueError("UNREVIEWED_SOURCE")
        except Exception as error:
            failures[source] = f"{type(error).__name__}: {error}"
    for entry in collector.entries:
        entry["source_complete"] = entry["source_id"] in metadata
    complete = [e for e in collector.entries if e["source_complete"]]
    receipt = {"schema_version": VERSION, "created_at": datetime.now(timezone.utc).isoformat(),
               "collector_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "transport_code_sha256": hashlib.sha256(Path(__file__).with_name("acquire.py").read_bytes()).hexdigest(),
               "sources": metadata, "files": collector.entries, "failures": failures,
               "counts": {"completed_sources": len(metadata), "failed_sources": len(failures),
                          "completed_source_files": len(complete),
                          "completed_source_bytes": sum(e["bytes"] for e in complete),
                          "article_tables": sum(m.get("table_count", 0) for m in metadata.values())},
               "note": "This is one acquisition run, not a cumulative inventory. Quarantine only; no new validated engine inputs."}
    path = immutable_write(collector.root, f"receipts/{uuid4()}.json", json_bytes(receipt))
    return path, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("storage/research/flow"))
    parser.add_argument("--manifest", type=Path, help="New, non-overwriting reviewed acquisition manifest")
    parser.add_argument("--sources", nargs="+", choices=[*ARTICLES, "glasspy-model-reference"],
                        default=[*ARTICLES, "glasspy-model-reference"])
    args = parser.parse_args()
    path, receipt = run(args.root, list(dict.fromkeys(args.sources)))
    integrity = verify_receipt(args.root, receipt)
    if args.manifest:
        archive = args.root.resolve()
        storage_root = archive.relative_to(Path.cwd()).as_posix() if archive.is_relative_to(Path.cwd()) else str(archive)
        manifest = {"storage_root": storage_root, "receipt_path": path,
                    "integrity_check": integrity, **receipt}
        immutable_write(args.manifest.parent, args.manifest.name, json_bytes(manifest))
    print(json.dumps({"receipt": path, "counts": receipt["counts"], "integrity": integrity,
                      "failures": receipt["failures"]}, ensure_ascii=False))
    raise SystemExit(1 if receipt["failures"] else 0)


if __name__ == "__main__":
    main()
