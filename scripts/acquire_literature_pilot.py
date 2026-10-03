"""Three bounded OA-fulltext requests. No corpus training or engine admission."""
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'storage/research/literature-2026-09-27/fulltext-pilot'
DOIS = ['10.3390/ma11122475', '10.3390/ma13081814', '10.3390/ma13225122']


def get(url):
    time.sleep(2)
    with urlopen(Request(url,headers={'User-Agent':'CeramicLabLiterature/0.1'}),timeout=40) as response:
        raw=response.read(8*1024*1024+1)
    if len(raw)>8*1024*1024: raise ValueError('SIZE_LIMIT')
    return raw


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    receipt=[]
    old=json.loads((ROOT/'data/manifests/flow-acquisition-2026-09-21-batch1.json').read_text(encoding='utf-8'))
    for doi in DOIS:
        entry=dict(doi=doi,reading_status='NOT_READ',engine_eligible=False,training_allowed=False)
        try:
            oldfile=next((r for r in old['files'] if r.get('source_id')=='stoneware-melt-2018' and r.get('filename')=='article.xml'),None) if doi==DOIS[0] else None
            if oldfile:
                path=ROOT/old['storage_root']/oldfile['raw_path']
                raw=path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=oldfile['sha256']: raise ValueError('CACHE_HASH_MISMATCH')
                url=oldfile['source_url']
                entry['acquisition']='EXISTING_VERIFIED_ARCHIVE'
            else:
                result=json.loads(get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':'DOI:'+doi,'format':'json'})))
                hits=[r for r in result['resultList']['result'] if r.get('doi','').lower()==doi and r.get('isOpenAccess')=='Y' and r.get('pmcid')]
                if not hits: raise ValueError('NO_OA_FULLTEXT_MATCH')
                url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+hits[0]['pmcid']+'/fullTextXML'
                raw=get(url)
                entry['acquisition']='NEW_API_DOWNLOAD'
            tree=ET.fromstring(raw)
            licenses=tree.findall('.//article-meta/permissions/license')
            links=[n.attrib.get('{http://www.w3.org/1999/xlink}href','') for node in licenses for n in node.iter()]
            allowed={'http://creativecommons.org/licenses/by/4.0/','https://creativecommons.org/licenses/by/4.0/'}
            if not any(link in allowed for link in links): raise ValueError('LICENSE_REVIEW_REQUIRED')
            digest=hashlib.sha256(raw).hexdigest()
            target=OUT/(digest+'.xml')
            if not target.exists(): target.write_bytes(raw)
            body=tree.find('body')
            sections=[]
            if body is not None:
                for sec in body.findall('sec'):
                    sections.append({'heading':''.join(sec.find('title').itertext()) if sec.find('title') is not None else '',
                                     'text':' '.join(sec.itertext())})
            tables=[{'id':t.get('id'), 'text':' '.join(t.itertext())} for t in tree.findall('.//table-wrap')]
            (OUT/(digest+'.sections.json')).write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf-8')
            (OUT/(digest+'.tables.json')).write_text(json.dumps(tables,ensure_ascii=False,indent=2),encoding='utf-8')
            entry.update(status='DOWNLOADED_NOT_READ',source_url=url,sha256=digest,
                         source_license='CC-BY-4.0', license_text=[' '.join(x.itertext()) for x in licenses],
                         retrieval_date=datetime.now(timezone.utc).isoformat(),section_count=len(sections),
                         table_count=len(tables),numeric_data_status='RAW_TABLE_TEXT_NOT_VALIDATED')
        except Exception as error: entry.update(status='NOT_ACQUIRED',error=str(error))
        receipt.append(entry)
        print(json.dumps(entry,ensure_ascii=False),flush=True)
    (OUT/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
