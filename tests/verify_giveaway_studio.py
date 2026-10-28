import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-gw-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':'gw','type':'giveaway','width':1920,'height':1080},{'id':'clock','type':'clock','width':250,'height':100,'clockFormat':'HH:MM:SS'}]
 launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':widgets}]});server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as info:page.locator('#btnRailComposer').click()
   studio=info.value;studio.set_default_timeout(7000);studio.wait_for_load_state();studio.locator('#widget-gw').wait_for(state='attached');studio.evaluate("window._gwNode=document.querySelector('#widget-gw');window._clockNode=document.querySelector('#widget-clock')")
   obs=ctx.new_page();obs.goto(f'http://127.0.0.1:{server.server_port}/composer.html');obs.locator('.type-giveaway').wait_for(state='attached')
   for style in ['gachapon','slot','shuffle']:
    data={'active':True,'phase':'winner','winner':'Tester','candidates':['Tester','Other'],'style':style,'drawId':style,'config':{}}
    page.evaluate("data=>BP3_BUS.emit('GIVEAWAY_UPDATE',data)",data)
    obs.evaluate("data=>window.dispatchEvent(new CustomEvent('bp3:remote-event',{detail:{event:'GIVEAWAY_UPDATE',payload:data}}))",data)
    studio.locator('#widget-gw .giveaway-draw-box').wait_for(state='attached')
    studio.wait_for_function("style=>{const draw=document.querySelector('#widget-gw .giveaway-draw-box'),slot=document.querySelector('#widget-gw .giveaway-slot-stage');return draw && slot && draw.classList.contains('style-gachapon')===(style==='gachapon') && slot.classList.contains('is-reel')===(style==='slot')}",arg=style)
    obs.wait_for_function("style=>{const draw=document.querySelector('.type-giveaway .giveaway-draw-box'),slot=document.querySelector('.type-giveaway .giveaway-slot-stage');return draw && slot && draw.classList.contains('style-gachapon')===(style==='gachapon') && slot.classList.contains('is-reel')===(style==='slot')}",arg=style)
    assert studio.evaluate("document.querySelector('#widget-gw')===window._gwNode && document.querySelector('#widget-clock')===window._clockNode")
   page.evaluate("BP3_BUS.emit('GIVEAWAY_UPDATE',{active:false})");studio.wait_for_timeout(300)
   assert studio.locator('#widget-gw .giveaway-cp-box').count()==0
   print('PASS giveaway legacy presentation mounted for all draw styles without replacing widgets');browser.close()
 finally:server.shutdown();server.server_close()
