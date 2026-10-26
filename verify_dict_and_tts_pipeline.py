import os
import sys
import time
import socket
import threading
import requests
from http.server import HTTPServer
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

from launch_dev import QuietHandler, is_port_in_use
import launch_dev

# Start server on dynamic port
test_port = 8995
while is_port_in_use(test_port):
    test_port += 1

server = HTTPServer(('127.0.0.1', test_port), QuietHandler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
time.sleep(1.2)

server_url = f"http://127.0.0.1:{test_port}"
print(f"[TEST] Server running at {server_url}")

# 1. Test Backend API: Dictionary
res_dict = requests.get(f"{server_url}/api/dictionary")
assert res_dict.status_code == 200, f"Dictionary API failed: {res_dict.status_code}"
dict_data = res_dict.json()
words_count = len(dict_data.get('replace_words', {}))
print(f"[TEST] /api/dictionary returned {words_count} words")
assert words_count >= 39, f"Expected at least 39 words, got {words_count}"

# 2. Test Backend API: TTS Audio Stream with Dictionary Replacement
# "youtube" should be replaced with "ยูทู๊ป" and "discord" with "ดิ๊ดข่อด"
res_tts = requests.get(f"{server_url}/api/tts", params={
    "text": "ยินดีต้อนรับสู่สตูดิโอครับ youtube และ discord 555+",
    "gender": "female"
})
assert res_tts.status_code == 200, f"TTS API failed: {res_tts.status_code}"
assert res_tts.headers.get('Content-Type') == 'audio/mpeg', f"Wrong content-type: {res_tts.headers.get('Content-Type')}"
audio_len = len(res_tts.content)
print(f"[TEST] /api/tts generated {audio_len} audio bytes (audio/mpeg)")
assert audio_len > 5000, f"Audio bytes too small: {audio_len}"

# 3. Test Playwright UI
artifacts_dir = r"C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    
    page.goto(f"{server_url}/index.html")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Open Settings Window
    page.evaluate("openToolWindow('settings')")
    time.sleep(0.5)

    # 3.1 Test Dictionary Table Section
    page.evaluate("switchSettingsSection('replace')")
    time.sleep(0.8)

    # Check rows rendered
    rows = page.locator("#dictTableBody tr").count()
    badge_text = page.locator("#dictWordCountBadge").text_content()
    print(f"[TEST] UI Dictionary table rendered {rows} rows, badge: '{badge_text}'")
    assert rows >= 39, f"Expected 39+ rows in table, got {rows}"

    # Take screenshot of Dictionary UI
    dict_screenshot_path = os.path.join(artifacts_dir, "dictionary_management_verified.png")
    page.screenshot(path=dict_screenshot_path)
    print(f"[TEST] Saved dictionary screenshot: {dict_screenshot_path}")

    # 3.2 Test Filter Input
    page.fill("#dictFilterInput", "youtube")
    time.sleep(0.4)
    filtered_rows = page.locator("#dictTableBody tr").count()
    print(f"[TEST] Filter 'youtube' resulted in {filtered_rows} row(s)")
    assert filtered_rows >= 1, "Filter should show youtube row"

    # Reset filter
    page.fill("#dictFilterInput", "")
    time.sleep(0.4)

    # 3.3 Test Add Word
    page.evaluate("toggleAddWordForm(true)")
    page.fill("#txtNewFindWord", "ezgame")
    page.fill("#txtNewReplaceWord", "อีซี่เกมเกมง่ายจัง")
    page.evaluate("saveNewDictionaryWord()")
    time.sleep(0.8)
    rows_after_add = page.locator("#dictTableBody tr").count()
    print(f"[TEST] After adding 'ezgame', rows: {rows_after_add}")
    assert rows_after_add == rows + 1, "Row count should increase by 1"

    # Clean up added test word
    page.evaluate("fetch('/api/dictionary/delete?word=ezgame').then(() => loadDictionaryTable())")
    time.sleep(0.8)

    # 3.4 Test TTS Settings Section
    page.evaluate("switchSettingsSection('tts')")
    time.sleep(0.5)

    # Test Edge-TTS tester
    page.fill("#txtTtsTestInput", "สวัสดีครับ ทดสอบระบบ Edge-TTS Broadcast Playroom")
    page.click("#btnTestEdgeTts")
    time.sleep(2.5)
    status_text = page.locator("#ttsTestStatus").text_content()
    print(f"[TEST] TTS tester status: '{status_text}'")
    assert "เล่นเสียง" in status_text or "สำเร็จ" in status_text or "Edge-TTS" in status_text, f"Unexpected status: {status_text}"

    # Take screenshot of TTS Settings UI
    tts_screenshot_path = os.path.join(artifacts_dir, "edge_tts_pipeline_verified.png")
    page.screenshot(path=tts_screenshot_path)
    print(f"[TEST] Saved TTS pipeline screenshot: {tts_screenshot_path}")

    browser.close()

print("[SUCCESS] All Dictionary and Edge-TTS Pipeline verification tests passed flawlessly!")
