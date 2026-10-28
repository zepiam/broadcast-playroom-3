import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(accept_downloads=True);ctx.add_init_script("localStorage.setItem('bp3_master_tts','false')");page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.evaluate("injectIncomingChat({username:'TestViewer',platform:'Twitch',text:'hello',event:'message'})")
   with page.expect_popup() as opened:page.locator('#btnRailUserManager').click()
   manager=opened.value;manager.wait_for_load_state();manager.locator('#userRosterBody').get_by_text('TestViewer',exact=True).first.wait_for()
   with manager.expect_download() as result:manager.locator('#btnUserRosterExport').click()
   download=result.value;file=Path(tmp)/'viewers.csv';download.save_as(str(file));text=file.read_text(encoding='utf-8-sig');assert 'TestViewer' in text and 'Twitch' in text and 'ชื่อผู้ชม' in text
   print('PASS user manager export CSV via popup with isolated viewer');browser.close()
 finally:server.shutdown();server.server_close()
