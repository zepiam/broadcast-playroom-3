import sys,time,tempfile,base64,types,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from obs_connection import ObsConnection
from obs_scene_info import dock_scene
from clip_markers import ClipMarkers
class Fake:
 scene='A'; enabled=True; active=False; online=True; nested=False
 def __init__(self,**kw):
  if not self.online:raise RuntimeError('offline')
  self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_version(self):return types.SimpleNamespace()
 def get_input_list(self):return types.SimpleNamespace(inputs=[])
 def get_current_program_scene(self):return types.SimpleNamespace(current_program_scene_name=self.scene)
 def get_scene_item_list(self,name):
  if self.nested:
   return types.SimpleNamespace(scene_items=([{'sourceName':'G','isGroup':True,'sceneItemEnabled':self.enabled},{'sourceName':'Inner','sourceType':'OBS_SOURCE_TYPE_SCENE','sceneItemEnabled':True}] if name in ('A','B') else [{'sourceName':'A','sourceType':'OBS_SOURCE_TYPE_SCENE','sceneItemEnabled':True}]))
  return types.SimpleNamespace(scene_items=[{'inputKind':'browser_source','sceneItemEnabled':self.enabled,'sourceName':'BP3'},{'inputKind':'browser_source','sceneItemEnabled':True,'sourceName':'Other'}])
 def get_group_scene_item_list(self,name):return types.SimpleNamespace(scene_items=[{'sourceName':'BP3','inputKind':'browser_source','sceneItemEnabled':True}])
 def get_input_settings(self,name):return types.SimpleNamespace(input_settings={'url':'http://localhost:8801/?p=2' if name=='BP3' else 'https://example.com:8801/'})
 def get_stream_status(self):return types.SimpleNamespace(output_active=self.active,output_timecode='00:00:10.000',output_duration=10000)
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=Fake)
enc=lambda b:base64.b64encode(b);dec=lambda b:base64.b64decode(b)
def wait(predicate):
 for _ in range(150):
  if predicate():return
  time.sleep(.02)
 raise AssertionError('timeout')
with tempfile.TemporaryDirectory() as tmp:
 svc=ObsConnection(Path(tmp)/'config',ClipMarkers(Path(tmp)/'markers'),enc,dec,.05)
 try:
  svc.save({'enabled':True,'host':'localhost','port':4455,'password':''})
  wait(lambda:svc.public()['scene'].get('scene_name')=='A')
  info=svc.public();assert len(info['scene']['sources'])==1 and info['scene']['sources'][0]['pinned_page']=='2'
  layout={'activePageId':'a','pages':[{'id':'a','name':'Alpha','widgets':[]},{'id':'b','name':'Beta','widgets':[{'id':'w','type':'clock'}]}]}
  view=dock_scene(layout,info['scene']);assert view['sources'][0]['display_page_id']=='b' and view['sources'][0]['widgets'][0]['id']=='w' and layout['activePageId']=='a'
  Fake.scene='B';Fake.active=True;wait(lambda:svc.public()['scene']['scene_name']=='B' and svc.public()['stream']['active'])
  Fake.nested=True;wait(lambda:svc.public()['scene']['has_overlay']);assert svc.public()['scene']['sources'][0]['source_name']=='BP3'
  Fake.enabled=False;wait(lambda:not svc.public()['scene']['has_overlay'])
  Fake.online=False;wait(lambda:svc.public()['state']=='waiting');assert not svc.public()['scene']['connected']
  print('PASS OBS scene/source, pinned page, stream state, nested group, cycles, disabled source and disconnect (fake OBS)')
 finally:svc.stop()
