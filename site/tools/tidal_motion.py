"""Real browser motion contract. Synthetic fixtures only; records a full natural cycle.
Requires Playwright Chromium and Pillow. Run: python tools/tidal_motion.py <site-root>.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
from PIL import Image,ImageChops
import json,math,os,sys,traceback
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=ROOT/'qa'/'six-paths-motion';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start()
BASE='https://zhiyuxinxi.github.io'
results=[]
def check(x,message):
 if not x:raise AssertionError(message)
def goto(p,route='home',theme='sunrise',scenario='default'):
 p.goto(f'{BASE}/prototype/index.html?reset=1&scenario={scenario}&theme={theme}#{route}',wait_until='networkidle');p.wait_for_function('window.App&&App.snapshot')
def clock(p):return p.evaluate("document.getElementById('ambient-tide').getCurrentTime()")
def phase(p,t):
 p.evaluate("t=>{let s=document.getElementById('ambient-tide');s.pauseAnimations();s.setCurrentTime(t)}",t);p.wait_for_timeout(50)
def capture(p,name):p.screenshot(path=str(OUT/(name+'.png')))
def metric(path,colors,paper,opacity):
 rgb=lambda h:tuple(int(h.lstrip('#')[i:i+2],16) for i in [0,2,4])
 anchors=[tuple(round(opacity*a+(1-opacity)*b) for a,b in zip(rgb(c),rgb(paper))) for c in colors]
 im=Image.open(path).convert('RGB');im=im.crop((3,3,im.width-12,im.height-3)).resize((100,200))
 labels=[min(range(3),key=lambda k:sum((pixel[i]-anchors[k][i])**2 for i in range(3)))for pixel in im.getdata()]
 coverage=[labels.count(i)/len(labels) for i in range(3)]
 edges=[]
 for x in [20,50,80]:
  ys=[y for y in range(200) if labels[y*100+x]==1]
  edges.append(sum(ys)/len(ys)/200 if ys else None)
 return {'coverage':coverage,'boundaryAt20_50_80':edges,'centroidA':[sum(i%100 for i,k in enumerate(labels) if k==0)/labels.count(0)/100,sum(i//100 for i,k in enumerate(labels) if k==0)/labels.count(0)/200]}
with sync_playwright() as w:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**args)
 # Natural, uninterrupted time: full product video plus quarter-cycle frames.
 ctx=b.new_context(viewport={'width':390,'height':844},locale='zh-CN',reduced_motion='no-preference',record_video_dir=str(OUT/'video'),record_video_size={'width':390,'height':844})
 p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  goto(p,theme='lime');p.evaluate("document.getElementById('ambient-tide').setCurrentTime(0)")
  geometry=lambda:p.locator('.v4-person-scene img,.home-scene h2,.home-primary').evaluate_all('(es)=>es.map(e=>JSON.stringify(e.getBoundingClientRect()))')
  first=geometry();samples=[]
  for index,target in enumerate([0,3.2,6.4,9.6,12.8,16,19.2,22.4,25.6,28.8,32]):
   p.wait_for_function('t=>document.getElementById("ambient-tide").getCurrentTime()>=t',arg=target,timeout=18000)
   capture(p,'cycle-'+str(index));samples.append(clock(p));check(first==geometry(),'Content moved with the background')
  check(not errors,str(errors));results.append({'test':'natural-32-second-decoupled-motion','status':'PASS','componentPeriodsSeconds':[16,23,19],'actualSampleTimes':samples,'contentGeometryStable':True})
 except Exception as e:results.append({'test':'natural-32-second-decoupled-motion','status':'FAIL','error':str(e)})
 video=p.video;ctx.close();video.save_as(str(OUT/'full-cycle.webm'));video.delete()
 # Dense angle sampling and cycle seam: smooth direction changes, no random jumps.
 ctx=b.new_context(viewport={'width':390,'height':844},reduced_motion='no-preference');p=ctx.new_page()
 try:
  goto(p);angles=[];motion=[]
  for i in range(129):
   phase(p,i/4);sample=p.evaluate("()=>{let a=document.getElementById('tide-field').transform.animVal.getItem(0).angle,m=document.getElementById('tide-offset').transform.animVal.getItem(0).matrix;return [a,m.e,m.f,document.getElementById('tide-front').getTotalLength()]}");angles.append(sample[0]);motion.append(sample)
  jumps=[abs(b-a) for a,b in zip(angles,angles[1:])]
  check(max(jumps)<18,'Direction jumped within 250ms');check(abs(angles[0]-angles[64])>5 and abs(angles[0]-angles[-1])>5,'Whole field repeats at 16/32 seconds')
  check(max(angles)-min(angles)>110,'Direction variation too narrow')
  check(all(max(abs(b-a) for a,b in zip(x,y))>.005 for x,y in zip(motion,motion[1:])), 'All motion tracks stopped together')
  results.append({'test':'continuous-multi-direction-angle-sampling','status':'PASS','sampleIntervalSeconds':.25,'angles':angles,'maximumStepDegrees':max(jumps),'trackSamplesAngleXYLength':motion,'noSynchronizedStops':True})
 except Exception as e:results.append({'test':'continuous-multi-direction-angle-sampling','status':'FAIL','error':str(e)})
 ctx.close()
 # Measure actual composited pixels at precise phases; hide content only for measurement.
 for theme in ['sunrise','candy','berry','lime','aurora','sea','nebula','amber']:
  ctx=b.new_context(viewport={'width':390,'height':844},locale='zh-CN',reduced_motion='no-preference');p=ctx.new_page()
  try:
   goto(p,theme=theme);p.add_style_tag(content='#app,#overlays,#notice{visibility:hidden!important}')
   tokens=p.evaluate("()=>{let c=getComputedStyle(document.body);return {colors:['a','b','c'].map(x=>c.getPropertyValue('--scene-'+x).trim()),paper:c.getPropertyValue('--paper').trim(),opacity:Number(getComputedStyle(document.getElementById('ambient-background')).opacity)}}")
   rows=[]
   for i,t in enumerate([0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,41,53,67,83,101,127]):
    phase(p,t);name=f'field-{theme}-{i}';capture(p,name);rows.append({'time':t,**metric(OUT/(name+'.png'),**tokens)})
   for k in [0,2]:
    values=[r['coverage'][k] for r in rows];check(min(values)>=.18,f'{theme} primary color {k} vanished: {values}');check(max(values)-min(values)>=.12,f'{theme} coverage change too small: {values}')
   for later in [8,16]:
    check(sum(abs(rows[0]['centroidA'][k]-rows[later]['centroidA'][k]) for k in [0,1])>.06,'Rendered field repeats after 16/32 seconds')
   centers=[r['centroidA'] for r in rows]
   check(max(c[0] for c in centers)-min(c[0] for c in centers)>.18,'No meaningful horizontal movement')
   check(max(c[1] for c in centers)-min(c[1] for c in centers)>.14,'No meaningful vertical movement')
   vectors=[(b[0]-a[0],b[1]-a[1]) for a,b in zip(centers,centers[1:])]
   check(any(abs(a[0]*b[1]-a[1]*b[0])>.001 for a,b in zip(vectors,vectors[1:])),'Motion stayed on one axis')
   # The quiet assessment gets neither moving scenery nor its colors showing through.
   p.evaluate("location.hash='question?id=session-demo-seed'")
   goto(p,'question?id=session-demo-seed',theme,'question');t=clock(p);capture(p,'question-'+theme+'-0');p.wait_for_timeout(400);capture(p,'question-'+theme+'-1')
   check(p.locator('#ambient-background').evaluate("e=>getComputedStyle(e).visibility==='hidden'"),'Assessment scenery still visible')
   check(abs(clock(p)-t)<.03,'Assessment clock still running')
   check(ImageChops.difference(Image.open(OUT/f'question-{theme}-0.png'),Image.open(OUT/f'question-{theme}-1.png')).getbbox() is None,'Assessment pixels moved')
   results.append({'test':'pixels-and-assessment-'+theme,'status':'PASS','tokens':tokens,'phases':rows})
  except Exception as e:results.append({'test':'pixels-and-assessment-'+theme,'status':'FAIL','error':str(e),'trace':traceback.format_exc(limit=2)})
  ctx.close()
 # Object identity, route-independent rendering and uninterrupted clock through four tabs.
 ctx=b.new_context(viewport={'width':390,'height':844},locale='zh-CN',reduced_motion='no-preference');p=ctx.new_page()
 try:
  goto(p);p.evaluate("window.tideRefs=[document.getElementById('ambient-background'),document.getElementById('ambient-tide'),document.getElementById('tide-motion'),document.getElementById('tide-direction'),document.getElementById('tide-drift')]")
  style=lambda:p.evaluate("()=>{let e=document.getElementById('ambient-background'),c=getComputedStyle(e),s=getComputedStyle(document.body);return [c.opacity,c.backgroundImage,c.filter,...['a','b','c'].map(x=>s.getPropertyValue('--scene-'+x))]}")
  initial=style();transitions=[]
  for route in ['explore','assistant','me','home']:
   before=clock(p);p.click('[data-action=tab][data-route='+route+']');p.wait_for_function('r=>App.currentRoute===r',arg=route);after=clock(p)
   check(p.evaluate("['ambient-background','ambient-tide','tide-motion','tide-direction','tide-drift'].every((id,i)=>document.getElementById(id)===window.tideRefs[i])"),'Route rebuilt background')
   check(after>=before and after-before<2,'Route reset clock');check(style()==initial,'Route changed background rendering');transitions.append({'route':route,'before':before,'after':after})
  for route in ['settings','appearance','records','home']:
   before=clock(p);p.evaluate('r=>location.hash=r',route);p.wait_for_function('r=>App.currentRoute===r',arg=route);after=clock(p)
   check(p.evaluate("['ambient-background','ambient-tide','tide-motion','tide-direction','tide-drift'].every((id,i)=>document.getElementById(id)===window.tideRefs[i])"),'Subpage rebuilt background')
   check(after>=before and after-before<2 and style()==initial,'Subpage changed clock or rendering');transitions.append({'route':route,'before':before,'after':after})
  p.click('[data-action=start]');p.wait_for_function('App.currentRoute.startsWith("question")');q=clock(p);p.wait_for_timeout(500)
  check(abs(clock(p)-q)<.03,'Question failed to pause');p.click('[data-action=pause]');p.get_by_role('button',name='保存位置，返回认识').click();p.wait_for_function('App.currentRoute==="home"');p.wait_for_timeout(300)
  check(clock(p)>q and clock(p)-q<2,'Returning from question reset rather than resumed');check(p.evaluate("document.getElementById('ambient-tide')===window.tideRefs[1]"),'Question replaced background')
  # User setting AND system setting independently settle on the same balanced frame.
  p.click('[data-action=tab][data-route=me]');p.click('[data-route=settings]');p.click('[data-action=v3-preferences]');p.click('[data-action=v3-motion]');p.keyboard.press('Escape')
  check(p.evaluate('App.snapshot.reduced'),'Local preference not saved');check(abs(clock(p)-8)<.03,'Local reduced motion not balanced');p.wait_for_timeout(300);check(abs(clock(p)-8)<.03,'Local reduced motion moved');capture(p,'reduced-local')
  p.click('[data-action=v3-preferences]');p.click('[data-action=v3-motion]');p.keyboard.press('Escape');p.emulate_media(reduced_motion='reduce');p.wait_for_timeout(200)
  check(abs(clock(p)-8)<.03,'System reduced motion not balanced');p.wait_for_timeout(300);check(abs(clock(p)-8)<.03,'System reduced motion moved');capture(p,'reduced-system')
  results.append({'test':'identity-clock-routes-focus-and-reduced-motion','status':'PASS','transitions':transitions,'questionPausedAt':q,'reducedFixedAt':8})
 except Exception as e:results.append({'test':'identity-clock-routes-focus-and-reduced-motion','status':'FAIL','error':str(e),'trace':traceback.format_exc(limit=2)})
 ctx.close()
 # Key homepage entry reachability and original saved-note identity.
 for width in [320,390,430]:
  ctx=b.new_context(viewport={'width':width,'height':844},locale='zh-CN',reduced_motion='reduce');p=ctx.new_page()
  try:
   goto(p);check(p.locator('.home-path').count()==4,'Expected four secondary entries');check(p.locator('.home-primary').count()==2,'Expected equal primary entries');capture(p,'home-'+str(width))
   p.locator('.home-path[data-route=single-factor]').click();p.wait_for_selector('.factor-picker');p.click('[data-action=back]');p.wait_for_function('App.currentRoute==="home"')
   p.click('[data-action=tab][data-route=assistant]');p.wait_for_selector('#chat-draft');check(not p.evaluate('App.snapshot.conversations.length'),'Entry auto-sent to assistant')
   goto(p,'explore',scenario='topic-record');p.locator('.life-entry [data-route=topic-workspace]').click();p.wait_for_selector('.record-summary');check('id=topic-note-demo-v2' in p.evaluate('App.currentRoute'),'Exploration duplicated recent record')
   results.append({'test':'home-key-entries-'+str(width),'status':'PASS'})
  except Exception as e:results.append({'test':'home-key-entries-'+str(width),'status':'FAIL','error':str(e)})
  ctx.close()
 b.close()
report={'publicURL':BASE,'sourceSHA':'53bca5fe5f7cf03399d4a735eb1659c6f6e9d94c','capturedAt':datetime.now(timezone.utc).isoformat(),'passed':all(r['status']=='PASS' for r in results),'componentPeriodsSeconds':[16,23,19],'results':results,'syntheticOnly':True,'limits':['Browser emulation, not physical-device battery/GPU measurement.','Pixel coverage classifies nearest rendered theme anchor; blend region is classified as its nearest color.']}
(OUT/'motion-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
for r in results:print(r['status'],r['test'],r.get('error',''),flush=True)
server.shutdown()
if not report['passed']:raise SystemExit(1)
