# HANDOFF.md — Broadcast Playroom 3 (v3.13)

## สถานะปัจจุบัน (Current Status)
- **เวอร์ชันล่าสุด:** v3.13 (ปล่อยอัปเดตอย่างเป็นทางการบน GitHub Releases เรียบร้อยแล้ว)
- **ผู้รับผิดชอบหลัก:** Antigravity (Google DeepMind)
- **การทดสอบความถูกต้อง (Production Verification):**
  - **Universal Auto-Save:** ผ่าน 100% (Game Overlay, Overlay+, Giveaway, Widget Customizer, OBS, TTS)
  - **Header Cleanup:** ผ่าน 100% (ไม่มีแถบหัวข้อซ้ำซ้อนในหน้าต่างย่อยทุกหน้าต่าง แคนวาส Composer Studio ขยายเต็มตา)
  - **Platform Settings Persistence:** ผ่าน 100% (`platform_settings.json` เป็น Source of Truth กู้คืนอัตโนมัติ ไม่สูญหาย)
  - **Live Update GitHub Tag Verification:** ตรวจพบ `v3.13` ล่าสุด 100%

---

## เครื่องมือตรวจสอบความเปลี่ยนแปลงประจำตัว (Dedicated Inspection Tool)
ทุกครั้งที่เริ่มต้นเซสชันใหม่ หรือหลัง `git pull`:
```bash
python inspect_changes.py [commit_ref]
```
- ตรวจสอบไฟล์ที่เปลี่ยนแปลงแยกตามหมวดหมู่ (Frontend HTML, CSS, JS, Python Backend, Config)
- ตรวจสอบฟังก์ชันหรือหัวข้อที่ถูกกระทบอย่างเจาะจง
- ใช้ `git diff <commit> <file>` เพื่อตรวจสอบโค้ดเฉพาะจุด ไม่รื้อระบบเดิมโดยไม่จำเป็น

---

## สรุปการแก้ไขล่าสุด (v3.11 – v3.13)
1. **v3.11:** แก้ไขปุ่ม "ปิดหน้าต่าง" และ "พับเก็บ" ด้านล่างของทุกหน้าต่างแยก (Popout Windows) ให้สั่งปิด Pywebview ได้อย่างสมบูรณ์แบบ
2. **v3.12:** นำแถบหัวข้อและคำอธิบายซ้ำซ้อน 2 บรรทัดออกจากทุกหน้าต่าง และขยายแคนวาส Composer Studio
3. **v3.13:** อัปเกรดระบบ Universal Auto-Save ทั่วทั้งโปรแกรม และล็อกไฟล์การตั้งค่าแพลตฟอร์มบนเครื่องให้เป็น Source of Truth ถาวร ไม่สูญหายเมื่ออัปเดต
