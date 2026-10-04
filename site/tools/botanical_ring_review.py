from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,math,argparse,shutil
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(Path(__file__).resolve().parents[1])));Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as w:
 b=w.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':1000});p.goto(f'http://127.0.0.1:{s.server_port}/review/botanical-tree/');p.wait_for_function('window.BotanicalTree');p.locator('.demo-frame summary').click();p.select_option('#structure','12');p.locator('.demo-frame summary').click();p.wait_for_timeout(300)
 p.locator('#viewport').screenshot(path=str(out/'390-ring.png'));p.screenshot(path=str(out/'390-overview-page.png'),full_page=True);assert p.locator('[data-branch][aria-hidden=false]').count()==12;assert p.locator('#index button').count()==12
 coords=p.evaluate('BotanicalTree.layout().filter(e=>e.key.startsWith("layout")).map(e=>e.anchor)');xs=[x[0] for x in coords];ys=[x[1] for x in coords];ratio=(max(xs)-min(xs))/(max(ys)-min(ys));assert .9<ratio<1.1
 for i in range(12):
  p.locator('.text-index summary').click();p.locator('[data-select=layout'+str(i)+']').click();p.wait_for_timeout(300);assert p.evaluate('BotanicalTree.snapshot().branch')=='layout'+str(i);assert p.locator('[data-leaf][aria-hidden=false]').count()==4;p.locator('.text-index summary').click();p.locator('#fit').click();p.wait_for_timeout(300)
 p.locator('#viewport').scroll_into_view_if_needed();r=p.locator('#viewport').bounding_box();p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2)
 def zoom(k):
  now=p.evaluate('BotanicalTree.snapshot().k');p.mouse.wheel(0,-math.log(k/now)/.002);p.wait_for_timeout(160)
 zoom(1.3);assert not p.locator('#nodes').evaluate('(e)=>e.classList.contains("compact-ring")')
 p.locator('#viewport').screenshot(path=str(out/'390-names.png'))
 for k in [1.17,1.23,1.18,1.22]:zoom(k);assert not p.locator('#nodes').evaluate('(e)=>e.classList.contains("compact-ring")')
 zoom(1.05)
 for k in [1.17,1.23,1.18,1.22]:zoom(k);assert p.locator('#nodes').evaluate('(e)=>e.classList.contains("compact-ring")')
 p.locator('#fit').click();p.wait_for_timeout(300)
 p.locator('[data-branch=layout6]').focus();p.keyboard.press('Enter');p.wait_for_timeout(300);assert p.locator(':focus').get_attribute('data-branch')=='layout6';p.keyboard.press('Tab');assert p.locator(':focus').get_attribute('data-leaf')=='f0';p.screenshot(path=str(out/'390-ring-focus.png'),full_page=True)
 (out/'report.json').write_text(json.dumps({'ring_world_projected_ratio':ratio,'overview_discoverable':12,'index_targets_verified':12,'all_branch_fit_four_leaves':True,'keyboard_number_to_leaf':True,'name_layer_hysteresis':True}));b.close()
