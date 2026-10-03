"""Six-entry UI previews only. Synthetic isolated contexts, no real scoring/model calls."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
import os,sys,json,traceback
from playwright.sync_api import sync_playwright
from product_browser import ProductBrowser
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=ROOT/'qa'/'six-paths-ui';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=s.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{s.server_port}'
results=[]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
def goto(p,r='home',theme='sunrise',scenario='default'):
 p.open_product(BASE,r,scenario,theme)
def shot(p,name):p.screenshot(path=str(OUT/(name+'.png')),full_page=True)
with sync_playwright() as w:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**args)
 for theme in ['sunrise','candy','berry','lime','aurora','sea','nebula','amber']:
  ctx=b.new_context(viewport={'width':320,'height':844},locale='zh-CN',reduced_motion='reduce');p=ProductBrowser(ctx.new_page());errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  try:
   goto(p,theme=theme);before=p.evaluate('JSON.stringify(App.snapshot)');check(p.locator('.home-assessment').count()==1 and p.locator('.home-path').count()==4,'One container plus four auxiliary entries required')
   boxes=p.locator('.assessment-mode [data-action=mode]').evaluate_all('(es)=>es.map(e=>({w:e.clientWidth,h:e.clientHeight}))');check(len(boxes)==2 and abs(boxes[0]['w']-boxes[1]['w'])<=1 and boxes[0]['h']==boxes[1]['h'],'Version choices unequal');check(p.locator('.home-assessment-start').count()==1 and p.locator('.home-assessment-start').is_disabled(),'Unavailable measurement must be clear before start')
   shot(p,theme+'-home-320')
   for r in ['single-factor','daily-checkin','short-16pf','personality-sandbox','ai-reset']:
    p.evaluate("location.hash='ai-reset'") if r=='ai-reset' else p.locator('[data-route='+r+']').click();p.wait_for_function('r=>App.currentRoute===r',arg=r)
    check(p.locator('.preview-heading').count()==1,'Missing owned preview heading');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Horizontal overflow '+r)
    check(p.locator('[data-action=preview-stage][data-stage=process]').count()==0,'Default page exposed fixture questions');check(p.evaluate('App.snapshot.sessions.length')==0,'Preview created a measurement')
    shot(p,theme+'-'+r);p.locator('[data-action=back]').click();p.wait_for_function('App.currentRoute==="home"')
   check(p.evaluate('JSON.stringify(App.snapshot)')==before,'Preview navigation wrote real state');check(not errors,str(errors));results.append({'test':'eight-theme-narrow-'+theme,'status':'PASS'})
  except Exception as e:results.append({'test':'eight-theme-narrow-'+theme,'status':'FAIL','error':str(e)})
  ctx.close()
 ctx=b.new_context(viewport={'width':390,'height':844},locale='zh-CN',reduced_motion='no-preference');p=ProductBrowser(ctx.new_page())
 try:
  goto(p,scenario='sample-report');before=p.evaluate('JSON.stringify(App.snapshot)');shot(p,'home-390');p.locator('[data-route=single-factor]').click();check(p.locator('.factor-choice').count()==16,'Not all sixteen factors selectable');check(p.locator('[data-action=preview-stage]').is_disabled(),'Empty factor starts preview')
  p.locator('[data-action=preview-factor][data-id=Q3]').focus();p.keyboard.press('Enter');check(p.locator('[data-id=Q3]').get_attribute('aria-pressed')=='true','Keyboard selection failed');shot(p,'factor-selected')
  p.locator('[data-action=preview-stage]').click();check(p.locator('#ambient-background').get_attribute('data-quiet')=='true','Question preview not quiet');check(p.locator('[data-stage=result]').is_disabled(),'Empty answer advances');shot(p,'factor-process-empty')
  for value in ['b','c']:
   p.locator('[data-action=preview-answer][data-value='+value+']').focus();p.keyboard.press('Enter');check(p.evaluate('v=>document.activeElement.dataset.value===v',value),'Answer focus moved');p.keyboard.press('Space');check(p.evaluate('v=>document.activeElement.dataset.value===v',value),'Space moved answer focus');check(p.locator('[data-action=preview-answer][data-value='+value+']').get_attribute('aria-pressed')=='true','Space changed selected answer')
  shot(p,'factor-process-selected');p.locator('[data-stage=result]').click();check('还没有可查看的解读' in p.locator('.preview-paper').inner_text(),'Fake result');shot(p,'factor-result-empty')
  p.locator('[data-action=back]').click();p.locator('[data-route=daily-checkin]').click();p.locator('[data-action=preview-count][data-value="5"]').focus();p.keyboard.press('Enter');check(p.evaluate("document.activeElement.dataset.value==='5'"),'Five-question focus moved');p.keyboard.press('Space');check(p.evaluate("document.activeElement.dataset.value==='5'"),'Space moved the selected count');check(p.locator('[data-value="5"]').get_attribute('aria-pressed')=='true','Count selection failed');shot(p,'daily-five-empty');p.locator('[data-stage=process]').click();check('1 / 5' in p.locator('.preview-paper').inner_text(),'Wrong daily final range');shot(p,'daily-process')
  p.locator('[data-action=back]').click();p.locator('[data-route=short-16pf]').click();p.locator('[data-stage=process]').click();p.locator('[data-action=preview-answer]').nth(1).click();p.locator('[data-stage=result]').click();shot(p,'short-result-empty')
  p.locator('[data-action=back]').click();p.locator('[data-route=personality-sandbox]').click();check(p.locator('input[type=range]').count()==16,'Simulation must allow all factors');check('已设置 0 / 16' in p.locator('#sandbox-count').inner_text(),'Midpoints treated as real inputs')
  p.locator('#hypothesis-A').focus();p.keyboard.press('ArrowRight');p.locator('#hypothesis-Q4').focus();p.keyboard.press('Home');check(p.locator('#value-A').inner_text()=='6' and p.locator('#value-Q4').inner_text()=='0','Native keyboard control failed');shot(p,'sandbox-selected')
  p.locator('[data-stage=result]').click();check('这组假设设定' in p.locator('.preview-paper').inner_text(),'No hypothetical boundary');shot(p,'sandbox-result');p.locator('[data-stage=config]').click();p.locator('[data-action=preview-clear-scores]').click();check('已设置 0 / 16' in p.locator('#sandbox-count').inner_text(),'Reset failed')
  check(p.evaluate('JSON.stringify(App.snapshot)')==before,'UI previews changed person/records/profile');p.reload(wait_until='networkidle');check('已设置 0 / 16' in p.locator('#sandbox-count').inner_text(),'Preview unexpectedly persisted')
  results.append({'test':'selection-keyboard-process-results-isolated-state','status':'PASS'})
 except Exception as e:results.append({'test':'selection-keyboard-process-results-isolated-state','status':'FAIL','error':str(e),'trace':traceback.format_exc(limit=2)})
 ctx.close();b.close()
report={'capturedAt':datetime.now(timezone.utc).isoformat(),'passed':all(x['status']=='PASS' for x in results),'syntheticOnly':True,'results':results}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));s.shutdown()
if not report['passed']:raise SystemExit(1)
