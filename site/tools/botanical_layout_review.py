from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json,math,argparse,shutil
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
parser=argparse.ArgumentParser(description='Botanical layout collision and camera review');parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];out=args.output;out.mkdir(parents=True,exist_ok=True)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(root)));Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_port}/review/botanical-tree/'
check_js='''()=>{const v=document.querySelector('#viewport').getBoundingClientRect();let es=[...document.querySelectorAll('.node[aria-hidden=false]')].map(e=>{let r=e.getBoundingClientRect();return {e,name:e.getAttribute('aria-label'),x:r.x,y:r.y,w:r.width,h:r.height}});const overlaps=[],badHits=[],clipped=[];for(let i=0;i<es.length;i++){let a=es[i];if(a.x<v.x-.5||a.y<v.y-.5||a.x+a.w>v.right+.5||a.y+a.h>v.bottom+.5)clipped.push(a.name);for(let j=i+1;j<es.length;j++){let b=es[j];if(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y)overlaps.push([a.name,b.name])}for(let [dx,dy] of [[.5,.5],[.2,.3],[.8,.7]]){let x=a.x+a.w*dx,y=a.y+a.h*dy;if(y>=0&&y<innerHeight){let t=document.elementFromPoint(x,y);if(!a.e.contains(t))badHits.push(a.name)}}}return {overlaps,clipped,badHits,targets:es.map(({name,w,h})=>({name,w,h})),parents:document.querySelectorAll('[data-branch][aria-hidden=false]').length,leaves:document.querySelectorAll('[data-leaf][aria-hidden=false]').length}}'''
results=[];failures=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 def wait():p.wait_for_timeout(300)
 def capture(name,total=False):
  p.locator('#viewport').scroll_into_view_if_needed();p.mouse.move(0,0);r=p.evaluate(check_js);r['name']=name;r['state']=p.evaluate('BotanicalTree.snapshot()');results.append(r);(out/'progress.json').write_text(json.dumps(results,ensure_ascii=False));p.locator('#viewport').screenshot(path=str(out/(name+'.png')))
  if r['overlaps'] or r['clipped'] or r['badHits'] or any(x['w']<44 or x['h']<44 for x in r['targets']) or total and r['parents']!=int(p.locator('#structure').input_value()):failures.append(r)
 def fit():p.locator('#fit').click();wait()
 def zoom(z):
  p.locator('#viewport').scroll_into_view_if_needed();r=p.locator('#viewport').bounding_box();p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);k=p.evaluate('BotanicalTree.snapshot().k');p.mouse.wheel(0,-math.log(z/k)/.002);wait()
 for width in [320,390,430,1170]:
  for count in [8,12]:
   p.set_viewport_size({'width':width,'height':1000 if width<500 else 751});p.goto(url);p.wait_for_function('window.BotanicalTree');wait();p.locator('.demo-frame summary').click();p.select_option('#structure',str(count));p.locator('.demo-frame summary').click();wait();prefix=f'{width}-{count}'
   capture(prefix+'-overview',True);zoom(.7);capture(prefix+'-minimum',True);fit();zoom(1.4);capture(prefix+'-threshold')
   fit();bid='planning' if count==8 else 'layout6';p.locator('[data-branch='+bid+']').click();wait();capture(prefix+'-expanded')
   zoom(2.65);capture(prefix+'-high');p.locator('#viewport').focus();p.keyboard.press('ArrowRight');p.keyboard.press('ArrowDown');p.keyboard.press('ArrowDown');capture(prefix+'-edge')
   p.locator('#fit-branch').click();wait();capture(prefix+'-branch-fit');assert p.locator('[data-leaf][aria-hidden=false]').count()==4
   p.locator('#zoom-out').scroll_into_view_if_needed();r=p.locator('#zoom-out').bounding_box();y=p.evaluate('scrollY');p.mouse.click(r['x']+r['width']/2,r['y']+r['height']/2);wait();state=p.evaluate('BotanicalTree.snapshot()');assert abs(state['x'])<1 and abs(state['y'])<1,('semantic camera',state);assert abs(p.evaluate('scrollY')-y)<2,('scroll shift',width,count,y,p.evaluate('scrollY'));capture(prefix+'-zoom-return')
   fit();p.locator('.demo-frame summary').click();p.check('#long-labels');p.locator('.demo-frame summary').click();wait();capture(prefix+'-long',True);p.screenshot(path=str(out/(prefix+'-long-page.png')),full_page=True)
   p.locator('[data-branch='+bid+']').click();wait();capture(prefix+'-long-expanded')
 # All directions, actual sixteen factors, and prior regressions.
 p.set_viewport_size({'width':320,'height':1000});p.goto(url);p.wait_for_function('window.BotanicalTree')
 for bid in ['risk','time','emotion','space','commitment','planning','growth','money']:
  fit();p.locator('[data-branch='+bid+']').click();wait();capture('320-8-sector-'+bid);assert p.locator('[data-leaf][aria-hidden=false]').count()==4
 p.locator('#tab-traits').click()
 for bid in ['group0','group1','group2','group3']:
  fit();p.locator('[data-branch='+bid+']').click();wait();capture('320-factors-'+bid)
 p.locator('#tab-personal').click();capture('320-personal-overview')
 for bid in ['visibility','evidence']:assert '部分线索有记录' in p.locator('[data-branch='+bid+']').get_attribute('aria-label')
 fit();zoom(1.64);capture('320-personal-no-selection');assert p.locator('[data-branch][aria-hidden=false]').count()>0
 p.locator('#tab-relations').click();fit();p.locator('[data-branch=space]').focus();p.keyboard.press('Enter');wait();assert p.locator(':focus').get_attribute('data-branch')=='space';p.locator('[data-leaf=f2]').focus();p.keyboard.press('Space');old=p.evaluate('BotanicalTree.snapshot()');p.locator('[data-close]').click();assert p.locator(':focus').get_attribute('id')=='viewport';now=p.evaluate('BotanicalTree.snapshot()');assert all(old[k]==now[k] for k in ['k','x','y','leaf'])
 p.emulate_media(reduced_motion='reduce');wait();assert p.evaluate('Ambient.isPaused()');capture('320-reduced-motion');assert not errors,errors;b.close()
(out/'report.json').write_text(json.dumps({'states':results,'failures':failures,'errors':errors},ensure_ascii=False,indent=2));print(json.dumps({'states':len(results),'failures':[r['name'] for r in failures],'errors':errors}));assert not failures
