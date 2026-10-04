"""Reproduce scaled-workbench pointer targeting while implicit scrolling positions the start button.
Ten independent sessions retain every failure; no retry, DOM-click, or timing bypass.
All records are isolated synthetic fixtures; no backend requests or publication.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
import json,os,sys,traceback
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'qa'/'workbench-pointer';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
results=[];matrix=[];errors=[];currentNode=[None]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
def test(name,fn):
 currentNode[0]=None
 try:detail=fn();results.append({'test':name,'status':'PASS','details':detail})
 except Exception as e:results.append({'test':name,'status':'FAIL','error':str(e),'traceback':traceback.format_exc(),'node':currentNode[0]})
 print(name,results[-1]['status'],results[-1].get('error',''),flush=True)
 (OUT/'progress.json').write_text(json.dumps({'results':results,'themeRouteMatrix':matrix,'pageErrors':errors},ensure_ascii=False,indent=2))
with sync_playwright() as w:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**args);c=b.new_context(viewport={'width':1480,'height':1100},locale='zh-CN');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto(BASE);p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')")
 data=p.evaluate('WorkbenchData');nodes=data['routes'];f=p.frames[1];actual=f.evaluate('Object.keys(Views.map)');families={x['route'].split('?')[0] for x in nodes if x.get('route')}
 def newly_completed_session():
  ctx=b.new_context(viewport={'width':1480,'height':1100},locale='zh-CN');q=ctx.new_page()
  try:
   q.goto(BASE+'/?workflow=new-session#scene=sample-report');q.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");frame=q.frames[1]
   frame.evaluate("""()=>{window.trace=[];for(const type of ['pointerdown','pointerup','mousedown','mouseup','click','focusin','scroll'])document.addEventListener(type,e=>{const b=document.querySelector('[data-action=start]');trace.push({type,t:performance.now(),target:e.target.outerHTML?.slice(0,160),x:e.clientX,y:e.clientY,scroll:scrollY,box:b?.getBoundingClientRect().toJSON(),hit:e.clientX?document.elementFromPoint(e.clientX,e.clientY)?.outerHTML.slice(0,160):null})},true);new MutationObserver(()=>trace.push({type:'mutation',t:performance.now()})).observe(document.getElementById('app'),{childList:true});}""")
   frame.locator('[data-action=start]').click();frame.wait_for_function("App.currentRoute.startsWith('question?')",timeout=2000);sid=frame.evaluate('App.snapshot.activeSession');check(sid!='session-demo-seed','Must exercise a newly created session')
   for choice in ['a','b','c']:
    frame.locator('[data-action=answer][data-id='+choice+']').click();frame.locator('[data-action=question-next]').click()
   frame.locator('[data-action=finish]').click();frame.wait_for_function('id=>App.currentRoute==="complete?id="+id',arg=sid)
   q.wait_for_function("document.querySelector('[data-page=complete]').getAttribute('aria-selected')==='true'",timeout=5000)
   check(q.locator('#page-title').inner_text()=='作答完成（3题示例）','Wrong completion title');check('complete%3Fid%3D'+sid in q.url,'Workbench URL lost actual new session')
   check(q.locator('.frame-shell').evaluate('e=>e.scrollTop===0&&e.scrollLeft===0'),'Scaled viewport mask scrolled after answering');frame.wait_for_function('scrollY===0');q.wait_for_timeout(200);q.screenshot(path=str(OUT/'real-new-session-complete.png'));return {'sessionId':sid,'seedFixture':False,'actualRoute':'complete?id='+sid,'selectedNode':'complete'}
  finally:
   q.screenshot(path=str(OUT/('session-'+str(attempt)+'.png')));(OUT/('state-'+str(attempt)+'.json')).write_text(json.dumps(frame.evaluate('({trace:window.trace,route:App.currentRoute,active:App.snapshot.activeSession,fixture:ProductContext.fixture,scrollY,body:document.body.innerText})'),ensure_ascii=False,indent=2));ctx.close()
 for attempt in range(10):test('new-session-'+str(attempt),newly_completed_session)

 c.close();b.close()
server.shutdown()
(OUT/'report.json').write_text(json.dumps({'results':results,'pageErrors':errors},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors or any(r['status']!='PASS' for r in results) else 0)
