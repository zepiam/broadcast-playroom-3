# Update WORKLOG.md and HANDOFF.md with UTF-8
worklog_entry = """## [2026-11-01 12:30] – Antigravity (Published v3.7 LIVE: Fix Giant Icon, Missing Stylesheets, Popout Headers & Splash Removal)

- **ผู้ดำเนินการ:** Antigravity (Google DeepMind)
- **สถานะ:** เผยแพร่เวอร์ชัน 3.7 (v3.7) ขึ้น GitHub Releases สำเร็จ พร้อม Cumulative Patches (Lite 28.2 MB / Full 92.6 MB)
- **สรุปสิ่งที่ดำเนินการและแก้ไข:**
  1. **แก้ไขอาการเปิดโปรแกรมแล้วรูปไอคอนใหญ่เต็มจอ (FOUC / Missing Stylesheet):**
     - **สาเหตุ:** `vite build` ไม่ได้แนบ `<link rel="stylesheet" href="./styles.css">` ลงใน `dist/index.html` ทำให้อินเทอร์เฟซไม่มีสไตล์ พื้นหลังกลายเป็นสีขาว และ `.desktop-titlebar-icon` (`bp-full-icon.png` ขนาด 1254x1254) ไม่มี CSS กำหนดความกว้าง จึงขยายเต็มจอ
     - **วิธีแก้ไข:**
       - เพิ่มระบบ Auto-inject สไตล์ชีตทั้งหมด (`styles.css`, `modal.css`, `widget_customizer.css`, `composer_studio.css`, `composer_widget_themes.css`, `ui_readability.css`) เข้าไปใน `<head>` ของ `dist/index.html` เสมอใน `copy_dist_assets.py`
       - ใส่ inline constraint `style="width:16px!important;height:16px!important;max-width:16px!important;max-height:16px!important;object-fit:contain;flex-shrink:0;display:inline-block;"` โดยตรงบนแท็ก `<img>` ของ `.desktop-titlebar-icon` เพื่อป้องกันรูปขยายแม้ในเสี้ยววินาทีก่อน CSS โหลด
       - ใส่ inline style `background:#1e1f22!important;color:#f2f3f5!important;` บนแท็ก `<html>`
  2. **ปิดหน้าต่างโหลด Splash Screen ถาวรตามคำขอ (Instant Startup):**
     - เนื่องจากแอปเปิดเร็วขึ้น 13 เท่าอยู่แล้ว (0.96 วินาที) ผู้ใช้ไม่ต้องการให้มีหน้าต่าง Splash
     - อัปเดต `launch_dev.py` กำหนด `no_splash = True` โดยเด็ดขาด
     - อัปเดต `splash.py` ให้ `create_splash()` ส่งกลับ `DummySplashController` แบบ no-op และ `run_splash_subprocess()` จบการทำงานทันที (exit 0) ไม่มีการสร้าง subprocess หรือเรียก PySide6 สำหรับ splash อีกต่อไป
  3. **แก้ปัญหาปุ่มย่อ/ปิดหน้าต่างซ้อนกันในหน้าต่างแยก (Popout Tool Windows):**
     - ในหน้าต่างป๊อปอัป มีทั้งปุ่มของ Windows (`_ □ X`) และปุ่มของเว็บ (`_ X`) ซ้อนกัน
     - ซ่อน `.floating-actions-right` และ `.desktop-titlebar` ภายในหน้าต่างป๊อปอัปให้เหลือเฉพาะ Titlebar ระบบของ Windows เพียงชุดเดียว
  4. **ซิงค์สถานะซ่อน/แสดงแพลตฟอร์ม (Sidebar vs Settings):**
     - ปรับให้การซ่อนแพลตฟอร์มมีผลทันทีทั้งในหน้าแรก (Sidebar compact & normal cards) และในหน้าต่าง Settings
  5. **สร้าง Cumulative Patch v3.7 และ Release ขึ้น GitHub:**
     - `BroadcastPlayroom3-Lite-Patch-3.7.zip` (28.2 MB)
     - `BroadcastPlayroom3-Full-Patch-3.7.zip` (92.6 MB)
     - อัปเดต `version.json` บน GitHub `master` branch และ GitHub Releases `v3.7` ให้ระบบ In-app updater ตรวจพบและดาวน์โหลดได้ทันที
  6. **การตรวจสอบผลการทำงาน (Verification):**
     - ทดสอบผ่าน Playwright script `tests/verify_ui_fixes.py`:
       - ขนาด `.desktop-titlebar-icon` กว้าง 16px สูง 16px แม่นยำ 100%
       - สีพื้นหลังบอดี้ `#1e1f22` ไม่ขาว
       - หน้าต่างป๊อปอัปไม่มีปุ่มซ้อน (`desktopTitlebar` = none, `floating-actions-right` = none)
       - ผ่านทุกการทดสอบ (All Playwright tests passed)

---

"""

with open("WORKLOG.md", "r", encoding="utf-8") as f:
    old_worklog = f.read()

with open("WORKLOG.md", "w", encoding="utf-8") as f:
    f.write(worklog_entry + old_worklog)

print("WORKLOG.md updated successfully!")

handoff_content = """# Broadcast Playroom 3 - Session Handoff

## Current Status (2026-11-01 12:30)
- **Active Release:** `v3.7` (LIVE on GitHub Releases)
- **Repo:** `zepiam/broadcast-playroom-3`
- **Key Changes in v3.7:**
  1. **Fixed Giant Anime Icon / White Screen Bug:** Auto-inject all required stylesheets (`styles.css`, `modal.css`, `widget_customizer.css`, etc.) into `dist/index.html`. Added inline CSS dimensions `16px!important` to `.desktop-titlebar-icon`.
  2. **Removed Splash Screen Permanently:** Converted `splash.py` to dummy no-op and set `no_splash = True` in `launch_dev.py` for instant 0.9s cold startup.
  3. **Fixed Duplicate Controls in Popout Windows:** Hid `.floating-actions-right` and `#desktopTitlebar` in standalone popouts, keeping only the native OS window frame.
  4. **Synchronized Platform Hiding:** Sidebar and Settings platform cards immediately reflect visibility changes across all views.
- **Verification:** All tests passed with Playwright (`tests/verify_ui_fixes.py`).
"""

with open("HANDOFF.md", "w", encoding="utf-8") as f:
    f.write(handoff_content)

print("HANDOFF.md updated successfully!")
