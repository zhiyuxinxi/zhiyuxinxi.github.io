"""Independent-review regressions and representative local-only theme journeys."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json, os, sys
from playwright.sync_api import sync_playwright
ROOT, OUT=map(lambda x:Path(x).resolve(),sys.argv[1:3]);OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}';results=[];errors=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
def shot(p,name):
 p.mouse.move(0,0);p.screenshot(path=str(OUT/(name+'.png')))
def settle(p):
 p.evaluate('Promise.all(document.querySelector(".overlay").getAnimations({subtree:true}).map(a=>a.finished))')
def visit(p,route,theme):
 p.goto(f'{base}/prototype/index.html?reset=1&theme={theme}#{route}');p.wait_for_function('window.App&&window.Ambient');p.wait_for_timeout(250);p.evaluate('Ambient.sample(8)')
with sync_playwright() as w:
 launch={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):launch['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**launch)
 for theme in json.loads((ROOT/'handoff/themes-v4.json').read_text()):
  t=theme['id'];p=b.new_page(viewport={'width':390,'height':844},locale='zh-CN');p.on('pageerror',lambda e:errors.append(str(e)))
  try:
   visit(p,'home',t);p.evaluate('window.savedCanvas=document.querySelector("canvas")');shot(p,t+'-home')
   p.locator('.nav [data-route=explore]').click();p.locator('.v3-topic[data-id=work-choice]').click();shot(p,t+'-topic')
   p.locator('[data-action=topic-journal]').first.click();p.locator('#topic-issue').fill('合成评审：下一次讨论前如何整理问题');p.locator('#topic-understanding').fill('合成评审：先列出两个已知条件，并保留尚未确认的部分。');p.locator('[data-action=topic-save]').click();p.wait_for_selector('.record-summary');shot(p,t+'-saved')
   p.locator('[data-action=topic-to-assistant]').click();p.wait_for_selector('.source-btn');p.locator('.composer textarea').fill('合成评审：只用这份记录，帮我理清下一步。');shot(p,t+'-assistant')
   p.locator('.source-btn').click();p.evaluate('document.querySelector(".dialog").getAnimations().forEach(a=>{a.pause();a.currentTime=50})')
   check(p.locator('#notice').evaluate('e=>getComputedStyle(e).opacity')=='0','Stale success toast covers modal');check(p.locator('#notice').get_attribute('role')=='status' and p.locator('#notice').get_attribute('aria-live')=='polite','Success live region removed');check('整理卡已保存在本机' in p.locator('#notice').text_content(),'Success announcement erased');check(p.locator('.dialog').evaluate('e=>getComputedStyle(e).opacity')=='1','Panel fades during entry');shot(p,t+'-modal-entering')
   p.evaluate('document.querySelector(".dialog").getAnimations().forEach(a=>a.play())');settle(p);shot(p,t+'-modal')
   check(p.locator('.dialog').evaluate('e=>getComputedStyle(e).backgroundColor.startsWith("rgb(")'),'Panel is translucent')
   p.keyboard.press('Tab');check(p.locator('.dialog').evaluate('e=>e.contains(document.activeElement)'),'Focus escaped modal');p.keyboard.press('Escape');check(p.locator('.source-btn').evaluate('e=>e===document.activeElement'),'Focus not restored')
   check(p.evaluate('savedCanvas===document.querySelector("canvas")'),'Canvas replaced on journey')
   p.locator('.nav [data-route=me]').click();shot(p,t+'-me');check(p.evaluate('App.snapshot.observations.some(x=>x.fields?.issue?.startsWith("合成评审"))'),'Saved record missing')
   visit(p,'report?id=report-sample-01',t)
   p.locator('#report-personal').scroll_into_view_if_needed();p.wait_for_function('document.querySelector(".report-chapters [aria-current=location]").dataset.id==="report-personal"');shot(p,t+'-report-observation')
   for chapter in ['report-action','report-evidence','report-overview','report-personal']:
    p.locator(f'.report-chapters [data-id={chapter}]').click();p.wait_for_function('(id)=>document.querySelector(".report-chapters [aria-current=location]").dataset.id===id',arg=chapter);p.wait_for_timeout(600);check(p.locator('.report-chapters [aria-current=location]').get_attribute('data-id')==chapter,'Unstable chapter after scroll')
   check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Horizontal overflow')
   results.append({'theme':t,'group':theme['group'],'journey':'home → explore → topic → write → save → assistant with explicit source → modal → me → report chapters','status':'PASS'})
  except Exception as e:results.append({'theme':t,'status':'FAIL','error':str(e)})
  p.close()
 p=b.new_page(viewport={'width':768,'height':1024},locale='zh-CN')
 try:
  p.goto(base);p.wait_for_function('document.querySelector("#runtime-status").textContent.includes("原型已连接")');p.get_by_role('tab',name='逐页开发说明',exact=True).click();p.wait_for_selector('.dev-fields');shot(p,'workbench-768-contract')
  check(p.locator('#mobile-nav').is_visible(),'Tablet directory toggle absent');check(p.locator('.sidebar').evaluate('e=>e.getBoundingClientRect().right<=1'),'Tablet directory not collapsed')
  field=p.locator('.dev-fields>div').first;check(field.evaluate('e=>getComputedStyle(e).display')=='block','Tablet fields not stacked');check(p.locator('.dev-fields dt',has_text='最小价值').count()==1,'Repeated minimum value label')
  p.locator('#mobile-nav').click();check(p.locator('.sidebar').evaluate('e=>e.classList.contains("open")'),'Directory cannot open');p.keyboard.press('Escape');check(p.locator('#mobile-nav').evaluate('e=>e===document.activeElement'),'Directory focus not restored')
  p.set_viewport_size({'width':390,'height':844});p.get_by_role('tab',name='底层逻辑方案',exact=True).click();p.wait_for_timeout(400);shot(p,'workbench-390-logic')
  check(p.locator('.view-tabs').evaluate('e=>e.scrollWidth<=e.clientWidth'),'Phone tabs overflow')
  for tab in p.locator('.view-tabs button').all():check(tab.evaluate('e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.height>=44}'),'Clipped or short destination')
  results.append({'state':'tablet-document-phone-navigation','status':'PASS'})
 except Exception as e:results.append({'state':'tablet-document-phone-navigation','status':'FAIL','error':str(e)})
 b.close()
server.shutdown();report={'results':results,'pageErrors':errors,'limits':'Local synthetic records only. No claim of award quality, native-device keyboard or full accessibility certification.'};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));sys.exit(1 if errors or any(x['status']=='FAIL' for x in results) else 0)
