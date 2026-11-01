"""Publish explicitly authorized v3.2 repair, artifacts first, manifest last."""
raise SystemExit('DISABLED: user requires GitHub update patches only. Use publish_update_patches_32.py; do not modify Hugging Face installers.')
import base64,hashlib,json,subprocess,zipfile,os
from pathlib import Path
from huggingface_hub import HfApi,CommitOperationAdd
root=Path(__file__).resolve().parent
artifacts={e:root/'build_trials'/('repair-'+e.capitalize()+'.zip') for e in ('lite','full')}
manifest=json.loads((root/'version.json').read_text(encoding='utf-8'))
for edition,path in artifacts.items():
 with zipfile.ZipFile(path) as archive:
  assert archive.testzip() is None
  assert json.loads(archive.read('version.json'))['version']=='3.2'
  assert json.loads(archive.read('_internal/version.json'))['version']=='3.2'
 digest=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
 manifest[edition]['sha256']=digest.hexdigest();manifest[edition]['size']=path.stat().st_size
manifest['published_at']='2026-10-31'
publish_dir=root/'build_trials'/'repair-publish';publish_dir.mkdir(exist_ok=True)
staged=publish_dir/'version.json'
staged.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified archives and hashes',flush=True)
api=HfApi()
result=api.create_commit(repo_id='men9ch/broadcast-playroom-3',repo_type='model',commit_message='Repair v3.2 frozen backend and version display',operations=[CommitOperationAdd(path_in_repo='BroadcastPlayroom3-'+e.capitalize()+'.zip',path_or_fileobj=str(p)) for e,p in artifacts.items()])
print('HF artifact commit:',result.oid,flush=True)
def gh(*args,**kwargs):return subprocess.check_output(['gh',*args],**kwargs).decode('utf-8')
lite_upload=publish_dir/'BroadcastPlayroom3-Lite.zip'
if not lite_upload.exists():os.link(artifacts['lite'],lite_upload)
gh('release','upload','v3.2',str(lite_upload),'--repo','zepiam/broadcast-playroom-3','--clobber')
gh('release','upload','v3.2',str(staged),'--repo','zepiam/broadcast-playroom-3','--clobber')
current=json.loads(gh('api','repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload={'message':'Repair v3.2 update manifest with verified archive hashes','sha':current['sha'],'content':base64.b64encode(staged.read_bytes()).decode('ascii'),'branch':'master'}
response=gh('api','--method','PUT','repos/zepiam/broadcast-playroom-3/contents/version.json','--input','-',input=json.dumps(payload).encode('utf-8'))
print('GitHub manifest commit:',json.loads(response)['commit']['sha'],flush=True)
(root/'version.json').write_bytes(staged.read_bytes())
print('Publication complete',flush=True)
