"""Verify deployed public bytes and UI in isolated, synthetic browser contexts.
This script performs only public HTTP reads; product writes stay in disposable localStorage.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, os, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/'live-release';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://zhiyuxinxi.github.io'
SOURCE='c0e074a3109d6fc187692111266b2ea5fe1dd26c'
results=[]
def check(x,message='Assertion failed'):
 if not x:raise AssertionError(message)
def proto(p,route='home',scenario='default',theme='sunrise'):
 p.goto(f'{BASE}/prototype/index.html?reset=1&scenario=release-check-{scenario}&theme={theme}#{route}',wait_until='networkidle')
 p.wait_for_function('window.App&&App.snapshot');return p
# Reuse the exact reviewed record-loop browser test, substituting only the live origin.
source=(ROOT/'tools'/'hosted_smoke.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='real_problem_loop')
exec(compile(ast.Module(body=[node],type_ignores=[]),'reviewed-record-loop','exec'))
with sync_playwright() as w:
 launch={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):launch['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**launch)
 ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,locale='zh-CN',reduced_motion='reduce')
 p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  hashes=[]
  for name in ['product.css','experience-v3.js','views.js','themes-v4.css','app.js','flows-v2.js']:
   expected=hashlib.sha256((ROOT/'prototype'/name).read_bytes()).hexdigest()
   for attempt in range(8):
    r=ctx.request.get(f'{BASE}/prototype/{name}?release_check={SOURCE}-{attempt}',timeout=30000)
    actual=hashlib.sha256(r.body()).hexdigest()
    if r.ok and actual==expected:break
    time.sleep(15)
   check(r.ok and actual==expected,'Deployed resource is stale or differs: '+name)
   hashes.append({'file':name,'sha256':actual,'matchesCandidate':True})
  results.append({'test':'deployed-resource-hashes','status':'PASS','files':hashes})
  p.goto(BASE+'/?release_check='+SOURCE,wait_until='networkidle')
  p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')")
  f=p.frame_locator('#product-frame');check(f.locator('.brandline,.wordmark,.prototype-label').count()==0,'Public root iframe is stale')
  check(f.locator('.home-scene h2').inner_text()=='16PF 性格探索','Public root lost main task')
  results.append({'test':'public-root-connected-iframe','status':'PASS'})
  proto(p)
  for route in ['home','explore','assistant','me']:
   if route!='home':p.click('[data-action=tab][data-route='+route+']');p.wait_for_function('r=>App.currentRoute===r',arg=route)
   check(p.locator('.brandline,.wordmark,.prototype-label').count()==0,'Toolbar returned on '+route)
   check(p.locator('button[data-route=appearance]').count()==0,'Appearance bypassed settings on '+route)
   check(p.evaluate("getComputedStyle(document.body,'::before').backgroundImage.includes('gradient')"),'No global tide on '+route)
   check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Overflow on '+route)
   check(p.locator('.nav button').all_text_contents()==['认识','探索','助理','我的'],'Primary navigation changed')
   if route=='home':check(p.locator('.home-scene h2').inner_text()=='16PF 性格探索' and p.locator('[data-action=start]').count()==1,'Homepage assessment changed')
   p.screenshot(path=str(OUT/(route+'.png')))
   results.append({'test':'live-'+route,'status':'PASS'})
  p.click('[data-route=settings]');p.wait_for_function('App.currentRoute==="settings"');p.screenshot(path=str(OUT/'settings.png'))
  check(p.locator('button[data-route=appearance]').count()==1,'Settings missing appearance')
  p.click('[data-route=appearance]');p.click('[data-action=theme][data-id=nebula]')
  p.set_viewport_size({'width':320,'height':844});p.evaluate('scrollTo(0,0)');p.wait_for_function('scrollY===0');p.screenshot(path=str(OUT/'appearance-dark-320.png'))
  box=p.locator('.v4-live-preview>.v4-person-scene').bounding_box();halo=p.locator('.v4-live-preview>.v4-person-scene>span').bounding_box()
  check(abs(halo['width']-halo['height'])<1 and .84<halo['width']/box['width']<.88,'Preview ring regression on live site')
  p.click('[data-action=back]');p.wait_for_function('App.currentRoute==="settings"');p.click('[data-action=v3-preferences]')
  p.screenshot(path=str(OUT/'settings-dialog-dark-320.png'));p.keyboard.press('Escape')
  check(p.evaluate("document.activeElement.dataset.action==='v3-preferences'"),'Dark dialog focus failed')
  results.append({'test':'live-personal-settings-theme-dark-dialog','status':'PASS'})
  p.set_viewport_size({'width':390,'height':844});p.click('[data-action=back]');p.click('[data-action=tab][data-route=home]');p.screenshot(path=str(OUT/'home-dark.png'))
  p.click('[data-action=tab][data-route=explore]');p.locator('.explore-tools summary').click();p.click('[data-action=all-factors]');check(p.locator('.dialog .bottle-tile').count()==16);p.keyboard.press('Escape')
  p.click('[data-action=daily]');check('每日轻探索' in p.locator('.dialog').inner_text());p.keyboard.press('Escape')
  results.append({'test':'live-relocated-exploration-tools','status':'PASS'})
  detail=real_problem_loop(p);results.append({'test':'live-original-record-action-review-version-loop','status':'PASS','details':detail})
  check(not errors,'Browser errors: '+str(errors))
 except Exception as e:
  results.append({'test':'live-check','status':'FAIL','error':str(e)})
  p.screenshot(path=str(OUT/'failure.png'),full_page=True)
 finally:
  summary={'sourceSHA':SOURCE,'url':BASE,'checkedAt':datetime.now(timezone.utc).isoformat(),'browser':b.version,'syntheticDataOnly':True,'passed':all(r['status']=='PASS' for r in results),'results':results,'pageErrors':errors}
  (OUT/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
  print(json.dumps(summary,ensure_ascii=False,indent=2));ctx.close();b.close()
if not summary['passed']:raise SystemExit(1)
