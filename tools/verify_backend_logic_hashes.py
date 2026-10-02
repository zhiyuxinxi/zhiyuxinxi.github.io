"""Only public GET requests; no deployment or repository mutation."""
import hashlib,json,pathlib,time,urllib.request

BASE='https://zhiyuxinxi.github.io/'
ROOT=pathlib.Path('site')
OUT=ROOT/'qa/backend-logic'
OUT.mkdir(exist_ok=True)
def fetch(path):
    with urllib.request.urlopen(BASE+path+'?logic_verify='+str(int(time.time())),timeout=20) as response:
        assert response.status==200
        return response.read()

expected=(ROOT/'backend-logic-review.js').read_bytes()
for attempt in range(36):
    try:
        if fetch('backend-logic-review.js')==expected:break
    except Exception:pass
    print('Waiting for approved release',attempt+1,flush=True)
    time.sleep(10)
else:raise AssertionError('Approved reader did not reach public root within six minutes')

assets=['index.html','workbench.js','workbench.css','development-review.js','backend-logic-review.js','handoff/backend-logic/manifest.json','handoff/backend-logic/architecture-plan.json','handoff/backend-logic/architecture-plan-validation.json','handoff/backend-logic/cloud-boundaries.json']
hashes={}
for path in assets:
    raw=fetch(path)
    assert raw==(ROOT/path).read_bytes(),path+' differs from approved source'
    hashes[path]=hashlib.sha256(raw).hexdigest()
local=json.loads(fetch('handoff/backend-logic/architecture-plan.json'))
cloud=json.loads(fetch('handoff/backend-logic/cloud-boundaries.json'))
assert [len(local[k]) for k in ['entities','operations','flows','acceptance','pageCoverage']]==[17,11,8,18,29]
assert sum(1 for value in cloud.values() if isinstance(value,list) for item in value if isinstance(item,dict) and 'classification' in item)==121
assert [len(cloud[k]) for k in ['dataClasses','conditionalFlows','errorMatrix','acceptance','historyRepairs']]==[11,7,20,28,13]
assert all(item['execution'].startswith('待执行') for item in local['acceptance']+cloud['acceptance'])
report={'status':'PASS','testedOrigin':BASE,'sourceSHA':'89b64f4b0e9b5cee3c66781b760f6ea85f698b72','assetHashes':hashes,'sourceDataCommit':'fe35cf7aa010d718c967679616bd1a44de71908c','allPlannedAcceptanceStillUnexecuted':46,'cloudClassifiedItems':121}
(OUT/'public-hashes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
