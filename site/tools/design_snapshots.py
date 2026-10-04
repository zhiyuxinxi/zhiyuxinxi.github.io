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
from product_browser import ProductBrowser
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
OUT=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else ROOT/'qa'/'design-candidate';OUT.mkdir(parents=True,exist_ok=True)
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
 ('report-empty','report','default',390,'sunrise',False),
 ('home-resume','home','question',390,'sunrise',False),
 ('home-action','home','ongoing-action',390,'sunrise',False),
 ('settings','settings','default',390,'sunrise',False),
 ('explore','explore','default',390,'sunrise',False),
 ('assistant','assistant','default',390,'sunrise',False),
 ('profile','me','default',390,'sunrise',False),
 ('topic','topic?id=work-choice','default',390,'sunrise',False),
 ('topic-resume','topic?id=work-choice','topic-record',390,'sunrise',False),
 ('report','report?id=report-sample-01','sample-report',390,'sunrise',False),
 ('question','question?id=session-demo-seed','question',390,'sunrise',False),
 ('appearance','appearance','default',390,'sunrise',False),
 ('appearance-320','appearance','default',320,'sunrise',False),
 ('appearance-dark-320','appearance','default',320,'nebula',False),
 ('home-320','home','default',320,'sunrise',False),
 ('explore-320','explore','default',320,'sunrise',False),
 ('assistant-320','assistant','default',320,'sunrise',False),
 ('profile-320','me','default',320,'sunrise',False),
 ('report-320','report?id=report-sample-01','sample-report',320,'sunrise',False),
 ('home-430','home','default',430,'sunrise',False),
 ('question-320','question?id=session-demo-seed','question',320,'sunrise',False),
 ('home-dark','home','default',390,'nebula',False),
 ('explore-dark','explore','default',390,'nebula',False),
 ('assistant-dark','assistant','source-login',390,'nebula',False),
 ('report-dark','report?id=report-sample-01','sample-report',390,'nebula',False),
 ('appearance-dark','appearance','default',390,'amber',False),
 ('home-large','home','default',320,'sunrise',True),
 ('explore-large','explore','default',320,'sunrise',True),
 ('assistant-large','assistant','default',320,'sunrise',True),
 ('profile-large','me','default',320,'sunrise',True),
 ('question-large','question?id=session-demo-seed','question',320,'sunrise',True),
 ('report-large','report?id=report-sample-01','sample-report',320,'sunrise',True),
]
def check(condition,message):
 if not condition:raise AssertionError(message)
with sync_playwright() as pw:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 browser=pw.chromium.launch(**args)
 for name,route,scenario,width,theme,large in CASES:
  ctx=browser.new_context(viewport={'width':width,'height':844},device_scale_factor=2,locale='zh-CN',reduced_motion='reduce')
  page=ProductBrowser(ctx.new_page());errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  row={'name':name,'route':route,'width':width,'theme':theme,'largeText':large}
  try:
   page.open_product(BASE,route,scenario,theme)
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
   if route=='assistant':
    check(page.locator('main h1').inner_text()=='我的画像','Profile heading missing')
    check(page.locator('[data-action=profile-group]').count()==4,'Four profile groups missing')
    check(page.locator('.profile-radar').count()==0,'Unknown state fabricated a radar')
    check(page.locator('[data-route=assistant-chat]').count()>0,'Assistant continuation missing')
   check(page.locator('.brandline,.wordmark,.prototype-label').count()==0,'Removed product toolbar returned')
   check(page.locator('button[data-route=appearance]').count()==(1 if route=='settings' else 0),'Appearance bypasses personal settings')
   check(page.evaluate("getComputedStyle(document.getElementById('ambient-background')).backgroundImage.includes('gradient')"),'Global tidal background missing')
   if route=='home':
    box=page.locator('.v4-person-scene img').evaluate('(e)=>e.getBoundingClientRect().toJSON()');check(box['width']>=160,'Approved portrait anchor too small')
    check(abs(box['x']+box['width']/2-(width-7)/2)<15,'Portrait not centered')
    halo=page.locator('.v4-person-scene span').bounding_box();check(abs(halo['width']-halo['height'])<1 and 148<=halo['width']<=154,'Halo must be a restrained circle')
    check(page.locator('.home-scene h2').inner_text()=='16PF 性格探索','Assessment headline changed with unrelated activity')
    check(page.locator('.life-entry,.home-support,.v3-life,.v3-capture,.v3-editorial').count()==0,'Secondary catalog returned to home')
    check(page.locator('.home-path').count()==4,'Homepage lost the four secondary entries')
    primary=page.locator('.home-assessment-start');check(primary.count()==1,'Single assessment action missing');check(page.locator('.assessment-mode [data-action=mode]').count()==2,'Version choice missing')
    check(primary.bounding_box()['height']>=50,'Assessment touch target too small');check(primary.bounding_box()['y']<page.locator('.home-paths').bounding_box()['y'],'Secondary paths precede assessment');check(scenario!='default' or primary.is_disabled(),'Default unavailable state lost')
    if scenario=='question':check(primary.get_attribute('data-action')=='resume','Unfinished assessment lost priority')
    if scenario=='ongoing-action':check(page.locator('.v3-action-resume').count()==1,'Active attempt lost its continuation')
    nav=page.locator('.nav').evaluate('(e)=>e.getBoundingClientRect().toJSON()');check(nav['bottom']<=page.evaluate('innerHeight')+1,'Navigation left viewport')
    check(page.locator('.nav button').all_text_contents()==['认识','探索','我的画像','我的'],'Four entry roles changed')
   if route=='appearance':
    person=page.locator('.v4-live-preview>.v4-person-scene').bounding_box();halo=page.locator('.v4-live-preview>.v4-person-scene>span').bounding_box()
    check(abs(halo['width']-halo['height'])<1,'Preview halo is not circular')
    check(.84<=halo['width']/person['width']<=.88,'Preview halo does not scale with its portrait')
    check(abs(halo['x']+halo['width']/2-person['x']-person['width']/2)<1 and abs(halo['y']+halo['height']/2-person['y']-person['height']/2)<1,'Preview halo not centered')
    card=page.locator('.v4-live-preview').bounding_box();check(halo['x']>=card['x'] and halo['x']+halo['width']<=card['x']+card['width'] and halo['y']>=card['y'] and halo['y']+halo['height']<=card['y']+card['height'],'Preview halo clipped')
   if route.startswith('topic?id='):
    primary=page.locator('.topic-start .btn');check(primary.evaluate('(e)=>e.getBoundingClientRect().y')<670,'Topic start is below the main task area')
    check(not page.locator('.topic-outline').get_attribute('open'),'Outline must start collapsed')
    if scenario=='topic-record':check(primary.get_attribute('data-id')=='topic-note-demo-v2','Resume lost original record identity')
   if route=='report':
    check(page.locator('.factor-detail,.report-identity').count()==0,'Default report fabricated sample content');check(page.locator('[data-route=home]').count()>0,'Empty report lost recovery')
   if route.startswith('report?'):
    check(page.locator('.factor-detail').get_attribute('open') is None,'Factor catalog must start collapsed')
    check(page.evaluate('ProductContext.fixture') and '非本人资料' in page.host.locator('#stage-caption').inner_text(),'Explicit sample provenance missing')
    page.click('[data-action=report-jump][data-id=report-personal]');check(page.locator('#report-note').is_visible(),'Personal note unreachable')
    check(page.locator('#report-note').bounding_box()['y']>=page.locator('.report-chapters').bounding_box()['height'],'Personal note obscured by chapter navigation')
    page.wait_for_function("document.querySelector('.report-chapters [aria-current=location]').dataset.id==='report-personal'")
    page.click('[data-action=report-jump][data-id=report-evidence]')
    page.wait_for_function("document.querySelector('.report-chapters [aria-current=location]').dataset.id==='report-evidence'")
    page.evaluate('scrollTo(0,0)')
    page.wait_for_function("document.querySelector('.report-chapters [aria-current=location]').dataset.id==='report-overview'")
   if route=='explore' and width==320:check(page.locator('.v3-topic-grid').evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length")==1,'Narrow explore did not become one column')
   page.screenshot(path=str(OUT/(name+'.png')))
   if name in ['explore','assistant','settings','home-resume','home-action','topic','report','profile','appearance','workspace-empty','record-saved','record-saved-dark','action-review']:page.screenshot(path=str(OUT/(name+'-full.png')),full_page=True)
   row['status']='PASS'
  except Exception as e:
   row.update(status='FAIL',error=str(e),trace=traceback.format_exc(limit=3))
   if route.startswith('report'):
    row['reportGeometry']=page.evaluate("""() => ({scrollY, padding:getComputedStyle(document.documentElement).scrollPaddingTop, active:document.querySelector('.report-chapters [aria-current=location]')?.dataset.id, navEnd:document.querySelector('.report-chapters')?.getBoundingClientRect().bottom, sections:[...document.querySelectorAll('.report-block')].map(e=>({id:e.id,y:e.getBoundingClientRect().top,margin:getComputedStyle(e).scrollMarginTop}))})""")
   page.screenshot(path=str(OUT/(name+'-failure.png')),full_page=True)
  results.append(row);print(row['status'],name,row.get('error',''),flush=True);ctx.close()
 # Narrow dark dialog uses the real personal settings entry and preserves focus.
 ctx=browser.new_context(viewport={'width':320,'height':844},locale='zh-CN',reduced_motion='reduce');page=ctx.new_page()
 try:
  page.goto(BASE+'/prototype/index.html?reset=1&scenario=default&theme=nebula#me',wait_until='networkidle')
  page.click('[data-route=settings]');page.locator('[data-action=v3-preferences]').focus();page.keyboard.press('Enter');page.wait_for_selector('.dialog')
  check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Narrow dark dialog overflows')
  box=page.locator('.dialog').bounding_box();check(box['x']>=0 and box['y']>=0 and box['x']+box['width']<=320,'Narrow dark dialog clipped')
  page.screenshot(path=str(OUT/'settings-dialog-dark-320.png'));page.keyboard.press('Escape')
  check(page.locator('.dialog').count()==0 and page.evaluate("document.activeElement.dataset.action==='v3-preferences'"),'Dark dialog did not restore settings focus')
  results.append({'name':'settings-dialog-dark-320','status':'PASS'})
 except Exception as e:results.append({'name':'settings-dialog-dark-320','status':'FAIL','error':str(e)})
 ctx.close()
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
  targets=['.v4-person-scene img','.home-scene h2','.home-assessment-start']
  sample=lambda:[page.locator(t).first.bounding_box() for t in targets]
  first=sample();previous=0
  for seconds in [3.5,7,14,21,28]:
   page.wait_for_timeout(int((seconds-previous)*1000));check(first==sample(),'Content moved during decorative breathing at '+str(seconds)+' seconds');previous=seconds
  page.click('[data-action=tab][data-route=me]');page.click('[data-route=settings]');page.locator('[data-action=v3-preferences]').focus();page.keyboard.press('Enter');page.wait_for_selector('.dialog')
  page.screenshot(path=str(OUT/'dialog-keyboard.png'));page.keyboard.press('Escape');check(page.locator('.dialog').count()==0,'Dialog failed Escape')
  check(page.evaluate("document.activeElement.dataset.action==='v3-preferences'"),'Dialog did not restore focus')
  results.append({'name':'motion-and-dialog-focus','status':'PASS'})
 except Exception as e:results.append({'name':'motion-and-dialog-focus','status':'FAIL','error':str(e)})
 ctx.close();browser.close()
report={'capturedAt':datetime.now(timezone.utc).isoformat(),'pass':all(x['status']=='PASS' for x in results),'results':results,'limits':['Emulated Chromium viewports; no physical Android/iOS keyboard or assistive-technology certification.']}
(OUT/'snapshot-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
server.shutdown()
if not report['pass']:raise SystemExit(1)
