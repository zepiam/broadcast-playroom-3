# verify_now_playing_and_multipage.py
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
INDEX_URL = "file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html"

async def test_now_playing_and_multipage():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # Handle dialogs automatically (for rename and delete)
        dialog_messages = []
        async def on_dialog(dialog):
            dialog_messages.append(dialog.message)
            if dialog.type == "prompt":
                await dialog.accept("ซีนเล่นเกม")
            else:
                await dialog.accept()

        page.on("dialog", lambda dialog: asyncio.create_task(on_dialog(dialog)))

        print("1. Opening index.html...")
        await page.goto(INDEX_URL)
        await page.wait_for_timeout(1000)

        print("2. Opening Composer Studio...")
        await page.evaluate("window.openToolWindow('composer')")
        await page.wait_for_timeout(1200)

        # 3. Test Now Playing Widget
        print("3. Testing Now Playing Widget (Art on left, no source badge)...")
        await page.evaluate("window.ComposerStudio.addWidget('now_playing')")
        await page.wait_for_timeout(800)

        np_id = await page.evaluate("""() => {
            const widgets = window.ComposerStudio.state.pages[0].widgets;
            const np = widgets.find(w => w.type === 'now_playing');
            return np ? np.id : null;
        }""")
        print(f"Now Playing ID: {np_id}")
        assert np_id is not None

        # Check widget inner HTML
        np_html = await page.evaluate(f"() => {{ return document.querySelector('#widget-{np_id}').innerHTML; }}")
        
        # Verify NO source badge
        assert "Spotify</span>" not in np_html, "Found Spotify source badge text!"
        assert "YT Music</span>" not in np_html, "Found YT Music source badge text!"
        assert "Player</span>" not in np_html, "Found Player source badge text!"
        print("PASS: No source badge is displayed in Now Playing widget!")

        # Verify cover art is positioned on the LEFT of the info text
        art_box = await page.locator(f"#widget-{np_id} .np-art").bounding_box()
        info_box = await page.locator(f"#widget-{np_id} .np-info").bounding_box()
        print(f"Art bounding box: {art_box}")
        print(f"Info bounding box: {info_box}")
        assert art_box is not None, "np-art element not found!"
        assert info_box is not None, "np-info element not found!"
        assert art_box['x'] < info_box['x'], f"Cover art must be on the LEFT of info! art.x={art_box['x']}, info.x={info_box['x']}"
        # Also verify they are in horizontal row (art top ~ info top)
        assert abs(art_box['y'] - info_box['y']) < 30, "Cover art and info must be aligned in a horizontal row!"
        print("PASS: Cover art is strictly on the LEFT, and info is on the RIGHT in row layout!")

        # 4. Test Multi-Page System
        print("4. Testing Multi-Page System...")
        # Check page bar existence
        page_bar = page.locator(".composer-page-bar")
        assert await page_bar.count() > 0, "composer-page-bar not found!"

        # Check initial tabs
        init_tab_count = await page.locator(".composer-page-tab").count()
        print(f"Initial page tabs: {init_tab_count}")
        assert init_tab_count >= 1

        # Click "+ หน้าใหม่"
        print("Clicking '+ หน้าใหม่'...")
        await page.click("#btnPageNew")
        await page.wait_for_timeout(600)

        tabs_after_new = await page.locator(".composer-page-tab").count()
        print(f"Page tabs after new: {tabs_after_new}")
        assert tabs_after_new == init_tab_count + 1

        # Add a clock widget on page 2
        print("Adding clock widget on Page 2...")
        await page.evaluate("window.ComposerStudio.addWidget('clock')")
        await page.wait_for_timeout(600)

        # Duplicate Page 2
        print("Clicking '⧉ สำเนา'...")
        await page.click("#btnPageDup")
        await page.wait_for_timeout(600)

        tabs_after_dup = await page.locator(".composer-page-tab").count()
        print(f"Page tabs after duplicate: {tabs_after_dup}")
        assert tabs_after_dup == tabs_after_new + 1

        # Rename active page
        print("Clicking '✎ เปลี่ยนชื่อ'...")
        await page.click("#btnPageRename")
        await page.wait_for_timeout(600)

        active_tab_text = await page.locator(".composer-page-tab.active").inner_text()
        print(f"Active tab after rename: {active_tab_text}")
        assert "ซีนเล่นเกม" in active_tab_text, "Page rename failed!"

        # Save screenshot of multi-page bar and now playing
        ss_multipage = os.path.join(ARTIFACT_DIR, "composer_multipage_and_nowplaying.png")
        await page.screenshot(path=ss_multipage)
        print(f"Saved screenshot: {ss_multipage}")

        # Delete the cloned page
        print("Clicking '🗑 ลบ'...")
        await page.click("#btnPageDel")
        await page.wait_for_timeout(600)

        tabs_after_del = await page.locator(".composer-page-tab").count()
        print(f"Page tabs after delete: {tabs_after_del}")
        assert tabs_after_del == tabs_after_dup - 1

        # Switch back to Page 1
        print("Switching back to Page 1...")
        first_tab = page.locator(".composer-page-tab").first
        await first_tab.click()
        await page.wait_for_timeout(600)

        # Verify Now Playing widget on Page 1 is still present and intact
        np_on_page1 = page.locator(f"#widget-{np_id}")
        assert await np_on_page1.count() > 0, "Now Playing widget was lost after switching pages!"
        print("PASS: Page 1 widgets preserved perfectly!")

        # Save final screenshot
        ss_final = os.path.join(ARTIFACT_DIR, "now_playing_left_cover_multipage_final.png")
        await page.screenshot(path=ss_final)
        print(f"Saved screenshot: {ss_final}")

        print("\nALL NOW PLAYING & MULTI-PAGE TESTS PASSED WITH 100% SUCCESS!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_now_playing_and_multipage())
