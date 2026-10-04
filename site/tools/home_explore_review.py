"""Home / local topic catalog browser checks. No real user data or remote services."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,sys,os
root=Path(sys.argv[1] if len(sys.argv)>1 else 'site').resolve();out=Path(sys.argv[2] if len(sys.argv)>2 else '/tmp/home-explore-review');out.mkdir(parents=True,exist_ok=True)
class Q(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Q,directory=str(root)));Thread(target=s.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{s.server_port}/prototype/index.html'
checks=[];matrix=[];errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox']);c=b.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(5000)
 def go(route='explore',theme='sunrise'):
  p.goto(url+f'?reset=1&theme={theme}#{route}');p.wait_for_function('window.App');p.wait_for_timeout(50)
 def ids():return p.locator('.decision-card').evaluate_all('(es)=>es.map(e=>e.dataset.id)')
 def click(action,id=None):p.locator('[data-action="'+action+'"]'+('[data-id="'+id+'"]' if id else '')).click()
 go();assert p.locator('.explore-intro button,.explore-intro a,.explore-intro [tabindex]').count()==0;assert p.locator('#topic-search-panel').is_hidden();assert len(ids())==8
 click('toggle-topic-search');assert p.locator('#explore-search').evaluate('(e)=>e===document.activeElement');inp=p.locator('#explore-search')
 cases={'辞职':['work-move','unpaid-break'],'考研':['exam-retake'],'  读研  ':['exam-retake'],'跳槽':['work-move'],'搬家':['independent-home'],'火星移民':[],'辞职 考研':[]}
 for query,expected in cases.items():inp.fill(query);assert ids()==expected,(query,ids());checks.append({'query':query,'ids':ids()})
 inp.fill('考研');click('category','工作');assert not ids();assert '工作 · 0' in p.locator('.explore-result-count').inner_text();click('clear-filters');assert len(ids())==8 and inp.input_value()=='';assert inp.evaluate('(e)=>e===document.activeElement')
 # Composition must retain previous results and the original input DOM until committed.
 inp.fill('辞职');before=ids();p.evaluate('window.savedInput=document.querySelector("#explore-search")')
 inp.dispatch_event('compositionstart');inp.evaluate("e=>{e.value='kaoyan';e.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true}));}");assert ids()==before
 inp.dispatch_event('keydown',{'key':'Enter','isComposing':True});assert ids()==before
 inp.evaluate("e=>{e.value='考研';e.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:'考研'}));}");assert ids()==['exam-retake'];assert p.evaluate('savedInput===document.querySelector("#explore-search")')
 click('clear-search');assert len(ids())==8 and inp.input_value()=='';assert inp.evaluate('(e)=>e===document.activeElement');assert p.locator('[data-action=clear-search]').is_hidden()
 assert p.evaluate("DecisionScenes.normalize('  ＡＢＣ　 １２３  ')")=='abc 123'
 # Query stays in memory across navigation, but never in URL or saved snapshot.
 inp.fill('研究生');click('nav','exam-retake');p.go_back();p.wait_for_function('App.currentRoute==="explore"');assert p.locator('#explore-search').input_value()=='研究生'
 assert '研究生' not in p.url;assert p.evaluate('Object.keys(localStorage).filter(k=>k.startsWith("jianji-design-v4:")).every(k=>JSON.parse(localStorage.getItem(k)).exploreSearch==="")')
 p.reload();assert p.locator('#topic-search-panel').is_hidden();assert len(ids())==8
 # Loaded local resources remain functional offline; cold-start caching is outside this prototype.
 p.evaluate('window.ambientBefore=document.querySelector("#ambient-tide")');requests=[];p.on('request',lambda r:requests.append(r.url));c.set_offline(True);click('toggle-topic-search');p.locator('#explore-search').fill('考研');assert ids()==['exam-retake'];click('clear-search');click('category','生活');assert len(ids())==2
 click('nav','city-return');assert '留在大城市' in p.locator('main').inner_text();p.go_back();p.wait_for_function('App.currentRoute==="explore"');assert p.evaluate('ambientBefore===document.querySelector("#ambient-tide")');assert not requests,requests;c.set_offline(False)
 # Every theme and all target widths; shared actions and geometric bounds.
 themes=p.evaluate('D.themes.map(t=>t.id)')
 for width in [320,390,1440]:
  p.set_viewport_size({'width':width,'height':900})
  for theme in themes:
   go('home',theme);assert p.locator('.home-secondary-grid .home-path').count()==4;original=p.locator('.assessment-purpose').inner_text();r=p.locator('.home-assessment-start').bounding_box();click('mode','ai');ai=p.locator('.assessment-purpose').inner_text();r2=p.locator('.home-assessment-start').bounding_box();assert original!=ai;assert p.locator('.home-assessment-start').is_disabled()
   image=p.locator('.home-portrait img').evaluate('(e)=>({fit:getComputedStyle(e).objectFit,src:e.getAttribute("src")})');assert image['fit']=='contain';assert 'original-person' in image['src'];assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
   if theme in ['sunrise','nebula']:
    p.screenshot(path=str(out/f'{width}-{theme}-home-ai.png'),full_page=True);click('mode','original');p.screenshot(path=str(out/f'{width}-{theme}-home-original.png'),full_page=True)
   p.evaluate('location.hash="explore"');p.wait_for_function('App.currentRoute==="explore"');assert len(ids())==8
   geometry=p.locator('.decision-card').evaluate_all('(es)=>es.map(e=>({w:e.clientWidth,h:e.clientHeight,sh:e.scrollHeight}))');columns=len(p.locator('.decision-grid').evaluate('e=>getComputedStyle(e).gridTemplateColumns').split());assert columns==(1 if width<380 else 2),(width,theme,columns);assert all(x['sh']<=x['h']+2 and (x['w']>x['h'] if columns==1 else .98<=x['w']/x['h']<=1.02) for x in geometry),(width,theme,geometry);assert p.locator('.decision-title,.decision-description').evaluate_all('(es)=>es.every(e=>e.scrollWidth<=e.clientWidth+1&&e.scrollHeight<=e.clientHeight+1)');assert not p.evaluate('document.documentElement.scrollWidth>innerWidth');assert p.locator('.decision-symbol svg').count()==8
   contrasts=p.evaluate('''()=>{const cvs=document.createElement('canvas'),ctx=cvs.getContext('2d');function rgb(c){ctx.clearRect(0,0,1,1);ctx.fillStyle=c;ctx.fillRect(0,0,1,1);return [...ctx.getImageData(0,0,1,1).data].slice(0,3)}function lum(c){return rgb(c).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0)}const bg=lum(getComputedStyle(document.querySelector('.decision-card')).backgroundColor);return ['.decision-title','.decision-description','.decision-category'].map(s=>{const fg=lum(getComputedStyle(document.querySelector(s)).color);return {selector:s,ratio:(Math.max(bg,fg)+.05)/(Math.min(bg,fg)+.05)}})}''');assert all(x['ratio']>=4.5 for x in contrasts),(theme,contrasts)
   if theme in ['sunrise','nebula']:p.screenshot(path=str(out/f'{width}-{theme}-explore.png'),full_page=True)
   matrix.append({'width':width,'theme':theme,'cards':len(geometry),'columns':columns,'cardGeometry':geometry,'cardContrast':contrasts,'homeCTAShiftPx':round(r2['y']-r['y'],2)})
 go();click('toggle-topic-search');p.locator('#explore-search').fill('火星移民');p.screenshot(path=str(out/'empty.png'),full_page=True);p.locator('[data-action=clear-filters]').focus();p.keyboard.press('Enter');assert len(ids())==8
 # Active ambient clock survives route change and filter updates; reduce-motion pauses it.
 p.emulate_media(reduced_motion='no-preference');p.evaluate('Ambient.resume();window.clock=Ambient.getTime();window.canvas=document.querySelector("#ambient-tide")');p.wait_for_timeout(150);p.evaluate('location.hash="home"');p.wait_for_function('App.currentRoute==="home"');assert p.evaluate('canvas===document.querySelector("#ambient-tide")&&Ambient.getTime()>=clock');p.emulate_media(reduced_motion='reduce');p.wait_for_function('Ambient.isPaused()')
 assert not errors,errors;b.close()
s.shutdown();(out/'report.json').write_text(json.dumps({'searchCases':checks,'matrix':matrix,'errors':errors,'checks':{'IME':True,'clearFocus':True,'offlineAfterLoadNoRequests':True,'queryNotPersistedOrInURL':True,'categoryAndQuery':True,'keyboard':True,'ambientContinuity':True,'reducedMotion':True},'limits':['No cold-start offline cache added','IME events simulated in Chromium, not physical keyboards','No formal accessibility certification']},ensure_ascii=False,indent=2));print(json.dumps({'states':len(matrix),'searchCases':len(checks),'errors':errors}))
