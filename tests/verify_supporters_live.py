import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='support-live-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as opened:page.locator('.status-support-link').click()
   settings=opened.value;settings.wait_for_load_state();settings.wait_for_function("!document.getElementById('supporterList').textContent.includes('กำลังโหลด')",timeout=25000)
   text=settings.locator('#supporterList').inner_text();assert 'โหลดรายชื่อไม่สำเร็จ' not in text
   print('PASS read-only real supporters API in settings; cards:',settings.locator('.support-person').count());browser.close()
 finally:server.shutdown();server.server_close()
