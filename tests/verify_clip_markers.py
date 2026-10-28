import sys,tempfile,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from clip_markers import ClipMarkers
class Fake:
 active=False
 record=False
 def __init__(self,**kwargs): self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_stream_status(self): return types.SimpleNamespace(output_active=self.active,output_timecode='00:03:00.000')
 def get_record_status(self): return types.SimpleNamespace(output_active=self.record,output_timecode='00:04:00.000')
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=Fake)
with tempfile.TemporaryDirectory() as tmp:
 service=ClipMarkers(Path(tmp)/'data');assert not service.mark()['ok'];service.configure('localhost',4455,'')
 assert not service.mark()['ok'];assert not (service.folder/'clip_markers.txt').exists()
 Fake.record=True;assert service.mark()['timecode']=='00:04:00';assert '[00:04:00]' in (service.folder/'clip_markers.txt').read_text(encoding='utf8')
 print('PASS inactive OBS refuses file; recording timecode stored')
