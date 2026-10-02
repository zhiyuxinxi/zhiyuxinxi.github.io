"""Read-only visual candidate review on a real HTTP origin. All state is synthetic.
Captures useful first screens plus full-page task details, and verifies geometry,
keyboard dialog recovery, font scaling, themes, and non-distorting portrait motion.
Run: python tools/design_snapshots.py <site-root>. Never deploys or mutates user data.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
import json,sys,os,traceback
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
OUT=ROOT/'qa'/'design-candidate';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
results=[]
CASES=[
 ('workspace-empty','topic-workspace?topic=work-choice','default',390,'sunrise',False),
 ('record-saved','topic-workspace?topic=work-choice&id=topic-note-demo-v2','topic-record',390,'sunrise',False),
 ('record-saved-dark','topic-workspace?topic=work-choice&id=topic-note-demo-v2','topic-record',320,'nebula',True),
 ('action-review','action-detail?id=action-demo-v2','action-review',390,'sunrise',False),
 ('home','home','default',390,'sunrise',False),
 ('explore','explore','default',390,'sunrise',False),
 ('assistant','assistant','default',390,'sunrise',False),
 ('profile','me','default',390,'sunrise',False),
 ('topic','topic?id=work-choice','default',390,'sunrise',False),
 ('topic-resume','topic?id=work-choice','topic-record',390,'sunrise',False),
 ('report','report?id=report-sample-01','default',390,'sunrise',False),
 ('question','question?id=session-demo-seed','question',390,'sunrise',False),
 ('appearance','appearance','default',390,'sunrise',False),
 ('home-320','home','default',320,'sunrise',False),
 ('explore-320','explore','default',320,'sunrise',False),
 ('assistant-320','assistant','default',320,'sunrise',False),
 ('profile-320','me','default',320,'sunrise',False),
 ('report-320','report?id=report-sample-01','default',320,'sunrise',False),
 ('home-430','home','default',430,'sunrise',False),
 ('question-320','question?id=session-demo-seed','question',320,'sunrise',False),
 ('home-dark','home','default',390,'nebula',False),
 ('explore-dark','explore','default',390,'nebula',False),
 ('assistant-dark','assistant','source-login',390,'nebula',False),
 ('report-dark','report?id=report-sample-01','default',390,'nebula',False),
 ('appearance-dark','appearance','default',390,'amber',False),
 ('home-large','home','default',320,'sunrise',True),
 ('explore-large','explore','default',320,'sunrise',True),
 ('assistant-large','assistant','default',320,'sunrise',True),
 ('profile-large','me','default',320,'sunrise',True),
 ('question-large','question?id=session-demo-seed','question',320,'sunrise',True),
 ('report-large','report?id=report-sample-01','default',320,'sunrise',True),
]
def check(condition,message):
 if not condition:raise AssertionError(message)
with sync_playwright() as pw:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 browser=pw.chromium.launch(**args)
 for name,route,scenario,width,theme,large in CASES:
  ctx=browser.new_context(viewport={'width':width,'height':844},device_scale_factor=2,locale='zh-CN',reduced_motion='reduce')
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  row={'name':name,'route':route,'width':width,'theme':theme,'largeText':large}
  try:
   page.goto(f'{BASE}/prototype/index.html?reset=1&scenario={scenario}&theme={theme}#{route}',wait_until='networkidle')
   page.wait_for_function('window.App && App.snapshot')
   if large:
    page.evaluate("location.hash='settings'")
    page.wait_for_selector('[data-action="font-size"][data-id="large"]')
    page.click('[data-action="font-size"][data-id="large"]')
    page.evaluate("r=>location.hash=r",route)
    page.wait_for_function("r=>App.currentRoute===r",arg=route)
   page.wait_for_timeout(80)
   check(not errors,'Browser errors: '+str(errors))
   check(page.title().endswith('知遇测评'),'Page title has stale brand')
   check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Horizontal document overflow')
   check(page.locator('img').evaluate_all('(es)=>es.every(e=>e.complete&&e.naturalWidth>0)'),'Missing image')
   row['primaryActions']=page.locator('.btn:not(.secondary):not(.tonal)').evaluate_all('(es)=>es.filter(e=>e.getClientRects().length).map(e=>({text:e.textContent.trim(),height:e.getBoundingClientRect().height,y:e.getBoundingClientRect().y}))')
   if route in ['home','assistant']:
    logo=page.locator('.brand-logo');check(logo.count()==1,'Missing supplied brand image')
    check(logo.get_attribute('src')=='assets/zhiyu-logo.png','Wrong logo asset')
    check(logo.evaluate("e=>e.naturalWidth===940&&e.naturalHeight===940&&getComputedStyle(e).objectFit==='contain'&&getComputedStyle(e).filter==='none'"),'Logo distorted, recolored, or missing')
   if route=='home':
    check(page.locator('.wordmark strong').inner_text()=='知遇测评','Homepage wordmark is stale')
    mark=page.locator('.wordmark').bounding_box();tools=page.locator('.brandline .v3-tools').bounding_box();check(mark['x']+mark['width']<=tools['x'],'Four-character wordmark collides with tools')
    box=page.locator('.v4-person-scene img').bounding_box();check(box['width']>=160,'Approved portrait anchor too small')
    check(abs(box['x']+box['width']/2-(width-7)/2)<15,'Portrait not centered')
    check(page.locator('[data-action=start]').count()==1,'Primary assessment lost')
    check(page.locator('[data-action=start]').bounding_box()['y']<720,'Homepage start pushed too low')
   if route.startswith('topic?id='):
    primary=page.locator('.topic-start .btn');check(primary.bounding_box()['y']<670,'Topic start is below the main task area')
    check(not page.locator('.topic-outline').get_attribute('open'),'Outline must start collapsed')
    if scenario=='topic-record':check(primary.get_attribute('data-id')=='topic-note-demo-v2','Resume lost original record identity')
   if route.startswith('report'):
    check(page.locator('.factor-detail').get_attribute('open') is None,'Factor catalog must start collapsed')
    check('虚构' in page.locator('.report-identity').inner_text(),'Sample identity missing')
    page.click('[data-action=report-jump][data-id=report-personal]');check(page.locator('#report-note').is_visible(),'Personal note unreachable')
    check(page.locator('#report-note').bounding_box()['y']>=page.locator('.report-chapters').bounding_box()['height'],'Personal note obscured by chapter navigation')
    page.wait_for_function("document.querySelector('.report-chapters [aria-current=location]').dataset.id==='report-personal'")
    page.click('[data-action=report-jump][data-id=report-evidence]')
    page.wait_for_function("document.querySelector('.report-chapters [aria-current=location]').dataset.id==='report-evidence'")
    page.evaluate('scrollTo(0,0)')
    page.wait_for_function("document.querySelector('.report-chapters [aria-current=location]').dataset.id==='report-overview'")
   if route=='explore' and width==320:check(page.locator('.v3-topic-grid').evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length")==1,'Narrow explore did not become one column')
   page.screenshot(path=str(OUT/(name+'.png')))
   if name in ['topic','report','profile','appearance','workspace-empty','record-saved','record-saved-dark','action-review']:page.screenshot(path=str(OUT/(name+'-full.png')),full_page=True)
   row['status']='PASS'
  except Exception as e:
   row.update(status='FAIL',error=str(e),trace=traceback.format_exc(limit=3))
   if route.startswith('report'):
    row['reportGeometry']=page.evaluate("""() => ({scrollY, padding:getComputedStyle(document.documentElement).scrollPaddingTop, active:document.querySelector('.report-chapters [aria-current=location]')?.dataset.id, navEnd:document.querySelector('.report-chapters')?.getBoundingClientRect().bottom, sections:[...document.querySelectorAll('.report-block')].map(e=>({id:e.id,y:e.getBoundingClientRect().top,margin:getComputedStyle(e).scrollMarginTop}))})""")
   page.screenshot(path=str(OUT/(name+'-failure.png')),full_page=True)
  results.append(row);print(row['status'],name,row.get('error',''),flush=True);ctx.close()
 # The review shell shares the same unchanged supplied logo at desktop and phone widths.
 for shell_width in [1480,390]:
  ctx=browser.new_context(viewport={'width':shell_width,'height':1100},locale='zh-CN');page=ctx.new_page()
  try:
   page.goto(BASE+'/',wait_until='networkidle')
   check(page.locator('.brand b').inner_text()=='知遇测评','Workbench wordmark is stale')
   logo=page.locator('.brand-logo');check(logo.evaluate("e=>e.naturalWidth===940&&e.naturalHeight===940&&getComputedStyle(e).objectFit==='contain'"),'Workbench logo missing or distorted')
   name_box=page.locator('.brand').bounding_box();actions_box=page.locator('.head-actions').bounding_box();check(name_box['x']+name_box['width']<=actions_box['x'],'Workbench name collides with actions')
   page.screenshot(path=str(OUT/('workbench-brand-'+str(shell_width)+'.png')))
   results.append({'name':'workbench-brand-'+str(shell_width),'status':'PASS'})
  except Exception as e:results.append({'name':'workbench-brand-'+str(shell_width),'status':'FAIL','error':str(e)})
  ctx.close()
 # Verify whole character and headline stay still throughout a complete decorative cycle.
 ctx=browser.new_context(viewport={'width':390,'height':844},locale='zh-CN');page=ctx.new_page()
 try:
  page.goto(BASE+'/prototype/index.html?reset=1&scenario=default#home',wait_until='networkidle')
  targets=['.v4-person-scene img','.home-scene h2','.home-scene > .btn']
  sample=lambda:[page.locator(t).bounding_box() for t in targets]
  first=sample();previous=0
  for seconds in [3.5,7,14,21,28]:
   page.wait_for_timeout(int((seconds-previous)*1000));check(first==sample(),'Content moved during decorative breathing at '+str(seconds)+' seconds');previous=seconds
  page.locator('[data-action=v3-preferences]').focus();page.keyboard.press('Enter');page.wait_for_selector('.dialog')
  page.screenshot(path=str(OUT/'dialog-keyboard.png'));page.keyboard.press('Escape');check(page.locator('.dialog').count()==0,'Dialog failed Escape')
  check(page.evaluate("document.activeElement.dataset.action==='v3-preferences'"),'Dialog did not restore focus')
  results.append({'name':'motion-and-dialog-focus','status':'PASS'})
 except Exception as e:results.append({'name':'motion-and-dialog-focus','status':'FAIL','error':str(e)})
 ctx.close();browser.close()
report={'capturedAt':datetime.now(timezone.utc).isoformat(),'pass':all(x['status']=='PASS' for x in results),'results':results,'limits':['Emulated Chromium viewports; no physical Android/iOS keyboard or assistive-technology certification.']}
(OUT/'snapshot-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
server.shutdown()
if not report['pass']:raise SystemExit(1)
