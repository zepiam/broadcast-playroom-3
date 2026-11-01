"""Publish v3.4 with current verified frontend and rebuilt core. GitHub only."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
# Reuse the validated archive checks and draft-first publication workflow.
subprocess.run([sys.executable,str(root/'repair_patch_ui32.py')],cwd=root,check=True)
publisher=(root/'publish_patch_33.py').read_text(encoding='utf-8')
publisher=publisher.replace('3.3','3.4')
publisher=publisher.replace('- แพตช์ซ่อมสำหรับผู้ใช้ 3.1 และ 3.2','- แก้บันทึกการเชื่อมต่ออัตโนมัติจาก Settings แยกหน้าต่าง\\n- รอโหลดชื่อช่องก่อนเริ่มเชื่อมต่อ\\n- แพตช์ซ่อมสำหรับผู้ใช้ 3.1–3.3')
exec(compile(publisher,str(root/'publish_patch_33.py'),'exec'),{'__file__':str(root/'publish_patch_33.py'),'__name__':'__main__'})
