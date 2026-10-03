"""Download an explicit, licensed source selection; no crawl and no execution.

Keeps original bytes and creates human-readable, checksum-verified copies.
Engine source is not a ceramic material dataset. See docs/simulation/01_ENGINE_SELECTION.md.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from .acquire import Collector


SOURCES = (
    {"id":"scikit-fem", "repository":"kinnala/scikit-fem", "commit":"a9c43abbc3b17c36a059132c9f571447b755920e", "version":"12.0.2", "license":"BSD-3-Clause", "author":"scikit-fem developers", "license_file":"LICENSE", "license_marker":"Redistribution and use in source and binary forms", "files":["LICENSE","README.md","docs/examples/ex11.py","docs/examples/ex19.py"]},
    {"id":"nvidia-warp", "repository":"NVIDIA/warp", "commit":"f4c57f26f1e3936a89afd283e39fcabf6d548dc7", "version":"v1.17.0", "license":"Apache-2.0", "author":"NVIDIA CORPORATION & AFFILIATES", "license_file":"LICENSE.md", "license_marker":"Apache License", "files":["LICENSE.md","README.md","warp/examples/fem/example_diffusion_3d.py","warp/examples/fem/example_diffusion.py"]},
)


def acquire(root):
    root = Path(root)
    collector = Collector(root)
    sources = []
    for source in SOURCES:
        prefix = f"https://raw.githubusercontent.com/{source['repository']}/{source['commit']}/"
        license_bytes, final = collector.fetch(prefix + source["license_file"])
        if source["license_marker"] not in license_bytes.decode("utf-8"):
            raise ValueError("LICENSE_REVIEW_REQUIRED")
        for name in source["files"]:
            raw, resolved = (license_bytes, final) if name == source["license_file"] else collector.fetch(prefix + name)
            collector.save(source["id"], name, prefix + name, raw, resolved)
            readable = root / "by_source" / source["id"] / source["commit"] / name
            readable.parent.mkdir(parents=True, exist_ok=True)
            if readable.exists() and readable.read_bytes() != raw:
                raise ValueError("IMMUTABLE_SOURCE_CONFLICT")
            if not readable.exists():
                readable.write_bytes(raw)
            collector.entries[-1]["readable_path"] = readable.relative_to(root).as_posix()
        sources.append({"source_id":source["id"], "source_name":source["repository"], "source_url":"https://github.com/"+source["repository"],
            "source_type":"PINNED_OPEN_SOURCE_CODE_SELECTION", "source_author":source["author"], "source_license":source["license"],
            "license_evidence":prefix+source["license_file"], "commercial_use_allowed":"ALLOWED_WITH_LICENSE_CONDITIONS", "attribution_required":True, "share_alike_required":False,
            "version":source["version"], "commit":source["commit"], "rights_scope":"Selected source files only; dependencies, patents and third-party datasets retain separate rights", "material_reference_data":False})
    return {"schema_version":"simulation-source-archive-v1", "retrieval_date":datetime.now(timezone.utc).isoformat(),
        "source_count":len(sources), "file_count":len(collector.entries), "bytes":sum(e["bytes"] for e in collector.entries),
        "sources":sources, "files":collector.entries, "access_method":"Direct official GitHub raw exports at pinned commits; one request/second; 8 MiB/file limit; no site scraping; no upstream code executed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("storage/simulation/01_sources"))
    parser.add_argument("--manifest",type=Path,required=True)
    args = parser.parse_args()
    if args.manifest.exists():
        parser.error("Manifest exists; choose a new receipt path")
    result = acquire(args.root)
    args.manifest.parent.mkdir(parents=True,exist_ok=True)
    args.manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("source_count","file_count","bytes")},indent=2))
