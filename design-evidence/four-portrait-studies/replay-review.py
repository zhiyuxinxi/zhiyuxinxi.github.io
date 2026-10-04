from pathlib import Path
import sys,json
repo=Path(__file__).resolve().parents[2];src=repo/'site/tools/botanical_topology_review.py';out=Path('/tmp/four-portrait-review');out.mkdir(parents=True,exist_ok=True);sys.argv=['review','--output',str(out/'checks')];scope={'__file__':str(src),'__name__':'helper'};exec(compile(src.read_text().split('with sync_playwright() as w:')[0].replace('/review/botanical-tree/','/review/portrait-art-study/'),str(src),'exec'),scope)
from playwright.sync_api import sync_playwright
rows=[];errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(device_scale_factor=1);p.on('pageerror',lambda e:errors.append(str(e)))
 for width in [320,390,1440]:
  p.set_viewport_size({'width':width,'height':1000});p.goto(scope['url']);p.wait_for_function('LineMaterial.status().ready');p.evaluate('window.keptAmbient=document.querySelector("#ambient-tide");window.keptLine=LineMaterial.canvas')
  for tab,count in [('relations',8),('traits',16),('personal',4),('completion',6)]:
   p.locator('#tab-'+tab).click();p.wait_for_timeout(300);p.mouse.move(0,0);m=p.evaluate('BotanicalTree.topology()');roots=[n for n in m['nodes'] if n['depth']==1];assert len(roots)==count
   if width==390:scope['check_geometry'](m,tab)
   r=p.evaluate('''()=>{const v=document.querySelector('#viewport').getBoundingClientRect(),k=BotanicalTree.snapshot().k,scale=Math.min(1.5,Math.max(.8,Math.sqrt(k))),labels=[...document.querySelectorAll('.tree-label:not([hidden])')].map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.label,x:r.x-v.x,y:r.y-v.y,w:r.width,h:r.height}}),nodes=BotanicalTree.layout(),hits=[];for(const edge of BotanicalTree.rendered()){const thick=edge.depth===1&&!edge.fine,data=LineMaterial.mesh(edge.q,(thick?8:edge.preview?3.8:5)*scale,(thick?3.6:1.5)*scale);for(let i=0;i<data.length;i+=4){const x=data[i],y=data[i+1];for(const l of labels)if(x>l.x&&x<l.x+l.w&&y>l.y&&y<l.y+l.h)hits.push([edge.id,l.id,'label']);for(const n of nodes)if(n.id!==edge.parent&&n.id!==edge.child&&Math.hypot(x-n.x,y-n.y)<n.size/2)hits.push([edge.id,n.id,'target'])}}return {hits:[...new Set(hits.map(JSON.stringify))],visibleRoots:nodes.filter(n=>n.depth===1).length,labelCount:labels.length,overflow:document.documentElement.scrollWidth>innerWidth,canvasKept:keptAmbient===document.querySelector('#ambient-tide')&&keptLine===LineMaterial.canvas}}''');assert not r['hits'],(tab,width,r);assert not r['overflow'];assert r['canvasKept'];assert r['visibleRoots']==count,(tab,width,r)
   if tab!='traits' and width>=390:assert r['labelCount']==count,(tab,width,r)
   p.locator('.phone').screenshot(path=str(out/f'{width}-{tab}.png'));rows.append({'width':width,'tab':tab,**r})
   node=roots[0]['id'];button=p.locator('[data-node="'+node+'"]');button.focus();p.keyboard.press('Enter');assert p.locator('#node-popover').evaluate('(e)=>e.matches(":popover-open")');p.keyboard.press('Escape');assert p.locator(':focus').get_attribute('data-node')==node
   p.locator('#viewport').focus();p.keyboard.press('+');p.wait_for_timeout(300);before=p.evaluate('BotanicalTree.snapshot()');assert before['k']>1
   p.evaluate('(id)=>BotanicalTree.inspect(id)',node);p.wait_for_timeout(300);saved=p.evaluate('BotanicalTree.snapshot()');p.keyboard.press('Escape');after=p.evaluate('BotanicalTree.snapshot()');assert all(after[k]==saved[k] for k in ['k','x','y','selected']);p.locator('#viewport').focus();p.keyboard.press('Home');p.wait_for_timeout(300)
  assert p.evaluate('BotanicalTree.snapshot().tab')=='completion';p.locator('#tab-completion').focus();p.keyboard.press('ArrowRight');assert p.evaluate('BotanicalTree.snapshot().tab')=='traits'
 # All 16 real factor nodes expose explanations; no invented scores or choice inputs.
 p.locator('#tab-traits').click()
 for n in p.evaluate('BotanicalTree.topology().nodes.filter(n=>n.depth).map(n=>n.id)'):
  p.evaluate('(id)=>BotanicalTree.inspect(id)',n);p.wait_for_timeout(230);assert p.locator('#node-popover').evaluate('(e)=>e.matches(":popover-open")');assert not p.locator('#node-popover input').count();p.keyboard.press('Escape')
 p.locator('#tab-completion').click();p.evaluate('BotanicalTree.inspect("simulation")');p.wait_for_timeout(300);assert '不属于本人测量完成结果' in p.locator('#node-popover').inner_text();p.keyboard.press('Escape');p.emulate_media(reduced_motion='reduce');p.wait_for_function('Ambient.isPaused()');assert not errors;b.close()
report={'states':rows,'geometry':scope['geometry'],'errors':errors,'checks':{'fourTabKeyboardCycle':True,'all16FactorsReachable':True,'simulationNotPersonalCompletion':True,'zoomAndPopoverCamera':True,'reducedMotion':True},'limits':['Chromium only','No physical-device or WebGL context recovery certification','Visual quality requires separate review']};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'states':len(rows),'geometryModels':len(scope['geometry']),'errors':errors}))
