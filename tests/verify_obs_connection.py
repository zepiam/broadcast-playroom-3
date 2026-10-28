import sys,tempfile,time,types,base64
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from obs_connection import ObsConnection
from clip_markers import ClipMarkers
class Fake:
 online=False
 def __init__(self,**kwargs):
  if not self.online:raise RuntimeError('offline')
  self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_version(self):return types.SimpleNamespace(obs_version='test')
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=Fake)
enc=lambda value:b'protected:'+base64.b64encode(value)
dec=lambda value:base64.b64decode(value.removeprefix(b'protected:'))
def await_state(service,state):
 for _ in range(100):
  if service.public()['state']==state:return
  time.sleep(.02)
 raise AssertionError(service.public())
with tempfile.TemporaryDirectory(prefix='obs-config-') as tmp:
 path=Path(tmp)/'obs.dat'; clips=ClipMarkers(Path(tmp)/'data'); service=ObsConnection(path,clips,enc,dec,.05)
 try:
  service.save({'enabled':True,'host':'127.0.0.1','port':4455,'password':'private'})
  assert b'private' not in path.read_bytes();await_state(service,'waiting')
  Fake.online=True;await_state(service,'connected')
  Fake.online=False;await_state(service,'waiting')
  service.save({'enabled':True,'host':'127.0.0.1','port':4455,'password':''});assert dec(path.read_bytes()).find(b'private')>=0
  assert 'password' not in service.public()
 finally:service.stop()
 restored=ObsConnection(path,clips,enc,dec,.05)
 assert restored.public()['enabled'] and restored.public()['has_password'] and clips._connection[2]=='private'
 restored.save({'enabled':False,'host':'127.0.0.1','port':4455,'password':'','clear_password':True})
 assert clips._connection is None and not restored.public()['has_password'];restored.stop()
 print('PASS encrypted persistence, restart, retry, offline, disable and password clear')
