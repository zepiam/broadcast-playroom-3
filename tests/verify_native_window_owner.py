import os,sys,tempfile,threading,time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
import win32con,win32gui,win32process,psutil
import app_window_ownership as ownership
from launch_dev import find_browser
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  body=b'<html><head><title>Broadcast Playroom 3</title></head><body><button onclick="window.open(\'/child\',\'test\',\'width=500,height=400\')">open</button><script>if(location.pathname==="/child")document.title="Settings Test - Broadcast Playroom 3"</script></body></html>'
  self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(body)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
with tempfile.TemporaryDirectory(prefix='bp3-native-window-') as folder:
 old=os.environ.get('LOCALAPPDATA');os.environ['LOCALAPPDATA']=folder;profile=Path(folder)/'BroadcastPlayroom3'/'browser_profile';profile.mkdir(parents=True)
 try:
  with sync_playwright() as p:
   ctx=p.chromium.launch_persistent_context(str(profile),executable_path=find_browser(),headless=False,args=['--app=http://127.0.0.1:'+str(server.server_port)+'/','--no-first-run'])
   main=ctx.pages[0] if ctx.pages else ctx.new_page();main.goto('http://127.0.0.1:'+str(server.server_port)+'/');main.wait_for_timeout(500)
   with main.expect_popup() as opened:main.locator('button').click()
   child=opened.value;child.wait_for_load_state();child.wait_for_timeout(700)
   ownership.TITLES['test']='Settings Test';result=ownership.set_tool_owner('test',timeout=3);print('native owner result',result,flush=True);assert result.get('ok') and result.get('owned')
   ownership.FREE_WINDOWS=frozenset((*ownership.FREE_WINDOWS,'test'));result=ownership.set_tool_owner('test',timeout=2);print('native free-window result',result,flush=True);assert result.get('ok') and result.get('owned') is False
   child.close();ctx.close();print('PASS actual Windows browser owner and exception behavior',flush=True)
 finally:
  if old is None:os.environ.pop('LOCALAPPDATA',None)
  else:os.environ['LOCALAPPDATA']=old
  server.shutdown();server.server_close()
