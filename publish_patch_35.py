"""Publish v3.5 with current verified frontend and rebuilt core. GitHub only."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
# Reuse the validated archive checks and draft-first publication workflow.
subprocess.run([sys.executable,str(root/'repair_patch_ui32.py')],cwd=root,check=True)
publisher=(root/'publish_patch_33.py').read_text(encoding='utf-8')
publisher=publisher.replace('3.3','3.5')
publisher=publisher.replace('- แพตช์ซ่อมสำหรับผู้ใช้ 3.1 และ 3.2','- เฟรมหน้าต่างสไตล์ Discord/Spotify พร้อม Snap Assist & Snap Layouts ของ Windows 11\\n- เพิ่มความเร็วในการเปิดโปรแกรมเร็วขึ้นกว่า 13 เท่า (จาก 13.1 วินาที เหลือ 0.96 วินาที)\\n- หน้าต่างเครื่องมือแยกเปิดตรงเข้าสู่เครื่องมือทันที ไม่แวบหน้าแรก และไม่มีแถบ address bar\\n- แก้ปัญหาลากหน้าต่างแล้วหลุดค้างตามเมาส์ และรองรับการขยายขอบหน้าต่างแบบ Native\\n- ป้องกันการเปิดหน้าต่างเครื่องมือซ้ำซ้อน สลับไปยังหน้าต่างเดิมที่เปิดอยู่ทันที\\n- ปรับปรุงความเสถียรและประสิทธิภาพระบบโดยรวม')
exec(compile(publisher,str(root/'publish_patch_33.py'),'exec'),{'__file__':str(root/'publish_patch_33.py'),'__name__':'__main__'})
