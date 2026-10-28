import sys,json,tempfile,threading,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-demo-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'demo','pages':[{'id':'demo','widgets':[{'id':'chat','type':'chat','width':600,'height':400}]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1280,'height':800});context.route('https://**/*',lambda r:r.abort());app=context.new_page();app.on('pageerror',lambda e:errors.append(str(e)));app.goto(base+'/index.html');app.wait_for_selector('#btnSimulateChat')
   obs=browser.new_page();obs.goto(base+'/?p=1');obs.wait_for_selector('.widget',state='attached')
   app.evaluate('window.demoSpeech=[];window.playChatMessageSpeech=(author)=>window.demoSpeech.push(author)')
   app.locator('#simChatSeconds').fill('0.2');app.locator('#simChatSeconds').dispatch_event('change');app.locator('#btnSimulateChat').click();app.wait_for_function("document.querySelectorAll('#chatList .chat-row').length>=3")
   check('Start button produces repeated local comments',app.locator('#btnSimulateChat').get_attribute('aria-pressed')=='true')
   app.locator('#simChatSeconds').fill('1');app.locator('#simChatSeconds').dispatch_event('change');count=app.locator('#chatList .chat-row').count();app.wait_for_timeout(400);check('Changing interval while running takes effect',app.locator('#chatList .chat-row').count()==count)
   obs.wait_for_function("document.body.textContent.includes('[DEMO]')");check('Independent overlay receives demo comments',True)
   app.locator('#btnSimulateChat').click();count=app.locator('#chatList .chat-row').count();app.wait_for_timeout(1100);check('Stop button stops generation',app.locator('#chatList .chat-row').count()==count and app.locator('#btnSimulateChat').get_attribute('aria-pressed')=='false')
   check('Demo does not pollute real roster, participants or TTS',app.evaluate("_activeChattersSet.size===0 && _gwParticipants.length===0 && !(JSON.parse(localStorage.getItem('bp3_user_roster') || '[]')).length && !demoSpeech.some(name=>String(name).startsWith('[DEMO]'))"))
   app.locator('#simChatSeconds').fill('0');app.locator('#simChatSeconds').dispatch_event('change');check('Interval lower bound enforced',app.locator('#simChatSeconds').input_value()=='0.2')
   app.evaluate("()=>{for(let i=0;i<205;i++)injectIncomingChat({username:'[DEMO] bounded',demo:true,text:'bounded '+i,platform:'Twitch',avatar:'',icon:''})}")
   check('Main chat retains only latest 200 messages',app.locator('#chatList .chat-row').count()==200 and app.locator('#chatList .chat-body-msg').last.inner_text()=='bounded 204')
   app.wait_for_timeout(600)
   check('UTF-8 log retains older comments', '[DEMO]' in (Path(folder)/'log.txt').read_text(encoding='utf-8'))
   app.reload();app.wait_for_selector('#simChatSeconds');check('Interval persists and demo does not auto-start',app.locator('#simChatSeconds').input_value()=='0.2' and app.locator('#btnSimulateChat').get_attribute('aria-pressed')=='false')
   check('EasyDonate setup hidden, saved data retained',app.evaluate("(()=>{const b=document.createElement('div');BP3LegacyControls.mount(b,{type:'donate_goal',dg_api_key:'saved-secret'},()=>{});return !b.querySelector('#compLegacy_dg_api_key') && !!b.querySelector('#compLegacy_dg_goal_title')})()"))
   entry={'id':'audit-log','event':'CHAT_MESSAGE','payload':{'username':'ผู้ชมจริง','platform':'Twitch','text':'<ข้อความจริง> ภาษาไทย\\nบรรทัดสอง'}}
   launch_dev.overlay_events.publish(entry);launch_dev.overlay_events.publish(entry)
   history=(Path(folder)/'log.txt').read_text(encoding='utf-8')
   check('Real text retained literally and duplicate relay not logged twice',history.count('<ข้อความจริง>')==1)
   check('No JavaScript errors' ,not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production layout unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'demo-controls.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
