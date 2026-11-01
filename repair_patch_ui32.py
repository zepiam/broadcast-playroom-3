import json,zipfile,os,hashlib,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
report_path=root/'build_trials/patch-report-3.2.json'
report=json.loads(report_path.read_text())
for edition,data in report.items():
 path=Path(data['file']);backup=path.with_suffix('.before-ui-fix.zip')
 if not backup.exists():shutil.copy2(path,backup)
 temporary=path.with_suffix('.ui-fixed.zip')
 with zipfile.ZipFile(path) as old,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as new:
  for entry in old.infolist():
   if not entry.filename.startswith('_internal/dist/'):new.writestr(entry,old.read(entry))
  for source in (root/'dist').rglob('*'):
   if source.is_file() and not source.name.startswith('shout_'):new.write(source,'_internal/dist/'+source.relative_to(root/'dist').as_posix())
 os.replace(temporary,path)
 with zipfile.ZipFile(path) as archive:
  assert archive.testzip() is None
  data['entries']=archive.namelist()
 data['size']=path.stat().st_size;data['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 print('Updated',edition,'UI patch',data['size'],flush=True)
report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
