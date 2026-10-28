import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='topbar-visibility-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1600,'height':900});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   for key in ['translate','overlay','game-overlay','overlay-plus']:
    item=page.locator('#topbar-item-'+key);assert item.is_visible();item.click(button='right');page.locator('#topbarContextMenu button.danger').click();assert item.is_hidden();assert key in page.evaluate("JSON.parse(localStorage.getItem('bp3_topbar_hidden'))")
   print('PASS four buttons hide from actual context menu')
   page.reload();assert all(page.locator('#topbar-item-'+key).is_hidden() for key in ['translate','overlay','game-overlay','overlay-plus']);print('PASS hidden state persists after reload')
   for key in ['translate','overlay','game-overlay','overlay-plus']:
    page.locator('#topbarSortable').click(button='right',position={'x':1,'y':1});page.locator('#topbarContextMenu button').filter(has=page.locator('span',has_text={'translate':'แปลภาษา','overlay':'🖥️ Overlay','game-overlay':'Game Overlay','overlay-plus':'Overlay+'}[key])).first.click();assert page.locator('#topbar-item-'+key).is_visible()
   assert page.evaluate("JSON.parse(localStorage.getItem('bp3_topbar_hidden')).length===0");print('PASS four buttons restored from context menu')
   page.reload();assert all(page.locator('#topbar-item-'+key).is_visible() for key in ['translate','overlay','game-overlay','overlay-plus']);print('PASS restored state persists after reload')
   browser.close()
 finally:server.shutdown();server.server_close()
