import json,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from clip_hotkey import ClipHotkey
class Keyboard:
 def __init__(self):self.hooks={};self.removed=[]
 def add_hotkey(self,key,callback,suppress=False):
  assert suppress is False
  if key=='bad':raise ValueError('invalid')
  token=object();self.hooks[token]=(key,callback);return token
 def remove_hotkey(self,token):self.removed.append(token);del self.hooks[token]
class Markers:
 def __init__(self):self.count=0
 def mark(self):self.count+=1;return {'ok':True,'message':'marked'}
with tempfile.TemporaryDirectory(prefix='bp3-keys-') as tmp:
 path=Path(tmp)/'keys.json';keys=Keyboard();markers=Markers();service=ClipHotkey(path,markers,keys);service.start()
 assert service.public()['active'] and service.public()['shortcut']=='f9'
 first=service.handle;keys.hooks[first][1]()
 for _ in range(100):
  if markers.count:break
  time.sleep(.01)
 assert markers.count==1 and service.public()['message']=='marked'
 service.set('ctrl+shift+m');assert first in keys.removed and json.loads(path.read_text())['shortcut']=='ctrl+shift+m'
 try:service.set('bad');raise AssertionError('invalid shortcut accepted')
 except ValueError:pass
 assert service.public()['shortcut']=='ctrl+shift+m' and service.public()['active']
 service.stop();assert not keys.hooks
 restored=ClipHotkey(path,markers,keys);restored.start();assert restored.public()['shortcut']=='ctrl+shift+m';restored.set('');assert not restored.public()['active'];restored.stop()
 print('PASS default F9, callback, replacement, validation, restart and disable')
