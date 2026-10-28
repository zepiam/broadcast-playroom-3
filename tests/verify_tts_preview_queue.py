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
   browser=p.chromium.launch();ctx=browser.new_context();ctx.add_init_script("""window.__sounds=[];window.Audio=class extends EventTarget {constructor(url){super();this.url=url;window.__sounds.push(this)}play(){return Promise.resolve()}pause(){}};""")
   ctx.route('**/api/capabilities',lambda route:route.fulfill(json={'rvc':True}));ctx.route('**/api/rvc/models',lambda route:route.fulfill(json={'models':[],'status':{'state':'idle','enabled':False,'loaded':False}}));ctx.route('**/api/rvc/status',lambda route:route.fulfill(json={'state':'idle','enabled':False,'loaded':False}));page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as opened:page.locator('#btnRailVoiceSettings').click()
   voice=opened.value;voice.wait_for_load_state();button=voice.locator('#btnVoiceTest');button.click(timeout=5000);assert button.is_disabled();assert voice.locator("[onclick='playVoiceTest()']").last.is_disabled()
   page.evaluate('playVoiceTest();playVoiceTest()');assert page.evaluate("window.__sounds.filter(x=>x.url.startsWith('/api/tts')).length")==1
   page.evaluate("window.__sounds.find(x=>x.url.startsWith('/api/tts')).onended()");assert button.is_enabled();button.click();assert page.evaluate("window.__sounds.filter(x=>x.url.startsWith('/api/tts')).length")==2
   page.evaluate("window.__sounds.filter(x=>x.url.startsWith('/api/tts'))[1].onended()")
   page.evaluate("()=>{Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[],speak:u=>window.__utter=u},configurable:true});window.SpeechSynthesisUtterance=class extends EventTarget {constructor(text){super();this.text=text}};}")
   button.click();page.evaluate("window.__sounds.filter(x=>x.url.startsWith('/api/tts'))[2].onerror()");assert button.is_disabled();page.evaluate("window.__utter.dispatchEvent(new Event('end'))");assert button.is_enabled()
   page.evaluate("window.__sounds=[];injectIncomingChat({username:'First',platform:'Twitch',text:'first test',event:'message'});injectIncomingChat({username:'Second',platform:'Twitch',text:'second test',event:'message'});injectIncomingChat({username:'Third',platform:'Twitch',text:'third test',event:'message'})")
   assert page.evaluate('window.__sounds.length')==1
   page.evaluate('window.__sounds[0].onended()');page.wait_for_function('window.__sounds.length===2');assert 'second%20test' in page.evaluate('window.__sounds[1].url')
   page.evaluate('window.__sounds[1].onended()');page.wait_for_function('window.__sounds.length===3');assert 'third%20test' in page.evaluate('window.__sounds[2].url');page.evaluate('window.__sounds[2].onended()')
   print('PASS voice test lock until ended and FIFO chat audio queue (fake audio, no playback)');browser.close()
 finally:server.shutdown();server.server_close()
