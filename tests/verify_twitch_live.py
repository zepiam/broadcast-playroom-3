import sys,os,json,time,tempfile,threading,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'work'/'compat-audit'
OUT.mkdir(parents=True,exist_ok=True)
result={'channel':'https://www.twitch.tv/ateliersage','real_network':True,'sent_chat_messages':0,'tests':[]}
server=None
original_hash=hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest()
def record(test,passed,detail=''):
 item=dict(test=test,status='PASS' if passed else 'FAIL',detail=detail);result['tests'].append(item);print(item,flush=True)
try:
 with tempfile.TemporaryDirectory(prefix='bp3-live-') as directory:
  launch_dev.LAYOUT_FILE=str(Path(directory)/'layout.json');launch_dev._LAYOUT_CACHE=None
  launch_dev.save_layout({'version':3,'activePageId':'live','pages':[{'id':'live','name':'Live','widgets':[dict(id='actual-live-chat',type='chat',width=700,height=900,x=20,y=20)]}]})
  server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
  base=f'http://127.0.0.1:{server.server_port}'
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True)
   context=browser.new_context(viewport={'width':1920,'height':1080});context.add_init_script("if(location.protocol==='http:')localStorage.setItem('bp3_master_tts','false')")
   context.route('https://**/*',lambda route:route.abort())
   page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
   page.on('dialog',lambda dialog:dialog.accept('https://www.twitch.tv/ateliersage'))
   page.goto(base+'/index.html');page.wait_for_timeout(1200)
   obs_context=browser.new_context(viewport={'width':1920,'height':1080});obs_context.route('https://**/*',lambda route:route.abort())
   obs=obs_context.new_page();obs.on('pageerror',lambda error:errors.append(str(error)));obs.goto(base+'/?p=1');obs.wait_for_selector('#widget-chat-feed-actual-live-chat')
   page.locator('#btn-plat-twitch').click()
   page.wait_for_function("document.querySelector('#btn-plat-twitch')?.textContent.includes('หยุด') || document.querySelector('#status-twitch')?.textContent.includes('ไม่สำเร็จ')",timeout=40000)
   state=launch_dev.chat_bridge.get_status()['twitch']
   record('Actual Twitch connect button opens anonymous channel',state['connected'],json.dumps(state,ensure_ascii=False))
   start=time.monotonic()
   while state['connected'] and time.monotonic()-start<150:
    messages=launch_dev.chat_bridge.get_messages()
    if messages and obs.locator('#widget-chat-feed-actual-live-chat .chat-line').count()>0:break
    page.wait_for_timeout(1000)
    if int(time.monotonic()-start)%30==0:print('Waiting for actual channel chat...',flush=True)
   messages=launch_dev.chat_bridge.get_messages()
   record('Actual channel sends provider messages',bool(messages),f'{len(messages)} messages received')
   record('Actual channel messages appear in main app',bool(messages) and page.locator('#chatList .chat-row').count()>0)
   record('Actual channel messages reach independent overlay context',obs.locator('#widget-chat-feed-actual-live-chat .chat-line').count()>0)
   page.screenshot(path=str(OUT/'live-twitch-app.png'));obs.screenshot(path=str(OUT/'live-twitch-overlay.png'),omit_background=True)
   if state['connected']:
    page.locator('#btn-plat-twitch').click();page.wait_for_timeout(700)
    record('Actual disconnect button closes Twitch client',not launch_dev.chat_bridge.get_status()['twitch']['connected'])
   record('No JavaScript errors during actual Twitch session',not errors,json.dumps(errors))
   browser.close()
except Exception as error:
 import traceback
 record('Actual Twitch harness completed',False,traceback.format_exc())
finally:
 launch_dev.chat_bridge.disconnect('twitch')
 if server:server.shutdown();server.server_close()
 record('Real production layout remains unchanged',original_hash==hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest())
 (OUT/'twitch-live.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
