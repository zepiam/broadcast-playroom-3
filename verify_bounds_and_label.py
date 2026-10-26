# verify_bounds_and_label.py
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
INDEX_URL = "file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html"

async def test_bounds_and_label():
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

        # 3. Test Widget at the very top of canvas (y = 0)
        print("3. Testing Widget at the very top of canvas (y = 0)...")
        # Align selected widget to Top via button [data-align="top"]
        await page.evaluate("""() => {
            const w = window.ComposerStudio.state.pages[0].widgets[0];
            window.ComposerStudio.selectWidget(w.id);
        }""")
        btn_top = page.locator('[data-align="top"]')
        if await btn_top.count() > 0:
            await btn_top.click()
        else:
            await page.evaluate("""() => {
                const w = window.ComposerStudio.state.pages[0].widgets[0];
                w.y = 0;
                window.ComposerStudio.renderCanvasWidgets();
            }""")
        await page.wait_for_timeout(600)

        # Check badge position when y = 0
        w_state = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0]")
        print(f"Widget pos: x={w_state['x']}, y={w_state['y']}")
        assert w_state['y'] == 0, f"Expected y=0, got {w_state['y']}"

        w_el = page.locator(f"#widget-{w_state['id']}")
        has_bottom_class = await w_el.evaluate("el => el.classList.contains('badge-at-bottom')")
        badge_el = w_el.locator(".composer-widget-badge")
        has_badge_bottom = await badge_el.evaluate("el => el.classList.contains('badge-bottom')")
        print(f"has_bottom_class: {has_bottom_class}, has_badge_bottom: {has_badge_bottom}")
        assert has_bottom_class and has_badge_bottom, "Badge should have badge-bottom class when widget is at top!"

        # Check computed style of badge: top should be calc(100% + 4px)
        badge_top_style = await badge_el.evaluate("el => window.getComputedStyle(el).top")
        print(f"Badge computed top: {badge_top_style}")
        assert float(badge_top_style.replace('px', '')) > 0, "Badge top must be positive (below the frame), NOT negative!"

        # Screenshot of widget at top with label flipped underneath
        shot_top = os.path.join(ARTIFACT_DIR, "widget_at_top_label_underneath.png")
        await page.screenshot(path=shot_top)
        print(f"Saved screenshot: {shot_top}")

        # 4. Move widget down (y = 150)
        print("4. Moving widget down (y = 150)...")
        await page.evaluate("""() => {
            const w = window.ComposerStudio.state.pages[0].widgets[0];
            w.y = 150;
            window.ComposerStudio.renderCanvasWidgets();
        }""")
        await page.wait_for_timeout(500)

        has_bottom_class_after = await w_el.evaluate("el => el.classList.contains('badge-at-bottom')")
        print(f"has_bottom_class at y=150: {has_bottom_class_after}")
        assert not has_bottom_class_after, "Badge should NOT be at bottom when y >= 26!"

        badge_top_after = await badge_el.evaluate("el => window.getComputedStyle(el).top")
        print(f"Badge computed top at y=150: {badge_top_after}")
        assert float(badge_top_after.replace('px', '')) < 0, "Badge top should be -24px above frame when y >= 26!"

        # 5. Test Width expansion clamping (never exceed canvas 1920)
        print("5. Testing Width expansion clamping...")
        # Set x = 1500, try to set width = 800 via inspector input #compPropW
        await page.evaluate("""() => {
            const w = window.ComposerStudio.state.pages[0].widgets[0];
            w.x = 1500;
            w.width = 300;
            window.ComposerStudio.renderCanvasWidgets();
            window.ComposerStudio.updateTransformInspector();
        }""")
        await page.wait_for_timeout(400)

        inp_w = page.locator("#compPropW")
        await inp_w.fill("800")
        await inp_w.dispatch_event("change")
        await page.wait_for_timeout(500)

        w_clamped = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0]")
        print(f"Widget after attempting width 800 at x=1500: x={w_clamped['x']}, width={w_clamped['width']}, rightEdge={w_clamped['x'] + w_clamped['width']}")
        assert w_clamped['x'] + w_clamped['width'] <= 1920, f"Widget right edge exceeded 1920: {w_clamped['x'] + w_clamped['width']}"
        assert w_clamped['width'] == 420, f"Expected clamped width 420 (1920 - 1500), got {w_clamped['width']}"

        # 6. Test dragging beyond canvas edges
        print("6. Testing drag and resize boundary clamping...")
        # Verify arrow keys clamping
        await page.evaluate("""() => {
            const w = window.ComposerStudio.state.pages[0].widgets[0];
            w.x = 10;
            w.y = 10;
            window.ComposerStudio.renderCanvasWidgets();
        }""")
        # Press ArrowLeft multiple times
        for _ in range(5):
            await page.keyboard.press("Shift+ArrowLeft")
            await page.keyboard.press("Shift+ArrowUp")
        await page.wait_for_timeout(300)

        w_arrows = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0]")
        print(f"Widget after moving left/up beyond 0: x={w_arrows['x']}, y={w_arrows['y']}")
        assert w_arrows['x'] >= 0, f"Widget x should be >= 0, got {w_arrows['x']}"
        assert w_arrows['y'] >= 0, f"Widget y should be >= 0, got {w_arrows['y']}"

        # Screenshot of clamped widget near edge
        shot_bounds = os.path.join(ARTIFACT_DIR, "widget_bounds_clamped_1920.png")
        await page.screenshot(path=shot_bounds)
        print(f"Saved screenshot: {shot_bounds}")

        await browser.close()
        print("\nALL BOUNDS & LABEL TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    asyncio.run(test_bounds_and_label())
