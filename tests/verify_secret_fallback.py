import os,sys,tempfile,threading,json
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-fallback-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]});server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});entry={'entries':[{'code':'!wow','name':'fixture.wav','url':'/playroom-media/'+'a'*64+'.wav','volume':1,'available':True}],'muted':False,'dailyLimit':0}
   ctx.add_init_script("localStorage.setItem('bp3_secret_sound_settings_v1',"+json.dumps(json.dumps(entry))+")")
   page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.evaluate("""window.__audio=[];window.Audio=class {constructor(url){this.url=url;window.__audio.push(this)}play(){return Promise.resolve()}pause(){}};window.__utter=null;window.SpeechSynthesisUtterance=class {constructor(text){this.text=text;this.events={}}addEventListener(n,fn){this.events[n]=fn}};window.speechSynthesis.getVoices=()=>[];window.speechSynthesis.speak=u=>window.__utter=u;window.bindTtsAvatarAudio=()=>{};window.bindTtsAvatarUtterance=()=>{};window._masterTtsEnabled=true;injectIncomingChat({username:'FallbackUser',platform:'Twitch',text:'!wow hello',event:'message'});""")
   page.evaluate("window.__audio.find(a=>a.url.startsWith('/api/tts')).onerror()");assert page.evaluate("!!window.__utter && window.__utter.text==='hello'")
   page.wait_for_timeout(250);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/playroom-media/')).length")==0
   page.evaluate("window.__utter.events.end()");page.wait_for_function("window.__audio.some(a=>a.url.startsWith('/playroom-media/'))")
   print('PASS secret sound waits for browser fallback speech to finish');browser.close()
 finally:server.shutdown();server.server_close()
