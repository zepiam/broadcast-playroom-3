import sys,tempfile,threading,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import launch_dev
server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/api/tts?text=original'
seen=[]
try:
 with patch.object(launch_dev.dict_manager,'apply_replace',return_value='changed'),patch.object(launch_dev.tts_service,'generate_audio_bytes',side_effect=lambda text,*args: seen.append(text) or b'audio'),patch.object(launch_dev.rvc_service,'convert',return_value=(b'converted','audio/wav')) as rvc:
  with urllib.request.urlopen(url+'&preview=1') as response: assert response.read()==b'audio' and response.headers.get_content_type()=='audio/mpeg'
  assert seen==['original'] and not rvc.called
  with urllib.request.urlopen(url) as response: assert response.read()==b'converted'
  assert seen==['original','changed'] and rvc.called
 with patch.object(launch_dev.dict_manager,'_words',{'55@':'ฮ่าๆ'}),patch.object(launch_dev.tts_service,'generate_audio_bytes',side_effect=lambda text,*args:seen.append(text) or b'audio'),patch.object(launch_dev.rvc_service,'convert',return_value=(b'audio','audio/mpeg')):
  with urllib.request.urlopen(url.replace('original','555555')) as response:assert response.read()==b'audio'
  assert seen[-1]=='ฮ่าๆ'
 with patch.object(launch_dev.tts_service,'generate_audio_bytes',return_value=b'edge-original'),patch.object(launch_dev.rvc_service,'convert',side_effect=RuntimeError('simulated RVC error')):
  with urllib.request.urlopen(url) as response:assert response.read()==b'edge-original' and response.headers.get_content_type()=='audio/mpeg'
 print('PASS preview bypasses dictionary and RVC while standard TTS remains unchanged')
finally:server.shutdown();server.server_close()
