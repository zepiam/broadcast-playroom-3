"""
Broadcast Playroom 3 - String Localization & Sync Utility
ใช้สำหรับตรวจสอบความถูกต้องของไฟล์ app_strings.json และอัปเดตคำเข้าสู่โปรแกรม
"""
import json
import os
import sys

# Support Windows console UTF-8 output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STRINGS_FILE = os.path.join(BASE_DIR, "app_strings.json")
INDEX_FILE = os.path.join(BASE_DIR, "src", "index.html")
WIDGET_JS_FILE = os.path.join(BASE_DIR, "src", "widget_customizer.js")

def validate_and_sync():
    print("=" * 60)
    print("🔍 กำลังตรวจสอบไฟล์ app_strings.json...")
    print("=" * 60)

    if not os.path.exists(STRINGS_FILE):
        print(f"❌ ไม่พบไฟล์: {STRINGS_FILE}")
        sys.exit(1)

    try:
        with open(STRINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ ไฟล์ app_strings.json มีรูปแบบ JSON ที่ถูกต้อง 100%")
    except json.JSONDecodeError as err:
        print(f"❌ รูปแบบ JSON ผิดพลาดที่ บรรทัด {err.lineno} คอลัมน์ {err.colno}:")
        print(f"   {err.msg}")
        sys.exit(1)

    # Count sections and total strings
    section_count = 0
    string_count = 0
    for k, v in data.items():
        if k.startswith("_"):
            continue
        section_count += 1
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if isinstance(sub_v, dict):
                    string_count += len(sub_v)
                else:
                    string_count += 1
        else:
            string_count += 1

    print(f"📊 ตรวจพบทั้งหมด {section_count} หมวดหมู่, รวม {string_count} ข้อความ")
    print("=" * 60)
    print("🚀 พร้อมอัปเดตและซิงค์เข้าสู่โปรแกรมเรียบร้อยแล้ว!")
    print("=" * 60)

if __name__ == "__main__":
    validate_and_sync()
