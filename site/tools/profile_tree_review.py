from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import json
import argparse, shutil
parser=argparse.ArgumentParser(description='Browser checks for the standalone profile-tree comparison')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];out=args.output;shots=out/'screenshots';shots.mkdir(parents=True,exist_ok=True)
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(root)));Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_port}/review/profile-trees/'
results=[];errors=[]
def check(v,m):
 if not v:raise AssertionError(m)
with sync_playwright() as w:
 browser=w.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox']);ctx=browser.new_context();p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));requests=[];p.on('request',lambda r:requests.append(r.url));p.goto(url);p.wait_for_function('window.TreeComparison');p.evaluate("localStorage.setItem('jianji-design-v4','do-not-touch');sessionStorage.setItem('sentinel','unchanged');window.originalCanvas=document.querySelector('#ambient-tide')")
 initial=p.evaluate('JSON.stringify(TreeComparison.positions)');themes=p.locator('#theme option').evaluate_all('(es)=>es.map(e=>e.value)')
 p.set_viewport_size({'width':1440,'height':1080});p.evaluate('Ambient.sample(8)');p.screenshot(path=str(shots/'desktop-three-schemes.png'),full_page=True)
 for width in [320,390,430]:
  p.set_viewport_size({'width':width,'height':844});p.evaluate('scrollTo(0,0)')
  for scheme in ['a','b','c']:
   p.locator('[data-scheme='+scheme+']').click();nodes=p.locator('.selected-scheme [data-branch]');check(nodes.count()==8,'8 main branches');rects=nodes.evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,b:r.bottom}})')
   check(all(r['b']<=844 for r in rects),'all main branches first screen '+str((width,scheme)))
   check(all(r['w']>=44 and r['h']>=44 for r in rects),'targets 44')
   check(all(not(a['x']<b['x']+b['w'] and a['x']+a['w']>b['x'] and a['y']<b['y']+b['h'] and a['y']+a['h']>b['y']) for i,a in enumerate(rects) for b in rects[i+1:]),'targets overlap '+str((width,scheme)))
   check(not p.evaluate('document.documentElement.scrollWidth>innerWidth'),'overflow');p.screenshot(path=str(shots/f'{width}-{scheme}-overview.png'))
  results.append({'test':f'{width}px 3 designs overview/44px/nonoverlap/first-screen','status':'PASS'})
 p.locator('.selected-scheme [data-branch=D7]').focus();p.keyboard.press('Enter');check(p.locator('.selected-scheme [data-facet]').count()==4,'only4leaves');p.keyboard.press('End');check(p.locator(':focus').get_attribute('data-facet')=='boundary','End');p.keyboard.press('Enter');check('风险兜底' in p.locator('#inspector').inner_text(),'context');p.screenshot(path=str(shots/'phone-risk-boundary.png'))
 p.locator('[data-entry=record]').click();p.locator('#sample-note').fill('这是临时合成记录，遇到突发开支时先确认预算。');p.locator('[data-save-example]').click();check('临时合成记录' in p.locator('#inspector').inner_text(),'sample save');p.keyboard.press('Escape');check(p.locator('.selected-scheme [data-branch]').count()==8,'Escape overview');check(p.evaluate('JSON.stringify(TreeComparison.positions)')==initial,'fixed positions');check(p.evaluate("document.querySelector('#ambient-tide')===originalCanvas"),'canvas continuity')
 p.locator('.selected-scheme [data-branch=D2]').click();p.locator('.selected-scheme [data-facet=ability]').click();check('未探索' in p.locator('#inspector').inner_text(),'unknown clickable');p.locator('[data-entry=question]').click();check('不计算分数' in p.locator('.entry-demo').inner_text(),'question no scoring');p.locator('[data-close-entry]').click();check(p.locator(':focus').get_attribute('data-entry')=='question','restore focus')
 p.locator('.display-options>summary').click();p.locator('#reset').click();check(not p.evaluate('Object.keys(TreeComparison.snapshot().temporary).length'),'reset temporary');check(p.evaluate("localStorage.getItem('jianji-design-v4')")=='do-not-touch','local storage isolation');check(p.evaluate("sessionStorage.getItem('sentinel')")=='unchanged','session isolation');p.locator('.display-options>summary').click();results.append({'test':'keyboard/focus/context/temporary/reset/storage isolation/canvas identity','status':'PASS'})
 for theme in themes:
  p.locator('.display-options>summary').click();p.locator('#theme').select_option(theme);p.locator('.display-options>summary').click();p.evaluate('scrollTo(0,0)')
  for scheme in ['a','b','c']:
   p.locator('[data-scheme='+scheme+']').click();check(p.locator('.selected-scheme [data-branch]').count()==8,'theme nodes');check(not p.evaluate('document.documentElement.scrollWidth>innerWidth'),'theme overflow')
  if theme in ['sunrise','nebula','amber']:
   p.evaluate('Ambient.sample(8)');p.screenshot(path=str(shots/f'theme-{theme}.png'))
 results.append({'test':'12 complete themes × 3 schemes','status':'PASS'})
 p.emulate_media(reduced_motion='reduce');p.wait_for_timeout(50);check(p.evaluate('Ambient.isPaused()'),'reduced motion');p.emulate_media(reduced_motion='no-preference');p.locator('.display-options>summary').click();p.locator('#still').check();check(p.evaluate('Ambient.isPaused()'),'manual static');p.locator('.display-options>summary').click();results.append({'test':'system reduced motion and manual static','status':'PASS'})
 check(not errors,str(errors));check(all(r.startswith(f'http://127.0.0.1:{srv.server_port}/') for r in requests),'external request');results.append({'test':'no page errors or external service requests','status':'PASS'})
 browser.close()
(out/'report.json').write_text(json.dumps({'results':results,'errors':errors,'themeCount':len(themes),'limits':'Chromium local HTTP; no real mobile keyboard or screen-reader certification. Existing app not modified.'},ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False))
