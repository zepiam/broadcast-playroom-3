"""Promote verified repaired core to v3.3 patches. GitHub only."""
import base64,hashlib,json,subprocess,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'version.json').read_text(encoding='utf-8'))
manifest.update(version='3.3',published_at='2026-10-31',changelog='- Broadcast Playroom v3.3\n- แก้ปุ่มและหน้าตั้งค่าใช้งานไม่ได้\n- จำค่าช่องและแพลตฟอร์มที่ซ่อน\n- ป้องกันข้อความเก่าเล่นซ้ำเมื่อเพิ่ม Chat Widget\n- ปรับการส่งบันทึก Composer ขณะปิดหน้า\n- แพตช์ซ่อมสำหรับผู้ใช้ 3.1 และ 3.2')
patches=[]
for edition in ('Lite','Full'):
 old=root/'build_trials'/('BroadcastPlayroom3-'+edition+'-Patch-3.2.zip')
 path=root/'build_trials'/('BroadcastPlayroom3-'+edition+'-Patch-3.3.zip')
 version=json.dumps({'product':'broadcast-playroom-3','version':'3.3','build_type':edition.lower()},indent=2).encode()
 with zipfile.ZipFile(old) as source,zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as target:
  for entry in source.infolist():
   if entry.filename not in ('version.json','_internal/version.json'):target.writestr(entry,source.read(entry))
  for name in ('version.json','_internal/version.json'):target.writestr(name,version)
 with zipfile.ZipFile(path) as check:
  assert check.testzip() is None
  for name in ('version.json','_internal/version.json'):assert json.loads(check.read(name))['version']=='3.3'
 digest=hashlib.sha256(path.read_bytes()).hexdigest()
 manifest[edition.lower()]={'type':'patch','url':'https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.3/'+path.name,'size':path.stat().st_size,'sha256':digest}
 patches.append(path);print('Validated',path.name,path.stat().st_size,flush=True)
folder=root/'build_trials/patch-publish-3.3';folder.mkdir(exist_ok=True)
staged=folder/'version.json';staged.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
notes=folder/'notes.md';notes.write_text(manifest['changelog'],encoding='utf-8')
def gh(*args,**kwargs):return subprocess.check_output(['gh',*args],**kwargs).decode('utf-8')
gh('release','create','v3.3','--repo','zepiam/broadcast-playroom-3','--draft','--title','Broadcast Playroom v3.3','--notes-file',str(notes))
for path in [*patches,staged]:gh('release','upload','v3.3',str(path),'--repo','zepiam/broadcast-playroom-3')
gh('release','edit','v3.3','--repo','zepiam/broadcast-playroom-3','--draft=false','--latest')
current=json.loads(gh('api','repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload={'message':'Publish GitHub repair patches v3.3 for installed v3.2 clients','sha':current['sha'],'content':base64.b64encode(staged.read_bytes()).decode(),'branch':'master'}
result=json.loads(gh('api','--method','PUT','repos/zepiam/broadcast-playroom-3/contents/version.json','--input','-',input=json.dumps(payload).encode()))
(root/'version.json').write_bytes(staged.read_bytes())
print('Published v3.3 commit',result['commit']['sha'],flush=True)
