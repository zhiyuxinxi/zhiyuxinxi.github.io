"""Non-question copy and local behavior regressions; synthetic browser data only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
import json,os,sys
from playwright.sync_api import sync_playwright
from product_browser import ProductBrowser
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
results=[];errors=[]
def check(value,message):
 if not value:raise AssertionError(message)
def test(name,fn):
 try:fn();results.append({'test':name,'status':'PASS'})
 except Exception as e:results.append({'test':name,'status':'FAIL','error':str(e)})
 print(results[-1],flush=True)
with sync_playwright() as w:
 options={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):options['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**options);p=ProductBrowser(b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce',locale='zh-CN'));p.host.set_default_timeout(8000);p.on('pageerror',lambda e:errors.append(str(e)))
 def visit(route,theme='sunrise',reset=True):
  p.open_product(base,route,'sample-report' if route.split('?')[0] in ['report','share'] else 'default',theme,reset)
 def shot(name):p.screenshot(path=str(out/(name+'.png')),full_page=True)
 def records():
  visit('records');check('还没有留下记录' in p.locator('main').inner_text(),'all-empty copy');shot('records-empty')
  p.click('[data-route=journal]');p.fill('#journal-text','周一讨论我先听了一会儿；熟悉话题时，我不需要准备。');p.click('[data-action=save-journal]');p.click('[data-action=record-filter][data-id=全部答卷]');check('其他记录还在' in p.locator('main').inner_text(),'filtered-empty copy');shot('records-filtered-empty')
  p.locator('.entry-empty [data-action=record-filter]').focus();p.keyboard.press('Enter');check(p.locator('.record-item').count()==1,'clear filter');p.reload(wait_until='networkidle');check(p.evaluate('App.snapshot.observations.length')==1,'record retained')
 test('all-empty-filtered-empty-keyboard-and-reload',records)
 def sharing():
  for context in ['work','relationship']:
   visit('report');p.click('[data-action=report-context][data-id='+context+']');p.fill('#report-note','私人测试观察，不应出现在分享图');p.click('[data-action=save-report-note]');p.click('[data-route=share]');sample=p.evaluate('UI.sampleShare(App.snapshot.reportContext)');check(sample['context'] in p.locator('#share-preview').inner_text(),'preview context')
   with p.expect_download() as wait:p.click('[data-action=export-share]')
   download=wait.value;file=out/(context+'-share.svg');download.save_as(file);svg=file.read_text();check(all(x in svg for x in sample['lines']+[sample['body'],sample['context']]),'download differs');check('私人测试观察' not in svg,'private text included');shot('share-'+context)
 test('both-share-contexts-preview-download-and-personal-isolation',sharing)
 def article():
  visit('article');excerpt=p.locator('#article-excerpt').inner_text();p.get_by_role('button',name='引用这段聚会情境',exact=True).click();sources=p.evaluate('App.snapshot.assistantSources');check(len(sources)==1 and sources[0]['excerpt']==excerpt,'wrong excerpt');check(p.evaluate('App.snapshot.conversations.length')==0,'unexpected send')
 test('fixed-article-quote-no-auto-send',article)
 def importing():
  visit('data');p.click('[data-action=import-spec]');check('5 MB' in p.locator('[role=dialog]').inner_text(),'import scope');p.keyboard.press('Escape');p.click('[data-action=v4-import]');p.locator('#v4-import-file').set_input_files({'name':'broken.json','mimeType':'application/json','buffer':b'{broken'});p.wait_for_function("document.getElementById('v4-import-status').textContent.includes('重新选择')");shot('import-readable-error');check(p.locator('#v4-import-file').is_visible(),'cannot retry');check(p.evaluate('App.snapshot.observations.length')==0,'failed import mutated records')
 test('import-scope-and-persistent-recoverable-json-error',importing)
 def source():
  visit('report');p.click('[data-action=report-context][data-id=relationship]');p.click('[data-action=source-report]');text=p.locator('[role=dialog]').inner_text();check('人际相处' in text and '虚构报告样例' in text,'localized provenance');check('sample-report' not in text and 'report-sample-01' not in text,'technical IDs leak');shot('source-relationship')
 test('readable-source-with-context-and-version',source)
 def action_history():
  visit('report');p.click('[data-action=add-action]');p.fill('#dialog-field','讨论前写两点，试一次再观察');p.click('[data-action=submit-dialog]');p.wait_for_selector('[data-action=action-outcome]');aid=p.evaluate('App.snapshot.actions[0].id')
  p.click('[data-action=action-outcome][data-outcome=not-yet]');p.click('[data-action=save-action-review]');a=p.evaluate('App.snapshot.actions[0]');check(a['status']=='active' and len(a['reviews'])==1,'not-yet must stay active')
  p.click('[data-action=action-outcome][data-outcome=partial]');p.fill('#action-observation','只试了一点；还要看当时的情境。');p.click('[data-action=save-action-review]');a=p.evaluate('App.snapshot.actions[0]');history=a['reviews'];check(a['status']=='reviewed' and len(history)==2,'partial review');p.click('[data-action=restart-action]');p.reload(wait_until='networkidle');a=p.evaluate('App.snapshot.actions[0]');check(a['id']==aid and a['status']=='active' and a['reviews']==history,'restart lost history');shot('action-restarted-history')
  p.click('[data-action=cancel-action]');p.click('[data-action=confirm-dialog]');p.click('[data-action=restart-action]');check(p.evaluate('App.snapshot.actions[0].reviews')==history,'put-down restart lost history')
 test('not-yet-reviewed-restart-and-put-down-preserve-history',action_history)
 def failed_observation():
  visit('report');p.evaluate("()=>{window.savedSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error('synthetic-copy-failure')}}");p.fill('#report-note','这段解释不太像我，我想保留不同的情境。');p.click('[data-action=save-report-note]');check(p.evaluate('App.snapshot.reportNotes.length')==0,'failed save mutated records');check('已保存本人观察' not in p.locator('#notice').inner_text(),'false success');check(p.input_value('#report-note').startswith('这段解释不太像我'),'failed input lost');shot('report-save-failure');p.evaluate('()=>{Storage.prototype.setItem=window.savedSetItem;}');p.click('[data-action=retry-drafts]');p.click('[data-action=save-report-note]');p.reload(wait_until='networkidle');check(p.evaluate('App.snapshot.reportNotes.length')==1,'retry did not save');check(p.evaluate('App.snapshot.sessions.length')==0,'observation created measurement')
 test('disagreement-write-failure-retention-retry-and-isolation',failed_observation)
 def themes():
  visit('home');themes=p.evaluate('D.themes.map(t=>t.id)')
  for theme in themes:
   p.set_viewport_size({'width':320,'height':740})
   visit('share',theme);check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'share overflow '+theme);shot('theme-'+theme+'-share-320')
   visit('report',theme);p.fill('#report-note','要看情况。熟悉的讨论和陌生的场合不一样。'*60);check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'long report overflow '+theme);check(p.locator('#report-note').input_value().startswith('要看情况'),'long draft lost');p.locator('[data-action=save-report-note]').focus();p.keyboard.press('Enter');check(p.evaluate('App.snapshot.reportNotes.length')==1,'long save failed');p.reload(wait_until='networkidle');check(p.evaluate('App.snapshot.reportNotes.length')==1,'long save not persistent')
 test('12-themes-320px-long-observation-keyboard-persistence',themes)
 def contracts():
  p.set_viewport_size({'width':1440,'height':1000});p.goto(base+'/#node=records&view=contract',wait_until='networkidle');p.locator('#expand-tree').click();p.locator('[data-page=records]').click();p.locator('#tab-contract').click();p.wait_for_function("document.getElementById('dev-sections')?.textContent.includes('当前文案与本地行为补充')");p.fill('#dev-query','records::record-filter');check('当前文案与本地行为补充' in p.locator('#dev-sections').inner_text(),'new contract not searchable');shot('current-contract')
 test('current-contract-visible-and-searchable',contracts)
 b.close()
report={'results':results,'pageErrors':errors,'scope':'Chromium local prototype only. No real login, payment, AI, measurement, cloud or publication.'};(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));server.shutdown();sys.exit(int(bool(errors) or any(r['status']=='FAIL' for r in results)))
