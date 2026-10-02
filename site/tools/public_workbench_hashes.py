"""Read-only comparison of published runtime bytes to the independently approved source."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/'public-complete-workbench';OUT.mkdir(parents=True,exist_ok=True)
SOURCE='481e89aa67620c04c6a990bfb70509db587bffe1';BASE='https://zhiyuxinxi.github.io/'
FILES=['index.html','workbench.js','workbench-data.js','workbench.css','handoff/routes.json','handoff/workbench-map.json','prototype/index.html','prototype/experience-v4.js','prototype/assessment-preview.js','prototype/experience-v2.js','prototype/experience-v3.js','prototype/ambient.js','prototype/product.css','prototype/themes-v4.css','prototype/themes-v4.js','prototype/app.js','prototype/flows-v2.js','prototype/views.js','prototype/assets/zhiyu-logo.png','prototype/assets/original-person-1.webp']
rows=[]
with sync_playwright() as w:
 ctx=w.request.new_context()
 for name in FILES:
  expected=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
  for attempt in range(8):
   r=ctx.get(BASE+name+'?release_check='+SOURCE+'-'+str(attempt),timeout=30000);actual=hashlib.sha256(r.body()).hexdigest()
   if r.ok and actual==expected:break
   time.sleep(15)
  rows.append({'file':name,'expectedSHA256':expected,'publicSHA256':actual,'httpStatus':r.status,'passed':r.ok and actual==expected})
 ctx.dispose()
report={'sourceCommit':SOURCE,'publicOrigin':BASE,'checkedAt':datetime.now(timezone.utc).isoformat(),'passed':all(x['passed'] for x in rows),'files':rows}
(OUT/'resource-hashes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
