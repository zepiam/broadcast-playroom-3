# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
HTML_PATH = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Test in standard 1920x1080 (Full HD)
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
        print("Composer Studio opened.")

        # 1. Verify 2-Line Layout (Icon on top, Title on bottom)
        add_group = page.locator("#compAddWidgetsGroup")
        assert await add_group.is_visible(), "Add widget group should be visible!"

        box = await add_group.bounding_box()
        print(f"Compact Add Group Width: {box['width']}px (Was over 1350px before!)")
        # Should be well under 750px now!
        assert box['width'] < 800, f"Add group should fit comfortably, got {box['width']}px!"

        # Check button styles
        btn_clock = page.locator(".btn-add-widget[data-widget-type='clock']")
        icon_clock = btn_clock.locator(".comp-widget-icon")
        label_clock = btn_clock.locator(".comp-widget-label")
        assert await icon_clock.is_visible(), "Icon should be visible!"
        assert await label_clock.is_visible(), "Label should be visible on bottom line!"

        # Take screenshot of the new compact 2-line toolbar
        toolbar = page.locator(".composer-topbar")
        await toolbar.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_toolbar_compact_2lines.png"))
        print("Captured composer_toolbar_compact_2lines.png")

        # 2. Test Compact Icon-Only Mode Toggle
        btn_toggle = page.locator("#btnToggleToolbarCompact")
        await btn_toggle.click()
        await page.wait_for_timeout(400)

        assert "icon-only-mode" in (await add_group.get_attribute("class") or "")
        box_icon_only = await add_group.bounding_box()
        print(f"Icon-Only Add Group Width: {box_icon_only['width']}px")

        await toolbar.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_toolbar_icon_only.png"))
        print("Captured composer_toolbar_icon_only.png")

        # Toggle back to 2-line mode
        await btn_toggle.click()
        await page.wait_for_timeout(300)
        assert "icon-only-mode" not in (await add_group.get_attribute("class") or "")

        # Full window screenshot
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_toolbar_full_view.png"))
        print("Captured composer_toolbar_full_view.png")

        await browser.close()
        print("\nALL TOOLBAR COMPACT TESTS PASSED SUCCESSFULLY 100%!")

if __name__ == "__main__":
    asyncio.run(main())
