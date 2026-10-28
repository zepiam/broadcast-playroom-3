import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-secret-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('secret')")
   assert settings.locator('#secretCodesList').input_value()==''
   settings.locator('#secretCodesList').fill('#secret\nสวัสดี');assert page.evaluate("getSpeakableChatText('ก่อน #secret หลัง')")=='ก่อน หลัง';assert page.evaluate("getSpeakableChatText('สวัสดี ทุกคน')")=='ทุกคน'
   assert page.evaluate("getSpeakableChatText('abc#secret123')")=='abc#secret123'
   settings.locator('#secretCodesEnabled').uncheck();assert page.evaluate("getSpeakableChatText('ก่อน #secret หลัง')")=='ก่อน #secret หลัง';assert page.evaluate("getSpeakableChatText('!unknown')")==''
   settings.close();page.reload()
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('secret')");assert settings.locator('#secretCodesList').input_value()=='#secret\nสวัสดี' and not settings.locator('#secretCodesEnabled').is_checked()
   settings.locator('#secretCodesEnabled').check();assert page.evaluate("getSpeakableChatText('ก่อน #secret หลัง')")=='ก่อน หลัง'
   print('PASS settings, TTS filtering, disabled, command suppression and persistence');browser.close()
 finally:server.shutdown();server.server_close()
