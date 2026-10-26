import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html")
        await page.wait_for_timeout(1000)

        # Open Composer Studio
        await page.evaluate("() => { if (window.openToolWindow) window.openToolWindow('composer'); else document.getElementById('win-composer').classList.add('active'); }")
        await page.wait_for_timeout(600)

        win = page.locator("#win-composer")
        assert await win.is_visible(), "Composer window not visible"

        # 1. VERIFY RIGHT SIDEBAR NO HORIZONTAL SCROLLBAR
        sb_right_info = await page.evaluate('''() => {
          const sb = document.querySelector('.composer-sidebar-right');
          const layers = document.querySelector('.composer-layers-list');
          const props = document.querySelector('.composer-props-body');
          return {
            sbClientWidth: sb.clientWidth,
            sbScrollWidth: sb.scrollWidth,
            hasSbHorizontalScroll: sb.scrollWidth > sb.clientWidth,
            layersClientWidth: layers.clientWidth,
            layersScrollWidth: layers.scrollWidth,
            hasLayersHorizontalScroll: layers.scrollWidth > layers.clientWidth,
            propsClientWidth: props.clientWidth,
            propsScrollWidth: props.scrollWidth,
            hasPropsHorizontalScroll: props.scrollWidth > props.clientWidth
          };
        }''')
        print("Right sidebar horizontal scroll check:", sb_right_info)
        assert not sb_right_info["hasSbHorizontalScroll"], f"Right sidebar has horizontal scrollbar: {sb_right_info}"
        assert not sb_right_info["hasLayersHorizontalScroll"], f"Layers list has horizontal scrollbar: {sb_right_info}"
        assert not sb_right_info["hasPropsHorizontalScroll"], f"Props body has horizontal scrollbar: {sb_right_info}"
        print("SUCCESS: 0 horizontal scrollbars in right sidebar!")

        # 2. CLICK CHAT WIDGET ON CANVAS -> LEFT PANEL OPENS
        chat_widget = page.locator("#composerCanvasStage .composer-widget[id*='chat']").first
        if await chat_widget.count() == 0:
            chat_widget = page.locator("#composerCanvasStage .composer-widget").first
        
        await chat_widget.click()
        await page.wait_for_timeout(400)

        left_panel = page.locator("#composerSidebarLeft")
        assert await left_panel.is_visible(), "Left customizer panel did not open on widget click"
        
        title_text = await page.locator("#compCustTitle").text_content()
        print("Left panel opened with title:", title_text)
        
        # Verify chat mode tabs exist
        tabs_count = await page.locator(".cwc-tab-btn[data-set-chat-mode]").count()
        print(f"Chat mode tabs count: {tabs_count}")
        assert tabs_count >= 5, "Chat mode switcher tabs missing"

        # Switch to Theme mode
        await page.locator(".cwc-tab-btn[data-set-chat-mode='theme']").click()
        await page.wait_for_timeout(300)
        
        # Pick cyberpunk theme
        theme_card = page.locator(".cwc-preset-card[data-chat-theme='cyberpunk']")
        if await theme_card.count() > 0:
            await theme_card.click()
            await page.wait_for_timeout(300)
            print("Selected cyberpunk theme in left panel")

        await win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/composer_left_panel_chat.png")
        print("Saved composer_left_panel_chat.png")

        # 3. TEST COLLAPSE & EXPAND
        btn_collapse = page.locator("#btnCollapseCustPanel")
        await btn_collapse.click()
        await page.wait_for_timeout(300)
        
        is_collapsed = await page.evaluate("() => document.getElementById('composerSidebarLeft').classList.contains('collapsed')")
        assert is_collapsed, "Left panel failed to collapse"
        
        btn_expand = page.locator("#btnExpandCustPanel")
        assert await btn_expand.is_visible(), "Expand button not visible after collapse"
        print("Collapse verified. Expand button visible:", await btn_expand.text_content())

        await win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/composer_panel_collapsed.png")
        print("Saved composer_panel_collapsed.png")

        # Click expand button
        await btn_expand.click()
        await page.wait_for_timeout(300)
        is_open = await page.evaluate("() => !document.getElementById('composerSidebarLeft').classList.contains('collapsed')")
        assert is_open, "Left panel failed to re-expand"
        print("Re-expand verified.")

        # 4. CLICK CLOCK WIDGET ON CANVAS
        clock_widget = page.locator("#composerCanvasStage .composer-widget[id*='clock']").first
        if await clock_widget.count() > 0:
            await clock_widget.click()
            await page.wait_for_timeout(400)
            
            cust_title = await page.locator("#compCustTitle").text_content()
            print("Clock selected, customizer title:", cust_title)
            
            # Select neon theme
            await page.locator("#compClockTheme").select_option("neon")
            await page.wait_for_timeout(200)
            
            # Select 12h format
            await page.locator("#compClockFormat").select_option("12")
            await page.wait_for_timeout(300)
            
            await win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/composer_left_panel_clock.png")
            print("Saved composer_left_panel_clock.png")

        # 5. CLICK TEXT WIDGET ON CANVAS
        text_widget = page.locator("#composerCanvasStage .composer-widget[id*='text']").first
        if await text_widget.count() > 0:
            await text_widget.click()
            await page.wait_for_timeout(400)
            
            # Select ticker mode
            await page.locator("#compTextMode").select_option("ticker")
            await page.wait_for_timeout(300)
            
            await win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/composer_left_panel_text.png")
            print("Saved composer_left_panel_text.png")

        # 6. ADD WEBCAM WIDGET FROM TOOLBAR
        btn_add_cam = page.locator(".btn-add-widget[data-widget-type='webcam']")
        await btn_add_cam.click()
        await page.wait_for_timeout(400)
        
        # Verify left panel auto-opens for webcam
        cust_title = await page.locator("#compCustTitle").text_content()
        print("Webcam added, customizer title:", cust_title)
        assert "เว็บแคม" in cust_title, f"Customizer title not webcam: {cust_title}"

        # Change streamer name and border color
        await page.locator("#compWebcamStreamerName").fill("MENG GAMING LIVE")
        await page.locator("#compWebcamStreamerName").dispatch_event("input")
        await page.wait_for_timeout(300)

        await win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/composer_left_panel_webcam.png")
        print("Saved composer_left_panel_webcam.png")

        # 7. ADD GOAL WIDGET FROM TOOLBAR
        btn_add_goal = page.locator(".btn-add-widget[data-widget-type='goal']")
        await btn_add_goal.click()
        await page.wait_for_timeout(400)
        
        cust_title = await page.locator("#compCustTitle").text_content()
        print("Goal added, customizer title:", cust_title)
        assert "เป้าหมาย" in cust_title, f"Customizer title not goal: {cust_title}"

        await page.locator("#compGoalCurrent").fill("850")
        await page.locator("#compGoalCurrent").dispatch_event("input")
        await page.wait_for_timeout(300)

        await win.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/composer_left_panel_goal.png")
        print("Saved composer_left_panel_goal.png")

        await browser.close()
        print("ALL TESTS PASSED 100%! UNIFIED CUSTOMIZER & SCROLLBAR FIX VERIFIED!")

asyncio.run(run())
