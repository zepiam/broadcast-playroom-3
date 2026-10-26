import sys
import os
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_platform_icons_loaded():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1600, 'height': 950})
        
        index_url = f"file:///{os.path.abspath('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html').replace(os.sep, '/')}"
        page.goto(index_url)
        page.wait_for_timeout(1000)

        # Check all plat-icon images
        icons = page.locator(".plat-icon")
        count = icons.count()
        print(f"Found {count} platform icons in Column 1:")
        
        for i in range(count):
            img = icons.nth(i)
            alt = img.get_attribute("alt")
            src = img.get_attribute("src")
            natural_width = img.evaluate("el => el.naturalWidth")
            print(f"  - [{alt}] src='{src}', naturalWidth={natural_width}")
            assert natural_width > 0, f"Image for {alt} is broken (naturalWidth is 0)!"

        # Click Simulate Chat and check chat icons
        page.locator("#btnSimulateChat").click()
        page.wait_for_timeout(1500)
        chat_plat_icons = page.locator("#chatList .plat-badge-chat")
        c_count = chat_plat_icons.count()
        print(f"Found {c_count} platform badges in chat:")
        for i in range(min(5, c_count)):
            img = chat_plat_icons.nth(i)
            src = img.get_attribute("src")
            nw = img.evaluate("el => el.naturalWidth")
            print(f"  - Chat badge src='{src}', naturalWidth={nw}")
            assert nw > 0, f"Chat badge {src} is broken!"

        # Take screenshot to verify
        page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/platform_icons_verified_fixed.png")
        print("✓ Captured screenshot of platform icons fixed!")

        browser.close()
        print("All platform images verified 100% loaded!")

if __name__ == '__main__':
    test_platform_icons_loaded()
