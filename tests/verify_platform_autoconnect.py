import os,sys,tempfile,threading,json,hashlib
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev,legacy_user_filters
with tempfile.TemporaryDirectory() as tmp:
 old=Path(tmp)/'old.json';old.write_text(json.dumps({'auto_connect_twitch':True,'twitch_channel':'legacychannel','auto_connect_kick':False,'kick_channel':'legacykick','ask_post_result':True,'kick_oauth_token':'secret-example'}),encoding='utf-8');digest=hashlib.sha256(old.read_bytes()).digest();loader=legacy_user_filters.load;legacy_user_filters.load=lambda:loader([old]);launch_dev.LEGACY_FILTER_IMPORT_ENABLED=True
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context();calls=[]
   def connect(route):calls.append(route.request.url);route.fulfill(json={'success':True,'connected':False})
   context.route('**/api/connect?*',connect);page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.wait_for_function("localStorage.getItem('bp3_legacy_autoconnect_imported')==='1'");page.wait_for_timeout(700)
   assert len(calls)==1 and 'platform=twitch' in calls[0] and 'legacychannel' in calls[0]
   assert page.evaluate("localStorage.getItem('bp3_channel_kick')")=='legacykick'
   assert 'secret-example' not in page.request.get(f'http://127.0.0.1:{server.server_port}/api/legacy/user-filters').text()
   with page.expect_popup() as opened:page.locator('#btnRailSettings').click()
   settings=opened.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('platforms')");assert settings.locator('#cfgTwitchAuto').is_checked();settings.locator('#cfgTwitchBotAskPost').wait_for(state='visible');assert settings.locator('#cfgTwitchBotAskPost').is_checked();settings.locator('#cfgTwitchAuto').uncheck();settings.locator('#cfgKickAuto').check();settings.close()
   assert page.evaluate("localStorage.getItem('bp3_auto_connect_twitch')")=='false';calls.clear();page.reload();page.wait_for_timeout(700)
   assert len(calls)==1 and 'platform=kick' in calls[0] and 'legacykick' in calls[0]
   assert hashlib.sha256(old.read_bytes()).digest()==digest
   print('PASS per-platform auto-connect, migration, saved changes and no token exposure (simulated connection)');browser.close()
 finally:launch_dev.LEGACY_FILTER_IMPORT_ENABLED=False;legacy_user_filters.load=loader;server.shutdown();server.server_close()
