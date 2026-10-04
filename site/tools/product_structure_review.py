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
  check(p.locator('.home-assessment').count()==1,'one container');check(p.locator('.home-assessment-start').count()==1,'one CTA');p.locator('[data-action=mode][data-id=ai]').focus();p.keyboard.press('Enter');check(p.locator('.home-assessment-start').get_attribute('data-route')=='ai-reset','AI CTA');p.locator('[data-action=mode][data-id=original]').click();check(p.locator('.home-assessment-start').is_disabled(),'unavailable before start');check('当前没有可用题目' in p.locator('main').inner_text(),'honest unavailable');p.locator('.home-assessment [data-route=explore]').click();check(p.locator('.decision-card').count()==8,'usable alternative');check(p.evaluate('App.snapshot.sessions.length')==0,'fake session');return {'singleCTA':True,'keyboardSelection':True,'noFakeSession':True}
 test('home-mode-and-unavailable',home)
 def topics():
  outputs=[]
  for scene in scenes:
   nav('topic-workspace?topic='+scene);check(p.locator('textarea').count()==4,'four inputs '+scene)
   title=p.evaluate('(id)=>DecisionScenes.items.find(x=>x.id===id).title',scene);texts={'facts':'关于'+title+'，我想先写下目前已经发生的事情。','priorities':'我在意稳定的休息，也希望保留继续学习的机会。','concerns':'我担心准备不足，也不想只因为一时情绪做决定。','unknown':'还需要了解实际安排、投入时间，以及可以获得的支持。'}
   for field in ['facts','priorities','concerns','unknown']:p.locator('#topic-'+field).fill(texts[field])
   p.locator('[data-action=topic-save]').click();n=p.evaluate('App.snapshot.observations.at(-1)');check(n['topicId']==scene,'topicID');check(n['fields']['facts']==texts['facts'],'specific fields')
   nav('topic-workspace?topic='+scene+'&id='+n['id']);p.locator('.record-editor summary').click();p.locator('#topic-facts').fill(title+' 我补充了一个最近发生的具体例子。');p.locator('[data-action=topic-save]').click();updated=p.evaluate('(id)=>App.snapshot.observations.find(x=>x.id===id)',n['id']);check(updated['revision']==2 and updated['fields']['facts'].endswith('具体例子。'),'revision');outputs.append({'scene':scene,'recordId':n['id'],'revision':2})
  p.reload();check(p.evaluate('App.snapshot.observations.filter(x=>x.kind==="topic-record").length')==8,'reload');return outputs
 test('eight-independent-scene-save-edit-reload',topics)
 def metadata():
  cases=[('relationship:D1:ability','relationshipDimension','D1'),('relationship:D1:willingness','relationshipFacet','willingness'),('relationship:D1:need','relationshipFacet','need'),('relationship:D1:boundary','relationshipFacet','boundary'),('observation:values','observationArea','values'),('factor:A','factorId','A')]
  for kind,key,val in cases:
   nav('journal?kind='+kind);p.locator('#journal-text').fill({'relationship:D1:ability':'目前能稳定承担自己的日常开支，大额支出需要提前安排。','relationship:D1:willingness':'共同活动的开支，我愿意提前商量并分担。','relationship:D1:need':'涉及共同储蓄时，我希望彼此能说清楚安排。','relationship:D1:boundary':'借出较大金额之前，我需要保留自己的应急储蓄。','observation:values':'换工作时，我发现学习机会和稳定休息对我都很重要。','factor:A':'和熟悉的同事讨论时，我比较愿意主动分享想法。'}[kind]);p.locator('[data-action=save-journal]').click();n=p.evaluate('App.snapshot.observations.at(-1)');check(n.get(key)==val,str(n))
  p.reload();nav('relationship-detail?id=D1');check(p.locator('.relationship-facets article').count()==4,'four facets');check(p.locator('.relationship-facets .list-item').count()==4,'four separate notes');nav('observation-area?id=values');check('学习机会和稳定休息' in p.locator('main').inner_text(),'area note');nav('factor-detail?id=A');check('主动分享想法' in p.locator('main').inner_text(),'factor note');p.screenshot(path=str(O/'screenshots/factor-personal-observation.png'),full_page=True);nav('relationship-detail?id=D1');p.screenshot(path=str(O/'screenshots/relationship-personal-observations.png'),full_page=True);return {'linkedNotes':6,'independentFacets':4,'reload':True}
 test('explicit-personal-evidence-associations',metadata)
 def profile():
  nav('assistant');check(p.locator('[data-action=profile-group]').count()==4,'four groups');check(p.locator('.profile-radar').count()==0,'no empty radar');p.locator('[data-action=profile-group][data-id=relationships]').click();check(p.locator('.relationship-dimensions .list-item').count()==8,'8 dimensions');p.locator('[data-action=profile-group][data-id=observations]').click();check(p.locator('.observation-area').count()==8,'8 containers');check('1 条记录' in p.locator('.observation-map').inner_text(),'manual count');return {'groups':4,'relationshipDimensions':8,'observationContainers':8,'unknownNotZero':True}
 test('profile-unknown-and-four-groups',profile)
 def relationship_context():
  nav('relationship-detail?id=D7');p.locator('.relationship-discussion>summary').click();p.locator('[data-route=assistant-chat][data-kind="relationship:D7:boundary"]').click();check('风险兜底 · 边界' in p.locator('.chat-topic').inner_text(),'Chinese topic lost');check(p.evaluate('App.snapshot.assistantSources.length')==0,'automatic personal reference')
  p.locator('textarea').fill('遇到突发困难时，我想先说清楚自己能承担的范围。');p.locator('[data-action=send]').click();check('暂不可用' in p.locator('[role=dialog]').inner_text(),'unavailable');p.keyboard.press('Escape');check('风险兜底 · 边界' in p.locator('.chat-topic').inner_text(),'topic lost after failure');p.reload();check('风险兜底 · 边界' in p.locator('.chat-topic').inner_text(),'topic lost after reload');check('突发困难' in p.locator('textarea').input_value(),'draft lost')
  p.locator('[data-action=context]').click();p.locator('[data-action=v2-pick-context]').first.click();check(p.evaluate('App.snapshot.assistantSources.length')==1,'explicit selection missing');check(p.evaluate('App.snapshot.conversations.length')==0,'automatic send');check('风险兜底 · 边界' in p.locator('.chat-topic').inner_text(),'topic lost after selection');p.screenshot(path=str(O/'screenshots/relationship-ai-context.png'),full_page=True);return {'topic':'风险兜底 · 边界','explicitSourceOnly':True,'noAutoSend':True,'unavailableKeepsDraftAndTopic':True}
 test('relationship-context-draft-and-explicit-reference',relationship_context)

 def matrixfn():
  for theme in themes:
   go('home',theme=theme)
   for route in routes:
    nav(params[route]);check(p.locator('main').inner_text().strip(),'blank '+route);overflow=p.evaluate('document.documentElement.scrollWidth>innerWidth+1');controls=p.evaluate('''()=>({unwiredButtons:[...document.querySelectorAll('main button:not([disabled])')].filter(e=>!e.dataset.action&&!(e.type==='submit'&&e.form)).map(e=>e.outerHTML.slice(0,180)),resizableTextareas:[...document.querySelectorAll('main textarea')].filter(e=>getComputedStyle(e).resize!=='none').map(e=>e.id)})''');matrix.append({'theme':theme,'route':route,'overflow':overflow,'controls':controls});check(not controls['unwiredButtons'] and not controls['resizableTextareas'],str(controls));check(not overflow,theme+' '+route+' overflow')
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
  q=ctx.new_page();q.goto(url+'/#page=assistant&scene=profile-sample&width=320');q.wait_for_function('document.querySelector("#runtime-status").textContent.includes("原型已连接")');f=q.frames[1];check(f.evaluate('ProductContext.fixture'),'fixture');check(f.locator('.profile-radar').count()==1,'graphic fixture');rects=f.locator('.radar-axis').evaluate_all('(es)=>es.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})');check(all(not(a['x']<z['x']+z['w'] and a['x']+a['w']>z['x'] and a['y']<z['y']+z['h'] and a['y']+a['h']>z['y']) for i,a in enumerate(rects) for z in rects[i+1:]),'overlapping chart controls');check('图形位置样例' in q.locator('#stage-caption').inner_text(),'outside provenance');q.screenshot(path=str(O/'screenshots/workbench-profile-fixture.png'),full_page=True);f.locator('.profile-radar').screenshot(path=str(O/'screenshots/full-profile-layout.png'));q.locator('#product-frame').screenshot(path=str(O/'screenshots/profile-viewport.png'));f.locator('.radar-axis').first.click();f.wait_for_function("App.currentRoute==='factor-detail?id=A'");text=f.locator('main').inner_text();check('布局示意，不含测评读数' in text and '图形布局夹具' in text,'fixture provenance');check('16PF 原版' not in text and '2026-10-03' not in text,'invented measurement source');q.screenshot(path=str(O/'screenshots/workbench-factor-layout-source.png'),full_page=True);f.locator('section.card').screenshot(path=str(O/'screenshots/factor-layout-source-detail.png'))
  q.goto(url+'/?check=contract#page=relationship-detail&mode=contract');q.wait_for_function('document.querySelector("#panel-contract").textContent.includes("当前开发契约")');check('relationshipDimension' in q.locator('#panel-contract').inner_text(),'new contract');q.screenshot(path=str(O/'screenshots/workbench-new-contract.png'),full_page=True);q.close()
  p.goto(url+'/prototype/index.html?scenario=profile-sample&preview=1&reset=1#assistant');check(not p.evaluate('ProductContext.fixture'),'top-level gate');check(p.locator('.profile-radar').count()==0,'top-level sample leak');return {'workbenchFixture':True,'externalProvenance':True,'standaloneNoFixture':True,'newContractReadable':True}
 test('fixture-boundary-and-contract-reader',workbench)
 test('browser-errors',lambda:check(not errors,str(errors)))
 (O/'report.json').write_text(json.dumps({'results':results,'matrix':matrix,'copyFindings':copy,'errors':errors},ensure_ascii=False,indent=2));b.close()
srv.shutdown()

sys.exit(1 if errors or any(x["status"]=="FAIL" for x in results) else 0)
