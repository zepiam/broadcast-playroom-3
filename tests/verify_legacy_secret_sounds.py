import os,sys,tempfile,threading,json,hashlib
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev,legacy_user_filters
with tempfile.TemporaryDirectory(prefix='bp3-legacy-sound-') as tmp:
 root=Path(tmp);sound=root/'old.wav';sound.write_bytes(b'legacy-audio-fixture');old=root/'settings.json';old.write_text(json.dumps({'secret_codes':[{'code':'!old','sound_path':str(sound),'volume':.45},{'code':'!missing','sound_path':str(root/'missing.wav'),'volume':1}],'secret_code_daily_limit':3,'code_sound_muted':True,'token':'private-secret'}),encoding='utf8');digest=hashlib.sha256(old.read_bytes()).digest()
 launch_dev.LAYOUT_FILE=str(root/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]});launch_dev.LEGACY_FILTER_IMPORT_ENABLED=True
 original=launch_dev.legacy_secret_sounds.read;launch_dev.legacy_secret_sounds.read=lambda:original([old]);oldfilters=legacy_user_filters.load;legacy_user_filters.load=lambda:{}
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.wait_for_function("!!BP3SecretSounds.match('!old')")
   response=page.request.get(f'http://127.0.0.1:{server.server_port}/api/legacy/secret-sounds');assert str(root) not in response.text() and 'private-secret' not in response.text()
   entry=next(item for item in response.json()['entries'] if item['code']=='!old');assert page.request.get(f'http://127.0.0.1:{server.server_port}'+entry['url']).body()==b'legacy-audio-fixture';assert page.request.get(f'http://127.0.0.1:{server.server_port}'+entry['url'],headers={'Origin':'https://unrelated.example'}).status==403
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('secret')");assert '!old' in settings.locator('#secretSoundList').inner_text() and 'ไม่พบไฟล์' in settings.locator('#secretSoundList').inner_text();assert settings.locator('#secretSoundLimit').input_value()=='3' and page.locator('#btnChatCodeMute').get_attribute('aria-pressed')=='true'
   assert hashlib.sha256(old.read_bytes()).digest()==digest
   print('PASS legacy secret sound migration, isolated registered file and missing file status');browser.close()
 finally:launch_dev.LEGACY_FILTER_IMPORT_ENABLED=False;launch_dev.legacy_secret_sounds.read=original;legacy_user_filters.load=oldfilters;server.shutdown();server.server_close()
