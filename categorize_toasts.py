import sys, re
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

matches = re.findall(r'showToast\((.*?)\)', c)

categories = {
    "1. การคลิกปุ่มทั่วไป / สลับโหมด UI เล็กๆ น้อยๆ (ที่รกสายตา มักไม่จำเป็นต้องแจ้ง)": [],
    "2. การสลับเสียง / สไลเดอร์ / ปุ่มลัดบนแถบ (กดบ่อย ไม่ควรแจ้งเตือนทุกครั้ง)": [],
    "3. การส่งข้อความแชท / แชทไหล / ข้อความจำลอง": [],
    "4. การคัดลอกลิงก์ / การคลิกขวาซ่อนปุ่ม / จัดลำดับ": [],
    "5. การทำงานของเครื่องมือสด (ASK, Giveaway, Playroom, Clip Marker)": [],
    "6. การตั้งค่าระบบสำคัญ (Defender, DNS, OBS Dock, บันทึกการตั้งค่า, เชื่อมต่อบัญชี)": []
}

for m in matches:
    clean = m.strip().strip("'\"`")
    if any(k in clean for k in ['Game Overlay', 'Overlay+', 'สลับโหมด', 'แปลภาษา', 'สลับการแสดง', 'แยกหน้าต่าง']):
        categories["1. การคลิกปุ่มทั่วไป / สลับโหมด UI เล็กๆ น้อยๆ (ที่รกสายตา มักไม่จำเป็นต้องแจ้ง)"].append(clean)
    elif any(k in clean for k in ['คืนค่าสไลเดอร์', 'สลับโมเดลเสียง', 'ระดับเสียง', 'อ่านแชท']):
        categories["2. การสลับเสียง / สไลเดอร์ / ปุ่มลัดบนแถบ (กดบ่อย ไม่ควรแจ้งเตือนทุกครั้ง)"].append(clean)
    elif any(k in clean for k in ['จำลองแชท', 'ส่งข้อความไปยัง', 'แชท']):
        categories["3. การส่งข้อความแชท / แชทไหล / ข้อความจำลอง"].append(clean)
    elif any(k in clean for k in ['คัดลอก', 'ซ่อนปุ่ม', 'คืนค่า', 'ปักหมุด', 'จัดลำดับ']):
        categories["4. การคัดลอกลิงก์ / การคลิกขวาซ่อนปุ่ม / จัดลำดับ"].append(clean)
    elif any(k in clean for k in ['โพล', 'Giveaway', 'Playroom', 'คลิป', 'มาร์กช็อต', 'Preset', 'Replie', 'คำสั่ง']):
        categories["5. การทำงานของเครื่องมือสด (ASK, Giveaway, Playroom, Clip Marker)"].append(clean)
    else:
        categories["6. การตั้งค่าระบบสำคัญ (Defender, DNS, OBS Dock, บันทึกการตั้งค่า, เชื่อมต่อบัญชี)"].append(clean)

for cat, items in categories.items():
    print(f"\n### {cat} (รวม {len(items)} รายการ):")
    for item in items[:15]:
        print(f"  - {item}")
    if len(items) > 15:
        print(f"  ... และอื่นๆ อีก {len(items)-15} รายการ")
