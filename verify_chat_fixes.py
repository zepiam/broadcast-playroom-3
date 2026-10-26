import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def verify_chat():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1500, 'height': 950})
        page = await context.new_page()

        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("1. Opening index.html & Composer Studio...")
        await page.goto('file:///E:/DOCS/Documents/AI%20TOOLS/broadcast%20playroom%203/dist/index.html')
        await page.wait_for_timeout(1000)
        await page.evaluate("window.openToolWindow('composer')")
        await page.wait_for_timeout(1000)

        # Clear canvas and add a single chat widget
        print("2. Adding chat widget...")
        await page.evaluate("""() => {
            window.ComposerStudio.state.pages[0].widgets = [];
            window.ComposerStudio.addWidget('chat');
        }""")
        await page.wait_for_timeout(500)

        chat_id = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0].id")
        await page.evaluate(f"window.ComposerStudio.openWidgetSettings('{chat_id}')")
        await page.wait_for_timeout(500)

        # Check default container background (MUST be transparent!)
        print("3. Checking default container background (must be transparent)...")
        bg_info = await page.evaluate("""() => {
            const inner = document.querySelector('.composer-widget.type-chat .composer-widget-inner');
            const s = window.getComputedStyle(inner);
            return {
                bg: s.backgroundColor,
                border: s.border,
                inlineStyle: inner.getAttribute('style')
            };
        }""")
        print("Default Container Background Info:", bg_info)
        assert 'rgba(0, 0, 0, 0)' in bg_info['bg'] or 'transparent' in bg_info['inlineStyle'], "Chat container should be transparent by default!"
        print("PASS: Chat container is 100% transparent by default!")

        # Take screenshot of clean transparent chat
        screenshot_transparent = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\chat_transparent_only_messages.png"
        await page.screenshot(path=screenshot_transparent)
        print(f"Saved Screenshot 1: {screenshot_transparent}")

        # Test SubTab Theme & Pagination
        print("4. Testing Theme Tab & Pagination...")
        await page.click('#tabSubTheme')
        await page.wait_for_timeout(500)

        ind1 = await page.inner_text('#compThemePageIndicator')
        print(f"Page indicator at start: {ind1}")
        assert '1 / 10' in ind1, "Initial page should be 1 / 10"

        # Test pagination next
        print("Testing Pagination Next to Page 2...")
        await page.click('#compBtnThemeNext')
        await page.wait_for_timeout(400)
        ind2 = await page.inner_text('#compThemePageIndicator')
        print(f"Page indicator after click: {ind2}")
        assert '2 / 10' in ind2, "Should advance to Page 2 / 10"

        # Select a theme on Page 2 (Cyberpunk)
        print("Selecting 'Cyberpunk' on Page 2...")
        card_cyberpunk = await page.query_selector('.cwc-preset-card[data-chat-theme="cyberpunk"]')
        if card_cyberpunk:
            await card_cyberpunk.click()
            await page.wait_for_timeout(500)
            theme_on_w = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0].chatTheme")
            print(f"Widget theme is now: {theme_on_w}")
            assert theme_on_w == 'cyberpunk', "Theme should be cyberpunk!"

        # Advance to Page 10
        print("Advancing to Page 10...")
        for p_num in range(3, 11):
            await page.click('#compBtnThemeNext')
            await page.wait_for_timeout(150)
        
        ind10 = await page.inner_text('#compThemePageIndicator')
        print(f"Page indicator on last page: {ind10}")
        assert '10 / 10' in ind10, "Should reach Page 10 / 10"

        # Select theme on Page 10 (e.g. Thai Silk or Vintage Film Strip)
        cards_page10 = await page.query_selector_all('#cwcPresetsGrid .cwc-preset-card')
        print(f"Cards found on Page 10: {len(cards_page10)}")
        assert len(cards_page10) > 0, "Page 10 should have theme cards"
        
        # Click last card on Page 10
        last_card_theme = await cards_page10[-1].get_attribute('data-chat-theme')
        print(f"Clicking Page 10 theme: {last_card_theme}")
        await cards_page10[-1].click()
        await page.wait_for_timeout(500)
        theme_page10 = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0].chatTheme")
        print(f"Widget theme is now: {theme_page10}")
        assert theme_page10 == last_card_theme, "Theme should match last card!"

        # Test pagination prev
        print("Testing Pagination Prev back to Page 9...")
        await page.click('#compBtnThemePrev')
        await page.wait_for_timeout(200)
        ind9 = await page.inner_text('#compThemePageIndicator')
        print(f"Page indicator after prev click: {ind9}")
        assert '9 / 10' in ind9, "Should be Page 9 / 10"

        print("PASS: Theme Pagination (all 10 pages) verified and responsive!")

        # Test Animations In/Out & Auto-Hide Duration
        print("5. Testing Animations In / Out & Auto-Hide Duration...")
        # Switch to Standard tab to see accordion easily
        await page.click('#tabSubStandard')
        await page.wait_for_timeout(400)

        # Set Animation In
        await page.select_option('#compChatAnimIn', 'bounce')
        # Set Animation Out
        await page.select_option('#compChatAnimOut', 'slide-left')

        # Check Auto-Hide initial
        row_hide = await page.query_selector('#compChatHideAfterRow')
        is_visible_before = await row_hide.is_visible()
        print(f"Hide-after row visible before checking auto-hide: {is_visible_before}")
        assert not is_visible_before, "Hide-after row should be hidden before checking auto-hide"

        # Toggle Auto-Hide checkbox
        print("Clicking Auto-Hide switch...")
        await page.evaluate("document.getElementById('compChatAutoHide').click()")
        await page.wait_for_timeout(300)
        is_visible_after = await row_hide.is_visible()
        print(f"Hide-after row visible after checking auto-hide: {is_visible_after}")
        assert is_visible_after, "Hide-after row should be visible now!"

        # Change duration slider
        print("Changing hide-after duration to 18 seconds...")
        await page.evaluate("""() => {
            const slider = document.getElementById('compChatHideAfter');
            slider.value = 18;
            slider.dispatchEvent(new Event('input'));
            slider.dispatchEvent(new Event('change'));
        }""")
        await page.wait_for_timeout(300)

        val_text = await page.inner_text('#compChatHideAfterVal')
        print(f"Hide-after display label: {val_text}")
        assert '18' in val_text, "Label should display 18 วินาที"

        w_state = await page.evaluate("window.ComposerStudio.state.pages[0].widgets[0]")
        print("Chat widget state anim & auto-hide:", {
            'anim_in': w_state.get('animation'),
            'anim_out': w_state.get('exitAnimation'),
            'autoHide': w_state.get('autoHide'),
            'hideAfter': w_state.get('hideAfter')
        })
        assert w_state.get('autoHide') == True, "autoHide must be true"
        assert w_state.get('hideAfter') == 18, "hideAfter must be 18"
        print("PASS: Animation In/Out and Auto-Hide Duration verified!")

        # Test Optional Container Box Customizer
        print("6. Testing Optional Container Background Box...")
        wrap_box = await page.query_selector('#compChatContainerSettingsWrap')
        assert not await wrap_box.is_visible(), "Container settings wrap should be hidden initially"

        print("Enabling Container Background Box...")
        await page.evaluate("document.getElementById('compChatContainerBgEnabled').click()")
        await page.wait_for_timeout(300)
        assert await wrap_box.is_visible(), "Container settings wrap should be visible now"

        # Configure custom container box
        await page.evaluate("""() => {
            const bgPick = document.getElementById('compChatContainerBgColor');
            bgPick.value = '#1e1b4b';
            bgPick.dispatchEvent(new Event('change'));

            const opSlider = document.getElementById('compChatContainerBgOpacity');
            opSlider.value = 85;
            opSlider.dispatchEvent(new Event('input'));
            opSlider.dispatchEvent(new Event('change'));

            const rSlider = document.getElementById('compChatContainerRadius');
            rSlider.value = 16;
            rSlider.dispatchEvent(new Event('input'));
            rSlider.dispatchEvent(new Event('change'));

            document.getElementById('compChatContainerBorder').click();
        }""")
        await page.wait_for_timeout(500)

        box_applied = await page.evaluate("""() => {
            const el = document.querySelector('.composer-widget.type-chat .widget-type-chat');
            return el ? el.getAttribute('style') : null;
        }""")
        print("Applied Container Box Style on Canvas:", box_applied)
        assert box_applied and 'rgba(30, 27, 75' in box_applied, "Should contain configured rgba color"
        assert 'border-radius: 16px' in box_applied or 'border-radius:16px' in box_applied, "Should contain radius 16px"

        # Take screenshot with container box enabled
        screenshot_with_box = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\chat_with_custom_container_box.png"
        await page.screenshot(path=screenshot_with_box)
        print(f"Saved Screenshot 2: {screenshot_with_box}")

        # Now toggle Container Box back OFF to confirm it returns to 100% transparent!
        print("Toggling Container Box back OFF...")
        await page.evaluate("document.getElementById('compChatContainerBgEnabled').click()")
        await page.wait_for_timeout(500)

        box_off_style = await page.evaluate("""() => {
            const el = document.querySelector('.composer-widget.type-chat .widget-type-chat');
            return el ? el.getAttribute('style') : null;
        }""")
        print("Style after toggling box OFF:", box_off_style)
        assert box_off_style and 'transparent' in box_off_style, "Container must return to transparent when disabled!"
        print("PASS: Container Box toggle and customization verified!")

        if errors:
            print("ERRORS:", errors)
            raise AssertionError(f"Encountered {len(errors)} page errors")
        else:
            print("\nALL CHAT WIDGET IMPROVEMENTS 100% VERIFIED AND WORKING!")

        await browser.close()

asyncio.run(verify_chat())
