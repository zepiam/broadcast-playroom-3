"""Authorized GitHub patch publication only. Does not modify Hugging Face."""
import base64,json,subprocess,zipfile,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
report=json.loads((root/'build_trials/patch-report-3.2.json').read_text())
manifest=json.loads((root/'version.json').read_text(encoding='utf-8'))
def gh(*args,**kwargs):return subprocess.check_output(['gh',*args],**kwargs).decode('utf-8')
for edition,data in report.items():
 path=Path(data['file'])
 with zipfile.ZipFile(path) as archive:
  assert archive.testzip() is None
  assert json.loads(archive.read('version.json'))['version']=='3.2'
  assert json.loads(archive.read('_internal/version.json'))['version']=='3.2'
 manifest[edition]={'type':'patch','url':'https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.2/'+path.name,'size':data['size'],'sha256':data['sha256']}
 gh('release','upload','v3.2',str(path),'--repo','zepiam/broadcast-playroom-3','--clobber')
 print('Uploaded patch',path.name,flush=True)
folder=root/'build_trials/patch-publish';folder.mkdir(exist_ok=True)
path=folder/'version.json';path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
gh('release','upload','v3.2',str(path),'--repo','zepiam/broadcast-playroom-3','--clobber')
current=json.loads(gh('api','repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload={'message':'Use GitHub delta patches for installed 3.1 to 3.2 updates','sha':current['sha'],'content':base64.b64encode(path.read_bytes()).decode(),'branch':'master'}
result=json.loads(gh('api','--method','PUT','repos/zepiam/broadcast-playroom-3/contents/version.json','--input','-',input=json.dumps(payload).encode()))
print('Patch manifest commit',result['commit']['sha'],flush=True)
(root/'version.json').write_bytes(path.read_bytes())
# Remove only the standalone Lite asset mistakenly uploaded by this repair session.
assets=json.loads(gh('release','view','v3.2','--repo','zepiam/broadcast-playroom-3','--json','assets'))['assets']
if any(a['name']=='BroadcastPlayroom3-Lite.zip' for a in assets):gh('release','delete-asset','v3.2','BroadcastPlayroom3-Lite.zip','--repo','zepiam/broadcast-playroom-3','--yes')
print('GitHub patch publication complete',flush=True)
