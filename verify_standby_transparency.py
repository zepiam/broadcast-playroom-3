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

def test_standby_transparency():
    print("=== TEST: Verifying 100% Standby Transparency on Overlay ===")

    # Layout with all standby widgets included
    test_layout = {
        "pages": [
            {
                "id": "page-1",
                "name": "ฉากหลักสตรีม",
                "widgets": [
                    {
                        "id": "w-chat-1",
                        "type": "chat",
                        "title": "แชทสด",
                        "x": 40,
                        "y": 500,
                        "width": 460,
                        "height": 540,
                        "z": 10,
                        "chatTheme": "glass-dark",
                        "chatMode": "default"
                    },
                    {
                        "id": "w-clock-1",
                        "type": "clock",
                        "title": "นาฬิกาดิจิทัล",
                        "x": 1640,
                        "y": 40,
                        "width": 240,
                        "height": 70,
                        "z": 11,
                        "clockTheme": "neon-glow"
                    },
                    {
                        "id": "w-rand-1",
                        "type": "randomizer",
                        "title": "สุ่มด่วน",
                        "x": 0,
                        "y": 0,
                        "width": 1920,
                        "height": 1080,
                        "z": 50,
                        "isFullScreen": True
                    },
                    {
                        "id": "w-ask-1",
                        "type": "ask",
                        "title": "โพลสำรวจความคิดเห็น",
                        "x": 0,
                        "y": 0,
                        "width": 1920,
                        "height": 1080,
                        "z": 51,
                        "isFullScreen": True
                    },
                    {
                        "id": "w-gw-1",
                        "type": "giveaway",
                        "title": "สุ่มแจกรางวัล",
                        "x": 0,
                        "y": 0,
                        "width": 1920,
                        "height": 1080,
                        "z": 52,
                        "isFullScreen": True
                    },
                    {
                        "id": "w-playroom-1",
                        "type": "playroom",
                        "title": "Playroom",
                        "x": 0,
                        "y": 0,
                        "width": 1920,
                        "height": 1080,
                        "z": 53,
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
        page = context.new_page()

        print(f"Loading OBS Live Overlay: http://127.0.0.1:{port}/composer.html")
        page.goto(f"http://127.0.0.1:{port}/composer.html?p=1")
        page.wait_for_selector(".composer-widget", timeout=5000)

        # 1. Verify Standby state on all 4 standby widgets
        print("\nChecking standby visibility:")
        
        # Randomizer card check
        rand_card = page.query_selector("#compRandomizerCard_w-rand-1")
        assert rand_card is not None
        assert not rand_card.is_visible(), "Randomizer card MUST BE HIDDEN on standby!"
        print("  [PASS] Randomizer card is completely hidden (display: none) on standby!")

        # Ask panel check
        ask_panel = page.query_selector("#compAskPanel_w-ask-1")
        assert ask_panel is not None
        assert not ask_panel.is_visible(), "ASK panel MUST BE HIDDEN on standby!"
        print("  [PASS] ASK panel is completely hidden on standby!")

        # Giveaway panel check
        gw_panel = page.query_selector("#compGwPanel_w-gw-1")
        assert gw_panel is not None
        assert not gw_panel.is_visible(), "Giveaway panel MUST BE HIDDEN on standby!"
        print("  [PASS] Giveaway panel is completely hidden on standby!")

        # Playroom stage & idle check
        pr_stage = page.query_selector("#compPlayroomStage_w-playroom-1")
        pr_idle = page.query_selector("#compPlayroomIdle_w-playroom-1")
        assert pr_stage is not None and not pr_stage.is_visible(), "Playroom stage MUST BE HIDDEN on standby!"
        assert pr_idle is not None and not pr_idle.is_visible(), "Playroom idle banner MUST BE HIDDEN on standby!"
        print("  [PASS] Playroom stage and idle banner are completely hidden on standby!")

        # 2. Take screenshot of the clean transparent standby overlay
        standby_screenshot = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\verified_standby_transparent_overlay.png"
        page.screenshot(path=standby_screenshot)
        print(f"\n[ARTIFACT] Saved clean standby screenshot: {standby_screenshot}")

        # 3. Simulate active spin event
        print("\nSimulating RANDOMIZER_SPIN event...")
        page.evaluate("""() => {
            const bus = new BroadcastChannel('bp3_system_channel');
            bus.postMessage({
                event: 'RANDOMIZER_SPIN',
                payload: {
                    items: ['ไอดีเกม A', 'หูฟังเกมมิ่ง B', 'คีย์บอร์ด C'],
                    winner: 'หูฟังเกมมิ่ง B',
                    duration: 3
                }
            });
        }""")

        # Verify it pops in during spin
        page.wait_for_selector("#compRandomizerCard_w-rand-1", state="visible", timeout=3000)
        print("  [PASS] Randomizer card successfully popped in on spin event!")
        
        # Take active spin screenshot
        spin_screenshot = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\verified_active_spin_overlay.png"
        page.screenshot(path=spin_screenshot)
        print(f"[ARTIFACT] Saved active spin screenshot: {spin_screenshot}")

        # Wait for duration to finish and verify it automatically hides back
        print("Waiting for spin duration to end (3.5s)...")
        time.sleep(4.5)
        assert not rand_card.is_visible(), "Randomizer card MUST AUTO-HIDE after spin duration!"
        print("  [PASS] Randomizer card automatically disappeared back to 100% transparent standby!")

        browser.close()

    server.shutdown()
    print("\n========================================================")
    print("🎉 ALL STANDBY TRANSPARENCY TESTS PASSED 100%! 🎉")
    print("========================================================")

if __name__ == '__main__':
    test_standby_transparency()
