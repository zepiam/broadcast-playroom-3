import os,sys,tempfile,threading,json,hashlib
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev,legacy_user_filters
with tempfile.TemporaryDirectory(prefix='bp3-legacy-filter-') as tmp:
 old=Path(tmp)/'settings.json';old.write_text(json.dumps({'blocked_users':[{'name':'OldTTSPerson','hide_overlay':False},{'name':'OldAll','hide_overlay':True}],'tts_bot_blacklist':['oldbot'],'overlay_hide_bots':False,'twitch_bot_name':'mybot','banned_words':['badword'],'dns_enabled':True,'dns_service':'google_doh','dns_custom':'','token':'private-secret'}),encoding='utf8');digest=hashlib.sha256(old.read_bytes()).digest()
 priority=Path(tmp)/'priority.json';priority.write_text(json.dumps({'dns_enabled':False}),encoding='utf8')
 assert legacy_user_filters.load([priority,old])['dns_enabled'] is False and legacy_user_filters.load([priority,old])['tts_bot_blacklist']==['oldbot']
 real_load=legacy_user_filters.load;legacy_user_filters.load=lambda:real_load([old]);launch_dev.LEGACY_FILTER_IMPORT_ENABLED=True
 launch_dev.dns_settings=launch_dev.DnsSettings(Path(tmp)/'dns.json');launch_dev.tts_service.dns_settings=launch_dev.dns_settings;launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   page.wait_for_function("window._blockedUsers?.oldttsperson==='tts' && window._blockedUsers?.oldall===true")
   response=page.request.get(f'http://127.0.0.1:{server.server_port}/api/legacy/user-filters');assert 'private-secret' not in response.text()
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('block')")
   assert settings.locator('#botBlacklistNames').input_value()=='oldbot' and not settings.locator('#botBlacklistHideOverlay').is_checked() and settings.locator('#botBlacklistOwnName').input_value()=='mybot'
   settings.evaluate("switchSettingsSection('networking')");settings.wait_for_timeout(500);assert settings.locator('#chkEnableDns').is_checked() and settings.locator('#selDnsProvider').input_value()=='google_doh'
   settings.evaluate("switchSettingsSection('ng')");assert settings.locator('#bannedWordsList').input_value()=='badword'
   settings.locator('#bannedWordsList').fill('customword');settings.close();page.reload()
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('ng')");assert settings.locator('#bannedWordsList').input_value()=='customword'
   assert hashlib.sha256(old.read_bytes()).digest()==digest
   print('PASS automatic old filter migration, allowlisted data, user edits preserved, old file unchanged');browser.close()
 finally:launch_dev.LEGACY_FILTER_IMPORT_ENABLED=False;legacy_user_filters.load=real_load;server.shutdown();server.server_close()
