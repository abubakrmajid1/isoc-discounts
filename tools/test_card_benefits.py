"""Regression checks for the card-first discount directory."""
from pathlib import Path
from functools import partial
import http.server
import threading
import json
from playwright.sync_api import sync_playwright, expect

root = Path.cwd()
out = root / 'card-benefits-checks'
out.mkdir(exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(root)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/index.html'
expected = {'wokway': '15%', 'aces': '15%', 'cha-cha': '10%', 'dfc': '20%', 'hello-asia': '15%', 'velvet-green': '25%', 'jerk-hut': '7%', 'foundry': '20%', 'zazah': '10%'}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.route('https://fonts.googleapis.com/**', lambda route: route.abort())
        page.route('https://fonts.gstatic.com/**', lambda route: route.abort())
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto(base, wait_until='networkidle')
        expect(page.locator('.offer')).to_have_count(9)
        expect(page.locator('[data-kind=card]')).to_have_attribute('aria-pressed', 'true')
        assert page.locator('[data-kind=all]').count() == 0
        assert page.locator('.pending').count() == 0
        assert set(page.locator('.offer').evaluate_all('(els)=>els.map(e=>e.id.replace("place-",""))')) == set(expected)
        for key, rate in expected.items():
            assert rate in page.locator(f'#place-{key} .offer-amount').inner_text()
        assert 'One drink + a food item, or a meal deal.' in page.locator('#place-cha-cha').inner_text()
        page.evaluate('document.querySelectorAll("img").forEach(i=>i.loading="eager")')
        page.evaluate('Promise.all([...document.images].map(i=>i.decode().catch(()=>null)))')
        broken = page.locator('.logo-box img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)')
        assert not broken, broken
        assert page.locator('.offer .logo-box img').count() == 7
        assert page.locator('#place-jerk-hut .logo-fallback').is_visible()
        assert page.locator('#place-foundry .logo-fallback').is_visible()
        for width in [320, 360, 390, 430, 768, 1440]:
            page.set_viewport_size({'width': width, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'Overflow at {width}'
            page.screenshot(path=str(out / f'{width}.png'), full_page=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        page.locator('[data-code=dfc]').click()
        assert page.evaluate('navigator.clipboard.readText()') == 'ISOC123'
        page.locator('[data-code=jerk-hut]').click()
        assert page.evaluate('navigator.clipboard.readText()') == 'SWANSEAISOC'
        page.locator('#search').fill('DFC')
        expect(page.locator('.offer')).to_have_count(1)
        assert 'over £25' in page.locator('.offer').inner_text()
        page.locator('[data-offer=dfc]').click()
        expect(page.locator('#offer-dialog')).to_be_visible()
        assert page.locator('#offer-dialog a', has_text='Order online').get_attribute('href') == 'https://www.dfcswansea.com/menu'
        page.screenshot(path=str(out / 'dfc-mobile.png'), full_page=True)
        page.keyboard.press('Escape')
        page.locator('#search').fill('')
        page.locator('[data-kind=student]').click()
        expect(page.locator('.offer')).to_have_count(4)
        page.locator('[data-kind=card]').click()
        expect(page.locator('.offer')).to_have_count(9)
        page.locator('#category').select_option('Food & drink')
        expect(page.locator('.offer')).to_have_count(7)
        page.locator('[data-kind=student]').click()
        expect(page.locator('.offer')).to_have_count(4)
        page.locator('[data-kind=card]').click()
        page.locator('#place-wokway [data-save]').click()
        page.locator('[data-kind=saved]').click()
        expect(page.locator('.offer')).to_have_count(1)
        page.reload(wait_until='networkidle')
        expect(page.locator('.offer')).to_have_count(9)
        expect(page.locator('#place-wokway [data-save]')).to_have_attribute('aria-pressed', 'true')
        for key in expected:
            page.locator(f'[data-offer="{key}"]').click()
            assert 'Show your ISOC discount card' in page.locator('.steps').inner_text()
            page.keyboard.press('Escape')
        page.goto(base + '#offer=dfc', wait_until='networkidle')
        expect(page.locator('#offer-dialog')).to_be_visible()
        assert 'DFC Swansea' in page.locator('#dialog-title').inner_text()
        assert not errors, errors
        result = {'passed': True, 'cardOffers': 9, 'otherStudentOffers': 4, 'loadedPartnerLogos': 7, 'textFallbacks': ['Jerk Hut', 'Foundry'], 'viewports': [320, 360, 390, 430, 768, 1440], 'checks': ['default card view', 'exact benefit rates', 'Cha Cha restriction', 'card instructions', 'no horizontal overflow', 'seven logo loads', 'copy both codes', 'DFC minimum spend', 'DFC order URL', 'student tab', 'category switching', 'search', 'persistent saved items', 'nine dialogs', 'Escape close', 'deep link'], 'javascriptErrors': errors}
        (out / 'results.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        browser.close()
finally:
    server.shutdown()
