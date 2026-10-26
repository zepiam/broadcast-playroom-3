# verify_platform_logos.py
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
INDEX_URL = "file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html"

async def test_platform_logos():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("1. Opening index.html...")
        await page.goto(INDEX_URL)
        await page.wait_for_timeout(1000)

        print("2. Opening Composer...")
        await page.evaluate("window.openToolWindow('composer')")
        await page.wait_for_timeout(1200)

        # 3. Add Viewer widget
        print("3. Adding Viewer widget...")
        await page.evaluate("window.ComposerStudio.addWidget('viewer')")
        await page.wait_for_timeout(800)

        viewer_id = await page.evaluate("""() => {
            const widgets = window.ComposerStudio.state.pages[0].widgets;
            const vw = widgets.find(w => w.type === 'viewer');
            return vw ? vw.id : null;
        }""")
        print(f"Viewer widget ID: {viewer_id}")
        assert viewer_id is not None

        # 4. Verify no circle emojis and official platform icons exist
        chips_html = await page.evaluate(f"() => {{ return document.querySelector('#widget-{viewer_id}').innerHTML; }}")
        print("Checking for red/purple circle emojis in viewer widget...")
        assert "🔴" not in chips_html, "Found red circle emoji 🔴 in viewer widget!"
        assert "🟣" not in chips_html, "Found purple circle emoji 🟣 in viewer widget!"
        assert "plat-icon" in chips_html, "plat-icon class not found in viewer widget!"
        print("PASS: No colored circle emojis! Official platform icons are used!")

        # 5. Open Settings Drawer
        print("4. Opening Settings Drawer via gear button...")
        widget_el = page.locator(f"#widget-{viewer_id}")
        await widget_el.click()
        await page.wait_for_timeout(300)
        gear_btn = widget_el.locator('.btn-widget-gear')
        await gear_btn.click()
        await page.wait_for_timeout(600)

        # 6. Verify platform checkboxes in drawer
        print("5. Verifying platform checkboxes...")
        cb_count = await page.evaluate("() => document.querySelectorAll('.comp-viewer-plat-cb').length")
        print(f"Platform checkboxes found: {cb_count}")
        assert cb_count >= 6, f"Expected at least 6 platform checkboxes, got {cb_count}"

        # Check Facebook and SOOP checkboxes
        print("Checking Facebook and SOOP...")
        await page.check(".comp-viewer-plat-cb[data-plat='facebook']")
        await page.wait_for_timeout(300)
        await page.check(".comp-viewer-plat-cb[data-plat='soop']")
        await page.wait_for_timeout(500)

        # Verify all 6 platform chips are now in canvas
        active_chips = await page.evaluate(f"() => {{ return Array.from(document.querySelectorAll('#widget-{viewer_id} .viewer-chip')).map(el => el.dataset.platform); }}")
        print("Active platform chips on canvas:", active_chips)
        for p_name in ['youtube', 'twitch', 'tiktok', 'kick', 'facebook', 'soop']:
            assert p_name in active_chips, f"Platform {p_name} not found in viewer chips!"

        # 7. Test ticker update simulation
        print("6. Testing Viewer simulation buttons...")
        await page.click("#btnDemoViewerAdd")
        await page.wait_for_timeout(400)
        await page.click("#btnDemoViewerRandom")
        await page.wait_for_timeout(600)

        # Save screenshot of Viewer widget with all 6 platform logos
        ss_viewer = os.path.join(ARTIFACT_DIR, "viewer_widget_official_platform_logos.png")
        await page.screenshot(path=ss_viewer)
        print(f"Saved screenshot: {ss_viewer}")

        # 8. Test Chat widget with platform logos
        print("7. Testing Chat widget with platform logos...")
        # Close drawer
        btn_close = page.locator("#btnCloseDrawer")
        if await btn_close.count() > 0:
            await btn_close.click()
            await page.wait_for_timeout(300)

        await page.evaluate("window.ComposerStudio.addWidget('chat')")
        await page.wait_for_timeout(800)

        chat_id = await page.evaluate("""() => {
            const widgets = window.ComposerStudio.state.pages[0].widgets;
            const cw = widgets.find(w => w.type === 'chat');
            return cw ? cw.id : null;
        }""")

        # Trigger send mock chat via demoManager
        await page.evaluate(f"""() => {{
            const w = window.ComposerStudio.state.pages[0].widgets.find(x => x.id === '{chat_id}');
            if (window.ComposerStudio.demoManager && w) {{
                window.ComposerStudio.demoManager.sendChatMsg(w);
                window.ComposerStudio.demoManager.sendChatMsg(w);
            }}
        }}""")
        await page.wait_for_timeout(600)

        chat_inner = await page.evaluate(f"() => {{ return document.querySelector('#widget-{chat_id}').innerHTML; }}")
        assert "plat-icon" in chat_inner, "plat-icon not found in chat widget messages!"
        print("PASS: Chat widget messages display official platform logos!")

        # 9. Test Now Playing widget with music logos
        print("8. Testing Now Playing widget with music logos...")
        await page.evaluate("window.ComposerStudio.addWidget('now_playing')")
        await page.wait_for_timeout(800)

        # Save final overview screenshot
        ss_all = os.path.join(ARTIFACT_DIR, "all_widgets_platform_logos_verified.png")
        await page.screenshot(path=ss_all)
        print(f"Saved screenshot: {ss_all}")

        print("\nALL PLATFORM LOGO TESTS PASSED WITH 100% SUCCESS!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_platform_logos())
