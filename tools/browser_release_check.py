"""Release checks in Chromium/Firefox plus actual Chromium browser zoom."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json, os, subprocess, sys
from playwright.sync_api import sync_playwright
ROOT,OUT=map(lambda s:Path(s).resolve(),sys.argv[1:3]);OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';results=[];errors=[]
def check(v,msg):
 if not v:raise AssertionError(msg)
def capture(p,name):p.mouse.move(0,0);p.screenshot(path=str(OUT/(name+'.png')))
with sync_playwright() as w:
 for engine in ['chromium','firefox']:
  try:
   b=getattr(w,engine).launch(headless=True);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)))
   for theme in ['sunrise','nebula']:
    p.goto(base+'/prototype/index.html?reset=1&theme='+theme+'#assistant');p.wait_for_function('window.App&&window.Ambient');p.locator('.composer textarea').fill('合成发布检查：保持已输入内容');p.locator('.source-btn').click();p.evaluate('Promise.all(document.querySelector(".overlay").getAnimations({subtree:true}).map(a=>a.finished))');check(p.locator('.dialog').evaluate('e=>getComputedStyle(e).opacity')=='1','Translucent modal');p.keyboard.press('Escape');check(p.locator('.source-btn').evaluate('e=>e===document.activeElement'),'Modal focus restoration');check('合成发布检查' in p.locator('.composer textarea').input_value(),'Draft lost');capture(p,engine+'-'+theme+'-assistant')
    p.goto(base+'/prototype/index.html?reset=1&theme='+theme+'#report?id=report-sample-01');p.wait_for_function('window.App&&window.Ambient');p.locator('#report-personal').scroll_into_view_if_needed();p.wait_for_function('document.querySelector(".report-chapters [aria-current=location]").dataset.id==="report-personal"');capture(p,engine+'-'+theme+'-report');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Horizontal overflow')
   p.goto(base+'/#mode=logic');p.wait_for_timeout(900);check(p.locator('.view-tabs').evaluate('e=>e.scrollWidth<=e.clientWidth'),'Clipped phone tabs');capture(p,engine+'-workbench');results.append({'browser':engine,'version':b.version,'status':'PASS'});b.close()
  except Exception as e:results.append({'browser':engine,'status':'FAIL','error':str(e)})
 try:
  b=w.chromium.launch(headless=False,args=['--window-size=1440,1000']);c=b.new_context(no_viewport=True);p=c.new_page();p.goto(base+'/prototype/index.html?reset=1#home');p.bring_to_front();before=p.evaluate('({width:innerWidth,dpr:devicePixelRatio})')
  subprocess.run(['xdotool','key','--clearmodifiers','ctrl+0'],check=True)
  for _ in range(5):subprocess.run(['xdotool','key','--clearmodifiers','ctrl+plus'],check=True)
  p.wait_for_timeout(500);after=p.evaluate('({width:innerWidth,dpr:devicePixelRatio})');check(abs(after['dpr']/before['dpr']-2)<.02,'Native 200% zoom was not achieved')
  for route in ['home','assistant','report?id=report-sample-01','settings']:
   p.goto(base+'/prototype/index.html?reset=1#'+route);p.wait_for_function('window.App&&window.Ambient');p.wait_for_timeout(250);check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Overflow at native 200%');capture(p,'native-200-'+route.split('?')[0])
  p.goto(base+'/#mode=contract');p.wait_for_selector('.dev-fields');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Workbench overflow at native 200%');capture(p,'native-200-workbench');results.append({'browser':'chromium native 200%','before':before,'after':after,'status':'PASS'});b.close()
 except Exception as e:results.append({'browser':'chromium native 200%','status':'FAIL','error':str(e)})
s.shutdown();report={'checks':results,'pageErrors':errors,'limits':'Representative checks only; no mobile software keyboard, screen-reader or complete cross-browser matrix.'};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));sys.exit(1 if errors or any(x['status']=='FAIL' for x in results) else 0)
