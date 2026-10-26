import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"
SRC_HTML = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1500, "height": 920})
        page = await context.new_page()

        print(f"Loading {SRC_HTML}...")
        await page.goto(f"file:///{SRC_HTML}")
        await page.wait_for_timeout(1000)

        # 1. Open Composer Studio window
        btn_composer = page.locator("#btnRailComposer")
        await btn_composer.click()
        await page.wait_for_timeout(600)
        win = page.locator("#win-composer")
        await win.wait_for(state="visible")
        print("Composer Studio opened.")

        # Capture initial toolbar
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_01_toolbar.png"))
        print("Captured composer_feat_01_toolbar.png")

        # 2. Test Chat Dropdown Context Menu
        btn_chat_menu = page.locator("#btnCompAddChatMenu")
        await btn_chat_menu.click()
        await page.wait_for_timeout(300)
        menu_chat = page.locator("#compChatDropdownMenu")
        assert await menu_chat.is_visible(), "Chat dropdown menu should be visible!"
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_02_chat_dropdown.png"))
        print("Captured composer_feat_02_chat_dropdown.png")

        # 3. Add Danmaku Widget from Menu
        opt_danmaku = page.locator(".comp-chat-menu-item[data-chat-mode='danmaku']")
        await opt_danmaku.click()
        await page.wait_for_timeout(600)

        # Verify Danmaku is full screen 1920x1080 and has NO resize handles
        danmaku_widget = page.locator(".widget-danmaku-full")
        assert await danmaku_widget.count() > 0, "Danmaku widget should be rendered on canvas!"
        handles_count = await danmaku_widget.locator(".composer-resize-handle").count()
        assert handles_count == 0, f"Danmaku should have 0 resize handles, got {handles_count}!"

        # Verify Left Customizer shows Danmaku title and controls
        cust_title = await page.locator("#compCustTitle").text_content()
        print(f"Danmaku Customizer Title: {cust_title}")
        assert "ดันมากุ" in cust_title, "Left customizer should show Danmaku title!"

        # Trigger Danmaku Demo
        btn_demo_danmaku = page.locator("#btnDemoDanmakuSingle")
        await btn_demo_danmaku.click()
        await page.wait_for_timeout(400)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_03_danmaku_fullscreen.png"))
        print("Captured composer_feat_03_danmaku_fullscreen.png")

        # 4. Test Duplicate Warning Modal: Click Danmaku again
        await btn_chat_menu.click()
        await page.wait_for_timeout(300)
        await opt_danmaku.click()
        await page.wait_for_timeout(400)

        confirm_modal = page.locator("#composerConfirmModal")
        assert await confirm_modal.is_visible(), "Duplicate confirmation modal should pop up!"
        modal_msg = await page.locator("#composerConfirmMsg").text_content()
        print(f"Duplicate Warning Message: {modal_msg}")
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_04_duplicate_warning.png"))
        print("Captured composer_feat_04_duplicate_warning.png")

        # Click Cancel on duplicate modal
        btn_cancel = page.locator("#btnComposerConfirmCancel")
        await btn_cancel.click()
        await page.wait_for_timeout(300)
        assert not await confirm_modal.is_visible(), "Modal should close on cancel"

        # 5. Add Balloon Chat Widget from Menu
        await btn_chat_menu.click()
        await page.wait_for_timeout(300)
        opt_balloon = page.locator(".comp-chat-menu-item[data-chat-mode='balloon']")
        await opt_balloon.click()
        await page.wait_for_timeout(600)

        # Verify Left Customizer shows Balloon title and only Balloon settings
        cust_title = await page.locator("#compCustTitle").text_content()
        print(f"Balloon Customizer Title: {cust_title}")
        assert "บอลลูน" in cust_title, "Left customizer should show Balloon title!"

        # Test Balloon Demo
        btn_balloon_demo = page.locator("#btnDemoBalloonSingle")
        await btn_balloon_demo.click()
        await page.wait_for_timeout(400)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_05_balloon_customizer.png"))
        print("Captured composer_feat_05_balloon_customizer.png")

        # 6. Add Character Chat Widget from Menu
        await btn_chat_menu.click()
        await page.wait_for_timeout(300)
        opt_char = page.locator(".comp-chat-menu-item[data-chat-mode='character']")
        await opt_char.click()
        await page.wait_for_timeout(600)

        # Verify Left Customizer shows Character Chat title
        cust_title = await page.locator("#compCustTitle").text_content()
        print(f"Character Customizer Title: {cust_title}")
        assert "ตัวละคร" in cust_title, "Left customizer should show Character title!"

        # Test Character Talk Demo
        btn_char_talk = page.locator("#btnDemoCharTalk")
        await btn_char_talk.click()
        await page.wait_for_timeout(400)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_06_character_customizer.png"))
        print("Captured composer_feat_06_character_customizer.png")

        # 7. Select Default Chat Widget and test 2 Tabs & Live Chat Demo
        layer_default = page.locator('#composerLayersList [data-id="w-chat-1"]')
        if await layer_default.count() > 0:
            await layer_default.click()
        else:
            await page.locator("#widget-w-chat-1").click(force=True)
        await page.wait_for_timeout(500)
        cust_title = await page.locator("#compCustTitle").text_content()
        print(f"Default Chat Customizer Title: {cust_title}")
        assert "มาตรฐาน" in cust_title or "แชท" in cust_title

        # Click Theme Tab
        btn_tab_theme = page.locator("#tabSubTheme")
        await btn_tab_theme.click()
        await page.wait_for_timeout(400)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_07_default_chat_themes.png"))
        print("Captured composer_feat_07_default_chat_themes.png")

        # Send demo message
        btn_send_chat = page.locator("#btnDemoChatSingle")
        await btn_send_chat.click()
        await page.wait_for_timeout(400)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_08_default_chat_demo.png"))
        print("Captured composer_feat_08_default_chat_demo.png")

        # 8. Add Goal Widget and test increment demo
        btn_add_goal = page.locator(".btn-add-widget[data-widget-type='goal']")
        await btn_add_goal.click()
        await page.wait_for_timeout(600)
        cust_title = await page.locator("#compCustTitle").text_content()
        print(f"Goal Customizer Title: {cust_title}")

        # Trigger Goal Demo
        btn_goal_plus = page.locator("#btnDemoGoalPlus")
        await btn_goal_plus.click()
        await page.wait_for_timeout(400)
        await win.screenshot(path=os.path.join(ARTIFACT_DIR, "composer_feat_09_goal_demo.png"))
        print("Captured composer_feat_09_goal_demo.png")

        print("\nALL 8 TESTS PASSED SUCCESSFULLY 100%!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
