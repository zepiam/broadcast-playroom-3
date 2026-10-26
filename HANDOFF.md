# HANDOFF — Broadcast Playroom 3

> **สถานะงานล่าสุดสำหรับการส่งต่องานระหว่าง Antigravity และ Codex**  
> *อัปเดตล่าสุด: 2026-10-26 14:15:00 +07:00 โดย Antigravity*  
> *Git Branch:* `master` | *Commit:* `83eeeea` (Dual-AI handoff protocol established)

---

## 1. ภาพรวมโปรเจกต์และเป้าหมายปัจจุบัน (Current Goal)
- **โปรเจกต์:** Broadcast Playroom 3 (`E:\DOCS\Documents\AI TOOLS\broadcast playroom 3`)
- **เป้าหมายหลัก:** พัฒนาระบบแผงควบคุมสตรีมเมอร์ (Desktop App), OBS Custom Browser Dock, และ OBS Live Overlay (Composer) ให้เสถียร แสดงผลตรงตามเวอร์ชันเดิม (`broadcast playroom dev`) 100% โดยไม่มีการเพิ่มลูกเล่น/เสียงแปลกปลอมโดยพลการ รองรับ Zero GPU Lockup และแยกการทำงานจากเบราว์เซอร์ส่วนตัวอย่างเด็ดขาด

---

## 2. สถานะงานปัจจุบัน (Work Status Breakdown)

### 2.1 ทำแล้วและตรวจผ่าน (Completed & Verified) ✅
*ทุกรายการด้านล่างนี้ผ่านการเขียนสคริปต์ทดสอบ E2E ด้วย Playwright จริงและมีหลักฐานภาพ/โค้ดยืนยัน 100%*

1. **Overlay Standby Transparency (ความโปร่งใส 100% ตอนพักใช้งาน)**:
   - ตรวจสอบ `overlay.html` และ `composer.html`: เมื่อไม่มีกิจกรรมหรือโพล/สุ่มใดๆ กำลังทำงาน หน้าจอจะโปร่งใสสนิท ไม่มีกล่องดำ ข้อความ หรือแถบใดๆ ลอยค้างบนจอ OBS
   - ผลการทดสอบ: ผ่าน 100% (`assert rand_overlay is None`)
2. **Quick Randomizer On-Demand Overlay (สุ่มด่วนลอยบนจอ OBS ทันที)**:
   - พอร์ตระบบ `#on-demand-randomizer-overlay` จากเวอร์ชันเก่ามาลง `composer.html`, `overlay.html`, และ `composer_studio.js`
   - เมื่อกดหมุนสุ่ม ตัวสุ่มจะลอยขึ้นบนจอ OBS ทันทีตาม Anchor หมุนสุ่มแบบหน่วงความเร็ว (deceleration) 26 สเต็ป สรุปผู้ชนะสีทอง ค้างตามเวลา (holdDuration) แล้ว Fade out และ `.remove()` ออกจาก DOM คืนสู่ 0% GPU idle โดยไม่ต้องสร้าง Widget ใน Composer
   - ผลการทดสอบ: ผ่าน 100%
3. **Ask Poll Overlay Lifecycle (วงจรชีวิตโพลสำรวจความคิดเห็น)**:
   - Standby โปร่งใส 100% $\rightarrow$ เมื่อกดเริ่มโพล แสดงกล่องคำถามและตัวเลือกพร้อมเวลานับถอยหลัง $\rightarrow$ เมื่อจบโพล สรุปผลเรียงคะแนนและไฮไลต์ผู้ชนะ $\rightarrow$ เมื่อกดปิดโพลหรือหมดเวลา ซ่อนกลับสู่ความโปร่งใส 100%
   - ผลการทดสอบ: ผ่าน 100%
4. **Giveaway Overlay Lifecycle (วงจรชีวิตกิจกรรมแจกรางวัล)**:
   - แก้ไข `emitGwState` ให้ส่งสัญญาณผ่าน `BroadcastChannel('bp3_system_channel')` ไปยัง OBS จริง
   - เชื่อมต่อปุ่มเปิด/ปิดรับโค้ด `#join` ให้แสดงและซ่อนตัวแบนเนอร์บน OBS ได้ทันที เมื่อกดสุ่มจะแสดงผู้ชนะ และเมื่อปิดรับโค้ดจะซ่อนกลับเป็นโปร่งใส 100%
   - ผลการทดสอบ: ผ่าน 100%
5. **กำจัดเสียงสังเคราะห์แปลกปลอม (Elimination of Arbitrary SFX)**:
   - ลบเสียง `playPlayroomSynthesizer` ที่ถูกใส่ไว้ในปุ่มเริ่มโพล, จบโพล, เริ่มสุ่ม Giveaway, และหมุน Randomizer ออกทั้งหมด
   - เสียงซาวด์เอฟเฟกต์ถูกจำกัดให้เล่นเฉพาะเมื่อกดในแท็บ Playroom Soundboard เท่านั้น
   - ผลการทดสอบ: ผ่าน 100%
6. **การแยกตัวจากเบราว์เซอร์ Chrome และสกัดกั้นปลั๊กอิน (Browser & Plugin Isolation)**:
   - เพิ่ม `--user-data-dir=%LOCALAPPDATA%\BroadcastPlayroom3\browser_profile` ใน `launch_dev.py` แยกโปรไฟล์ออกจาก Chrome ส่วนตัว 100%
   - ใส่แฟล็ก `--disable-extensions`, `--disable-plugins`, `--disable-save-password-bubble`, `--disable-features=AutofillServerCommunication,PasswordGeneration`
   - ฝังระบบ Anti-Autofill ใน `index.html`, `dock.html`, `composer.html`, `overlay.html` สั่งติดแท็ก `data-bwignore="true"`, `data-lpignore="true"`, `autocomplete="off"` บนทุก input (ทั้งแบบคงที่และแบบ dynamic รวม 223+ ช่อง)
   - ผลการทดสอบ: ผ่าน 100% ปลั๊กอิน Bitwarden / LastPass ไม่สามารถเข้ามายุ่งเกี่ยวกับช่องกรอกได้อีกต่อไป
7. **แก้ปัญหาลิงก์ OBS Browser Source คืนค่าวิดเจ็ตเริ่มต้น**:
   - อัปเดต `composer_layout.json` ให้มีวิดเจ็ตมาตรฐานครบชุด (นาฬิกา Clock มุมขวาบน, แชทสด Chat มุมล่างซ้าย, โพล Ask, แจกรางวัล Giveaway)
   - ปรับ `launch_dev.py` ฟังก์ชัน `get_layout()` ให้ตรวจ `mtime` ของ `composer_layout.json` แบบเรียลไทม์ ไม่ค้างแคชในแรม
   - ผลการทดสอบ: เปิด `http://127.0.0.1:8080/composer.html?p=1` แล้วเรนเดอร์วิดเจ็ตขึ้นครบ 4 ตัวถูกต้อง

---

### 2.2 ทำแล้วแต่ยังไม่ได้ตรวจ (Completed but Unverified) 🟡
- ไม่มี (ทุกฟังก์ชันที่ดำเนินการได้รับการตรวจผ่านการรัน Playwright ครบถ้วนแล้ว)

---

### 2.3 ข้อเสนอที่ยังไม่ได้ทำ (Proposed / Backlog) 📋
1. **การปรับแต่งธีมและการจัดตำแหน่งหน้าจอเพิ่มเติมผ่าน UI Composer Studio**:
   - ตรวจสอบการลากย้ายและปรับขนาด (Resize) วิดเจ็ตเพิ่มเติมในหน้าจอความละเอียดอื่นๆ
2. **การเชื่อมต่อแชทจริงหลายแพลตฟอร์มพร้อมกัน (Multi-Platform Live Chat)**:
   - ทดสอบการดึงแชทสดจริงจาก YouTube, Twitch, TikTok, SOOP เข้าสู่ `chat_bridge.py`

---

## 3. ไฟล์สำคัญและหน้าที่ของแต่ละไฟล์ (Key Architecture Map)

| ไฟล์ | หน้าที่สำคัญ |
| :--- | :--- |
| `launch_dev.py` | ไพธอนเซิร์ฟเวอร์หลัก (พอร์ต 8080) ทำหน้าที่เสิร์ฟไฟล์, จัดการ layout API, คุมการเปิดหน้าต่างแอป Chrome sandbox mode |
| `run.bat` | แบตช์ไฟล์สำหรับดับเบิลคลิกเปิดโปรแกรมในโหมดพัฒนา |
| `composer_layout.json` | ไฟล์บันทึกตำแหน่งวิดเจ็ตและเลย์เอาต์หน้าจอสำหรับ OBS |
| `copy_dist_assets.py` | สคริปต์ซิงค์ไฟล์จาก `src/` ไปยัง `dist/` |
| `src/index.html` & `dist/index.html` | หน้าต่างหลักของโปรแกรม (ควบคุมโพล, สุ่มด่วน, แจกรางวัล, ซาวด์บอร์ด, แชท) |
| `src/composer.html` & `dist/composer.html` | หน้าจอสำหรับใส่เป็น OBS Browser Source (`http://127.0.0.1:8080/composer.html`) |
| `src/overlay.html` & `dist/overlay.html` | หน้าจอทางเลือก (Alias ของ composer.html) |
| `src/dock.html` & `dist/dock.html` | หน้าต่างสำหรับใส่เป็น OBS Custom Browser Dock (`http://127.0.0.1:8080/dock.html`) |
| `src/composer_studio.js` & `dist/composer_studio.js` | คอร์เอนจินของ Composer Canvas และตัวจัดการอีเวนต์ |

---

## 4. ผลการทดสอบและคำสั่งที่ใช้ทดสอบ (Verification Commands)

### รันบิลด์โปรเจกต์:
```powershell
npm run build
```
*(จะรัน `vite build && python copy_dist_assets.py` อัตโนมัติ)*

### รันทดสอบระบบ Overlay และ Lifecycle ทั้งหมด:
```powershell
python "C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\scratch\verify_all_tools_old_vs_new.py"
```

### รันทดสอบการป้องกัน Browser Plugin (Bitwarden / Autofill Isolation):
```powershell
python "C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\scratch\verify_plugin_isolation.py"
```

### รันทดสอบความถูกต้องของ OBS Browser Source URL:
```powershell
python "C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1\scratch\test_live_screen.py"
```

---

## 5. จุดที่หยุดและขั้นตอนถัดไปสำหรับ AI ผู้รับช่วงต่อ (Next Steps)
- **จุดที่หยุดล่าสุด:** ระบบ Overlay ทั้งหมด (Randomizer, Ask, Giveaway, Chat, Clock), การตัดเสียงแปลกปลอม, การตัดขาดจากปลั๊กอิน Chrome และการเรนเดอร์บน OBS ทำงานสมบูรณ์ 100% แล้ว
- **ขั้นตอนถัดไป:**
  1. หากผู้ใช้ต้องการปรับแต่งฟีเจอร์ใดเพิ่มเติม ให้เริ่มจากการอ่าน `HANDOFF.md` และตรวจเช็คไฟล์จริง
  2. เมื่อมีการแก้ไขโค้ดใดๆ ต้องรัน `npm run build` เสมอเพื่อให้ไฟล์ใน `dist/` อัปเดตตรงกับ `src/`
  3. ก่อนจบงานย่อย ให้อัปเดตสถานะใน `HANDOFF.md` และเพิ่มประวัติลงใน `WORKLOG.md` ทันที
