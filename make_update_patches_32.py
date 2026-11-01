"""Build core-file deltas against local installed baselines; never include user data."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
report={}
for edition,trial,baseline in [('Lite','trial-20261031-020057-846402',root/'build_trials/lite/BroadcastPlayroom3-Lite'),('Full','trial-20261031-020611-244291',Path(r'E:\DOCS\Documents\BroadcastPlayroom3\full'))]:
 source=root/'build_trials'/trial/'dist'/('BroadcastPlayroom3-'+edition)
 output=root/'build_trials'/('BroadcastPlayroom3-'+edition+'-Patch-3.2.zip')
 included=[]
 with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as archive:
  for path in source.rglob('*'):
   if not path.is_file():continue
   relative=path.relative_to(source);name=relative.as_posix()
   if name=='build_receipt.json':continue
   if name.startswith('data/') or path.name in ('composer_layout.json','replace_words.json','bot_accounts.dat'):raise ValueError('User data in source')
   old=baseline/relative
   if name.endswith('version.json') or not old.is_file() or path.stat().st_size!=old.stat().st_size or digest(path)!=digest(old):
    archive.write(path,name);included.append(name)
 report[edition.lower()]={'file':str(output),'size':output.stat().st_size,'sha256':digest(output),'entries':included,'baseline':str(baseline)}
 print(edition,'patch bytes',output.stat().st_size,'files',len(included),flush=True)
(root/'build_trials/patch-report-3.2.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
