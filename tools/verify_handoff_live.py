"""Read-only verification against the actual published root, using synthetic browser state."""
import concurrent.futures, hashlib, json, pathlib, time, urllib.request
from playwright.sync_api import sync_playwright

BASE = 'https://zhiyuxinxi.github.io/'
OUT = pathlib.Path('live-handoff-evidence')
OUT.mkdir(exist_ok=True)
report = {'url': BASE, 'sourceSHA': 'b8677fdec0bfd3481ab4ba86a4e2ae73909f0840', 'checks': [], 'pageErrors': [], 'assetHashes': {}}

def record(name, detail):
    report['checks'].append({'name': name, 'status': 'PASS', 'detail': detail})
    print('PASS', name, flush=True)

def fetch(path):
    with urllib.request.urlopen(BASE + path + '?handoff_verify=' + str(int(time.time())), timeout=30) as response:
        assert response.status == 200
        return response.read()

try:
    # This read-only job can start while the authorized release is still deploying.
    expected_script = pathlib.Path('site/workbench.js').read_bytes()
    for attempt in range(36):
        try:
            if fetch('workbench.js') == expected_script:
                break
        except Exception:
            pass
        print('Waiting for reviewed workbench deployment', attempt + 1, flush=True)
        time.sleep(10)
    else:
        raise AssertionError('Reviewed workbench did not reach the public root within six minutes')
    for name in ['index.html', 'workbench.js', 'workbench.css', 'workbench-data.js', 'development-review.js', 'prototype/ambient.js', 'handoff/development/manifest.json']:
        raw = fetch(name)
        expected = pathlib.Path('site', name).read_bytes()
        assert raw == expected, 'Root resource differs from reviewed source: ' + name
        report['assetHashes'][name] = hashlib.sha256(raw).hexdigest()
    record('public-root-versus-site-source-hashes', len(report['assetHashes']))
    manifest = json.loads(fetch('handoff/development/manifest.json'))
    def chunk(item):
        name, meta = item
        raw = fetch('handoff/development/' + name)
        assert len(raw) == meta['bytes'] and hashlib.sha256(raw).hexdigest() == meta['sha256'], name
        return name, json.loads(raw)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        chunks = dict(pool.map(chunk, manifest['files'].items()))
    index = chunks['index.json']
    pages = [chunks['pages/' + row['id'] + '.json'] for row in index['pages']]
    history = chunks['history-index.json']['records']
    assert len(pages) == 39 and sum(len(p['buttons']) for p in pages) == 299
    assert sum(r['kind'] == 'mobile' for r in history) == 119
    assert sum(r['actionCount'] for r in history if r['kind'] == 'mobile') == 551
    assert sum(r['kind'] == 'backend' for r in history) == 22
    assert sum(r['actionCount'] for r in history if r['kind'] == 'backend') == 66
    assert all(b['api']['currentNetworkRequest'] is False and b['api']['endpoint'] is None for p in pages for b in p['buttons'])
    record('public-chunk-integrity-and-counts', {'chunksIncludingManifest': len(chunks) + 1, 'counts': index['counts'], 'currentBusinessRequests': 0})
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, locale='zh-CN')
        page = context.new_page()
        page.on('pageerror', lambda error: report['pageErrors'].append(str(error)))
        catalog = json.loads(pathlib.Path('site/workbench-data.js').read_text().split('=', 1)[1].strip().rstrip(';'))['routes']
        for contract in pages:
            node = next(n['id'] for n in catalog if (n.get('route') or '').split('?')[0] == contract['route'])
            page.goto('about:blank')
            page.goto(BASE + '?verify=handoff#page=' + node + '&mode=contract')
            page.locator('#dev-query').wait_for()
            assert contract['route'] in page.locator('#panel-contract .dev-kicker').inner_text()
            assert str(len(contract['buttons'])) + ' 组按钮' in page.locator('#dev-result-count').inner_text()
            page.wait_for_function("document.querySelector('#runtime-status').textContent.includes('已连接')")
        record('all-39-live-contract-panels', 'Correct route and button-group count for every contract; hidden previews connected.')
        page.goto(BASE + '?verify=home#page=home&mode=contract')
        page.locator('#dev-query').wait_for()
        page.wait_for_function("document.querySelector('#runtime-status').textContent.includes('已连接')")
        page.screenshot(path=str(OUT / 'desktop-contract.png'))
        page.locator('#tab-preview').click()
        frame = page.frames[1]
        frame.wait_for_function('window.Ambient && innerWidth>0 && document.querySelector("#ambient-tide").height>=96')
        assert frame.evaluate('document.querySelector("#ambient-tide").getContext("2d").getImageData(0,0,1,1).data[3]') == 255
        frame.locator('[data-action=tab][data-route=explore]').click()
        page.wait_for_function("document.querySelector('[data-page=explore]').getAttribute('aria-selected')==='true'")
        page.locator('#tree-search').fill('订单')
        assert page.locator('[data-page=orders]').is_visible()
        page.locator('#clear-search').click()
        assert page.locator('#tree-search').input_value() == ''
        record('hidden-preview-recovery-and-original-navigation', 'Canvas rendered after showing; product explore navigation synced tree; tree search/clear retained.')
        page.locator('#tab-history').click()
        page.locator('#history-query').wait_for()
        assert '119 项职责 · 551 项关联动作' in page.locator('#history-count').inner_text()
        page.locator('#history-gap').check()
        assert '13 项职责' in page.locator('#history-count').inner_text()
        page.screenshot(path=str(OUT / 'desktop-history.png'))
        page.locator('#history-gap').uncheck()
        page.locator('#history-value').select_option('删除')
        assert '8 项职责' in page.locator('#history-count').inner_text()
        page.locator('#history-value').select_option('')
        page.locator('#history-status').select_option('真实遗漏')
        assert '15 项职责' in page.locator('#history-count').inner_text()
        page.locator('#history-status').select_option('')
        page.locator('#history-query').fill('home::version')
        assert '1 项职责' in page.locator('#history-count').inner_text()
        page.locator('[data-history-id] summary').first.click()
        page.wait_for_function("document.querySelector('[data-history-id]').dataset.loaded==='1'")
        assert '应用版本选择' in page.locator('#history-rows').inner_text()
        page.locator('[data-dev-node=single-factor]').click()
        page.locator('#dev-query').wait_for()
        assert 'single-factor' in page.locator('#panel-contract .dev-kicker').inner_text()
        page.locator('#tab-history').click()
        page.locator('#history-clear').click()
        page.locator('#history-kind').select_option('backend')
        assert '22 项职责 · 66 项关联动作' in page.locator('#history-count').inner_text()
        record('live-history-search-filters-destination', '119/551; 13 valuable gaps vs 15 current omissions; 8 deletion proposals; action-ID expansion; destination route; backend22/66.')
        page.goto(BASE + '?verify=assistant#page=assistant&mode=contract')
        page.locator('#dev-query').fill('currentNetworkRequest')
        text = page.locator('#dev-sections').inner_text()
        assert '当前真实网络请求' in text and '计划位置' in text and 'local' in text and 'cloud' in text
        record('local-versus-planned-cloud', 'Current local handlers/no real requests distinguished from planned cloud operations; no endpoint invented.')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto(BASE + '?verify=narrow#page=explore&mode=contract')
        page.locator('#dev-query').wait_for()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(OUT / 'narrow-contract.png'))
        page.locator('#mobile-nav').click()
        assert page.locator('#mobile-nav').get_attribute('aria-expanded') == 'true'
        page.keyboard.press('Escape')
        assert page.locator('#mobile-nav').get_attribute('aria-expanded') == 'false'
        record('narrow-live-layout-and-drawer', '390px document has no horizontal overflow; drawer opens and Escape closes it.')
        assert not report['pageErrors'], report['pageErrors']
        browser.close()
    report['status'] = 'PASS'
except Exception as error:
    report['status'] = 'FAIL'
    report['error'] = str(error)
    raise
finally:
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
