"""Native-origin publication gate. Uses a real HTTP server, real resource loading and native localStorage.
Run: python tools/hosted_smoke.py <site-root>. Requires Playwright Chromium.
Failure raises a nonzero exit code and blocks deployment. All test data are synthetic.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
from importlib.metadata import version
import json,sys,os,traceback,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=ROOT/'qa';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
RESULTS=[]
def check(x,msg='Assertion failed'):
 if not x:raise AssertionError(msg)
def proto(p,route='home',scenario='default',theme='sunrise'):
 p.goto(f'{BASE}/prototype/index.html?reset=1&scenario={scenario}&theme={theme}#{route}',wait_until='networkidle');p.wait_for_function('window.App && App.snapshot');return p

def root_and_resources(p):
 responses=[];p.on('response',lambda r:responses.append((r.url,r.status)));p.goto(BASE+'/',wait_until='networkidle');p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')")
 check(p.locator('[role=tree]').count()==1);f=p.frame_locator('#product-frame');check(f.locator('[data-action=start]').count()==1);check(not[(u,s)for u,s in responses if s>=400],str(responses));check(len(p.locator('#theme-select option').all())==12)

def bridge_and_themes(p):
 root_and_resources(p);p.select_option('#theme-select','nebula');f=p.locator('#product-frame').element_handle().content_frame();f.wait_for_function('App.snapshot.theme==="nebula"');check(f.evaluate('innerWidth')==390,'Wrong actual preview width');p.select_option('#width-select','320');f.wait_for_function('innerWidth===320');p.click('#density-button');f.wait_for_function('App.snapshot.density==="compact"');p.click('#motion-button');f.wait_for_function('App.snapshot.reduced');p.click('[data-folder=personal]');p.click('[data-page=appearance]');f.wait_for_function('App.currentRoute==="appearance"');check(f.locator('.v4-theme-card').count()==12)

def tree_keyboard_and_search(p):
 root_and_resources(p);p.locator('[data-folder=core]').focus();p.keyboard.press('ArrowRight');p.keyboard.press('ArrowDown');check(p.evaluate('document.activeElement.dataset.page')=='explore');p.keyboard.press('Enter');f=p.locator('#product-frame').element_handle().content_frame();f.wait_for_function('App.currentRoute==="explore"');p.fill('#tree-search','订单');check(p.locator('[data-page=orders]').is_visible());p.click('#clear-search');check(p.evaluate('document.activeElement.id')=='tree-search');p.click('[data-folder=assist]');p.click('[data-page=skills]');check(p.locator('#panel-contract').is_visible());check('无独立' in p.locator('#panel-contract').inner_text()or'没有用空壳页面' in p.locator('#panel-contract').inner_text())

def blocked_scene_reload(p):
 root_and_resources(p);p.select_option('#scene-select','save-failure');f=p.locator('#product-frame').element_handle().content_frame();f.wait_for_function('App.currentRoute.startsWith("question")');f.click('[data-action=answer][data-id=c]');check(f.locator('[data-action=question-next]').is_disabled());p.select_option('#scene-select','default');p.wait_for_selector('.wb-dialog');check('未保存' in p.locator('.wb-dialog').inner_text());check(f.evaluate('App.pendingAnswer.choice')=='c');p.click('#wb-close');f.click('[data-action=retry-save]');check(not f.locator('[data-action=question-next]').is_disabled())

def native_persistence(p):
 proto(p,'journal');p.fill('#journal-text','发布门禁：本机草稿的重载恢复');p.reload(wait_until='networkidle');check(p.locator('#journal-text').input_value()=='发布门禁：本机草稿的重载恢复');p.click('[data-action=save-journal]');p.reload(wait_until='networkidle');s=p.evaluate('App.snapshot');check(len(s['observations'])==1);check(s['observations'][0]['text']=='发布门禁：本机草稿的重载恢复')

def cross_window_conflict(p):
 proto(p,'journal');q=p.context.new_page();q.goto(BASE+'/prototype/index.html?scenario=default#journal',wait_until='networkidle');q.fill('#journal-text','来自第二个窗口的最新内容');q.click('[data-action=save-journal]');p.wait_for_function('App.externalChange===true');before=q.evaluate('localStorage.getItem(App.storageKey)');p.fill('#journal-text','第一个窗口的未提交内容');p.click('[data-action=save-journal]');check(q.evaluate('localStorage.getItem(App.storageKey)')==before,'Stale window overwrote newer data');check('另一个页面' in p.locator('#storage-status').inner_text());q.close()

def sample_boundaries_and_answer(p):
 proto(p);p.click('[data-action=start]');
 for choice in ['a','b','c']:p.click('[data-action=answer][data-id='+choice+']');p.click('[data-action=question-next]')
 p.click('[data-action=finish]');s=p.evaluate('App.snapshot');check(s['sessions'][0]['status']=='completed');check('score'not in s['sessions'][0]);p.evaluate("location.hash='report?id=report-sample-01'");p.wait_for_selector('.report-identity');check('虚构' in p.locator('.report-identity').inner_text());check(p.locator('[data-action=factor]').count()==16);p.click('[data-action=quote-report]');check(not p.evaluate('App.snapshot.conversations.length'));check('虚构样例' in p.locator('body').inner_text())

def topic_roundtrip(p):
 proto(p,'topic-workspace?topic=work-choice');p.fill('#topic-options','选择A或B');p.fill('#topic-limits','发布门禁：保留原字段');p.click('[data-action=topic-save]');before=p.evaluate('App.snapshot.observations[0]');p.click('[data-action=topic-edit]');p.fill('#topic-options','重新比较A与B');p.click('[data-action=topic-save]');after=p.evaluate('App.snapshot.observations[0]');check(before['id']==after['id'] and after['revision']==2);check(after['fields']['limits']=='发布门禁：保留原字段');p.click('[data-action=topic-to-assistant]');check(p.evaluate('App.snapshot.assistantSources[0].objectId')==after['id'])

def real_problem_loop(p):
 shots=OUT/'record-loop-screenshots';shots.mkdir(exist_ok=True)
 proto(p,'explore');p.click('.life-entry [data-route="topic-workspace"]');p.wait_for_selector('#topic-issue');check(not p.evaluate('App.snapshot.logged'));check(p.evaluate('App.snapshot.sessions.length')==0)
 p.click('[data-action=topic-save]');check(p.locator('#topic-error').is_visible());check(p.evaluate('App.snapshot.observations.length')==0)
 p.fill('#topic-issue','下次讨论，先独立准备还是先交流？');p.fill('#topic-options','先写两点；先问一个问题');p.fill('#topic-evidence','上次写两点后容易开始，但还没排除话题熟悉度');p.fill('#topic-unknown','换个话题会怎样？');p.fill('#topic-understanding','先试一个低成本变化，不急着定论');p.reload(wait_until='networkidle');check(p.input_value('#topic-issue').startswith('下次讨论'))
 p.click('[data-action=topic-save]');n=p.evaluate('App.snapshot.observations[0]');check(p.locator('.record-summary').is_visible());p.wait_for_timeout(4500);p.screenshot(path=str(shots/'record-saved.png'),full_page=True);check(p.locator('.record-editor').get_attribute('open') is None);p.click('[data-action=add-action]');p.fill('#dialog-field','讨论前写两点，观察是否容易开始');p.click('[data-action=submit-dialog]');a=p.evaluate('App.snapshot.actions[0]');check(a['sourceId']==n['id'] and a['sourceVersion']=='1');check(a['sourceSnapshot']['version']=='1');p.wait_for_timeout(4500);p.screenshot(path=str(shots/'action-origin.png'),full_page=True)
 p.click('[data-action=action-outcome][data-outcome=partial]');p.fill('#action-observation','只试了一点，暂时不能判断');p.click('[data-action=save-action-review]');check(p.locator('.action-latest').is_visible());p.wait_for_timeout(4500);p.screenshot(path=str(shots/'action-review.png'),full_page=True);check(p.evaluate('App.snapshot.actions[0].reviews[0].actionText')==a['text'])
 p.click('.action-origin [data-route="topic-workspace"]');check(p.evaluate("({id})=>{const [route,q]=App.currentRoute.split('?');const params=new URLSearchParams(q);return route==='topic-workspace'&&params.get('id')===id&&params.get('topic')==='work-choice'}",{'id':n['id']}),'Return must retain topic and original record ID');p.click('[data-action=topic-edit]');p.fill('#topic-issue','补上讨论对象这个条件');p.click('[data-action=topic-save]');p.reload(wait_until='networkidle');n2=p.evaluate('App.snapshot.observations[0]');check(n2['id']==n['id'] and n2['revision']==2);check(n2['revisions'][0]['fields']==n['fields']);check(p.evaluate('App.snapshot.actions[0].sourceSnapshot')==a['sourceSnapshot'])
 p.click('[data-action=topic-edit]');p.fill('#topic-issue','这是未正式保存的新草稿');p.click('[data-action=topic-to-assistant]');check(p.locator('#dialog-title').inner_text()=='先选择采用哪个版本');check(p.evaluate('App.snapshot.assistantSources.length')==0);p.click('[data-action=topic-attach-saved]');check(p.evaluate('App.snapshot.assistantSources[0].version')=='2');check('未正式保存' not in p.evaluate('App.snapshot.assistantSources[0].excerpt'));check(p.evaluate('App.snapshot.conversations.length')==0);check(not p.evaluate('App.snapshot.logged'))
 return {'recordIdStable':True,'sourceRevisionImmutable':True,'noAssessmentOrLoginRequired':True,'unresolvedAccepted':True}

def record_failure_and_legacy(p):
 proto(p,'topic-workspace?topic=work-choice&id=topic-note-demo-v2','topic-record');old=p.evaluate('App.snapshot.observations[0]');p.click('[data-action=topic-edit]');check(p.input_value('#topic-issue')=='');check(p.input_value('#topic-options')==old['fields']['options']);p.click('[data-action=topic-save]');check(p.evaluate('App.snapshot.observations[0].revision')==1)
 p.click('[data-action=topic-edit]');p.context.set_offline(True);p.fill('#topic-evidence','离线补充的本人观察');p.click('[data-action=topic-save]');check(p.evaluate('App.snapshot.observations[0].revision')==2);p.context.set_offline(False);p.reload(wait_until='networkidle');check(p.evaluate('App.snapshot.observations[0].fields.options')==old['fields']['options']);p.click('[data-action=topic-edit]')
 p.evaluate("()=>{window.originalSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new Error('synthetic-storage-full')};}");p.fill('#topic-issue','写入失败也不能丢掉');p.click('[data-action=topic-save]');check(p.evaluate('App.snapshot.observations[0].revision')==2);check(p.input_value('#topic-issue')=='写入失败也不能丢掉');check('尚未保存' in p.locator('#storage-status').inner_text());p.evaluate('()=>{Storage.prototype.setItem=window.originalSetItem;}');p.click('[data-action=retry-drafts]');p.click('[data-action=topic-save]');check(p.evaluate('App.snapshot.observations[0].revision')==3)
 return {'oldFieldsPreserved':True,'offlineLocalSave':True,'failedWriteRecoverable':True}

def record_snapshot_privacy(p):
 proto(p,'topic-workspace?topic=work-choice');secret='合成私密来源不应随取消范围导出';p.fill('#topic-issue',secret);p.fill('#topic-options','选择A或B');p.click('[data-action=topic-save]');nid=p.evaluate('App.snapshot.observations[0].id');p.click('[data-action=add-action]');p.fill('#dialog-field','只观察一次');p.click('[data-action=submit-dialog]');aid=p.evaluate('App.snapshot.actions[0].id')
 p.evaluate("location.hash='data'");p.wait_for_selector('[data-action=export-preview]');p.click('[data-action=export-preview]');p.uncheck('[name=export-group][value=notes]')
 with p.expect_download() as download:p.click('[data-action=export-data]')
 exported=json.loads(Path(download.value.path()).read_text());check('observations' not in exported);check('sourceSnapshot' not in exported['actions'][0]);check(secret not in json.dumps(exported,ensure_ascii=False));check(p.evaluate('App.snapshot.actions[0].sourceSnapshot.excerpt').find(secret)>=0,'Export mutated local source')
 p.evaluate("r=>location.hash=r",'topic-workspace?topic=work-choice&id='+nid);p.wait_for_selector('[data-action=delete-journal]');p.click('[data-action=delete-journal]');p.click('[data-action=confirm-dialog]');check(p.evaluate('App.snapshot.observations.length')==0);check(p.evaluate('App.snapshot.actions.length')==1);check(p.evaluate('App.snapshot.actions[0].sourceSnapshot===undefined'));check(secret not in p.evaluate('localStorage.getItem(App.storageKey)'))
 p.evaluate("r=>location.hash=r",'action-detail?id='+aid);p.wait_for_selector('.action-origin');check('来源全文已删除' in p.locator('.action-origin').inner_text());check(secret not in p.locator('body').inner_text());p.reload(wait_until='networkidle');check(secret not in p.locator('body').inner_text())
 return {'exportSelectionHonored':True,'deletedSourcePlaintextRemoved':True,'actionRetained':True}

def original_order(p):
 proto(p,'order?id=DEMO-ANNUAL-001','paid-annual');check('年方案' in p.locator('.order-heading').inner_text());check(p.evaluate('App.snapshot.plan')=='monthly');check(p.evaluate('App.snapshot.orders[0].plan')=='annual')

def gallery_isolation(p):
 root_and_resources(p);f=p.locator('#product-frame').element_handle().content_frame();key=f.evaluate('App.storageKey');before=f.evaluate('localStorage.getItem(App.storageKey)');p.click('[data-mode=themes]');check(p.locator('#theme-gallery iframe').count()==8);gf=p.locator('#theme-gallery iframe').first.element_handle().content_frame();gf.wait_for_function('window.App&&App.snapshot');check(gf.evaluate('App.storageKey')!=key);check(f.evaluate('localStorage.getItem(App.storageKey)')==before,'Gallery changed main storage');p.click('[data-use-theme=sea]');f.wait_for_function('App.snapshot.theme==="sea"');check(p.locator('#panel-preview').is_visible())

def persona_and_settings(p):
 proto(p,'appearance');check(p.locator('.v4-avatar-options img').count()==6);p.click('[data-action=avatar][data-id="3"][data-family=scene]');p.click('[data-action=theme][data-id=amber]');p.reload(wait_until='networkidle');check(p.evaluate('App.snapshot.avatarFamily')=='scene');check(p.evaluate('App.snapshot.avatar')==3);check(p.evaluate('App.snapshot.theme')=='amber','Theme reverted on reload');p.click('[data-action=avatar][data-id="2"][data-family=original]');p.evaluate("location.hash='home'");p.wait_for_selector('.v4-person-scene img');check('original-person-2.webp' in p.locator('.v4-person-scene img').get_attribute('src'))

def relocated_entries_and_settings(p):
 proto(p)
 check(p.locator('.brandline,.wordmark,.prototype-label').count()==0)
 check(p.locator('button[data-route=appearance]').count()==0)
 p.click('[data-action=tab][data-route=explore]')
 p.locator('.explore-tools summary').click()
 p.click('[data-action=daily]');check('每日轻探索' in p.locator('.dialog').inner_text());p.keyboard.press('Escape')
 p.click('[data-action=all-factors]');check(p.locator('.dialog .bottle-tile').count()==16);p.keyboard.press('Escape')
 for route in ['simulation','report','article']:
  p.click('.explore-tools [data-route='+route+']');p.wait_for_function('r=>App.currentRoute.startsWith(r)',arg=route)
  check(p.locator('[data-action=back]').count()>=1,'Task return lost')
  p.click('[data-action=back]');p.wait_for_function('App.currentRoute==="explore"');p.locator('.explore-tools summary').click()
 p.click('[data-action=tab][data-route=me]');p.click('[data-route=settings]');p.click('[data-route=appearance]')
 p.click('[data-action=theme][data-id=nebula]');p.click('[data-action=back]');p.wait_for_function('App.currentRoute==="settings"')
 p.click('[data-action=v3-preferences]');p.click('[data-action=v3-motion]');p.keyboard.press('Escape')
 check(p.evaluate("document.activeElement.dataset.action==='v3-preferences'"),'Settings dialog focus lost')
 check(p.evaluate('App.snapshot.reduced'),'Motion preference not saved')
 check(p.evaluate("document.getElementById('ambient-tide').animationsPaused()"),'Reduced motion did not stop global tide')
 p.click('[data-action=back]');p.wait_for_function('App.currentRoute==="me"')
 p.click('[data-route=records]');check('记录' in p.locator('main').inner_text())
 return {'movedToolsReachable':True,'settingsOnlyAppearanceEntry':True,'darkDialogKeyboardRecovery':True}

def home_state_priority(p):
 for scenario,action in [('ongoing-action','start'),('combined','resume'),('complete','nav')]:
  proto(p,'home',scenario)
  check(p.locator('.home-scene h2').inner_text()=='16PF 性格探索')
  primary=p.locator('.home-primary').first;check(primary.get_attribute('data-action')==action)
  check(p.locator('.v3-action-resume').count()==(0 if scenario=='complete' else 1))
  (OUT/'design-candidate').mkdir(exist_ok=True);p.screenshot(path=str(OUT/'design-candidate'/('home-'+scenario+'.png')))
  primary.click()
  p.wait_for_function("r=>App.currentRoute.startsWith(r)",arg='review?' if scenario=='complete' else 'question?')
  if scenario!='ongoing-action':check('session-demo-seed' in p.evaluate('App.currentRoute'),'Original answer ID lost')
 return {'firstWithAction':'start','combined':'resume','completed':'original review','stableHeadline':True}

def route_matrix(p):
 paths=json.loads((ROOT/'handoff/routes.json').read_text());visited=0
 for r in paths:
  if not r.get('route'):continue
  proto(p,r['route'],r.get('scenario','default'),'nebula');check(p.locator('.brandline,.wordmark,.prototype-label').count()==0,'Removed toolbar returned on '+r['id']);check(p.locator('#main-content').count()==1,r['id']);check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),r['id']+' horizontal overflow');visited+=1
 return {'route_mappings':visited,'scope':'Valid named fixture IDs. Native page rendering, console and overflow checks; not full backend actions.'}

def theme_six_page_matrix(p):
 rows=[]
 for theme in ['sunrise','candy','berry','lime','aurora','sea','nebula','amber']:
  for r,sc in [('home','default'),('explore','default'),('question?id=session-demo-seed','question'),('report?id=report-sample-01','default'),('assistant','default'),('me','default')]:
   proto(p,r,sc,theme);check(p.evaluate('App.snapshot.theme')==theme);check(p.evaluate("getComputedStyle(document.getElementById('ambient-background')).backgroundImage.includes('gradient')"),'Missing global scene');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),theme+' '+r);check(p.locator('#main-content').count()==1);imgs=p.locator('img').evaluate_all('(es)=>es.filter(e=>!e.complete||e.naturalWidth===0).map(e=>e.src)');check(not imgs,'Missing images '+str(imgs));rows.append({'theme':theme,'page':r,'pass':True})
 (OUT/'hosted-theme-matrix.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));return {'combinations':len(rows)}

def run(pw,browser,name,fn,size=(390,844)):
 context=browser.new_context(viewport={'width':size[0],'height':size[1]},locale='zh-CN');p=context.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 try:detail=fn(p);check(not errors,str(errors));r={'test':name,'status':'PASS','details':detail or {}}
 except Exception as e:
  r={'test':name,'status':'FAIL','error':str(e),'trace':traceback.format_exc(limit=3)};(OUT/'hosted-failures').mkdir(exist_ok=True);p.screenshot(path=str(OUT/'hosted-failures'/f'{name}.png'),full_page=True)
 RESULTS.append(r);print(r['status'],name,r.get('error',''),flush=True);context.close()
with sync_playwright() as pw:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=pw.chromium.launch(**args);browser_version=b.version
 for name,fn in [('root_resources',root_and_resources),('bridge_theme_width_density',bridge_and_themes),('tree_keyboard_search_specs',tree_keyboard_and_search),('unsaved_scene_guard',blocked_scene_reload),('native_reload_persistence',native_persistence),('native_cross_window_guard',cross_window_conflict),('answer_sample_boundaries',sample_boundaries_and_answer),('topic_edit_source_roundtrip',topic_roundtrip),('real_problem_record_action_review',real_problem_loop),('record_failure_legacy_offline',record_failure_and_legacy),('record_snapshot_export_delete_scope',record_snapshot_privacy),('original_order_snapshot',original_order),('theme_gallery_isolation',gallery_isolation),('persona_setting_independence',persona_and_settings),('relocated_entries_and_settings',relocated_entries_and_settings),('home_state_priority',home_state_priority),('route_mappings',route_matrix),('eight_themes_six_pages',theme_six_page_matrix)]:run(pw,b,name,fn,(1480,1100)if name in ['root_resources','bridge_theme_width_density','tree_keyboard_search_specs','unsaved_scene_guard','theme_gallery_isolation']else(390,844))
 # Native images are evidence only, all data synthetic.
 c=b.new_context(viewport={'width':1500,'height':1280});p=c.new_page();p.goto(BASE+'/',wait_until='networkidle');p.wait_for_timeout(500);(OUT/'hosted-screenshots').mkdir(exist_ok=True);p.screenshot(path=str(OUT/'hosted-screenshots/workbench.png'));c.close();b.close()
summary={'version':'4.0.0-preservation','environment':('GitHub Actions' if os.environ.get('GITHUB_ACTIONS') else 'Local workspace')+' / real HTTP resource loading / native Chromium localStorage and iframe messaging','timestampUTC':datetime.now(timezone.utc).isoformat(),'browser':browser_version,'playwright':version('playwright'),'passed':sum(x['status']=='PASS'for x in RESULTS),'failed':sum(x['status']=='FAIL'for x in RESULTS),'results':RESULTS,'notVerified':['Actual end-user browser/network','Android/iOS devices and soft keyboards','Real 16PF scoring/norms','Real model/auth/payment/sync','Complete WCAG audit','Target-user preference'], 'sourceEntrySHA256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()}
(OUT/'hosted-smoke.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('NATIVE HTTP GATE',summary['passed'],'PASS',summary['failed'],'FAIL');server.shutdown();sys.exit(1 if summary['failed']else 0)
