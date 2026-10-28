import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-window-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();requests=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1600,'height':900});ctx.add_init_script("localStorage.setItem('bp3_auto_popout_windows','false')");page=ctx.new_page()
   def owner(route):requests.append(route.request.post_data_json['name']);route.fulfill(json={'ok':True})
   ctx.route('**/api/window/owner',owner);page.goto(f'http://127.0.0.1:{server.server_port}/index.html');assert page.locator('#btnRailChatWidget').is_hidden() and page.locator('#btnTogglePopoutMode').count()==0
   for name,button in [('giveaway','#btnRailGw'),('ask','#btnRailAsk'),('replie','#btnRailReplie'),('randomizer','#btnRailRandomizer'),('composer','#btnRailComposer'),('settings','#btnRailSettings'),('user-manager','#btnRailUserManager'),('playroom','#btnRailPlayroom')]:
    with page.expect_popup() as result:page.locator(button).click()
    popup=result.value;popup.wait_for_load_state();popup.wait_for_selector('#win-'+name);assert popup.locator('.btn-popout-toggle').count()==0
    if name in ('giveaway','ask','replie','randomizer'):assert popup.locator('#win-'+name+' [onclick="copyObsUrl() "]').count()==0 and popup.locator('#win-'+name+' [onclick="copyObsUrl()"]' ).count()==0
    page.wait_for_function('(name)=>window.__ownerRequests?.includes(name)',arg=name,timeout=5000) if False else None
    popup.close()
   page.wait_for_timeout(300);assert set(['giveaway','ask','replie','randomizer','composer','settings','user-manager','playroom']).issubset(set(requests));print('PASS separate windows despite old saved preference; hidden controls, OBS links and ownership requests')
   browser.close()
 finally:server.shutdown();server.server_close()
