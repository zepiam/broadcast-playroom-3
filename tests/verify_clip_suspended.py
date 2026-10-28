import os,sys,tempfile,threading,requests
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}]});launch_dev.clip_markers.folder=Path(tmp)/'marker';launch_dev.clip_markers.folder.mkdir();marker=launch_dev.clip_markers.folder/'clip_markers.txt';marker.write_text('keep',encoding='utf-8')
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  assert requests.post(base+'/api/clip-markers',json={'action':'clear'}).status_code==410;assert requests.post(base+'/api/clip-hotkey',json={'shortcut':'f9'}).status_code==410;assert requests.get(base+'/api/clip-hotkey/status').json()['suspended'];assert marker.read_text(encoding='utf-8')=='keep'
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page();page.goto(base+'/index.html');assert not page.locator('[data-item-id="clip-marker"]').is_visible();assert 'clip_hotkey.start()' not in __import__('inspect').getsource(launch_dev.main);browser.close()
  print('PASS clip marker hidden, endpoints suspended, no hotkey start, history unchanged')
 finally:server.shutdown();server.server_close()
