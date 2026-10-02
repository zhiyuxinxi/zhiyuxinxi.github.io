"""Soft-field contract: actual RGB dominance, full-speed video, legibility and persistence.
Synthetic fixtures only. Run with CHROMIUM_PATH when using a system browser.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from datetime import datetime,timezone
from PIL import Image,ImageChops
import json,os,sys,traceback,math
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();OUT=ROOT/'qa'/'soft-fields-restored';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start();BASE='https://zhiyuxinxi.github.io'
results=[]
def check(ok,msg):
 if not ok:raise AssertionError(msg)
def goto(p,route='home',theme='sunrise',scenario='default'):
 p.goto(f'{BASE}/prototype/index.html?reset=1&scenario={scenario}&theme={theme}#{route}',wait_until='networkidle');p.wait_for_function('window.App&&App.snapshot&&window.Ambient')
def phase(p,t):p.evaluate('t=>Ambient.sample(t)',t);p.wait_for_timeout(60)
def shot(p,name):
 path=OUT/(name+'.png');p.screenshot(path=str(path));return path
def rgb(h):return tuple(int(h[i:i+2],16) for i in [1,3,5])
def metric(path,colors):
 a,b=map(rgb,colors);d=[b[i]-a[i] for i in range(3)];den=sum(v*v for v in d);im=Image.open(path).convert('RGB');im=im.crop((0,0,im.width-10,im.height)).resize((100,200));points=list(im.getdata());mix=[sum((p[i]-a[i])*d[i] for i in range(3))/den for p in points];mask=[v<.5 for v in mix];n=sum(mask)
 return {'dominanceA':n/len(mask),'dominanceB':1-n/len(mask),'coreA':sum(v<.35 for v in mix)/len(mask),'coreB':sum(v>.65 for v in mix)/len(mask),'blendBand':sum(.35<=v<=.65 for v in mix)/len(mask),'centroidA':[sum(i%100 for i,k in enumerate(mask) if k)/n/100,sum(i//100 for i,k in enumerate(mask) if k)/n/200]}
def lum(c):
 x=[v/255 for v in c];x=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in x];return sum(v*k for v,k in zip(x,[.2126,.7152,.0722]))
def contrast(p,name):
 p.wait_for_timeout(320)  # Let route scroll restoration settle before pixel coordinates.
 # Measure actual background pixels beneath visible text, not token pairs alone.
 runs=p.evaluate('''()=>{const out=[],w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const e=n.parentElement;if(!n.textContent.trim()||e.closest('svg,[aria-hidden=true],button:disabled'))continue;let r=document.createRange();r.selectNodeContents(n);const c=getComputedStyle(e);if(c.visibility!=='visible')continue;for(const b of r.getClientRects()){if(b.width<3||b.height<3||b.top<0||b.bottom>innerHeight-2||b.left<0||b.right>innerWidth-10)continue;const covered=[.2,.5,.8].some(fx=>[.3,.7].some(fy=>{const hit=document.elementFromPoint(b.x+b.width*fx,b.y+b.height*fy);return hit&&!e.contains(hit)}));if(covered)continue;out.push({text:n.textContent.trim().slice(0,60),color:c.color,size:parseFloat(c.fontSize),weight:parseInt(c.fontWeight)||400,x:b.x,y:b.y,w:b.width,h:b.height})}}return out}''')
 style=p.add_style_tag(content='#app *,#overlays *{transition:none!important;color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important}');path=shot(p,name+'-background-probe');style.evaluate('(e)=>e.remove()');p.wait_for_timeout(180);im=Image.open(path).convert('RGB');path.unlink();bad=[];minimum=99
 for r in runs:
  import re
  c=[float(x) for x in re.findall(r'[\d.]+',r['color'])];fg=c[:3];alpha=c[3] if len(c)>3 else 1
  ratios=[]
  for fx in [.2,.5,.8]:
   for fy in [.3,.7]:
    x=min(im.width-1,int(r['x']+r['w']*fx));y=min(im.height-1,int(r['y']+r['h']*fy));bg=im.getpixel((x,y));f=[fg[i]*alpha+bg[i]*(1-alpha) for i in range(3)];l1,l2=sorted([lum(f),lum(bg)]);ratios.append((l2+.05)/(l1+.05))
  ratio=min(ratios);minimum=min(minimum,ratio);target=3 if r['size']>=24 or (r['size']>=18.66 and r['weight']>=700) else 4.5
  if ratio<target-.03:bad.append({'text':r['text'],'ratio':round(ratio,2),'target':target})
 return {'runs':len(runs),'minimum':minimum,'failures':bad}
with sync_playwright() as w:
 args={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):args['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**args)
 # Record an actual uninterrupted area cycle with independent direction evolution.
 c=b.new_context(viewport={'width':390,'height':844},locale='zh-CN',record_video_dir=str(OUT/'video'),record_video_size={'width':390,'height':844});p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  goto(p,theme='lime');phase(p,0);p.evaluate('Ambient.resume()');rects=lambda:p.locator('.v4-person-scene img,.home-primary,.home-path').evaluate_all('(es)=>es.map(e=>JSON.stringify(e.getBoundingClientRect()))');start=rects();samples=[]
  for t in [0,4,8,12,16,20,24,28,32]:
   p.wait_for_function('t=>Ambient.getTime()>=t',arg=t,timeout=14000);shot(p,'natural-'+str(t));samples.append(p.evaluate('Ambient.getTime()'));check(rects()==start,'Content moved with field')
  check(not errors,str(errors));results.append({'test':'natural-cycle','status':'PASS','seconds':samples,'contentGeometryStable':True})
 except Exception as e:results.append({'test':'natural-cycle','status':'FAIL','error':str(e)})
 video=p.video;c.close();video.save_as(str(OUT/'natural-32-seconds.webm'));video.delete()
 for theme in ['sunrise','candy','berry','lime','aurora','sea','nebula','amber','green','peach','blue','violet']:
  c=b.new_context(viewport={'width':390,'height':844},locale='zh-CN');p=c.new_page();rows=[];legibility=[]
  try:
   goto(p,theme=theme);colors=p.evaluate("['--field-a','--field-b'].map(k=>getComputedStyle(document.body).getPropertyValue(k).trim())")
   hide=p.add_style_tag(content='#app,#overlays,#notice{visibility:hidden!important}')
   for t in [0,4,8,12,16,20,24,28,32,40,56,72,88,104,120,136]:
    phase(p,t);rows.append({'seconds':t,**metric(shot(p,f'field-{theme}-{t}'),colors)})
   hide.evaluate('(e)=>e.remove()');ratios=[r['dominanceA'] for r in rows]
   check(min(ratios)>=.145 and max(ratios)<=.855,f'15–85 bounds: {ratios}');check(min(ratios)<.19 and max(ratios)>.81,'Area fails to approach endpoints');check(min(r['coreA'] for r in rows)>.075 and min(r['coreB'] for r in rows)>.075,'Minor color lost in blend')
   centers=[r['centroidA'] for r in rows];check(max(c[0] for c in centers)-min(c[0] for c in centers)>.15 and max(c[1] for c in centers)-min(c[1] for c in centers)>.15,'Direction stayed fixed')
   for route in ['home','explore','assistant','me']:
    p.evaluate('r=>location.hash=r',route);p.wait_for_function('r=>App.currentRoute===r',arg=route)
    for t in [8,16,24]:
     phase(p,t);name=f'{theme}-{route}-{t}';shot(p,name);legibility.append({'route':route,'time':t,**contrast(p,name)})
   check(not [r for r in legibility if r['failures']],str([r for r in legibility if r['failures']]))
   goto(p,'question?id=session-demo-seed',theme,'question');q=p.evaluate('Ambient.getTime()');a=shot(p,'question-'+theme);p.wait_for_timeout(400);z=shot(p,'question-'+theme+'-later');check(ImageChops.difference(Image.open(a),Image.open(z)).getbbox() is None,'Question is moving');check(p.evaluate('Ambient.isPaused()') and p.evaluate('Ambient.getTime()')==q,'Question clock not paused')
   results.append({'test':'theme-'+theme,'status':'PASS','colors':colors,'pixels':rows,'contrast':legibility})
  except Exception as e:results.append({'test':'theme-'+theme,'status':'FAIL','error':str(e),'pixels':rows,'contrast':legibility})
  c.close()
 # Representative reading, input, modal, keyboard and deep-page states at extremes.
 for theme in ['sunrise','nebula','amber']:
  c=b.new_context(viewport={'width':320,'height':844},locale='zh-CN');p=c.new_page();checks=[]
  try:
   goto(p,theme=theme)
   for route in ['article?id=read-traits','report?id=report-sample-01','topic-workspace?topic=work-choice','assistant']:
    p.evaluate('r=>location.hash=r',route);p.wait_for_function('r=>App.currentRoute===r',arg=route);p.wait_for_timeout(400)
    for t in [8,24]:
     phase(p,t);name=f'deep-{theme}-{route.split("?")[0]}-{t}';shot(p,name);v=contrast(p,name);checks.append({'route':route,'phase':t,**v});check(not v['failures'],str(v['failures']))
    if route.startswith(('article','report')):
     p.evaluate('window.scrollTo(0,Math.min(720,document.body.scrollHeight-innerHeight))');shot(p,f'reading-{theme}-{route.split("?")[0]}');v=contrast(p,'reading-probe');checks.append({'route':route+'-scrolled',**v});check(not v['failures'],str(v['failures']))
   field=p.locator('.composer textarea');field.fill('合成验证：我希望保留输入，慢慢整理这一件事。');field.focus();check(field.evaluate("e=>getComputedStyle(e.closest('.composer')).outlineStyle!=='none'"),'Input focus invisible');shot(p,'input-'+theme)
   field_colors=field.evaluate("e=>({text:getComputedStyle(e).color,surface:getComputedStyle(e.closest('.composer')).backgroundColor,placeholder:getComputedStyle(e,'::placeholder').color})")
   import re
   parse=lambda s:[float(x) for x in re.findall(r'[\d.]+',s)][:3]
   for key in ['text','placeholder']:
    a,z=sorted([lum(parse(field_colors[key])),lum(parse(field_colors['surface']))]);check((z+.05)/(a+.05)>=4.5,'Input '+key+' contrast')
   p.locator('.source-btn').click();p.wait_for_selector('[role=dialog]');p.wait_for_timeout(350);shot(p,'modal-'+theme);v=contrast(p,'modal-probe');checks.append({'route':'source-modal',**v});check(not v['failures'],str(v['failures']));p.keyboard.press('Escape');check(p.locator('[role=dialog]').count()==0,'Escape did not close');check(field.input_value().startswith('合成验证'),'Modal lost input');check(p.locator('.source-btn').evaluate('e=>e===document.activeElement'),'Focus not restored')
   p.evaluate("location.hash='settings'");p.wait_for_selector('[data-action="font-size"][data-id="large"]');p.locator('[data-action="font-size"][data-id="large"]').click();p.evaluate("location.hash='assistant'");p.wait_for_selector('.composer textarea');check(p.locator('.composer textarea').input_value().startswith('合成验证'),'Settings lost input');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Large input overflow');shot(p,'large-input-'+theme)
   results.append({'test':'deep-input-reading-modal-'+theme,'status':'PASS','contrast':checks,'inputColors':field_colors})
  except Exception as e:results.append({'test':'deep-input-reading-modal-'+theme,'status':'FAIL','error':str(e),'contrast':checks})
  c.close()

 # Same canvas and clock survive all navigation, input remains intact, static preferences.
 c=b.new_context(viewport={'width':320,'height':760},locale='zh-CN');p=c.new_page()
 try:
  goto(p);aspect=[]
  colors=p.evaluate("['--field-a','--field-b'].map(k=>getComputedStyle(document.body).getPropertyValue(k).trim())")
  hide=p.add_style_tag(content='#app,#overlays,#notice{visibility:hidden!important}')
  for width in [320,430]:
   p.set_viewport_size({'width':width,'height':760})
   for t in [8,24]:
    phase(p,t);row=metric(shot(p,f'aspect-{width}-{t}'),colors);check(.145<=row['dominanceA']<=.855,'Aspect ratio coverage');aspect.append({'width':width,'time':t,**row})
  hide.evaluate('(e)=>e.remove()');p.set_viewport_size({'width':320,'height':760});p.evaluate('Ambient.resume()');p.evaluate('window.originalField=document.getElementById("ambient-tide")');before=p.evaluate('Ambient.getTime()')
  for route in ['explore','assistant','me','settings','appearance','records','home','single-factor','daily-checkin','short-16pf','personality-sandbox','ai-reset']:
   p.evaluate('r=>location.hash=r',route);p.wait_for_function('r=>App.currentRoute===r',arg=route);after=p.evaluate('Ambient.getTime()');check(after>=before,'Route reset clock');check(p.evaluate('document.getElementById("ambient-tide")===window.originalField'),'Canvas recreated');check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Narrow overflow '+route);before=after;shot(p,'narrow-'+route)
  p.emulate_media(reduced_motion='reduce');a=shot(p,'reduced');q=p.evaluate('Ambient.getTime()');p.wait_for_timeout(350);z=shot(p,'reduced-later');check(ImageChops.difference(Image.open(a),Image.open(z)).getbbox() is None,'Reduced motion moved');check(p.evaluate('Ambient.isPaused()') and p.evaluate('Ambient.getTime()')==q,'Reduced motion clock runs');p.emulate_media(reduced_motion='no-preference');p.wait_for_timeout(160);check(p.evaluate('Ambient.getTime()')>q,'Motion did not resume');results.append({'test':'persistent-navigation-narrow-reduced','status':'PASS','aspectRatioPixels':aspect})
 except Exception as e:results.append({'test':'persistent-navigation-narrow-reduced','status':'FAIL','error':str(e)})
 c.close();b.close()
server.shutdown();report={'generatedAt':datetime.now(timezone.utc).isoformat(),'metricDefinition':'Full viewport backdrop with content temporarily hidden; project actual RGB onto field-a→field-b segment. Projection <0.5 is A-dominant, >=0.5 B-dominant; central .35–.65 is additionally reported as blend, not counted as a third theme color. Excludes rightmost 10px scrollbar. Dominance bounds allow 0.5 percentage point raster tolerance. This does not claim opaque cards are visible backdrop.','results':results};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'results':[{'test':r['test'],'status':r['status'],'error':r.get('error')} for r in results]},ensure_ascii=False,indent=2));sys.exit(0 if all(r['status']=='PASS' for r in results) else 1)
