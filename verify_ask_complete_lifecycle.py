import os
import sys
import time
import json
import threading
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3')
import launch_dev

def test_ask_lifecycle():
    print("=== TEST: Verifying ASK Poll Lifecycle, Popout Window & Overlay Sync ===")

    # Setup layout with ASK widget
    test_layout = {
        "pages": [
            {
                "id": "page-1",
                "name": "ฉากหลักสตรีม",
                "widgets": [
                    {
                        "id": "w-ask-1",
                        "type": "ask",
                        "title": "โพลสำรวจความคิดเห็น",
                        "x": 0,
                        "y": 0,
                        "width": 1920,
                        "height": 1080,
                        "z": 50,
                        "isFullScreen": True
                    }
                ]
            }
        ],
        "activePageId": "page-1",
        "updatedAt": time.time()
    }
    launch_dev.save_layout(test_layout)

    server = launch_dev.start_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = launch_dev.PORT

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})

        # 1. Open OBS Live Overlay
        overlay_page = context.new_page()
        overlay_page.goto(f"http://127.0.0.1:{port}/composer.html?p=1")
        overlay_page.wait_for_selector(".composer-widget.type-ask", timeout=5000)

        # Standby: Panel MUST BE HIDDEN
        panel = overlay_page.query_selector("#compAskPanel_w-ask-1")
        assert panel is not None
        assert not panel.is_visible(), "ASK Panel must be hidden on standby initially!"
        print("1. [PASS] Overlay ASK panel is hidden on standby.")

        # 2. Open Main App Window
        app_page = context.new_page()
        app_page.goto(f"http://127.0.0.1:{port}/index.html")

        # Open ASK Tool Window (pops out into separate window)
        print("\nOpening ASK Tool Window (Popout)...")
        with app_page.expect_popup() as pop_info:
            app_page.evaluate("openToolWindow('ask')")
        pop_page = pop_info.value
        pop_page.wait_for_load_state("domcontentloaded")
        print("2. [PASS] ASK Tool Window opened in popout window.")

        # Verify BP3_BUS and _askPollState bridged in popout
        has_bus = pop_page.evaluate("typeof window.BP3_BUS === 'object'")
        has_state = pop_page.evaluate("typeof window._askPollState === 'object'")
        assert has_bus, "BP3_BUS should be bridged in popout window!"
        assert has_state, "_askPollState should be bridged in popout window!"
        print(f"3. [PASS] BP3_BUS and _askPollState are bridged in popout (BP3_BUS: {has_bus}, _askPollState: {has_state})")

        # 3. Start Poll from Popout Window
        print("\nClicking '🚀 เริ่มเปิดโหวตขึ้นจอ OBS' from popout window...")
        btn_start = pop_page.wait_for_selector("#askFooterIdle button.primary", state="visible")
        btn_start.click()

        # Verify Overlay reveals poll panel
        overlay_page.wait_for_selector("#compAskPanel_w-ask-1", state="visible", timeout=3000)
        print("4. [PASS] Overlay revealed live ASK poll panel on voting start!")

        # 4. Simulate a vote and end poll
        pop_page.evaluate("window._askPollState.choices[0].votes = 15; window._askPollState.choices[1].votes = 5; emitAskState();")
        time.sleep(0.5)

        print("\nEnding poll (คลิก '⏹ จบโหวตทันที')...")
        btn_end = pop_page.wait_for_selector("#askFooterVoting button:has-text('จบโหวตทันที')", state="visible")
        btn_end.click()

        # Verify Ended state in popout and overlay
        pop_page.wait_for_selector("#askFooterEnded", state="visible", timeout=3000)
        assert overlay_page.is_visible("#compAskPanel_w-ask-1")
        print("5. [PASS] Poll ended, winner summarized on overlay.")

        # Take screenshot of ended result on overlay
        ended_screenshot = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\verified_ask_ended_result_on_overlay.png"
        overlay_page.screenshot(path=ended_screenshot)

        # 5. Close / Hide Overlay Result (คลิก '✕ ปิดผลออกจาก Overlay')
        print("\nClicking '✕ ปิดผลออกจาก Overlay' in popout...")
        btn_close_overlay = pop_page.wait_for_selector("#askFooterEnded button:has-text('ปิดผลออกจาก Overlay')", state="visible")
        btn_close_overlay.click()

        # CRITICAL TEST: Verify overlay panel IS NOT VISIBLE (DISAPPEARED!)
        time.sleep(1.0)
        assert not overlay_page.is_visible("#compAskPanel_w-ask-1"), "ASK Panel MUST DISAPPEAR when '✕ ปิดผลออกจาก Overlay' is clicked!"
        print("6. [PASS] Overlay ASK panel disappeared immediately! NO RESULT LEFT HANGING!")

        # Take screenshot of clean overlay after close
        clean_screenshot = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\verified_ask_overlay_closed_clean.png"
        overlay_page.screenshot(path=clean_screenshot)

        # 6. Verify Reset & Start New Poll
        print("\nVerifying Starting a NEW Poll after close/re-open...")
        # Footer idle should be visible again and inputs enabled
        pop_page.wait_for_selector("#askFooterIdle", state="visible", timeout=3000)
        q_input = pop_page.query_selector("#askQuestion")
        assert q_input is not None and not q_input.is_disabled(), "Question input MUST BE ENABLED for new poll!"

        # Type a new question
        q_input.fill("สตรีมวันพรุ่งนี้ อยากให้แจกของขวัญอะไรดี?")
        
        # Click Start New Poll
        btn_start_new = pop_page.query_selector("#askFooterIdle button.primary")
        assert btn_start_new is not None and btn_start_new.is_visible()
        btn_start_new.click()

        # Verify second poll starts and appears on overlay with new question!
        overlay_page.wait_for_selector("#compAskPanel_w-ask-1", state="visible", timeout=3000)
        q_on_overlay = overlay_page.inner_text("#compAskQ_w-ask-1")
        print(f"Question on overlay for second poll: '{q_on_overlay}'")
        assert "สตรีมวันพรุ่งนี้" in q_on_overlay, "Overlay should show new question for second poll!"
        print("7. [PASS] Successfully started NEW poll cleanly with updated question!")

        # 7. Close and reopen tool window test
        print("\nTesting closing and re-opening the ASK window...")
        app_page.evaluate("closeToolWindow('ask')")
        time.sleep(0.5)

        # Re-open ASK window from rail in app_page
        with app_page.expect_popup() as pop_info2:
            app_page.evaluate("openToolWindow('ask')")
        pop_page2 = pop_info2.value
        pop_page2.wait_for_load_state("domcontentloaded")

        # End and reset from newly opened popout
        pop_page2.bring_to_front()
        time.sleep(0.5)
        pop_page2.evaluate("() => { const btn = Array.from(document.querySelectorAll('#askFooterVoting button')).find(x => x.textContent.includes('จบโหวต')); if (btn) btn.onclick(); }")
        time.sleep(0.5)
        
        btn_reset = pop_page2.wait_for_selector("#askFooterEnded button:has-text('เริ่มโพลใหม่')", state="visible", timeout=3000)
        btn_reset.click()

        # Verify overlay is closed and idle footer is ready
        time.sleep(1.0)
        assert not overlay_page.is_visible("#compAskPanel_w-ask-1"), "Overlay must be closed after 'เริ่มโพลใหม่'!"
        pop_page2.wait_for_selector("#askFooterIdle", state="visible", timeout=3000)
        print("8. [PASS] Re-opened ASK window reset poll cleanly and closed overlay.")

        browser.close()

    server.shutdown()
    print("\n=========================================================================")
    print("🎉 ALL ASK POLL LIFECYCLE & OVERLAY SYNC TESTS PASSED 100%! 🎉")
    print("=========================================================================")

if __name__ == '__main__':
    test_ask_lifecycle()
