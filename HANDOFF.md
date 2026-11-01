# HANDOFF.md — Broadcast Playroom 3 (v3.9)

## สถานะปัจจุบัน (Current Status)
- **เวอร์ชันล่าสุด:** v3.9 (ปล่อยอัปเดตอย่างเป็นทางการบน GitHub Releases แล้ว)
- **การทดสอบความถูกต้อง:**
  - Automated Python Unit Verification: ผ่าน 100%
  - Playwright Headless Popout Game Overlay Test: ผ่าน 100% (บันทึกภาพหลักฐานที่ erified_game_overlay_restored.png)
  - Live Update GitHub Tag Verification: ตรวจพบ v3.9 ล่าสุด 100%

## สรุปการแก้ไขสำคัญ (Key Changes in v3.9)
1. **Game Overlay Settings Full V2 Parity:**
   - โหมด Default, Themes, Balloon, Character Talk
   - ปรับแต่งอนิเมชั่นเข้า/ออก และ Auto-Hide ซ่อนข้อความเมื่อหมดเวลา
   - ปรับแต่งกล่องข้อความ (Box), Stroke, Shadow, และรายการฟอนต์ Google Fonts ภาษาไทยครบ 32 ฟอนต์
   - แก้ไขการ Initialize อัตโนมัติในโหมด Popout Window
2. **Channel & Platform Settings Persistence:**
   - Multi-path discovery & bidirectional sync ระหว่าง Data Root และ %LOCALAPPDATA%
   - ป้องกันการส่งค่าว่างทับข้อมูลเดิม
   - Pre-update backup & post-update restore ใน updater.py และ batch script
