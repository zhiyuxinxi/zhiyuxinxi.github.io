"""Targeted 12-theme, four-selected-tab contract; actual computed colors and pixels."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
from PIL import Image
from playwright.sync_api import sync_playwright
import json,os,sys,re,hashlib
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=ROOT/'qa/nav-contrast';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=s.serve_forever,daemon=True).start();results=[]
def rgb(v):return [float(x) for x in re.findall(r'[\d.]+',v)][:3]
def lum(c):
 a=[v/255 for v in c];return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*k for v,k in zip(a,[.2126,.7152,.0722]))
def ratio(a,b):
 lo,hi=sorted([lum(a),lum(b)]);return (hi+.05)/(lo+.05)
with sync_playwright() as w:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**args)
 for theme in [t['id'] for t in json.loads((ROOT/'handoff/themes-v4.json').read_text())]:
  c=b.new_context(viewport={'width':390,'height':844},locale='zh-CN');p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));rows=[]
  try:
   p.goto(f'http://127.0.0.1:{s.server_port}/prototype/index.html?reset=1&scenario=nav-contrast&theme={theme}#home',wait_until='networkidle')
   for route in ['home','explore','assistant','me']:
    p.locator(f'.nav button[data-route="{route}"]').click();p.wait_for_function('r=>App.currentRoute===r',arg=route)
    for t in [8,24]:
     p.evaluate('t=>Ambient.sample(t)',t);p.wait_for_timeout(250)
     rows_js=p.locator('.nav button').evaluate_all('''es=>es.map(e=>{const icon=e.querySelector('.navicon'),svg=icon.querySelector('svg'),g=getComputedStyle(icon),b=icon.getBoundingClientRect(),s=getComputedStyle(e),nav=e.closest('.nav').getBoundingClientRect();const probe=document.createElement('i');probe.style.color='var(--primary)';document.body.append(probe);const primary=getComputedStyle(probe).color;probe.style.color='var(--on-primary)';const onPrimary=getComputedStyle(probe).color;probe.remove();return {route:e.dataset.route,active:e.classList.contains('active'),background:g.backgroundColor,iconColor:getComputedStyle(svg).color,labelColor:s.color,expectedBackground:primary,expectedIcon:onPrimary,x:b.x+b.width/2,y:b.y+b.height/2,labelBgX:b.x+b.width/2,labelBgY:nav.bottom-3}})''')
     assert len(rows_js)==4 and sum(x['active'] for x in rows_js)==1
     active=next(x for x in rows_js if x['active']);assert active['route']==route
     assert active['background']==active['expectedBackground'],f'{theme}/{route}: legacy selected background override'
     assert active['iconColor']==active['expectedIcon'],f'{theme}/{route}: selected foreground mismatch'
     name=f'{theme}-{route}-{t}';p.screenshot(path=str(OUT/(name+'.png')))
     hide=p.add_style_tag(content='.nav svg{visibility:hidden!important}');buf=p.screenshot();hide.evaluate('(e)=>e.remove()')
     from io import BytesIO
     im=Image.open(BytesIO(buf)).convert('RGB')
     for r in rows_js:
      background=im.getpixel((int(r['x']),int(r['y'])));label_bg=im.getpixel((int(r['labelBgX']),int(r['labelBgY'])));r['renderedIconContrast']=ratio(rgb(r['iconColor']),background);r['renderedLabelContrast']=ratio(rgb(r['labelColor']),label_bg)
      assert r['renderedIconContrast']>=3,f'{theme}/{route}/{r["route"]}: icon contrast {r["renderedIconContrast"]}'
      assert r['renderedLabelContrast']>=4.5,f'{theme}/{route}/{r["route"]}: label contrast {r["renderedLabelContrast"]}'
      if not r['active']:assert r['background']=='rgba(0, 0, 0, 0)','Unselected icon acquired active fill'
     rows.append({'route':route,'seconds':t,'tabs':rows_js})
   assert not errors,str(errors);results.append({'theme':theme,'status':'PASS','states':rows})
  except Exception as e:results.append({'theme':theme,'status':'FAIL','error':str(e),'states':rows})
  c.close()
 b.close()
s.shutdown();r={'sourceCSSSHA256':hashlib.sha256((ROOT/'prototype/product.css').read_bytes()).hexdigest(),'createdAt':datetime.now(timezone.utc).isoformat(),'scope':'12 themes × four selected tabs × two field endpoints; 384 selected/unselected icon and label checks. Expected token pairs plus actual screenshot backgrounds. Synthetic data only.','results':results};(OUT/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'theme':x['theme'],'status':x['status'],'error':x.get('error')} for x in results],ensure_ascii=False,indent=2));sys.exit(0 if all(x['status']=='PASS' for x in results) else 1)
