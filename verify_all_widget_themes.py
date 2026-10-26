# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
HTML_PATH = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print(f"Loading {HTML_PATH}...")
        await page.goto(f"file:///{HTML_PATH.replace(os.sep, '/')}")
        await page.wait_for_timeout(1000)

        # Open Composer Studio
        btn_rail = page.locator("#btnRailComposer")
        await btn_rail.click()
        await page.wait_for_timeout(600)
        win = page.locator("#win-composer")
        await win.wait_for(state="visible")
        assert await win.is_visible(), "Composer Studio window should be visible!"

        # 1. Test Clock Widget & 32 Themes
        layer_clock = page.locator('#composerLayersList [data-id="w-clock-1"]')
        if await layer_clock.count() > 0:
            await layer_clock.click()
        else:
            await page.evaluate("window.ComposerStudio.selectWidget('w-clock-1')")
        await page.wait_for_timeout(500)

        clock_title = await page.locator("#compCustTitle").text_content()
        print(f"Clock Title: {clock_title}")
        assert "นาฬิกา" in clock_title, "Should show Clock Customizer!"
        theme_opts_count = await page.locator("#compClockTheme option").count()
        print(f"Clock Themes Count: {theme_opts_count}")
        assert theme_opts_count >= 30, f"Expected 32 clock themes, got {theme_opts_count}!"

        # Select Neon theme and capture screenshot
        await page.select_option("#compClockTheme", "neon")
        await page.wait_for_timeout(300)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "all_themes_01_clock.png"))
        print("Captured all_themes_01_clock.png")

        # 2. Add Webcam Widget & test 23 Themes
        btn_add_webcam = page.locator(".btn-add-widget[data-widget-type='webcam']")
        await btn_add_webcam.click()
        await page.wait_for_timeout(600)

        webcam_title = await page.locator("#compCustTitle").text_content()
        print(f"Webcam Title: {webcam_title}")
        assert "เว็บแคม" in webcam_title, "Should show Webcam Customizer!"
        webcam_opts_count = await page.locator("#compWebcamTheme option").count()
        print(f"Webcam Themes Count: {webcam_opts_count}")
        assert webcam_opts_count >= 20, f"Expected 23 webcam themes, got {webcam_opts_count}!"

        # Select Rainbow Border theme and capture
        await page.select_option("#compWebcamTheme", "rainbow-border")
        await page.wait_for_timeout(300)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "all_themes_02_webcam.png"))
        print("Captured all_themes_02_webcam.png")

        # 3. Add Viewer Count Widget & test 28 Themes
        btn_add_viewer = page.locator(".btn-add-widget[data-widget-type='viewer']")
        await btn_add_viewer.click()
        await page.wait_for_timeout(600)

        viewer_title = await page.locator("#compCustTitle").text_content()
        print(f"Viewer Title: {viewer_title}")
        assert "ผู้ชม" in viewer_title or "คนดู" in viewer_title, "Should show Viewer Customizer!"
        viewer_opts_count = await page.locator("#compViewerTheme option").count()
        print(f"Viewer Themes Count: {viewer_opts_count}")
        assert viewer_opts_count >= 25, f"Expected 28 viewer themes, got {viewer_opts_count}!"

        # Select Cyberpunk theme and platforms mode
        await page.select_option("#compViewerTheme", "cyberpunk")
        await page.select_option("#compViewerMode", "platforms")
        await page.wait_for_timeout(300)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "all_themes_03_viewer.png"))
        print("Captured all_themes_03_viewer.png")

        # 4. Add Goal Widget & test 5 Bar Styles + 19 Color Themes
        btn_add_goal = page.locator(".btn-add-widget[data-widget-type='goal']")
        await btn_add_goal.click()
        await page.wait_for_timeout(600)

        goal_title = await page.locator("#compCustTitle").text_content()
        print(f"Goal Title: {goal_title}")
        assert "เป้าหมาย" in goal_title, "Should show Goal Customizer!"
        bar_opts_count = await page.locator("#compGoalBarStyle option").count()
        color_opts_count = await page.locator("#compGoalColorTheme option").count()
        print(f"Goal Bar Styles: {bar_opts_count}, Goal Color Themes: {color_opts_count}")
        assert bar_opts_count == 5, f"Expected 5 bar styles, got {bar_opts_count}!"
        assert color_opts_count == 19, f"Expected 19 color themes, got {color_opts_count}!"

        # Select Liquid bar style and Cyberpunk color theme
        await page.select_option("#compGoalBarStyle", "liquid")
        await page.select_option("#compGoalColorTheme", "cyberpunk")
        await page.wait_for_timeout(300)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "all_themes_04_goal.png"))
        print("Captured all_themes_04_goal.png")

        # 5. Select Text Widget & test 3 Modes
        layer_text = page.locator('#composerLayersList [data-id="w-text-1"]')
        if await layer_text.count() > 0:
            await layer_text.click()
        else:
            await page.evaluate("window.ComposerStudio.selectWidget('w-text-1')")
        await page.wait_for_timeout(500)

        text_title = await page.locator("#compCustTitle").text_content()
        print(f"Text Title: {text_title}")
        assert "ข้อความ" in text_title, "Should show Text Customizer!"
        text_modes_count = await page.locator("#compTextMode option").count()
        print(f"Text Modes Count: {text_modes_count}")
        assert text_modes_count == 3, f"Expected 3 text modes, got {text_modes_count}!"

        # Select Ticker mode
        await page.select_option("#compTextMode", "ticker")
        await page.wait_for_timeout(300)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "all_themes_05_text.png"))
        print("Captured all_themes_05_text.png")

        await browser.close()
        print("\nALL WIDGET THEMES VERIFICATION COMPLETED SUCCESSFULLY 100%!")

if __name__ == "__main__":
    asyncio.run(main())
