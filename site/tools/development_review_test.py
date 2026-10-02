"""Static data integrity and real-browser development documentation checks."""
import functools,hashlib,http.server,json,os,pathlib,threading,sys
from playwright.sync_api import sync_playwright
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'site').resolve();out=root/'qa/development-review';out.mkdir(parents=True,exist_ok=True)
data=root/'handoff/development';manifest=json.loads((data/'manifest.json').read_text());tests=[]
def passed(name,detail):tests.append({'name':name,'status':'PASS','detail':detail})
for name,meta in manifest['files'].items():
 b=(data/name).read_bytes();assert len(b)==meta['bytes'];assert hashlib.sha256(b).hexdigest()==meta['sha256']
index=json.loads((data/'index.json').read_text());hist=json.loads((data/'history-index.json').read_text())['records'];pages=[json.loads((data/'pages'/f'{r["id"]}.json').read_text()) for r in index['pages']]
assert len(pages)==39 and sum(len(p['buttons']) for p in pages)==299
assert len([r for r in hist if r['kind']=='mobile'])==119
assert sum(r['actionCount'] for r in hist if r['kind']=='mobile')==551
assert len([r for r in hist if r['kind']=='backend'])==22
assert sum(r['actionCount'] for r in hist if r['kind']=='backend')==66
assert sum(r['gap'] for r in hist)==13
for page in pages:
 entities={e['entityId'] for e in page['localData']}
 for button in page['buttons']:
  assert button['api']['currentNetworkRequest'] is False
  assert button['api']['endpoint'] is None
  assert set(button['localDataEntities'])<=entities
passed('audited-data-integrity',index['counts'])
# No unapproved private-source URLs, absolute local paths, or embedded source archives.
import re
for f in data.rglob('*.json'):
 text=f.read_text();assert '/workspace/' not in text and '/tmp/' not in text
 for url in re.findall(r'https?://[^"\s]+',text):assert url.startswith('https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/blob/')
assert not list(data.rglob('*.zip'))
passed('publication-boundary','Only public-safe audited chunks; source IDs and hashes retained.')
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1);errors=[];requests=[]
 def visit(url):
  page.goto('about:blank');page.goto(url)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 visit(origin);page.wait_for_function("document.querySelector('#runtime-status').textContent.includes('已连接')")
 assert not any('/development/' in u for u in requests)
 passed('lazy-initial-load','Product preview does not load development datasets.')
 page.locator('#tab-contract').click();page.locator('#dev-query').wait_for();assert page.locator('#dev-result-count').inner_text().find(str(len(pages[0]['buttons']))+' 组按钮')>=0
 page.screenshot(path=str(out/'desktop-development.png'))
 catalog=json.loads((root/'workbench-data.js').read_text().split('=',1)[1].strip().rstrip(';'))['routes']
 for p in pages:
  node=next(n['id'] for n in catalog if (n.get('route') or '').split('?')[0]==p['route'])
  visit(origin+'/#page='+node+'&mode=contract');page.locator('#dev-query').wait_for();assert p['route'] in page.locator('#panel-contract .dev-kicker').inner_text()
 passed('all-page-contracts','39 route-specific document panels load and show their correct route.')
 visit(origin+'/#page=personality-sandbox&mode=contract');page.locator('#dev-query').wait_for();page.locator('#dev-query').fill('滑杆');page.wait_for_timeout(100)
 page.locator('#dev-query').fill('impossible-no-result');assert '没有匹配项' in page.locator('#dev-sections').inner_text();page.locator('#dev-clear').click();assert page.locator('#dev-query').input_value()=='';assert page.locator('#dev-query').evaluate('(e)=>e===document.activeElement')
 # Composition must not redraw until committed.
 before=page.locator('#dev-result-count').inner_text();page.locator('#dev-query').dispatch_event('compositionstart');page.locator('#dev-query').fill('impossible-no-result');assert page.locator('#dev-result-count').inner_text()==before;page.locator('#dev-query').dispatch_event('compositionend');assert '没有匹配项' in page.locator('#dev-sections').inner_text();page.locator('#dev-clear').click()
 passed('page-search-and-ime','Filtering, no results, clear focus and composition boundaries verified.')
 page.locator('#tab-history').click();page.locator('#history-query').wait_for();assert '119 项职责 · 551 项关联动作' in page.locator('#history-count').inner_text()
 page.locator('#history-gap').check();assert '13 项职责' in page.locator('#history-count').inner_text();page.screenshot(path=str(out/'desktop-history-gaps.png'));page.locator('#history-gap').uncheck()
 page.locator('#history-value').select_option('删除');assert '8 项职责' in page.locator('#history-count').inner_text();page.locator('#history-value').select_option('');page.locator('#history-status').select_option('真实遗漏');assert '15 项职责' in page.locator('#history-count').inner_text();page.locator('#history-status').select_option('')
 page.locator('#history-query').fill('home::version');assert '1 项职责' in page.locator('#history-count').inner_text();page.locator('[data-history-id] summary').first.click();page.locator('[data-history-id] [data-retry]').count();page.wait_for_function("document.querySelector('[data-history-id]').dataset.loaded==='1'");assert '应用版本选择' in page.locator('#history-rows').inner_text();
 page.reload();page.locator('#history-query').wait_for();assert page.locator('#history-query').input_value()=='home::version'
 page.locator('#history-clear').click();page.locator('#history-next').click();assert '第 2 / 8 页' in page.locator('#history-position').inner_text();page.locator('#history-query').fill('xxxxxxxxxxxx');assert '没有匹配项' in page.locator('#history-rows').inner_text();page.locator('#history-clear').click();assert '第 1 / 8 页' in page.locator('#history-position').inner_text()
 page.locator('#history-kind').select_option('backend');assert '22 项职责 · 66 项关联动作' in page.locator('#history-count').inner_text();page.locator('[data-dev-node]').first.click();assert page.locator('#tab-contract').get_attribute('aria-selected')=='true'
 passed('history-search-filter-links','119/551 and22/66,15 omissions vs13 valuable gaps,8 deletion proposals, action-ID search, pagination reset, URL reload and backend links verified.')
 visit(origin+'/#page=home&mode=history&hq=home::version');page.locator('[data-dev-node="single-factor"]').click();page.locator('#dev-query').wait_for();assert 'single-factor' in page.locator('#panel-contract .dev-kicker').inner_text()
 page.locator('#dev-query').fill('currentHandler');assert page.locator('#dev-sections a').count()>0
 for link in page.locator('#dev-sections a').all():assert re.match(r'https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/blob/[a-f0-9]{40}/site/',link.get_attribute('href'))
 passed('destination-and-evidence-links','History destination opens matching contract; source links pinned to public repo commit.')
 page.set_viewport_size({'width':390,'height':844});visit(origin+'/#page=explore&mode=contract');page.locator('#dev-query').wait_for();page.screenshot(path=str(out/'narrow-development.png'));page.locator('#dev-query').fill('explore-search');page.screenshot(path=str(out/'narrow-input-contract.png'));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 page.locator('#tab-history').click();page.locator('#history-query').wait_for();page.screenshot(path=str(out/'narrow-history.png'));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 passed('narrow-document-panels','390px contract, input detail and history controls; no horizontal document overflow.')
 # Simulated static-resource failure and retry on a fresh context.
 ctx=browser.new_context();bad=ctx.new_page();bad.route('**/handoff/development/index.json',lambda r:r.abort());bad.goto(origin+'/#page=home&mode=contract');bad.locator('[data-retry]').wait_for();bad.unroute('**/handoff/development/index.json');bad.locator('[data-retry]').click();bad.locator('#dev-query').wait_for();ctx.close()
 passed('load-failure-retry','Resource error stays actionable; retry recovers without reloading the product.')
 assert not errors,errors
 browser.close()
server.shutdown();report={'status':'PASS','counts':index['counts'],'tests':tests,'pageErrors':errors,'sourceDataCommit':index['sourceCommit']};(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
