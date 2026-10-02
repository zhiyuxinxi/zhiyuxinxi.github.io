"""Public-data integrity and focused read-only architecture reader checks."""
import functools, hashlib, http.server, json, os, pathlib, re, sys, threading
from playwright.sync_api import sync_playwright

root = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'site').resolve()
data = root/'handoff/backend-logic'
out = root/'qa/backend-logic'
out.mkdir(parents=True,exist_ok=True)
results=[]; errors=[]
def passed(name,detail):
    results.append({'name':name,'status':'PASS','detail':detail});print('PASS',name,flush=True)

manifest=json.loads((data/'manifest.json').read_text())
for name in manifest['publishedFiles']:
    raw=(data/name).read_bytes(); expected=manifest['sourceFiles'][name]
    assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256']
local=json.loads((data/'architecture-plan.json').read_text());cloud=json.loads((data/'cloud-boundaries.json').read_text())
counts={k:len(local[k]) for k in ['entities','operations','flows','acceptance','pageCoverage']}
assert counts=={'entities':17,'operations':11,'flows':8,'acceptance':18,'pageCoverage':29}
classified=[x for v in cloud.values() if isinstance(v,list) for x in v if isinstance(x,dict) and 'classification' in x]
assert len(classified)==121
assert [len(cloud[k]) for k in ['dataClasses','conditionalFlows','errorMatrix','acceptance','historyRepairs']]==[11,7,20,28,13]
catalog=json.loads((root/'workbench-data.js').read_text().split('=',1)[1].strip().rstrip(';'))['routes']
pageids={r['id'] for r in catalog}|{r['route'].split('?')[0] for r in catalog if r.get('route')}
def walk(value,legend):
    if isinstance(value,list):
        for x in value:walk(x,legend)
    elif isinstance(value,dict):
        if 'id' in value and ('status' in value or 'classification' in value):assert (value.get('classification') or value.get('status')) in legend
        for key,v in value.items():
            if key in ['pages','pageIds']:assert set(v)<=pageids,(key,v)
            if key=='pageId':assert v in pageids,v
            if key=='requirementIds':assert all(re.fullmatch(r'ZY-[A-Z]+-\d{3}',x) for x in v)
            if key in ['decisionIds','decisionRefs','existingDecisionIds']:assert all(x=='PAGE-ARCH-CANDIDATE' or re.fullmatch(r'D-(0[1-9]|1\d|2[0-2])',x) for x in v),v
            walk(v,legend)
walk(local,local['meta']['statusLegend']);walk(cloud,cloud['classificationLegend'])
for entry in local['acceptance']+cloud['acceptance']:assert entry['execution'].startswith('待执行')
for path in data.glob('*.json'):
    text=path.read_text();assert not any(token in text for token in ['/workspace/','/tmp/','sediment://','file://'])
    for url in re.findall(r'https?://[^"\s]+',text):assert re.match(r'https://(developer.android.com|www.rfc-editor.org|pages.nist.gov|cheatsheetseries.owasp.org)/',url),url
passed('data-integrity-and-boundaries',{'local':counts,'cloudItems':len(classified),'pages':'All referenced page IDs exist in current workbench','requirements':'ID format verified; full161 requirement membership follows supplied cross-reviewed source validation, not a new full-matrix audit.','acceptance':'46 planned acceptance items remain unexecuted business criteria.'})

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
try:
    with sync_playwright() as pw:
        launch={'args':['--no-sandbox']}
        if os.environ.get('CHROMIUM_PATH'):launch['executable_path']=os.environ['CHROMIUM_PATH']
        browser=pw.chromium.launch(**launch);ctx=browser.new_context(viewport={'width':1440,'height':1000},locale='zh-CN');p=ctx.new_page();requests=[]
        p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url))
        p.goto(base);p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('已连接')")
        assert not any('/backend-logic/' in u for u in requests)
        p.locator('#tab-logic').click();p.locator('#logic-query').wait_for()
        assert '仅方案' in p.locator('#panel-logic').inner_text()
        p.screenshot(path=str(out/'desktop-local.png'))
        p.locator('#logic-section').select_option('entities');assert p.locator('.logic-item').count()==17
        p.locator('.logic-item summary').first.click();assert p.locator('.logic-item').first.get_attribute('open') is not None
        p.locator('#logic-section').select_option('flows');assert p.locator('.logic-item').count()==8
        p.locator('#logic-query').fill('空');assert p.locator('#logic-section').input_value()=='all'
        p.locator('#logic-query').fill('zz-no-result');assert '没有匹配条目' in p.locator('#logic-rows').inner_text()
        p.locator('#logic-clear').click();assert p.locator('#logic-query').evaluate('e=>e===document.activeElement')
        before=p.locator('#logic-count').inner_text();p.locator('#logic-query').dispatch_event('compositionstart');p.locator('#logic-query').fill('zz-no-result');assert p.locator('#logic-count').inner_text()==before
        p.locator('#logic-query').dispatch_event('compositionend');assert '没有匹配条目' in p.locator('#logic-rows').inner_text();p.locator('#logic-clear').click()
        p.locator('#logic-status').select_option('待决定');assert all('待决定' in e.inner_text() for e in p.locator('.logic-item summary').all())
        p.reload();p.locator('#logic-query').wait_for();assert p.locator('#logic-status').input_value()=='待决定'
        p.locator('#logic-status').select_option('');assert p.locator('.logic-item').count()==20;p.locator('#logic-more').click();assert p.locator('.logic-item').count()==40
        passed('local-directory-search-status-and-ime','17 entities, 8 flows, source status labels, bounded list, no-results, clear focus, IME and URL reload verified.')
        p.locator('[data-logic-doc=cloud]').click();p.locator('#logic-section').wait_for();p.locator('#logic-section').select_option('conditionalFlows');assert p.locator('.logic-item').count()==7
        p.locator('.logic-item summary').first.click();assert '条件待确认' in p.locator('.logic-item').first.inner_text()
        p.locator('.logic-item summary').first.evaluate("e=>e.scrollIntoView({block:'start'})");p.screenshot(path=str(out/'desktop-cloud-flow.png'))
        p.locator('[data-logic-page=content]').first.click();p.locator('#dev-query').wait_for();assert 'content' in p.locator('#panel-contract .dev-kicker').inner_text()
        p.locator('#tab-logic').click();p.locator('#logic-query').wait_for();p.locator('#logic-section').select_option('officialSources');p.locator('.logic-item summary').first.click()
        links=p.locator('#logic-rows a').all();assert len(links)==7;assert all(a.get_attribute('rel')=='noopener' and a.get_attribute('href').startswith('https://') for a in links)
        p.locator('#logic-return').click();p.locator('#dev-query').wait_for()
        passed('cloud-flow-page-links-and-official-sources','7 conditional flows; related page opens its development contract; 7 official links keep exact source URLs; return preserves current page.')
        for width in [1440,390]:
            p.set_viewport_size({'width':width,'height':1000 if width==1440 else 844})
            p.goto('about:blank');p.goto(base+'/#page=home&mode=logic&logicDoc=cloud&logicSection=dataClasses');p.locator('#logic-query').wait_for()
            p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('已连接')")
            assert p.locator('.logic-item').count()==11
            p.locator('.logic-item summary').first.click()
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            p.screenshot(path=str(out/f'logic-{width}.png'))
            p.locator('.logic-item[open] dt').filter(has_text='最小按次外发').first.evaluate("e=>e.scrollIntoView({block:'start'})")
            p.screenshot(path=str(out/f'boundary-detail-{width}.png'))
            p.locator('#tab-preview').click();p.wait_for_function("document.querySelector('#product-frame').getBoundingClientRect().width>200")
            frame=p.frames[1];frame.wait_for_function('window.Ambient&&innerWidth>0');assert frame.evaluate('document.querySelector("#ambient-tide").getContext("2d").getImageData(0,0,1,1).data[3]')==255
        passed('direct-mode-and-responsive-return','1440px and390px real screenshots; no horizontal overflow; direct logic entry returns to nonzero, rendered preview.')
        badctx=browser.new_context();bad=badctx.new_page();bad.route('**/handoff/backend-logic/architecture-plan.json',lambda r:r.abort());bad.goto(base+'/#mode=logic');bad.locator('#logic-retry').wait_for();bad.unroute('**/handoff/backend-logic/architecture-plan.json');bad.locator('#logic-retry').click();bad.locator('#logic-query').wait_for();badctx.close()
        assert all(u.startswith(base+'/') for u in requests)
        assert not errors,errors
        passed('failure-retry-and-static-only-requests','Load error recovers via retry; observed requests stay on same static origin; no business SDK or upload.')
        browser.close()
finally:
    server.shutdown();(out/'report.json').write_text(json.dumps({'sourceCommit':manifest['sourceCommit'],'tests':results,'pageErrors':errors,'scope':'Read-only document UI and source integrity; no business acceptance executed.'},ensure_ascii=False,indent=2)+'\n')
