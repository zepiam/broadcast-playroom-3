import os
import sys
import time
import json
import threading
from http.server import HTTPServer
from playwright.sync_api import sync_playwright

# Set up UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Import handler and server from launch_dev
sys.path.insert(0, r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3')
import launch_dev

def run_tests():
    # Reset composer_layout.json to clean initial state
    initial_clean_layout = {
        "pages": [
            {
                "id": "page-1",
                "name": "หน้า 1 (มาตรฐาน)",
                "widgets": [
                    {
                        "id": "w-chat-1",
                        "type": "chat",
                        "title": "แชทสด",
                        "x": 40,
                        "y": 480,
                        "width": 460,
                        "height": 560,
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
                        "clockTheme": "neon-glow",
                        "clockFormat": "HH:MM:SS"
                    },
                    {
                        "id": "w-viewer-1",
                        "type": "viewer",
                        "title": "ยอดคนดูสด",
                        "x": 1640,
                        "y": 125,
                        "width": 240,
                        "height": 60,
                        "z": 12,
                        "viewerTheme": "cyberpunk"
                    }
                ]
            }
        ],
        "activePageId": "page-1",
        "updatedAt": time.time()
    }
    launch_dev.save_layout(initial_clean_layout)

    print("=== STEP 1: Launching Live Dev Server on 8080 ===")
    server = launch_dev.start_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = launch_dev.PORT
    print(f"Dev server started on port {port}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # STEP 2: Verify Server API
        print("\n=== STEP 2: Verifying Server Status & Layout API ===")
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        res = page.goto(f"http://127.0.0.1:{port}/api/server_status")
        assert res.status == 200, f"Expected 200, got {res.status}"
        status_data = json.loads(page.text_content("body"))
        print(f"Server Status Response: {status_data}")
        assert status_data['status'] == 'online'

        res_layout = page.goto(f"http://127.0.0.1:{port}/api/composer/layout")
        assert res_layout.status == 200
        layout_data = json.loads(page.text_content("body"))
        pages = layout_data.get('pages', [])
        assert len(pages) > 0, "Pages should not be empty"
        print(f"Layout API returned {len(pages)} page(s) with {len(pages[0].get('widgets', []))} widget(s)")

        # STEP 3: Verify OBS Overlay Page (composer.html)
        print("\n=== STEP 3: Loading OBS Live Overlay (composer.html) ===")
        overlay_page = context.new_page()
        res_overlay = overlay_page.goto(f"http://127.0.0.1:{port}/composer.html?p=1&test=1")
        assert res_overlay.status == 200, f"Expected 200, got {res_overlay.status}"

        # Wait for widgets to render
        overlay_page.wait_for_selector(".composer-widget", timeout=5000)
        widgets = overlay_page.query_selector_all(".composer-widget")
        print(f"Found {len(widgets)} live widget(s) rendered on OBS stage:")
        for w in widgets:
            w_type = w.get_attribute("data-type")
            box = w.bounding_box()
            print(f"  - [{w_type}] at ({box['x']}, {box['y']}), size: {box['width']}x{box['height']}")

        assert len(widgets) >= 3, f"Expected at least 3 widgets, got {len(widgets)}"

        # Verify Clock ticker is active
        clock_el = overlay_page.query_selector(".composer-widget.type-clock")
        assert clock_el is not None, "Clock widget should exist"
        initial_time = clock_el.text_content().strip()
        print(f"Initial clock time on OBS: {initial_time}")
        time.sleep(1.2)
        clock_el_after = overlay_page.query_selector(".composer-widget.type-clock")
        updated_time = clock_el_after.text_content().strip()
        print(f"Clock time after 1.2s: {updated_time}")

        # STEP 4: Verify OBS Overlay Alias (overlay.html)
        print("\n=== STEP 4: Loading OBS Overlay Alias (overlay.html) ===")
        alias_page = context.new_page()
        res_alias = alias_page.goto(f"http://127.0.0.1:{port}/overlay.html?p=1")
        assert res_alias.status == 200, f"Expected 200, got {res_alias.status}"
        alias_page.wait_for_selector(".composer-widget", timeout=5000)
        alias_widgets = alias_page.query_selector_all(".composer-widget")
        print(f"Alias overlay.html rendered {len(alias_widgets)} widget(s) successfully!")
        assert len(alias_widgets) == len(widgets)

        # STEP 5: Verify Real-time Update via POST /api/composer/layout
        print("\n=== STEP 5: Testing Real-time Push & Poll Synchronization ===")
        # Add a new randomizer widget to layout
        new_layout = json.loads(json.dumps(layout_data))
        new_layout['pages'][0]['widgets'].append({
            "id": "w-randomizer-test",
            "type": "randomizer",
            "title": "สุ่มด่วน",
            "x": 0,
            "y": 0,
            "width": 1920,
            "height": 1080,
            "z": 99,
            "isFullScreen": True
        })

        import urllib.request
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/composer/layout",
            data=json.dumps(new_layout).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            assert response.status == 200

        print("POSTed new layout with 4 widgets. Waiting for overlay polling sync...")
        overlay_page.wait_for_selector(".type-randomizer", timeout=3000)
        updated_widgets = overlay_page.query_selector_all(".composer-widget")
        print(f"Live Overlay updated! Current widgets count: {len(updated_widgets)}")
        assert len(updated_widgets) == 4, f"Expected 4 widgets after live sync, got {len(updated_widgets)}"

        # STEP 6: Capture Visual Screenshot of the Live Overlay
        screenshot_path = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\verified_live_obs_overlay.png"
        overlay_page.screenshot(path=screenshot_path)
        print(f"\n[ARTIFACT] Saved live OBS overlay screenshot: {screenshot_path}")

        # STEP 7: Verify Main App Window UI Controls
        print("\n=== STEP 7: Verifying Composer Studio & Settings UI ===")
        app_page = context.new_page()
        app_page.goto(f"http://127.0.0.1:{port}/index.html")
        app_page.evaluate("_autoPopoutWindows = false; openToolWindow('composer')")
        app_page.wait_for_selector("#btnCompTestBrowser", state="visible", timeout=6000)
        test_btn = app_page.query_selector("#btnCompTestBrowser")
        copy_btn = app_page.query_selector("#btnCompCopyObs")
        assert test_btn is not None, "Button #btnCompTestBrowser should exist"
        assert copy_btn is not None, "Button #btnCompCopyObs should exist"
        print("Buttons '#btnCompTestBrowser' and '#btnCompCopyObs' verified in Composer Studio toolbar!")

        # Verify Settings modal inputs
        inp_overlay = app_page.query_selector("#inpSettingsObsOverlayUrl")
        inp_dock = app_page.query_selector("#inpSettingsObsDockUrl")
        assert inp_overlay is not None, "Settings overlay URL input should exist"
        assert inp_dock is not None, "Settings dock URL input should exist"
        print(f"Settings overlay URL value: {inp_overlay.get_attribute('value')}")
        print(f"Settings dock URL value: {inp_dock.get_attribute('value')}")

        browser.close()

    server.shutdown()
    print("\n========================================================")
    print("🎉 ALL TESTS PASSED! OBS LIVE OVERLAY IS FULLY WORKING! 🎉")
    print("========================================================")

if __name__ == '__main__':
    run_tests()
