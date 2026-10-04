"""Verify graph interactions against a URL; evidence remains outside the deployed site."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,json,hashlib,urllib.request,subprocess,os,time
ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
base=a.url.rstrip('/')+'/';source=Path(__file__).resolve().parents[1];result={'url':base,'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),'workingTreeModified':bool(subprocess.check_output(['git','diff','--name-only'],cwd=source,text=True).strip()),'hashes':[],'checks':[],'errors':[],'passed':False}
try:
 for rel in ['prototype/product-surface.js','prototype/product.css','prototype/app.js']+['review/relationship-map/'+n for n in ['index.html','camera.js','camera.css','models.js','semantics.js','theme.js','assets/leaf-node.png']]:
  expected=hashlib.sha256((source/rel).read_bytes()).hexdigest()
  with urllib.request.urlopen(base+rel+'?profile_check='+str(time.time_ns()),timeout=25) as r:actual=hashlib.sha256(r.read()).hexdigest()
  assert expected==actual,rel;result['hashes'].append({'path':rel,'sha256':actual})
 with sync_playwright() as w:
  b=w.chromium.launch(**({'executable_path':os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}),args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:result['errors'].append(str(e)));p.goto(base+'prototype/index.html?theme=green#assistant',wait_until='networkidle');p.wait_for_function('window.Ambient&&window.App');p.evaluate('window.__canvas=document.querySelector("#ambient-background canvas")');assert p.evaluate('!!window.__canvas');start=p.evaluate('Ambient.getTime()');before=p.evaluate('App.snapshot');assert p.locator('[data-action=profile-group]').count()==4
  for group,mode in [('traits','traits'),('relationships','relationships'),('observations','personal'),('completion','completion')]:
   tab=p.locator('[data-action=profile-group][data-id='+group+']');tab.focus();p.keyboard.press('Enter');assert tab.get_attribute('aria-pressed')=='true';f=p.locator('.profile-tendencies iframe').element_handle().content_frame();f.wait_for_function('window.MapCamera');assert f.evaluate('MapModel.type')==mode;assert f.evaluate('!MapSemantics.research&&Math.max(...MapSemantics.nodes.map(n=>n.depth))===2&&!MapSemantics.setState("pair-a","present")');assert f.locator('[data-kind=leaf]:visible').count()==0
   p.screenshot(path=str(a.output/(group+'-overview.png')),full_page=True)
   f.locator('[data-kind=branch]').first.click();leaf=f.locator('[data-kind=leaf]:visible').first;leaf.wait_for();state=f.evaluate('MapCamera.state()');leaf.click();p.locator('.dialog').wait_for();p.screenshot(path=str(a.output/(group+'-detail.png')));p.keyboard.press('Escape');assert p.locator('.dialog').count()==0;after=f.evaluate('MapCamera.state()');assert all(state[k]==after[k] for k in ['x','y','k','current']);assert f.evaluate('Ambient.isPaused()');f.locator('#fit').click() if f.locator('#fit').count() else f.get_by_role('button',name='全图',exact=True).click();assert f.locator('[data-kind=leaf]:visible').count()==0
   if group=='relationships':
    summary=p.locator('.profile-text-list>summary');assert not p.locator('.relationship-dimensions').is_visible();summary.focus();p.keyboard.press('Enter');assert p.locator('.relationship-dimensions').is_visible();assert p.locator('.relationship-dimensions [data-route=relationship-detail]').count()==8;summary.click()
   result['checks'].append(group+': keyboard switch, overview, focus, leaf dialog, unchanged camera on close, return to overview')
  assert p.evaluate('window.__canvas===document.querySelector("#ambient-background canvas")');assert p.evaluate('Ambient.getTime()')>start;after=p.evaluate('App.snapshot');assert before['sessions']==after['sessions'] and before['observations']==after['observations'];result['checks'].append('same background canvas with continuous time and unchanged user records')
  p.locator('[data-action=profile-group][data-id=observations]').click();assert p.locator('.profile-tendencies>h2').inner_text()=='个人画像';p.set_viewport_size({'width':320,'height':740});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(a.output/'personal-320.png'));p.emulate_media(reduced_motion='reduce');p.reload(wait_until='networkidle');assert p.evaluate('Ambient.isPaused()');assert not result['errors'];result['passed']=True;b.close()
finally:
 (a.output/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
