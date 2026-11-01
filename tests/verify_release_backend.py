"""Isolated frozen-backend version smoke test; no update installation/publication."""
import json,os,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
exe=Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix='bp3-release-check-') as tmp:
 env=dict(os.environ,LOCALAPPDATA=tmp,USERPROFILE=tmp,HOME=tmp)
 with (Path(tmp)/'backend.log').open('w',encoding='utf-8') as log:
  process=subprocess.Popen([str(exe),'--headless','--no-splash'],cwd=tmp,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  try:
   for attempt in range(90):
    if process.poll() is not None:raise RuntimeError((Path(tmp)/'backend.log').read_text(encoding='utf-8',errors='replace')[-2500:])
    try:
     with urllib.request.urlopen('http://127.0.0.1:8801/api/app-instance',timeout=1) as response:state=json.load(response)
     if state.get('edition')==('full' if 'full' in exe.name.lower() else 'lite'):break
    except OSError:pass
    time.sleep(1)
   else:raise RuntimeError('Backend startup timeout')
   assert json.loads((exe.parent/'version.json').read_text(encoding='utf-8'))['version']=='3.2'
   with urllib.request.urlopen('http://127.0.0.1:8801/api/version',timeout=3) as response:version=json.load(response)
   assert version['version']=='3.2',version
   print('PASS frozen backend started; runtime version=3.2; instance:',state)
   if os.environ.get('BP3_UI_CHECK')=='1':subprocess.run([sys.executable,str(Path(__file__).with_name('diagnose_installed_ui.py'))],check=True)
  finally:
   process.terminate()
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.kill();process.wait()
