import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json,threading,tempfile,time,hashlib,traceback
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
marker=Path(sys.argv[2]) if len(sys.argv)>2 else None
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
results=[];errors=[]
def check(name,success,detail=''):
 results.append({'test':name,'status':'PASS' if success else 'FAIL','detail':detail});print(results[-1],flush=True);assert success,name
with tempfile.TemporaryDirectory() as directory:
 launch_dev.LAYOUT_FILE=str(Path(directory)/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.save_layout({'pages':[{'id':'audit','widgets':[{'id':'obs-chat','type':'chat','width':600,'height':300}]}],'activePageId':'audit','legacyTools':{'game_overlay_x':120,'game_overlay_y':120,'game_overlay_width':420,'game_overlay_height':300,'game_overlay_alpha':1,'game_overlay_auto_hide':False}})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);app=browser.new_page();app.on('pageerror',lambda error:errors.append(str(error)));app.goto(base+'/index.html')
   obs=browser.new_page();obs.goto(base+'/composer.html?p=1')
   game=browser.new_page();game.on('pageerror',lambda error:errors.append(str(error)));game.goto(base+'/legacy-game-chat.html');game.wait_for_function('typeof config!=="undefined" && config.font_size===14')
   launch_dev.overlay_events.publish({'event':'CHAT_MESSAGE','payload':{'username':'Desktop Auditor','text':'ACTUAL NATIVE OVERLAY MESSAGE','platform':'Twitch'}})
   game.locator('#chat').filter(has_text='ACTUAL NATIVE OVERLAY MESSAGE').wait_for(state='visible');check('Original Game Overlay HTML/config renders actual relay messages',True)
   app.locator('#topbar-item-game-overlay').click()
   until=time.monotonic()+30
   while time.monotonic()<until and not any(item.get('ready') for item in launch_dev.desktop_overlays.snapshot()['instances']):app.wait_for_timeout(100)
   state=launch_dev.desktop_overlays.snapshot();check('Main application button starts real legacy Qt window',len(state['instances'])==1 and state['instances'][0]['ready'],json.dumps(state))
   if marker:
    (out/'desktop-ready.json').write_text(json.dumps({'base':base,'state':state}),encoding='utf-8');print('READY FOR NATIVE VISUAL INSPECTION',flush=True)
    until=time.monotonic()+240
    while time.monotonic()<until and not marker.exists():app.wait_for_timeout(200)
    state=launch_dev.desktop_overlays.snapshot();check('Native hotkey exits edit mode',not state['instances'][0]['editing'])
    settings=launch_dev.get_layout()['legacyTools'];check('Dragged native position persists in temporary profile',settings.get('game_overlay_x')!=120 or settings.get('game_overlay_y')!=120,json.dumps(settings))
    check('Native clear leaves OBS chat intact','ACTUAL NATIVE OVERLAY MESSAGE' in obs.locator('#widget-chat-feed-obs-chat').inner_text())
   app.evaluate("desktopOverlayAction('game','edit')");app.wait_for_timeout(400)
   app.locator('#topbar-item-game-overlay').click();app.wait_for_timeout(600)
   check('Main application button stops its native Game Overlay',len(launch_dev.desktop_overlays.snapshot()['instances'])==0)
   with app.expect_popup() as info:app.evaluate("openDesktopOverlaySettings()")
   settings=info.value;settings.wait_for_load_state('domcontentloaded');
   for index in range(3):settings.locator('#desktopOverlayUrl'+str(index)).fill(base+'/legacy-game-chat.html')
   settings.locator('#desktop-game_overlay_font_size').fill('23');settings.locator('#btnSaveDesktopOverlays').click();app.wait_for_timeout(300)
   check('Game Overlay font setting saves actual value',launch_dev.get_layout()['legacyTools']['game_overlay_font_size']==23)
   check('Overlay+ actual URL saves to temporary profile',launch_dev.get_layout()['legacyTools']['more_overlays'][0]['url']==base+'/legacy-game-chat.html')
   settings.close();game.reload();game.wait_for_function('config.font_size===23');check('Saved Game Overlay font reaches original renderer',True)
   app.locator('#topbar-item-game-overlay').click();until=time.monotonic()+30
   while time.monotonic()<until and not any(item.get('ready') for item in launch_dev.desktop_overlays.snapshot()['instances']):app.wait_for_timeout(100)
   check('Game Overlay reopens with persisted dimensions',any(item.get('ready') for item in launch_dev.desktop_overlays.snapshot()['instances']))
   app.locator('#topbar-item-game-overlay').click();app.wait_for_timeout(300)
   app.locator('#topbar-item-overlay-plus').click();until=time.monotonic()+30
   while time.monotonic()<until:
    state=launch_dev.desktop_overlays.snapshot()
    if len(state['instances'])==3 and all(item['ready'] for item in state['instances']):break
    app.wait_for_timeout(100)
   state=launch_dev.desktop_overlays.snapshot();check('Overlay+ button opens three configured real Qt URL windows',len(state['instances'])==3 and all(item['kind']=='overlay+' and item['ready'] for item in state['instances']),json.dumps(state))
   app.locator('#topbar-item-overlay-plus').click();app.wait_for_timeout(600);check('Overlay+ button closes its own window',not launch_dev.desktop_overlays.snapshot()['instances'])
   check('No JavaScript page errors',not errors,str(errors));browser.close()
 except Exception:
  results.append({'test':'Harness completion','status':'FAIL','detail':traceback.format_exc()});print(traceback.format_exc(),flush=True)
 finally:
  launch_dev.desktop_overlays.stop();server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest)
  (out/'desktop-overlays.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
if any(item['status']=='FAIL' for item in results):sys.exit(1)
