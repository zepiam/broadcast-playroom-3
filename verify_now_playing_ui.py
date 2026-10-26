# verify_now_playing_ui.py
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
INDEX_URL = "file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html"

async def test_composer_now_playing():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("1. Opening index.html...")
        await page.goto(INDEX_URL)
        await page.wait_for_timeout(1000)

        # Open Composer
        print("2. Opening Composer...")
        await page.evaluate("window.openToolWindow('composer')")
        await page.wait_for_timeout(1200)

        # Add Now Playing Widget
        print("3. Adding Now Playing widget...")
        await page.evaluate("window.ComposerStudio.addWidget('now_playing')")
        await page.wait_for_timeout(800)

        # Find the newly added now_playing widget ID
        np_id = await page.evaluate("""() => {
            const widgets = window.ComposerStudio.state.pages[0].widgets;
            const np = widgets.find(w => w.type === 'now_playing');
            return np ? np.id : null;
        }""")
        print(f"Now Playing widget ID: {np_id}")
        assert np_id is not None, "Failed to create now_playing widget"

        # Click widget to select it
        print("4. Selecting widget...")
        widget_el = page.locator(f"#widget-{np_id}")
        await widget_el.click()
        await page.wait_for_timeout(500)

        # Open Settings Drawer via gear button .btn-widget-gear
        print("5. Opening Settings Drawer via gear button...")
        gear_btn = widget_el.locator('.btn-widget-gear')
        await gear_btn.click()
        await page.wait_for_timeout(600)

        is_open = await page.evaluate("!document.getElementById('composerSidebarLeft').classList.contains('collapsed')")
        assert is_open, "Settings drawer did not open"
        print("Settings drawer successfully opened!")

        # Check #compNpSource dropdown options
        print("6. Checking #compNpSource options...")
        sel = page.locator("#compNpSource")
        assert await sel.count() > 0, "#compNpSource dropdown not found!"

        options = await sel.locator("option").all_inner_texts()
        print(f"Dropdown options found: {options}")
        assert "ทุกแหล่งที่กำลังเล่น" in options[0]
        assert "Spotify เท่านั้น" in options[1]
        assert "YouTube Music เท่านั้น" in options[2]
        assert "เครื่องเล่นมีเดียในคอมพิวเตอร์" in options[3]

        # Select YouTube Music
        print("7. Selecting 'YouTube Music เท่านั้น'...")
        await sel.select_option("ytmusic")
        await page.wait_for_timeout(500)

        # Verify badge in canvas widget
        badge_text = await page.locator(f"#widget-{np_id} .widget-type-now-playing").inner_text()
        print(f"Widget text after YT Music selection: {badge_text}")
        assert "YT Music" in badge_text, f"Expected 'YT Music' badge, got: {badge_text}"

        # Click demo trigger next song
        btn_next = page.locator("#btnDemoNowPlayingNext")
        if await btn_next.count() > 0:
            print("8. Clicking demo song change button...")
            await btn_next.click()
            await page.wait_for_timeout(400)
            song_title = await page.locator("#compNpTitle").input_value()
            artist = await page.locator("#compNpArtist").input_value()
            print(f"Demo song: '{song_title}' by '{artist}'")
            assert "YouTube Music" in artist or "YOASOBI" in artist or "King Gnu" in artist or "Creepy Nuts" in artist or "Kenshi Yonezu" in artist

        # Take screenshot of YouTube Music setting
        shot_yt = os.path.join(ARTIFACT_DIR, "now_playing_ytmusic_selected.png")
        await page.screenshot(path=shot_yt)
        print(f"Screenshot saved: {shot_yt}")

        # Select desktop_player
        print("9. Selecting 'เครื่องเล่นมีเดียในคอมพิวเตอร์'...")
        await sel.select_option("desktop_player")
        await page.wait_for_timeout(500)
        badge_dp = await page.locator(f"#widget-{np_id} .widget-type-now-playing").inner_text()
        assert "Player" in badge_dp, f"Expected 'Player' badge, got: {badge_dp}"

        if await btn_next.count() > 0:
            await btn_next.click()
            await page.wait_for_timeout(400)
            artist_dp = await page.locator("#compNpArtist").input_value()
            print(f"Desktop player demo: '{artist_dp}'")

        # Take screenshot of Desktop Player setting
        shot_dp = os.path.join(ARTIFACT_DIR, "now_playing_desktop_player_selected.png")
        await page.screenshot(path=shot_dp)
        print(f"Screenshot saved: {shot_dp}")

        # Select Spotify
        print("10. Selecting 'Spotify เท่านั้น'...")
        await sel.select_option("spotify")
        await page.wait_for_timeout(500)
        badge_sp = await page.locator(f"#widget-{np_id} .widget-type-now-playing").inner_text()
        assert "Spotify" in badge_sp, f"Expected 'Spotify' badge, got: {badge_sp}"

        # Take screenshot of Spotify setting
        shot_sp = os.path.join(ARTIFACT_DIR, "now_playing_spotify_selected.png")
        await page.screenshot(path=shot_sp)
        print(f"Screenshot saved: {shot_sp}")

        await browser.close()
        print("\nALL PLAYWRIGHT TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    asyncio.run(test_composer_now_playing())
