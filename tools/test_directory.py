"""Functional and visual checks for the static discount directory."""
import json, pathlib, subprocess, time
from playwright.sync_api import sync_playwright
out = pathlib.Path('site-checks'); out.mkdir(exist_ok=True)
server = subprocess.Popen(['python', '-m', 'http.server', '8765'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
report = {'checks': [], 'errors': []}
def ok(name):
    report['checks'].append(name); print('PASS:', name)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for width, height, name in [(1440, 1050, 'desktop'), (390, 844, 'mobile'), (320, 740, 'small'), (768, 1024, 'tablet')]:
            page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
            page.on('pageerror', lambda error: report['errors'].append(str(error)))
            page.goto('http://127.0.0.1:8765/', wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            assert page.locator('.offer').count() == 6
            page.locator('footer').scroll_into_view_if_needed(); page.wait_for_timeout(600)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow '+name
            assert page.locator('.logo-box img').evaluate_all('(imgs) => imgs.every(i => i.complete && i.naturalWidth > 0 && !i.hidden)'), 'Missing brand logo '+name
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(out / (name+'.png')), full_page=True)
            ok(name+' layout and logos')
            page.locator('[data-kind="student"]').click()
            assert page.locator('.offer').count() == 4
            page.locator('#search').fill('boots')
            assert page.locator('.offer').count() == 1
            page.locator('[data-save="boots"]').click()
            assert page.locator('#saved-count').inner_text() == '1'
            page.reload(wait_until='networkidle')
            page.locator('[data-kind="saved"]').click()
            assert page.locator('.offer').count() == 1
            assert 'Boots' in page.locator('.offer').inner_text()
            ok(name+' filters and persistent saved offers')
            page.locator('[data-offer="boots"]').click()
            assert page.locator('#offer-dialog').is_visible()
            assert 'Advantage Card' in page.locator('#dialog-content').inner_text()
            if name == 'mobile': page.screenshot(path=str(out/'mobile-details.png'))
            assert '#offer=boots' in page.url
            page.keyboard.press('Escape')
            assert not page.locator('#offer-dialog').is_visible()
            assert page.locator('[data-offer="boots"]').evaluate('(e) => e === document.activeElement')
            page.locator('[data-kind="card"]').click()
            assert page.locator('.offer').count() == 2
            page.locator('[data-offer="wokway"]').click()
            assert 'not yet active' in page.locator('#dialog-content').inner_text()
            assert page.locator('#dialog-content .steps').count() == 0
            page.keyboard.press('Escape')
            ok(name+' modal keyboard access and pending-offer safeguards')
            page.locator('[data-help]').first.click()
            assert page.locator('#help-dialog').is_visible()
            page.keyboard.press('Escape')
            page.goto('http://127.0.0.1:8765/#offer=specsavers', wait_until='networkidle')
            assert page.locator('#offer-dialog').is_visible()
            assert '£70' in page.locator('#dialog-content').inner_text()
            links = page.locator('#dialog-content a').evaluate_all('(a) => a.map(x=>x.href)')
            assert any('google.com/maps/dir/?api=1&destination=' in link for link in links)
            ok(name+' deep links, help and map links')
            page.close()
        assert not report['errors'], report['errors']
        browser.close()
    report['passed'] = True
finally:
    server.terminate()
    (out/'report.json').write_text(json.dumps(report, indent=2))
