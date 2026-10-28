import sys,tempfile,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from clip_markers import ClipMarkers
class Fake:
 active=True;seconds=10
 def __init__(self,**args):self.base_client=types.SimpleNamespace(ws=types.SimpleNamespace(close=lambda:None))
 def get_stream_status(self):return types.SimpleNamespace(output_active=self.active,output_timecode=f'00:00:{self.seconds:02d}.000')
 def get_record_status(self):return types.SimpleNamespace(output_active=False)
sys.modules['obsws_python']=types.SimpleNamespace(ReqClient=Fake)
with tempfile.TemporaryDirectory() as tmp:
 service=ClipMarkers(Path(tmp));service.configure('localhost',4455,'');service.update_stream(True)
 assert service.mark()['ok'];Fake.seconds=20;assert service.mark()['ok']
 path=Path(tmp)/'clip_markers.txt';text=path.read_text(encoding='utf-8');assert text.count('Live Session:')==1 and '[00:00:10]' in text and '[00:00:20]' in text
 service.update_stream(False);Fake.seconds=3;service.update_stream(True);assert service.mark()['ok'];assert path.read_text(encoding='utf-8').count('Live Session:')==2
 service.action('clear');Fake.seconds=4;assert service.mark()['ok'];assert path.read_text(encoding='utf-8').count('Live Session:')==1
 Fake.active=False;assert not service.mark()['ok'];assert path.read_text(encoding='utf-8').count('Live Session:')==1
 print('PASS live session marker header, stop/start, clear and idle with fake OBS')
