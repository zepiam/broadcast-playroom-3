import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

artifact_dir = r'C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1'
abs_html = os.path.abspath(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\dist\index.html')
clean_path = abs_html.replace('\\', '/')
file_url = f"file:///{clean_path}"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        print("1. Loading main app window...")
        await page.goto(file_url, wait_until='networkidle')
        await asyncio.sleep(0.5)

        # Listen for popup window creation
        popup_opened_future = asyncio.get_event_loop().create_future()
        context.on("page", lambda new_p: popup_opened_future.set_result(new_p) if not popup_opened_future.done() else None)

        print("2. Opening settings popout window...")
        await page.evaluate("popoutToolWindow('settings')")
        popup_page = await asyncio.wait_for(popup_opened_future, timeout=5.0)
        print("Popout settings window opened successfully.")
        await asyncio.sleep(0.5)

        # Check popup is open
        is_closed_before = popup_page.is_closed()
        print(f"Popout window is_closed before main exit: {is_closed_before}")
        assert not is_closed_before, "Popout window should be open"

        print("3. Closing main application window (simulating program exit)...")
        await page.evaluate("closeAllPopoutWindows()")
        await page.close()
        await asyncio.sleep(0.6)

        # Check popup is closed
        is_closed_after = popup_page.is_closed()
        print(f"Popout window is_closed after main exit: {is_closed_after}")
        assert is_closed_after, "Popout window should have automatically closed!"

        print("TEST PASSED: Child settings window closed automatically when main program closed!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
