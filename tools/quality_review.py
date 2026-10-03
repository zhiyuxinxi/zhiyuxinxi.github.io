"""Design candidate evidence on native Chromium. Synthetic local fixtures only.

Usage: CHROMIUM_PATH=/usr/bin/chromium python tools/quality_review.py <site> <output>
Captures each original theme in key states, plus narrow, focus and fit evidence.
This is a layout/interaction check, not an aesthetic score or accessibility certification.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json, os, sys
from playwright.sync_api import sync_playwright

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
NARROW_ONLY = '--narrow-only' in sys.argv[3:]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}'
results, errors = [], []

def check(ok, message):
    if not ok:
        raise AssertionError(message)

def shot(page, name):
    page.mouse.move(0, 0)
    page.screenshot(path=str(OUT / (name + '.png')))

def visit(page, route, theme='sunrise', scenario='default'):
    page.goto(f'{BASE}/prototype/index.html?reset=1&theme={theme}&scenario={scenario}#{route}')
    page.wait_for_function('window.App && window.Ambient')
    page.wait_for_timeout(220)
    page.evaluate('Ambient.sample(8)')

with sync_playwright() as w:
    launch = {'headless': True, 'args': ['--no-sandbox']}
    if os.environ.get('CHROMIUM_PATH'):
        launch['executable_path'] = os.environ['CHROMIUM_PATH']
    browser = w.chromium.launch(**launch)
    themes = json.loads((ROOT / 'handoff/themes-v4.json').read_text())
    original = [] if NARROW_ONLY else [t['id'] for t in themes if t['group'] == '原始主题']
    for theme in original:
        ctx = browser.new_context(viewport={'width': 390, 'height': 844}, locale='zh-CN')
        p = ctx.new_page()
        p.on('pageerror', lambda e: errors.append(str(e)))
        for route, scenario in [('home', 'default'), ('topic?id=work-choice', 'default'),
                                ('question?id=session-demo-seed', 'question'),
                                ('report?id=report-sample-01', 'default'),
                                ('assistant', 'default'), ('me', 'default')]:
            name = theme + '-' + route.split('?')[0]
            try:
                visit(p, route, theme, scenario)
                check(p.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow')
                check(p.locator('.brandline,.wordmark,.prototype-label').count() == 0, 'Brand toolbar returned')
                shot(p, name)
                if route.startswith('report'):
                    p.locator('#report-personal').scroll_into_view_if_needed()
                    p.wait_for_function('document.querySelector(".report-chapters [aria-current=location]").dataset.id==="report-personal"')
                    shot(p, name + '-observation')
                if route == 'assistant':
                    p.locator('.composer textarea').fill('合成测试：' + '想把具体情况写下来，慢慢理清。' * 35)
                    p.locator('.source-btn').click()
                    p.wait_for_selector('[role=dialog]')
                    p.evaluate('Promise.all(document.querySelector(".overlay").getAnimations({subtree:true}).map(a=>a.finished))')
                    shot(p, theme + '-modal')
                    p.keyboard.press('Escape')
                    check(p.locator('.source-btn').evaluate('e=>e===document.activeElement'), 'Modal focus not restored')
                    check(p.locator('.composer textarea').input_value().startswith('合成测试：'), 'Long draft lost')
                if route.startswith('question'):
                    check(p.evaluate('Ambient.isPaused()'), 'Assessment not quiet')
                    p.locator('[data-action=answer]').first.focus()
                    p.keyboard.press('ArrowDown')
                    shot(p, theme + '-question-selected')
                results.append({'state': name, 'status': 'PASS'})
            except Exception as e:
                results.append({'state': name, 'status': 'FAIL', 'error': str(e)})
        ctx.close()

    for theme in ['sunrise', 'nebula', 'amber']:
        ctx = browser.new_context(viewport={'width': 320, 'height': 844}, locale='zh-CN', reduced_motion='reduce')
        p = ctx.new_page()
        p.on('pageerror', lambda e: errors.append(str(e)))
        for route in ['home', 'explore', 'assistant', 'me', 'appearance']:
            name = 'narrow-reduced-' + theme + '-' + route
            try:
                visit(p, route, theme)
                check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Narrow overflow')
                check(p.evaluate('Ambient.isPaused()'), 'Reduced motion not static')
                if route == 'explore':
                    check(p.locator('.v3-categories button').evaluate_all('es=>new Set(es.map(e=>e.getBoundingClientRect().top)).size') == 1, 'Narrow categories strand one item')
                    check(p.locator('.v3-title>.textbtn').bounding_box()['height'] <= 48, 'Favorite action wraps vertically')
                shot(p, name)
                results.append({'state': name, 'status': 'PASS'})
            except Exception as e:
                results.append({'state': name, 'status': 'FAIL', 'error': str(e)})
        ctx.close()

    # Document tabs must restore the same iframe, and fit both the page and caption.
    ctx = browser.new_context(viewport={'width': 1440, 'height': 1000}, locale='zh-CN')
    p = ctx.new_page()
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.goto(BASE)
    p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')")
    for width, height in ([] if NARROW_ONLY else [(1440, 1000), (1188, 761), (768, 1024), (390, 844)]):
        name = 'workbench-' + str(width)
        try:
            p.set_viewport_size({'width': width, 'height': height})
            p.wait_for_timeout(250)
            p.get_by_role('tab', name='实际页面', exact=True).click()
            p.wait_for_timeout(250)
            check(p.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'Workbench overflow')
            if width > 900:
                check(p.locator('.stage-note').evaluate('e=>e.getBoundingClientRect().bottom<=document.querySelector(".main-foot").getBoundingClientRect().top'), 'Preview caption clipped')
            shot(p, name)
            frame = p.frames[1]
            frame.evaluate('window.qualityReviewIdentity = document.getElementById("ambient-tide")')
            for label in ['逐页开发说明', '历史对账', '底层逻辑方案']:
                p.get_by_role('tab', name=label, exact=True).click()
                p.wait_for_timeout(250)
                check(p.locator('.preview-tools').is_hidden(), 'Irrelevant preview tools remain')
                shot(p, name + '-' + {'逐页开发说明': 'contract', '历史对账': 'history', '底层逻辑方案': 'logic'}[label])
            p.get_by_role('tab', name='实际页面', exact=True).click()
            p.wait_for_timeout(200)
            check(frame.evaluate('qualityReviewIdentity===document.getElementById("ambient-tide")'), 'Returning from docs recreated canvas')
            check(p.locator('.preview-tools').is_visible(), 'Preview tools did not return')
            results.append({'state': name, 'status': 'PASS'})
        except Exception as e:
            results.append({'state': name, 'status': 'FAIL', 'error': str(e)})
    ctx.close()
    browser.close()

server.shutdown()
report = {'results': results, 'pageErrors': errors, 'scope': '3 themes x 5 narrow reduced-motion pages.' if NARROW_ONLY else '8 original themes x 6 key pages plus selected answer, scrolled report, long draft and source modal; 3 themes x 5 narrow reduced-motion pages; 4 workbench sizes and document return. Real business services and device keyboards not exercised.'}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({'passed': sum(r['status']=='PASS' for r in results), 'failures': [r for r in results if r['status']=='FAIL'], 'pageErrors': errors}, ensure_ascii=False))
sys.exit(1 if errors or any(r['status']=='FAIL' for r in results) else 0)
