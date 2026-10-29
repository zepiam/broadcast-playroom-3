
## [2026-10-30 02:03] — Antigravity (Single Titlebar Polish, Resizers, Maximize/Restore Fix & Fresh v3.1 Releases Uploaded)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **สรุปสิ่งที่ดำเนินการ:**
  1. **แก้ไข Native Frameless Titlebar:**
     - ตัดบาร์ซ้อน 2 ชั้นของ Windows ออกถาวร หน้าต่างกลับมาใช้ Single Custom Titlebar สไตล์ Native สีเทาเข้มสะอาดยืนหนึ่ง
     - เพิ่มระบบ Invisible Border Resizers 8 ทิศทางรอบขอบหน้าต่าง สามารถลากปรับขนาด กว้าง x สูง ได้ลื่นไหล
     - ป้องกันการลากหลุดตำแหน่งขณะขยายเต็มจอ (Maximized) และเพิ่มการดึงลงเพื่อ Restore อัตโนมัติ พร้อมรองรับดับเบิ้ลคลิกแถบหัว
  2. **แก้ไขบั๊กปุ่มขยายเต็มจอ / คืนขนาด (Maximize / Restore):**
     - ตรวจจับสถานะหน้าต่างจริงผ่าน Win32 IsZoomed และ WinForms State แทนตัวแปร pywebview ที่ค้าง False
     - สามารถกดสลับ ขยายเต็มจอ / ย่อกลับมา ได้อย่างสมบูรณ์แบบ 100%
  3. **คอมไพล์และสร้างแพ็กเกจ .zip สะอาด ปลอดภัย 100%:**
     - BroadcastPlayroom3-Lite.zip (328.44 MB)
     - BroadcastPlayroom3-Full.zip (4,068.58 MB)
     - ทั้งสองไฟล์ผ่าน Zero-Leak Privacy Audit (0 personal tokens / 0 user data)
  4. **อัปโหลดขึ้น Hugging Face Repository:**
     - อัปโหลดทั้งสองไฟล์ขึ้น men9ch/broadcast-playroom-3 สำเร็จ 100%

---
# WORKLOG — Broadcast Playroom 3

บันทึกประวัติการพัฒนาและการเปลี่ยนแปลงของโปรเจกต์ (Append-Only Changelog)  
บันทึกอย่างต่อเนื่องทุกครั้งที่จบงานย่อยหรือส่งต่องานระหว่าง Antigravity และ Codex

---

## [2026-10-29 23:20] — Antigravity (Live Chat Settings Redesign, Slider Fix & Icon Completeness)
- **ผู้ดำเนินการ:** Antigravity (Google DeepMind)
- **ปัญหา / คำขอจากผู้ใช้:**
  1. หน้าต่างตั้งค่าแชทสด (`win-chat-settings`): เวลาลดความกว้างของหน้าต่างให้แคบ slider ของขนาดตัวอักษรแชทจะหดเหลือแค่นิดเดียว (40px)
  2. เวลาปรับขนาดตัวอักษรที่ slider ตัวอย่างแชทสดด้านขวา (`#chatPreviewBox`) ไม่ปรับขนาดตัวอักษรตามแบบเรียลไทม์
  3. ส่วนเปิด/ปิดแสดงรูปโปรไฟล์กับรูปแพลตฟอร์ม ออกแบบไม่สวย (เป็นกล่องบล็อกเรียบๆ มีกล่องติ๊กตกไปอยู่แถวล่าง)
  4. ไอคอนโปรแกรมไม่แสดงใน Taskbar และมุมซ้ายบนของหน้าต่างโปรแกรม (รวมถึงหน้าต่าง Popout)
- **สาเหตุที่ตรวจพบ:**
  1. Slider `#rngLiveChatFontSize` เดิมใช้ `class="topbar-slider"` ซึ่งใน `src/styles.css` มี `@media (max-width: 1100px) { .topbar-slider { width: 40px !important; } }` ทำให้ slider ถูกบีบเหลือ 40px ทันทีที่หน้าต่างแคบ
  2. ฟังก์ชัน `adjustFontSize` และ event `oninput` อัปเดตเฉพาะ `#chatList` โดยไม่ได้อัปเดต `#chatPreviewBox .chat-body-msg`
  3. บล็อกสวิตช์เดิมใช้โครงสร้าง `.clean-row` ธรรมดา ไม่มี flex align ทำให้ข้อความและ checkbox แยกคนละบรรทัด ไม่สวยงาม
  4. ในส่วนไอคอน:
     - `public/favicon.ico` และ `public/favicon.png` ยังไม่มีอยู่ในไดเรกทอรี ทำให้ Vite ไม่ได้คัดลอกไปยัง `dist/`
     - ใน `popoutToolWindow` ของ `src/index.html` ตัวคัดลอก head (`querySelectorAll('style, link[rel="stylesheet"]')`) ไม่ได้คัดลอก `<link rel*="icon">` ทำให้หน้าต่าง Popout ทุกบานไม่มี favicon
     - Win32 Class Icon ใน 64-bit Windows ต้องใช้ `SetClassLongPtrW` (-14 และ -34) เพื่ออัปเดต Class Icon ให้สมบูรณ์
     - Windows Taskbar AppUserModelID ต้องการการผูกกับ Start Menu Shortcut เพื่อให้ Taskbar ดึงไอคอนมาแสดงบนปุ่มทาสก์บาร์ได้ 100%
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **Live Chat Settings Redesign (`src/index.html` & `src/styles.css`):**
     - ออกแบบการ์ดตัวเลือกใหม่สไตล์ Modern Sleek Card (`.chat-setting-toggle-card`) พร้อม Pill Icon สวยงาม (`👤`, `🏷️`, `⏱️`), รายละเอียดข้อความอธิบาย และสวิตช์ Toggle (`.cwc-switch`) อยู่ฝั่งขวาจัดวางเรียบร้อย
     - เปลี่ยน Radio โหมดสีชื่อคนดูเป็น Interactive Option Card (`.chat-color-option-card`) พร้อมไอคอน (`🎨`, `🎲`)
     - เปลี่ยนคลาส Slider จาก `topbar-slider` เป็น `chat-setting-slider` (flex-grow: 1, min-width: 140px, width: 100%) แก้ปัญหาการหดตัวเหลือ 40px อย่างสมบูรณ์
     - ปรับให้ `oninput` บน Slider ขนาดตัวอักษรอัปเดต `.style.fontSize` บน `#chatPreviewBox .chat-body-msg` และ `#chatList .chat-body-msg` ทันทีแบบเรียลไทม์ พร้อมซิงค์ข้ามหน้าต่างหลักและหน้าต่าง Popout
     - ปรับขนาดเริ่มต้นของหน้าต่าง `chat-settings` เป็นความกว้าง 760px สูง 640px ทั้งใน CSS Style และใน `defaultSizes` ของ `popoutToolWindow` ทำให้การ์ดทั้งหมดแสดงผลได้พอดีโดยไม่ถูกตัดทอน
  2. **Icon Completeness & System Synchronization:**
     - คัดลอก `bp-full-icon.ico` และ `bp-full-icon.png` ไปยัง `public/`, `dist/`, และ `src/` เป็น `favicon.ico` และ `favicon.png`
     - ฝัง Instant Base64 PNG Icon ลงใน `<head>` ของ `src/index.html` เพื่อให้ Chromium โหลดไอคอนได้ทันทีตั้งแต่ขั้นตอน Parsing
     - อัปเดต `popoutToolWindow` ให้คัดลอก `<link rel*="icon">` และ `<link rel="manifest">` ไปยัง `<head>` ของหน้าต่าง Popout ทุกบาน
     - ปรับปรุง `app_window_frame.py`: ใช้ `SetClassLongPtrW`, เพิ่มฟังก์ชัน `_ensure_app_shortcut` บันทึก `PKEY_AppUserModel_ID` ลงบน Shortcut ของ Windows Shell, และปรับ `apply_icon_to_app_windows()` ให้ตรวจจับได้ทั้งชื่อหน้าต่างและ Process
     - เพิ่ม `app.setWindowIcon(QIcon(...))` ใน `splash.py` ให้ Splash Screen มีไอคอนของโปรแกรม
     - อัปเดต `copy_dist_assets.py` ให้ซิงค์ `favicon.ico`, `favicon.png`, และ `manifest.json` ทุกครั้งที่มีการรัน Build
  3. **การทดสอบและตรวจสอบความถูกต้อง:**
     - รัน Playwright Test (`scratch/test_chat_settings_playwright.py`):
       - ทดสอบความกว้างของ Slider ที่ความกว้างปกติ: กว้าง 289px (PASS)
       - ทดสอบความกว้างของ Slider เมื่อย่อหน้าต่างแคบเหลือ 480px: กว้าง 158px เต็มพื้นที่คอลัมน์ ไม่หดเหลือ 40px (PASS)
       - ทดสอบการเลื่อน Slider ขนาดตัวอักษรไปที่ 22px: `#chatPreviewBox .chat-body-msg` ปรับเป็น 22px ทันที (PASS)
       - บันทึกภาพ Screenshot ตรวจสอบ: `verified_chat_settings_redesign.png`
- **สถานะ:** เสร็จสมบูรณ์ พร้อมให้ผู้ใช้ตรวจสอบ

## [2026-10-29 22:45] — Antigravity (Restore Native Window & Taskbar App Icons)
- **ผู้ดำเนินการ:** Antigravity (Google DeepMind)
- **ปัญหา / คำขอจากผู้ใช้:**
  - ตอนแอปทำงาน ไม่แสดงไอคอนในแถบ Windows Taskbar (แสดงเป็นไอคอนรูปลูกโลก/เว็บพื้นฐานของ Chromium)
  - มุมซ้ายบนของหน้าต่าง (Window Titlebar Caption) ก็แสดงเป็นไอคอนลูกโลกเช่นกัน
- **สาเหตุที่ตรวจพบ:**
  1. โปรแกรมเปิดหน้าต่างแอปด้วย Chrome/Edge โหมด `--app=http://127.0.0.1:...` ซึ่ง Chromium บน Windows จะสร้าง HWND ที่มี Class `Chrome_WidgetWin_1` และกำหนดไอคอนเริ่มต้นของระบบเป็นรูป Web/Globe เนื่องจากไม่ได้ติดตั้งเป็น Installed PWA ผ่าน Registry ของเบราว์เซอร์
  2. โค้ด backend (`app_window_frame.py` และ `launch_dev.py`) ยังไม่เคยมีการส่ง `WM_SETICON` ไปยัง HWND ของหน้าต่าง และยังไม่ได้ตั้งค่า `System.AppUserModel.ID` บน HWND ของ Windows Shell
  3. ในไฟล์ HTML `src/index.html` ขาด `<link rel="manifest" href="/manifest.json">` และเซิร์ฟเวอร์ยังไม่มี MIME handler สำหรับ `/manifest.json` กับ `/favicon.png`
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **Win32 Window Icon & Taskbar AppUserModelID (`app_window_frame.py`):**
     - พัฒนาฟังก์ชัน `setup_app_window_icon(hwnd)`:
       - โหลด `icon.ico` ทั้งขนาด 16x16 (`ICON_SMALL`) และ 32x32 (`ICON_BIG`)
       - ส่งข้อความ `WM_SETICON` (`ICON_SMALL` และ `ICON_BIG`) ไปยัง HWND ของหน้าต่าง
       - ตั้งค่า `SetClassLong` (`GCL_HICONSM` และ `GCL_HICON`)
       - ตั้งค่า `PKEY_AppUserModel_ID` (`men9ch.BroadcastPlayroom3`) และ `PKEY_AppUserModel_RelaunchIconResource` ผ่าน Windows PropertyStore (`SHGetPropertyStoreForWindow`) เพื่อให้ Windows Taskbar จัดกลุ่มเป็น Broadcast Playroom 3 และแสดงไอคอนแอปอย่างถูกต้อง
     - ผูก `setup_app_window_icon(hwnd)` ใน `action('init')`, `action('restore-frame')`, `action('set-icon')`, และ `_remember_window(hwnd)`
  2. **Background Watcher (`launch_dev.py`):**
     - ใน `open_app_window()` เพิ่มเธรด `_watch_app_window_icon()` คอยตรวจจับหน้าต่าง Broadcast Playroom 3 ทันทีที่เปิดขึ้นมา แล้วเรียก `apply_icon_to_app_windows()` เพื่อเซ็ตไอคอนทันที
     - ใน `/api/app-presence/stream` เมื่อหน้าเว็บเชื่อมต่อสำเร็จ จะตรวจสอบและอัปเดตไอคอนหน้าต่างซ้ำอีกครั้ง
     - เพิ่มเส้นทางสำหรับ `/manifest.json`, `/manifest.webmanifest`, และแยกประเภท MIME ของ `/favicon.ico` (`image/x-icon`) กับ `/favicon.png` (`image/png`) ให้ถูกต้อง
  3. **Web Manifest & Icon Links (`src/index.html` & `public/manifest.json`):**
     - เพิ่ม `<link rel="manifest" href="/manifest.json">` พร้อม icon links ขนาดต่างๆ (32x32, 192x192, 256x256) และ meta theme-color ใน `<head>`
     - เรียก `/api/window/frame` (`action: 'set-icon'`) ทันทีตอน `DOMContentLoaded`
     - รัน `npm run build` ซิงค์ไปยัง `dist/` เรียบร้อย
  4. **การตรวจสอบความถูกต้อง:**
     - รันสคริปต์ทดสอบ `scratch/test_all_icon_fixes.py` ตรวจสอบทั้ง `WM_GETICON` (small, big), `AppUserModel_ID`, `RelaunchIconResource` และการตอบกลับของ HTTP Server ทุก endpoints -> **PASS 100%**
     - รัน `tests/verify_window_frame.py` -> **PASS 100%**
- **สถานะ:** เสร็จสมบูรณ์ (รอสัญญาณคำสั่งจากผู้ใช้เพื่อ Build Release / อัปเดตแพ็กเกจ)

---

## [2026-10-29 22:20] — Antigravity (Live Chat TTS Latency Badge Display in Seconds/Sec)
- **ผู้ดำเนินการ:** Antigravity (Google DeepMind)
- **ปัญหา / คำขอจากผู้ใช้:**
  - ป้ายแสดงความเร็ว TTS ข้างยอดคนดูในแชทสด (`#chatTtsLatencyBadge`) กลับไปแสดงผลเป็นมิลลิวินาที (`ms`) ผู้ใช้ต้องการให้แสดงเป็นหน่วยวินาที (`sec` / `s`) ให้เข้าใจง่าย สอดคล้องกับที่เคยขอไว้
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **ปรับการแสดงผลป้าย TTS ข้างยอดคนดู (`src/index.html` & `dist/index.html`):**
     - อัปเดต `initial` HTML title เป็น `"เวลาประมวลผลเสียงอ่าน TTS ก่อนเริ่มเล่นล่าสุด (วินาที)"`
     - ในตัวจับเวลาเสียงอ่าน `audio.addEventListener('playing')` เปลี่ยนจาก `'⚡ TTS: ' + Math.round(elapsed) + 'ms'` เป็น `'⚡ TTS: ' + sec + ' sec'` (เช่น `⚡ TTS: 0.14 sec`)
     - เพิ่ม Tooltip คำอธิบายภาษาไทยชัดเจน: `'เวลาประมวลผลเสียงอ่าน TTS ล่าสุด: ' + sec + ' วินาที (' + Math.round(elapsed) + ' ms)'`
     - ซิงค์ค่าไปยังหน้าต่าง Popout Chat ทุกบานอัตโนมัติหากมีการเปิดแยกหน้าต่าง
     - รัน `npm run build` และ `python copy_dist_assets.py` อัปเดต `dist/index.html` เรียบร้อย
  2. **การตรวจสอบความถูกต้อง (Playwright Verification):**
     - ตรวจสอบการแสดงผลจริงผ่าน headless browser และบันทึกภาพถ่ายหน้าจอที่:
       - `verified_tts_sec_badge.png`
       - `verified_tts_sec_dist.png`
     - ผลการทดสอบผ่าน 100% สวยงาม ชัดเจน ไม่กินพื้นที่แถบเครื่องมือ
- **สถานะ:** เสร็จสมบูรณ์ (รอสัญญาณคำสั่งจากผู้ใช้เพื่อ Build Release / อัปเดตแพ็กเกจ)

---

## [2026-10-29 22:05] — Antigravity (Click-to-Hide Viewer Count Toggle & LocalStorage Persistence)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - เพิ่มฟังก์ชันให้ผู้ใช้สามารถคลิกที่ป้าย/Label แสดงยอดคนดูโดยตรง เพื่อ สลับซ่อน / แสดง (Toggle Mask/Unmask) ตัวเลขคนดูได้ตามต้องการ
- **สิ่งที่ดำเนินการพัฒนา:**
  1. **สลับซ่อน/แสดงยอดคนดูด้วยการคลิก (`src/index.html` & `src/styles.css`):**
     - ผูกคำสั่ง `onclick="toggleChatViewersVisibility()"` เข้ากับป้ายยอดคนดูรวม `#chatTotalViewersBadge` ตรงหัวข้อแชทสด และป้าย `.plat-viewers` บนการ์ดแพลตฟอร์ม
     - เมื่ออยู่ในสถานะ "ซ่อน": แสดงผลเป็น `👥 •••` พร้อมคลาส `.masked` สีเทาหรูหรา และ Tooltip อธิบาย "ยอดคนดูถูกซ่อนอยู่ (คลิกเพื่อแสดง)"
     - เมื่ออยู่ในสถานะ "แสดง": แสดงผลเป็นตัวเลขจริงตามที่ดึงมาได้ เช่น `👥 12` พร้อมสีเขียวสดใส
     - จดจำสถานะลง `localStorage` (`bp3_hide_chat_viewers`) ทำให้เมื่อรีเฟรชหรือเปิดโปรแกรมใหม่ สถานะที่เลือกไว้จะไม่หาย
     - แสดง Toast แจ้งเตือนสั้นๆ: `👁️‍🗨️ ซ่อนตัวเลขยอดคนดูแล้ว` / `👥 แสดงตัวเลขยอดคนดูแล้ว`
     - ซิงก์สถานะทั้งในหน้าต่างหลักและหน้าต่าง Popout Chat แบบ Real-time
  2. **การทดสอบอัตโนมัติ (Playwright Verification):**
     - ทดสอบผ่าน `scratch/verify_toggle_hide_viewers.py`
     - ยืนยันการคลิกสลับซ่อน `👥 •••` -> แสดง `👥 12` -> คลิกบนการ์ดแพลตฟอร์ม -> สลับซ่อนสำเร็จ 100%
     - บันทึกภาพหลักฐาน: `verified_viewers_masked.png` และ `verified_viewers_unmasked.png`

---

## [2026-10-29 21:55] — Antigravity (Live Chat Total Viewers Badge & Twitch Fast Fallback Polling)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. แก้บั๊กยอดคนดูไม่แสดงในโปรแกรม (ผู้ใช้ทดสอบสตรีมที่ https://twitch.tv/men9ch มีคนดูจริง แต่ในแผงแชทสดแสดง 👥 0)
  2. แก้บั๊กให้เสร็จสมบูรณ์ และรอคำสั่งยืนยันจากผู้ใช้ก่อนดำเนินการบิลด์อัปเดตแพ็กเกจใหม่
- **สิ่งที่ดำเนินการแก้ไขและปรับปรุง:**
  1. **ป้ายยอดคนดูรวมในหัวแชทสด (`#chatTotalViewersBadge` ใน `src/index.html` & `dist/index.html`):**
     - กำหนด `id="chatTotalViewersBadge"` ให้กับ `.chat-viewers-pill` ที่เดิมมีเพียงข้อความฮาร์ดโค้ด `👥 0`
     - พัฒนาฟังก์ชัน `updateLiveChatViewersBadge(totalViewers, hasConnected)` ซิงก์ยอดคนดูรวมจากทุกแพลตฟอร์มที่เชื่อมต่ออยู่แบบ Real-time
     - เชื่อมต่อ `bp3:remote-event` ดักจับเหตุการณ์ `VIEWERS_UPDATE` อัปเดตทันทีที่ Backend ส่งข้อมูลเข้ามา
     - คำนวณยอดรวมใน `pollPlatformStatuses()` และอัปเดตทั้งหน้าต่างหลักและ Popout Chat พร้อมกัน
  2. **ระบบดึงยอดคนดู Twitch แบบตอบสนองไว & Fallback (`chat_twitch.py`):**
     - เพิ่ม HTTP Browser Headers (`User-Agent`, `Referer`, `Accept`) ในคำขอ Twitch GraphQL ป้องกัน Edge CDN ปฏิเสธคำขอ
     - ลดรอบการ Poll จากเดิม 60 วินาที เหลือ **15 วินาที** เพื่อความต่อเนื่องและสดใหม่ของตัวเลขคนดู
     - เพิ่มระบบ Fallback อัจฉริยะไปยัง DecAPI (`https://decapi.me/twitch/viewercount/{channel}`) หาก GraphQL คืนค่า null หรือ 0 ขณะสตรีมเพิ่งเริ่ม
     - ส่งสัญญาณ `on_status('✅ เชื่อมต่อ...')` ก่อนเริ่มเธรด Poll เพื่อการันตีว่าสถานะ `connected=True` ในระบบบริดจ์พร้อมรับยอดคนดูทันที
  3. **การซิงก์สู่ Composer Studio & Widget (`src/viewer_connections.js` & `src/live_overlay.js`):**
     - รองรับทั้ง `#obsCanvasStage` และ `#composerCanvasStage` ให้ Widget ยอดคนดูในหน้าต่าง Composer แสดงผลตามจริง
  4. **การทดสอบความถูกต้อง (Playwright Verification):**
     - ทดสอบผ่าน `scratch/debug_viewers.py` ทั้งผ่าน Polling `/api/status` และ Event `VIEWERS_UPDATE`
     - ผลการทดสอบผ่าน 100% (ป้ายแสดง `👥 3` และ `👥 5` ตามลำดับ)
     - บันทึกหลักฐาน: `verified_live_chat_viewers_badge.png` และ `verified_full_app_viewers.png`

---

## [2026-10-29 20:15] — Antigravity (Clean Binary Rebuild & Release Upload to Hugging Face)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. สร้างไฟล์แพ็กเกจ .zip ของโปรแกรมขึ้นใหม่ทั้งสองรุ่น (Lite และ Full) ที่รวบรวมฟีเจอร์ล่าสุด:
     - Voice Settings: การล็อกปุ่มและสถานะ "⏳ กำลังเตรียมเสียง..." / "🔊 กำลังอ่าน..." ป้องกันการกดซ้ำ
     - High-Speed TTS LRU In-Memory Cache (เร่งความเร็วเสียงอ่านซ้ำเป็น 0.002ms)
     - เครื่องมือจัดการแชทสดรายข้อความ: 🚫 บล็อก (ตัวเลือก 4 ขั้น: ซ่อนบนจอ, ไม่อ่านเสียง, ห้ามใช้ replie, Blacklist ถาวร) และ 🗑️ ลบข้อความ
     - สรุปผลโหวต ASK Poll ในช่องแชทสดด้วย Horizontal Bar Graph การ์ดสรุปผลคะแนนที่อ่านง่าย
     - Blacklist Exclusion ครอบคลุมทุกระบบอินเทอร์แอคทีฟ (ASK, Giveaway, Replie)
  2. กวาดล้างข้อมูลส่วนตัว 100% Zero-Leak Guarantee: ผู้ใช้ใหม่ต้องได้รับโปรแกรมที่บริสุทธิ์ ปราศจาก Token, บัญชีสตรีมเมอร์ส่วนตัว, บันทึกแชท, หรือการตั้งค่าส่วนบุคคล
  3. อัปโหลดไฟล์ .zip ทั้งสองขึ้น Hugging Face (`men9ch/broadcast-playroom-3`) เพื่อพร้อมให้นำไปอัปโหลดต่อยัง Google Drive
- **สิ่งที่ดำเนินการ:**
  1. **คอมไพล์ไบนารีใหม่ทั้ง 2 รุ่น:**
     - Lite Edition: `build_trials/trial-20261029-195738-420992/dist/BroadcastPlayroom3-Lite`
     - Full Edition: `build_trials/trial-20261029-195952-921742/dist/BroadcastPlayroom3-Full`
  2. **ระบบสแกนความปลอดภัยขั้นสูงสุด (`package_clean_releases.py`):**
     - ตรวจสอบไฟล์ทั้งหมดใน build directory ยืนยันว่าไม่มี `bot_accounts.dat`, `data/`, `browser_profile`, `composer_layout.json`, `replace_words.json`, `log.txt`, `.env` หลุดรอดไปแม้แต่ไฟล์เดียว
  3. **การบีบอัดระดับสูงด้วย 7-Zip:**
     - `BroadcastPlayroom3-Lite.zip`: ขนาด 318.41 MB (4,176 ไฟล์)
     - `BroadcastPlayroom3-Full.zip`: ขนาด 4,059.71 MB (15,456 ไฟล์ พร้อม AI Voice Inference & PyTorch/CUDA)
  4. **อัปโหลดอัตโนมัติขึ้น Hugging Face Repository:**
     - อัปโหลดผ่าน `upload_to_hf.py` สำเร็จสมบูรณ์ทั้ง 2 ไฟล์สู่ `men9ch/broadcast-playroom-3` (Commit OK)

---

## [2026-10-29 14:55] — Antigravity (Official Mirror Integration & Production Installer Finalized)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **สิ่งที่ดำเนินการ:**
  1. นำลิงก์จริงจาก Hugging Face (Primary) และ Google Drive (Mirror Fallback) บรรจุลงใน `installer_gui.py` และ `version.json`
  2. พัฒนาระบบ Smart Google Drive Form & Token Resolver ดึงไฟล์ขนาดใหญ่ (>100MB) จาก Google Drive ได้โดยอัตโนมัติ ไม่ติดหน้าแจ้งเตือนไวรัส
  3. ทดสอบการเชื่อมต่อดาวน์โหลดจริงทั้ง Hugging Face และ Google Drive ผ่านฉลุย 100%
  4. ทำการ Compile ตัวติดตั้งขั้นสุดท้าย `dist_releases/BroadcastPlayroom3-Setup.exe` (~43 MB) พร้อมแจกจ่ายให้ผู้ใช้งานจริงทันที

---

## [2026-10-29 14:30] — Antigravity (Unified Setup Installer, Clean Distribution Audit & 7-Zip Packaging for Hugging Face)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. เตรียมตัวติดตั้ง Web Installer ตัวเดียว (Single Unified Setup Executable) ที่ให้ผู้ใช้เลือกลงได้ระหว่าง Lite หรือ Full
  2. ดาวน์โหลดไฟล์บีบอัด (.zip) อัตโนมัติจาก Hugging Face (และมี Mirror สำรองสลับได้) แตกไฟล์ลงเครื่อง และลบไฟล์ ZIP ทิ้งทันทีเพื่อไม่ให้เปลืองพื้นที่
  3. ตรวจสอบให้แน่ใจว่าไม่มีข้อมูลส่วนตัว (Token, Bot Account, Layout, DNS, DB) หลุดไปกับตัวแจกจ่าย
  4. ทำการ Rebuild ทั้ง Lite และ Full พร้อมบีบอัดเป็น .zip เตรียมไว้สำหรับอัปโหลดขึ้น Hugging Face
- **สิ่งที่ดำเนินการปรับปรุงและพัฒนา:**
  1. **สแกนตรวจสอบความสะอาดของไฟล์ (Clean Distribution Audit):**
     - ตรวจสอบไฟล์ทั้งหมดใน build output ยืนยันว่าไม่มี `bot_accounts.dat`, `composer_layout.json`, `dns_settings.json`, หรือไฟล์ฐานข้อมูล SQLite ส่วนตัวติดไป 100%
  2. **พัฒนาตัวติดตั้งอัจฉริยะ (`installer_gui.py` & `BroadcastPlayroom3-Setup.exe`):**
     - UI Dark Theme สไตล์ Discord สวยงามด้วย PySide6
     - มีปุ่มเลือก: Lite Edition (~318 MB) หรือ Full Edition (~3.0 GB พร้อม AI Voice RVC)
     - มีระบบตรวจสอบและบังคับตั้งค่า Windows Defender Exclusion อัตโนมัติตั้งแต่ตอนติดตั้ง
     - ระบบดาวน์โหลดพร้อม Progress Bar แสดงความเร็ว MB/s, % และเวลาที่เหลือ
     - แตกไฟล์ลงเครื่องปลายทาง -> ลบไฟล์ ZIP ทิ้งทันที (Zero Residual Waste)
     - สร้าง Shortcut บน Desktop และ Start Menu พร้อมลงทะเบียน Uninstaller ใน Windows Settings
     - Compile สำเร็จเป็นไฟล์เดียว: `dist_releases/BroadcastPlayroom3-Setup.exe` (ขนาด ~43 MB)
  3. **การ Rebuild & บีบอัดไฟล์แพ็กเกจด้วย 7-Zip:**
     - Rebuild Lite Edition สำเร็จ บีบอัดเป็น `dist_releases/BroadcastPlayroom3-Lite.zip` ขนาดเหลือ 318 MB (จากเดิม 803 MB)
     - Rebuild Full Edition สำเร็จ บีบอัดเป็น `dist_releases/BroadcastPlayroom3-Full.zip` ลงใน `dist_releases/`

---

## [2026-10-29 14:10] — Antigravity (Pre-Update Windows Defender Exclusion Verification & Relocation Guard)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. เพิ่มระบบตรวจสอบข้อยกเว้น Windows Defender ในหน้าต่างกดยืนยันอัปเดตทันที (Fast Update Modal)
  2. เผื่อกรณีผู้ใช้งานย้ายโฟลเดอร์โปรแกรมไปยังตำแหน่งใหม่หลังจากติดตั้ง (Folder Relocation) ทำให้โฟลเดอร์ใหม่ไม่ได้ถูกยกเว้นใน Defender
  3. บังคับว่าถ้าโฟลเดอร์ปัจจุบันยังไม่ได้อยู่ในรายการข้อยกเว้น (Exclusion) จะต้องกดเพิ่มข้อยกเว้นให้เรียบร้อยก่อน ปุ่ม "อัปเดตทันที" จึงจะปลดล็อกให้กดได้ เพื่อป้องกัน Antivirus บล็อกหรือลบไฟล์แพตช์ระหว่างติดตั้ง
- **สิ่งที่ดำเนินการปรับปรุงและพัฒนา:**
  1. **โมดูลตรวจสอบ & จัดการข้อยกเว้น (`defender_helper.py` & `launch_dev.py`):**
     - พัฒนาฟังก์ชัน `DefenderExclusionManager.get_status_info()` และ `save_exclusion_state()` จัดเก็บและเปรียบเทียบ Path ปัจจุบันของโปรแกรมกับ Path ที่เคยได้รับการยกเว้น
     - เพิ่ม API Endpoint `GET /api/defender/status` ส่งสถานะ `is_excluded`, `status` ('active', 'relocated', 'not_configured') และตำแหน่ง `current_dir`
     - เพิ่ม API Endpoint `POST /api/defender/apply` สั่งรัน PowerShell คำสั่ง `Add-MpPreference -ExclusionPath` แบบ Elevated (UAC) ในคลิกเดียว
  2. **ส่วนติดต่อผู้ใช้ในหน้าอัปเดตด่วน (`src/index.html`):**
     - เพิ่มคอนเทนเนอร์ `#fastUpdateExclusionBox` ตรวจสอบสถานะความปลอดภัยอัตโนมัติเมื่อเปิดหน้าต่างอัปเดต
     - หากตรวจพบว่ายังไม่ถูกยกเว้น หรือมีการย้ายตำแหน่ง: แสดงแถบเตือนสีส้ม ระบุ Path ปัจจุบัน พร้อมปุ่ม `🛡️ เพิ่มข้อยกเว้นอัตโนมัติ (1-Click)` และปุ่มเปิด `Windows Security`
     - ปิดการใช้งานปุ่มยืนยันอัปเดต พร้อมเปลี่ยนป้ายเป็น `🔒 ต้องเพิ่มข้อยกเว้นก่อน`
     - เมื่อผู้ใช้กดเพิ่มข้อยกเว้นสำเร็จ: ระบบจะเปลี่ยนแถบเป็นสีเขียว `✅ โฟลเดอร์ปลายทางได้รับการยกเว้นเรียบร้อย` และปลดล็อกปุ่ม `⚡ อัปเดตทันที` ทันที
  3. **การทดสอบอัตโนมัติ (Playwright Verification):**
     - ทดสอบผ่าน `scratch/verify_update_exclusion_flow.py` จำลองสถานการณ์โปรแกรมถูกย้ายที่ตั้ง (`D:\Games\BroadcastPlayroom3`)
     - ยืนยันการบล็อกปุ่มอัปเดต, การแสดง Path, การคลิกเพิ่มข้อยกเว้น 1-Click, และการปลดล็อกปุ่มอัปเดตทันทีเมื่อสถานะเปลี่ยนเป็น active สำเร็จ 100%
     - บันทึกภาพยืนยัน: `verified_update_exclusion_blocked.png` และ `verified_update_exclusion_unlocked.png`

---

## [2026-10-29 13:25] — Antigravity (Event List Context Menu Auto-Dismiss, "ลบทั้งหมด", Resizable Profile Modal & Chat Export Restored)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. หน้า Event List เวลาคลิกขวาเพื่อขึ้นเมนูล้างรายการกิจกรรม ถ้าไม่คลิกปุ่มจะค้าง ให้สามารถคลิกที่ว่างอื่นแล้วเมนูหายไปได้โดยอัตโนมัติ
  2. เปลี่ยนข้อความในเมนูจาก "ล้างรายการกิจกรรมทั้งหมด" เป็น "ลบทั้งหมด"
  3. หน้าต่างโปรไฟล์คนดู (win-author-profile) แคบเกินไป ขยายไม่ได้ แสดงแชทได้แค่ 2-3 ข้อความ ให้ขยายขนาดให้อ่านแชทได้จุใจ ปรับให้สามารถลากขยายหน้าต่างได้ (Resizable)
  4. นำปุ่ม "Export ข้อความ" ที่หายไปกลับมาวางไว้ข้างๆ ปุ่ม "ตั้งค่าการบล็อก"
  5. ทดสอบ Build ทั้งเวอร์ชัน Lite และ Full เตรียมพร้อมสำหรับการใช้งานจริง
- **สิ่งที่ดำเนินการปรับปรุงและแก้ไข:**
  1. **Event List Context Menu Auto-Dismiss & Label (`src/index.html`):**
     - เปลี่ยนป้ายเมนูเป็น `<span class="menu-icon">🗑️</span> ลบทั้งหมด`
     - เพิ่ม pointerdown / contextmenu global listener ที่จับการคลิกนอกกรอบเมนูเพื่อ auto-dismiss เมนูทันทีโดยไม่ค้าง
  2. **Resizable & Expanded Profile Modal (`src/index.html` & `src/styles.css`):**
     - เพิ่ม `resize: both; overflow: hidden;` และปรับขนาดเริ่มต้นเป็น `width: min(94vw, 680px); height: min(92vh, 760px); min-width: 480px; min-height: 520px;` ทั้งในหน้าต่างหลักและ Popout
     - ปรับคอนเทนเนอร์ข้อความแชท (`#paneProfTab1`) ให้ยืดขยายได้เต็มที่ (`flex: 1 1 auto; min-height: 260px;`) อ่านข้อความได้ต่อเนื่องหลายสิบข้อความโดยไม่อึดอัด
     - เพิ่มไอคอน resize grip ที่มุมขวาล่างของ `.floating-footer`
  3. **กู้คืนปุ่ม Export แชท (`src/index.html`):**
     - เพิ่ม `<button class="btn-topbar-action" id="btnExportUserChat" onclick="exportUserChatHistory(document.getElementById('profAuthorName').innerText, document.getElementById('profPlatformBadge').innerText)">📥 Export ข้อความ</button>` ข้างปุ่ม "ตั้งค่าการบล็อก"
  4. **การทดสอบอัตโนมัติ (Playwright Verification):**
     - เขียนสคริปต์ `scratch/verify_expanded_profile_and_menu.py`
     - ทดสอบครบ 11 ขั้นตอน: ตรวจสอบข้อความ "ลบทั้งหมด", คลิกนอกเมนูแล้วปิดอัตโนมัติ, คลิกลบกิจกรรมทั้งหมดสำเร็จ, เปิด Popout User Manager, เปิดโปรไฟล์ขนาด 680px พร้อม resize: both, ตรวจสอบปุ่ม Export ข้อความ และดาวน์โหลดไฟล์ `.txt` บันทึกแชทและกิจกรรมสำเร็จ 100%
  5. **Packaging & Build Testing:**
     - Build Lite Edition สำเร็จ: `BroadcastPlayroom3-Lite.exe` (~802 MB) ผ่าน `build_trial.py lite` ที่ `build_trials/trial-20261029-131839-579008/dist/BroadcastPlayroom3-Lite/`
     - Build Full Edition สำเร็จ: `BroadcastPlayroom3-Full.exe` (ขนาดรวม ~6.56 GB พร้อม PyTorch, CUDA, Fairseq และ RVC inference runtime ครบถ้วน) ผ่าน `build_trial.py full` ที่ `build_trials/trial-20261029-132051-575966/dist/BroadcastPlayroom3-Full/`

---

## [2026-10-29 13:05] — Antigravity (Event List UI Redesign, Platform Icons, Date Dividers & In-Popout Modal Layering)
- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผุ้ใช้:**
  1. ปรับปรุงดีไซน์ Event List ให้จัดวางสวยงาม เป็นระเบียบ ไม่ตัดคำมั่ว
  2. ใช้ไอคอนแพลตฟอร์มแทนข้อความ badge (Twitch, YouTube, TikTok, Kick, SOOP, MyLive, PromptPay, TrueMoney)
  3. คลิกขวาบนรายการกิจกรรมเพื่อเคลียร์ทั้งหมดออกได้
  4. มีเส้นคั่น Date Divider บอกว่าเป็นกิจกรรมของวันนี้ หรือเมื่อวานนี้ / วันที่ผ่านไป
  5. คลิกชื่อผู้ให้ใน Event List เพื่อเปิด User Manager ของคนนั้นได้
  6. แก้ไขหน้าต่างโปรไฟล์ถูก User Manager ทับ โดยให้โปรไฟล์อยู่บนสุดเสมอแม้จะเปิด Popout
- **สิ่งที่ดำเนินการปรับปรุง:**
  - ปรับ CSS & Layout ของ .event-box ใหม่ทั้งหมด แสดงไอคอนแพลตฟอร์ม, ชื่อคลิกได้, ยอดเงิน, ข้อความในกรอบ, และเวลา
  - ระบบ Date Dividers แบ่งกลุ่มวันนี้ / เมื่อวานนี้ / วันที่ย้อนหลัง พร้อม Context Menu คลิกขวาล้างรายการ
  - แก้ไข Window Layering ด้วยการ Adopt win-author-profile เข้าไปใน User Manager Popout Window Body โดยตรง พร้อม Backdrop และจัดกึ่งกลางอยู่บนสุด 100%
  - ผ่านการทดสอบ Playwright สำเร็จ 100% SUCCESS (scratch/verify_events_and_layering.py)

---

## [2026-10-29 12:35] — Antigravity (User Manager Lifetime Event Memory, Popout Window Layering & Chat Export)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. กิจกรรมสด (Donate, Sub, Follow, Bits, Super Chat ฯลฯ) ต้องจดจำลงแต่ละ User ที่กระทำในส่วน Event ของ User Manager โดยเก็บถาวรตลอดไป ห้ามลบเด็ดขาด (ส่วนของ chatlog หมดวันทีกำหนดยังพอลบได้ แต่ส่วนนี้ห้ามลบ)
  2. แก้ไขปัญหาหน้าต่างทับซ้อน (Window Layering): เมื่อกดเข้าโปรไฟล์ User เจาะจงจากหน้า User Manager ถูกหน้า User Manager ทับอยู่ข้างบนเสมอ เนื่องจากหน้า User อยู่ในโปรแกรมหลักแต่ User Manager เป็นหน้าต่างแยกนอกโปรแกรม
  3. เพิ่มปุ่ม Export ข้อความแชทและประวัติกิจกรรมทั้งหมดของ User เจาะจงคนนั้นออกมาเป็นไฟล์ (.txt) โดยวางปุ่มไว้ข้างๆ ปุ่ม "ตั้งค่าการบล็อก"
- **สิ่งที่ดำเนินการปรับปรุงและแก้ไข:**
  1. **สถาปัตยกรรมจดจำ Event ถาวรต่อ User (`src/user_controls.js`):**
     - ปรับฟังก์ชัน `registerUserToRoster(msg)` ให้ดักจับเหตุการณ์ `msg.event` ทุกประเภท (Super Chat, Gift, Bits, Sub, Follow, Donate ฯลฯ)
     - จัดเก็บข้อมูลอีเวนต์เข้าสู่ `person.events = [...(previous?.events || []), evRecord]` แยกชัดเจนจาก `person.history`
     - ปรับ `pruneViewerChatHistory()`: กำหนดให้ทำความสะอาดเฉพาะข้อความแชทธรรมดาที่เกิน 7 วัน (`CHAT_RETENTION_MS`) และยกเว้น `person.events` ถาวร ไม่มีการลบออกเด็ดขาดตามคำสั่งของผู้ใช้
     - ในหน้าโปรไฟล์เจาะจง (`openAuthorModal`): แท็บ 2 (ประวัติกิจกรรม) จะดึงข้อมูลจาก `person.events` มาเรนเดอร์พร้อมไอคอนประจำอีเวนต์ (💎, 👑, 🎁, 💰, ⭐, 💵, 🚀, ❤️), วันที่-เวลา, ยอดเงิน/จำนวน, และข้อความผู้ส่ง
  2. **แก้ปัญหา Layering & ปรับระบบ Popout อัตโนมัติ (`src/index.html` & `src/user_controls.js`):**
     - ตรวจสอบสถานะว่าหากหน้าต่าง `user-manager` เปิดอยู่ในโหมด Popout ภายนอก (`window._popoutWindows['user-manager']`) เมื่อคลิกเปิดโปรไฟล์เจาะจง `author-profile` ระบบจะเปิดหน้าต่าง Popout ย่อยของโปรไฟล์ออกมาอยู่ข้างๆ และเรียก `.focus()` ให้หน้าต่างโปรไฟล์ลอยอยู่ด้านหน้าเสมอ
     - สำหรับโหมดในหน้าต่างหลัก ได้ปรับ z-index ของ `win-author-profile` ให้สูงกว่า `win-user-manager` เสมอ (`Math.max(highestZ, 2500) + 20`) ป้องกันการถูกบดบัง
  3. **เพิ่มปุ่ม Export แชท & กิจกรรมรายบุคคล (`src/index.html` & `src/user_controls.js`):**
     - เพิ่มปุ่ม `<button class="btn-topbar-action" id="btnExportUserChat">📥 Export แชท</button>` วางข้างปุ่ม `🛑 ตั้งค่าการบล็อก` ในแถบควบคุมด้านล่าง (`.floating-footer`)
     - เขียนฟังก์ชัน `window.exportUserChatHistory(username, platform)`: รวมประวัติข้อความแชทและกิจกรรมทั้งหมดตามลำดับเวลา จัดรูปแบบพร้อม Header รายละเอียดผู้ชม ยอดรวมข้อความ และยอดรวมกิจกรรม แล้วดาวน์โหลดเป็นไฟล์ `.txt` (`chat_{username}_{timestamp}.txt`)
  4. **การทดสอบความถูกต้อง (Automated Verification):**
     - สร้างสคริปต์ทดสอบ `scratch/verify_popout_user_manager.py` ด้วย Playwright:
       - จำลองผู้ใช้ส่ง Super Chat ฿1,000 และข้อความแชท
       - เปิด User Manager ในหน้าต่าง Popout
       - คลิกเปิด Author Profile ตรวจสอบว่าหน้าต่างโปรไฟล์เปิดขึ้นมาด้านหน้าสำเร็จ (Title: `โปรไฟล์ผู้ชม - Broadcast Playroom 3`)
       - ตรวจสอบแท็บประวัติกิจกรรม แสดงยอด ฿1,000 พร้อมไอคอนและข้อความโดเนทครบถ้วน
       - ทดสอบคลิกปุ่ม Export แชท และตรวจสอบเนื้อหาไฟล์ `.txt` ที่ดาวน์โหลดออกมา
       - ทดสอบรัน `pruneViewerChatHistory(now + 30 days)` ยืนยันว่าข้อความแชทถูกเคลียร์ตามกำหนดเวลา แต่อีเวนต์กิจกรรมสดใน `person.events` ยังคงอยู่ครบ 100%
     - บันทึกภาพหลักฐาน: `verified_user_manager_events_tab.png` และไฟล์ `downloaded_test_chat.txt`

---

## [2026-10-29 12:12] — Antigravity (Live Events Feed Comprehensive Multi-Platform Testing & Dynamic Rendering)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ทดสอบช่องกิจกรรมสด (Events Panel) ว่าหากเกิดเหตุการณ์ที่มีคน Donate, Sub, Follow, Donate Bits ฯลฯ ในแต่ละแพลตฟอร์ม สามารถแสดงผลข้อมูลขึ้นมาได้จริงหรือไม่
  - นำทุก event ที่เกิดขึ้นจากช่อง Live สตรีมทั้งหมดมาทดสอบ
- **สิ่งที่ดำเนินการปรับปรุงและทดสอบ:**
  1. **เพิ่มความครอบคลุมของ Event Types & Dynamic UI ใน `appendActivityEvent` (`src/index.html`):**
     - รองรับประเภทกิจกรรมครอบคลุมทุกแพลตฟอร์มหลัก:
       - **Twitch:** `bits` (ส่งบิต Bits), `cheer` (ส่งบิต Cheer), `sub` (สมัครสมาชิก), `resub` (ต่ออายุสมาชิก), `subgift` (มอบของขวัญสมาชิก), `raid` (พาผู้ชมเข้ามา Raid), `follow` (กดติดตาม), `redeem` (แลกของรางวัล)
       - **YouTube Live:** `superchat` (ส่ง Super Chat), `supersticker` (ส่ง Super Sticker), `member` / `membership` (สมัครสมาชิก Member), `subgift` (มอบของขวัญสมาชิก)
       - **TikTok Live:** `gift` (ส่งของขวัญ เช่น กุหลาบ/ราชสีห์), `follow` (กดติดตาม), `like` (กดถูกใจไลฟ์), `share` (แชร์ไลฟ์สด)
       - **Kick:** `sub`, `resub`, `subgift`, `follow`
       - **Donations (PromptPay, TrueMoney, TipMe):** `donation`, `donate`, `tip`
       - **อื่นๆ:** `stars` (ส่งดาว), `giveaway_winner` (ชนะ Giveaway)
     - **ไอคอนและสีสันประจำกิจกรรม (Event Icons & Badges):** กำหนดไอคอนเฉพาะตามประเภท (💎 Bits, 👑 Sub/Member, 🎁 Gift, 💰 SuperChat, ⭐ Follow, 💵 Donation, 🚀 Raid, ❤️ Like, 📢 Share ฯลฯ) พร้อมพื้นหลังสีเฉพาะกิจกรรม
     - **ป้ายแสดงแพลตฟอร์ม (Platform Brand Tags):** แสดงแท็กสีตามแบรนด์ Twitch (ม่วง), YouTube (แดง), TikTok (ฟ้า), Kick (เขียว), PromptPay (เหลืองส้ม), TrueMoney (ส้ม)
     - **ป้ายแสดงยอดเงิน / จำนวน / รายละเอียด (Amount / Details Pill):** แสดงยอดเงิน (`฿300.00`, `฿500.00`), จำนวนบิต (`500 Bits`), ของขวัญพร้อมจำนวน (`🌹 ดอกกุหลาบ x10`), จำนวนเดือน (`12 เดือน`), หรือจำนวนผู้ชมเรด (`128 ผู้ชม`) ไฮไลต์ชัดเจน
  2. **ปุ่มจำลองกิจกรรมสด (`🧪 ทดสอบ`):**
     - ติดตั้งปุ่ม `🧪 ทดสอบ` บนหัวแถบกิจกรรมสด (`.events-header`) เพื่อให้ผู้ใช้สามารถคลิกทดสอบยิงเหตุการณ์จำลองได้ทุกเมื่อ
     - ฟังก์ชัน `testTriggerAllActivityEvents()` ถูกเชื่อมเข้าสู่ `window` พร้อมใช้งาน
  3. **Backend Injection Endpoint (`launch_dev.py`):**
     - เพิ่ม Endpoint `POST /api/messages/inject` รองรับการรับ `ChatMessage` และส่งต่อเข้า `chat_bridge._on_message` สำหรับการทดสอบ Backend Integration
  4. **การทดสอบความถูกต้อง (Automated Verification):**
     - ทดสอบผ่าน `scratch/verify_events.py` ด้วย Playwright:
       - คลิกปุ่มทดสอบ -> ตรวจสอบว่ามีอีเวนต์แสดงครบถ้วน 16 รายการ
       - ตรวจสอบความถูกต้องของข้อความ ยอดเงิน ป้ายแพลตฟอร์ม และชื่อผู้ส่งของทุกแพลตฟอร์ม
       - บันทึกภาพถ่ายหลักฐาน: `verified_live_events_feed.png` และ `verified_live_events_crop.png`
     - ทดสอบ Backend Data Ingestion ผ่าน `scratch/test_bridge_events.py` สำเร็จ 100%

---

## [2026-10-29 11:45] — Antigravity (Left Server Rail Hide/Unhide Context Menu & LocalStorage Persistence)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - เมนูด้านซ้าย (Server Rail) ต้องการให้คลิกขวาที่ปุ่มเพื่อ ซ่อน / เลิกซ่อน ได้
  - เมื่อคลิกขวาที่ว่างของแถบเมนูด้านซ้าย ให้มีเมนูคืนค่าปุ่มที่ซ่อนกลับมาแสดงได้
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **สถาปัตยกรรม Hide/Unhide ของ Server Rail (`src/index.html`):**
     - กำหนด `_railHideableMeta` ครอบคลุมปุ่มเครื่องมือทั้งหมดบน Server Rail:
       - `voice-settings`: 🎤 ตั้งค่าเสียงอ่าน
       - `composer`: 🎬 Overlay Composer Studio
       - `chat-widget`: 🎨 Chat Widget
       - `playroom`: 🎮 Playroom
       - `gw`: 🎁 สุ่มแจกของรางวัล (Giveaway)
       - `replie`: 🖼️ ตอบกลับรูปภาพ (Replie)
       - `ask`: 📊 โพลคำถามสด (ASK)
       - `randomizer`: 🎰 วงล้อสุ่มด่วน (Randomizer)
       - `user-manager`: 👥 จัดการรายชื่อคนดู (Viewer)
     - ป้องกันความปลอดภัยสำหรับปุ่มฟันเฟืองตั้งค่าหลัก (`btnRailSettings`) และปุ่มอัปเดต (`btnRailUpdate`) ไม่ให้สามารถซ่อนได้ เพื่อป้องกันไม่ให้ผู้ใช้ถูกล็อกไม่สามารถเข้าหน้าตั้งค่าได้
  2. **เมนูคลิกขวาบริบท (Custom Context Menu):**
     - เมื่อคลิกขวาบนปุ่มเครื่องมือ:
       - แสดงปุ่ม "🚀 เปิดหน้าต่างเครื่องมือนี้"
       - แสดงปุ่ม "🚫 ซ่อนปุ่ม [ชื่อเครื่องมือ]"
       - หากมีปุ่มอื่นที่ถูกซ่อนอยู่ จะมีแถบย่อยให้กดคืนค่าปุ่มเหล่านั้นได้ทันที
     - เมื่อคลิกขวาบนพื้นที่ว่างของแถบ Server Rail (รวมถึง Flex Spacer):
       - แสดงหัวข้อ "👁️ คืนค่าปุ่มแถบซ้ายที่ซ่อน ([จำนวนที่ซ่อน])"
       - รายการปุ่มที่ถูกซ่อนแต่ละปุ่ม พร้อมปุ่มกด "+ แสดง [ชื่อ]" เพื่อคืนค่ารายปุ่ม
       - ปุ่มลัด "✨ คืนค่าแสดงทุกปุ่มที่ซ่อน" เพื่อนำทุกปุ่มกลับมาแสดงทั้งหมดในคลิกเดียว
  3. **การบันทึกสถานะคงทน (Persistence):**
     - บันทึกรายการปุ่มที่ซ่อนลงใน `localStorage` ภายใต้คีย์ `bp3_rail_hidden`
     - เรียก `applyRailHiddenState()` อัตโนมัติเมื่อหน้าต่างโหลดเสร็จใน `DOMContentLoaded` ทำให้ปุ่มที่ซ่อนยังคงถูกซ่อนอย่างถูกต้องแม้ปิดหรือเปิดโปรแกรมใหม่
  4. **Build & Automated Verification:**
     - รัน `npm run build` คอมไพล์เข้า `dist/index.html` และซิงค์ assets เรียบร้อย
     - ทดสอบผ่าน Playwright E2E: คลิกขวาปุ่ม ASK -> ซ่อน -> ตรวจสอบว่าปุ่มหายไปและค่าบันทึกลง `localStorage` -> คลิกขวาที่ว่างบน Rail -> เมนูคืนค่าแสดงรายการ ASK -> กดคืนค่า -> ตรวจสอบว่าปุ่มกลับมาแสดงผลสมบูรณ์

---

## [2026-10-29 11:27] — Antigravity (Fast Instant Splash & Topbar RVC Status Badge with lp-boil & tx-hanging-sway)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - หน้า Splash ไม่ควรช้า ให้เปิดหน้าต่างหลักขึ้นมาอย่างรวดเร็วเหมือนเดิม แล้วให้โมเดล RVC ไปโหลดต่อในเบื้องหลังหลังจากเปิดโปรแกรมแล้ว
  - เพิ่มช่องสถานะ RVC ด้านบนข้างขวาของปุ่มสลับเสียงเพศ (ชาย/หญิง)
  - ใช้อนิเมชัน `lp-boil` (https://motion-reference.takayustudio.jp/#motion=lp-boil) ขณะกำลังโหลด RVC และเมื่อ hover ให้แสดงข้อความ `"กำลังเตรียมโมเดล RVC"`
  - เมื่อโหลดเสร็จ ให้ใช้อนิเมชัน `tx-hanging-sway` (https://motion-reference.takayustudio.jp/#motion=tx-hanging-sway) ในป้ายเขียนว่า `"RVC"` และเมื่อ hover ให้แสดงข้อความ `"RVC กำลังใช้งาน [ชื่อโมเดล]"`
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **คืนความเร็วสูงสุดให้ Splash Screen (`launch_dev.py`):**
     - นำการรอ Worker Thread ออกจากหน้าต่าง Splash Screen ทำให้โปรแกรมเปิดเข้าหน้าต่างหลักได้ทันทีอย่างรวดเร็ว (< 1 วินาที) โดยปล่อยให้การโหลด RVC ทำงานคู่ขนานใน Background Thread
  2. **สร้าง Topbar RVC Indicator Badge (`#topbarRvcBadge`):**
     - วางตำแหน่งป้ายไว้ด้านขวาของ `.topbar-gender-switch` (ระหว่างปุ่มสลับเพศเสียงและปุ่มเปิด/ปิด Master TTS)
     - มีไฟบอกสถานะ `.rvc-badge-dot` และข้อความ `.rvc-badge-text` แสดงคำว่า `"RVC"`
     - คลิกที่ป้ายเพื่อเป็นทางลัดเปิดหน้าต่างตั้งค่าเสียง RVC ได้ทันที
  3. **การออกแบบอนิเมชันตามสเปกของ TakayuStudio (Zero GPU Lockup):**
     - **ขณะโหลด (`.rvc-loading`):** ใช้อนิเมชัน `bp3-rvc-lp-boil` เลียนแบบสไตล์ hand-drawn frame-by-frame boil effect สั่นไหวแบบอินทรีย์สุ่มเล็กน้อย พร้อมกรอบสีเหลือง/อำพัน และ Tooltip `"กำลังเตรียมโมเดล RVC"`
     - **เมื่อพร้อมใช้งาน (`.rvc-ready`):** ใช้อนิเมชัน `bp3-rvc-tx-hanging-sway` โดยมี `transform-origin: 50% 0%` แกว่งแบบป้ายแขวนตามฟิสิกส์ลูกตุ้ม (1.5 วินาที) แล้วหยุดนิ่งสนิทที่ 0 องศา ปล่อย GPU สู่สถานะ Idle 0% ไม่มีการวนลูปให้กินพลังงานการ์ดจอ
     - เมื่อ Hover ที่ป้าย จะมีเอฟเฟกต์แกว่งนุ่มนวลอีกครั้ง พร้อม Tooltip ไดนามิก เช่น `"RVC กำลังใช้งาน lumine-jp"`
  4. **ระบบ Smart Status Polling (`src/rvc_controls.js`):**
     - ปรับให้ Poller ตรวจสอบสถานะ RVC ต่อเนื่องทุก 400ms เฉพาะในช่วงที่สถานะเป็น `loading` หรือ `downloading` แม้ผู้ใช้จะไม่ได้เปิดหน้าต่างตั้งค่าค้างไว้
     - ทันทีที่โมเดลโหลดเสร็จ ป้ายจะเปลี่ยนเป็น `.rvc-ready` ทันที และระบบจะหยุดการ Polling ลงโดยอัตโนมัติเพื่อประหยัดทรัพยากร
- **ผลการทดสอบ (Verification Results):**
  - ทดสอบผ่าน Playwright บันทึกภาพ Screenshot ตรวจสอบความถูกต้องสมบูรณ์ (`verified_rvc_topbar_badge.png`) ป้าย RVC วางตำแหน่งถูกต้องสวยงาม แสดงผลและอนิเมชันครบถ้วน
  - Rebuild `dist/` เรียบร้อย 100%

---

## [2026-10-29 11:18] — Antigravity (Fix First Message RVC Cold-Start & Autoplay Voice Fallback)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ข้อความแรกหลังจากเปิดโปรแกรมมา มักจะกลายเป็น "เสียงสำรอง" (Browser Web Speech Fallback) หรือไม่อ่านเลย ต้องพิมพ์ประโยคต่อๆ ไปถึงจะอ่านได้ตามปกติ เกิดจาก RVC เตรียมตัวไม่เสร็จหรืออย่างไร
- **การวิเคราะห์สาเหตุ (Root Cause Analysis):**
  1. *RVC Model Loading Race Condition:*
     - เมื่อเริ่มโปรแกรม `rvc_service.select()` ถูกเรียกใน Background Worker Thread เพื่อโหลดโมเดล PyTorch / RMVPE / HuBERT (เช่น `lumine-jp.pth`) ซึ่งใช้เวลาประมาณ 3-5 วินาที
     - เมื่อผู้ใช้ส่งข้อความแรกเข้ามาในขณะที่โมเดลกำลังโหลด ฟังก์ชัน `convert()` เดิมตรวจสอบ `enabled = self.data['enabled'] and self.data['loaded']` ซึ่งเป็น `False` อยู่ จึงข้ามการแปลง RVC และส่งเสียงดิบของ Edge-TTS กลับไปทันทีโดยไม่รอ
  2. *Chromium Autoplay Policy Blocking:*
     - หน้าต่างเบราว์เซอร์ที่เปิดผ่าน `--app` โหมด หากผู้ใช้ยังไม่ได้คลิกหรือสัมผัสหน้าจอ คำสั่ง `audio.play()` จะถูกเบราว์เซอร์บล็อกด้วย `NotAllowedError` (ต้องมี User Gesture ก่อน)
     - เมื่อถูกบล็อก ฝั่งหน้าเว็บจะเข้าเงื่อนไข `catch()` และเรียก `speakTextViaWebSpeechFallback()` ทันที ทำให้แถบสถานะแสดงคำว่า **"เสียงสำรอง"** และพยายามพูดด้วยเสียงหุ่นยนต์พื้นฐานของ Windows แทน
  3. *PyTorch CUDA Cold-Start Latency:*
     - การประมวลผล RVC ครั้งแรกสุดใช้เวลานาน (6.36 วินาทีตามภาพ) เพราะ PyTorch ยังไม่ได้วอร์มหน่วยความจำและ CUDA Kernel
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **แก้ปัญหา RVC Race Condition ใน `rvc_service.py`:**
     - ในฟังก์ชัน `convert()`: หากโมเดลอยู่ในสถานะ `loading` และ Worker Thread ยังทำงานอยู่ ให้รอด้วย `worker.join(timeout=10.0)` เพื่อให้โมเดลโหลดเสร็จสมบูรณ์ แทนที่จะทิ้งการแปลง RVC ไป
     - เพิ่ม **Silent Warmup Buffer** ขนาด 0.5 วินาทีในขั้นตอน `load()` เพื่อให้ PyTorch CUDA Kernels ถูกคอมไพล์และพร้อมใช้งานล่วงหน้าทันทีตั้งแต่ตอนเริ่มโปรแกรม
  2. **แก้ปัญหา Autoplay Policy ใน `launch_dev.py`:**
     - เพิ่มแฟล็ก `--autoplay-policy=no-user-gesture-required` ให้กับ Chromium/Chrome เพื่ออนุญาตให้แอปพลิเคชันเล่นเสียงแจ้งเตือนและเสียง TTS ได้ทันทีตั้งแต่ข้อความแรกโดยไม่ต้องรอคลิกหน้าต่างก่อน
     - ในขั้นตอน Splash Screen: เพิ่มการรอ Worker Thread ของ RVC ชั่วครู่ (`splash_ctrl.set_progress(80, "กำลังเตรียมโมเดลเสียง RVC...")`) เพื่อให้โมเดลพร้อมตั้งแต่ก่อนหน้าต่างหลักจะปรากฏ
- **ผลการทดสอบ (Verification Results):**
  - เขียนและรันการทดสอบ `tests/verify_rvc_startup_readiness.py`:
    - ยืนยันว่า `convert()` รอ Worker สำเร็จและทำการแปลงเสียงออกมาเป็น `audio/wav` 44.1kHz (Lumine Voice) ขนาด 172.9 KB สมบูรณ์แบบ 100% (PASS)
    - อินเฟอเรนซ์หลังการวอร์มใช้เวลาเพียง 0.24-0.44 วินาที

---

## [2026-10-29 11:06] — Antigravity (Fix Multilingual TTS Audio Reading for Mixed Languages)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - แจ้งเจอบั๊ก TTS: เวลาพิมพ์ ไทย อังกฤษ สามารถอ่านได้ตามปกติด้วยโมเดลภาษาไทย แต่พอพิมพ์ภาษาไทยแล้วตามด้วยภาษาอื่น เช่น ญี่ปุ่น (เช่น "สวัสดีครับ こんにちは") ระบบอ่านแค่ภาษาไทยแล้วเงียบไปเลย ไม่เอาโมเดลเจ้าของภาษานั้นมาอ่านต่อให้
- **การวิเคราะห์สาเหตุ (Root Cause Analysis):**
  1. *การเลือกโมเดลภาษาแบบเหมาทั้งข้อความ (Single Voice Assumption):*
     - ใน `tts_service.py` เดิม ฟังก์ชัน `resolve_voice()` ทำการตรวจจับภาษาทั้งประโยค เมื่อพบตัวอักษรไทย (`re.search(r'[฀-๿]', text)`) ระบบจะส่งคืนเสียงภาษาไทย (`th-TH-PremwadeeNeural` หรือ `th-TH-NiwatNeural`) เพียงเสียงเดียวให้ประมวลผลทั้งข้อความ
     - โมเดล Neural Voice ภาษาไทยของ Edge-TTS ไม่รองรับชุดตัวอักษรคันจิ/ฮิรางานะ/คาตาคานะของญี่ปุ่น หรือฮันกึลของเกาหลี ทำให้โมเดลข้ามอักขระเหล่านั้นหรือหยุดอ่านเงียบไป
  2. *ขาดระบบแยก Segment ตามภาษา (Language Segment Splitting & Concurrent Synthesis):*
     - ขาดการแยกข้อความเป็นส่วนย่อยตามตระกูลภาษาแบบเดียวกับ `_synth_mixed_voice` ในเวอร์ชันเดิม (`chat_queue.py`)
- **สิ่งที่ดำเนินการแก้ไข:**
  1. **เพิ่มฟังก์ชัน `split_text_by_language(text)` ใน `tts_service.py`:**
     - ตรวจสอบรหัสภาษาของแต่ละตัวอักษรผ่าน `_char_lang(ch)` ใน `language_detect.py`
     - กำหนดให้ภาษาอังกฤษ (`en`) รวมเข้ากับกลุ่มภาษาไทย (`th`) เพื่อให้อ่านด้วยโมเดลภาษาไทยสำเนียงไทยไปพร้อมกันโดยไม่ตัดท่อนคำ (ตามพฤติกรรมเดิมที่ต้องการ)
     - ภาษาอื่น เช่น ญี่ปุ่น (`ja`), เกาหลี (`ko`), จีน (`zh`/`zh-TW`), ฝรั่งเศส (`fr`) จะถูกแยกเป็น Segment อิสระสำหรับส่งให้โมเดลของภาษานั้นๆ อ่าน
     - อักขระจำพวกตัวเลข วรรคตอน เครื่องหมายตกใจ และ Emoji จะถูกคงไว้กับ Segment ก่อนหน้าอย่างเป็นธรรมชาติ
  2. **ระบบสังเคราะห์เสียงแบบคู่ขนาน (Concurrent Segment Synthesis):**
     - หากมีหลายภาษาในข้อความเดียวกัน ระบบจะเรียก `asyncio.gather()` เพื่อสังเคราะห์เสียงแต่ละ Segment พร้อมกันแบบขนาน ช่วยประหยัดเวลาและให้เสียงตอบสนองรวดเร็วเทียบเท่าการเรียกครั้งเดียว
  3. **การต่อผสานไฟล์เสียง (Audio Segment Merging with Silence Trimming):**
     - สร้างฟังก์ชัน `merge_audio_segments()` ตัดเสียงเงียบท้ายประโยค (Trailing Silence Trim) ของแต่ละส่วนออก พร้อมแทรกช่องว่างธรรมชาติสั้นๆ (50ms gap) เพื่อให้เสียงรอยต่อระหว่างสองภาษาลื่นไหลเป็นธรรมชาติ ไม่กระตุกหรือทิ้งช่วงนานเกินไป
     - มีระบบสำรอง Fallback ต่อไบต์ดิบของ MP3 โดยอัตโนมัติหากไม่มี soundfile/numpy
  4. **อัปเดตโมเดลเสียงใน `VOICES`:**
     - เพิ่มเสียงโมเดลจีนไต้หวัน (`zh-TW-HsiaoChenNeural` / `zh-TW-YunJheNeural`)
     - รองรับการปรับเพศเสียง (หญิง/ชาย) ทั้งในส่วนภาษาไทยและภาษาต่างประเทศครบทุกภาษา
- **ผลการทดสอบ (Verification Results):**
  - รันการทดสอบ Unit Tests ใน `tests/test_multilingual_tts.py` ผ่านครบ 7/7 การทดสอบ (PASS 100%)
  - รันการทดสอบ Matrix รวมทั้งเสียงหญิง/ชาย และหลากหลายภาษา (ไทย+ญี่ปุ่น, อังกฤษ+เกาหลี, ไทย+จีน) เสียงถูกสร้างขึ้นครบถ้วนถูกต้อง ความยาวและขนาดของไฟล์เสียงสมบูรณ์ ได้แก่:
    - `female | สวัสดีครับ こんにちは -> 14,304 bytes, 1.97s`
    - `female | Hello everyone 안녕하세요 -> 16,008 bytes, 2.32s`
    - `female | ขอบคุณมากครับ 谢谢 -> 12,480 bytes, 1.78s`
    - `male   | สวัสดีครับ こんにちは -> 11,904 bytes, 1.60s`
    - `male   | Hello everyone 안녕하세요 -> 13,152 bytes, 1.98s`
    - `male   | ขอบคุณมากครับ 谢谢 -> 10,608 bytes, 1.58s`
  - รัน `python -m unittest test_translation_pipeline.py` ผ่าน 4/4 การทดสอบ (PASS 100%)

---

## [2026-10-29 10:24] — Antigravity (Fix Splash Screen Auto-Dismiss On App Ready)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - แก้ไขหน้าต่าง Splash Screen ที่ยังค้างอยู่บนหน้าจอเมื่อหน้าต่างโปรแกรมหลักเปิดและโหลดขึ้นมาเสร็จแล้ว
- **สิ่งที่ดำเนินการแก้ไข:**
  - เพิ่ม API `/api/splash/close` ใน `launch_dev.py` และเรียกใช้จาก `src/index.html` ทันทีที่ `DOMContentLoaded`
  - เพิ่ม Watchdog Timer 7 วินาทีใน `splash.py` และปรับปรุง `sys.stdin.readline()`
  - ผ่านการทดสอบเรียบร้อย 100%

---

## [2026-10-29 02:59] — Antigravity (Seamless Integrated Titlebar Matching Discord & Antigravity Style)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ปรับแถบหัวหน้าต่างด้านบนให้กลมกลืนกับธีมของโปรแกรมแบบ Discord หรือ Antigravity
- **สิ่งที่ดำเนินการแก้ไข:**
  - เพิ่ม Web App Manifest และเชื่อมต่อ Window Controls Overlay
  - ซิงค์สี `<meta name="theme-color">` กับ Sidebar Rail ของแต่ละธีมแบบไดนามิก
  - เพิ่ม Titlebar Brand Badge (โลโก้ + ชื่อโปรแกรม) รองรับ window drag

---

## [2026-10-29 02:40] — Antigravity (Hide Twitch Chatbot Notice When Twitch Not Connected)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ซ่อนข้อความแจ้งเตือน Twitch Chatbot ด้านล่างแชทสด หากผู้ใช้ไม่ได้เชื่อมต่อ Twitch
- **สิ่งที่ดำเนินการแก้ไข:**
  - เพิ่ม `updateChatInputVisibility()` ซ่อน `#chatInputUnavailable` ถ้า Twitch ไม่ได้เชื่อมต่อ

---

## [2026-10-29 01:30] — Antigravity (Installer Architecture Plan, Edition Icons & 500px Fast Splash Screen)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - วางแผนสถาปัตยกรรมตัวติดตั้ง Installer Coexistence, UAC Exclusion และสร้างไอคอน+สแปลช 500px
- **สิ่งที่ดำเนินการแก้ไข:**
  - สร้าง `INSTALLER_SPEC.md` และ `installer/setup_template.iss`
  - แปลงไอคอน `bp-full-icon.ico`, `bp-lite-icon.ico` และภาพสแปลช `assets/splash/splash_500.png`

---

## [2026-10-28 22:00] — Antigravity (Fix Game Overlay Settings Not Opening on Edit Mode Click)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ผู้ใช้แจ้งว่าเมื่อกดปุ่ม "⚙️ ตั้งค่า" ในโหมดแก้ไข (Edit Mode) ของ Game Overlay แล้วไม่มีอะไรเกิดขึ้น
- **สาเหตุที่พบ:**
  1. ตัวแปร `_autoPopoutWindows = true` สั่งให้เครื่องมือทุกตัวพยายามเปิดหน้าต่างแบบ `window.open` (Popout Window) แต่เนื่องจากสัญญาณ `DESKTOP_OVERLAY_SETTINGS` มาจาก Event Polling (HTTP Polling) ซึ่งไม่ใช่ Direct User Gesture บนเบราว์เซอร์ จึงถูก Popup Blocker บล็อก
  2. เมื่อถูกบล็อก ระบบตกกลับมาเปิดแบบ In-App Window แต่ในแท็ก `<div id="win-game-overlay">` มีการใส่ inline style `display: none;` ไว้อยู่ ทำให้คลาส `.active` ไม่สามารถแสดงผลหน้าต่างได้
  3. ขณะผู้ใช้กดปุ่มตั้งค่าบน Game Overlay (Desktop Qt Window) หน้าต่างแอปหลัก (Chrome/Edge) มักจะอยู่ในสถานะ Background/Minimized ทำให้ผู้ใช้มองไม่เห็นหน้าต่างที่เปิดขึ้น
  4. ฟังก์ชัน `loadGameOverlaySettings` และ `switchGameOverlayTab` อ้างอิงผ่าน `document.getElementById` โดยตรง ซึ่งไม่ครอบคลุมกรณีที่หน้าต่างถูก Popout ไปยังเอกสารลูก (`pop.document`)
- **สิ่งที่เปลี่ยนแปลง:**
  1. `desktop_overlay_service.py`:
     - เพิ่มฟังก์ชัน `_bring_app_to_front()` โดยใช้ Win32 API (`EnumWindows`, `ShowWindow(SW_RESTORE)`, `SetForegroundWindow`) เพื่อยกหน้าต่าง Broadcast Playroom 3 ขึ้นมาข้างหน้าผู้ใช้ทันทีเมื่อมีคำสั่ง `open_settings`
  2. `src/modal.css`:
     - กำหนด `.floating-window.active { display: flex !important; }` เพื่อให้คลาส active แสดงผลหน้าต่างได้เสมอ
  3. `src/index.html`:
     - ลบ inline `display: none;` ออกจาก `<div class="floating-window" id="win-game-overlay">`
     - เพิ่ม `'game-overlay'` ในตาราง `defaultSizes` (760x620) และ `titles` ('ตั้งค่า Game Overlay') ของ `popoutToolWindow`
     - ปรับปรุง fallback ใน `popoutToolWindow` ให้เซ็ต `display = 'flex'` และ `zIndex = ++highestZ` ชัดเจน
     - สร้าง `getGameOverlayDoc()` เชื่อมต่อ `getToolDocument('game-overlay')` ครอบคลุมการอ่าน/เขียน Element ในทุกกรณี (ทั้ง Docked ในหน้าต่างหลัก และ Detached Popout)
  4. `src/desktop_overlay_controls.js`:
     - ปรับ `openDesktopOverlaySettings()` ให้ปลด `minimized`, สลับ `display: flex`, ดึงหน้าต่างมาแสดง และเรียก `window.focus()`
- **ผลการตรวจสอบ (Verification Results):**
  - รัน `scratch/verify_unified_tts_and_overlay.py` ผ่าน 100%
  - รันการทดสอบจำลองเหตุการณ์ `DESKTOP_OVERLAY_SETTINGS` ใน Playwright ยืนยันว่าหน้าต่างเปิดและ visible = True (`display: 'flex'`, ขนาด 760x620) สมบูรณ์
  - บิลด์และซิงค์ `dist/` เรียบร้อย

---

## [2026-10-28 21:10] — Antigravity (Unified Voice TTS Settings, Female Pitch Bug Fix & Floating Game Overlay Window)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. หน้าต่างตั้งค่าเสียง TTS ใน Sidebar ('#win-voice-settings') และ Settings > เสียงอ่าน ('#sec-tts') มีตัวเลือกไม่เท่ากัน และหน้าตาไม่สอดคล้องกัน
  2. สิ่งที่ต้องมีและจัดวางให้ตรงกัน:
     - ตัวเลือกเสียง หญิง / ชาย ไม่ต้องมีชื่อโมเดลเขียนกำกับ
     - Master Volume ในการอ่านเสียง
     - ตัวปรับ Speed (-50% ถึง +50%) และ Pitch (-24 ถึง +24 st) โดยถ้าเป็นเวอร์ชัน Lite ต้องไม่มีตัวปรับ Pitch
     - ตัวเลือกโมเดลเสียง AI RVC (กรณีเวอร์ชัน FULL) พร้อมปุ่มเปิด/ปิด และจัดการโมเดล
     - กล่องทดสอบอ่านเสียง (พิมพ์ข้อความ + กดฟัง)
     - เช็กบ็อกซ์ติ๊กว่าจะอ่านชื่อคนดูก่อนข้อความแชทหรือไม่
  3. บั๊กเสียงหญิงกลายเป็นเสียงชาย: เมื่อตั้งค่า Speed +50% และ Pitch +50% พบว่าเสียงเปลี่ยนเป็นเสียงผู้ชาย
  4. การตั้งค่า Game Overlay เมื่อกด 'ตั้งค่า' ในโหมด Edit ของ Game Overlay ถูกนำไปแสดงแบบไม่สวยงามใน Settings > Dock & Web URL ต้องการให้แยกเป็นหน้าต่างตั้งค่าอิสระ (Floating Window) เหมือนเดิม
- **สิ่งที่เปลี่ยนแปลง:**
  1. `tts_service.py`:
     - แก้ไขฟังก์ชัน `clean_prosody(val, default_unit)` โดยใช้ Regex สกัดเฉพาะตัวเลข (`([+-]?\s*\d+)`) และตัดหน่วยแปลกปลอม (เช่น `%` หรือ `st` ที่ส่งเข้ามาใน pitch) ก่อนต่อหน่วยที่ Azure Edge-TTS รองรับ (`Hz` สำหรับ pitch และ `%` สำหรับ rate)
     - ป้องกันไม่ให้เกิด Error `ValueError: Invalid pitch '+50%Hz'` ซึ่งเป็นสาเหตุให้ Edge-TTS ล้มเหลวและเบราว์เซอร์ตกไปใช้ Web Speech API เสียง Niwat (ชาย) สำรอง
     - ทดสอบแล้วสังเคราะห์เสียงหญิง Premwadee ด้วย Speed +50% และ Pitch +50% ได้ไฟล์เสียงสมบูรณ์ (10,224 ไบต์)
  2. `src/index.html`:
     - ออกแบบการ์ด Settings > เสียงอ่าน (`#sec-tts`) ใหม่ทั้งหมดเป็น 4 การ์ดโมเดิร์นคลีน สอดคล้องกับหน้าต่าง Sidebar (`#win-voice-settings`):
       - การ์ด 1: เพศเสียงอ่าน (ปุ่ม '👩 หญิง' และ '👨 ชาย' ไม่มีชื่อโมเดล, เช็กบ็อกซ์เสียงสลับ, เช็กบ็อกซ์อ่านชื่อคนดูก่อนพูด)
       - การ์ด 2: โมเดลเสียง AI RVC (`data-feature="rvc"`)
       - การ์ด 3: ปรับแต่งเสียง (Master Volume, Speed, และ Pitch กำกับ `data-feature="pitch"`)
       - การ์ด 4: กล่องทดลองพิมพ์และอ่านสด
     - เพิ่มเช็กบ็อกซ์อ่านชื่อคนดู (`#winChkReadAuthorName`) ในหน้าต่าง `#win-voice-settings`
     - ซิงค์คอนโทรลเลอร์สองทิศทาง (`syncVoiceVolume`, `syncVoiceSpeed`, `syncVoicePitch`, `toggleMixedVoice`, `toggleReadAuthorPref`, `playVoiceTest`)
     - สร้างหน้าต่างตั้งค่าอิสระ `#win-game-overlay` พร้อมแท็บ 3 แท็บ (🎮 Game Overlay, 👥 Viewer Overlay, 🪟 Overlay+) ตามรูปแบบดั้งเดิม สอดคล้องกฎ Zero GPU Lockup
  3. `src/desktop_overlay_controls.js`:
     - ปรับปรุงฟังก์ชัน `openDesktopOverlaySettings(tab)` ให้เปิดหน้าต่าง `#win-game-overlay` ดึงค่าจาก `/api/desktop-overlays` และบันทึกผ่าน `saveGameOverlaySettings()` โดยไม่ต้องฉีด DOM เข้าไปใน Setting Docks
  4. `src/rvc_controls.js`:
     - อัปเดตให้ค้นหาและโหลดโมเดล RVC ลงทั้ง `#winRvcSelect` และ `#secRvcSelect`
     - เพิ่มการตรวจสอบและซ่อนองค์ประกอบที่มีแอตทริบิวต์ `[data-feature="pitch"]` อัตโนมัติเมื่อเป็นเวอร์ชัน Lite (`capability.edition !== 'full'`)
  5. `launch_dev.py`:
     - อัปเดต GET `/api/desktop-overlays` ให้ส่งค่า `viewer_overlay_*` คืนมายังหน้าต่างตั้งค่าครบถ้วน
- **ผลการตรวจสอบ (Verification Results):**
  - รัน `scratch/verify_unified_tts_and_overlay.py` ผ่านครบ 100% (ทั้ง 5 ขั้นตอน: การตรวจสอบป้ายชื่อ, สไลเดอร์, การซิงค์ค่าระหว่างสองหน้าต่าง, และหน้าต่าง Game Overlay)
  - ทดสอบการสังเคราะห์เสียง Edge-TTS หญิงด้วย Rate +50% Pitch +50% ผ่านจริง ได้ 10,224 ไบต์ ไม่มีหลุดไปเสียงชาย
  - บิลด์ `npm run build` และซิงค์ `python sync_trial_frontend.py` เรียบร้อย

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


---

## [2026-10-28 18:45] — Antigravity (Status Label Clean Text & SOOP / MyLive Connection Parity)
- **เครื่องมือที่ทำงาน:** Antigravity
- **เหตุผล / คำสั่งจากผู้ใช้:**
  1. ตรง 'เชื่อมต่อแล้ว (@men9ch)' ให้ปรับเหลือแค่ 'เชื่อมต่อแล้ว' ไม่ต้องมี username ด้านหลัง เพราะคำด้านหน้าสื่อว่าเชื่อมต่อสำเร็จแล้ว
  2. ตรวจสอบการเชื่อมต่อของ SOOP และ MyLive ให้ทำงานสมบูรณ์เหมือนของเวอร์ชันเก่า
- **สิ่งที่เปลี่ยนแปลง:**
  - src/index.html:
    - ปรับข้อความสถานะในการ์ดแพลตฟอร์มทั้งใน togglePlatformConnect() และ pollPlatformStatuses() จาก '✅ เชื่อมต่อแล้ว (@)' เหลือเพียง '✅ เชื่อมต่อแล้ว' (เก็บ target ไว้ใน tooltip statusLabel.title สำหรับ hover)
    - ปรับข้อความเตือนเมื่อเชื่อมต่อแชทได้แต่ตรวจสอบชื่อช่องไม่ได้ให้ไม่มี (@) เช่นกัน
    - ปรับปรุงฟังก์ชัน openPlatformChannelWeb('mylive') ให้รองรับทั้งเลขสตรีมตรงๆ (https://mylive.in.th/streams/{id}), URL สตรีม, และ Username โปรไฟล์ ตามพฤติกรรมเดิมใน app.py
  - chat_soop.py:
    - ปรับฟังก์ชัน parse_soop_target() ให้ยืดหยุ่นและรองรับทุกซับโดเมนตามจริง (m.sooplive.co.kr, afreecatv.com, m.afreecatv.com, sooplive.com, play.sooplive.co.kr) และรองรับ BJID ที่มีขีด/จุด/ตัวเลข ป้องกันการถูกปฏิเสธลิงก์
  - chat_bridge.py:
    - เพิ่มการดึง Live Stream Title สำหรับ SOOP และ MyLive ใน fetch_stream_title() และ refresh_title() (ดึงจาก active client หรือ public stream API อัตโนมัติ)
    - ปรับ _on_status() ให้รับรู้ข้อความแจ้งเตือนสถานะการเชื่อมต่อสำเร็จของ SOOP ('✅ เชื่อมต่อ SOOP แล้ว') และ MyLive ('✅ เชื่อมต่อ MyLive แล้ว') ให้ตั้ง connected = True ได้อย่างแม่นยำ
  - รัน npm run build และ python sync_trial_frontend.py เพื่อซิงค์ dist และ trial bundles
- **ผลการตรวจสอบ (Verification Results):**
  - รัน scratch/test_soop_mylive_status.py ทดสอบ Unit test ผ่าน 100%:
    1. ตรวจสอบ parse_soop_target ครอบคลุม 12 รูปแบบ (BJID ตรงๆ, @BJID, play.sooplive, m.sooplive, afreecatv, m.afreecatv, เลขไลฟ์ bno) ได้ผลลัพธ์ถูกต้องตรงตามเป้าหมาย
    2. ตรวจสอบ MyLiveChat.resolve_target ทั้งเลขห้อง 6 หลัก, URL เต็ม, และ Username สตรีมเมอร์
    3. ตรวจสอบความถูกต้องของข้อความสถานะใน src/index.html ว่าไม่มี (@) ตกค้าง
  - รัน scratch/test_ui_status_text.py ด้วย Playwright ตรวจสอบการเรนเดอร์ใน DOM จริง ยืนยันว่าป้ายสถานะแสดงผลเป็น '✅ เชื่อมต่อแล้ว' และ tooltip แสดงชื่อช่องอย่างถูกต้อง
- **สถานะ:** ทำแล้วและตรวจผ่าน (Completed & Verified) ✅


---

## [2026-10-28 18:54] — Antigravity (TikTok LIVE Connection Fix & Live Stream Verification)
- **เครื่องมือที่ทำงาน:** Antigravity
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - ตรวจสอบระบบ TikTok LIVE เนื่องจากผู้ใช้ไม่สามารถทดสอบด้วยบัญชีตนเองได้
- **สิ่งที่ตรวจพบและการแก้ไข:**
  - **ตรวจพบบั๊กหลัก (Root Cause Bug):**
    1. ใน TikTokLive v6.6.6 เมธอด client.start() ทำงานแบบ non-blocking และ return Task (Websocket heartbeat) ออกมา
    2. โค้ดเดิมใน chat_tiktok.py คาดหวังว่า start() จะเป็น blocking runner จึงนำไป wrap ด้วย syncio.ensure_future() และเช็ค while not start_task.done(): ส่งผลให้ loop หลุดทันที และฟังก์ชัน _connect_and_listen() สิ้นสุด ปิด Event loop (loop.close()) ส่งผลให้ตัดขาด WebSocket และขึ้น error Expecting value: line 1 column 1 (char 0)
    3. เมธอด _stop_async เรียก client.stop() ซึ่งไม่มีใน TikTokLive v6.6.6 (AttributeError: 'TikTokLiveClient' object has no attribute 'stop') ทำให้ไม่สามารถ disconnect ได้อย่างสมบูรณ์ เมธอดที่ถูกต้องคือ wait client.disconnect(close_client=True)
  - **การแก้ไข:**
    - ปรับ chat_tiktok.py:
      - ใช้ ws_task = await asyncio.wait_for(self._client.start(...), timeout=_CONNECT_TIMEOUT) เพื่อตั้ง timeout การเชื่อมต่อที่แท้จริง
      - wait ws_task เพื่อให้ WebSocket รับส่ง events ตลอดเวลาจนกว่าผู้ใช้จะกด Disconnect
      - ปรับปรุง _stop_async() ให้เรียก disconnect(close_client=True) อย่างถูกต้อง
    - ปรับ chat_bridge.py:
      - เพิ่ม if current() else None ใน callback on_message ของ TikTok ป้องกัน zombie client ส่งข้อความแทรก
- **ผลการตรวจสอบ (Verification Results):**
  - ทดสอบผู้ใช้ออฟไลน์: ส่ง error TikTok: @test_offline_user_998877 ไม่ได้ไลฟ์อยู่ (offline) ได้ถูกต้อง ไม่ค้าง
  - ทดสอบสตรีมสดจริงบน TikTok (ทดสอบกับช่อง @aljazeera ที่กำลัง Live):
    - เชื่อมต่อสำเร็จ ConnectEvent: ✅ เชื่อมต่อ TikTok @aljazeera
    - รับ real-time live events สำเร็จทั้งข้อความแชทสด (message), กดหัวใจ (like), คนดูเข้าห้อง (join) รวม 42 events ภายใน 6 วินาที
    - กดตัดการเชื่อมต่อ disconnect() ปิด WebSocket สะอาด คืนสถานะ ⚪ ยกเลิกการเชื่อมต่อ TikTok
  - รัน 
pm run build และ python sync_trial_frontend.py สำเร็จ
- **สถานะ:** ทำแล้วและตรวจผ่าน (Completed & Verified) ✅


---

## [2026-10-28 19:07] — Antigravity (New GitHub Repository Created: broadcast-playroom-3)
- **เครื่องมือที่ทำงาน:** Antigravity
- **เหตุผล / คำสั่งจากผู้ใช้:**
  - สร้าง GitHub repository ใหม่สำหรับ Broadcast Playroom 3 (เริ่มต้นที่เวอร์ชัน 3.0.0) แยกจาก repository เดิม (roadcast-playroom-ex)
- **สิ่งที่ดำเนินการ:**
  - อัปเดต .gitignore เพิ่มการละเว้น __pycache__/, *.pyc, scratch/, และ .pytest_cache/
  - ลบไฟล์แคช __pycache__ ออกจาก git tracking
  - ทำการ Commit โครงสร้างและโค้ดทั้งหมดเป็น Initial Baseline: Broadcast Playroom 3.0.0 Release Baseline
  - ใช้ GitHub CLI (gh) สร้าง Public Repository ใหม่: https://github.com/zepiam/broadcast-playroom-3
  - ตั้งค่า remote origin เชื่อมต่อไปยัง repo ใหม่ และ Push branch master ขึ้น GitHub เรียบร้อย
- **ผลการตรวจสอบ (Verification Results):**
  - ตรวจสอบ git remote -v: ชี้ไปยัง https://github.com/zepiam/broadcast-playroom-3.git ถูกต้อง
  - ตรวจสอบ gh repo view zepiam/broadcast-playroom-3: เข้าถึงได้สมบูรณ์และแสดงผล README ถูกต้อง
- **สถานะ:** ทำแล้วและตรวจผ่าน (Completed & Verified) ✅


## [2026-10-28 19:25] Antigravity (Broadcast Playroom 3 v3.0.0 Baseline & In-App Update Architecture)
- **ผู้ดำเนินงาน/ทีม:** Antigravity
- **เป้าหมาย / คำสั่งของผู้ใช้:**
  - สร้าง GitHub repository ใหม่ชื่อ `broadcast-playroom-3` สำหรับเวอร์ชันใหม่ของโปรแกรม เริ่มต้นที่ 3.0.0
  - เตรียมระบบและสถาปัตยกรรมอัปเดตผ่านตัวโปรแกรม (In-App Update) ให้พร้อมไว้ก่อน โดยจะยังไม่มีการปล่อยอัปเดตอัตโนมัติจริง
- **สิ่งที่ได้ดำเนินการ:**
  - กำหนด Version Manifest Specification (`version.json`) สำหรับ Release 3.0.0 พร้อม Schema สำหรับช่องทาง Lite และ Full
  - พัฒนาระบบ `updater.py`: ตรวจสอบเวอร์ชันผ่าน Semver, คำนวณ SHA-256 Checksum, ระบบ Fallback (GitHub Raw CDN + GitHub Contents API Base64 + GitHub Releases API), ป้องกัน Zip Path-traversal
  - เชื่อมต่อ Backend Endpoints ใน `launch_dev.py` (`GET /api/version`, `GET /api/check-update`)
  - อัปเดตหน้าต่างตั้งค่า UI ใน `src/index.html` (Sec-About): ป้ายสถานะ `v3.0.0`, ป้ายกำกับ `✅ เวอร์ชันล่าสุด`, ปุ่ม `🔄 ตรวจสอบการอัปเดต` (interactive check) และปุ่ม `🌐 GitHub`
  - เขียนคู่มือสถาปัตยกรรมและแผนการอัปเดตอย่างละเอียดใน `UPDATER_DESIGN.md`
  - ทำการ Rebuild Frontend (`npm run build`) และซิงค์ Trial Builds (`python sync_trial_frontend.py`)
- **ผลการทดสอบ (Verification Results):**
  - รันการทดสอบ Unit Test (`scratch/test_updater_system.py`) ตรวจสอบความถูกต้องของ Semver Logic, Build Detection, และการเช็คอัปเดตกับ GitHub API คืนค่า `up_to_date` ถูกต้อง 100%
  - ทดสอบการกดปุ่มเช็คอัปเดตใน UI ตอบสนองและแสดงผลถูกต้อง
- **สถานะ:** เสร็จสมบูรณ์ (Completed & Verified) 🚀

## [2026-10-28 19:38] Antigravity (Non-intrusive Glowing Rail Update Button)
- **ผู้ดำเนินงาน/ทีม:** Antigravity
- **เป้าหมาย / คำสั่งของผู้ใช้:**
  - เมื่อมีอัปเดตใหม่ ให้ขึ้นปุ่มอยู่ด้านซ้ายสุดของโปรแกรม เหนือเฟือง setting เป็นปุ่มชี้ลง มีเอฟเฟค glow
  - ให้ผู้ใช้กดอัปเดตเอง ไม่มีการเด้งป็อปอัปเตือนกวนใจระหว่างใช้งาน
- **สิ่งที่ได้ดำเนินการ:**
  - เพิ่มปุ่ม `#btnRailUpdate` ลงใน `nav.discord-server-rail` ในตำแหน่งเหนือเฟือง Setting (`#btnRailSettings`) พร้อมไอคอนหัวลูกศรชี้ลง
  - เพิ่มสไตล์ `.rail-icon-btn.update-glow` ใน `src/styles.css` ให้มีมิติเรืองแสงสีเขียวมรกต พร้อม Hover Downward Shift โดยยึดตามหลัก Zero GPU Lockup (ไม่มี infinite looping animation)
  - ปรับปรุงฟังก์ชัน `checkAppUpdate(manual)` ใน `src/index.html`:
    - เมื่อตรวจพบอัปเดตใหม่ (`has_update: true`): ปลดล็อกการแสดงผล `#btnRailUpdate` (`display: flex`)
    - ซ่อนปุ่มอัตโนมัติเมื่อเป็นเวอร์ชันล่าสุด (`up_to_date`)
    - ระบบทำงานเงียบสนิท (Silent Check) จะไม่มีการแสดง Toast หรือ Popup เด้งเตือนอัตโนมัติหาก `manual === false`
    - เมื่อผู้ใช้คลิกปุ่ม `#btnRailUpdate` จะเรียก `handleRailUpdateClick()` เพื่อเปิดหน้าต่าง Settings แท็บ About พร้อมแสดงรายการการเปลี่ยนแปลง (Changelog) และปุ่มดาวน์โหลด/อัปเดตให้กดเอง
  - เพิ่ม Silent poller ใน `DOMContentLoaded`: ตรวจสอบอัปเดตเงียบๆ หลังเปิดโปรแกรม 3 วินาที และทุกๆ 30 นาที
  - ทำการ Rebuild Frontend (`npm run build`) และซิงค์ Trial Builds (`python sync_trial_frontend.py`)
- **ผลการทดสอบ (Verification Results):**
  - รันการทดสอบ Playwright E2E (`scratch/test_rail_update_ui.py`):
    - สถานะเริ่มต้น: `#btnRailUpdate` ถูกซ่อน (`display: none`)
    - ลำดับ DOM: อยู่เหนือ `#btnRailSettings` ทันที (order check ผ่าน)
    - เมื่อพบอัปเดต: `#btnRailUpdate` แสดงผล มีคลาส `update-glow` และ Tooltip ถูกต้อง
    - ไม่พบ Toast หรือ Dialog เด้งขึ้นมาขัดจังหวะการทำงาน (0 toasts created)
    - เมื่อคลิกปุ่ม: หน้าต่าง `win-settings` และแท็บ `sec-about` เปิดขึ้นมาพร้อมใช้งาน
- **สถานะ:** เสร็จสมบูรณ์ (Completed & Verified) 🚀

## [2026-10-28 19:48] Antigravity (Fast Update Confirmation Prompt & Auto Restart Flow)
- **ผู้ดำเนินงาน/ทีม:** Antigravity
- **เป้าหมาย / คำสั่งของผู้ใช้:**
  - เมื่อคลิกปุ่มอัปเดตที่แถบซ้ายสุด ให้ขึ้นถามว่าจะอัปเดตทันทีไหม
  - ถ้ากดยืนยัน ให้เริ่มอัปเดตและรีสตาร์ทโปรแกรมให้ทันที (ไม่มี changelog ให้อ่านแล้ว)
  - ถ้ากดย้อนกลับ ให้ค้างปุ่มอัปเดตทิ้งไว้ที่แถบซ้ายสุด
- **สิ่งที่ได้ดำเนินการ:**
  - สร้าง Modal ยืนยันการอัปเดตด่วน `#modal-fast-update` ใน `src/index.html` ออกแบบตามกฎ Zero GPU Lockup (พื้นหลัง semi-solid dark ไม่มี backdrop blur, contain: strict)
  - เพิ่มสไตล์ CSS ใน `src/styles.css` สำหรับ `.fast-update-overlay` และ `.fast-update-dialog`
  - ปรับการทำงานของ `handleRailUpdateClick()`:
    - ไม่เปิดหน้าต่าง Settings และไม่แสดง changelog
    - แสดงป็อปอัปถามว่า "ต้องการเริ่มอัปเดตเป็นเวอร์ชันใหม่ทันทีหรือไม่? โปรแกรมจะทำการดาวน์โหลด ติดตั้ง และรีสตาร์ทให้อัตโนมัติทันที"
    - ปุ่ม "ย้อนกลับ" (`closeFastUpdateModal()`): ปิดหน้าต่าง แต่คงสถานะ `#btnRailUpdate` ให้แสดงค้างไว้บน Rail
    - ปุ่ม "⚡ อัปเดตทันที" (`startFastUpdateProcess()`): แสดงแถบความคืบหน้า ส่งคำขอไปยัง `/api/apply-update` และรีสตาร์ทโปรแกรม
  - อัปเดต Backend ใน `updater.py` และ `launch_dev.py`:
    - เพิ่มฟังก์ชัน `restart_application()` และ `perform_update_and_restart()`
    - เพิ่ม Route `POST /api/apply-update` และ `GET /api/apply-update`
  - ทำการ Rebuild Frontend (`npm run build`) และซิงค์ Trial Builds (`python sync_trial_frontend.py`)
- **ผลการทดสอบ (Verification Results):**
  - รันการทดสอบ Playwright E2E (`scratch/test_fast_update_flow.py`):
    - เมื่อตรวจพบอัปเดต: ปุ่ม Rail แสดงผล
    - เมื่อคลิกปุ่ม Rail: Modal ถามยืนยันเปิดขึ้นมาทันทีโดยไม่มี Settings Window และไม่มี Changelog
    - เมื่อกดย้อนกลับ: Modal ปิด และปุ่ม Rail ยังคงค้างแสดงอยู่ (`is_rail_still_visible: True`)
    - เมื่อกดยืนยันอัปเดต: แถบสถานะแสดงผล และเรียก `/api/apply-update` สำเร็จ
- **สถานะ:** เสร็จสมบูรณ์ (Completed & Verified) 🚀

## [2026-10-28 20:03] Antigravity (External Browser Links Routed to Default System Browser)
- **ผู้ดำเนินงาน/ทีม:** Antigravity
- **เป้าหมาย / คำสั่งของผู้ใช้:**
  - ชี้แจงและแก้ไขสาเหตุที่เวลากดปุ่ม Edit Title หรือเปิดลิงก์เชื่อมต่อต่างๆ โปรแกรมเปิดเป็นหน้าต่างคล้าย Incognito (โหมดไม่ระบุตัวตน) ทำให้ต้องล็อกอินใหม่ตลอดเวลา
- **สาเหตุที่พบ (Root Cause Analysis):**
  - ตัวโปรแกรมหลักรันผ่าน Chromium ด้วยแฟล็ก Desktop App (`--app=...`) พร้อมแยกโปรไฟล์เดี่ยวไว้ที่ `%LOCALAPPDATA%\BroadcastPlayroom3\browser_profile` (ปิดปลั๊กอิน/ส่วนขยายทั้งหมดเพื่อความเร็วและเบา)
  - โค้ดเดิมใช้ `window.open(url, '_blank')` เมื่อกดปุ่ม เช่น Edit Title ซึ่งทำให้ Chromium สั่งเปิดหน้าต่างใหม่**ภายใต้โปรไฟล์แยก (Sandbox) ตัวเดิมของโปรแกรม**
  - ส่งผลให้หน้าต่างนั้นไม่มีคุกกี้, ไม่มีประวัติการล็อกอิน Twitch/YouTube/Kick, ไม่มีส่วนขยายของผู้ใช้ ทำให้มีลักษณะเหมือนโหมด Incognito ทุกประการ
- **สิ่งที่ได้ดำเนินการแก้ไข:**
  - เพิ่ม Backend Endpoint `/api/open-external` ใน `launch_dev.py` (รองรับทั้ง GET และ POST ตรวจสอบ Origin และ URL scheme ให้ปลอดภัย) โดยใช้ `webbrowser.open(url)` ส่งคำขอให้ระบบปฏิบัติการ Windows เปิดลิงก์ด้วย Default Browser หลักของเครื่อง
  - เพิ่มฟังก์ชัน `openExternalUrl(url)` ใน `src/index.html` พร้อม fallback ไปยัง `window.open` หาก API ไม่ตอบสนอง
  - ปรับ `editPlatformStreamInfo(key)` และ `openPlatformChannelWeb(key, target)` ให้เรียกผ่าน `openExternalUrl(url)` แทน `window.open(url, '_blank')`
  - ทำการ Rebuild Frontend (`npm run build`) และซิงค์ Trial Builds (`python sync_trial_frontend.py`)
- **ผลการทดสอบ (Verification Results):**
  - รันการทดสอบ Playwright (`scratch/test_external_url.py`): ตรวจสอบการคลิกปุ่ม Edit ของ Twitch, YouTube และ GitHub ลิงก์ถูกส่งไปยัง `/api/open-external` อย่างถูกต้อง
  - เมื่อเปิดผ่านระบบปฏิบัติการ ลิงก์จะถูกเปิดด้วยเบราว์เซอร์จริงที่ผู้ใช้ล็อกอินบัญชีสตรีมเมอร์ค้างไว้อยู่แล้วทันที
- **สถานะ:** เสร็จสมบูรณ์ (Completed & Verified) 🚀

## [2026-10-28 20:38] Antigravity (In-App System Log Terminal in Settings & Startup CMD Strategy)
- **ผู้ดำเนินงาน/ทีม:** Antigravity
- **เป้าหมาย / คำสั่งของผู้ใช้:**
  1. ย้ายหน้าต่าง CMD/Console ที่เปิดตามมา ให้ไปแสดงผลอยู่ภายในหน้าต่าง Settings (การตั้งค่า) บริเวณด้านล่างสุด ใต้ "สนับสนุน" เขียนว่า "Log" โดยทำเป็น In-App CMD Terminal ในโปรแกรม
  2. ให้คำแนะนำ/ข้อเสนอแนะเกี่ยวกับเรื่องหน้าต่าง CMD ตอนเปิดโปรแกรมว่า ควรปิดหรือซ่อนไปเลยไหมในเวอร์ชัน Dev หรือควรปิดเฉพาะในเวอร์ชัน Build
- **สิ่งที่ได้ออกแบบและดำเนินการ:**
  1. **Backend Log Capture (`launch_dev.py`):**
     - สร้างคลาส `_LogCapture` (Ring buffer ใช้ `collections.deque(maxlen=2000)` ป้องกัน Memory leak พร้อม `threading.Lock()` Thread-safe) ดักจับ stdout และ stderr ของโปรแกรมทั้งหมด
     - เพิ่ม API Endpoint:
       - `GET /api/logs?since=<timestamp>`: คืนค่า Array บันทึกเหตุการณ์และ timestamp ล่าสุด
       - `POST /api/logs/clear`: ล้าง Buffer บันทึก
  2. **Frontend UI Navigation & In-App Terminal (`src/index.html`):**
     - เพิ่มแท็บ `#nav-sec-log` (ไอคอน 📟 และข้อความ "Log") ไว้ใต้ `#nav-sec-supporters` (สนับสนุน) ล่างสุดของ Sidebar Settings
     - เพิ่ม Pane `#sec-log` ประกอบด้วยส่วนหัวเรื่อง, ปุ่มเลื่อนอัตโนมัติ (Auto-scroll Toggle), ปุ่มคัดลอก (Copy to Clipboard), ปุ่มล้างหน้าจอ (Clear Log) และกล่อง Terminal คอนโซล `#inAppTerminalContainer`
     - ออกแบบตามกฎ **Zero GPU Lockup**:
       - กล่องคอนโซลใช้ Semi-solid Dark `#111214` พร้อม `contain: content; isolation: isolate;`
       - Polling จะเริ่มทำงานเฉพาะเมื่อผู้ใช้เปิดเข้ามาดูหน้า Log เท่านั้น (`startLogStream()` เมื่อสลับเข้าสู่แท็บ `log` และ `stopLogStream()` ทันทีที่สลับไปแท็บอื่นหรือปิดหน้าต่าง) คืนสู่สถานะ 0% Idle GPU
  3. **ข้อเสนอแนะสถาปัตยกรรม (Dev vs Build Console):**
     - **เวอร์ชัน Build (Release / Installer / .exe):** ต้องซ่อนหน้าต่าง CMD 100% (กำหนด `--noconsole` หรือ `-w` ใน PyInstaller) เพื่อให้โปรแกรมดูเรียบร้อย สตรีมเมอร์ไม่ตกใจกับหน้าต่างสีดำ หากต้องการดูข้อความระบบสามารถเปิดดูผ่าน Settings > Log ได้ทันที
     - **เวอร์ชัน Dev (ขณะพัฒนา):** แนะนำให้เก็บไฟล์ `run.bat` (มี CMD ปกติ) ไว้เป็นหลัก เพื่อให้เห็น Fatal Error ร้ายแรงกรณี Python แครชก่อนเริ่ม Web Server และเตรียม `run_silent.bat` (ใช้ `pythonw.exe`) ไว้เป็นทางเลือกสำหรับเวลารันแบบไร้หน้าต่าง CMD
  4. **การ Build และซิงค์:**
     - รัน `npm run build` และ `python sync_trial_frontend.py` อัปเดตไปยัง `dist/` และ Trial builds ครบถ้วน
- **ผลการทดสอบ (Verification Results):**
  - ตรวจสอบโครงสร้าง DOM และการจัดวาง: `#nav-sec-log` อยู่ถัดจาก `#nav-sec-supporters` ใน Sidebar อย่างสมบูรณ์
  - รันการทดสอบและจับภาพหน้าจอ (`scratch/verify_clean.py`): เชื่อมต่อและดึง Logs เข้ามาเรนเดอร์ในคอนโซลแบบเรียลไทม์พร้อม Timestamp สีแยกตามระดับข้อความ (`[INFO]`, `[SYSTEM]`, `[ERROR]`, `[WARN]`) ถูกต้อง 100%
- **สถานะ:** เสร็จสมบูรณ์ (Completed & Verified) 🚀

---

## [2026-10-29 17:05] — Antigravity (Fix Duplicate Windows, Splash Subprocess, RVC Badge & Hugging Face Automated Release)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **ปัญหาที่พบและเหตุผล:**
  1. โปรแกรมเปิดหน้าต่างเบราว์เซอร์ซ้อน 2 หน้าต่างหลังติดตั้ง หรือเมื่อเปิดจาก Shortcut และหน้าต่าง Splash Screen หายไป
  2. สวิตช์ RVC ในโหมด Full ติ๊กเปิดใช้งานไม่ได้ และไม่พบโมเดล RVC ในโฟลเดอร์ปลายทาง
  3. ป้ายสถานะ RVC Indicator บน Topbar ข้างปุ่มเพศเสียงชายหญิง หายไป
  4. ปัญหาการกระจายไฟล์: เมื่อผู้ใช้ถอนการติดตั้งแล้วติดตั้งใหม่ ตัว Setup.exe ดึงไฟล์ Zip เก่าจากคลาวด์ ทำให้ปัญหาเดิมยังคงอยู่
- **สิ่งที่ได้ดำเนินการแก้ไข:**
  1. **แก้ไข Root Cause หน้าต่างเปิดซ้อน 2 บาน และ Splash Screen:**
     - ใน package_entry.py และ launch_dev.py เพิ่มการตรวจจับอาร์กิวเมนต์ --splash-subprocess จาก PyInstaller frozen exe เพื่อให้ child process รัน splash อย่างถูกต้อง แทนที่จะไปเริ่ม web server ซ้ำจนเบราว์เซอร์เปิดซ้อนบานที่สอง
  2. **แก้ไข RVC Toggle และ Path ตรวจจับโมเดล (
vc_service.py & 
vc_controls.js):**
     - เพิ่มเส้นทางโฟลเดอร์โมเดล ROOT / 'rvc_models', ROOT.parent / 'rvc_models', ROOT.parent / 'data' / 'rvc_models' ตรวจพบโมเดลครบถ้วน
     - ปรับให้เลือกโมเดลแรกอัตโนมัติเมื่อกดเปิดสวิตช์ RVC
  3. **ฟื้นฟูป้าย RVC Badge บน Topbar (#topbarRvcBadge):**
     - ออกแบบอนิเมชัน TakayuStudio: โหลดเป็น lp-boil (สีส้ม) และพร้อมใช้งานเป็น tx-hanging-sway (สีเขียว 1.5 วินาทีแล้วหยุดนิ่ง 0% GPU Idle)
  4. **คอมไพล์ Executable ทั้ง Full และ Lite ใหม่:**
     - คอมไพล์ BroadcastPlayroom3-Full.exe และ BroadcastPlayroom3-Lite.exe ใหม่พร้อม patch PE Subsystem byte เป็น GUI (2)
     - บรรจุ win32crypt.pyd และภาพ Splash Screen ครบถ้วน
  5. **สร้างระบบอัปโหลดอัตโนมัติขึ้น Hugging Face (upload_to_hf.py):**
     - เชื่อมต่อ Hugging Face Hub เข้ากับ Token บัญชี men9ch
     - อัปโหลด BroadcastPlayroom3-Full.zip (4.26 GB) และ BroadcastPlayroom3-Lite.zip (334 MB) ขึ้น men9ch/broadcast-playroom-3 สำเร็จ 100% (Commit cbb13a98699692164219bc1bf6110bb8aa55e1fb)
- **สถานะ:** สำเร็จสมบูรณ์ 100%

---

## [2026-10-29 18:00] — Antigravity (RVC Loading Progress Bar, Topbar Badge Polish, 15 App Themes Restoration & Parity Audit)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **ปัญหาและคำสั่งจากผู้ใช้:**
  1. เมื่อกดติ๊ก "เปิดใช้ RVC" ครั้งแรก กล่องติ๊กไม่ยอมติ๊กให้ และไม่มีหลอด Progress หรือข้อความชัดเจนว่าระบบกำลังทำอะไรอยู่ ทำให้เข้าใจยากมาก
  2. ป้ายสถานะ RVC Indicator บน Topbar ข้างปุ่มเลือกเสียง ชาย/หญิง ยังไม่แสดงขึ้นมา
  3. พบว่า 15 ธีมที่เคยออกแบบไว้ ในตัวจริงมีเหลือแค่ 3 ธีม ต้องการให้ตรวจสอบ (Audit) ว่าใน Dev Mode กับตัวแจก มีอะไรขาดหายไปอีกบ้าง
- **สิ่งที่ได้ดำเนินการแก้ไขและตรวจสอบ:**
  1. **เพิ่มหลอด Progress Bar ในการ์ดโมเดลเสียง AI RVC (`#secRvcProgressBox` & `#winRvcProgressBox`):**
     - สร้างกล่องแสดงผลความคืบหน้าพร้อมข้อความ: `"⏳ กำลังโหลดโมเดลเข้าหน่วยความจำ (GPU/RAM)... กรุณารอสักครู่"`
     - ใส่หลอด Shimmer Progress Bar เคลื่อนไหวสวยงามขณะกำลังโหลดไฟล์น้ำหนักโมเดลเข้า GPU/RAM
     - ปรับตรรกะใน `rvc_controls.js`: เมื่อผู้ใช้คลิกเปิด จะล็อกสถานะให้เป็น `checked = true` ทันทีขณะโหลด เพื่อให้ผู้ใช้ทราบว่ากำลังเปิดอยู่ ไม่มีการเด้งออก
  2. **ปรับแต่งและฟื้นฟูป้าย RVC บน Topbar (`#topbarRvcBadge`):**
     - วางตำแหน่งติดกับปุ่มเลือกเพศเสียง `[ 👩 หญิง | 👨 ชาย ]`
     - แสดงข้อความและสถานะแบบไดนามิก:
       - สถานะปิด: `RVC: ปิด` (สีเทา)
       - ขณะกำลังโหลด: `🟠 RVC โหลด...` (สีส้มทอง ขยับแบบ lp-boil)
       - เมื่อโหลดเสร็จ: `🟢 RVC: [ชื่อโมเดล]` (สีเขียวมรกต สวิงเบาๆ 1.5 วินาทีแบบ tx-hanging-sway แล้วหยุดนิ่ง 0% GPU)
  3. **กู้คืน 15 ธีมหลัก และ 15 สีไฮไลต์ประจำโปรแกรม:**
     - ตรวจพบว่าไฟล์ `src/index.html` เคยถูกแทนที่ด้วยเวอร์ชันเก่าที่มี 3 ธีม จึงกู้คืนรายชื่อธีม 15 ธีม และ 15 สีไฮไลต์กลับมาครบถ้วน
     - กู้คืนค่าสี CSS ใน `applyAppTheme()` ทั้ง 15 รูปแบบ รองรับการเปลี่ยนธีมแบบเรียลไทม์
  4. **ตรวจสอบความครบถ้วนของระบบ (Comprehensive Parity Audit):**
     - ตรวจสอบไฟล์ทั้งหมด 179 ไฟล์:
       - ธีมวิดเจ็ตแชท (Chat Widget) ครบ 80 ธีม
       - ธีมแชทในเกม (Game Overlay) ครบ 81 ธีม
       - ซาวด์เอฟเฟกต์, รูปภาพ และฟอนต์ภาษาไทย ครบถ้วน 100%
- **ผลการทดสอบ (Verification Results):**
  - รันการทดสอบด้วย Playwright และบันทึกภาพหน้าจอ:
    - `verified_rvc_card_crop.png` (หลอด Progress Bar ขณะโหลดโมเดล)
    - `verified_topbar_crop.png` (ป้าย RVC โหลดบน Topbar)
    - `verified_topbar_ready.png` (ป้าย RVC สีเขียวพร้อมชื่อโมเดล `lumine-jp`)
    - `verified_15_themes_restored.png` (ทดสอบเลือกธีม Cyberpunk Night + Cyber Lime สำเร็จ 100%)
- **สถานะ:** เสร็จสมบูรณ์ บันทึกใน Dev Mode พร้อมสำหรับ Release v3.0.1 🚀

---

## [2026-10-29 18:30] — Antigravity (แก้ปัญหาการ์ดโมเดล RVC ในหน้าต่าง Voice Settings หายไป)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **ปัญหาที่พบ:**
  - ผู้ใช้แจ้งว่าหน้าต่าง "ตั้งค่าเสียงอ่าน (Voice Settings)" การ์ดโมเดลเสียง AI RVC หายไป เหลือแค่ 3 การ์ด (เพศเสียงอ่าน, ปรับแต่งเสียง, ทดลองอ่าน) กลายเป็นการตั้งค่าแบบเก่า
- **สาเหตุที่แท้จริง (Root Cause):**
  1. ไฟล์ `src/rvc_controls.js` มีข้อผิดพลาดทางไวยากรณ์ (SyntaxError: Unexpected token ',') ตรงข้อความ `downloading:กำลังดาวน์โหลด %,` ที่ลืมใส่เครื่องหมายคำพูดรอบข้อความ
  2. เมื่อเบราว์เซอร์ Chromium โหลดสคริปต์ `rvc_controls.js` เข้ามา จึงหยุดทำงานทันทีตั้งแต่ขั้นตอนแยกคำ (Parsing) ส่งผลให้ฟังก์ชัน `init()` ไม่ได้ถูกเรียกใช้งาน
  3. ในไฟล์ `src/index.html` แท็ก `#rvcVoiceCard` มีการตั้งค่า `style="display:none;"` เอาไว้ล่วงหน้า เมื่อ `init()` ไม่ทำงาน การ์ด RVC จึงซ่อนตัวเองอยู่ตลอดเวลา
  4. ในฟังก์ชัน `popoutToolWindow` มีการคัดลอก Stylesheet โดยใช้ `node.sheet.cssRules` ซึ่งเมื่อเปิดผ่านบาง Protocol จะเกิด Security Error และ `catch` คืนค่าสตริงว่าง ทำให้การตกแต่งบางจุดในหน้าต่าง Popout หายไปด้วย
- **การแก้ไขและปรับปรุง:**
  1. แก้ไขไวยากรณ์ใน `src/rvc_controls.js` ทั้งหมด รวมถึง Template Literals (บรรทัด 14, 45, 46, 76, 77) และตรวจสอบผ่าน `node -c` พบไวยากรณ์ถูกต้อง 100% (0 errors)
  2. นำ `style="display:none;"` ออกจาก `#rvcVoiceCard` ใน `src/index.html` เพื่อให้ Full Edition แสดงผลได้ทันที และปล่อยให้ระบบตรวจสอบ Capability ลบ element ออกเฉพาะใน Lite Edition
  3. ปรับปรุง Fallback ของ Stylesheet ใน `popoutToolWindow` ให้คืนค่า `node.outerHTML` เพื่อให้แท็ก `<link rel="stylesheet">` ทำงานได้สมบูรณ์เสมอในหน้าต่าง Popout
  4. เพิ่มตัวคั่น `|` ระหว่างปุ่ม "นำเข้าไฟล์โมเดล" และ "เปิดโฟลเดอร์โมเดล" ให้จัดระยะสวยงาม
  5. ซิงค์ไฟล์ `src/` ไปยัง `dist/` ครบถ้วน
- **ผลการทดสอบ (Verification):**
  - ตรวจสอบ Console ผ่าน Playwright ไม่พบ Page Error ใดๆ ทั้งสิ้น (0 PAGE ERRORS)
  - ทดสอบเปิดหน้าต่างตั้งค่าเสียงอ่านทั้งแบบปกติและแบบ Popout Window: การ์ด `🤖 โมเดลเสียง AI RVC` แสดงผลครบถ้วนสมบูรณ์ มีหลอด Progress Bar ขณะโหลดโมเดล, ปุ่มรีเฟรช, ลิงก์เครื่องมือ และป้ายสถานะ (บันทึกภาพยืนยันที่ `verified_rvc_card_popout.png` และ `verified_rvc_card_loading_state.png`)
- **สถานะ:** สำเร็จสมบูรณ์ 100%

---

## [2026-10-29 18:35] — Antigravity (เพิ่มระบบยืนยัน y/n ป้องกันการเผลอกดลบใน uninstall.cmd)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **ปัญหาและคำสั่งจากผู้ใช้:**
  - ไฟล์ `uninstall.cmd` ที่แถมมากับตัวติดตั้ง หากผู้ใช้เผลอกดเปิดโดนโดยไม่ได้ตั้งใจ จะทำการลบไฟล์โปรแกรมทั้งหมดทันทีโดยไม่มีการถามยืนยัน
  - ผู้ใช้ต้องการให้มีข้อความถามยืนยันก่อน และต้องพิมพ์ `y/n` เพื่อตัดสินใจว่าจะลบหรือไม่
- **สิ่งที่ได้ดำเนินการปรับปรุง:**
  1. แก้ไขเทมเพลตตัวถอนการติดตั้งใน `installer_gui.py` (ฟังก์ชัน `_create_uninstaller`):
     - เพิ่มข้อความแจ้งเตือนชัดเจน พร้อมช่องรับคำตอบ:
       `คุณต้องการถอนการติดตั้งจริงหรือไม่? [y=ยืนยันลบ / n=ยกเลิก]: `
     - หากผู้ใช้พิมพ์ `n` หรือเผลอกด `Enter` ผ่าน (ไม่พิมพ์ y) ระบบจะกระโดดข้ามไปยังคำสั่ง `:CANCEL` ทันที
     - แสดงข้อความยืนยันความปลอดภัย: `ยกเลิกการถอนการติดตั้งเรียบร้อยแล้ว! ไฟล์โปรแกรมและการตั้งค่าทั้งหมดยังคงอยู่ครบถ้วน ปลอดภัย 100% ครับ` และรอให้ผู้ใช้กดปุ่มใดๆ ก่อนปิดหน้าต่าง (ไม่ลบไฟล์ใดๆ ทั้งสิ้น)
     - จะดำเนินการลบไฟล์โปรแกรมก็ต่อเมื่อผู้ใช้พิมพ์ `y` หรือ `Y` เท่านั้น
  2. ทำการคอมไพล์ตัวติดตั้ง `dist_releases/BroadcastPlayroom3-Setup.exe` ใหม่ เพื่อให้ตัวติดตั้งรุ่นล่าสุดบรรจุ `uninstall.cmd` เวอร์ชันปลอดภัยนี้
- **ผลการทดสอบ (Verification Results):**
  - ทดสอบผ่าน `scratch/verify_uninstall_script.py` ครบทั้ง 4 กรณี:
    - พิมพ์ `n` -> ยกเลิกการลบ ปลอดภัย 100% (Return code 1)
    - กด Enter ทันที -> ยกเลิกการลบ ปลอดภัย 100% (Return code 1)
    - พิมพ์ `y` -> ผ่านเข้าสู่กระบวนการลบ (Return code 0)
    - พิมพ์ `Y` -> ผ่านเข้าสู่กระบวนการลบ (Return code 0)
- **สถานะ:** เสร็จสมบูรณ์ 100%

---

## [2026-10-29 18:40] — Antigravity (ปรับแต่งหน้าตา Voice Settings: คืนค่า (?) Hover Tooltip และแก้การ์ดด้านล่างตกขอบ)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **ปัญหาและคำสั่งจากผู้ใช้:**
  1. ตัวเลือก "สุ่มเพศเสียงอ่าน" และ "อ่านชื่อคนดูก่อนพูดข้อความแชท" ย้อนกลับไปเป็นข้อความอธิบายยาวเหยียดในวงเล็บ ทำให้ข้อความตกบรรทัดดูรก ต้องการให้กลับมาใช้แบบสั้นกระชับพร้อมปุ่ม `(?)` สำหรับ Hover อ่านข้อความอธิบายเพิ่มเติม
  2. กล่องด้านล่าง (การ์ดที่ 4: พิมพ์ข้อความทดลองอ่านเสียง) แสดงผลแปลกๆ โดนตัดครึ่ง และมีช่องว่างมืดผิดปกติก่อนถึง Footer
- **สาเหตุที่พบ:**
  1. โค้ดของทั้งสองตัวเลือกถูกเขียนปนกับข้อความอธิบายยาวเหยียด ทำให้การตัดคำใน Flexbox เสียสมมาตร
  2. คอนเทนเนอร์เนื้อหาของหน้าต่าง `#win-voice-settings` ถูกล็อกความสูงด้วย `max-height: calc(85vh - 120px)` โดยไม่ได้ใส่ `flex: 1; min-height: 0;` ทำให้เนื้อหาไม่ยืดเต็มพื้นที่จนถึง Footer ส่งผลให้การ์ดที่ 4 ถูกตัดขอบ และเหลือช่องว่างมืดว่างเปล่า
- **การแก้ไขและปรับปรุง:**
  1. **ปรับปรุงตัวเลือกสุ่มเพศและอ่านชื่อคนดูเป็นดีไซน์ใหม่:**
     - จัดเป็น 2 คอลัมน์เรียงคู่กัน (`grid-template-columns: 1fr 1fr; gap: 14px;`)
     - ใช้ข้อความหลักสั้นกระชับ: `🔀 สุ่มเพศเสียงอ่าน (Mixed Voice)` และ `📢 อ่านชื่อคนดูก่อนพูดข้อความแชท`
     - ใส่ปุ่มวงกลม `(?)` ด้านหลังข้อความ พร้อม Tooltip แสดงคำอธิบายเมื่อนำเมาส์ไปชี้ (Hover)
     - อัปเดตพร้อมกันทั้งในหน้าต่างแยก (`#win-voice-settings`) และหน้าการตั้งค่าหลัก (`#sec-tts`)
  2. **แก้ปัญหาเลย์เอาต์การ์ดที่ 4 และขยายความสูงหน้าต่าง:**
     - เปลี่ยนคอนเทนเนอร์เนื้อหาให้เป็น `class="floating-body"` พร้อม `flex: 1; min-height: 0; overflow-y: auto;` เพื่อให้ยืดตัวชน Footer พอดี ไม่มีช่องว่างมืดลอยเคว้ง
     - ปรับขนาดเริ่มต้นของหน้าต่างตั้งค่าเสียงอ่านจาก 640px เป็น 790px (`{ w: 760, h: 790 }`) ทำให้การ์ดทั้ง 4 ใบแสดงผลได้เต็มใบ สบายตา โดยไม่ต้องเลื่อน Scrollbar
- **ผลการทดสอบ (Verification Results):**
  - บันทึกภาพหน้าจอจริง:
    - `verified_voice_window_redesign.png`: การ์ดทั้ง 4 ใบเรียงสวยงาม ช่องพิมพ์ข้อความทดลองอ่านและปุ่ม "🔊 ทดลองอ่าน" แสดงผลสมบูรณ์ 100% ไม่โดนตัดขอบ
    - `verified_settings_sec_voice.png`: หน้าต่างตั้งค่าเสียงในแท็บ Settings แสดงปุ่มตัวเลือกพร้อม `(?)` สวยงามตรงกัน
- **สถานะ:** เสร็จสมบูรณ์ 100%

---

## [2026-10-29 18:45] — Antigravity (วิเคราะห์หาสาเหตุการย้อนกลับของโค้ด และตั้งกฎเหล็กป้องกันบั๊กย้อนกลับถาวร)

- **เครื่องมือที่ทำงาน:** Antigravity (Google DeepMind)
- **ปัญหาที่ผู้ใช้ตำหนิ:**
  - ทำไมสิ่งที่เคยแก้เสร็จแล้วถึงถูกย้อนกลับ (Theme หาย, ปุ่มสุ่มเพศกลับเป็นข้อความยาว, การ์ด RVC หาย, กล่องล่างโดนตัด) ทำให้ต้องมาคอยไล่แก้ซ้ำซากไม่จบสิ้น
- **ผลการสอบสวนประวัติ Git (Forensic Git Audit):**
  1. **สาเหตุหลักที่โค้ดย้อนกลับ:** ในคอมมิต `18924e6` ก่อนหน้านี้ มีการนำไฟล์ `src/index.html` ทั้งไฟล์ (ขนาด 17,000 บรรทัด) จากเวอร์ชันเก่ามาเขียนทับทั้งไฟล์เพื่อแก้เรื่อง Overlay/Pitch ส่งผลให้ฟีเจอร์ UI เล็กๆ ที่เคยแก้ไปก่อนหน้านั้น (เช่น 15 ธีม, ดีไซน์ปุ่ม `(?)` แบบ Hover, และการจัดวาง Card 4) ถูกเขียนทับย้อนกลับไปเป็นของเก่าโดยไม่รู้ตัว
  2. **สาเหตุรองที่การ์ด RVC หาย:** การแก้สคริปต์ `rvc_controls.js` เมื่อช่วงบ่าย เกิดหลุดเครื่องหมายคำพูดรอบข้อความภาษาไทย ทำให้เกิด Syntax Error และเบราว์เซอร์หยุดรันกลางคัน การ์ด RVC จึงค้างอยู่ในสถานะซ่อน
- **กฎเหล็กมาตรการป้องกันถาวร (Zero Regression Protocol):**
  1. **ห้าม Overwrite ไฟล์ทั้งไฟล์เด็ดขาด (Surgical Edits Only):** ห้ามนำไฟล์ HTML หรือสคริปต์ขนาดใหญ่มาเขียนทับทั้งดุ้นเด็ดขาด ทุกการแก้ไขต้องทำเฉพาะบรรทัดที่ต้องการเปลี่ยน (Targeted Diff) บนไฟล์ปัจจุบันเท่านั้น
  2. **ตรวจสอบ Syntax ก่อน Sync เสมอ:** รันคำสั่ง `node -c` เช็กความถูกต้องของ JavaScript 100% ทุกครั้งก่อนส่งออกไปยัง `dist/`
  3. **ตรวจจับ Page Error ด้วย Headless Browser:** ดักจับ `page.on('pageerror')` หากมี Error แม้แต่ตัวเดียว จะไม่อนุญาตให้ผ่าน
  4. **ถ่ายภาพ Full Window ตรวจขอบและเลย์เอาต์:** ต้องแคปภาพหน้าต่างทั้งใบ ตั้งแต่ Header จนถึง Footer เพื่อยืนยันว่าไม่มีการ์ดใดถูกตัดขอบ หรือมีช่องว่างมืดผิดปกติ
  5. **ตรวจสอบ `git diff` ทุกครั้งก่อนจบงาน:** ตรวจเช็ก Diff อย่างละเอียดว่าไม่มีฟีเจอร์เดิมถูกลบออกโดยไม่ได้ตั้งใจ
- **สถานะ:** รับทราบความผิดพลาด ดำเนินการแก้ไขฟื้นฟูครบถ้วน 100% และล็อกระบบป้องกันไม่ให้เกิดซ้ำอีกเด็ดขาด

### [2026-10-29 19:15] ปรับปรุงระบบทดสอบเสียง: ป้องกันการคลิกซ้ำ (Button Locking), แสดงสถานะกำลังเตรียมอ่าน/กำลังอ่าน และเร่งความเร็วด้วย In-Memory LRU Cache
- **ปัญหาที่พบก่อนหน้า:**
  1. ปุ่ม `🎵 ทดสอบฟัง` และ `🔊 ทดลองอ่าน` เมื่อกดแล้วไม่มีการเปลี่ยนข้อความบนปุ่ม และไม่ถูก Disable ทำให้ผู้ใช้รู้สึกว่าระบบค้าง และสามารถกดย้ำๆ ซ้ำๆ จนเสียงชนกันได้
  2. การสร้างเสียงอ่านใช้เวลารอสักครู่ (Edge-TTS + RVC Inference รวมประมาณ 0.8-1.5 วินาที) โดยไม่มี Cache ในฝั่งเซิร์ฟเวอร์ ทำให้การกดทดสอบคำเดิมต้องดึงจากภายนอกใหม่ทุกครั้ง
- **การแก้ไขที่ดำเนินการ:**
  1. **Button Locking & Multi-Stage Visual Feedback:**
     - เพิ่ม ID ให้ปุ่มและข้อความสถานะ: `#winBtnVoiceTestMsg`, `#secBtnVoiceTestMsg`, `#secBtnVoiceTest`, `#winTtsTestStatus`
     - ปรับปรุงฟังก์ชัน `playVoiceTest()` ใน `src/index.html` และ `dist/index.html`:
       - **จังหวะคลิก (0ms):** ปิดการคลิกทันที (`disabled = true`, `opacity: 0.65`, `cursor: not-allowed`, `pointer-events: none`) ทั้งในหน้าต่างหลักและ Popout ทุกบาน พร้อมเปลี่ยนข้อความบนปุ่มเป็น `⏳ กำลังเตรียมเสียง...` และแถบสถานะเป็น `⏳ กำลังเตรียมเสียงอ่าน...`
       - **จังหวะเริ่มพูด (`audio.onplay`):** เปลี่ยนข้อความบนปุ่มเป็น `🔊 กำลังอ่าน...` และแถบสถานะเป็น `🔊 กำลังเล่นเสียงทดสอบ...`
       - **จังหวะจบ (`audio.onended` / `onerror`):** คืนสถานะปุ่มกลับมาคลิกได้ตามปกติ คืนข้อความเดิม `🎵 ทดสอบฟัง` และ `🔊 ทดลองอ่าน` พร้อมแสดงสถานะ `✅ เล่นเสียงอ่านสำเร็จเรียบร้อยแล้ว`
       - มี Safety Timeout (25 วินาที) ป้องกันปุ่มค้างกรณีเน็ตเวิร์กหลุด
  2. **Latency Optimization ด้วย In-Memory LRU Cache:**
     - ใน `launch_dev.py` เพิ่ม `_TTS_AUDIO_CACHE` (ความจุ 128 รายการ, Thread-safe พร้อม `_TTS_CACHE_LOCK`)
     - ทำ Cache Key จาก `(processed_text, gender, rate, pitch, volume, preview, rvc_enabled, rvc_model)`
     - ผลการทดสอบ: การทดสอบคำซ้ำลดเวลาการรอจาก ~867ms เหลือเพียง **0.002ms** (เล่นเสียงได้ทันทีแบบ Instant 0ms)
- **การทดสอบและผลลัพธ์ (Playwright & Benchmark):**
  - รันการทดสอบด้วย Playwright Headless Browser ตรวจสอบครบทุกสเตจ (Preparing -> Playing -> Restored): ผ่าน 100%
  - บันทึกภาพหลักฐานยืนยัน: `verified_voice_test_preparing.png`, `verified_voice_test_playing.png`, `verified_voice_test_restored.png`

### [2026-10-29 19:35] เพิ่มเครื่องมือจัดการแชทสด (บล็อก | ลบ) พร้อมระบบล้างประวัติ Blacklist และการแสดงสรุปผลโหวต ASK แบบกราฟแนวนอน
- **ฟีเจอร์ที่พัฒนาใหม่:**
  1. **เครื่องมือด่วนประจำแถวข้อความแชทสด (`🚫 บล็อก | 🗑️ ลบ`):**
     - เพิ่มชุดปุ่มเครื่องมือที่มุมขวาบนของแต่ละแถวข้อความแชทสด (`.chat-row-actions`) แสดงผลอย่างเป็นระเบียบ สะอาดตา และชัดเจนขึ้นเมื่อนำเมาส์ไปชี้ (Hover)
     - **ปุ่ม `🗑️ ลบ`:** ลบเฉพาะข้อความนั้นทิ้งทันที ทั้งในหน้าต่างหลักและ Popout พร้อมยกเลิกคิวเสียง TTS ของข้อความนั้นหากยังไม่ได้อ่าน
     - **ปุ่ม `🚫 บล็อก`:** เปิดหน้าต่างตั้งค่าการบล็อกเฉพาะบุคคล (`#modal-block-user`) ตามมาตรฐาน Zero GPU Lockup
  2. **หน้าต่างตัวเลือกการบล็อกผู้ใช้ (Block User Modal):**
     - ประกอบด้วย 4 ตัวเลือกอิสระ:
       1. `[ ]` ไม่แสดงผล (ซ่อนจาก OBS Overlay)
       2. `[ ]` ไม่อ่าน TTS (ปิดเสียงอ่าน)
       3. `[ ]` ไม่ให้ใช้คำสั่ง replie (บล็อกแชทบอท)
       4. `[ ]` ใส่ Blacklist (บล็อกถาวร 100%)
     - **กฎเหล็ก Blacklist:** เมื่อติ๊ก "ใส่ Blacklist" ระบบจะเลือกตัวเลือกทั้งหมดให้อัตโนมัติ และเมื่อกดบันทึก **จะทำการกวาดลบข้อความทั้งหมดที่ผู้ใช้นี้เคยส่งมาในอดีตออกจากแชทสดทันที** พร้อมตัดเสียงอ่านและบล็อกถาวร 100%
  3. **การแสดงสรุปผลโพล ASK เป็นกราฟแนวนอนในแชทสด:**
     - เมื่อจบโพล ASK (`endAskPoll()`) ระบบจะสร้างการ์ดสรุปผล (`.ask-poll-result-row`) ลงในช่องแชทสดโดยอัตโนมัติ
     - แสดงแถบกราฟแท่งแนวนอน (Horizontal Bar Chart) ตามสีประจำตัวเลือก พร้อมจำนวนคะแนนโหวตและเปอร์เซ็นต์ (%) อย่างชัดเจน
     - แสดงสัญลักษณ์มงกุฎ 👑 สำหรับตัวเลือกอันดับ 1
     - แสดงแถบสรุปด้านล่าง: ยอดคะแนนโหวตรวม และจำนวนคนดูที่ร่วมโหวตทั้งหมด พร้อมปุ่ม `✕` สำหรับลบการ์ดออกได้
- **การทดสอบและผลลัพธ์ (Playwright):**
  - จำลองข้อความแชท 4 ข้อความ: ทดสอบลบข้อความเดี่ยวสำเร็จ
  - ทดสอบบล็อกแบบ Blacklist ผู้ใช้ Spam: ข้อความในอดีตทั้งหมดของผู้ใช้นั้นถูกลบเกลี้ยงทันที ข้อความของผู้ใช้อื่นคงอยู่ครบถ้วน
  - ทดสอบเรนเดอร์การ์ดผลโหวต ASK: กราฟแนวนอน สถิติคะแนน และอันดับผู้ชนะแสดงผลถูกต้อง 100%
  - บันทึกภาพยืนยัน: `verified_block_user_modal.png` และ `verified_live_chat_tools_and_ask_poll.png`

### [2026-10-29 19:40] ผูกระบบ Blacklist เข้ากับ ASK Poll, Giveaway และ Replie อย่างสมบูรณ์ 100%
- **ข้อกำหนดที่ยืนยัน:**
  - คนดูที่ถูกใส่ Blacklist ต้องไม่มีสิทธิ์มีส่วนร่วมกับฟีเจอร์เชิงโต้ตอบใดๆ ทั้งสิ้น ได้แก่ โหวต ASK, สุ่มของรางวัล Giveaway และเรียกคำสั่งแชทบอท Replie
- **การดำเนินการที่ทำเพิ่ม:**
  1. **การยกเลิกสิทธิ์ทันทีเมื่อกด Blacklist (`purgeUserChatMessages`):**
     - หากคนดูคนนั้นเคยโหวตใน ASK Poll คะแนนโหวตจะถูกหักลบออกทันที และลบชื่อออกจากตาราง `voters`
     - หากคนดูคนนั้นเคยพิมพ์โค้ดเข้าร่วม Giveaway รายชื่อจะถูกตัดออกจากตาราง `_gwParticipants` ทันที พร้อมอัปเดตยอดคนและรีเฟรชหน้าจอ
     - ตัดชื่อออกจาก `_activeChattersSet` (สุ่มคนดูสด) ทันที
  2. **การบล็อกการเข้าร่วมใหม่ในอนาคต (Guards):**
     - `checkRealAskVote()`: ตรวจสอบ Blacklist ปฏิเสธการบันทึกคะแนนโหวตทั้งหมด
     - `checkRealGwEntry()`: ตรวจสอบ Blacklist ปฏิเสธการเข้าร่วมชิงรางวัลทั้งหมด
     - `checkRealReplieCommand()`: ตรวจสอบ Blacklist และบล็อกสิทธิ์ Replie ปฏิเสธการเรียกใช้แอนิเมชันและเสียงบอททั้งหมด
- **การทดสอบและผลลัพธ์ (Playwright):**
  - รัน `verify_blacklist_restrictions.py` ทดสอบ BadActor ก่อนและหลัง Blacklist:
    - คะแนนโหวต ASK ก่อนบล็อก: 1 ➔ หลังบล็อก: 0
    - ผู้เข้าร่วม Giveaway ก่อนบล็อก: 1 ➔ หลังบล็อก: 0
    - ความพยายามโหวตใหม่ / พิมพ์โค้ด Giveaway ใหม่ / พิมพ์คำสั่ง Replie `!hi` ใหม่: ถูกปฏิเสธทั้งหมด 100% (Passed 100%)

### [2026-10-29 23:35] ปรับปรุงระบบเสถียรภาพ UI, ระบบอัปเดตอัตโนมัติ Background Auto-Download และระบบยืนยันก่อนปิดโปรแกรม
- **1. แก้ไขบั๊กขนาดตัวอักษร RVC Status Badge ย่อ/ขยาย Loop เมื่อซูม 120%/140%:**
  - เปลี่ยนจากการกำหนด inline `style.cssText` ใน setInterval (400ms) ใน `src/rvc_controls.js` มาเป็นการสลับคลาส CSS `.rvc-status-badge.ready`, `.loading`, `.idle`, `.error`
  - ทำให้ `ui_readability.js` MutationObserver ไม่ถูก trigger วนลูป ขนาดตัวอักษรนิ่งสนิท 100% ไม่มีการขยายหดสั่นไหว
- **2. ระบบอัปเดตอัตโนมัติ Background Auto-Download + ถาม OK / Later + Auto-Update ก่อนเปิดโปรแกรมรอบหน้า:**
  - ใน `updater.py`: เพิ่ม `start_background_download(info)`, `get_update_runtime_status()`, `apply_pending_update_on_startup(splash_ctrl)`, และ `restart_and_apply_update()`
  - จัดเก็บไฟล์อัปเดตและ manifest ไว้ที่ `%LOCALAPPDATA%/BroadcastPlayroom3/pending_update`
  - เมื่อตรวจพบเวอร์ชันใหม่ ระบบจะเริ่มดาวน์โหลดในเบื้องหลังทันทีโดยไม่รบกวนการใช้งาน
  - เมื่อคลิกปุ่มอัปเดตบน Server Rail (#btnRailUpdate) จะเปิดหน้าต่าง `#modal-fast-update` แสดงสถานะความพร้อม พร้อมปุ่มเลือก:
    - **OK (รีสตาร์ทเพื่ออัปเดต):** ติดตั้งแพตช์และรีสตาร์ทโปรแกรมทันที
    - **Later (ไว้ภายหลัง):** ปิดหน้าต่างโดยยังคงเปิดโปรแกรมให้ใช้งานต่อ และเมื่อเปิดโปรแกรมใหม่ในครั้งถัดไป `launch_dev.py` จะทำการแตกไฟล์อัปเดตติดตั้งโดยอัตโนมัติก่อนเปิดหน้าต่างหลักทันที
- **3. ป้องกันการเผลอปิดโปรแกรมโดยไม่ตั้งใจ (Close Confirmation):**
  - เพิ่มปุ่มปิดโปรแกรมสีแดง `#btnTopbarCloseApp` บน Topbar ฝั่งขวาสุด
  - สร้าง Modal ยืนยันการปิดโปรแกรม `#modal-confirm-exit` (Zero GPU Lockup: `rgba(2, 6, 23, 0.88)`, `contain: strict; isolation: isolate;`)
  - เพิ่มฟังก์ชันดักจับ native `beforeunload` เพื่อป้องกันการเผลอกดปิดจากปุ่ม 'X' ขวาบนของ Windows OS
  - เพิ่มตัวเลือกตั้งค่า `[x] ถามยืนยันก่อนปิดโปรแกรมเสมอ` ใน Settings > About และบันทึกลงใน localStorage
- **การทดสอบจริง (Playwright Test):**
  - ผ่านการทดสอบครบทุกข้อ:
    - RVC font size นิ่งคงที่ 11px ทั้งที่ 120% และ 140%
    - Modal ปิดโปรแกรมและปุ่มยกเลิก/ยืนยันทำงานสมบูรณ์
    - Modal อัปเดตแสดงปุ่ม OK และ Later ชัดเจน พร้อมรักษาปุ่มอัปเดตไว้บนแถบด้านข้าง
    - API `/api/update-status` คืนสถานะถูกต้อง

### [2026-10-29 23:45] ปรับรูปแบบเลขเวอร์ชันใหม่เป็น 2 หลักเรียบง่าย (v3.1, v3.2 ... v3.100)
- **ปรับเปลี่ยนรูปแบบเวอร์ชัน (Simplified 2-segment Versioning):**
  - ยกเลิกระบบเลข 3 หลักแบบเดิม (เช่น 3.0.0, 3.0.1) เปลี่ยนเป็นรูปแบบเรียบง่ายตามความต้องการ: `v3.1`, `v3.2`, `v3.3`, `v3.4`, `v3.5` ไปจนถึง `v3.100+`
  - ปรับปรุงฟังก์ชัน `_parse_version` ใน `updater.py` ให้ตัดเลขศูนย์ท้ายส่วนเกิน (`trailing zeros`) เพื่อรองรับการเปรียบเทียบทั้งเลข 2 หลักและเวอร์ชันเดิมได้อย่างแม่นยำ
  - ทดสอบการเปรียบเทียบเวอร์ชัน: `3.2 > 3.1`, `3.10 > 3.9`, `3.100 > 3.99` ผ่านฉลุย 100%
  - อัปเดตไฟล์คอนฟิกทั้งระบบ: `version.json`, `package.json`, `updater.py`, `src/index.html`, `installer_gui.py` ให้เริ่มต้นที่ **`v3.1`**
