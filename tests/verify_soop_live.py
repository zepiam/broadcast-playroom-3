import os,sys,tempfile,threading,time
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev,chat_bridge,chat_soop,requests
with tempfile.TemporaryDirectory(prefix='bp3-soop-live-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.overlay_events.chat_log_path=Path(tmp)/'chat.log';launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[{'id':'chat','type':'chat','chatMode':'default','width':600,'height':400}]}]})
 chat_bridge.print=lambda *args,**kwargs:None
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});ctx.add_init_script("localStorage.setItem('bp3_master_tts','false')")
   page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');obs=ctx.new_page();obs.goto(f'http://127.0.0.1:{server.server_port}/composer.html');obs.frame_locator('#legacyChat_chat').locator('#chat').wait_for(state='attached')
   response=requests.post(chat_soop._LIVE_API_URL+'?bjid=djsinicyn',data={'bid':'djsinicyn','bno':'','type':'live','player_type':'html5','mode':'landing','from_api':'0','pwd':'','stream_type':'common','quality':'HD'},headers=chat_soop._HEADERS,timeout=10)
   bno=str((response.json().get('CHANNEL') or {}).get('BNO') or '');
   if not bno.isdigit():print('SKIP: public test stream is offline');browser.close();raise SystemExit(0)
   url='https://play.sooplive.com/djsinicyn/'+bno
   page.evaluate("url=>{setPlatformChannel('soop',url);window.__openedUrl='';window.open=u=>{window.__openedUrl=u;};openPlatformChannelWeb('soop',url)}",url);assert page.evaluate('window.__openedUrl')==url
   page.locator('#btn-plat-soop').click()
   page.wait_for_function("typeof _platformStates !== 'undefined' && _platformStates.soop.connected",timeout=20000)
   page.wait_for_function("document.querySelector('#chatList .chat-row[data-message-id]')",timeout=30000)
   mid=page.locator('#chatList .chat-row[data-message-id]').first.get_attribute('data-message-id')
   obs.frame_locator('#legacyChat_chat').locator(f'[data-message-id="{mid}"]').wait_for(state='attached',timeout=15000)
   existing_ids=set(page.locator('#chatList .chat-row[data-message-id]').evaluate_all("rows=>rows.map(row=>row.dataset.messageId)"))
   bridge=launch_dev.chat_bridge
   bridge._reconnect_interval=1
   first_client=bridge._clients['soop']
   first_client._ws.shutdown()
   deadline=time.monotonic()+35
   while time.monotonic()<deadline:
    if bridge._clients.get('soop') is not first_client and bridge._statuses['soop']['connected']:
     break
    time.sleep(.2)
   else: raise AssertionError('SOOP did not reconnect after socket shutdown')
   page.wait_for_function("ids=>Array.from(document.querySelectorAll('#chatList .chat-row[data-message-id]')).some(row=>!ids.includes(row.dataset.messageId))",arg=list(existing_ids),timeout=30000)
   new_ids=page.locator('#chatList .chat-row[data-message-id]').evaluate_all("rows=>rows.map(row=>row.dataset.messageId)")
   new_id=next(value for value in new_ids if value not in existing_ids)
   obs.frame_locator('#legacyChat_chat').locator(f'[data-message-id=\"{new_id}\"]').wait_for(state='attached',timeout=15000)
   print('PASS live SOOP URL, matching overlay message and automatic reconnect; no outbound messages or TTS');page.locator('#btn-plat-soop').click();browser.close()
 finally:launch_dev.chat_bridge.disconnect('soop');server.shutdown();server.server_close()
