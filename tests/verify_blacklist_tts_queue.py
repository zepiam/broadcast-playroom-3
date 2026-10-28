import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-tts-block-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   page.evaluate("""window.__audios=[];window.Audio=class {constructor(url){this.url=url;this.paused=false;window.__audios.push(this)} play(){return Promise.resolve()} pause(){this.paused=true}};window.bindTtsAvatarAudio=()=>{};window._masterTtsEnabled=true;playChatMessageSpeech('SpeakerA','hello one','twitch');playChatMessageSpeech('SpeakerB','hello two','twitch');""")
   assert page.evaluate('window.__audios.length')==1
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('block')");settings.locator('#blockedViewerName').fill('SpeakerB');settings.locator('button[onclick="blockViewerFromSettings()"]:visible').click()
   settings.get_by_label('บล็อก ทุกส่วน speakerb').uncheck();settings.get_by_label('บล็อก TTS speakerb').check()
   page.evaluate('window.__audios[0].onended()');page.wait_for_timeout(300);assert page.evaluate("window.__audios.filter(x=>x.url.startsWith('/api/tts')).length")==1
   page.evaluate("playChatMessageSpeech('SpeakerC','hello three','twitch')");assert page.evaluate("window.__audios.filter(x=>x.url.startsWith('/api/tts')).length")==2
   settings.locator('#blockedViewerName').fill('SpeakerC');settings.locator('button[onclick="blockViewerFromSettings()"]:visible').click()
   assert page.evaluate("window.__audios.filter(x=>x.url.startsWith('/api/tts'))[1].paused")
   print('PASS blocking removes queued speech and stops matching current speech');browser.close()
 finally:server.shutdown();server.server_close()
