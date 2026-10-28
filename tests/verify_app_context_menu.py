import os, sys, tempfile, threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright

os.environ['BP3_EDITION'] = 'lite'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.dont_write_bytecode = True
import launch_dev

with tempfile.TemporaryDirectory() as tmp:
    launch_dev.LAYOUT_FILE = str(Path(tmp) / 'layout.json')
    server = ThreadingHTTPServer(('127.0.0.1', 0), launch_dev.QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
            check = "el => !el.dispatchEvent(new MouseEvent('contextmenu', {bubbles:true,cancelable:true,button:2}))"
            assert page.locator('body').evaluate(check)
            page.locator('#topbar-item-overlay').click(button='right')
            assert page.locator('#topbarContextMenu').is_visible()
            page.mouse.click(10, 200)
            for key in ('game-overlay', 'overlay-plus'):
                item = page.locator('#topbar-item-' + key)
                item.click(button='right')
                page.locator('#topbarContextMenu button.danger').click()
                assert not item.is_visible()
            page.locator('#topbarSortable').click(button='right', position={'x': 4, 'y': 16})
            page.locator('#topbarContextMenu button').filter(has_text='Game Overlay').click()
            assert page.locator('#topbar-item-game-overlay').is_visible()
            page.locator('#topbarSortable').click(button='right', position={'x': 4, 'y': 16})
            page.locator('#topbarContextMenu button').filter(has_text='Overlay+').click()
            assert page.locator('#topbar-item-overlay-plus').is_visible()
            for key in ('translate', 'overlay', 'game-overlay', 'overlay-plus'):
                page.evaluate('(key) => hideTopbarButton(key)', key)
            page.locator('#topbarSortable').click(button='right', position={'x': 4, 'y': 16})
            assert page.locator('#topbarContextMenu button').count() == 4
            page.locator('#topbarContextMenu button').filter(has_text='Game Overlay').click()
            assert page.locator('#topbar-item-game-overlay').is_visible()
            with context.expect_page() as pending:
                page.locator('#btnRailSettings').click()
            popup = pending.value
            popup.wait_for_load_state()
            popup.locator('#win-settings').wait_for(state='visible')
            assert popup.locator('body').evaluate(check)
            assert popup.locator('input').first.evaluate(check)
            with context.expect_page() as pending:
                page.evaluate("openToolWindow('composer')")
            composer = pending.value
            composer.wait_for_load_state()
            composer.locator('#win-composer').wait_for(state='visible')
            assert composer.locator('body').evaluate(check)
            browser.close()
            print('PASS: browser menu suppressed; topbar buttons can be hidden and restored, including when all are hidden')
    finally:
        server.shutdown()
        server.server_close()
