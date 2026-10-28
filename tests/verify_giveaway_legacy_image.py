import os,sys,tempfile,threading,hashlib,requests,traceback
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from legacy_compat import make_server
from playroom_media import PlayroomMedia
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);launch_dev.playroom_media=PlayroomMedia(root/'media');launch_dev.LAYOUT_FILE=str(root/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 main=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);alias=make_server(launch_dev.QuietHandler,'chat',0)
 for server in (main,alias):threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();appctx=browser.new_context();appctx.add_init_script("localStorage.setItem('bp3_master_tts','false')");app=appctx.new_page();app.goto(f'http://127.0.0.1:{main.server_port}/index.html')
   other=browser.new_context();pending={};other.on('request',lambda request:pending.__setitem__(id(request),request.url));other.on('requestfinished',lambda request:pending.pop(id(request),None));other.on('requestfailed',lambda request:pending.pop(id(request),None));extras=[other.new_page() for _ in range(5)];[page.goto(f'http://localhost:{alias.server_port}/giveaway') for page in extras];obs=other.new_page();obs.on('response',lambda r: print('MEDIA',r.status,r.url,flush=True) if '/playroom-media/' in r.url else None);obs.goto(f'http://localhost:{alias.server_port}/giveaway')
   with app.expect_popup() as opened:app.locator('#btnRailGw').click()
   gw=opened.value;gw.wait_for_load_state();gw.locator('#btnGwToggleLiveCode').click()
   app.evaluate("_gwParticipants.push({username:'First',platform:'Twitch',time:'now'})")
   for style in ['gachapon','slot','shuffle']:
    gw.locator('#gwDrawStyle').select_option(style);gw.locator('#btnGwDraw').click();gw.wait_for_timeout(200)
   gw.locator('[onclick="resetGiveaway()"]').click();gw.locator('#gwOverlaySettings summary').click()
   image=root/'banner.svg';image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="90"><rect width="300" height="90" fill="purple"/></svg>',encoding='utf-8')
   with gw.expect_file_chooser() as chooser:gw.locator('#btnGiveawayImportImage').click()
   chooser.value.set_files(str(image));app.wait_for_function("getGwOverlayOptions().config.overlay_has_image")
   print('SETTINGS',app.evaluate('getGwOverlayOptions()'),flush=True)
   gw.locator('#btnGwToggleLiveCode').click();obs.locator('.giveaway-image-box.visible').wait_for(timeout=5000);obs.wait_for_timeout(1500)
   print('IMAGE',obs.locator('.giveaway-custom-img').evaluate("e=>({src:e.src,attr:e.getAttribute('src'),width:e.naturalWidth,complete:e.complete})"),flush=True)
   print('DIRECT',requests.get(f'http://localhost:{alias.server_port}/api/avatar/sync',timeout=3).status_code,flush=True);assert obs.locator('.giveaway-custom-img').evaluate('e=>e.naturalWidth')==300
   print('PASS legacy giveaway banner imported and rendered');browser.close()
 finally:
  for server in (main,alias):server.shutdown();server.server_close()
