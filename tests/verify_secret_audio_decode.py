import os,sys,tempfile,threading,io,wave
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from playroom_media import PlayroomMedia
with tempfile.TemporaryDirectory(prefix='bp3-audio-decode-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.playroom_media=PlayroomMedia(Path(tmp)/'media');launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(args=['--mute-audio']);ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   page.evaluate("""window.__audioDone=false;const OriginalAudio=window.Audio;window.Audio=function(url){const audio=new OriginalAudio(url);audio.addEventListener('ended',()=>window.__audioDone=true);return audio};""")
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('secret')")
   buf=io.BytesIO()
   with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*1600)
   settings.locator('#secretSoundCode').fill('fixture');settings.locator('#secretSoundFile').set_input_files({'name':'fixture.wav','mimeType':'audio/wav','buffer':buf.getvalue()});settings.locator('button[onclick="addSecretSound()"]').click();settings.locator('#secretSoundList').filter(has_text='!fixture').wait_for();settings.locator('#secretSoundList button').get_by_text('▶ ฟัง').click();page.wait_for_function('window.__audioDone',timeout=10000)
   print('PASS uploaded WAV decoded and reached playback end in muted browser');browser.close()
 finally:server.shutdown();server.server_close()
