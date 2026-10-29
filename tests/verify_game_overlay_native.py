"""Native Qt smoke test with an isolated layout; no OBS or real chat."""
import ctypes, os, sys, tempfile, threading, time
from ctypes import wintypes
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
os.environ['BP3_EDITION']='lite'
import launch_dev

with tempfile.TemporaryDirectory(prefix='bp3-native-game-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}], 'legacyTools':{'game_overlay_width':350,'game_overlay_height':220,'viewer_overlay_width':400,'viewer_overlay_height':80}})
 service=launch_dev.desktop_overlays;service._ensure_hotkeys=lambda *args:None
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 def wait_ready(kind):
  deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   matches=[item for item in service.snapshot()['instances'] if item['kind']==kind and item.get('ready')]
   if matches:return matches[0]
   time.sleep(.1)
  raise RuntimeError(kind+' native window did not become ready')
 try:
  service.act('toggle','game',base);game=wait_ready('game')
  native=service.instances[game['id']];service.command(native,'set_size',width=430,height=260)
  rect=wintypes.RECT();deadline=time.monotonic()+5
  while time.monotonic()<deadline:
   ctypes.windll.user32.GetWindowRect(game['hwnd'],ctypes.byref(rect))
   if rect.right-rect.left==430 and rect.bottom-rect.top==260:break
   time.sleep(.1)
  else:raise RuntimeError('Native Game Overlay did not resize')
  service.act('demo','game',base);assert service.snapshot()['instances'][0]['demo_running']
  service.act('demo','game',base);assert not service.snapshot()['instances'][0]['demo_running']
  service.act('edit','game',base)
  service.act('toggle','viewer',base);viewer=wait_ready('viewer')
  service.act('edit','viewer',base)
  service.act('stop','viewer',base);service.act('stop','game',base)
  assert not service.snapshot()['instances']
  print('PASS actual Qt Game/Viewer start and stop, Game resize, edit commands and demo toggles')
 finally:
  service.stop();server.shutdown();server.server_close()
