import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-status-') as tmp:
 launch_dev.dns_settings=launch_dev.DnsSettings(Path(tmp)/'dns.json');launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});state={'ok':True,'calls':0}
   def reply(route):
    state['calls']+=1;route.fulfill(status=200 if state['ok'] else 500,content_type='audio/mpeg',body=b'fake-audio' if state['ok'] else b'')
   ctx.route('**/api/tts?**',reply);page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.wait_for_timeout(900)
   assert page.locator('#serverStatusText').inner_text()=='ยังไม่ได้ทดสอบ' and state['calls']==0
   page.locator('#topbarServerStatus').click();page.wait_for_function("document.getElementById('serverStatusText').textContent==='ทดสอบเสียงสำเร็จ'");assert state['calls']==1
   state['ok']=False;page.locator('#topbarServerStatus').click();page.wait_for_function("document.getElementById('serverStatusText').textContent==='ทดสอบไม่สำเร็จ'")
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('networking')")
   settings.locator('#dnsTestResult').filter(has_text='ยังไม่ได้ทดสอบ').wait_for();assert not settings.locator('#chkEnableDns').is_disabled()
   settings.evaluate("switchSettingsSection('defender')");assert 'ยังไม่ได้ตรวจสอบ' in settings.locator('#lblDefenderStatus').inner_text();assert 'E:\\DOCS' not in settings.locator('#lblDefenderPath').inner_text()
   print('PASS TTS actual request success/failure, honest DNS and Defender status');browser.close()
 finally:server.shutdown();server.server_close()
