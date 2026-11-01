import os
import sys
import time
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

class TestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "src"), **kwargs)

    def do_POST(self):
        if self.path == '/api/platform/settings':
            size = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(size)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": true}')
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/platform/settings':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"hidden_platforms": []}')
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass

def run():
    server = HTTPServer(('127.0.0.1', 2399), TestHandler)
    st = threading.Thread(target=server.serve_forever, daemon=True)
    st.start()
    print("Test server running on port 2399")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Test 1: Popout window standalone styling
        print("\n--- Test 1: Popout Window Header Redundant Buttons ---")
        popout_page = context.new_page()
        popout_page.on('pageerror', lambda err: print('POPOUT PAGEERROR:', err))
        popout_page.goto("http://127.0.0.1:2399/index.html?popout=settings")
        popout_page.wait_for_load_state("domcontentloaded")
        popout_page.wait_for_function("typeof window.togglePlatformVisibility === 'function'")
        
        # Check computed style of floating-actions-right in popout
        actions_display = popout_page.evaluate("""() => {
            const el = document.querySelector('#win-settings .floating-actions-right');
            return el ? window.getComputedStyle(el).display : 'none';
        }""")
        print(f"Popout #win-settings .floating-actions-right computed display: {actions_display}")
        assert actions_display == 'none', f"Expected 'none', got '{actions_display}'"
        print("PASS: Popout window floating-actions-right is completely hidden!")

        # Test 2: Main window & Popout window sync for platform hiding
        print("\n--- Test 2: Platform Hiding Across Windows ---")
        main_page = context.new_page()
        main_page.goto("http://127.0.0.1:2399/index.html")
        main_page.on('pageerror', lambda err: print('MAIN PAGEERROR:', err))
        main_page.wait_for_selector("#card-twitch")
        main_page.wait_for_function("typeof window.applyPlatformHiddenState === 'function'")

        # Initial state: card-twitch should be visible
        initial_twitch_display = main_page.evaluate("""() => {
            const card = document.getElementById('card-twitch');
            return window.getComputedStyle(card).display;
        }""")
        print(f"Main window #card-twitch initial display: {initial_twitch_display}")
        assert initial_twitch_display != 'none', "Initial Twitch card should be visible"

        # Now in the popout_page (Settings): hide Twitch using togglePlatformVisibility('twitch')
        print("Hiding Twitch in Settings window...")
        popout_page.evaluate("togglePlatformVisibility('twitch', false)")

        # Wait for sync to propagate to main_page
        time.sleep(0.6)

        # Check in main_page: card-twitch should now be hidden!
        hidden_twitch_display = main_page.evaluate("""() => {
            const card = document.getElementById('card-twitch');
            return window.getComputedStyle(card).display;
        }""")
        print(f"Main window #card-twitch display after hiding in Settings: {hidden_twitch_display}")
        assert hidden_twitch_display == 'none', f"Expected 'none', got '{hidden_twitch_display}'"
        print("PASS: Main window #card-twitch successfully hidden after toggling in Settings window!")

        # Now in popout_page: unhide Twitch
        print("Unhiding Twitch in Settings window...")
        popout_page.evaluate("togglePlatformVisibility('twitch', true)")
        time.sleep(0.6)

        unhidden_twitch_display = main_page.evaluate("""() => {
            const card = document.getElementById('card-twitch');
            return window.getComputedStyle(card).display;
        }""")
        print(f"Main window #card-twitch display after unhiding in Settings: {unhidden_twitch_display}")
        assert unhidden_twitch_display != 'none', f"Expected visible display, got '{unhidden_twitch_display}'"
        print("PASS: Main window #card-twitch successfully reappeared after unhiding in Settings window!")

        # Take screenshot of popout window for verification artifact
        screenshot_path = ROOT / "tests" / "popout_clean_header.png"
        popout_page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()
    
    server.shutdown()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run()
