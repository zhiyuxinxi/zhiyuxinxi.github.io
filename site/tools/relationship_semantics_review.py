"""Check the new hand-drawn graph's own semantics and interactions, locally or publicly."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,json,subprocess,hashlib,urllib.request,os,time
ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();base=a.url.rstrip('/')+'/';a.output.mkdir(parents=True,exist_ok=True);src=Path(__file__).resolve().parents[1]
r={'url':base,'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip(),'workingTreeModified':bool(subprocess.check_output(['git','diff','--name-only'],cwd=src,text=True).strip()),'hashes':[],'checks':[],'errors':[],'passed':False}
def intersect(a,b,c,d):
 ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c[0],d[1]-c[1];den=ux*vy-uy*vx
 if abs(den)<1e-10:return None
 wx,wy=c[0]-a[0],c[1]-a[1];t=(wx*vy-wy*vx)/den;u=(wx*uy-wy*ux)/den
 return [a[0]+t*ux,a[1]+t*uy] if 0<t<1 and 0<u<1 else None

def check(ok,message):
 assert ok,message
try:
 for name in ['index.html','models.js','semantics.js','camera.js','camera.css','structure.html','assets/leaf-node.png']:
  path='review/relationship-map/'+name
  with urllib.request.urlopen(base+path+'?semantic_check='+str(time.time_ns()),timeout=25) as response:actual=hashlib.sha256(response.read()).hexdigest()
  check(actual==hashlib.sha256((src/path).read_bytes()).hexdigest(),'hash '+path);r['hashes'].append({'path':path,'sha256':actual})
 with sync_playwright() as w:
  b=w.chromium.launch(**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}),args=['--no-sandbox']);p=b.new_page(reduced_motion='reduce');p.on('pageerror',lambda e:r['errors'].append(str(e)))
  for width in [320,390,1170]:
   p.set_viewport_size({'width':width,'height':844});p.goto(base+'review/relationship-map/index.html?map=structure&theme=green&still=1',wait_until='networkidle');p.wait_for_function('window.MapCamera');model=p.evaluate('MapSemantics.snapshot()');nodes={n['id']:n for n in model['nodes']}
   for n in nodes.values():
    if n['parent']:check(n['depth']==nodes[n['parent']]['depth']+1,'parent depth')
    if n['type']=='intermediate':check(not n['clickable'],'intermediate is not clickable')
   check(set(n['depth'] for n in nodes.values() if n['type']=='terminal')=={2,3,5,6},'same graph has unequal terminal depths')
   check(any(len(n['children'])==1 for n in nodes.values()) and any(len(n['children'])>1 for n in nodes.values()),'single and multiple children')
   check(p.locator('[data-kind=leaf]:visible').count()==0,'overview has no terminal hotspots');check(p.locator('.semantic-joint[tabindex]').count()==0,'no intermediate focus targets')
   attachment=p.evaluate('''()=>RelationshipArt.branches.flatMap(b=>b.nodeSpecs.filter(n=>n.parent!=='root').map(n=>{const parent=MapSemantics.by.get(n.parent),pts=b.vines[n.path].pts;return {id:n.id,distance:Math.hypot(pts[0][0]-parent.point[0],pts[0][1]-parent.point[1])}}))''');check(all(x['distance']<.0001 for x in attachment),'exact parent-node attachment')
   if width==390:
    r['model']=model;r['attachments']=attachment;p.screenshot(path=str(a.output/'overview.png'))
    curves=p.evaluate('RelationshipArt.branches.flatMap(b=>b.paths.map(p=>({id:p.semanticNode.id,points:p.poly.p})))');crossings=[]
    for i,c in enumerate(curves):
     for d in curves[i+1:]:
      for A,B in zip(c['points'],c['points'][1:]):
       for C,D in zip(d['points'],d['points'][1:]):
        hit=intersect(A,B,C,D)
        if hit:crossings.append([c['id'],d['id'],hit])
    check(not crossings,'semantic graph crossings');r['crossings']=crossings

   p.locator('[data-kind=branch][data-branch=deep]').click()
   for depth in range(2,7):
    if depth>2:p.locator('[data-camera=in]').click()
    p.wait_for_timeout(35);check(p.evaluate('MapCamera.state().depth')==depth,'zoom depth '+str(depth));visible=p.locator('[data-kind=leaf]:visible').evaluate_all('(es)=>es.map(e=>+e.dataset.depth)');check(all(d<=depth for d in visible),'no premature terminal')
    check(p.locator('[data-kind=leaf][aria-hidden=true]').evaluate_all('(es)=>es.every(e=>e.tabIndex===-1&&getComputedStyle(e).display==="none")'),'no hidden hotspots')
    paths=p.evaluate('''()=>RelationshipArt.branches.flatMap(b=>b.paths.map(p=>({depth:p.semanticNode.depth,branch:b.id,visible:p.gSet.some(s=>s.e.style.display!=='none')})))''');check(all(x['visible']==(x['branch']=='deep' and x['depth']<=depth) for x in paths),'path visibility follows actual depth')
    if width==390:p.screenshot(path=str(a.output/('depth-'+str(depth)+'.png')))
   for _ in range(4):p.locator('[data-camera=out]').click()
   p.wait_for_timeout(35);check(p.evaluate('MapCamera.state().depth')==2,'zoom out collapses deeper nodes');check(p.locator('[data-kind=leaf]:visible').count()==0,'hidden after zoom out')
   for n in nodes.values():
    if n['type']!='terminal':continue
    p.evaluate('(id)=>MapCamera.inspectNode(id)',n['id']);p.wait_for_timeout(35);hit=p.locator('[data-kind=leaf][data-node="'+n['id']+'"]');check(hit.is_visible(),'reachable terminal '+n['id']);before=p.evaluate('MapCamera.state()');collisions=p.evaluate('''()=>RelationshipArt.branches.filter(b=>b.id===MapCamera.state().current).flatMap(b=>b.items.filter(it=>it.g.style.display!=='none').flatMap(it=>{const r=it.tx.getBBox();return b.paths.filter(p=>p.semanticNode.depth<=MapCamera.state().depth&&p.poly.p.some(([x,y])=>x>r.x&&x<r.x+r.width&&y>r.y&&y<r.y+r.height)).map(p=>[it.semanticNode.id,p.semanticNode.id])}))''');check(not collisions,'line-label collision '+str(collisions));hit.click();check(p.locator('dialog').is_visible(),'terminal opens detail');check('真实深度：'+str(n['depth']) in p.locator('#detail-copy').inner_text(),'detail reports semantic depth');p.keyboard.press('Escape');after=p.evaluate('MapCamera.state()');check(all(before[k]==after[k] for k in ['x','y','k','current','depth']),'close preserves camera');check(p.evaluate('document.activeElement.dataset.node')==n['id'],'focus restored')
   p.locator('[data-camera=overview]').click();check(p.locator('[data-kind=leaf]:visible').count()==0,'return overview');r['checks'].append(str(width)+'px: depth 2–6 zoom, exact parents, every terminal detail/close/focus, hidden hotspots')
  p.set_viewport_size({'width':780,'height':1000});p.goto(base+'review/relationship-map/structure.html',wait_until='networkidle');f=p.locator('#study').element_handle().content_frame();f.wait_for_function('window.MapSemantics');p.locator('[data-node=pair-group]').click();f.locator('[data-camera=in]').click();f.wait_for_function("MapCamera.state().depth===3&&document.querySelector('#stage').dataset.depth==='3'");check(f.locator('[data-kind=leaf]:visible').count()==2,'both AB leaves visible')
  for A,B in [('present','present'),('unknown','present'),('unknown','unknown'),('present','unknown'),('present','present')]:
   p.select_option('[data-state=pair-a]',A);p.select_option('[data-state=pair-b]',B);states=f.evaluate('MapSemantics.snapshot()');pair={n['id']:n.get('state') for n in states['nodes'] if n.get('pair')};check(pair=={'pair-a':A,'pair-b':B},'AB independent state');check(states['pairs'][0]['exclusive'] is False and states['pairs'][0]['normalized'] is False,'AB coexistence');check(f.locator('[data-node=pair-a]').get_attribute('aria-label').find('有示例记录' if A=='present' else '未知')>=0,'visible accessible state')
  p.wait_for_timeout(100);p.screenshot(path=str(a.output/'paired-both.png'),full_page=True);check(f.evaluate('MapCamera.state().depth')==3,'AB depth survives capture');p.select_option('[data-state=pair-b]','unknown');p.screenshot(path=str(a.output/'paired-a-only.png'),full_page=True);r['checks'].append('A/B both, A only, B only and unknown independently represented; no normalization')
  p.locator('[data-node=deep-6a]').click();f.wait_for_function('MapCamera.state().depth===6');p.wait_for_timeout(100);p.screenshot(path=str(a.output/'study-depth6.png'),full_page=True)
  check(not r['errors'],'browser errors');r['passed']=True;b.close()
finally:
 (a.output/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
