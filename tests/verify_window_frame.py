"""Exercise native window actions on a disposable Windows fixture, not user windows."""
import sys,os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import win32gui,win32con,psutil
from app_window_frame import action
hwnd=win32gui.CreateWindowEx(0,'STATIC','Broadcast Playroom 3',win32con.WS_OVERLAPPEDWINDOW|win32con.WS_VISIBLE,100,100,600,400,0,0,0,None)
profile=str(Path(os.environ['LOCALAPPDATA'])/'BroadcastPlayroom3'/'browser_profile')
class FixtureProcess:
 def name(self):return 'chrome.exe'
 def cmdline(self):return ['chrome.exe','--user-data-dir='+profile]
try:
 with patch.object(win32gui,'EnumWindows',side_effect=lambda callback,data:callback(hwnd,data)),patch.object(psutil,'Process',return_value=FixtureProcess()):
  assert action('init')['ok']
  assert action('maximize')['ok']
  assert win32gui.GetWindowPlacement(hwnd)[1]==win32con.SW_SHOWMAXIMIZED
  assert action('maximize')['ok']
  assert win32gui.GetWindowPlacement(hwnd)[1]!=win32con.SW_SHOWMAXIMIZED
  print('PASS native init, maximize and restore on disposable Windows fixture')
finally:win32gui.DestroyWindow(hwnd)
