# HANDOFF.md — Broadcast Playroom 3 (v3.14)

## สถานะปัจจุบัน (Current Status)
- **เวอร์ชันล่าสุด:** v3.14 (ปล่อยอัปเดตอย่างเป็นทางการบน GitHub Releases เรียบร้อยแล้ว)
- **ผู้รับผิดชอบหลัก:** Antigravity (Google DeepMind)
- **การทดสอบความถูกต้อง (Production Verification):**
  - **Universal Auto-Save & Clean Buttons:** ผ่าน 100% (หน้าต่าง Settings และ Chat Settings นำปุ่มบันทึกซ้ำซ้อนออก เหลือเฉพาะปุ่ม "ปิดหน้าต่าง")
  - **Permanent Platform Settings Persistence:** ผ่าน 100% (ช่องทางสตรีม เช่น `men9ch` และสถานะติ๊ก Auto-Connect ไม่หาย 100% รองรับ Multi-path merge & real-time backup sync)
  - **Popout Settings Parity:** ผ่าน 100% (ทั้งหน้าต่างหลักและ Popout โหลดค่าช่องและเช็กบ็อกซ์จากฐานข้อมูลเรียลไทม์)
  - **Live Update GitHub Tag Verification:** ตรวจพบ `v3.14` ล่าสุด 100%

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

## สรุปการแก้ไขล่าสุด (v3.11 – v3.14)
1. **v3.11:** แก้ไขปุ่ม "ปิดหน้าต่าง" และ "พับเก็บ" ด้านล่างของทุกหน้าต่างแยก (Popout Windows) ให้สั่งปิด Pywebview ได้อย่างสมบูรณ์แบบ
2. **v3.12:** นำแถบหัวข้อและคำอธิบายซ้ำซ้อน 2 บรรทัดออกจากทุกหน้าต่าง และขยายแคนวาส Composer Studio
3. **v3.13:** อัปเกรดระบบ Universal Auto-Save ทั่วทั้งโปรแกรม
4. **v3.14:** นำปุ่มบันทึกที่ซ้ำซ้อนออกจากหน้าต่าง Settings และ Chat Settings และแก้ไขข้อผิดพลาดในตัวแบ็กอัปของ Updater ที่ทำให้ข้อมูลช่องและเช็กบ็อกซ์ Auto-Connect ถูกรีเซ็ตขณะอัปเดต โดยเพิ่มระบบผสานข้อมูลและซิงก์ไฟล์แบ็กอัปอัตโนมัติอย่างถาวร
