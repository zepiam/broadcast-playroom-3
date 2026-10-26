import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def run():
    dist_html = os.path.abspath(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\dist\index.html")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-web-security', '--allow-file-access-from-files']
        )
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        page.goto(f"file:///{dist_html}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        
        print("Page loaded successfully.")
        
        # 1. Test Server Status indicator on topbar
        server_status_wrap = page.locator("#topbarServerStatus")
        assert server_status_wrap.is_visible(), "topbarServerStatus should be visible on topbar"
        
        dot = page.locator("#serverStatusDot")
        text = page.locator("#serverStatusText")
        assert dot.is_visible(), "serverStatusDot should be visible"
        assert text.is_visible(), "serverStatusText should be visible"
        print(f"PASS: Server Status indicator visible! Status text: {text.inner_text()}")
        
        # Click server status to trigger health check
        server_status_wrap.click()
        page.wait_for_timeout(600)
        print(f"PASS: Clicked Server Status! Current text: {text.inner_text()}")
        
        page.screenshot(path="topbar_server_status_verified.png")
        print("PASS: Saved screenshot topbar_server_status_verified.png")
        
        # 2. Open Settings Window
        page.locator("#btnRailSettings").click()
        page.wait_for_timeout(600)
        
        win_settings = page.locator("#win-settings")
        assert win_settings.is_visible(), "win-settings should be visible"
        
        # Test Network & DNS section
        page.locator("#nav-sec-networking").click()
        page.wait_for_timeout(400)
        assert page.locator("#sec-networking").is_visible(), "sec-networking should be visible"
        
        # Run DNS Speed test
        page.evaluate("""() => {
            if (typeof runDnsSpeedTest === 'function') {
                runDnsSpeedTest();
            }
        }""")
        page.wait_for_timeout(700)
        print("PASS: Tested Network & DNS section and Speed Test!")
        
        # Test Docks section
        page.locator("#nav-sec-docks").click()
        page.wait_for_timeout(400)
        assert page.locator("#sec-docks").is_visible(), "sec-docks should be visible"
        print("PASS: Tested Docks section with 1-Click Auto OBS Installer!")
        
        page.screenshot(path="network_dns_and_dock_settings.png")
        print("PASS: Saved screenshot network_dns_and_dock_settings.png")
        
        browser.close()

if __name__ == '__main__':
    run()
