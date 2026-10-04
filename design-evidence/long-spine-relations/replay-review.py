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
rows=[];errors=[];checks={}
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(device_scale_factor=1);p.on('pageerror',lambda e:errors.append(str(e)))
 for width in [320,390,1440]:
  p.set_viewport_size({'width':width,'height':1000});p.goto(base);p.wait_for_function('LineMaterial.status().ready');p.evaluate('window.keptCanvas=LineMaterial.canvas;window.keptAmbient=document.querySelector("#ambient-tide")')
  for branch in [None,'risk','time','emotion','space','commitment','planning','growth','money']:
   p.locator('#fit').click();p.wait_for_timeout(250)
   if branch:p.locator(f'[data-node="{branch}"]').click();p.wait_for_timeout(250)
   r=p.evaluate('''()=>{const nodes=BotanicalTree.layout(),labels=[...document.querySelectorAll('.tree-label:not([hidden])')].map(e=>e.dataset.label),hidden=[...document.querySelectorAll('.tree-node[hidden]')];return {nodes:nodes.map(n=>n.id),labels,hiddenFocusable:hidden.filter(n=>n.tabIndex>=0).length,leafImages:document.querySelectorAll('.tree-node:not([hidden]) .business-leaf').length,overflow:document.documentElement.scrollWidth>innerWidth,overlaps:nodes.flatMap((n,i)=>nodes.slice(i+1).filter(m=>Math.hypot(n.x-m.x,n.y-m.y)<(n.size+m.size)/2).map(m=>[n.id,m.id]))}}''')
   r['materialContacts']=p.evaluate("""()=>{const v=document.querySelector('#viewport').getBoundingClientRect(),k=BotanicalTree.snapshot().k,scale=Math.min(1.5,Math.max(.8,Math.sqrt(k))),labels=[...document.querySelectorAll('.tree-label:not([hidden])')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.label,x:r.x-v.x,y:r.y-v.y,w:r.width,h:r.height}}),nodes=BotanicalTree.layout(),hits=[];for(const edge of BotanicalTree.rendered()){const thick=edge.depth===1&&!edge.fine,data=LineMaterial.mesh(edge.q,(edge.artWidth?.[0]??(thick?8:5))*scale,(edge.artWidth?.[1]??(thick?3.6:1.5))*scale,...(edge.uv||[0,1]));for(let i=0;i<data.length;i+=4){const x=data[i],y=data[i+1];for(const l of labels)if(x>l.x&&x<l.x+l.w&&y>l.y&&y<l.y+l.h)hits.push([edge.id,l.id,'label']);for(const n of nodes)if(n.id!==edge.parent&&n.id!==edge.child&&Math.hypot(x-n.x,y-n.y)<n.size/2)hits.push([edge.id,n.id,'target'])}}return [...new Set(hits.map(JSON.stringify))]}""")
   r.update(width=width,branch=branch);rows.append(r)
   assert not r['hiddenFocusable'] and not r['overflow'] and not r['overlaps'],r
   if not branch:assert len(r['nodes'])==9 and r['leafImages']==0,r
   else:
    assert r['leafImages']==4,r
    leaf=p.locator(f'[data-node="{branch}/f0"]');leaf.focus();p.keyboard.press('Enter');assert p.locator('#node-popover').evaluate('(e)=>e.matches(":popover-open")');saved=p.evaluate('BotanicalTree.snapshot()');p.keyboard.press('Escape');after=p.evaluate('BotanicalTree.snapshot()');assert all(saved[k]==after[k] for k in ['x','y','k']);assert p.locator(':focus').get_attribute('data-node')==branch+'/f0'
   if branch in [None,'space','money','planning']:p.locator('.phone').screenshot(path=str(out/f'{width}-{branch or "overview"}.png'))
  for tab in ['traits','personal','completion','relations']:
   p.locator('#tab-'+tab).click();p.wait_for_timeout(50);assert p.evaluate('LineMaterial.canvas===keptCanvas&&document.querySelector("#ambient-tide")===keptAmbient')
  p.locator('#fit').click();p.wait_for_timeout(250);p.locator('#viewport').focus();p.keyboard.press('+');p.wait_for_timeout(250);assert p.evaluate('BotanicalTree.snapshot().k')>1;p.keyboard.press('Home');p.wait_for_timeout(250);assert p.evaluate('BotanicalTree.snapshot().k')==1
 p.locator('[data-node="money"]').click();p.wait_for_timeout(250);before=p.evaluate('BotanicalTree.snapshot()');r=p.locator('#viewport').bounding_box();p.mouse.move(r['x']+180,r['y']+280);p.mouse.down();p.mouse.move(r['x']+210,r['y']+310,steps=5);p.mouse.up();after=p.evaluate('BotanicalTree.snapshot()');assert after['x']!=before['x'];assert not p.locator('#node-popover').evaluate('(e)=>e.matches(":popover-open")')
 p.emulate_media(reduced_motion='reduce');p.wait_for_function('Ambient.isPaused()');checks={'all32LeavesAtThreeWidths':True,'noHiddenFocusTargets':True,'noHitTargetOverlap':True,'keyboardLeafPopoverAndCameraRestore':True,'panAndClickSuppression':True,'zoomHome':True,'persistentCanvases':True,'reducedMotion':True}
 b.close()
(out/'interaction-report.json').write_text(json.dumps({'states':rows,'errors':errors,'checks':checks},ensure_ascii=False,indent=2));print(json.dumps({'states':len(rows),'errors':errors,'checks':checks}))
s.shutdown()
