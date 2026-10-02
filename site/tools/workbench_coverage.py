"""Enumerate actual Views.map, verify every tree preview and theme shell on native HTTP.
Does not treat shared tokens or a first viewport as complete all-state visual acceptance.
All records are isolated synthetic fixtures; no backend requests or publication.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
import json,os,sys
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=ROOT/'qa'/'complete-workbench';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
results=[];matrix=[];errors=[];currentNode=[None]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
def test(name,fn):
 try:detail=fn();results.append({'test':name,'status':'PASS','details':detail})
 except Exception as e:results.append({'test':name,'status':'FAIL','error':str(e),'node':currentNode[0]})
 print(name,results[-1]['status'],results[-1].get('node'),flush=True)
with sync_playwright() as w:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**args);c=b.new_context(viewport={'width':1480,'height':1100},locale='zh-CN');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto(BASE);p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')")
 data=p.evaluate('WorkbenchData');nodes=data['routes'];f=p.frames[1];actual=f.evaluate('Object.keys(Views.map)');families={x['route'].split('?')[0] for x in nodes if x.get('route')}
 def mapping():
  check(set(actual)==families,'Actual route families differ from tree: '+str(set(actual)^families));ids=[x['id'] for x in nodes];check(len(ids)==len(set(ids)),'Duplicate node IDs')
  roots=[id for g in data['groups'] for id in g['items']];check(set(roots)=={x['id'] for x in nodes if not x.get('parentId')},'Unreachable root nodes')
  check(all(not x.get('parentId') or x['parentId'] in ids for x in nodes),'Orphan node');return {'routeFamilies':len(actual),'nodes':len(nodes),'previewNodes':sum(bool(x.get('route')) for x in nodes),'specificationOrPlanned':sum(not x.get('route') for x in nodes)}
 test('exhaustive-route-and-tree-map',mapping)
 def visit_tree():
  visited=[]
  browse_nodes=nodes+[dict(id='state:'+x['id'],route=x['route'],scenario=x['id']) for x in data['scenes']]+[dict(id='backend:'+x['id']) for x in data['backend']]
  for x in browse_nodes:
   currentNode[0]=x['id']
   p.locator('#expand-tree').click();p.locator('[data-page="'+x['id']+'"]').click()
   p.wait_for_function('(id)=>document.querySelector("[data-page=\\\""+id+"\\\"]").getAttribute("aria-selected")==="true"',arg=x['id'],timeout=5000)
   if x.get('route'):
    f=p.frames[1];f.wait_for_function('r=>App.currentRoute===r',arg=x['route']);p.wait_for_timeout(100)
    check(f.locator('main').inner_text().strip()!='','Blank route '+x['id'])
    if x.get('previewStage'):f.wait_for_function('s=>AssessmentPreview.getStage()===s',arg=x['previewStage'])
    if x.get('previewAction'):f.wait_for_selector('[role=dialog]',timeout=5000);f.locator('[role=dialog]').press('Escape')
    check(f.locator('.brandline,.wordmark,.prototype-label').count()==0,'Product toolbar returned')
   else:check(p.locator('#panel-contract').is_visible(),'Specification used fake preview')
   visited.append(x['id'])
  return {'visited':visited}
 test('every-tree-node-real-navigation',visit_tree)
 def states():
  p.locator('#expand-tree').click();p.locator('[data-page=single-factor]').click();f=p.frames[1];f.locator('[data-action=preview-factor]').first.click();f.locator('[data-action=preview-stage][data-stage=process]').click();p.wait_for_function("document.querySelector('[data-page=single-factor-process]').getAttribute('aria-selected')==='true'")
  f.locator('[data-action=preview-answer]').first.click();f.locator('[data-action=preview-stage][data-stage=result]').click();p.wait_for_function("document.querySelector('[data-page=single-factor-result]').getAttribute('aria-selected')==='true'")
  url=p.url;p.reload();p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");p.frames[1].wait_for_function("AssessmentPreview.getStage()==='result'");return {'deepLink':url.split('#')[-1],'stageReflectedInTree':True}
 test('substate-sync-and-deep-link',states)
 def search_keyboard():
  p.locator('#tree-search').fill('结果空状态');check(p.locator('.tree-leaf:visible').count()>=3,'Search misses nested results');p.locator('#clear-search').click();check(p.locator('#tree-search').input_value()=='','Clear failed');p.locator('#collapse-tree').click();first=p.locator('.tree-folder').first;first.focus();first.press('ArrowRight');check(first.get_attribute('aria-expanded')=='true','Right key fails');first.press('ArrowRight');check(p.locator('.tree-leaf').first.evaluate('e=>e===document.activeElement'),'Roving focus fails');return {'nestedSearch':True,'keyboardTree':True}
 test('tree-search-clear-and-keyboard',search_keyboard)
 def stale_message():
  before=p.url;p.frames[1].evaluate("parent.postMessage({type:'jianji-preview-state',version:4,reviewSession:'obsolete',route:'home',theme:'amber'},location.origin)");p.wait_for_timeout(80);check(p.url==before,'Obsolete iframe message changed current selection');return {'obsoleteGenerationIgnored':True}
 test('obsolete-frame-message-ignored',stale_message)
 def newly_completed_session():
  ctx=b.new_context(viewport={'width':1480,'height':1100},locale='zh-CN');q=ctx.new_page()
  try:
   q.goto(BASE+'/?workflow=new-session');q.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");frame=q.frames[1]
   frame.locator('[data-action=start]').click();frame.wait_for_function("App.currentRoute.startsWith('question?')");sid=frame.evaluate('App.snapshot.activeSession');check(sid!='session-demo-seed','Must exercise a newly created session')
   for choice in ['a','b','c']:
    frame.locator('[data-action=answer][data-id='+choice+']').click();frame.locator('[data-action=question-next]').click()
   frame.locator('[data-action=finish]').click();frame.wait_for_function('id=>App.currentRoute==="complete?id="+id',arg=sid)
   q.wait_for_function("document.querySelector('[data-page=complete]').getAttribute('aria-selected')==='true'",timeout=5000)
   check(q.locator('#page-title').inner_text()=='作答完成（3题示例）','Wrong completion title');check('complete%3Fid%3D'+sid in q.url,'Workbench URL lost actual new session')
   check(q.locator('.frame-shell').evaluate('e=>e.scrollTop===0&&e.scrollLeft===0'),'Scaled viewport mask scrolled after answering');frame.wait_for_function('scrollY===0');q.wait_for_timeout(200);q.screenshot(path=str(OUT/'real-new-session-complete.png'));return {'sessionId':sid,'seedFixture':False,'actualRoute':'complete?id='+sid,'selectedNode':'complete'}
  finally:ctx.close()
 test('new-session-completion-reflects-in-tree',newly_completed_session)
 def actual_exploration_topics():
  ctx=b.new_context(viewport={'width':1480,'height':1100},locale='zh-CN');q=ctx.new_page();visited=[]
  try:
   q.goto(BASE+'/?workflow=exploration');q.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");frame=q.frames[1];frame.locator('[data-action=tab][data-route=explore]').click()
   topics=frame.evaluate("D.topics.filter(x=>x.id!=='work-choice').map(x=>x.id)")
   for topic in topics:
    frame.locator('[data-action=nav][data-route=topic][data-id='+topic+']').click();frame.wait_for_function('r=>App.currentRoute===r',arg='topic?id='+topic)
    node='topic-'+topic;q.wait_for_function('id=>document.querySelector("[data-page=\\\""+id+"\\\"]").getAttribute("aria-selected")==="true"',arg=node,timeout=5000)
    check(q.locator('#page-title').inner_text()==next(x['name'] for x in nodes if x['id']==node),'Wrong topic title');visited.append({'route':'topic?id='+topic,'selectedNode':node})
    check(q.locator('.frame-shell').evaluate('e=>e.scrollTop===0&&e.scrollLeft===0'),'Scaled viewport mask scrolled after topic navigation')
    if topic=='relationships':frame.wait_for_function('scrollY===0');q.wait_for_timeout(200);q.screenshot(path=str(OUT/'real-explore-relationships.png'))
    frame.locator('[data-action=back]').first.click();frame.wait_for_function("App.currentRoute==='explore'")
   check(len(visited)==4,'Must visit all four non-default topics');return visited
  finally:ctx.close()
 test('explore-to-four-nondefault-topics-reflects-in-tree',actual_exploration_topics)

 def captures():
  shots=[]
  for width,height in [(1480,1100),(1188,761),(390,844)]:
   p.set_viewport_size({'width':width,'height':height});p.goto(BASE+'/?layout='+str(width)+'#page=home');p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");p.wait_for_timeout(200)
   check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Shell overflow')
   if width>740:
    box=p.locator('#product-frame').bounding_box();check(box['y']+box['height']<height-25,'Full preview is clipped')
   name='layout-'+str(width);p.screenshot(path=str(OUT/(name+'.png')));shots.append(name)
   if width==390:
    p.locator('#mobile-nav').click();p.wait_for_timeout(250);check(p.locator('#sidebar').evaluate('e=>e.getBoundingClientRect().x>=0'),'Mobile tree closed');p.screenshot(path=str(OUT/'mobile-tree.png'));p.keyboard.press('Escape');check(p.locator('#mobile-nav').get_attribute('aria-expanded')=='false','Escape fails')
   else:
    p.locator('#preview-scale').select_option('actual');check(p.locator('#product-frame').bounding_box()['height']>800,'Actual size is lost');p.screenshot(path=str(OUT/('actual-'+str(width)+'.png')))
  return shots
 test('desktop-fit-original-size-and-mobile',captures)
 c.close()
 # Every real route gets a real browser render in each available theme, with genuine prerequisite fixtures.
 c=b.new_context(viewport={'width':390,'height':844},locale='zh-CN');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 primary={}
 for x in nodes:
  if x.get('route') and x['route'].split('?')[0] not in primary:primary[x['route'].split('?')[0]]=x
 for t in ([] if os.environ.get('WORKBENCH_SHELL_ONLY') else data['themes']):
  for base,x in primary.items():
   row={'theme':t['id'],'route':base}
   try:
    p.goto(BASE+'/prototype/index.html?reset=1&scenario='+x.get('scenario','default')+'&theme='+t['id']+'#'+x['route'],wait_until='load');p.wait_for_function('window.App&&window.Ambient');p.wait_for_timeout(70)
    check(p.evaluate('App.currentRoute')==x['route'],'Wrong route');check(p.locator('main').inner_text().strip()!='','Blank content');check(p.locator('.brandline,.wordmark,.prototype-label').count()==0,'Removed toolbar returned');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Horizontal overflow')
    shared=p.evaluate("({theme:App.snapshot.theme,mode:document.body.dataset.themeMode,canvas:!!document.querySelector('#ambient-tide'),field:getComputedStyle(document.body).getPropertyValue('--field-a'),surface:getComputedStyle(document.body).getPropertyValue('--surface'),quiet:Ambient.isPaused()})")
    check(shared['theme']==t['id'] and shared['canvas'] and shared['field'].strip() and shared['surface'].strip(),'Missing shared theme owner');check(shared['quiet']==(base=='question'),'Quiet route mismatch')
    if t['id']=='sunrise':p.screenshot(path=str(OUT/('page-'+base+'.png')),full_page=True)
    row.update(status='PASS',shared=shared)
   except Exception as e:row.update(status='FAIL',error=str(e))
   matrix.append(row)
 c.close();b.close()
server.shutdown();scope=('8 workbench shell regression checks: route/tree coverage, navigation, substate deep links, keyboard/search, stale messages, fit/original size and narrow drawer. Shell-only run: the 39 × 12 = 468 theme-route render matrix and all-route full-page screenshots were not rerun.' if os.environ.get('WORKBENCH_SHELL_ONLY') else 'All real route families × all 12 themes: real render, shared shell/token presence, no toolbar, no horizontal overflow. Full-page screenshots of all routes in sunrise. This is not a claim of all interaction states or pixel contrast in every theme.');report={'createdAt':datetime.now(timezone.utc).isoformat(),'scope':scope,'results':results,'themeRouteMatrix':matrix,'pageErrors':errors};(OUT/('shell-report.json' if os.environ.get('WORKBENCH_SHELL_ONLY') else 'report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'tests':results,'matrixPassed':sum(x['status']=='PASS' for x in matrix),'matrixTotal':len(matrix),'matrixFailures':[x for x in matrix if x['status']=='FAIL'],'pageErrors':errors},ensure_ascii=False,indent=2));sys.exit(0 if all(x['status']=='PASS' for x in results+matrix) and not errors else 1)
