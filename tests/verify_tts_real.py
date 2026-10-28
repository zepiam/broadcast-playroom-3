import sys,threading,json,time,urllib.request,urllib.parse,io
from pathlib import Path
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
import launch_dev
from rvc_service import RVCService
import soundfile as sf
out=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'work'/'compat-audit'
out.mkdir(parents=True,exist_ok=True)
launch_dev.rvc_service=RVCService(edition='lite')
server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
result={'service':'production /api/tts, actual Edge synthesis','text':'ทดสอบระบบอ่านแชท','generated_audio':True}
try:
 text=urllib.parse.quote(result['text'])
 with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/api/tts?text={text}&gender=female',timeout=60) as response:
  audio=response.read();result['content_type']=response.headers.get('Content-Type')
 info=sf.info(io.BytesIO(audio))
 assert info.frames>0 and info.duration>0
 result.update(status='PASS',bytes=len(audio),sample_rate=info.samplerate,duration=info.duration)
 (out/'tts-real.mp3').write_bytes(audio)
except Exception as error:result.update(status='FAIL',error=str(error))
finally:
 server.shutdown();server.server_close();(out/'tts-real.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False),flush=True)
