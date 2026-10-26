import sys
import os
import time
import threading
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3')
from launch_dev import start_server, PORT
from chat_bridge import chat_bridge
from chat_twitch import ChatMessage

def test_real_chat_system():
    # 1. Start server in thread
    server = start_server()
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"✓ Started test HTTP server on port {PORT}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1600, 'height': 950})

            # Load from http dev server
            page.goto(f'http://127.0.0.1:{PORT}/index.html')
            page.wait_for_timeout(1000)

            # 1. Verify chatList is clean with empty state
            empty_state = page.locator("#chatEmptyState")
            assert empty_state.is_visible(), "Chat empty state must be visible initially!"
            print("✓ Live chat empty state is visible (0 mock messages).")

            chat_rows = page.locator("#chatList .chat-row")
            assert chat_rows.count() == 0, "No mock chat rows should exist!"
            print("✓ Verified 0 mock messages in #chatList.")

            # 2. Click connect on Twitch card
            btn_twitch = page.locator("#btn-plat-twitch")
            assert btn_twitch.is_visible(), "Twitch connect button must be visible!"
            btn_twitch.click()
            page.wait_for_timeout(1500)

            # Verify card status
            status_twitch = page.locator("#status-twitch")
            status_text = status_twitch.inner_text()
            print(f"✓ Twitch status after clicking connect: '{status_text}'")
            assert "เชื่อมต่อแล้ว" in status_text, "Twitch should be connected!"

            # 3. Simulate an incoming real chat via chat_bridge
            test_msg = ChatMessage(
                platform='twitch',
                author='RealStreamer_Fan',
                text='ทดสอบระบบแชทจริงพร้อมใช้งานแล้วครับ!',
                event='message'
            )
            chat_bridge._on_message('Twitch', test_msg)
            print("✓ Injected real message into chat_bridge.")

            # Wait for poller to pick it up in browser
            page.wait_for_timeout(1500)

            # 4. Verify message rendered in #chatList
            chat_rows_after = page.locator("#chatList .chat-row")
            print(f"Chat rows count after message: {chat_rows_after.count()}")
            assert chat_rows_after.count() == 1, "Real chat message must be rendered in #chatList!"

            rendered_author = page.locator("#chatList .chat-username").first.inner_text()
            rendered_msg = page.locator("#chatList .chat-body-msg").first.inner_text()
            print(f"✓ Rendered: [{rendered_author}] {rendered_msg}")
            assert rendered_author == "RealStreamer_Fan"
            assert "ทดสอบระบบแชทจริง" in rendered_msg

            # Verify empty state was removed
            assert empty_state.count() == 0 or not empty_state.is_visible()
            print("✓ Empty state cleanly removed when real chat arrived.")

            # 5. Capture screenshot
            page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/real_chat_system_verified.png")
            print("✓ Saved screenshot real_chat_system_verified.png")

            # 6. Disconnect Twitch
            btn_twitch.click()
            page.wait_for_timeout(1000)
            status_after_disc = status_twitch.inner_text()
            print(f"✓ Twitch status after disconnect: '{status_after_disc}'")
            assert "ยังไม่เชื่อมต่อ" in status_after_disc

            browser.close()
            print("All Real Chat Connection tests passed 100%!")

    finally:
        server.shutdown()
        print("Server stopped cleanly.")

if __name__ == '__main__':
    test_real_chat_system()
