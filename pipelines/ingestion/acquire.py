"""Bounded downloads from reviewed official APIs/exports; never runs upstream code.

Raw objects are content-addressed and immutable. A new receipt records each run.
This archive is NOT the production chemistry reference set or a training corpus.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import time
from urllib.parse import urlparse
from urllib.request import Request, HTTPRedirectHandler, build_opener
from uuid import uuid4
import xml.etree.ElementTree as ET

VERSION = "reviewed-acquisition-v1.3"
MAX_BYTES = 8 * 1024 * 1024
HOSTS = {"archive.ics.uci.edu", "zenodo.org", "data.mendeley.com",
         "www.ebi.ac.uk", "raw.githubusercontent.com", "api.github.com", "www.nist.gov", "tsapps.nist.gov",
         "link.springer.com", "link.springernature.com", "www.iieta.org", "oiccpress.com",
         "prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com"}
KILN_COMMIT = "a2b3071e4e55f47c20326563200da0b49d3c5bb8"
PROFILES = ("cone-05-fast-bisque", "cone-05-long-bisque", "cone-6-long-glaze",
            "test-200-250", "test-fast")
NIST_POLICY = "https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications"


def article_authors(meta):
    authors = []
    for group in meta.findall("contrib-group"):
        for person in group.findall("contrib"):
            if person.get("contrib-type") != "author" and group.get("content-type") != "author":
                continue
            name = person.find("name")
            if name is not None:
                authors.append(" ".join(filter(None, [name.findtext("given-names"), name.findtext("surname")])))
    if not authors:
        raise ValueError("AUTHOR_METADATA_REVIEW_REQUIRED")
    return "; ".join(authors)


def checked_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in HOSTS or parsed.username or parsed.password:
        raise ValueError("UNREVIEWED_DOWNLOAD_HOST: " + str(parsed.hostname))
    return url


class ReviewedRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        checked_url(newurl)  # check before following, not only after receiving data
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Collector:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.entries = []
        self.last_request = 0.0

    def fetch(self, url, *, max_bytes=MAX_BYTES):
        if type(max_bytes) is not int or not 0 < max_bytes <= 32 * 1024 * 1024:
            raise ValueError("INVALID_DOWNLOAD_SIZE_LIMIT")
        checked_url(url)
        time.sleep(max(0, 1.0 - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        request = Request(url, headers={"User-Agent": "CeramicLabResearch/0.1 (bounded public data download)"})
        with build_opener(ReviewedRedirects).open(request, timeout=30) as response:
            checked_url(response.url)
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError("DOWNLOAD_SIZE_LIMIT")
            return raw, response.url

    def save(self, source, filename, url, raw, final_url=None, expected_sha256=None):
        checksum = hashlib.sha256(raw).hexdigest()
        if expected_sha256 and checksum != expected_sha256:
            raise ValueError("UPSTREAM_CHECKSUM_MISMATCH")
        target = self.root / "raw" / "sha256" / checksum
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != checksum:
                raise ValueError("LOCAL_CHECKSUM_MISMATCH")
            reused = True
        else:
            with target.open("xb") as stream:
                stream.write(raw)
            reused = False
        self.entries.append({"source_id": source, "filename": filename, "source_url": url,
                             "resolved_url": final_url or url, "raw_path": target.relative_to(self.root).as_posix(),
                             "sha256": checksum, "bytes": len(raw), "reused": reused,
                             "retrieved_at": datetime.now(timezone.utc).isoformat()})

    def download(self, source, filename, url, expected_sha256=None):
        raw, final = self.fetch(url)
        self.save(source, filename, url, raw, final, expected_sha256)
        return raw

    def collect(self, source):
        if source in ("metakaolin-2024", "feldspar-activation-2023"):
            pmc = {"metakaolin-2024": "PMC10820037", "feldspar-activation-2023": "PMC10779675"}[source]
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
            raw, final = self.fetch(url)
            doc = ET.fromstring(raw)
            meta = doc.find("./front/article-meta")
            permission = meta.find("permissions")
            if permission is None or "creativecommons.org/licenses/by/4.0" not in ET.tostring(permission, encoding="unicode"):
                raise ValueError("LICENSE_CHANGED")
            doi = meta.find("article-id[@pub-id-type='doi']").text
            authors = article_authors(meta)
            title = "".join(meta.find("title-group/article-title").itertext())
            self.save(source, "article.xml", url, raw, final)
            return {"license": "CC-BY-4.0", "license_evidence": "https://doi.org/" + doi,
                    "source_name": title, "source_author": authors,
                    "version": pmc + "; content hash pinned", "entity_kind": "STUDY_SCOPED_RAW_MATERIAL_ANALYSES"}
        if source in ("anorthite-2018", "sanitary-body-2022"):
            from io import BytesIO
            from pypdf import PdfReader
            if source == "anorthite-2018":
                # Journal's public archive; Springer currently redirects to an identity host.
                # Do not follow that identity flow or bypass it.
                url = "https://oiccpress.com/ijic/article/download/4155/1953/2972"
                doi = "10.1007/s40090-018-0137-4"
                authors = "Ali Arastehnodeh; Majid Saghi"
                title = "Using white cement as a source of calcium oxide in Anorthite body"
                evidence = "https://link.springer.com/article/" + doi
            else:
                evidence = "https://www.iieta.org/node/11313"
                policy, policy_final = self.fetch(evidence)
                if b"creativecommons.org/licenses/by/4.0" not in policy or b"10.18280/acsm.460306" not in policy:
                    raise ValueError("ARTICLE_LICENSE_REVIEW_REQUIRED")
                self.save(source, "article-and-license.html", evidence, policy, policy_final)
                url = "https://www.iieta.org/download/file/fid/76842"
                doi = "10.18280/acsm.460306"
                authors = "Khaled Boulaiche; Kamel Boudeghdegh; Sofiane Haddad; Abdelmalek Roula; Hichem Alioui"
                title = "Valorisation of Industrial Soda-Lime Glass Waste and Its Effect on the Rheological Behavior, Physical-Mechanical and Structural Properties of Sanitary Ceramic Vitreous Bodies"
            raw, final = self.fetch(url)
            if not raw.startswith(b"%PDF-"):
                raise ValueError("ARTICLE_NOT_PDF")
            content = "".join(page.extract_text() or "" for page in PdfReader(BytesIO(raw)).pages)
            # Reviewed PDF wraps the license host as 'creativecom-\nmons'.
            # Repair only that textual line wrap for license checking, never data.
            license_text = re.sub(r"creativecom-\s+mons", "creativecommons", content)
            compact = "".join(license_text.replace("\u00ad", "").split())
            if doi not in compact:
                raise ValueError("ARTICLE_IDENTITY_CHANGED")
            if source == "anorthite-2018" and "creativecommons.org/licenses/by/4.0" not in compact:
                raise ValueError("ARTICLE_LICENSE_REVIEW_REQUIRED")
            self.save(source, "article.pdf", url, raw, final)
            return {"license": "CC-BY-4.0", "license_evidence": evidence, "source_name": title,
                    "source_type": "PUBLISHED_ARTICLE_DIRECT_DOWNLOAD",
                    "source_author": authors, "version": "DOI:" + doi + "; content hash pinned",
                    "entity_kind": "STUDY_SCOPED_RAW_MATERIAL_ANALYSES_AND_TESTS"}
        if source == "nist-srm-ceramics":
            # SRM certificates, NOT Standard Reference Data (SRD) compilations.
            policy, final = self.fetch(NIST_POLICY)
            if b"royalty-free basis throughout the world" not in policy or b"Fair Use of Other NIST Data/Works" not in policy:
                raise ValueError("NIST_POLICY_REVIEW_REQUIRED")
            self.save(source, "nist-data-use-policy.html", NIST_POLICY, policy, final)
            for code in ("70b", "97b", "98b", "99b"):
                url = f"https://tsapps.nist.gov/srmext/certificates/{code}.pdf"
                raw, final = self.fetch(url)
                if not raw.startswith(b"%PDF-"):
                    raise ValueError("NIST_CERTIFICATE_NOT_PDF")
                self.save(source, f"SRM-{code}.pdf", url, raw, final)
            return {"license": "LicenseRef-NIST-NonSRD-Data-Use", "license_evidence": NIST_POLICY,
                    "source_author": "National Institute of Standards and Technology / National Bureau of Standards",
                    "source_name": "NIST ceramic SRM certificates", "source_url": "https://www.nist.gov/srm",
                    "version": "Certificate revisions and content hashes; retrieved 2026-09-20",
                    "entity_kind": "ELEMENTAL_REFERENCE_MATERIAL_CERTIFICATES",
                    "license_conditions": "NIST non-SRD data terms: attribution, retention of notice, identification of modifications. No endorsement or certification of this platform. Not a blanket license for SRD or third-party works."}
        if source == "uci-583":
            url = "https://archive.ics.uci.edu/static/public/583/chemical%2Bcomposition%2Bof%2Bceramic%2Bsamples.zip"
            self.download(source, "ceramic-samples.zip", url)
            return {"license": "CC-BY-4.0", "license_evidence": "https://archive.ics.uci.edu/dataset/583/chemical+composition+of+ceramic+samples",
                    "source_author": "UCI dataset deposit; contributor not listed on reviewed page", "version": "DOI:10.24432/C54P5X; content hash pinned",
                    "entity_kind": "FIRED_SAMPLE_COMPOSITION"}
        if source == "zenodo-14742972":
            url = "https://zenodo.org/api/records/14742972"
            raw, final = self.fetch(url)
            data = json.loads(raw)
            if data["metadata"]["license"]["id"] != "cc-by-4.0":
                raise ValueError("LICENSE_CHANGED")
            self.save(source, "metadata.json", url, raw, final)
            for file in data["files"]:
                if file["key"].endswith(".xlsx") and file["size"] < 1_000_000:
                    self.download(source, file["key"], file["links"]["self"])
            return {"license": "CC-BY-4.0", "license_evidence": url, "source_author": "Jelena Živković",
                    "version": "14742972-v1", "entity_kind": "ARCHAEOLOGICAL_BODY_GLAZE_TABLES"}
        if source == "mendeley-p49ncrb39k":
            url = "https://data.mendeley.com/public-api/datasets/p49ncrb39k"
            raw, final = self.fetch(url)
            data = json.loads(raw)
            if data["version"] != 2 or data["data_licence"]["short_name"] != "CC BY 4.0":
                raise ValueError("SOURCE_VERSION_OR_LICENSE_CHANGED")
            self.save(source, "metadata.json", url, raw, final)
            for file in data["files"]:
                if file["filename"].endswith(".csv") or file["filename"] == "README.md":
                    detail = file["content_details"]
                    self.download(source, file["filename"], detail["download_url"], detail["sha256_hash"])
            return {"license": "CC-BY-4.0", "license_evidence": url, "source_author": "Wenpeng Xu",
                    "version": "DOI:10.17632/p49ncrb39k.2", "entity_kind": "PASTE_GLAZE_ELEMENTAL_MEASUREMENTS_AND_SUMMARIES"}
        if source == "fabris-2024":
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11721402/fullTextXML"
            raw, final = self.fetch(url)
            doc = ET.fromstring(raw)
            permission = ET.tostring(doc.find("./front/article-meta/permissions"), encoding="unicode")
            if "creativecommons.org/licenses/by/4.0" not in permission:
                raise ValueError("LICENSE_CHANGED")
            self.save(source, "article.xml", url, raw, final)
            return {"license": "CC-BY-4.0", "license_evidence": "https://doi.org/10.3390/ma18010060",
                    "source_author": "Riccardo Fabris, Giulia Masi, Denia Mazzini, Leonardo Sanseverino, Maria Chiara Bignozzi",
                    "version": "PMC11721402; content hash pinned", "entity_kind": "PUBLISHED_MATERIALS_RECIPES_TEST_RESULTS"}
        if source == "kiln-controller":
            base = f"https://raw.githubusercontent.com/jbruce12000/kiln-controller/{KILN_COMMIT}/"
            raw, final = self.fetch(base + "README.md")
            if b"either version 3 of the License" not in raw:
                raise ValueError("LICENSE_CHANGED")
            self.save(source, "README.md", base + "README.md", raw, final)
            self.download(source, "config.py.txt", base + "config.py")  # retain as text, never execute
            for name in PROFILES:
                self.download(source, name + ".json", base + "storage/profiles/" + name + ".json")
            return {"license": "GPL-3.0-or-later", "license_evidence": base + "README.md",
                    "source_author": "Jason Bruce and kiln-controller contributors; origin picoReflow",
                    "version": KILN_COMMIT, "entity_kind": "UNVALIDATED_SCHEDULE_EXAMPLES"}
        raise ValueError("UNKNOWN_SOURCE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--sources", nargs="+", choices=("uci-583", "zenodo-14742972", "mendeley-p49ncrb39k", "fabris-2024", "kiln-controller", "nist-srm-ceramics", "metakaolin-2024", "feldspar-activation-2023", "anorthite-2018", "sanitary-body-2022"), required=True)
    args = parser.parse_args()
    collector = Collector(args.storage)
    sources, failures = {}, {}
    for source in dict.fromkeys(args.sources):
        try:
            info = collector.collect(source)
            info.update(source_id=source, source_name=info.get("source_name", source), source_url=info.get("source_url", info["license_evidence"]),
                        source_license=info["license"], source_type=info.get("source_type", "OFFICIAL_EXPORT_OR_API"),
                        retrieval_date=datetime.now(timezone.utc).date().isoformat(),
                        commercial_use_allowed="ALLOWED", attribution_required="REQUIRED",
                        share_alike_required="REQUIRED" if source == "kiln-controller" else "NOT_REQUIRED",
                        license_conditions=info.get("license_conditions", "Retain attribution/license and comply with any applicable third-party and copyleft obligations."),
                        layer="OPEN_DATA", rights_partition="COPYLEFT_REFERENCE" if source == "kiln-controller" else ("NIST_NON_SRD_REFERENCE" if source == "nist-srm-ceramics" else "CC_BY_REFERENCE"),
                        product_release="NOT_APPROVED", training="NOT_ENABLED", core_engine_eligible=False)
            sources[source] = info
            print(json.dumps({"source": source, "state": "ARCHIVED_REFERENCE_ONLY"}), flush=True)
        except Exception as exc:
            failures[source] = type(exc).__name__ + ": " + str(exc)
            print(json.dumps({"source": source, "state": "FAILED", "error": failures[source]}), flush=True)
    receipt = {"schema_version": VERSION, "collector_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "created_at": datetime.now(timezone.utc).isoformat(),
               "sources": sources, "files": collector.entries, "failures": failures,
               "note": "Raw archive only. Failed/partial sources are not releases. No upstream script executed."}
    folder = collector.root / "receipts"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (uuid4().hex + ".json")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
    print(json.dumps({"receipt": str(path), "files": len(collector.entries), "failures": len(failures)}))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
