import sys, json, time, os, io, contextlib, traceback
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
sys.dont_write_bytecode=True
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'work'/'compat-audit'/'rvc-smoke.json'
OUT.parent.mkdir(parents=True,exist_ok=True)
model=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'broadcast playroom dev/rvc_models/lumine-jp.pth'
started=time.time();engine=None;log=io.StringIO()
result={'model':model.name,'device':'cpu','real_weights':True,'downloaded_weights':False}
try:
 print('Loading existing real RVC model on CPU...',flush=True)
 with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
  import numpy as np
  from rvc_engine import RVCEngine
  engine=RVCEngine(str(model),device='cpu');engine.load()
 print('Model load returned; running real inference...',flush=True)
 with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
  samples=(.1*np.sin(2*np.pi*220*np.arange(16000)/16000)).astype(np.float32)
  converted,rate=engine.convert_array(samples,16000)
  result.update(loaded=engine.is_loaded,sample_rate=int(rate),output_samples=len(converted),finite=bool(np.isfinite(converted).all()),peak=float(np.max(np.abs(converted))))
  if not result['loaded'] or not result['finite'] or result['output_samples']==0 or result['peak']==0:raise RuntimeError('Empty or invalid RVC output')
 result['status']='PASS'
except Exception as error:
 result.update(status='FAIL',error=str(error),traceback=traceback.format_exc(),runtime_log=log.getvalue()[-6000:])
finally:
 if engine:
  with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):engine.unload()
 result['elapsed_seconds']=round(time.time()-started,2)
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if result['status']!='PASS':sys.exit(1)
