import os
import sys
import time
import subprocess
import urllib.request
import json
from playwright.sync_api import sync_playwright

os.environ["PYTHONIOENCODING"] = "utf-8"

def main():
    root_dir = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"
    artifact_dir = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"

    # 1. Start launch_dev.py
    cmd = [sys.executable, "launch_dev.py", "--no-browser"]
    proc = subprocess.Popen(cmd, cwd=root_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")

    server_port = 8801
    server_ready = False
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{server_port}/api/status", timeout=1) as res:
                if res.status == 200:
                    server_ready = True
                    break
        except Exception:
            time.sleep(0.5)

    if not server_ready:
        proc.kill()
        print("Failed to start server")
        sys.exit(1)

    print(f"Server is ready on port {server_port}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1400, "height": 900})
            page = context.new_page()

            # 2. Navigate to main UI
            page.goto(f"http://127.0.0.1:{server_port}/index.html")
            page.wait_for_selector("#topbar-item-translate", timeout=8000)

            # Check initial translate button state
            btn = page.locator("#topbar-item-translate")
            label = page.locator("#txtTranslateLabel")
            icon = page.locator("#txtTranslateIcon")
            print("Initial button text:", label.inner_text())

            # 3. Toggle button (click to switch to multilang)
            btn.click()
            time.sleep(0.6)
            print("After click 1 text:", label.inner_text(), "icon:", icon.inner_text())
            assert "อ่านทุกภาษา" in label.inner_text(), "Should toggle to multilang"

            # Check backend mode
            with urllib.request.urlopen(f"http://127.0.0.1:{server_port}/api/translate/mode") as res:
                mode_data = json.loads(res.read())
                print("Backend mode after toggle 1:", mode_data)
                assert mode_data.get("mode") == "multilang"

            # Toggle back to translate
            btn.click()
            time.sleep(0.6)
            print("After click 2 text:", label.inner_text(), "icon:", icon.inner_text())
            assert "แปลภาษา" in label.inner_text(), "Should toggle to translate"

            # Check backend mode
            with urllib.request.urlopen(f"http://127.0.0.1:{server_port}/api/translate/mode") as res:
                mode_data = json.loads(res.read())
                print("Backend mode after toggle 2:", mode_data)
                assert mode_data.get("mode") == "translate"

            # 4. Open Settings > Translate Section (handle popup if opened, or in-page)
            try:
                with page.expect_popup(timeout=2000) as popup_info:
                    page.evaluate("() => { openToolWindow('settings'); }")
                settings_page = popup_info.value
                settings_page.wait_for_load_state()
                settings_page.evaluate("() => { switchSettingsSection('translate'); }")
                settings_page.wait_for_selector("#sec-translate", state="visible", timeout=5000)
                
                chk_live = settings_page.locator("#chkAutoTranslateLive")
                chk_orig = settings_page.locator("#chkShowOriginalText")
                assert chk_live.is_checked(), "chkAutoTranslateLive should be checked"
                assert chk_orig.is_checked(), "chkShowOriginalText should be checked"
                settings_page.close()
                print("Settings popup verified and closed")
            except Exception as e:
                # If in-page window instead of popup
                page.evaluate("() => { switchSettingsSection('translate'); }")
                page.wait_for_selector("#sec-translate", state="visible", timeout=5000)
                chk_live = page.locator("#chkAutoTranslateLive")
                chk_orig = page.locator("#chkShowOriginalText")
                assert chk_live.is_checked(), "chkAutoTranslateLive should be checked"
                assert chk_orig.is_checked(), "chkShowOriginalText should be checked"
                page.evaluate("() => { closeToolWindow('settings'); }")
                print("In-page settings verified and closed")

            # 5. Inject a foreign chat message (English) via /api/test/chat
            test_msg = {
                "platform": "Twitch",
                "author": "Emily",
                "text": "Good evening streamer! How are you today?"
            }
            req = urllib.request.Request(
                f"http://127.0.0.1:{server_port}/api/test/chat",
                data=json.dumps(test_msg).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                inject_res = json.loads(res.read())
                print("Inject response:", inject_res)
                assert inject_res.get("ok") is True

            # 6. Wait for chat message to appear in the live chat feed
            page.wait_for_selector("#chatList .chat-row", timeout=10000)
            
            chat_rows = page.locator("#chatList .chat-row")
            print(f"Total live chat rows in #chatList: {chat_rows.count()}")
            last_row = chat_rows.last
            row_text = last_row.inner_text()
            print("Last chat row text:\n", row_text)

            # Check that Emily's translated message contains Thai and original text label
            assert "Emily" in row_text, "Author Emily must be in row"
            assert "ต้นฉบับ: Good evening streamer! How are you today?" in row_text, "Original text label must be displayed"
            # And Thai translation should be present
            assert ("สวัสด" in row_text) or ("ตอนเย็น" in row_text) or ("สบายดี" in row_text), "Thai translated text should be present"

            # 7. Take screenshot of Live Chat with translated message and the Translate button
            screenshot_path = os.path.join(artifact_dir, "verified_translate_feature.png")
            page.screenshot(path=screenshot_path)
            print("Screenshot saved to:", screenshot_path)

            print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
            browser.close()
    finally:
        proc.kill()
        print("Server stopped")

if __name__ == "__main__":
    main()
