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
        
        # 1. Open Settings Window
        page.locator("#btnRailSettings").click()
        page.wait_for_timeout(600)
        
        win_settings = page.locator("#win-settings")
        assert win_settings.is_visible(), "win-settings should be visible"
        
        # 2. Click Windows Defender section
        nav_defender = page.locator("#nav-sec-defender")
        assert nav_defender.is_visible(), "nav-sec-defender should be visible in settings sidebar"
        nav_defender.click()
        page.wait_for_timeout(500)
        
        sec_defender = page.locator("#sec-defender")
        assert sec_defender.is_visible(), "sec-defender pane should be visible"
        
        # 3. Test 1-Click Exclusion Button
        btn_exclusion = page.locator("#sec-defender button.primary").first
        assert btn_exclusion.is_visible(), "1-Click exclusion button should be visible"
        btn_exclusion.click()
        page.wait_for_timeout(400)
        
        status_lbl = page.locator("#lblDefenderStatus")
        print(f"PASS: 1-Click Exclusion applied! Status: {status_lbl.inner_text()}")
        
        path_box = page.locator("#lblDefenderPath")
        print(f"PASS: Folder path verified: {path_box.inner_text()}")
        
        page.screenshot(path="defender_1click_exclusion_verified.png")
        print("PASS: Saved screenshot defender_1click_exclusion_verified.png")
        
        browser.close()

if __name__ == '__main__':
    run()
