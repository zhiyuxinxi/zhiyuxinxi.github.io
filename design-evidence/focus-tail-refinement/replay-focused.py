from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import json
repo=Path(__file__).resolve().parents[2]
out=Path('/tmp/focus-tail-review');out.mkdir(parents=True,exist_ok=True)
s=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(repo/'site')))
Thread(target=s.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{s.server_port}/review/portrait-art-study/'
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':1000},device_scale_factor=2);p.goto(base);p.wait_for_function('LineMaterial.status().ready');p.wait_for_timeout(100)
 original=p.evaluate('BotanicalTree.topology()');p.locator('.phone').screenshot(path=str(out/'390-overview.png'))
 prefix=p.evaluate("""()=>{const m=BotanicalTree.topology(),v=document.querySelector('#viewport'),d={w:v.clientWidth,h:v.clientHeight,s:Math.min(v.clientWidth/390,v.clientHeight/720)};return BotanicalTree.rendered().filter(e=>e.role==='carrier').map(e=>{const q=m.edges.find(a=>a.id===e.id).q,t=e.rootId==='space'?.48:.62,expected=TreeGeometry.point(q,t).map((x,i)=>(i?d.h:d.w)/2+x*d.s);return {id:e.id,t,error:Math.hypot(...e.q[3].map((x,i)=>x-expected[i]))}})}""")
 assert all(e['error']<1e-6 for e in prefix)
 p.locator('[data-node="space"]').click();p.wait_for_timeout(300);p.mouse.move(0,0);p.locator('.phone').screenshot(path=str(out/'390-focus.png'))
 distance=p.evaluate("""()=>{const n=document.querySelector('[data-node="space"]').getBoundingClientRect(),l=document.querySelector('[data-label="space"]').getBoundingClientRect();return Math.hypot(n.x+n.width/2-l.x-l.width/2,n.y+n.height/2-l.y-l.height/2)}""");assert distance<85
 assert p.locator('[data-label="emotion"]').is_hidden();assert p.evaluate('BotanicalTree.rendered().filter(e=>e.rootId!=="space").every(e=>e.opacity===.22)')
 assert original==p.evaluate('BotanicalTree.topology()')
 r=p.locator('#viewport').bounding_box();p.mouse.move(r['x']+200,r['y']+250);p.mouse.down();p.mouse.move(r['x']+220,r['y']+265,steps=5);p.mouse.up();p.wait_for_timeout(50)
 assert p.evaluate('BotanicalTree.rendered().every(e=>e.opacity===1)');assert p.locator('[data-label="emotion"]').is_visible();p.mouse.move(0,0);p.locator('.phone').screenshot(path=str(out/'390-after-pan.png'))
 (out/'focused-report.json').write_text(json.dumps({'overviewCurvePrefix':prefix,'titleCenterDistancePx':distance,'neighborTitleRestoredOnPan':True,'neighborOpacityRestoredOnPan':True,'semanticTopologyAndWorldPositionsUnchanged':True},indent=2));b.close()
s.shutdown()
