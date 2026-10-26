import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

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

        popup_opened_future = asyncio.get_event_loop().create_future()
        context.on("page", lambda new_p: popup_opened_future.set_result(new_p) if not popup_opened_future.done() else None)

        print("2. Opening settings popout window...")
        await page.evaluate("popoutToolWindow('settings')")
        popup_page = await asyncio.wait_for(popup_opened_future, timeout=5.0)
        await asyncio.sleep(0.5)

        print("3. Closing main page directly (hard close, no manual cleanup)...")
        await page.close()
        
        # Wait up to 1 second for the 200ms heartbeat inside popup to detect opener is closed and close itself
        print("Waiting for popup heartbeat auto-close...")
        for _ in range(10):
            await asyncio.sleep(0.15)
            if popup_page.is_closed():
                break

        is_closed_after = popup_page.is_closed()
        print(f"Popout window is_closed via heartbeat: {is_closed_after}")
        assert is_closed_after, "Popout window heartbeat should have auto-closed the popup!"

        print("HEARTBEAT AUTO-CLOSE TEST PASSED!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
