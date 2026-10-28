import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-rand-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   page.evaluate("window.__events=[]; const emit=BP3_BUS.emit.bind(BP3_BUS); BP3_BUS.emit=(e,p)=>{ if(e==='RANDOMIZER_SPIN') window.__events.push(p); return emit(e,p); }")
   with page.expect_popup() as opened: page.locator('#btnRailRandomizer').click()
   panel=opened.value;panel.wait_for_load_state();panel.locator('#randSpinDuration').select_option('2');panel.evaluate('switchRandTab(2)');panel.locator('#randColorTheme').select_option('mint');panel.locator('#randAnchor').select_option('top-right');panel.locator('#randHoldDuration').select_option('8');panel.locator('button[onclick="runSpinRandomizer()"]').click()
   page.wait_for_function('window.__events.length > 0');payload=page.evaluate('window.__events[0]');assert payload['settings']['anchor']=='top-right' and payload['settings']['duration']==8 and payload['settings']['spin_duration']==2 and payload['settings']['color_theme']=='mint' and payload['settings']['mode']=='wheel'
   overlay=page.locator('#on-demand-randomizer-overlay-cs');overlay.wait_for(state='attached');assert overlay.evaluate('(el)=>el.style.right')=='40px';assert overlay.evaluate('(el)=>el.style.top')=='40px';assert overlay.evaluate('(el)=>el.firstElementChild.style.borderColor')=='rgb(16, 185, 129)'
   obs=ctx.new_page();obs.goto(f'http://127.0.0.1:{server.server_port}/composer.html');obs.evaluate("data=>window.dispatchEvent(new CustomEvent('bp3:remote-event',{detail:{event:'RANDOMIZER_SPIN',payload:data}}))",payload)
   rendered=obs.locator('#on-demand-randomizer-overlay');rendered.wait_for(state='attached');assert rendered.evaluate('(el)=>el.style.right')=='40px' and rendered.evaluate('(el)=>el.style.top')=='40px';assert rendered.evaluate('(el)=>el.firstElementChild.style.borderColor')=='rgb(16, 185, 129)'
   assert page.locator('[data-randomizer-mode=wheel]').count()==1 and obs.locator('[data-randomizer-mode=wheel]').count()==1
   page.wait_for_timeout(2300)
   assert 'สุ่มสำเร็จ' in obs.locator('#randomizer-footer-pill').inner_text() or 'ผลการสุ่ม' in obs.locator('#randomizer-footer-pill').inner_text()
   assert 'ผลการสุ่ม' in page.locator('#cs-footer-pill').inner_text()
   panel.evaluate('switchRandTab(1)');panel.locator('#randDisplayMode').select_option('box');panel.locator('#randItemsText').fill('Alpha\nBeta');panel.locator('button[onclick="runSpinRandomizer()"]').click()
   page.wait_for_function('window.__events.length>=2');boxed=page.evaluate('window.__events[1]');assert boxed['settings']['mode']=='box'
   page.locator('[data-randomizer-mode=box]').wait_for(state='attached');obs.evaluate("data=>window.dispatchEvent(new CustomEvent('bp3:remote-event',{detail:{event:'RANDOMIZER_SPIN',payload:data}}))",boxed);obs.locator('[data-randomizer-mode=box]').wait_for(state='attached')
   page.wait_for_timeout(2300);assert page.locator('[data-randomizer-mode=box]').inner_text()=='🎉';assert obs.locator('[data-randomizer-mode=box]').inner_text()=='🎉'
   panel.locator('#randDisplayMode').select_option('viewers');page.evaluate("window._activeChattersSet=new Set(['LiveUser'])");panel.locator('button[onclick="runSpinRandomizer()"]').click();page.wait_for_function('window.__events.length>=3');assert page.evaluate("window.__events[2].winner")=='LiveUser'
   panel.close();page.reload()
   with page.expect_popup() as reopened:page.locator('#btnRailRandomizer').click()
   panel=reopened.value;panel.wait_for_load_state();assert panel.locator('#randAnchor').input_value()=='top-right';assert panel.locator('#randHoldDuration').input_value()=='8';assert panel.locator('#randSpinDuration').input_value()=='2';assert panel.locator('#randColorTheme').input_value()=='mint';assert panel.locator('#randDisplayMode').input_value()=='viewers'
   print('PASS randomizer selections and payload, Composer/OBS anchor and persistence');browser.close()
 finally:server.shutdown();server.server_close()
