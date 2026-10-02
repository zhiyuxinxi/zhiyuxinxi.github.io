"""Build public, lazily loaded review documents from the independently audited ZIP."""
import hashlib,json,pathlib,sys,zipfile,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED='dfc65d26f350967ec9cd3bf6e855ecae855d058ea1141c71f1d1096dad77f2ac'
SOURCE='5f2d14e153ed166c015de363fbfcbade2706f748'
def digest(b):return hashlib.sha256(b).hexdigest()
def build(path):
 raw=pathlib.Path(path).read_bytes();assert digest(raw)==EXPECTED
 with zipfile.ZipFile(path) as z:
  assert set(z.namelist())=={'source-history-public.json','source-history-public.md','source-history-public.manifest.json','page-contracts.json','page-contracts.md','validation.json'}
  hb=z.read('source-history-public.json');pb=z.read('page-contracts.json')
  assert digest(hb)=='b91650021a6872f2452760d67597bd007e4a4d1fd2ba4610d49c6d3c7bfa40a5'
  assert digest(pb)=='19cddc67a193854b9b93eaadc8c7db049b5378a4951b412d7ee5962e2d1e6c97'
  h=json.loads(hb);p=json.loads(pb);validation=json.loads(z.read('validation.json'))
 out=ROOT/'handoff/development';out.mkdir(exist_ok=True)
 files={}
 def write(name,data):
  dest=out/name;dest.parent.mkdir(exist_ok=True);b=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode();dest.write_bytes(b);files[name]={'bytes':len(b),'sha256':digest(b)}
 def text(v):
  if isinstance(v,dict):return ' '.join(text(x) for x in v.values())
  if isinstance(v,list):return ' '.join(text(x) for x in v)
  return '' if v is None else str(v)
 pages=[]
 for page in p['pages']:
  id=page['id'];assert re.fullmatch('[a-z0-9-]+',id)
  write('pages/'+id+'.json',page)
  pages.append({k:page[k] for k in ['id','route','name','businessSpine','implementationBoundary']})
 write('shared.json',{'sharedContracts':p['sharedContracts'],'entityCatalog':p['entityCatalog']})
 records=[]
 for kind,key in [('mobile','mobileMappings'),('backend','backendMappings')]:
  for item in h[key]:
   id=item['originalId'];assert re.fullmatch('[a-z0-9-]+',id)
   actions=[a for a in h['actionMappings'] if a['originalPageId']==id] if kind=='mobile' else item['actions']
   write('history/'+kind+'-'+id+'.json',{'item':item,'actions':actions})
   records.append({'id':id,'name':item['originalName'],'kind':kind,'disposition':item['disposition'],'valueDecision':item.get('valueDecision'),'valueReason':item.get('valueReason',''),'destinations':item.get('currentDestinations',[]),'domains':item.get('currentDomainIds',[]),'actionCount':len(actions),'gap':any(g['originalId']==id for g in h['meaningfulRepairs']),'search':text([item,actions]).lower()})
 write('history-index.json',{'records':records})
 write('source-summary.json',{'sourceBranch':'design/zhiyu-audit-data','sourceCommit':SOURCE,'zipSha256':EXPECTED,'historySha256':digest(hb),'pageContractsSha256':digest(pb),'pageMeta':p['meta'],'history':{k:v for k,v in h.items() if k not in ['mobileMappings','actionMappings','backendMappings']},'validation':validation})
 write('index.json',{'sourceCommit':SOURCE,'pages':pages,'counts':{'routes':len(p['pages']),'buttonGroups':sum(len(x['buttons']) for x in p['pages']),'representativeStates':p['meta']['counts']['renderedVariants'],'mobileResponsibilities':len(h['mobileMappings']),'mobileActions':len(h['actionMappings']),'backendDomains':len(h['backendMappings']),'backendActions':sum(len(x['actions']) for x in h['backendMappings']),'meaningfulGaps':len(h['meaningfulRepairs'])}})
 # Public-safe data only; no original ZIP, full private evidence, or duplicate markdown.
 write('manifest.json',{'sourceCommit':SOURCE,'zipSha256':EXPECTED,'files':files.copy()})
 print(json.dumps({'files':len(files),'bytes':sum(x['bytes'] for x in files.values())}))
if __name__=='__main__':build(sys.argv[1])
