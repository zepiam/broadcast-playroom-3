import time
import threading
from http.server import HTTPServer
from playwright.sync_api import sync_playwright
import launch_dev

test_port = 9003
while launch_dev.is_port_in_use(test_port):
    test_port += 1

server = HTTPServer(('127.0.0.1', test_port), launch_dev.QuietHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()
time.sleep(1)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("console", lambda msg: print(f"CONSOLE: [{msg.type}] {msg.text}"))
    page.goto(f"http://127.0.0.1:{test_port}/index.html")
    page.wait_for_load_state("networkidle")

    # Send a chat
    page.fill("#txtChatInput", "สวัสดีครับ ทดสอบ")
    page.click("#btnChatSend")
    time.sleep(4)

    browser.close()
