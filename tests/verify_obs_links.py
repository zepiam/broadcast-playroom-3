import os,sys,tempfile,threading,types,base64
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
class FakeClient:
 def __init__(self,host,port,password,timeout):
  if password != 'good': raise RuntimeError('bad password')
  self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_version(self): return types.SimpleNamespace(obs_version='test')
 def get_stream_status(self): return types.SimpleNamespace(output_active=True,output_timecode='01:02:03.000')
 def get_record_status(self): return types.SimpleNamespace(output_active=False)
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=FakeClient)
class FakeKeyboard:
 def __init__(self):self.keys={}
 def add_hotkey(self,key,callback,suppress=False): self.keys[key]=callback;return key
 def remove_hotkey(self,key):self.keys.pop(key,None)
with tempfile.TemporaryDirectory(prefix='bp3-obs-links-') as folder:
 launch_dev.clip_markers.folder=Path(folder)/'markers';launch_dev.clip_hotkey=launch_dev.ClipHotkey(Path(folder)/'hotkey.json',launch_dev.clip_markers,FakeKeyboard());launch_dev.clip_hotkey.start();launch_dev.obs_connection=launch_dev.ObsConnection(Path(folder)/'obs.dat',launch_dev.clip_markers,lambda b:base64.b64encode(b),lambda b:base64.b64decode(b));launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');base=f'http://127.0.0.1:{server.server_port}/'
   assert page.locator('#localServerStatus').inner_text().endswith(f':{server.server_port}')
   page.wait_for_function("document.getElementById('obsConnectionStatus').textContent.includes('ปิดใช้งาน')")
   with page.expect_popup() as result:page.locator('#btnRailSettings').click()
   settings=result.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('docks')")
   assert settings.locator('#inpSettingsObsOverlayUrl').input_value()==base
   assert settings.locator('#inpSettingsObsDockUrl').input_value()==base+'dock.html'
   with ctx.expect_page() as opened:settings.locator('button[onclick="openObsPage(\'dock\')"]').click()
   dock=opened.value;dock.wait_for_load_state();assert dock.url==base+'dock.html'
   settings.evaluate("switchSettingsSection('obs')")
   settings.locator('#obsWsPassword').fill('good');dialogs=[];settings.on('dialog',lambda dialog:(dialogs.append(dialog.message),dialog.accept()))
   settings.locator('button[onclick="testObsConnection()"]').click();settings.wait_for_timeout(500)
   assert 'OBS test' in dialogs[-1]
   settings.locator('#obsWsEnabled').check();settings.locator('button[onclick="saveObsConnection()"]').click();settings.wait_for_timeout(500)
   assert launch_dev.obs_connection.public()['enabled'] and launch_dev.obs_connection.public()['has_password']
   assert settings.locator('#obsWsPassword').input_value()==''
   settings.locator('button[onclick="testObsConnection()"]').click();settings.wait_for_timeout(500);assert 'OBS test' in dialogs[-1]
   page.locator('.split-btn-main[onclick*=markClip]').click()
   page.wait_for_function("document.getElementById('clipMarkerStatus').textContent.includes('01:02:03')")
   marker=launch_dev.clip_markers.folder/'clip_markers.txt';assert '[01:02:03]' in marker.read_text(encoding='utf-8')
   page.on('dialog',lambda dialog:dialog.accept('ctrl+shift+m') if dialog.type=='prompt' else dialog.accept())
   page.evaluate("configureClipHotkey()");page.wait_for_timeout(300);assert launch_dev.clip_hotkey.public()['shortcut']=='ctrl+shift+m'
   page.evaluate("clipMarkerAction('clear')");page.wait_for_function("document.getElementById('clipMarkerStatus').textContent.includes('ล้าง')");assert marker.read_text(encoding='utf-8')==''
   settings.locator('#obsWsPassword').fill('bad');settings.locator('button[onclick="testObsConnection()"]').click();settings.wait_for_timeout(300)
   assert 'ไม่สำเร็จ' in dialogs[-1]
   print('PASS OBS links and tests, clip mark from OBS timecode and confirmed clear');browser.close()
 finally:launch_dev.clip_hotkey.stop();launch_dev.obs_connection.stop();server.shutdown();server.server_close()
