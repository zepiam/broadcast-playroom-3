import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def verify():
    dist_html_path = os.path.abspath('dist/index.html').replace('\\', '/')
    file_url = f"file:///{dist_html_path}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        # 1. Test Main Window
        print("Navigating to main window:", file_url)
        await page.goto(file_url, wait_until="networkidle")
        
        icon = page.locator(".desktop-titlebar-icon")
        assert await icon.count() > 0, "Icon not found"
        box = await icon.bounding_box()
        print(f"Desktop titlebar icon bounding box: {box}")
        assert box['width'] <= 20 and box['height'] <= 20, f"Icon is too large! Width={box['width']}, Height={box['height']}"
        
        body_bg = await page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
        print(f"Body background color: {body_bg}")
        assert "rgb(30, 31, 34)" in body_bg or "rgb(43, 45, 49)" in body_bg or "rgb(2, 6, 23)" in body_bg, f"Unexpected body background: {body_bg}"
        
        await page.screenshot(path="tests/verified_main_window_clean.png")
        print("Main window screenshot saved to tests/verified_main_window_clean.png")
        
        # 2. Test Popout Mode (settings)
        popout_url = f"{file_url}?popout=settings"
        print("Navigating to popout mode:", popout_url)
        page_popout = await browser.new_page(viewport={"width": 800, "height": 600})
        await page_popout.goto(popout_url, wait_until="networkidle")
        
        # In popout mode, desktop titlebar must be hidden
        titlebar_display = await page_popout.evaluate("() => { const el = document.getElementById('desktopTitlebar'); return el ? window.getComputedStyle(el).display : 'none'; }")
        print(f"Popout desktop titlebar display: {titlebar_display}")
        assert titlebar_display == 'none', f"Desktop titlebar should be hidden in popout mode, got: {titlebar_display}"
        
        # In popout mode, floating-actions-right must be hidden
        actions_display = await page_popout.evaluate("() => { const el = document.querySelector('#win-settings .floating-actions-right'); return el ? window.getComputedStyle(el).display : 'none'; }")
        print(f"Popout floating-actions-right display: {actions_display}")
        assert actions_display == 'none', f"Floating actions should be hidden in popout mode, got: {actions_display}"
        
        await page_popout.screenshot(path="tests/verified_popout_window_clean.png")
        print("Popout window screenshot saved to tests/verified_popout_window_clean.png")
        
        await browser.close()
        print("ALL PLAYWRIGHT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(verify())
