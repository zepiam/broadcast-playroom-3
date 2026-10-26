import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file:///E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html')
    page.wait_for_timeout(500)
    print("chatList HTML:\n", page.locator("#chatList").inner_html()[:400])
    browser.close()
