import sys
import os
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_settings_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1600, 'height': 950})
        
        index_url = f"file:///{os.path.abspath('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html').replace(os.sep, '/')}"
        page.goto(index_url)
        page.wait_for_timeout(800)

        # Open Settings
        page.evaluate("() => openToolWindow('settings')")
        page.wait_for_timeout(600)

        settings_win = page.locator("#win-settings")
        assert settings_win.is_visible(), "Settings window must be visible!"

        # Check Twitch Bot buttons inside sec-platforms
        twitch_subcard = page.locator("#win-settings #twitchBotBadge").locator("..")
        buttons = twitch_subcard.locator("button")
        b_count = buttons.count()
        print(f"Twitch bot buttons count: {b_count}")
        assert b_count >= 2, "Must have at least 2 bot action buttons"

        for i in range(b_count):
            btn = buttons.nth(i)
            box = btn.bounding_box()
            text = btn.inner_text().replace('\n', ' ')
            print(f"  - Button [{i}]: '{text}' -> height={box['height']}px, width={box['width']}px")
            # Must NOT wrap vertically into > 30px!
            assert box['height'] <= 28, f"Button '{text}' wrapped vertically (height is {box['height']}px)!"

        # Screenshot the Settings window
        settings_win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/settings_ui_polished_verified.png")
        print("✓ Captured screenshot of polished Settings window!")

        browser.close()
        print("Settings UI test passed 100%!")

if __name__ == '__main__':
    test_settings_ui()
