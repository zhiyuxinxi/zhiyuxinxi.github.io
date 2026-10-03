"""Current product structure browser regression. Synthetic local records only; no real services or publication.
Run with site root and optional evidence directory; historical test reports do not substitute for this check.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,re,time,os,sys
R=Path(sys.argv[1] if len(sys.argv)>1 else 'site').resolve();O=Path(sys.argv[2] if len(sys.argv)>2 else str(R/'qa/product-structure')).resolve();(O/'screenshots').mkdir(parents=True,exist_ok=True)
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(R)));Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_port}'
results=[];errors=[];matrix=[];copy=[]
def check(v,m):
 if not v:raise AssertionError(m)
def test(n,fn):
 try:result=fn();results.append(dict(test=n,status='PASS',details=result))
 except Exception as e:results.append(dict(test=n,status='FAIL',error=str(e)))
 print(n,results[-1]['status'],results[-1].get('error',''),flush=True)
with sync_playwright() as w:
 b=w.chromium.launch(**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}),args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');p=ctx.new_page();p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)))
 def go(route,reset=False,theme='sunrise'):
  p.goto(url+'/prototype/index.html?scenario=current-product-check&theme='+theme+('&reset=1' if reset else '')+'#'+route);p.wait_for_function('window.App && document.querySelector("main")');
 def nav(route):
  p.evaluate('r=>location.hash=r',route);p.wait_for_function('r=>decodeURIComponent(App.currentRoute)===decodeURIComponent(r)',arg=route)
 go('home',True)
 scenes=p.evaluate('DecisionScenes.items.map(x=>x.id)');themes=p.evaluate('D.themes.map(x=>x.id)');routes=p.evaluate('Object.keys(Views.map)')
 manifest=json.loads((R/'handoff/routes.json').read_text());params={x['route'].split('?')[0]:x['route'] for x in manifest if x.get('route')};params.update({'topic':'topic?id=exam-retake','topic-workspace':'topic-workspace?topic=exam-retake','factor-detail':'factor-detail?id=A','relationship-detail':'relationship-detail?id=D1','observation-area':'observation-area?id=values'})
 def mapping():
  check(len(routes)==43,str(len(routes)));check(set(routes)==set(params),str(set(routes)^set(params)));check(len({x['id'] for x in manifest})==97,'node IDs');return {'routes':43,'nodes':97,'themes':len(themes)}
 test('route-theme-catalog',mapping)
 def home():
  check(p.locator('.home-assessment').count()==1,'one container');check(p.locator('.home-assessment-start').count()==1,'one CTA');p.locator('[data-action=mode][data-id=ai]').focus();p.keyboard.press('Enter');check(p.locator('.home-assessment-start').get_attribute('data-route')=='ai-reset','AI CTA');p.locator('[data-action=mode][data-id=original]').click();p.locator('.home-assessment-start').click();check('暂时无法开始测评' in p.locator('main').inner_text(),'honest unavailable');check(p.evaluate('App.snapshot.sessions.length')==0,'fake session');return {'singleCTA':True,'keyboardSelection':True,'noFakeSession':True}
 test('home-mode-and-unavailable',home)
 def topics():
  outputs=[]
  for scene in scenes:
   nav('topic-workspace?topic='+scene);check(p.locator('textarea').count()==4,'four inputs '+scene)
   for field in ['facts','priorities','concerns','unknown']:p.locator('#topic-'+field).fill(scene+'：'+field+'，保留我自己的条件。')
   p.locator('[data-action=topic-save]').click();n=p.evaluate('App.snapshot.observations.at(-1)');check(n['topicId']==scene,'topicID');check(n['fields']['facts'].startswith(scene),'specific fields')
   nav('topic-workspace?topic='+scene+'&id='+n['id']);p.locator('.record-editor summary').click();p.locator('#topic-facts').fill(scene+'：修改事实');p.locator('[data-action=topic-save]').click();updated=p.evaluate('(id)=>App.snapshot.observations.find(x=>x.id===id)',n['id']);check(updated['revision']==2 and updated['fields']['facts'].endswith('修改事实'),'revision');outputs.append({'scene':scene,'recordId':n['id'],'revision':2})
  p.reload();check(p.evaluate('App.snapshot.observations.filter(x=>x.kind==="topic-record").length')==8,'reload');return outputs
 test('eight-independent-scene-save-edit-reload',topics)
 def metadata():
  cases=[('relationship:D1:ability','relationshipDimension','D1'),('relationship:D1:willingness','relationshipFacet','willingness'),('relationship:D1:need','relationshipFacet','need'),('relationship:D1:boundary','relationshipFacet','boundary'),('observation:values','observationArea','values'),('factor:A','factorId','A')]
  for kind,key,val in cases:
   nav('journal?kind='+kind);p.locator('#journal-text').fill('本人记录 '+kind);p.locator('[data-action=save-journal]').click();n=p.evaluate('App.snapshot.observations.at(-1)');check(n.get(key)==val,str(n))
  p.reload();nav('relationship-detail?id=D1');check(p.locator('.relationship-facets article').count()==4,'four facets');check(p.locator('.relationship-facets .list-item').count()==4,'four separate notes');nav('observation-area?id=values');check('本人记录 observation:values' in p.locator('main').inner_text(),'area note');nav('factor-detail?id=A');check('本人记录 factor:A' in p.locator('main').inner_text(),'factor note');return {'linkedNotes':6,'independentFacets':4,'reload':True}
 test('explicit-personal-evidence-associations',metadata)
 def profile():
  nav('assistant');check(p.locator('[data-action=profile-group]').count()==3,'three groups');check(p.locator('.profile-radar').count()==0,'no empty radar');p.locator('[data-action=profile-group][data-id=relationships]').click();check(p.locator('.relationship-dimensions .list-item').count()==8,'8 dimensions');p.locator('[data-action=profile-group][data-id=observations]').click();check(p.locator('.observation-area').count()==8,'8 containers');check('1 条记录' in p.locator('.observation-map').inner_text(),'manual count');return {'groups':3,'relationshipDimensions':8,'observationContainers':8,'unknownNotZero':True}
 test('profile-unknown-and-three-groups',profile)
 def matrixfn():
  for theme in themes:
   go('home',theme=theme)
   for route in routes:
    nav(params[route]);check(p.locator('main').inner_text().strip(),'blank '+route);overflow=p.evaluate('document.documentElement.scrollWidth>innerWidth+1');matrix.append({'theme':theme,'route':route,'overflow':overflow});check(not overflow,theme+' '+route+' overflow')
    if theme==themes[0]:
     text=p.locator('main').inner_text();matches=re.findall(r'.{0,18}(?:原型|设计预览|演示|本轮|样例).{0,25}',text)
     if matches:copy.append({'route':route,'matches':matches})
   print('theme complete',theme,flush=True)
  check(not copy,'Runtime development copy: '+str(copy));return {'checks':len(matrix),'runtimeCopyFindings':copy}
 test('all-43-routes-across-12-themes',matrixfn)
 def widths():
  for width in [320,390,430]:
   p.set_viewport_size({'width':width,'height':844})
   for route in ['home','explore','assistant','relationship-detail?id=D3','topic-workspace?topic=first-job','assistant-chat']:
    go(route,theme='sunrise');check(not p.evaluate('document.documentElement.scrollWidth>innerWidth+1'),route+' '+str(width));p.screenshot(path=str(O/'screenshots'/f'{width}-{route.split("?")[0]}.png'),full_page=True)
   if width==320:
    nav('explore');rects=p.locator('.decision-card').evaluate_all('(es)=>es.map(e=>({w:e.clientWidth,h:e.clientHeight,sh:e.scrollHeight}))');check(all(x['w']>x['h'] and x['sh']<=x['h']+2 for x in rects),'320 rectangles '+str(rects))
  return {'widths':[320,390,430],'routes':6}
 test('responsive-real-browser-screenshots',widths)
 def workbench():
  q=ctx.new_page();q.goto(url+'/#page=assistant&scene=profile-sample&width=320');q.wait_for_function('document.querySelector("#runtime-status").textContent.includes("原型已连接")');f=q.frames[1];check(f.evaluate('ProductContext.fixture'),'fixture');check(f.locator('.profile-radar').count()==1,'graphic fixture');rects=f.locator('.radar-axis').evaluate_all('(es)=>es.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})');check(all(not(a['x']<z['x']+z['w'] and a['x']+a['w']>z['x'] and a['y']<z['y']+z['h'] and a['y']+a['h']>z['y']) for i,a in enumerate(rects) for z in rects[i+1:]),'overlapping chart controls');check('图形位置样例' in q.locator('#stage-caption').inner_text(),'outside provenance');q.screenshot(path=str(O/'screenshots/workbench-profile-fixture.png'),full_page=True)
  q.goto(url+'/?check=contract#page=relationship-detail&mode=contract');q.wait_for_function('document.querySelector("#panel-contract").textContent.includes("当前开发契约")');check('relationshipDimension' in q.locator('#panel-contract').inner_text(),'new contract');q.screenshot(path=str(O/'screenshots/workbench-new-contract.png'),full_page=True);q.close()
  p.goto(url+'/prototype/index.html?scenario=profile-sample&preview=1&reset=1#assistant');check(not p.evaluate('ProductContext.fixture'),'top-level gate');check(p.locator('.profile-radar').count()==0,'top-level sample leak');return {'workbenchFixture':True,'externalProvenance':True,'standaloneNoFixture':True,'newContractReadable':True}
 test('fixture-boundary-and-contract-reader',workbench)
 test('browser-errors',lambda:check(not errors,str(errors)))
 (O/'report.json').write_text(json.dumps({'results':results,'matrix':matrix,'copyFindings':copy,'errors':errors},ensure_ascii=False,indent=2));b.close()
srv.shutdown()

sys.exit(1 if errors or any(x["status"]=="FAIL" for x in results) else 0)
