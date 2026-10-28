import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context();page=ctx.new_page();page.goto(base+'/index.html');item=page.locator('#topbar-item-overlay');item.click(button='right')
   with ctx.expect_page() as opened:page.locator('#topbarContextMenu button').filter(has_text='เปิดทดสอบสดในเบราว์เซอร์').click()
   preview=opened.value;preview.wait_for_load_state();assert preview.url==base+'/composer.html?test=1';preview.close()
   item.click(button='right')
   with ctx.expect_page() as opened:page.locator('#topbarContextMenu button').filter(has_text='ตั้งค่า OBS WebSocket').click()
   settings=opened.value;settings.wait_for_load_state();settings.locator('#sec-obs').wait_for(state='visible');print('PASS overlay menu opens active server preview and OBS settings');browser.close()
 finally:server.shutdown();server.server_close()
