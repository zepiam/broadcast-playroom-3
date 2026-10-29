"""Windows hotkeys with an owned message loop and explicit unregister."""
import ctypes,threading
from ctypes import wintypes
class DesktopHotkey:
 def __init__(self,chord,callback):
  self.chord=chord.lower()
  parts=chord.lower().replace('control','ctrl').split('+');mods=0
  for part in parts[:-1]:
   if part not in {'ctrl':2,'shift':4,'alt':1,'win':8}:raise ValueError('Unsupported hotkey modifier')
   mods|={'ctrl':2,'shift':4,'alt':1,'win':8}[part]
  key=parts[-1].strip();vk=ord(key.upper()) if len(key)==1 and key.isalnum() else 0
  if key.startswith('f') and key[1:].isdigit() and 1<=int(key[1:])<=24:vk=0x70+int(key[1:])-1
  if not vk:raise ValueError('Unsupported hotkey key')
  self.ready=threading.Event();self.thread_id=0;self.error=None
  def run():
   user32=ctypes.windll.user32;self.thread_id=ctypes.windll.kernel32.GetCurrentThreadId();message=wintypes.MSG();user32.PeekMessageW(ctypes.byref(message),None,0,0,0)
   if not user32.RegisterHotKey(None,1,mods|0x4000,vk):self.error='คีย์ลัด '+chord+' ถูกใช้งานอยู่';self.ready.set();return
   self.ready.set()
   try:
    while user32.GetMessageW(ctypes.byref(message),None,0,0)>0:
     if message.message==0x0312:threading.Thread(target=callback,daemon=True).start()
   finally:user32.UnregisterHotKey(None,1)
  self.thread=threading.Thread(target=run,daemon=True);self.thread.start();self.ready.wait(3)
  if self.error:raise RuntimeError(self.error)
 def close(self):
  if self.thread.is_alive():ctypes.windll.user32.PostThreadMessageW(self.thread_id,0x0012,0,0);self.thread.join(timeout=2)
