import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   page.evaluate("""window.__audio=[];window.Audio=class {constructor(url){this.url=url;this.paused=false;window.__audio.push(this)}play(){return Promise.resolve()}pause(){this.paused=true}};window.bindTtsAvatarAudio=()=>{};injectIncomingChat({username:'One',platform:'Twitch',text:'one',event:'message'});injectIncomingChat({username:'Two',platform:'Twitch',text:'two',event:'message'});injectIncomingChat({username:'Three',platform:'Twitch',text:'three',event:'message'});""")
   assert page.evaluate('_audioTtsQueue.length')==2
   page.locator('#btnMasterTts').click();assert page.evaluate('_audioTtsQueue.length')==0 and page.evaluate('window.__audio[0].paused')
   page.wait_for_timeout(250);page.locator('#btnMasterTts').click();page.wait_for_timeout(250);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/api/tts')).length")==1
   page.evaluate("""Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[],speak:u=>window.__utter=u,cancel:()=>{window.__cancelled=true}},configurable:true});window.SpeechSynthesisUtterance=class extends EventTarget {constructor(text){super();this.text=text}};window.bindTtsAvatarUtterance=()=>{};injectIncomingChat({username:'Four',platform:'Twitch',text:'four',event:'message'});injectIncomingChat({username:'Five',platform:'Twitch',text:'five',event:'message'});window.__audio.filter(a=>a.url.startsWith('/api/tts'))[1].onerror();""")
   assert page.evaluate('_audioTtsQueue.length')==1
   page.locator('#btnMasterTts').click();assert page.evaluate('window.__cancelled') and page.evaluate('_audioTtsQueue.length')==0
   page.locator('#btnMasterTts').click();page.wait_for_timeout(250);assert page.evaluate("window.__audio.filter(a=>a.url.startsWith('/api/tts')).length")==2
   print('PASS stop clears queued chat, stops audio and browser fallback, no old messages resume');browser.close()
 finally:server.shutdown();server.server_close()
