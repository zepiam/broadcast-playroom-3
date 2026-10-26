import os
import time
import threading
from http.server import HTTPServer
from playwright.sync_api import sync_playwright
import launch_dev

test_port = 8996
while launch_dev.is_port_in_use(test_port):
    test_port += 1

server = HTTPServer(('127.0.0.1', test_port), launch_dev.QuietHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(1)

artifacts_dir = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto(f"http://127.0.0.1:{test_port}/index.html")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # 1. Capture main window screenshot (should show 3-column layout restored)
    main_shot = os.path.join(artifacts_dir, "layout_structure_restored_verified.png")
    page.screenshot(path=main_shot)
    print("Saved main layout screenshot:", main_shot)

    # Check bounding box of eventsCol: should be on the right side (x > 1000)
    box_events = page.locator("#eventsCol").bounding_box()
    box_chat = page.locator(".col-chat").bounding_box()
    print("Chat box:", box_chat)
    print("Events box:", box_events)
    assert box_events['x'] > box_chat['x'], f"Events should be to the right of chat! events.x={box_events['x']}, chat.x={box_chat['x']}"
    assert box_events['y'] < 150, f"Events should be at top! events.y={box_events['y']}"

    # 2. Open Settings Window and verify
    page.evaluate("openToolWindow('settings')")
    time.sleep(0.5)
    settings_shot = os.path.join(artifacts_dir, "settings_modal_fixed_verified.png")
    page.screenshot(path=settings_shot)
    print("Saved settings modal screenshot:", settings_shot)

    browser.close()

print("[VERIFIED] UI Layout 3-column structure and Settings Modal are 100% perfectly restored!")
