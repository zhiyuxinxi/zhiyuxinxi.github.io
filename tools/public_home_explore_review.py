"""Public, data-free home/explore verification; works with a local HTTP base too."""
import argparse,json,os,subprocess,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
report={'url':a.url,'verifiedCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'passed':False,'checks':[]};errors=[]
try:
 with sync_playwright() as w:
  launch={'headless':True,'args':['--no-sandbox']}
  if os.environ.get('CHROMIUM_PATH'):launch['executable_path']=os.environ['CHROMIUM_PATH']
  b=w.chromium.launch(**launch);c=b.new_context(viewport={'width':1480,'height':1100});p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
  for mode in ['workbench','standalone']:
   p.set_viewport_size({'width':1480,'height':1100} if mode=='workbench' else {'width':390,'height':844})
   p.goto(a.url.rstrip('/')+('/?public_home_explore=1#page=home' if mode=='workbench' else '/prototype/index.html?reset=1#home'),wait_until='networkidle')
   if mode=='workbench':
    p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");f=p.locator('#product-frame').element_handle().content_frame()
   else:f=p
   f.wait_for_function('window.App&&window.Ambient');original=f.locator('.assessment-purpose').inner_text();f.locator('[data-action=mode][data-id=ai]').click();ai=f.locator('.assessment-purpose').inner_text();assert original!=ai and 'AI辅助重写题目与选项' in ai;assert f.locator('.home-assessment-start').is_disabled()
   assert f.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
   p.screenshot(path=str(out/(mode+'-home-ai.png')))
   f.evaluate('window.beforeCanvas=document.querySelector("#ambient-tide");window.beforeClock=Ambient.getTime()');f.locator('[data-action=tab][data-route=explore]').click();f.wait_for_function('App.currentRoute==="explore"');assert f.evaluate('beforeCanvas===document.querySelector("#ambient-tide")&&Ambient.getTime()>=beforeClock')
   intro=f.locator('.explore-intro');assert intro.is_visible();assert intro.locator('button,a').count()==0;assert intro.evaluate('e=>parseFloat(getComputedStyle(e).paddingTop)>0&&parseFloat(getComputedStyle(e).borderTopWidth)>0')
   assert f.locator('.decision-card').count()==8 and f.locator('.decision-symbol svg').count()==8;assert f.locator('#topic-search-panel').is_hidden();p.screenshot(path=str(out/(mode+'-explore.png')))
   f.locator('[data-action=category][data-id="学业"]').click();assert f.locator('.decision-card').count()==1
   f.locator('[data-action=toggle-topic-search]').click();inp=f.locator('#explore-search');inp.fill('读研');assert f.locator('.decision-card').evaluate_all('(es)=>es.map(e=>e.dataset.id)')==['exam-retake']
   f.locator('[data-action=category][data-id="生活"]').click();assert f.locator('.decision-card').count()==0
   f.locator('[data-action=clear-search]').click();assert inp.input_value()=='' and inp.evaluate('e=>e===document.activeElement');f.locator('[data-action=category][data-id="全部"]').click();assert f.locator('.decision-card').count()==8
   requests=[];p.on('request',lambda r:requests.append(r.url));c.set_offline(True);inp.fill('考研');assert f.locator('.decision-card').count()==1;assert not requests;assert f.evaluate('Object.keys(localStorage).filter(k=>k.startsWith("jianji-design-v4:")).every(k=>JSON.parse(localStorage.getItem(k)).exploreSearch==="")');c.set_offline(False)
   p.screenshot(path=str(out/(mode+'-search.png')));p.emulate_media(reduced_motion='reduce');f.wait_for_function('Ambient.isPaused()');p.emulate_media(reduced_motion='no-preference')
   report['checks'].append({'entry':mode,'versionCopy':True,'introContainer':True,'eightCards':True,'categoryIntersection':True,'localAliasSearch':True,'clearFocus':True,'noSearchRequests':True,'queryNotPersisted':True,'ambientContinuity':True,'reducedMotion':True})
  assert not errors,errors;report['passed']=True;b.close()
except Exception as e:report.update(error=str(e),traceback=traceback.format_exc())
report['pageErrors']=errors;(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));raise SystemExit(0 if report['passed'] else 1)
