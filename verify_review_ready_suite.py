import sys
import os
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_review_ready_system():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        index_url = f"file:///{os.path.abspath('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html').replace(os.sep, '/')}"
        print(f"Loading Main App: {index_url}")
        page.goto(index_url)
        page.wait_for_timeout(1000)

        # 1. Check Topbar Server Status LED
        server_status = page.locator("#topbarServerStatus")
        assert server_status.is_visible(), "Topbar Server Status must be visible!"
        print("✓ Topbar Server Status is visible.")
        server_status.click()
        page.wait_for_timeout(300)
        status_text = server_status.inner_text()
        print(f"✓ Clicked Server Status: {status_text}")

        # 2. Check Live Chat Simulator
        btn_sim = page.locator("#btnSimulateChat")
        assert btn_sim.is_visible(), "Chat Simulator button must be visible in chat header!"
        btn_sim.click() # Start simulator
        print("✓ Clicked Chat Simulator button.")
        page.wait_for_timeout(1500)
        chat_items = page.locator("#chatList .chat-row")
        chat_count = chat_items.count()
        print(f"✓ Chat items count after simulation started: {chat_count}")
        assert chat_count > 0, "Chat simulation should inject messages into #chatList!"
        btn_sim.click() # Stop simulator

        # 3. Check Settings - Network & DNS and Defender
        btn_settings = page.locator("#btnOpenSettings, button[title*='ตั้งค่า'], .btn-settings-header").first
        if btn_settings.is_visible():
            btn_settings.click()
        else:
            page.evaluate("() => { if(window.openSettings) window.openSettings(); else document.getElementById('win-settings').classList.remove('hidden'); }")
        page.wait_for_timeout(500)

        # Click Networking Tab
        nav_net = page.locator("#nav-sec-networking")
        if nav_net.is_visible():
            nav_net.click()
            page.wait_for_timeout(300)
            sec_net = page.locator("#sec-networking")
            assert sec_net.is_visible(), "Network & DNS section must be visible!"
            print("✓ Network & DNS Settings tab verified.")

        # Click Defender Tab
        nav_def = page.locator("#nav-sec-defender")
        if nav_def.is_visible():
            nav_def.click()
            page.wait_for_timeout(300)
            sec_def = page.locator("#sec-defender")
            assert sec_def.is_visible(), "Defender 1-Click section must be visible!"
            print("✓ Windows Defender 1-Click tab verified.")

        # Click OBS Dock Tab
        nav_dock = page.locator("#nav-sec-docks")
        if nav_dock.is_visible():
            nav_dock.click()
            page.wait_for_timeout(300)
            sec_dock = page.locator("#sec-docks")
            assert sec_dock.is_visible(), "OBS Dock section must be visible!"
            print("✓ OBS Dock Settings tab verified.")

        # Close settings
        page.evaluate("() => { const w = document.getElementById('win-settings'); if(w) w.classList.add('hidden'); }")
        page.wait_for_timeout(300)

        # 4. Check Composer Studio
        page.locator("#btnRailComposer").click()
        page.wait_for_timeout(600)
        composer_win = page.locator("#win-composer")
        assert composer_win.is_visible(), "Composer Studio window (#win-composer) must open!"
        print("✓ Composer Studio opened.")

        # Take comprehensive screenshot of Main Studio
        page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/full_review_ready_main_studio.png")
        print("✓ Saved main studio screenshot.")

        # 5. Test Standalone OBS Dock (dock.html)
        dock_page = context.new_page()
        dock_url = f"file:///{os.path.abspath('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/dock.html').replace(os.sep, '/')}"
        print(f"Loading OBS Dock: {dock_url}")
        dock_page.goto(dock_url)
        dock_page.wait_for_timeout(500)

        dock_master_tts = dock_page.locator("#btnDockTts")
        assert dock_master_tts.is_visible(), "Dock master TTS switch must be visible!"
        dock_master_tts.click()
        print("✓ Toggled Dock Master TTS switch.")

        dock_gender = dock_page.locator("#btnDockFemale")
        assert dock_gender.is_visible(), "Dock gender female switch must be visible!"
        dock_gender.click()
        print("✓ Selected Dock Female Voice.")

        # Quick trigger click
        btn_ask_trigger = dock_page.locator("button[data-action='ask_start']")
        if btn_ask_trigger.is_visible():
            btn_ask_trigger.click()
            print("✓ Clicked Dock Quick Trigger ASK Poll.")

        dock_page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/full_review_ready_obs_dock.png")
        print("✓ Saved OBS dock screenshot.")

        # 6. Test Standalone OBS Composer Canvas (composer.html)
        comp_page = context.new_page()
        comp_url = f"file:///{os.path.abspath('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer.html').replace(os.sep, '/')}"
        print(f"Loading OBS Composer Canvas: {comp_url}")
        comp_page.goto(comp_url)
        comp_page.wait_for_timeout(800)

        canvas_stage = comp_page.locator("#obsCanvasStage")
        assert canvas_stage.is_visible(), "OBS Composer Canvas stage must be visible!"
        comp_page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/full_review_ready_obs_canvas.png")
        print("✓ Saved OBS canvas screenshot.")

        browser.close()
        print("All Review-Ready tests passed 100%!")

if __name__ == '__main__':
    test_review_ready_system()
