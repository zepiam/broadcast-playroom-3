import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-demo-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':'gw','type':'giveaway','width':1920,'height':1080},{'id':'ask','type':'ask','width':500,'height':350}]
 launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':widgets}]});server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as info:page.locator('#btnRailComposer').click()
   studio=info.value;studio.set_default_timeout(7000);studio.wait_for_load_state();obs=ctx.new_page();obs.goto(f'http://127.0.0.1:{server.server_port}/composer.html')
   studio.locator('.composer-layer-item[data-id="gw"] .btn-layer-setting').click();studio.locator('#btnDemoGiveawayDraw').click()
   studio.locator('#widget-gw .giveaway-draw-box').wait_for(state='attached');obs.locator('.type-giveaway .giveaway-draw-box').wait_for(state='attached')
   assert not page.evaluate('!!window._liveGwState?.active')
   if studio.locator('#btnCompCloseSetting').is_visible():studio.locator('#btnCompCloseSetting').click()
   studio.locator('.composer-layer-item[data-id="ask"] .btn-layer-setting').click();studio.locator('#btnDemoAskVote').click()
   studio.locator('#widget-ask').filter(has_text='[DEMO]').wait_for(state='attached');obs.locator('.type-ask').filter(has_text='[DEMO]').wait_for(state='attached')
   assert not page.evaluate('!!window._liveAskState?.active')
   page.evaluate("window._liveAskState={active:true,question:'real'}");dialogs=[];page.on('dialog',lambda d:(dialogs.append(d.message),d.accept()));studio.locator('#btnDemoAskVote').click();page.wait_for_timeout(300)
   assert dialogs and 'โพลจริง' in dialogs[-1];assert page.evaluate('window._liveAskState.question')=='real'
   print('PASS demo controls on Composer/OBS and live poll guard');browser.close()
 finally:server.shutdown();server.server_close()
