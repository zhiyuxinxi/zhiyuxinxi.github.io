"""Read-only release proof: actual Pages bytes, browser states, and unchanged sibling graphs."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
from PIL import Image
import argparse,hashlib,json,subprocess,urllib.request,time,io,os
ap=argparse.ArgumentParser();ap.add_argument('--url',default='https://zhiyuxinxi.github.io/');ap.add_argument('--source',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
base=a.url.rstrip('/')+'/';sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.source,text=True).strip();r={'verifiedCommit':sha,'url':base,'hashes':[],'themes':[],'siblingImages':{},'checks':[],'errors':[],'passed':False}
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(a.baseline.resolve())));Thread(target=server.serve_forever,daemon=True).start();before=f'http://127.0.0.1:{server.server_port}/'
try:
 for rel in ['prototype/product.css','prototype/product-surface.js','prototype/app.js','prototype/ambient.js','prototype/themes-v4.css','prototype/themes-v4.js']+['review/relationship-map/'+n for n in ['index.html','camera.js','camera.css','models.js','semantics.js','theme.js','assets/terminal-leaf.svg']]:
  expected=hashlib.sha256((a.source/rel).read_bytes()).hexdigest()
  with urllib.request.urlopen(base+rel+'?release='+sha,timeout=30) as response:actual=hashlib.sha256(response.read()).hexdigest()
  assert expected==actual,rel;r['hashes'].append({'path':rel,'sha256':actual})
 with sync_playwright() as w:
  b=w.chromium.launch(**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}),args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844},device_scale_factor=2,reduced_motion='reduce');p.on('pageerror',lambda e:r['errors'].append(str(e)))
  for mode in ['traits','personal','completion']:
   images=[]
   for name,url in [('baseline',before),('public',base)]:
    p.goto(url+'review/relationship-map/?map='+mode+'&theme=green&still',wait_until='networkidle');p.evaluate('document.fonts.ready');p.wait_for_timeout(100);p.mouse.move(0,0);data=p.screenshot(path=str(a.output/(name+'-'+mode+'.png')));images.append(hashlib.sha256(data).hexdigest())
   assert images[0]==images[1],(mode,images);r['siblingImages'][mode]={'baseline':images[0],'public':images[1],'identical':True}
  for theme in ['green','peach','blue','violet','sunrise','candy','berry','lime','aurora','sea','nebula','amber']:
   p.goto(base+'prototype/index.html?theme='+theme+'#assistant',wait_until='networkidle');p.locator('[data-action=profile-group][data-id=relationships]').click();iframe=p.locator('.profile-tendencies iframe');f=iframe.element_handle().content_frame();f.wait_for_function('window.MapCamera');p.locator('.profile-tendencies').scroll_into_view_if_needed();p.wait_for_timeout(100)
   assert p.evaluate('App.snapshot.theme')==theme
   assert f.evaluate('document.documentElement.style.colorScheme')==('dark' if theme in ['nebula','amber'] else 'light')
   assert f.locator('.root-join:visible').count()==8
   assert f.locator('[data-kind=leaf]:visible').count()==0
   assert f.evaluate('Ambient.isPaused()') and p.evaluate('Ambient.isPaused()')
   rect=iframe.bounding_box();xy=(round((rect['x']+rect['width']-25)*2),round((rect['y']+25)*2))
   shown=Image.open(io.BytesIO(p.screenshot(path=str(a.output/(theme+'-overview.png'))))).convert('RGB');iframe.evaluate('(e)=>e.style.visibility="hidden"');hidden=Image.open(io.BytesIO(p.screenshot())).convert('RGB');iframe.evaluate('(e)=>e.style.visibility=""')
   visiblePixel=shown.getpixel(xy);backgroundPixel=hidden.getpixel(xy);assert max(abs(x-y) for x,y in zip(visiblePixel,backgroundPixel))<=2,(theme,visiblePixel,backgroundPixel)
   r['themes'].append({'theme':theme,'transparentOverActualBackground':True,'visiblePixel':visiblePixel,'backgroundPixel':backgroundPixel,'reducedMotion':True})
  p.goto(base+'prototype/index.html?theme=green#assistant',wait_until='networkidle');p.locator('[data-action=profile-group][data-id=relationships]').click();f=p.locator('.profile-tendencies iframe').element_handle().content_frame();f.wait_for_function('window.MapCamera');p.locator('.profile-tendencies').scroll_into_view_if_needed();p.screenshot(path=str(a.output/'overview.png'));records=p.evaluate('({sessions:App.snapshot.sessions,observations:App.snapshot.observations})')
  for branch in f.evaluate('RelationshipArt.branches.map(b=>b.id)'):
   f.evaluate('(id)=>MapCamera.focusBranch(id)',branch);p.wait_for_timeout(50);assert f.locator('[data-kind=leaf]:visible').count()==3;p.screenshot(path=str(a.output/('focus-'+branch+'.png')));state=f.evaluate('MapCamera.state()');f.locator('[data-kind=leaf]:visible').first.click();p.locator('.dialog').wait_for();
   if branch=='emo':p.screenshot(path=str(a.output/'detail.png'))
   p.keyboard.press('Escape');after=f.evaluate('MapCamera.state()');assert all(state[k]==after[k] for k in ['x','y','k','current']);assert p.locator('.dialog').count()==0
   f.get_by_role('button',name='全图',exact=True).click();assert f.locator('[data-kind=leaf]:visible').count()==0
  assert records==p.evaluate('({sessions:App.snapshot.sessions,observations:App.snapshot.observations})');r['checks'].append('8 focused branches, 24 terminal images, detail close camera preservation, return overview, unchanged records')
  p.emulate_media(reduced_motion='no-preference');p.reload(wait_until='networkidle');f=p.locator('.profile-tendencies iframe').element_handle().content_frame();f.wait_for_function('window.MapCamera');p.evaluate('window.proofCanvas=document.querySelector("#ambient-tide")');t=p.evaluate('Ambient.getTime()');f.locator('[data-kind=branch][data-branch=emo]').click();f.locator('[data-kind=leaf]:visible').first.click();p.keyboard.press('Escape');p.wait_for_timeout(150);assert p.evaluate('Ambient.getTime()')>t;assert p.evaluate('proofCanvas===document.querySelector("#ambient-tide")');r['checks'].append('same live parent canvas; time advances through focus/detail/close')
  p.set_viewport_size({'width':1280,'height':900});p.goto(base,wait_until='networkidle');assert p.locator('#product-frame').count()==1;p.screenshot(path=str(a.output/'public-workbench.png'));r['checks'].append('actual public workbench and prototype load');assert not r['errors'];r['passed']=True;b.close()
finally:
 (a.output/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
