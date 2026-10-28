import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','name':'Alpha','widgets':[]},{'id':'b','name':'Beta','widgets':[{'id':'w','type':'clock','title':'Other scene clock','x':0,'y':0,'width':200,'height':80}]}]})
 launch_dev.obs_connection.public=lambda:{'scene':{'connected':True,'scene_name':'Scene B','has_overlay':True,'sources':[{'source_name':'Source B','is_pinned':True,'pinned_page':'2'}]},'stream':{'active':True,'timecode':'00:01:00','duration_ms':60000}}
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/dock.html');page.locator('#txtPinnedPageName').filter(has_text='Beta').wait_for(timeout=10000);page.locator('#txtPinnedSceneDesc').filter(has_text='Scene B').wait_for();assert launch_dev.get_layout()['activePageId']=='a'
   print('PASS Dock shows current scene pinned page from simulated OBS without switching Composer');browser.close()
 finally:server.shutdown();server.server_close()
