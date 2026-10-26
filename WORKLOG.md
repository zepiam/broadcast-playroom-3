# WORKLOG — Broadcast Playroom 3

บันทึกประวัติการพัฒนาและการเปลี่ยนแปลงของโปรเจกต์ (Append-Only Changelog)  
บันทึกอย่างต่อเนื่องทุกครั้งที่จบงานย่อยหรือส่งต่องานระหว่าง Antigravity และ Codex

---

## [2026-10-26 14:15] — Antigravity (Initial Baseline & Overlay Lifecycle Alignment)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ผู้ใช้ตรวจพบว่าเวอร์ชันใหม่มีเสียง Sound Effect แปลกปลอมที่ใส่เข้ามาเอง
  - ระบบ Overlay ของเครื่องมือต่างๆ (Ask, Randomizer, Giveaway) ทำงานไม่ตรงตามเวอร์ชันเดิม (`broadcast playroom dev`)
  - มีการอ้างอิงเบราว์เซอร์ Chrome ส่วนตัว ทำให้ Extension เช่น Bitwarden เข้ามาแทรกแซงช่องกรอก
  - ลิงก์ OBS Browser Source แสดงผลเป็นจอว่างเปล่า
- **สิ่งที่เปลี่ยนแปลง:**
  1. `src/index.html`:
     - ลบคำสั่ง `playPlayroomSynthesizer` ออกจาก `startAskPoll()`, `endAskPoll()`, `startGiveawaySpin()`, และ `spinRandomizer()` เพื่อตัดเสียงแปลกปลอมออก 100%
     - ยุบรวม `runSpinRandomizer()` ที่ซ้ำซ้อนให้เหลือจุดเดียว และส่ง payload สุ่มด่วนไปยัง OBS ทันที
     - แก้ไข `emitGwState()` ให้ส่งสัญญาณผ่าน `BroadcastChannel('bp3_system_channel')` พร้อมสถานะ `active` และ `phase`
     - เชื่อมต่อ `toggleGwLiveCode(btn)` ให้เรียก `emitGwState()` เพื่อเปิด/ปิดโค้ดบน OBS ทันที
     - เพิ่มแท็กป้องกัน Anti-Autofill และ Bitwarden Suppression (`data-bwignore="true"`, `data-lpignore="true"`, `autocomplete="off"`) บนทุกช่องกรอก
  2. `src/composer.html` & `src/overlay.html`:
     - พอร์ตฟังก์ชัน `handleRandomizerSpin(data)` เวอร์ชัน `#on-demand-randomizer-overlay` จากเวอร์ชันเดิมมาใส่สมบูรณ์แบบ
     - รองรับการสร้าง On-Demand Overlay ลอยบนจอ OBS อัตโนมัติ หมุน 26 ticks แบบ deceleration โชว์ผู้ชนะสีทอง ค้างตามเวลา แล้วลบตัวเองออกจาก DOM คืนสู่ความโปร่งใส 100% (0% GPU idle)
     - เพิ่มการซ่อนวิดเจ็ตในสถานะ Standby (`display: none;`) เพื่อไม่ให้มีกล่องดำหรือเส้นขอบตกค้างบนจอ OBS
     - เพิ่ม CSS & Script ป้องกัน Browser Extension แทรกแซง
  3. `src/composer_studio.js`:
     - ปรับแต่ง `bus.on('RANDOMIZER_SPIN')` ให้สร้าง On-Demand Overlay ขึ้นบน Canvas ในแอปด้วย
     - เพิ่มการรองรับสถานะ Idle Transparency ของ Giveaway และ Ask
  4. `launch_dev.py`:
     - เพิ่มพารามิเตอร์เปิด Chromium ให้แยกโปรไฟล์เด็ดขาด: `--user-data-dir=%LOCALAPPDATA%\BroadcastPlayroom3\browser_profile`
     - เพิ่มแฟล็กปิด Extension: `--disable-extensions`, `--disable-plugins`, `--disable-save-password-bubble`, `--disable-features=AutofillServerCommunication,PasswordGeneration`
     - ปรับปรุงฟังก์ชัน `get_layout()` ให้ตรวจ `mtime` ของ `composer_layout.json` เพื่อโหลดเลย์เอาต์ใหม่จากดิสก์เสมอ
  5. `copy_dist_assets.py`:
     - เพิ่มการก็อปปี้ `modal.css` และ `widget_customizer.css` ไปยังโฟลเดอร์ `dist/`
  6. `composer_layout.json`:
     - บันทึกคืนค่าวิดเจ็ตมาตรฐานครบชุด (นาฬิกาดิจิทัล Clock, กล่องแชทสด Chat, โพล Ask, กล่องแจกรางวัล Giveaway)
  7. เริ่มต้น Git Repository และทำ Baseline Commit `0457591`
- **ผลการตรวจสอบ (Verification Results):**
  - รัน `npm run build` ผ่านสมบูรณ์ ไม่มี error
  - รันสคริปต์ Playwright `verify_all_tools_old_vs_new.py` ผ่าน 100% (Standby Transparency, Randomizer On-Demand, Giveaway Lifecycle, Ask Poll Lifecycle)
  - รันสคริปต์ Playwright `verify_plugin_isolation.py` ผ่าน 100% (ตรวจสอบ 223+ inputs พบว่ามี `data-bwignore="true"` ครบทุกช่อง และ Extension CSS suppression ทำงานถูกต้อง)
  - รันสคริปต์ `test_live_screen.py` ทดสอบ `http://127.0.0.1:8080/composer.html?p=1` พบเรนเดอร์วิดเจ็ตครบ 4 ตัวถูกต้อง
- **สถานะ:** ทำแล้วและตรวจผ่าน (Completed & Verified) ✅
