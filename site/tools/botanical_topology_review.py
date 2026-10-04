"""Candidate-only geometry, semantic tree and native-browser evidence; output stays outside site."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import argparse,json,math,shutil
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);parser.add_argument('--url');parser.add_argument('--quick',action='store_true');args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(Path(__file__).resolve().parents[1])));Thread(target=server.serve_forever,daemon=True).start();url=args.url or f'http://127.0.0.1:{server.server_port}/review/botanical-tree/'
def at(q,t):
 u=1-t;return [u**3*q[0][i]+3*u*u*t*q[1][i]+3*u*t*t*q[2][i]+t**3*q[3][i] for i in [0,1]]
def cross(a,b,c,d):
 if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]) or max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]):return None
 ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c[0],d[1]-c[1];den=ux*vy-uy*vx
 if abs(den)<1e-10:return None
 wx,wy=c[0]-a[0],c[1]-a[1];t=(wx*vy-wy*vx)/den;u=(wx*uy-wy*ux)/den
 return [a[0]+t*ux,a[1]+t*uy] if 0<t<1 and 0<u<1 else None
geometry=[];screens=[];errors=[];failures=[]
def check_geometry(m,name):
 nodes={n['id']:n for n in m['nodes']};edges=m['edges'];samples={e['id']:[at(e['q'],i/120) for i in range(121)] for e in edges};hits=[];sector=[];inward=[]
 for e in edges:
  root=nodes[e['rootId']];ps=samples[e['id']];last=0
  for p in ps:
   r=math.hypot(*p)
   if r+1e-5<last:inward.append(e['id']);break
   last=r
   if r>28:
    a=math.atan2(p[1],p[0]);da=math.atan2(math.sin(a-root['angle']),math.cos(a-root['angle']))
    if da<root['lo']-root['angle']-1e-6 or da>root['hi']-root['angle']+1e-6:sector.append(e['id']);break
 for i,e in enumerate(edges):
  for f in edges[i+1:]:
   shared=set([e['parent'],e['child']])&set([f['parent'],f['child']]);a=samples[e['id']];b=samples[f['id']]
   for A,B in zip(a,a[1:]):
    for C,D in zip(b,b[1:]):
     p=cross(A,B,C,D)
     if p and not any(math.dist(p,nodes[n]['p'])<=28 for n in shared):hits.append([e['id'],f['id'],p])
 r={'name':name,'nodes':len(nodes),'edges':len(edges),'maxDepth':max(n['depth'] for n in nodes.values()),'crossings':hits,'sectorEscapes':sector,'inwardEdges':inward,'commonNodeExclusionWorldRadius':28};geometry.append(r);assert not hits and not sector and not inward,r
with sync_playwright() as w:
 b=w.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 def pause():p.wait_for_timeout(300)
 def capture(name):
  p.locator('#viewport').scroll_into_view_if_needed();p.mouse.move(0,0);p.locator('#viewport').screenshot(path=str(out/(name+'.png')));r=p.evaluate('''()=>{const v=document.querySelector('#viewport').getBoundingClientRect(),nodes=[...document.querySelectorAll('.tree-node:not([hidden])')],labels=[...document.querySelectorAll('.tree-label:not([hidden])')],paths=BotanicalTree.rendered(),hits=[],targetHits=[];for(const e of paths)for(const n of BotanicalTree.layout()){if(n.id!==e.parent&&n.id!==e.child&&e.samples.some(p=>Math.hypot(p[0]-n.x,p[1]-n.y)<n.size/2))targetHits.push([e.id,n.id])}for(const l of labels){const r=l.getBoundingClientRect();for(const e of paths)if(e.samples.some(p=>p[0]>r.x-v.x&&p[0]<r.right-v.x&&p[1]>r.y-v.y&&p[1]<r.bottom-v.y))hits.push([l.dataset.label,e.id])}return {visible:BotanicalTree.layout(),lineTextHits:hits,targetHits,ghosts:[...document.querySelectorAll('.tree-node[hidden]')].filter(e=>e.tabIndex!==-1).length,nontransparent:labels.filter(e=>getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)').length,masks:document.querySelectorAll('#branches mask').length,decorations:document.querySelectorAll('#viewport img,.corner-art,[data-decoration]').length,overflow:document.documentElement.scrollWidth>innerWidth}}''');r['name']=name;screens.append(r);(out/'progress.json').write_text(json.dumps({'geometry':geometry,'states':screens},ensure_ascii=False));assert not r['targetHits'] and not r['lineTextHits'] and not r['ghosts'] and not r['nontransparent'] and not r['masks'] and not r['decorations'] and not r['overflow'],r
 for width in ([390] if args.quick else [320,390,430,1170]):
  p.set_viewport_size({'width':width,'height':1000 if width<500 else 850})
  for count in ([8,12] if args.quick else [8,6,7,12]):
   p.goto(url+f'?structure={count}');p.wait_for_function('window.BotanicalTree');pause();prefix=f'{width}-{count}'
   if width==390:check_geometry(p.evaluate('BotanicalTree.topology()'),str(count))
   capture(prefix+'-overview');p.locator('#zoom-out').click();pause();capture(prefix+'-minimum');p.locator('#fit').click();pause();p.locator('#zoom-in').click();pause();capture(prefix+'-names')
   id='planning' if count==8 else 'layout4';p.evaluate('(id)=>BotanicalTree.inspect(id)',id);pause();p.locator('[data-expand-node]').click();pause();capture(prefix+'-expanded');p.locator('#zoom-out').scroll_into_view_if_needed();box=p.locator('#zoom-out').bounding_box();y=p.evaluate('scrollY');p.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2);pause();s=p.evaluate('BotanicalTree.snapshot()');assert s['x']==0 and s['y']==0;assert abs(p.evaluate('scrollY')-y)<2
   if count!=8:
    p.evaluate('BotanicalTree.inspect("layout4/d6")');pause();p.screenshot(path=str(out/(prefix+'-deep6-sheet.png')),full_page=True);before=p.evaluate('BotanicalTree.snapshot()');p.keyboard.press('Escape');after=p.evaluate('BotanicalTree.snapshot()');assert all(before[k]==after[k] for k in ['x','y','k','selected']);capture(prefix+'-deep6');assert any(n['depth']==6 for n in after and p.evaluate('BotanicalTree.layout()'))
   p.locator('#fit').click();pause();p.locator('.demo-frame summary').click();p.check('#long-labels');p.locator('.demo-frame summary').click();capture(prefix+'-long')
  for tab in ['traits','personal']:
   p.goto(url);p.wait_for_function('window.BotanicalTree');p.locator('#tab-'+tab).click();pause();capture(f'{width}-{tab}-overview')
   if width==390:check_geometry(p.evaluate('BotanicalTree.topology()'),tab)
   id='group0' if tab=='traits' else 'rhythm';p.locator('[data-node="'+id+'"]').click();p.locator('[data-expand-node]').click();pause();capture(f'{width}-{tab}-expanded')
 # Every node remains reachable from the ordinary name index; no synthetic choice widgets.
 p.goto(url+'?structure=12');p.wait_for_function('window.BotanicalTree');all_nodes=p.evaluate('BotanicalTree.topology().nodes.filter(n=>n.depth).map(n=>n.id)')
 for id in all_nodes:
  p.locator('.text-index summary').click();p.locator('[data-select="'+id+'"]').click();pause();assert p.locator('#node-popover').evaluate('(e)=>e.matches(":popover-open")');assert p.evaluate('BotanicalTree.snapshot().selected')==id;assert not p.locator('#node-popover input,#node-popover select').count();p.keyboard.press('Escape');p.locator('.text-index summary').click()
 p.locator('#fit').click();pause();n=p.locator('[data-node=layout0]');n.focus();p.keyboard.press('Enter');assert p.locator('#node-popover').evaluate('(e)=>e.matches(":popover-open")');p.keyboard.press('Escape');assert p.locator(':focus').get_attribute('data-node')=='layout0'
 # Drag/pinch are browser pointer events; popup dismissal must not change the viewport.
 p.locator('#fit').click();pause();r=p.locator('#viewport').bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2;p.mouse.move(x,y);p.mouse.down();p.mouse.move(x+60,y+35,steps=6);p.mouse.up();pause();assert abs(p.evaluate('BotanicalTree.snapshot().x'))>40;p.locator('#fit').click();pause()
 p.locator('#tab-personal').click();p.locator('[data-node=visibility]').click();assert '只能有一个' in p.locator('#node-popover').inner_text();p.keyboard.press('Escape');p.locator('[data-node=rhythm]').click();assert '同时存在' in p.locator('#node-popover').inner_text();p.keyboard.press('Escape');p.locator('[data-node=evidence]').click();assert '不代表人格高低' in p.locator('#node-popover').inner_text();p.keyboard.press('Escape')
 p.locator('#tab-traits').click();p.evaluate('BotanicalTree.inspect("group0/A")');pause();assert '较低' in p.locator('#node-popover').inner_text() and '没有有效量表' in p.locator('#node-popover').inner_text();p.keyboard.press('Escape')
 touch=b.new_context(viewport={'width':390,'height':1000},is_mobile=True,has_touch=True);q=touch.new_page();q.goto(url);q.wait_for_function('window.BotanicalTree');cdp=touch.new_cdp_session(q);r=q.locator('#viewport').bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
 def points(dx):return [{'x':x-dx,'y':y,'id':1},{'x':x+dx,'y':y,'id':2}]
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':points(40)});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':points(80)});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});q.wait_for_timeout(300);assert q.evaluate('BotanicalTree.snapshot().k')>1.5;touch.close()
 p.locator('.demo-frame summary').click();p.wait_for_function('document.querySelectorAll("#theme option").length===13');p.evaluate('window.originalCanvas=document.querySelector("#ambient-tide");localStorage.setItem("sentinel","kept")')
 for value in p.locator('#theme option').evaluate_all('(es)=>es.map(e=>e.value)'):p.select_option('#theme',value)
 p.select_option('#theme','study');p.locator('.demo-frame summary').click();p.emulate_media(reduced_motion='reduce');p.wait_for_function('Ambient.isPaused()');assert p.evaluate('originalCanvas===document.querySelector("#ambient-tide")&&localStorage.getItem("sentinel")==="kept"');assert not errors,errors;b.close()
report={'geometry':geometry,'states':screens,'errors':errors,'allAnonymousNodesReachable':len(all_nodes),'limits':['Chromium only','28 world-unit exclusion around shared graph endpoint; no exclusion for unrelated paths','Geometry sampled at 120 segments per unmasked cubic; analytical sector construction also constrains the full Bezier hull','No physical-device or screen-reader certification']};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'states':len(screens),'geometryModels':len(geometry),'allNodesReachable':len(all_nodes),'errors':errors}))
