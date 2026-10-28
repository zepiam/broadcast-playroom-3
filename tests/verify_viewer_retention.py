import os,sys,json,tempfile,threading,time
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='viewer-retention-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context();now=int(time.time()*1000);person={'username':'Tester','platform':'Twitch','count':9,'isVip':True,'lastSeen':now,'history':[{'event':'message','time':now-8*86400000,'text':'old'},{'event':'message','time':now-6*86400000,'text':'recent'},{'event':'sub','time':now-9*86400000,'text':'activity'},{'event':'message','text':'unknown time'}]};context.add_init_script('localStorage.setItem("bp3_user_roster",'+json.dumps(json.dumps([person]))+')');page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.wait_for_function("JSON.parse(localStorage.getItem('bp3_user_roster'))[0].history.length===3");data=page.evaluate("JSON.parse(localStorage.getItem('bp3_user_roster'))[0]");assert [x['text'] for x in data['history']]==['recent','activity','unknown time'] and data['count']==9 and data['isVip'];print('PASS expired viewer chat removed; recent chat, activity and viewer data preserved');browser.close()
 finally:server.shutdown();server.server_close()
