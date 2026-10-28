import base64,sys,tempfile,time,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from obs_connection import ObsConnection
from clip_markers import ClipMarkers
class Fake:
 online=True;pressed=[]
 def __init__(self,**kwargs):
  if not self.online:raise RuntimeError('offline')
  self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_version(self):return types.SimpleNamespace(obs_version='fake')
 def get_input_list(self):return types.SimpleNamespace(inputs=[{'inputName':name,'inputKind':'browser_source'} for name in ['ours','old','dock','external','wrongport','wrongpath']]+[{'inputName':'camera','inputKind':'dshow_input'}])
 def get_input_settings(self,name):return types.SimpleNamespace(input_settings={'url':{'ours':'http://localhost:8801/?p=2','old':'http://127.0.0.1:8765/chat-widget','dock':'http://localhost:8801/dock.html','external':'https://example.com/','wrongport':'http://localhost:7777/','wrongpath':'http://localhost:8801/index.html'}[name]})
 def press_input_properties_button(self,name,prop):self.pressed.append((name,prop))
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=Fake)
with tempfile.TemporaryDirectory(prefix='bp3-obs-refresh-') as tmp:
 enc=lambda b:base64.b64encode(b);dec=lambda b:base64.b64decode(b)
 svc=ObsConnection(Path(tmp)/'obs.dat',ClipMarkers(Path(tmp)/'data'),enc,dec,.05,lambda:{8801,8765})
 try:
  svc.save({'enabled':True,'host':'localhost','port':4455,'password':''})
  for _ in range(100):
   if svc.public()['state']=='connected':break
   time.sleep(.02)
  assert set(Fake.pressed)=={('ours','refreshnocache'),('old','refreshnocache')}
  time.sleep(.2);assert len(Fake.pressed)==2
  svc.save({'enabled':True,'host':'localhost','port':4455,'password':''});time.sleep(.15);assert len(Fake.pressed)==2
  Fake.online=False
  for _ in range(100):
   if svc.public()['state']=='waiting':break
   time.sleep(.02)
  Fake.online=True
  for _ in range(100):
   if svc.public()['state']=='connected':break
   time.sleep(.02)
  assert len(Fake.pressed)==2
  print('PASS only matching local sources refresh once; unrelated and rapid reconnect untouched')
 finally:svc.stop()
