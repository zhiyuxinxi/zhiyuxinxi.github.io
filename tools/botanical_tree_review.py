from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json, math
import argparse, shutil
parser=argparse.ArgumentParser(description='Standalone botanical tree browser review');parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];out=args.output;out.mkdir(parents=True,exist_ok=True)
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(root)));Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_port}/review/botanical-tree/'
checks=[]
def check(v,msg):
 if not v:raise AssertionError(msg)
def pause(p):p.wait_for_timeout(280)
def snap(p):return p.evaluate('BotanicalTree.snapshot()')
with sync_playwright() as w:
 browser=w.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox']);ctx=browser.new_context();p=ctx.new_page();errors=[];req=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:req.append(r.url));p.goto(url);p.wait_for_function('window.BotanicalTree');p.wait_for_function('document.querySelectorAll("#theme option").length===13');p.evaluate("localStorage.setItem('sentinel','kept');sessionStorage.setItem('sentinel','kept');window.savedCanvas=document.querySelector('#ambient-tide')")
 check(p.evaluate('BotanicalTree.counts()')=={'relations':8,'factors':16},'8 relations,16 factors')
 for width in [320,390,430,1440]:
  p.set_viewport_size({'width':width,'height':1100});pause(p);p.locator('#fit').click();pause(p)
  check(not p.evaluate('document.documentElement.scrollWidth>innerWidth'),'horizontal overflow')
  rects=p.locator('[data-branch]').evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})');check(all(r['w']>=44 and r['h']>=44 for r in rects),'targets');check(all(not(a['x']<b['x']+b['w'] and a['x']+a['w']>b['x'] and a['y']<b['y']+b['h'] and a['y']+a['h']>b['y']) for i,a in enumerate(rects) for b in rects[i+1:]),f'parent overlap {width}');p.screenshot(path=str(out/f'{width}-overview.png'),full_page=True)
  for bid in ['risk','time','emotion','space','commitment','planning','growth','money']:
   p.locator('#fit').click();pause(p);p.locator('[data-branch='+bid+']').click();pause(p);box=p.locator('#viewport').bounding_box();leaves=p.locator('[data-leaf]').evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})');check(len(leaves)==4,'four leaves');check(all(r['x']>=box['x']-1 and r['x']+r['w']<=box['x']+box['width']+1 and r['y']>=box['y']-1 and r['y']+r['h']<=box['y']+box['height']+1 for r in leaves),f'leaf clipped {width} {bid} {leaves}');check(all(not(a['x']<b['x']+b['w'] and a['x']+a['w']>b['x'] and a['y']<b['y']+b['h'] and a['y']+a['h']>b['y']) for i,a in enumerate(leaves) for b in leaves[i+1:]),f'leaf overlap {width} {bid}')
  checks.append(f'{width}: parents nonoverlap, 8 branches x4 leaves fully visible')
 p.set_viewport_size({'width':390,'height':1000});p.locator('#fit').click();pause(p);p.locator('[data-branch=space]').click();pause(p);p.locator('[data-leaf=f2]').click();before=snap(p);p.screenshot(path=str(out/'390-selected-need.png'),full_page=True);p.locator('[data-close]').click();after=snap(p);check(all(before[k]==after[k] for k in ['k','x','y','branch','leaf']),'close context');p.locator('#fit').click();pause(p);check(snap(p)['leaf']=='f2','hidden leaf retained');check('已保留' in p.locator('#detail').inner_text(),'hidden selection notice')
 for _ in range(15):p.locator('#zoom-out').click(force=True)
 pause(p);check(abs(snap(p)['k']-.7)<.02,'min');p.locator('#viewport').focus();p.keyboard.press('+');pause(p);check(snap(p)['k']>.7,'keyboard zoom');p.keyboard.press('ArrowRight');check(snap(p)['x']!=0,'keyboard pan');p.keyboard.press('Home');pause(p)
 for _ in range(7):p.locator('#zoom-in').click(force=True);pause(p)
 check(snap(p)['k']==3,'max');p.locator('#fit').click();pause(p)
 # Drag over a branch must not activate it.
 r=p.locator('[data-branch=time]').bounding_box();old=snap(p);p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);p.mouse.down();p.mouse.move(r['x']+130,r['y']+80,steps=10);p.mouse.up();pause(p);check(snap(p)['branch']==old['branch'],'drag activated branch');check(snap(p)['x']!=old['x'],'drag moves');p.locator('#fit').click();pause(p)
 saved=snap(p);p.locator('#tab-traits').click();pause(p);p.locator('[data-branch=group0]').click();pause(p);check(p.locator('[data-leaf]').count()==4,'traits4');p.locator('[data-leaf=A]').click();check('无有效量表结果' in p.locator('#detail').inner_text(),'unknown has no value');p.screenshot(path=str(out/'390-bipolar.png'),full_page=True)
 p.locator('#tab-personal').click();p.locator('[data-branch=rhythm]').click();pause(p);p.locator('[data-leaf=company]').click();check(p.locator('.choices .current').count()==2,'independent coexist');p.screenshot(path=str(out/'390-independent.png'),full_page=True);p.locator('#fit').click();pause(p);p.locator('[data-branch=visibility]').click();pause(p);check(p.locator('.choices .current').count()==1,'exclusive state');p.screenshot(path=str(out/'390-exclusive.png'),full_page=True)
 p.locator('#tab-relations').click();pause(p);check(all(snap(p)[k]==saved[k] for k in ['k','x','y','branch','leaf']),'tab viewport restore')
 for _ in range(12):
  p.locator('#tab-traits').click();p.locator('#tab-personal').click();p.locator('#tab-relations').click();p.locator('#zoom-in').click();p.locator('#fit').click()
 pause(p);check(snap(p)['k']==1,'rapid final stable');check(p.evaluate("document.querySelector('#ambient-tide')===savedCanvas"),'canvas persistent');check(p.evaluate("localStorage.getItem('sentinel')==='kept'&&sessionStorage.getItem('sentinel')==='kept'"),'no storage mutation');checks.append('keyboard, zoom bounds, drag/click isolation, close context, tabs, rapid actions, 5 semantics, storage/canvas identity')
 p.locator('.demo-frame summary').click()
 for t in p.locator('#theme option').evaluate_all('(es)=>es.map(e=>e.value)'):
  p.select_option('#theme',t);check(not p.evaluate('document.documentElement.scrollWidth>innerWidth'),'theme overflow')
 p.select_option('#theme','study');p.locator('.demo-frame summary').click();p.emulate_media(reduced_motion='reduce');pause(p);check(p.evaluate('Ambient.isPaused()'),'reduced static');p.emulate_media(reduced_motion='no-preference');checks.append('13 appearances and system reduced motion')
 # Chromium CDP touch events exercise actual browser pointer delivery, not physical hardware.
 touch=browser.new_context(viewport={'width':390,'height':1000},is_mobile=True,has_touch=True);q=touch.new_page();q.goto(url);q.wait_for_function('window.BotanicalTree');cdp=touch.new_cdp_session(q);r=q.locator('#viewport').bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
 def pts(dx):return [{'x':x-dx,'y':y,'id':1},{'x':x+dx,'y':y,'id':2}]
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':pts(40)});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':pts(85)});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});pause(q);check(snap(q)['k']>1.5,'CDP pinch zoom');q.screenshot(path=str(out/'390-touch-pinch.png'),full_page=True);checks.append('Chromium CDP two-finger pinch (not physical device)')
 # Hysteresis, resize with active selection, bounded pan, and one-finger touch.
 p.locator('#fit').click();pause(p);r=p.locator('#viewport').bounding_box();p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2)
 def to_zoom(z):
  p.mouse.wheel(0,-math.log(z/snap(p)['k'])/.002);p.wait_for_timeout(60)
 to_zoom(1.6);check(snap(p)['tier']==2,'enter leaf tier')
 for z in [1.4,1.48,1.41,1.49]:to_zoom(z);check(snap(p)['tier']==2,'hysteresis from above')
 to_zoom(1.3)
 for z in [1.4,1.48,1.41,1.49]:to_zoom(z);check(snap(p)['tier']==1,'hysteresis from below')
 p.locator('#fit').click();pause(p);p.locator('[data-branch=space]').click();pause(p);p.locator('[data-leaf=f2]').click();selected=snap(p);p.set_viewport_size({'width':320,'height':800});pause(p);check(all(snap(p)[k]==selected[k] for k in ['k','x','y','branch','leaf']),'resize retains viewport')
 p.locator('#viewport').focus()
 for _ in range(60):p.keyboard.press('ArrowRight')
 check(abs(snap(p)['x'])<1000,'bounded pan');p.keyboard.press('Home');pause(p);check(snap(p)['x']==0 and snap(p)['k']==1,'out of bounds recovery')
 p.locator('#tab-personal').click();p.locator('#fit').click();pause(p);p.locator('[data-branch=evidence]').click();pause(p);check('不代表人格高低' in p.locator('#detail').inner_text(),'completion not score')
 q.locator('#fit').click();pause(q);r=q.locator('#viewport').bounding_box();x=r['x']+150;y=r['y']+180
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+75,'y':y+50,'id':1}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});pause(q);check(abs(snap(q)['x'])>40,'single touch pan');q.locator('#fit').click();pause(q);check(snap(q)['x']==0,'touch recovery');checks.append('semantic hysteresis, selected resize, completion semantics, CDP one-finger pan/recovery')
 # Independent-review regressions: unselected semantic zoom, keyboard rebuild focus, derived records.
 p.locator('.demo-frame summary').click();p.locator('#reset').click();p.locator('.demo-frame summary').click()
 for t in ['traits','personal','relations']:
  p.locator('#tab-'+t).click()
  for _ in range(2):p.locator('#zoom-in').click();pause(p)
  check(p.locator('[data-branch][aria-hidden=false]').count()>0,'unselected parents at leaf-tier zoom '+t);check(p.locator('#level').inner_text().startswith('主枝'),'unselected level label');p.locator('#fit').click();pause(p)
 p.locator('[data-branch=space]').focus();p.keyboard.press('Enter');pause(p);check(p.locator(':focus').get_attribute('data-branch')=='space','focus after branch rebuild')
 p.keyboard.press('Tab');check(p.locator(':focus').get_attribute('data-leaf')=='f0','Tab reaches leaf');p.keyboard.press('Space');check(snap(p)['leaf']=='f0','Space opens leaf')
 p.locator('[data-close]').focus();p.keyboard.press('Enter');check(p.locator(':focus').get_attribute('id')=='viewport','close focus')
 p.locator('[data-expand]').focus();p.keyboard.press('Enter');pause(p);check(p.locator(':focus').get_attribute('data-branch')=='space','expand focus');p.locator('[data-overview]').focus();p.keyboard.press('Enter');pause(p);check(p.locator(':focus').get_attribute('id')=='viewport','overview focus')
 p.locator('#tab-personal').click()
 for bid in ['visibility','evidence']:
  n=p.locator('[data-branch='+bid+']');check('recorded' in n.get_attribute('class'),'derived parent record '+bid);check('部分线索有记录' in n.get_attribute('aria-label'),'partial record meaning '+bid)
 checks.append('review fixes: unselected zoom/reset/tab parents, keyboard Enter/Space/Tab focus restoration, parent partial records derived from leaves')
 check(not errors,str(errors));check(all(u.startswith(f'http://127.0.0.1:{srv.server_port}/') for u in req),'external network');browser.close()
(out/'report.json').write_text(json.dumps({'checks':checks,'errors':errors,'limits':['Chromium only','CDP synthesized touch; no physical phone','No screen-reader certification','No real measurement/backend']},ensure_ascii=False,indent=2));print(json.dumps(checks,ensure_ascii=False))
