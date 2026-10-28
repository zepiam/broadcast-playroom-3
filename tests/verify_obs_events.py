import sys,tempfile,time,base64,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from obs_connection import ObsConnection
from clip_markers import ClipMarkers
class Req:
 scene='A';online=True
 def __init__(self,**kw):
  if not self.online:raise RuntimeError('offline')
  self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_version(self):return types.SimpleNamespace()
 def get_input_list(self):return types.SimpleNamespace(inputs=[])
 def get_current_program_scene(self):return types.SimpleNamespace(current_program_scene_name=self.scene)
 def get_scene_item_list(self,name):return types.SimpleNamespace(scene_items=[])
 def get_stream_status(self):return types.SimpleNamespace(output_active=False)
class Events:
 instances=[]
 def __init__(self,**kw):self.closed=False;self.handlers={};self.callback=types.SimpleNamespace(register=self.register);self.instances.append(self)
 def register(self,funcs):self.handlers={f.__name__:f for f in funcs}
 def unsubscribe(self):self.closed=True
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=Req,EventClient=Events)
enc=lambda b:base64.b64encode(b);dec=lambda b:base64.b64decode(b)
def wait(predicate,timeout=3):
 until=time.monotonic()+timeout
 while time.monotonic()<until:
  if predicate():return
  time.sleep(.01)
 raise AssertionError('timeout')
with tempfile.TemporaryDirectory() as tmp:
 service=ObsConnection(Path(tmp)/'settings',ClipMarkers(Path(tmp)/'data'),enc,dec,5)
 try:
  service.save({'enabled':True,'host':'localhost','port':4455,'password':''});wait(lambda:service.public()['scene']['scene_name']=='A' and Events.instances)
  Req.scene='B';Events.instances[0].handlers['on_current_program_scene_changed'](None)
  wait(lambda:service.public()['scene']['scene_name']=='B',.7)
  service.save({'enabled':False,'host':'localhost','port':4455,'password':''});wait(lambda:Events.instances[0].closed);wait(lambda:not service.public()['scene']['connected'])
  print('PASS OBS scene event wakes polling promptly and unsubscribes on disable')
 finally:service.stop()
