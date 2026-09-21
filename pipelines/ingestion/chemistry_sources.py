"""Archive selected pinned open-source references, never execute them.

Uses the existing bounded official-export collector. No recipe/photo scraping.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from .acquire import Collector

SOURCES = (
    {"id": "periodictable", "repository": "python-periodictable/periodictable",
     "commit": "182ef63a9ec118ef725aae5bb81860f4ba0fb573",
     "license": "LicenseRef-Public-Domain-with-file-specific-notices", "author": "Paul Kienzle and contributors",
     "license_file": "LICENSE.txt", "marker": "Periodictable is in the public domain.",
     "share_alike": False, "integration": "PINNED_PACKAGE_ADAPTER",
     "files": ["LICENSE.txt", "README.rst", "periodictable/mass.py", "periodictable/formulas.py", "test/test_mass.py", "test/test_formulas.py"]},
    {"id": "openglaze", "repository": "KyaniteLabs/openglaze",
     "commit": "ba43d84925bc83610fcf8be0b5fafee27e77210c",
     "license": "MIT", "author": "OpenGlaze Contributors",
     "license_file": "LICENSE", "marker": "MIT License", "share_alike": False,
     "integration": "CODE_REVIEW_ONLY_NO_UPSTREAM_MATERIAL_DATA",
     "files": ["LICENSE", "README.md", "core/chemistry/umf.py", "core/chemistry/batch.py", "core/chemistry/optimizer.py"]},
    {"id": "glasspy", "repository": "drcassar/glasspy",
     "commit": "ddc06240152749d14d01e0c4f7cec9e4e79c706d",
     "license": "GPL-3.0; bundled data have separate terms", "author": "Daniel R. Cassar and contributors",
     "license_file": "LICENSE", "marker": "GlassPy is licensed under the GNU General Public Licence version 3.",
     "share_alike": True, "integration": "RESEARCH_ARCHIVE_ONLY",
     "files": ["LICENSE", "README.md", "glasspy/viscosity/equilibrium.py", "glasspy/viscosity/equilibrium_log.py"]},
)


def acquire(root):
    root = Path(root).resolve()
    collector = Collector(root)
    sources = []
    for source in SOURCES:
        prefix = f"https://raw.githubusercontent.com/{source['repository']}/{source['commit']}/"
        license_raw, license_final = collector.fetch(prefix + source["license_file"])
        if source["marker"] not in license_raw.decode("utf-8"):
            raise ValueError("LICENSE_REVIEW_REQUIRED")
        for filename in source["files"]:
            raw, final = ((license_raw, license_final) if filename == source["license_file"]
                          else collector.fetch(prefix + filename))
            collector.save(source["id"], filename, prefix + filename, raw, final)
            path = root / "by_source" / source["id"] / source["commit"] / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_bytes() != raw:
                raise ValueError("IMMUTABLE_SOURCE_CONFLICT")
            if not path.exists():
                with path.open("xb") as stream:
                    stream.write(raw)
            collector.entries[-1]["readable_path"] = path.relative_to(root).as_posix()
        sources.append({"source_name": source["repository"], "source_id": source["id"],
                        "source_url": "https://github.com/" + source["repository"],
                        "source_type": "PINNED_SOURCE_SELECTION", "source_author": source["author"],
                        "source_license": source["license"], "license_evidence": prefix + source["license_file"],
                        "commercial_use_allowed": "ALLOWED_WITH_LICENSE_CONDITIONS",
                        "attribution_required": True, "share_alike_required": source["share_alike"],
                        "retrieval_date": datetime.now(timezone.utc).isoformat(), "commit": source["commit"],
                        "integration": source["integration"], "dataset_training_allowed": "NOT_REVIEWED",
                        "rights_scope": "Selected files only; licenses and third-party notices preserved; no blanket permission for external datasets"})
    return {"schema_version": "chemistry-source-selection-v1", "sources": sources,
            "files": collector.entries, "source_count": len(sources), "file_count": len(collector.entries),
            "bytes": sum(x["bytes"] for x in collector.entries),
            "method": "Official GitHub raw export, pinned commit; one request/second; 8 MiB/file cap; no execution",
            "production_material_analyses_added": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("storage/chemistry/01_sources"))
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.manifest.exists():
        parser.error("Choose a new manifest path; existing receipt will not be overwritten")
    result = acquire(args.root)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({key: result[key] for key in ("source_count", "file_count", "bytes")}))
