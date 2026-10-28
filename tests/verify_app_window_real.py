import os,sys,tempfile,threading,time
from pathlib import Path
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import win32gui,win32con,win32process
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
with tempfile.TemporaryDirectory(prefix='bp3-real-tools-') as folder:
 os.environ['LOCALAPPDATA']=folder;os.environ['BP3_EDITION']='lite'
 import launch_dev
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 profile=Path(folder)/'BroadcastPlayroom3'/'browser_profile';profile.mkdir(parents=True)
 def find(title):
  found=[]
  def cb(hwnd,_):
   if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd)==title:found.append(hwnd)
  win32gui.EnumWindows(cb,None);return found
 try:
  with sync_playwright() as p:
   ctx=p.chromium.launch_persistent_context(str(profile),executable_path=launch_dev.find_browser(),headless=False,args=['--app='+base+'/index.html','--no-first-run'])
   page=ctx.pages[0] if ctx.pages else ctx.new_page();page.goto(base+'/index.html');page.wait_for_timeout(500)
   with page.expect_popup() as op:page.locator('#btnRailSettings').click()
   settings=op.value;settings.wait_for_load_state();deadline=time.monotonic()+6
   while time.monotonic()<deadline:
    mains=find('Broadcast Playroom 3');wins=find('ตั้งค่าระบบ (Settings) - Broadcast Playroom 3')
    if len(mains)==len(wins)==1 and win32gui.GetWindow(wins[0],win32con.GW_OWNER)==mains[0]:break
    time.sleep(.1)
   assert len(mains)==len(wins)==1 and win32gui.GetWindow(wins[0],win32con.GW_OWNER)==mains[0]
   assert not (win32gui.GetWindowLong(wins[0],win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST)
   with page.expect_popup() as op:page.locator('#btnRailAsk').click()
   ask=op.value;ask.wait_for_load_state();deadline=time.monotonic()+5
   while time.monotonic()<deadline:
    wins=find('ASK Widget ตั้งคำถามโหวต - Broadcast Playroom 3')
    if len(wins)==1 and win32gui.GetWindow(wins[0],win32con.GW_OWNER)!=mains[0]:break
    time.sleep(.1)
   assert len(wins)==1 and win32gui.GetWindow(wins[0],win32con.GW_OWNER)!=mains[0];print('PASS actual app buttons: settings owned by app, ASK independent, no global topmost')
   ask.close();settings.close();ctx.close()
 finally:server.shutdown();server.server_close()
