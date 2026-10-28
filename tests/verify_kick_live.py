import sys,threading,tempfile,time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from chat_bridge import ChatBridge
with tempfile.TemporaryDirectory(prefix='kick-live-') as temp:
 launch_dev.LAYOUT_FILE=str(Path(temp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.chat_bridge=ChatBridge()
 launch_dev.save_layout({'activePageId':'kick','pages':[{'id':'kick','widgets':[{'id':'kickchat','type':'chat','chatMode':'default','width':600,'height':400}]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context();context.add_init_script("localStorage.setItem('bp3_master_tts','false')");app=context.new_page();app.goto(base+'/index.html');app.evaluate("setPlatformChannel('kick','3mr')");obs=browser.new_page();obs.goto(base+'/?p=1');obs.wait_for_selector('#legacyChat_kickchat');app.locator('#btn-plat-kick').click()
   app.wait_for_function("document.querySelector('#card-kick').classList.contains('connected')",timeout=20000)
   app.wait_for_function("document.querySelectorAll('#chatList .chat-row').length>0",timeout=25000)
   obs.frame_locator('#legacyChat_kickchat').locator('#chat .msg').first.wait_for(state='attached',timeout=25000)
   print('PASS: real Kick connection, main live chat and independent overlay received chat')
   app.locator('#btn-plat-kick').click();browser.close()
 finally:
  launch_dev.chat_bridge.disconnect('kick');server.shutdown();server.server_close()
