"""Check that each trial can serve and apply its own packaged stylesheets."""
import functools, threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

with sync_playwright() as p:
    browser = p.chromium.launch()
    for edition, name in [('lite', 'BroadcastPlayroom3-Lite'), ('full', 'BroadcastPlayroom3-Full')]:
        directory = root / 'build_trials' / edition / name / '_internal' / 'dist'
        server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(directory)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            page = browser.new_page()
            page.route('https://fonts.googleapis.com/**', lambda route: route.abort())
            failed = []
            page.on('response', lambda response: failed.append(response.url) if '/assets/' in response.url and response.status >= 400 else None)
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='domcontentloaded')
            styles = page.locator('link[rel="stylesheet"][href^="./assets/"]')
            assert styles.count() >= 2
            for n in range(styles.count()):
                assert styles.nth(n).evaluate('el => !!el.sheet'), f'{edition}: missing stylesheet'
            assert page.locator('.topbar').evaluate("el => getComputedStyle(el).display") == 'flex'
            assert page.locator('.topbar').evaluate("el => getComputedStyle(el).backgroundColor") != 'rgba(0, 0, 0, 0)'
            assert not failed, f'{edition}: missing assets {failed}'
            page.close()
            print(f'{edition}: packaged stylesheets load and topbar is styled: PASS')
        finally:
            server.shutdown(); server.server_close()
    browser.close()
