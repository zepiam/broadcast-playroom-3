import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-block-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as popup:page.locator('#btnRailSettings').click()
   settings=popup.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('block')")
   assert 'viewertest' not in settings.locator('#blockedViewerList').inner_text().lower()
   settings.locator('#blockedViewerName').fill('ViewerTest');settings.locator('button[onclick="blockViewerFromSettings()"]:visible').click();assert 'viewertest' in settings.locator('#blockedViewerList').inner_text()
   page.evaluate("injectIncomingChat({demo:true,username:'ViewerTest',platform:'Twitch',text:'blocked-test-unique'})");assert 'blocked-test-unique' not in page.locator('#chatList').inner_text()
   settings.close();page.reload()
   with page.expect_popup() as popup:page.locator('#btnRailSettings').click()
   settings=popup.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('block')");assert 'viewertest' in settings.locator('#blockedViewerList').inner_text()
   settings.locator('#blockedViewerList tr').filter(has_text='viewertest').get_by_text('ปลดบล็อก').click();page.evaluate("injectIncomingChat({demo:true,username:'ViewerTest',platform:'Twitch',text:'unblocked-test-unique'})");assert 'unblocked-test-unique' in page.locator('#chatList').inner_text()
   print('PASS block, chat filtering, restart persistence and unblock');browser.close()
 finally:server.shutdown();server.server_close()
