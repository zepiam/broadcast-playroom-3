import sys,json,tempfile,threading,time,hashlib,faulthandler
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from playroom_media import PlayroomMedia
from chat_twitch import ChatMessage
faulthandler.dump_traceback_later(45,repeat=True)
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
results=[]
def record(name,value):
 print(name,value,flush=True);results.append({'test':name,'status':'PASS' if value else 'FAIL'});assert value,name
with tempfile.TemporaryDirectory(prefix='bp3-gw-direct-') as directory:
 root=Path(directory);launch_dev.LAYOUT_FILE=str(root/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.playroom_media=PlayroomMedia(root/'uploads')
 launch_dev.save_layout({'activePageId':'test','pages':[{'id':'test','widgets':[{'id':'test-gw','type':'giveaway','width':1920,'height':1080}]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context();context.route('https://**/*',lambda route:route.abort());context.add_init_script("localStorage.setItem('bp3_master_tts','false')")
   app=context.new_page();app.set_default_timeout(8000);errors=[];app.on('pageerror',lambda error:errors.append(str(error)));app.goto(base+'/index.html');app.wait_for_timeout(1000)
   remote=browser.new_context();overlay=remote.new_page();overlay.set_default_timeout(8000);overlay.goto(base+'/giveaway')
   with app.expect_popup() as info:app.locator('#btnRailGw').click()
   gw=info.value;gw.set_default_timeout(8000);gw.wait_for_load_state('domcontentloaded');gw.on('pageerror',lambda error:errors.append(str(error)))
   print('STEP receive names',flush=True);gw.locator('[onclick="resetGiveaway()"]').click();gw.locator('#gwInputCodeCustom').fill('#direct');gw.locator('#btnGwToggleLiveCode').click()
   for name in ['direct_first','direct_first','direct_second']:launch_dev.chat_bridge._on_message('Twitch',ChatMessage(platform='twitch',author=name,text='#direct'))
   app.wait_for_function('_gwParticipants.length===2',timeout=8000);record('Code collects unique names without prize fields',gw.locator('#gwPrizeTableBody,#btnGwMode2').count()==0)
   gw.locator('#gwTableBody tr').filter(has_text='direct_first').locator('button').click();gw.locator('#btnGwDraw').click();gw.wait_for_function("document.querySelectorAll('#gwWinnerHistory tr').length===1",timeout=8000);record('Draw records actual remaining name', 'direct_second' in gw.locator('#gwWinnerHistory').text_content())
   gw.locator('#btnGwDraw').click();gw.wait_for_function("document.querySelectorAll('#gwWinnerHistory tr').length===2",timeout=8000);record('Same list can be drawn again',True)
   gw.locator('[onclick="resetGiveaway()"]').click();print('STEP screenshot',flush=True);gw.screenshot(path=str(out/'giveaway-direct-window.png'),timeout=8000)
   print('STEP expand settings',flush=True);gw.locator('#gwOverlaySettings summary').click()
   image=root/'banner.svg';image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="90"><rect width="300" height="90" fill="purple"/></svg>',encoding='utf-8')
   print('STEP choose image',flush=True)
   with gw.expect_file_chooser() as choice:gw.locator('#btnGiveawayImportImage').click()
   choice.value.set_files(str(image));app.wait_for_function("getGwOverlayOptions().config.overlay_image_url.startsWith('/playroom-media/')",timeout=8000)
   print('STEP image overlay',flush=True);gw.locator('#btnGwToggleLiveCode').click();overlay.locator('.giveaway-image-box.visible').wait_for(state='visible')
   decoded=overlay.locator('.giveaway-custom-img').evaluate("image=>Promise.race([image.decode().then(()=>({ok:true,width:image.naturalWidth,src:image.getAttribute('src')})),new Promise(resolve=>setTimeout(()=>resolve({ok:false,src:image.getAttribute('src'),complete:image.complete}),5000))])")
   print('IMAGE',decoded,flush=True);record('Selected image decodes in independent Overlay',decoded.get('ok') and decoded.get('width')==300)
   gw.locator('#btnGwToggleLiveCode').click();gw.locator('[name="gwOverlayMode"][value="banner"]').check();gw.locator('#gwReceiveDuration').fill('1');gw.locator('#btnSaveGiveawaySettings').click();gw.locator('#btnGwToggleLiveCode').click();app.wait_for_function('_isGwCodeBroadcasting===false',timeout=5000);record('Optional reception timer stops',True)
   record('No JavaScript errors',not errors);print('STEP browser cleanup',flush=True);browser.close()
 finally:
  (out/'giveaway-direct.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print('STEP server cleanup',flush=True);server.shutdown();server.server_close();faulthandler.cancel_dump_traceback_later()
