import os,sys,tempfile,threading,io,wave
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from playroom_media import PlayroomMedia
with tempfile.TemporaryDirectory(prefix='bp3-secret-sound-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.playroom_media=PlayroomMedia(Path(tmp)/'media');launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   page.evaluate("window.__audio=[];window.Audio=class {constructor(url){this.url=url;this.paused=false;window.__audio.push(this)}play(){return Promise.resolve()}pause(){this.paused=true}};window.bindTtsAvatarAudio=()=>{};window._masterTtsEnabled=true")
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('secret')");assert settings.locator('#secretSoundList').inner_text()==''
   buf=io.BytesIO()
   with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*80)
   settings.locator('#secretSoundCode').fill('wow');settings.locator('#secretSoundFile').set_input_files({'name':'fixture.wav','mimeType':'audio/wav','buffer':buf.getvalue()});settings.locator('button[onclick="addSecretSound()"]').click();settings.locator('#secretSoundList').filter(has_text='!wow').wait_for()
   blocked=page.request.post(f'http://127.0.0.1:{server.server_port}/api/playroom/import',headers={'Origin':'https://unrelated.example','X-Filename':'bad.wav'},data=b'fake');assert blocked.status==403
   uploaded=page.evaluate("BP3SecretSounds.match('!wow').url");assert page.request.get(f'http://127.0.0.1:{server.server_port}'+uploaded).body()==buf.getvalue();assert page.request.get(f'http://127.0.0.1:{server.server_port}'+uploaded,headers={'Origin':'https://unrelated.example'}).status==403
   page.evaluate("injectIncomingChat({username:'SoundUser',platform:'Twitch',text:'!wow hello',event:'message'})");page.wait_for_function("window.__audio.some(a=>a.url.startsWith('/api/tts'))")
   urls=page.evaluate("window.__audio.map(a=>a.url)");tts=next(u for u in urls if u.startswith('/api/tts'));assert 'hello' in tts and 'wow' not in tts
   assert not any(u.startswith('/playroom-media/') for u in urls)
   page.evaluate("window.__audio.find(a=>a.url.startsWith('/api/tts')).onended()");page.wait_for_function("window.__audio.some(a=>a.url.startsWith('/playroom-media/'))")
   page.evaluate("window.__audio.find(a=>a.url.startsWith('/playroom-media/')).onended()");page.wait_for_timeout(200)
   page.evaluate("window._blockedUsers.blockedsound={tts:true};injectIncomingChat({username:'BlockedSound',platform:'Twitch',text:'!wow',event:'message'})");page.wait_for_timeout(200);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).length")==1
   page.evaluate("injectIncomingChat({username:'MuteQueueUser',platform:'Twitch',text:'!wow another',event:'message'})");page.wait_for_timeout(150);page.locator('#btnChatCodeMute').click()
   page.evaluate("window.__audio.filter(a=>a.url.startsWith('/api/tts')).at(-1).onended()");page.wait_for_timeout(250);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).length")==1
   page.locator('#btnChatCodeMute').click()
   settings.locator('#secretSoundLimit').fill('1');settings.locator('#secretSoundLimit').dispatch_event('change')
   page.evaluate("injectIncomingChat({username:'LimitedUser',platform:'Twitch',text:'!wow',event:'message'})");page.wait_for_timeout(200)
   before=page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).length")
   page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).at(-1).onended()");page.wait_for_timeout(200)
   page.evaluate("injectIncomingChat({username:'LimitedUser',platform:'Twitch',text:'!wow',event:'message'})");page.wait_for_timeout(200);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).length")==before
   page.locator('#btnChatCodeMute').click();page.evaluate("injectIncomingChat({username:'AnotherUser',platform:'Twitch',text:'!wow',event:'message'})");page.wait_for_timeout(200);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).length")==before
   settings.close();page.reload()
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('secret')");assert '!wow' in settings.locator('#secretSoundList').inner_text() and settings.locator('#secretSoundLimit').input_value()=='1';assert page.locator('#btnChatCodeMute').get_attribute('aria-pressed')=='true'
   settings.on('dialog',lambda dialog:dialog.accept('renamed'))
   settings.locator('#secretSoundList button').get_by_text('แก้โค้ด').click();settings.locator('#secretSoundList').filter(has_text='!renamed').wait_for()
   settings.locator('#secretSoundList input[type=file]').set_input_files({'name':'replacement.wav','mimeType':'audio/wav','buffer':buf.getvalue()});settings.locator('#secretSoundList').filter(has_text='replacement.wav').wait_for()
   volume=settings.locator('#secretSoundList input[type=range]');volume.fill('40');assert '40%' in settings.locator('#secretSoundList').inner_text()
   settings.locator('#secretSoundList button').get_by_text('ลบ').click();assert settings.locator('#secretSoundList').inner_text()==''
   print('PASS audio import, playback order, limits, mute, persistence, edit, replace, volume and delete');browser.close()
 finally:server.shutdown();server.server_close()
