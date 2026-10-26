# verify_full_now_playing.py
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
INDEX_URL = "file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html"

async def test_full_now_playing():
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

        # 3. Add Now Playing widget
        print("3. Adding Now Playing widget...")
        await page.evaluate("window.ComposerStudio.addWidget('now_playing')")
        await page.wait_for_timeout(800)

        np_id = await page.evaluate("""() => {
            const widgets = window.ComposerStudio.state.pages[0].widgets;
            const np = widgets.find(w => w.type === 'now_playing');
            return np ? np.id : null;
        }""")
        print(f"Now Playing widget ID: {np_id}")
        assert np_id is not None

        # 4. Open Settings Drawer
        print("4. Opening Settings Drawer via gear button...")
        widget_el = page.locator(f"#widget-{np_id}")
        await widget_el.click()
        await page.wait_for_timeout(300)
        gear_btn = widget_el.locator('.btn-widget-gear')
        await gear_btn.click()
        await page.wait_for_timeout(600)

        # 5. Verify manual text inputs for songTitle and artist are REMOVED
        print("5. Verifying removal of manual songTitle and artist inputs...")
        assert await page.locator("#compNpTitle").count() == 0, "compNpTitle must NOT exist!"
        assert await page.locator("#compNpArtist").count() == 0, "compNpArtist must NOT exist!"
        print("PASS: Song title and artist text inputs have been completely removed!")

        # 6. Verify all 5 cards exist
        print("6. Verifying all 5 setting cards...")
        sel_source = page.locator("#compNpSource")
        sel_theme = page.locator("#compNpTheme")
        sel_style = page.locator("#compNpStyle")
        font_size = page.locator("#compNpFontSize")
        artist_size = page.locator("#compNpArtistFontSize")
        time_size = page.locator("#compNpTimeFontSize")
        txt_clr = page.locator("#compNpTextColor")
        acc_clr = page.locator("#compNpAccentColor")
        chk_art = page.locator("#compNpShowArt")
        chk_prog = page.locator("#compNpShowProgress")
        chk_scroll = page.locator("#compNpScrollTitle")
        sel_sync = page.locator("#compNpSyncMode")
        chk_trans = page.locator("#compNpTransparent")
        bg_clr = page.locator("#compNpBgColor")
        bg_op = page.locator("#compNpBgOpacity")
        box_rad = page.locator("#compNpRadius")
        art_rad = page.locator("#compNpArtRadius")
        art_size = page.locator("#compNpArtSize")

        assert await sel_source.count() > 0, "compNpSource missing"
        assert await sel_theme.count() > 0, "compNpTheme missing"
        assert await sel_style.count() > 0, "compNpStyle missing"
        assert await font_size.count() > 0, "compNpFontSize missing"
        assert await artist_size.count() > 0, "compNpArtistFontSize missing"
        assert await time_size.count() > 0, "compNpTimeFontSize missing"
        assert await txt_clr.count() > 0, "compNpTextColor missing"
        assert await acc_clr.count() > 0, "compNpAccentColor missing"
        assert await chk_art.count() > 0, "compNpShowArt missing"
        assert await chk_prog.count() > 0, "compNpShowProgress missing"
        assert await chk_scroll.count() > 0, "compNpScrollTitle missing"
        assert await sel_sync.count() > 0, "compNpSyncMode missing"
        assert await chk_trans.count() > 0, "compNpTransparent missing"
        assert await bg_clr.count() > 0, "compNpBgColor missing"
        assert await bg_op.count() > 0, "compNpBgOpacity missing"
        assert await box_rad.count() > 0, "compNpRadius missing"
        assert await art_rad.count() > 0, "compNpArtRadius missing"
        assert await art_size.count() > 0, "compNpArtSize missing"
        print("PASS: All 18 V2 settings controls are present!")

        # 7. Test Theme Preset Application (Cyberpunk)
        print("7. Testing Theme preset application (Cyberpunk)...")
        await sel_theme.select_option("cyberpunk")
        await page.wait_for_timeout(500)
        bg_val = await bg_clr.input_value()
        acc_val = await acc_clr.input_value()
        txt_val = await txt_clr.input_value()
        print(f"Cyberpunk theme applied: bg={bg_val}, accent={acc_val}, text={txt_val}")
        assert bg_val.lower() == "#0a0014"
        assert acc_val.lower() == "#00ffff"
        assert txt_val.lower() == "#ff00ff"

        # 8. Test Style Selection (CRT Scanline)
        print("8. Testing Style selection (CRT)...")
        await sel_style.select_option("crt")
        await page.wait_for_timeout(500)
        overlay_class = await page.locator(f"#widget-{np_id} .np-style-overlay").evaluate("el => el.className")
        print(f"Overlay classes: {overlay_class}")
        assert "np-style-crt" in overlay_class, "Overlay must have np-style-crt class"

        # Screenshot of Cyberpunk + CRT
        shot1 = os.path.join(ARTIFACT_DIR, "now_playing_v2_cyberpunk_crt.png")
        await page.screenshot(path=shot1)
        print(f"Saved screenshot: {shot1}")

        # 9. Test Theme Preset (Apple Music) + Style (Vinyl)
        print("9. Testing Apple Music + Vinyl...")
        await sel_theme.select_option("applemusic")
        await sel_style.select_option("vinyl")
        await page.wait_for_timeout(500)
        bg_val2 = await bg_clr.input_value()
        assert bg_val2.lower() == "#fc2c55"
        overlay_class2 = await page.locator(f"#widget-{np_id} .np-style-overlay").evaluate("el => el.className")
        assert "np-style-vinyl" in overlay_class2

        # Screenshot of Apple Music + Vinyl
        shot2 = os.path.join(ARTIFACT_DIR, "now_playing_v2_applemusic_vinyl.png")
        await page.screenshot(path=shot2)
        print(f"Saved screenshot: {shot2}")

        await browser.close()
        print("\nALL V2 NOW PLAYING TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    asyncio.run(test_full_now_playing())
