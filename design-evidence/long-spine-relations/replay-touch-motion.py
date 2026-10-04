from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import json
repo=Path(__file__).resolve().parents[2]
out=Path('/tmp/long-spine-review');out.mkdir(parents=True,exist_ok=True)
s=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(repo/'site')))
Thread(target=s.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{s.server_port}/review/portrait-art-study/'
from PIL import Image
import io
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':1000},has_touch=True,device_scale_factor=1);p.goto(base);p.wait_for_function('LineMaterial.status().ready');p.locator('[data-node="space"]').click();p.wait_for_timeout(300)
 frames=[]
 for i in range(8):
  frames.append(Image.open(io.BytesIO(p.locator('#viewport').screenshot())).convert('RGB'));p.wait_for_timeout(500)
 frames[0].save(out/'leaf-background.gif',save_all=True,append_images=frames[1:],duration=550,loop=0)
 c=p.context.new_cdp_session(p);r=p.locator('#viewport').bounding_box();cx=r['x']+r['width']/2;cy=r['y']+r['height']/2
 def touch(kind,dist):c.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':[] if kind=='touchEnd' else [{'x':cx-dist/2,'y':cy,'id':1},{'x':cx+dist/2,'y':cy,'id':2}]})
 touch('touchStart',200)
 for d in [180,140,100,70,50]:touch('touchMove',d);p.wait_for_timeout(30)
 touch('touchEnd',0);p.wait_for_timeout(100);state=p.evaluate('BotanicalTree.snapshot()');hidden=p.locator('.leaf-node:not([hidden])').count();assert state['k']<1.36 and hidden==0
 (out/'touch-report.json').write_text(json.dumps({'pinchShrink':True,'finalZoom':state['k'],'visibleLeaves':hidden,'leafAlphaSource':'RGBA 512x427','physicalDevice':False},indent=2));b.close()
s.shutdown()
