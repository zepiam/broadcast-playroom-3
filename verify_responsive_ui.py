import sys
import os
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_responsive_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Test 1: Standard Desktop Resolution 1600x950
        page = browser.new_page(viewport={'width': 1600, 'height': 950})
        index_url = f"file:///{os.path.abspath('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html').replace(os.sep, '/')}"
        page.goto(index_url)
        page.wait_for_timeout(800)

        # 1. Verify brand badge is removed
        brand = page.locator(".brand-badge")
        assert brand.count() == 0, "Brand badge should be completely removed!"
        print("✓ Brand badge 'Broadcast Playroom v3.0.0' is removed.")

        # 2. Check topbar Server Status
        server_status = page.locator("#topbarServerStatus")
        assert server_status.is_visible(), "Server status must be visible!"
        print("✓ Server status is visible at left of topbar.")

        # 3. Check btnMasterTts height
        btn_tts = page.locator("#btnMasterTts")
        box = btn_tts.bounding_box()
        print(f"✓ btnMasterTts bounding box at 1600px: height={box['height']}px, width={box['width']}px")
        assert box['height'] <= 34, f"btnMasterTts height is {box['height']}px - it wrapped or stretched vertically!"

        # 4. Check btnSimulateChat height
        btn_sim = page.locator("#btnSimulateChat")
        sim_box = btn_sim.bounding_box()
        print(f"✓ btnSimulateChat bounding box at 1600px: height={sim_box['height']}px, width={sim_box['width']}px")
        assert sim_box['height'] <= 34, f"btnSimulateChat height is {sim_box['height']}px - it wrapped vertically!"

        # 5. Check col-events width
        events_col = page.locator("#eventsCol")
        col_box = events_col.bounding_box()
        print(f"✓ col-events width: {col_box['width']}px")
        assert abs(col_box['width'] - 220) <= 2, f"col-events width is {col_box['width']}px, expected 220px!"

        page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/responsive_ui_1600px.png")
        print("✓ Saved 1600px screenshot.")

        # Test 2: Compact / Narrow Window 1366x768
        page.set_viewport_size({'width': 1366, 'height': 768})
        page.wait_for_timeout(500)

        box_compact = btn_tts.bounding_box()
        sim_compact = btn_sim.bounding_box()
        print(f"✓ Compact 1366px: btnMasterTts height={box_compact['height']}px, btnSimulateChat height={sim_compact['height']}px")
        assert box_compact['height'] <= 34, "btnMasterTts wrapped vertically at 1366px!"
        assert sim_compact['height'] <= 34, "btnSimulateChat wrapped vertically at 1366px!"

        page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/responsive_ui_1366px_compact.png")
        print("✓ Saved 1366px compact screenshot.")

        browser.close()
        print("All Responsive UI tests passed 100%!")

if __name__ == '__main__':
    test_responsive_ui()
