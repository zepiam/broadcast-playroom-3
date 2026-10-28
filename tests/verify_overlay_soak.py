import sys,json,tempfile,threading,time,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[];samples=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-soak-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'pages':[{'id':'soak','widgets':[{'id':'chat','type':'chat','width':600,'height':400,'maxMessages':20},{'id':'emotes','type':'emote_party','width':600,'height':400,'epDuration':1,'epMaxEmotes':10}]}],'activePageId':'soak'})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);page=browser.new_page();page.set_default_timeout(8000);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'/?p=1');page.wait_for_selector('.widget',state='attached');cdp=page.context.new_cdp_session(page);cdp.send('Performance.enable');start=time.monotonic()
   for cycle in range(24):
    for index in range(100):launch_dev.overlay_events.publish({'event':'CHAT_MESSAGE','payload':{'id':cycle*100+index+1,'username':'soak','text':f'Cycle {cycle} message {index}','platform':'Twitch'}})
    page.wait_for_function(f"document.getElementById('widget-chat-feed-chat')?.textContent.includes('Cycle {cycle} message 99')")
    metrics=page.evaluate("()=>{BP3LegacyEmotes.show(_overlayWidgets.find(w=>w.id==='emotes'),Array.from({length:50},()=>({text:'⭐'})));return {messages:document.getElementById('widget-chat-feed-chat').children.length,emotes:document.querySelectorAll('[data-live-emote]').length}}")
    assert metrics['messages']<=100 and metrics['emotes']<=10,metrics
    page.wait_for_timeout(4800);assert page.locator('[data-live-emote]').count()==0
    cdp.send('HeapProfiler.collectGarbage');heap=next(m['value'] for m in cdp.send('Performance.getMetrics')['metrics'] if m['name']=='JSHeapUsedSize');samples.append({'cycle':cycle+1,'elapsed_s':round(time.monotonic()-start,2),'heap_bytes_after_gc':heap,**metrics})
    if cycle%6==5:print('Soak cycles',cycle+1,'elapsed',round(time.monotonic()-start),'heap',int(heap),flush=True)
   check('2400 relay messages render in order across 24 bursts without crash',True);check('Chat and Emote Party stay bounded; emotes clear each cycle',True)
   page.reload();page.wait_for_function("document.getElementById('widget-chat-feed-chat')?.textContent.includes('Cycle 23 message 99')");check('Overlay refresh restores last message snapshot',True)
   launch_dev.overlay_events.publish({'event':'CHAT_CLEAR','payload':{}});page.wait_for_function("document.getElementById('widget-chat-feed-chat')?.textContent.trim()===''");check('Clear works after repeated bursts and refresh',True);check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'overlay-soak.json').write_text(json.dumps({'results':results,'errors':errors,'samples':samples,'limits':'Short headless Chromium soak only; no GPU, full-day or actual OBS stability claim.'},indent=2),encoding='utf-8')
