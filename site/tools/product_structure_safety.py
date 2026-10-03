"""Current product structure browser regression. Synthetic local records only; no real services or publication.
Run with site root and optional evidence directory; historical test reports do not substitute for this check.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,re,time,os,sys
R=Path(sys.argv[1] if len(sys.argv)>1 else 'site').resolve();O=Path(sys.argv[2] if len(sys.argv)>2 else str(R/'qa/product-structure')).resolve();(O/'screenshots').mkdir(parents=True,exist_ok=True)
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(R)));Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_port}'
results=[];errors=[];matrix=[];copy=[]
def check(v,m):
 if not v:raise AssertionError(m)
def test(n,fn):
 try:result=fn();results.append(dict(test=n,status='PASS',details=result))
 except Exception as e:results.append(dict(test=n,status='FAIL',error=str(e)))
 print(n,results[-1]['status'],results[-1].get('error',''),flush=True)
import hashlib,os
with sync_playwright() as w:
 b=w.chromium.launch(**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}),args=['--no-sandbox']);c=b.new_context(viewport={'width':390,'height':844});p=c.new_page();p.set_default_timeout(6000)
 def go(r='home',reset=False):
  p.goto(url+'/prototype/index.html?theme=lime'+('&reset=1' if reset else '')+'#'+r);p.wait_for_function('window.App&&window.Ambient')
 def nav(r):p.evaluate('r=>location.hash=r',r);p.wait_for_function('r=>decodeURIComponent(App.currentRoute)===r',arg=r)
 def continuity():
  go(reset=True);p.evaluate('window.canvasBefore=document.getElementById("ambient-tide"); Ambient.sample(8);Ambient.resume()');start=p.evaluate('Ambient.getTime()');p.wait_for_timeout(450);events=[]
  for r in ['explore','assistant','relationship-detail?id=D1','observation-area?id=values','assistant-chat','home']:
   nav(r);events.append({'route':r,'time':p.evaluate('Ambient.getTime()'),'motion':p.locator('#ambient-background').get_attribute('data-motion')});check(p.evaluate('canvasBefore===document.getElementById("ambient-tide")'),'canvas replaced');check(p.evaluate('Ambient.getTime()')>=start,'time restarted');p.wait_for_timeout(180)
  nav('question');t=p.evaluate('Ambient.getTime()');p.wait_for_timeout(300);check(p.evaluate('Ambient.isPaused() && Ambient.getTime()=== '+str(t)),'question not quiet');nav('home');p.emulate_media(reduced_motion='reduce');t=p.evaluate('Ambient.getTime()');image1=p.locator('#ambient-tide').screenshot();p.wait_for_timeout(300);check(p.evaluate('Ambient.isPaused()'),'motion preference');check(image1==p.locator('#ambient-tide').screenshot(),'reduced frame changed');p.emulate_media(reduced_motion='no-preference');return events
 test('canvas-identity-clock-question-and-reduced-motion',continuity)
 def area():
  go(reset=True);ratios=[]
  for sec in [0,4,8,12,16,20,24,28,32]:
   v=p.evaluate('''t=>{Ambient.sample(t);const c=document.getElementById('ambient-tide'),v=c.getContext('2d').getImageData(0,0,c.width,c.height).data,s=getComputedStyle(document.body),rgb=h=>h.match(/[a-f\\d]{2}/gi).map(n=>parseInt(n,16)),a=rgb(s.getPropertyValue('--field-a').trim()),b=rgb(s.getPropertyValue('--field-b').trim());let n=0;for(let i=0;i<v.length;i+=4){const d=c=>c.reduce((s,x,k)=>s+(v[i+k]-x)**2,0);if(d(a)<d(b))n++;}return n/(v.length/4);}''',sec);ratios.append({'seconds':sec,'colorA':v});check(.14<=v<=.86,'area outside envelope')
  check(max(x['colorA'] for x in ratios)>.8 and min(x['colorA'] for x in ratios)<.2,'insufficient span');p.evaluate('Ambient.resume()');return ratios
 test('retained-two-color-area-envelope',area)
 def focus_and_long():
  go(reset=True);p.locator('[data-action=mode][data-id=ai]').focus();p.keyboard.press('Enter');check(p.evaluate("document.activeElement.dataset.id==='ai'"),'mode focus');nav('assistant');p.locator('[data-action=profile-group][data-id=relationships]').focus();p.keyboard.press('Space');check(p.evaluate("document.activeElement.dataset.id==='relationships'"),'group focus');nav('settings');p.locator('[data-action=font-size][data-id=large]').click();p.set_viewport_size({'width':320,'height':740});nav('explore');check(p.locator('.decision-card').evaluate_all('(es)=>es.every(e=>e.scrollHeight<=e.clientHeight+2)'),'large text clipping');p.screenshot(path=str(O/'screenshots/large-320-explore.png'),full_page=True)
  nav('journal?kind=relationship:D3:boundary');p.locator('#journal-text').fill('需要留意双方的时间和边界。'*230);p.locator('[data-action=save-journal]').focus();p.keyboard.press('Enter');check(len(p.evaluate('App.snapshot.observations[0].text'))>2000,'long save');p.reload();check(len(p.evaluate('App.snapshot.observations[0].text'))>2000,'reload');check(not p.evaluate('document.documentElement.scrollWidth>innerWidth'),'overflow');return {'keyboardFocus':True,'largeText':True,'longText':True}
 test('keyboard-focus-large-text-and-long-record',focus_and_long)
 def failure():
  go('topic-workspace?topic=city-return',True);p.evaluate('()=>{window.oldSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error("synthetic-full")}}');p.locator('#topic-facts').fill('保存失败时仍保留的本人情况');p.locator('[data-action=topic-save]').click();check(p.evaluate('App.snapshot.observations.length')==0,'false success');check('保存失败' in p.locator('#topic-facts').input_value(),'input lost');p.evaluate('()=>{Storage.prototype.setItem=window.oldSet}');p.locator('[data-action=retry-drafts]').click();p.locator('[data-action=topic-save]').click();check(p.evaluate('App.snapshot.observations.length')==1,'retry missing');p.reload();check(p.evaluate('App.snapshot.observations[0].fields.facts')=='保存失败时仍保留的本人情况','recover');return {'noFalseSuccess':True,'retryPersisted':True}
 test('write-failure-input-retention-and-retry',failure)
 def nofake():
  go('assistant-chat',True);p.locator('textarea').fill('我想进一步了解自己的情况');p.locator('[data-action=send]').click();check('暂不可用' in p.locator('[role=dialog]').inner_text(),'unavailable');check(p.evaluate('App.snapshot.conversations.length===0 && App.snapshot.used===0'),'fake AI orquota');p.keyboard.press('Escape');p.locator('[data-action=context]').click();check('虚构' not in p.locator('[role=dialog]').inner_text(),'sample source');p.keyboard.press('Escape');nav('report');check(p.locator('.report-identity').count()==0,'sample report');return {'noGeneratedAnswer':True,'noQuotaCharge':True,'noDefaultSampleReportOrSource':True}
 test('no-fake-ai-or-default-sample',nofake)
 # visual proof at 12s natural speed: genuine running canvas, route changes in one document.
 p.set_viewport_size({'width':390,'height':844});go('home',True);p.emulate_media(reduced_motion='no-preference');p.evaluate('Ambient.resume()');frames=O/'motion-frames';frames.mkdir(exist_ok=True);t=time.monotonic()
 for i in range(24):
  if i in [8,16]:nav('explore' if i==8 else 'assistant')
  p.screenshot(path=str(frames/f'{i:03}.png'));delay=(i+1)*.5-(time.monotonic()-t)
  if delay>0:p.wait_for_timeout(delay*1000)
 (O/'extra-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));b.close()
srv.shutdown()

sys.exit(1 if any(x["status"]=="FAIL" for x in results) else 0)
