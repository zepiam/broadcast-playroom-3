# HANDOFF NOTES - Broadcast Playroom 3 (v3.87)
- **Current Version**: v3.87 (Released — grey/crashed window auto-recovery + Microsoft Edge as default browser)
- **Status**: Tested, Smoke Test Gate Passed, Published to GitHub & Hugging Face.
---

> 📘 ปัญหา RVC/TTS: อ่าน `RVC_FLOW.md` ก่อน (flow, ไฟล์, data dir, เหตุการณ์ที่ผ่านมา, ขั้นตอนไล่ปัญหา)

## 🛠️ ยังไม่ปล่อย (รอ release ถัดไป) — ตำแหน่งเสียงอ่าน 3 มิติ (Claude, 2026-11-27)
- **ผู้ใช้ขอ:** ปรับตำแหน่งเสียง TTS รอบตัวแบบ ASMR (หน้า/หลัง/ซ้าย/ขวา/ใกล้/ไกล) มีรูปคนตรงกลางให้ลากจุดเสียง + ปุ่มทดสอบฟัง
- **ไฟล์ใหม่ `src/tts_spatial.js`** (เพิ่มใน `copy_dist_assets.py` และ `<script>` ถัดจาก `tts_avatar.js` ใน `src/index.html`): `window.bp3SpatialAudio.attach(audio)` ต่อ `<audio>` → `MediaElementSource` → `PannerNode` (HRTF, inverse distance, rolloff 0.45) → limiter (`DynamicsCompressor` -2 dB, ratio 20 กัน HRTF ทำเสียงหูใกล้ดังจนแตก) → ลำโพง. **ตำแหน่งตรงกลาง (ค่าเริ่มต้น) = ไม่ต่อผ่าน Web Audio เลย เสียงเหมือนเดิม 100%**; ถ้า AudioContext ไม่ running ก็เล่นปกติ (ไม่เสี่ยงเงียบ). ค่าตั้ง `localStorage.bp3_tts_spatial = {x,y}` (x ขวา+, y หน้า+, ระยะ = รัศมี → 0.35–3.55 ม.), sync ข้ามหน้าต่างด้วย storage event, ขยับระหว่างเล่นเปลี่ยนตำแหน่งทันที
- **UI:** การ์ด "🎧 ตำแหน่งเสียงอ่าน" แทรกต่อจากการ์ด "ปรับแต่งเสียง (Volume, Speed & Pitch)" ทั้งใน Voice Settings และ Settings > TTS (inject ด้วย JS ไม่แก้ markup): วงกลมมองจากด้านบน หัวคนตรงกลาง (จมูกชี้หน้า) ลากจุด/คลิก/ลูกศร (Shift = ก้าวใหญ่, Home = ตรงกลาง; **ไม่ใช้ Escape เพราะเป็นปุ่มปิดหน้าต่างของแอป**), ป้ายหน้า/หลัง/ซ้าย/ขวาอยู่นอกวง, ข้อความบอกทิศ+ระยะ, preset 7 แบบ (ตรงกลาง, ข้างหน้า, ข้างหูซ้าย, ข้างหูขวา, ด้านหลัง, กระซิบข้างหู, ไกลออกไป), ปุ่ม "▶ ทดสอบฟังตำแหน่งนี้"/"⏹ หยุดทดสอบ" อ่านข้อความทดสอบเสียงเดิม (`bp3_tts_test_message`) ด้วยเพศ/speed/pitch/volume ปัจจุบัน
- **ใช้กับ:** เสียงอ่านแชท (คิวหลัก, ไม่รวมเสียงลับ/secret sounds), ปุ่มทดลองอ่านเสียง, อีกจุดเล่น TTS (~บรรทัด 61495), ทดลองฟังคำในพจนานุกรม, ปุ่ม ▶ ทดสอบโมเดล RVC (`rvc_controls.js`)
- **ทดสอบแล้ว:** engine test (Chromium + Edge, วัด RMS แยกช่องซ้าย/ขวาด้วย Analyser): ตรงกลางไม่ถูก route; ซ้าย L≈0.21/R≈0.12, ขวากลับกัน; หน้า/หลัง L=R แต่ระดับต่างกัน (HRTF filter); ไกลเบากว่าใกล้; `audio.volume` และ `muted` ยังทำงานหลัง route (0.2 → ~20%, muted → 0); ไม่มี error. UI test บนหน้าจริงจาก `launch_dev.QuietHandler` (Edge): การ์ด 2 ใบอยู่ถัดจากการ์ด Volume/Speed/Pitch, ลากไปขวาหน้า → บันทึก + ข้อความ "ขวาหน้า • ระยะปานกลาง", preset, ลูกศร, Home, อีกหน้าต่างได้ค่าใหม่, ไม่มี page error; ปุ่มทดสอบจริงกับ Edge-TTS: AudioContext running, ปุ่มเปลี่ยนเป็นหยุดแล้วกลับเมื่อเสียงจบ. ภาพ preset 4 แบบตรวจแล้วจุดไม่ทับป้าย. build + gates ผ่าน
- **ยังไม่ทดสอบ:** หูฟังจริง/การรับรู้หน้า-หลังของคน; คิวแชทจริงในหน้าต่างหลัก (ต่อเหมือนจุดอื่น); OBS ที่จับเสียงเป็นโมโนจะทำให้มิติหาย (ต้องให้ผู้ใช้ตั้ง stereo)
- **เพิ่ม (2026-11-27): ปุ่ม 3D บน top bar** (`#topbarTts3dToggle`, inject ถัดจาก `#topbarRvcBadge` หรือ `.topbar-gender-switch` ใน Lite; ใช้ class `topbar-rvc-badge tts3d-badge` + `tts3d-on/off`, ไม่มีแอนิเมชัน): คลิก = สลับเสียง 3 มิติ ↔ เสียงอ่านปกติ, คลิกขวา = เปิดหน้าต่างตั้งค่าเสียง, ตอนเปิดแสดง "3D <ทิศ>" + tooltip. State ใหม่ `bp3_tts_spatial = {x, y, on}`: ปิดแล้วจำตำแหน่งไว้ เปิดกลับมาใช้ตำแหน่งเดิม (ถ้าเคยเป็นตรงกลางใช้ค่าเริ่ม ขวาหน้า 0.55/0.35); เลือกตำแหน่งในการ์ด = เปิดเอง, preset ตรงกลาง = ปิด; การ์ดตอนปิดแสดง "ปิด 3D อยู่ • เสียงปกติ"; ค่าเก่า `{x,y}` ไม่มี `on` อ่านเป็นเปิดถ้าไม่ใช่ตรงกลาง. API: `bp3SpatialAudio.setOn/toggle/isOn`. ปิดระหว่างเสียงกำลังเล่นที่ route แล้ว → ย้ายไปหน้าตรง 1 ม. (ใกล้เสียงปกติที่สุด). ทดสอบบนหน้าจริง (Edge): 14/14 (ปุ่มอยู่ถัด RVC badge, ค่าเริ่มปิด, เปิด→ขวาหน้า+route, เลือกซ้ายแล้วปุ่มตาม, ปิด→จำตำแหน่ง+ไม่ route, การ์ดแสดงปิด, เปิดกลับได้ตำแหน่งเดิม, ตรงกลาง=ปิด, หน้าต่างอื่นสั่งปิดแล้วปุ่มหน้าหลักตาม, ค่าเก่าโหลดถูก, ปิดแล้วรีโหลดยังปิด, ไม่มี error) + engine/การ์ด regression ผ่านทั้งหมด
- **พบระหว่างทดสอบ (ไม่ได้แก้, มีอยู่เดิม):** บางครั้ง `user_controls.js` เรียก `window.BP3Blacklist.botNames/classify` ก่อน `blacklist.js` พร้อม → page error 2 ตัว (เกิด 1 ใน ~10 ครั้ง, เกิดทั้งที่มีและไม่มี tts_spatial.js — ตรวจ 8 รอบเท่ากัน 0)

## 🚀 RELEASED v3.87 — ใช้ Microsoft Edge เป็นค่าเริ่มต้น (Claude, 2026-11-26)
- **Release v3.87 (รวมสองหัวข้อนี้):** `publish_release_v387.py` (คัดจาก v386 + เพิ่ม `app_window_ownership.py` ใน CORE_FILES) → build + gates ผ่าน, SHA-256 gate ผ่าน, HF + GitHub Release v3.87 + tag + purge jsDelivr สำเร็จ (commit 9029b97). ตรวจหลังปล่อย: patch lite/full จาก GitHub และ HF SHA-256 ตรง `version.json` ทั้ง 4 ไฟล์, `version.json` ทั้งสองที่เป็น 3.87, zip มี `app_window_ownership.py`/`app_presence.py`/`power_guard.py` ทั้ง root และ `_internal/`
- **ผู้ใช้สั่ง:** ให้โปรแกรมเปิดหน้าต่างด้วย Edge เป็น default (มีทุกเครื่อง Windows 10/11)
- **แก้ (`launch_dev.py`):** `find_browser()` ลำดับใหม่ Edge → Chrome (`_EDGE_CANDIDATES`/`_CHROME_CANDIDATES`); override ได้ด้วย env `BP3_BROWSER=chrome` หรือ `{"browser": "chrome"}` ใน `data/power_settings.json` (`_browser_preference()`). โปรไฟล์แยกตาม browser: Edge ใช้ `data/browser_profile_edge`, Chrome ใช้ `data/browser_profile` เดิม (`app_browser_profile_dir()`) — ห้ามให้ Edge กับ Chrome ใช้ `--user-data-dir` เดียวกัน. ครั้งแรกที่สร้างโปรไฟล์ Edge จะคัดลอก `Default/Local Storage` + `Default/IndexedDB` จากโปรไฟล์เดิม (`_seed_profile_storage`, log `[LAUNCH] Copied app settings`) → ค่าตั้งใน localStorage ไม่หาย. หน้าต่างหลักและ popout ใช้ helper เดียวกัน. `updater.py` ล้าง cache ทั้งสองโปรไฟล์. `app_window_ownership.py` ยอมรับทั้งสองโปรไฟล์
- **⚠️ ต้องทำตอน release:** เพิ่ม `app_window_ownership.py` ใน `CORE_FILES` (ตอนนี้ไม่มีในแพตช์ ใช้ตัวที่คอมไพล์ใน exe; เครื่องติดตั้งไม่มีไฟล์นี้บนดิสก์). `BP3_PatchInstaller.exe` (คอมไพล์แล้ว) ยังล้าง cache แค่ `browser_profile` — ไม่กระทบเพราะ `open_app_window` ล้าง cache ของโปรไฟล์ที่ใช้ทุกครั้งที่เปิดอยู่แล้ว
- **ทดสอบแล้ว (dev app + Edge 158 จริง):** เปิดด้วย msedge.exe + คัดลอกค่าตั้งสำเร็จ; เทียบ localStorage ของ origin 127.0.0.1:8801 ระหว่างโปรไฟล์ Chrome เดิมกับ Edge ใหม่: **66/66 key ตรงกันทั้งขนาด**; ปิดปกติออก 5.5 วิ (Edge ไม่ค้าง background); ฆ่า renderer → กู้หน้าต่างใน 52 วิ, ปิดหลังกู้ 6.5 วิ; หน้า OBS เก่า 6.0 วิ; reopen ไม่มีหน้าต่าง → เปิดใหม่ 1.0 วิ (ผ่าน msedge). **การแสดงผล:** หน้าต่างหลัก + popout 5 ตัว (voice-settings, settings, composer, giveaway, user-manager) เปิดใน msedge.exe + `browser_profile_edge` ทุกตัว, จับภาพด้วย PrintWindow เทียบกับ Chrome (`BP3_BROWSER=chrome` ซึ่งยืนยันว่า override ใช้ได้) ต่างกัน ≤0.09% พิกเซล (anti-aliasing); Overlay `/?p=1`, `/?p=1&test=1`, `/chat-widget` ใน Edge และ Chromium: widgets ครบ (10/10/2), พื้นหลังโปร่งใส, ไม่มี UI โปรแกรม, ไม่มี page error. Overlay ใน OBS ใช้ CEF ของ OBS เอง ไม่ขึ้นกับการเปลี่ยน browser. build + gates ผ่าน
- **ยังไม่ทดสอบ:** exe จริง; ผู้ใช้ที่ไม่มี Edge (ตกไป Chrome ตามเดิม); เครื่องที่ไม่มีทั้งคู่ (เปิดใน default browser — ไม่มี watchdog/กู้หน้าต่าง)

## 🚀 RELEASED v3.87 — หน้าเทาหลังเปิดทิ้งไว้ + โปรแกรมหายเอง (Claude, 2026-11-26)
- **อาการ (ผู้ใช้แจ้ง, v3.86):** เปิดทิ้งไว้ ไม่ได้ปิด กลับมาเจอหน้าต่างสีเทาเปล่า (title ยังเป็น Broadcast Playroom v3.86)
- **หลักฐานบนเครื่องเจ้าของ:** `ui_health.log` มี `ok:` ทุก 5 นาทีถึง 22:39:04 แล้วหยุด; ตอน 23:11 ไม่มี `BroadcastPlayroom3-Full.exe` แล้ว แต่ Chrome ของโปรแกรม (เริ่ม 19:13) ยังอยู่; ไม่มี Application Error/WER → backend **ออกเองแบบ clean** ทางเดียวคือ `app_presence.should_exit()`; ไม่มี crash dump ใน Crashpad. 22:40:03 Windows sync เวลา (ถอย 3.3 วิ) — ยังไม่รู้ว่าเกี่ยวไหม
- **สาเหตุ (ยืนยันด้วย control test):** เมื่อหน้า app ตาย/หลุด (renderer crash, GPU/compositor ล้ม ฯลฯ) SSE `/api/app-presence/stream` ขาด → presence ว่าง 3 วิ → backend ปิดตัวเองทั้งที่หน้าต่าง Chrome ยังเปิด → watchdog ของ power_guard (อยู่ใน backend) ตายตามไปด้วย จึงไม่เคยกู้หน้าเทาได้. Control (โค้ดเดิม, ฆ่า renderer ของหน้าต่าง): backend ออกใน 4 วิ ขณะ Chrome ยังอยู่. **ยังไม่รู้ต้นเหตุที่ทำให้หน้าตาย** (ฝั่ง Chrome) — ตอนนี้แค่ทำให้กู้คืนได้ + มี log
- **แก้:** (1) `app_presence.should_exit(browser_alive=..., hold_max=600, on_hold=...)`: ถ้า presence หายแต่ Chrome main ของโปรแกรมยังรัน → ไม่ปิด (สูงสุด 10 นาที), log `presence: app page disconnected...` เมื่อค้างเกิน 10 วิ (2) `power_guard`: `browser_alive()` (นับว่ายังอยู่ระหว่าง watchdog กำลังรีสตาร์ต — `recovering_until`, ล้างเมื่อเปิดหน้าต่างใหม่เสร็จ), `page_lost()` → watchdog รีสตาร์ตหน้าต่างเมื่อหน้าหลุด ≥35 วิ และไม่มี heartbeat ≥45 วิ (ไม่ต้องรอ 180+240 วิ) (3) `launch_dev.py`: ส่ง callback + log `app exit: ...` ทุกครั้งที่ปิดตัว
- **ทดสอบแล้ว (dev app + Chrome จริงบนเครื่องนี้):** ฆ่า renderer → backend อยู่ต่อ → watchdog รีสตาร์ต → หน้าต่างกลับมาใช้ได้ใน **51 วิ** (ก่อนเร่ง: 232 วิ); ปิดทันทีหลังกู้ → ออกใน 5.5 วิ; ปิดปกติ 5.8 วิ (ไม่มี log hold ปลอม); หน้า OBS เก่าเปิดค้าง → ออก 6.3 วิ; unit test hold logic (limit 600 วิ, browser ปิดระหว่าง hold, behaviour เดิมเมื่อไม่ส่ง callback). build + gates ผ่าน
- **ยังไม่ทดสอบ:** exe จริง + อาการหน้าเทาจริง (ทดสอบด้วยการฆ่า renderer ซึ่งขึ้น "Aw, Snap!" ไม่ใช่เทาเปล่า). LITE ไม่มี psutil — `browser_alive()` พึ่ง Popen ที่ register ไว้; ถ้า Chrome ส่งต่อให้ process เดิม (Popen ออกทันที) จะถือว่า browser ปิด = พฤติกรรมเดิม. ถ้าผู้ใช้ยังเจอ ให้ขอ `ui_health.log` — จะเห็นบรรทัด presence/watchdog/app exit

## 🚀 RELEASED v3.86 — ปิดโปรแกรมแล้วยังค้างใน Task Manager (Claude, 2026-11-26)
- **Release:** `publish_release_v386.py` (คัดจาก v385) → build + gates ผ่าน, SHA-256 gate ผ่าน, HF + GitHub Release v3.86 + tag + purge jsDelivr สำเร็จ (commit 73cf4ec). ตรวจหลังปล่อย: patch lite/full จาก GitHub และ HF SHA-256 ตรง `version.json` ทั้ง 4 ไฟล์, `version.json` ทั้งสองที่เป็น 3.86
- **ยังไม่ยืนยันบนเครื่องจริง:** exe ที่ติดตั้ง + OBS จริง (ปิดหน้าต่างแล้ว process หายใน ~5–7 วิ แม้ OBS เปิดอยู่)
- **อาการ (ผู้ใช้แจ้ง):** กดปิดหน้าต่างแล้ว process ยังค้าง; กดเปิดโปรแกรมใหม่ก็ไม่มีหน้าต่างขึ้น
- **หลักฐานบนเครื่องเจ้าของ (v3.84):** `rvc_debug.log` มี init 18:44 แล้ว init อีก 3 ครั้ง 18:53:41/48/58 แต่ `ui_health.log` มี `power_guard started` แค่ 18:44 → 3 ครั้งหลังเจอ process เก่ายังรันอยู่บนพอร์ต 8801 แล้วแค่สั่ง reopen
- **สาเหตุ:** โปรแกรมปิดตัวเมื่อ `app_presence` ไม่มีหน้าต่าง role=app ต่อ `/api/app-presence/stream`. v3.78–v3.84 เสิร์ฟ `index.html` (มี `app_presence.js data-role="app"`) ที่ `/` ทำให้ Browser Source ของ OBS (`/?p=N`) นับเป็นหน้าต่างโปรแกรม → ปิดหน้าต่างจริงแล้ว process ไม่ออกตราบที่ OBS เปิดอยู่. v3.85 แก้ `/` แล้ว แต่ OBS ที่ยังไม่ refresh ยังรันหน้าเก่าอยู่. บั๊กรอง: `/api/app-instance/reopen` แค่ `bring_main_window_to_front()` — ถ้าไม่มีหน้าต่างก็ไม่ทำอะไร
- **แก้ (`launch_dev.py`):** (1) `/api/app-presence/stream` ปฏิเสธ (403) ถ้า Referer path ไม่ใช่ `/index.html` (ไม่มี Referer = ยอมรับเหมือนเดิม) → หน้า OBS เก่าค้างไม่ทำให้โปรแกรมค้างอีก (2) reopen: ถ้า bring-to-front หาหน้าต่างไม่เจอ → `open_app_window()` ใหม่ใน thread (log `[REOPEN] No app window found`)
- **ทดสอบแล้ว (E2E บนเครื่องนี้ด้วย dev app + หน้าต่าง Chrome จริง + WM_CLOSE):** ปิดธรรมดาออกใน 5.8 วิ; มี RVC โหลดบน GPU ออกใน 7.1 วิ; **กรณีหน้า OBS เก่า** (Playwright เสิร์ฟ index.html ที่ `/?p=1`): หลังแก้ออกใน 6–7 วิ, **control ก่อนแก้ยังค้างเกิน 25 วิ** (ยืนยันสาเหตุ); reopen ตอนไม่มีหน้าต่าง → เปิดหน้าต่างใหม่ใน 0.5 วิ และปิดอีกทีก็ออกปกติ. build + gates ผ่าน
- **ยังไม่ทดสอบ:** exe จริง (frozen) กับ OBS จริง. ตัดออก: thread ที่ไม่ใช่ daemon (ตรวจแล้ว chat threads เป็น daemon ทั้งหมด)

## 🚀 RELEASED HOTFIX v3.85 — Overlay OBS กลายเป็นหน้าโปรแกรม (Claude, 2026-11-26)
- **Release:** `publish_release_v385.py` ล้มที่ STEP 4 (commit message มี `"/"` ใน f-string เครื่องหมายคำพูดซ้อน → TypeError) หลังอัปโหลด HF สำเร็จแล้ว. ทำ STEP 4–6 ต่อด้วยมือ: ตรวจ SHA zip ในเครื่องตรง version.json → commit 4cbede6 + tag v3.85 + push → `gh release create v3.85` (zip x2 + version.json + changelog) → purge jsDelivr 200. แก้ข้อความ commit ในสคริปต์แล้ว (ระวัง: ห้ามใส่ `"` ใน commit message ของสคริปต์ publish)
- **ตรวจหลังปล่อย:** patch lite/full จาก GitHub และ HF SHA-256 ตรง `version.json` ทั้ง 4 ไฟล์, `version.json` ทั้งสองที่เป็น 3.85, release notes ถูกต้อง
- **อาการ (ผู้ใช้แจ้ง):** Browser Source ใน OBS ที่ชี้ `http://127.0.0.1:8801/?p=1` (ลิงก์ที่ Composer Studio สร้าง `${host}/?p=N`) แสดงหน้าโปรแกรมหลักแทน Overlay
- **สาเหตุ:** v3.78 (Antigravity, commit f750730) เพิ่มบล็อก "Layer 2" ต้น `QuietHandler.do_GET` ที่จับ `path in ('/', '/index.html')` แล้วส่ง `dist/index.html` ทำให้ `/` ไม่ไปถึงตาราง `views` (`'/': self.legacy_view` = composer overlay) อีกเลย. พังตั้งแต่ v3.78–v3.84. หน้าต่างโปรแกรมเปิดที่ `/index.html?v=...` จึงไม่ต้องใช้ `/`
- **แก้ (`launch_dev.py` บรรทัดเดียว):** บล็อกนั้นจับเฉพาะ `path == '/index.html'` (ยังได้ no-cache เหมือนเดิม) + คอมเมนต์เตือนห้ามจับ `/`
- **ทดสอบแล้ว:** `QuietHandler` จริง: `/?p=1`, `/?p=1&test=1`, `/`, `/overlay.html?p=1`, `/composer.html?p=1` = Overlay (no-store); `/index.html`, `/index.html?v=3.84` = หน้าโปรแกรม (no-cache). Playwright เปิด `/?p=1&test=1`: 10 widgets, พื้นหลังโปร่งใส, ไม่มี UI โปรแกรม, ไม่มี error. build + gates ผ่านที่ 3.85
- **ยังไม่ทดสอบ:** ใน OBS จริง (อาจต้องกด Refresh ที่ Browser Source หลังอัปเดต)
- **บทเรียน:** ห้ามจับ `/` ใน do_GET — เป็น URL ของ OBS overlay

## 🚀 RELEASED v3.84 — ปุ่มทดสอบฟังเสียงโมเดล RVC (Claude, 2026-11-23)
- **Release:** `publish_release_v384.py` (คัดจาก v383 เปลี่ยน changelog/commit message) → build + gates ผ่าน, SHA-256 gate ผ่าน, HF + GitHub Release v3.84 + tag + purge jsDelivr สำเร็จ (commit 29c0075). ตรวจหลังปล่อย: patch lite/full จาก GitHub และ HF SHA-256 ตรง `version.json` ทั้ง 4 ไฟล์, `version.json` ทั้งสองที่เป็น 3.84
- **ยังไม่ยืนยันบนเครื่องจริง:** อัปเดตผ่านโปรแกรม และปุ่มทดสอบฟังในหน้าต่าง Voice Settings จริง
- **สิ่งที่เปลี่ยน:** แถวโมเดลที่โหลดแล้วมีปุ่มกลม play (`.rvc-cat-play`) หน้าปุ่ม "ใช้โมเดลนี้" → อ่านข้อความทดสอบเสียงด้วยโมเดลนั้น. ระหว่างทำงานปุ่มเป็น pause + วงแหวน SVG ที่เติมตาม `audio.currentTime/duration` (rAF เฉพาะตอนเล่น) ครบรอบพอดีตอนเสียงจบ. ระหว่างทดสอบ ปุ่ม play แถวอื่นกดไม่ได้; กด pause = หยุดทันที; ปิดหน้าต่าง = หยุด. ข้อความ = `localStorage.bp3_tts_test_message` หรือช่องข้อความทดสอบในหน้าตั้งค่าเสียง; เพศ = `window._currentVoiceGender`; speed/pitch/volume จาก `getTtsProsodyForPreview()`
- **Backend:** GET `/api/rvc/preview?id&text&gender&rate&pitch` ใน `launch_dev.py` (Edge-TTS แล้ว `rvc_service.preview()`), คืน `audio/wav`. `preview()` ไม่เปลี่ยนโมเดลที่ใช้อยู่: ถ้าเป็นโมเดลที่โหลดอยู่ใช้ engine เดิม, ไม่งั้นโหลด engine ชั่วคราวแล้ว unload (HuBERT แชร์ cache). ล็อกให้ทดสอบได้ทีละอัน (คำขอซ้อนได้ 400 "กำลังทดสอบเสียงโมเดลอื่นอยู่"), แคชผลล่าสุด 8 รายการ
- **ทดสอบแล้ว:** Playwright harness 13/13 (ปุ่มเฉพาะแถวที่โหลดแล้ว, pause+ring, ปุ่มอื่น disabled, ring เพิ่มแบบ monotonic จนเกือบครบ, จบพร้อมเสียง ~2 วิ, pause หยุดทันที, ใช้ข้อความ/เพศของผู้ใช้, server lock, ไม่แตะโมเดลที่ใช้อยู่); `launch_dev.QuietHandler` จริง: 200 audio/wav, id ผิด 400, Lite 403; **engine RVC จริงบนเครื่องนี้ (GPU) กับ lumine-jp/paimon-jp:** ครั้งแรก ~11 วิ (โหลด HuBERT/rmvpe), โมเดลถัดไป ~1.5 วิ, ซ้ำจากแคชทันที, Edge-TTS ~6.5 วิตอน cold; harness ชุดเดิม (catalog/ลบ) ยังผ่าน; build + gates ผ่าน
- **ยังไม่ทดสอบ:** ในหน้าต่างโปรแกรมจริง. ช่วงเตรียมเสียงครั้งแรกอาจนาน 10–17 วิ มีแค่ปุ่ม pause + ข้อความ "กำลังเตรียมเสียง..." ที่ footer (ไม่ได้ใส่แอนิเมชันโหลด ตามกฎห้ามเพิ่มแอนิเมชันเอง — เสนอผู้ใช้แล้ว). กด pause ระหว่างเตรียมเสียง ฝั่ง server ยังทำต่อจนเสร็จ คลิกโมเดลอื่นทันทีอาจได้ข้อความให้รอ

## 🚀 RELEASED v3.83 — ปุ่มลบโมเดล RVC (Claude, 2026-11-23)
- **Release:** `publish_release_v383.py` (คัดจาก v382 เปลี่ยน changelog/commit message) → build + gates ผ่าน, SHA-256 gate ผ่าน, HF + GitHub Release v3.83 + tag + purge jsDelivr สำเร็จ. ตรวจหลังปล่อย: patch lite/full จากทั้ง GitHub และ HF SHA-256 ตรง `version.json` ทั้ง 4 ไฟล์, `version.json` ทั้งสองที่เป็น 3.83. เลขเวอร์ชัน 3.83 ใน `package.json`, `updater.py`, `copy_dist_assets.py` x2, `src/index.html`
- **ยังไม่ยืนยันบนเครื่องจริง:** อัปเดตผ่านโปรแกรม และการลบโมเดลจริงในหน้าต่าง Voice Settings
- **ไอเดียที่เสนอผู้ใช้ (ยังไม่ทำ):** เปลี่ยนกล่องยืนยันลบจาก `confirm()` ของเบราว์เซอร์เป็นกล่องในธีมโปรแกรม
- **สิ่งที่เปลี่ยน:** ในหน้าต่างโมเดลเสียง RVC แถวที่โหลดแล้วมีปุ่มถังขยะ (`.rvc-cat-delete`) ข้างปุ่ม "ใช้โมเดลนี้"/"กำลังใช้งาน" → ถามยืนยันก่อน (ถ้าเป็นโมเดลที่ใช้อยู่จะบอกว่าจะถูกปิดก่อนลบ) → ลบแล้วแถวกลับเป็นปุ่ม "ดาวน์โหลด"
- **Backend:** `rvc_service.delete_model(id)` + POST `/api/rvc/delete` ใน `launch_dev.py` (ล้าง `_TTS_AUDIO_CACHE` ด้วย). ไฟล์ `.pth` + `.index` ที่คู่กันถูกย้ายไป **Recycle Bin ของ Windows** (`SHFileOperationW` + `FOF_ALLOWUNDO`, กู้คืนได้) ไม่ใช่ลบถาวร. ถ้าเป็นโมเดลที่เลือกอยู่: unload + `selected=None` + บันทึก `rvc_settings.json` ก่อน. ห้ามลบระหว่างโหลด/ดาวน์โหลด. ลบ entry ใน `.catalog_downloads.json` ด้วย. `.index` ที่ตรงกับ `.pth` ตัวอื่นที่ชื่อยาวกว่า (raiden vs raiden-jp) ไม่ถูกลบ
- **ทดสอบแล้ว:** Playwright harness 18/18 (ปุ่มมีเฉพาะแถวที่โหลดแล้ว, กดยกเลิกไม่ลบ, ลบ Lumine ลบ .pth+.index แต่ Raiden อยู่, ลบโมเดลที่ใช้อยู่แล้ว unload, manifest อัปเดต); เรียก Recycle Bin จริงบน Windows สำเร็จ; `npm run build` + gates ผ่าน
- **ยังไม่ทดสอบ:** ในโปรแกรมจริง. โมเดลที่ import เองซึ่งไม่อยู่ใน catalog ยังลบจากหน้านี้ไม่ได้ (ไม่มีแถวให้กด)

## 🚀 RELEASED v3.82 — หน้าต่างโมเดลเสียง RVC แบบรายการ (Claude, 2026-11-23)
- **Release:** `publish_release_v382.py` รันบนเครื่องเจ้าของโดย Claude → build + Safety Gate + Smoke Test Gate ผ่าน, SHA-256 gate ผ่าน, อัปขึ้น Hugging Face + GitHub Release v3.82 + tag + purge jsDelivr สำเร็จ. ตรวจหลังปล่อย: ดาวน์โหลด patch lite/full จากทั้ง GitHub และ HF แล้ว SHA-256 ตรง `version.json` ทั้ง 4 ไฟล์, `version.json` บนทั้งสองที่เป็น 3.82
- **ยังไม่ยืนยันบนเครื่องจริง:** อัปเดตผ่านตัวอัปเดตในโปรแกรม และหน้าต่างโมเดลใหม่ในหน้าต่าง Voice Settings จริง
- **สิ่งที่เปลี่ยน:** หน้าต่าง "ดาวน์โหลดโมเดลเสียงเพิ่ม..." (`openRvcDownloader()` ใน `src/rvc_controls.js`) เปลี่ยนจาก dropdown เป็นรายการการ์ด มีช่องค้นหาและชิปตัวกรอง ทั้งหมด/โหลดแล้ว/Genshin/VTuber/Anime. โมเดลที่โหลดแล้วมีไอคอนเช็คสีเขียว อยู่บนสุด ไม่มีปุ่มดาวน์โหลด มีปุ่ม "ใช้โมเดลนี้" แทน หรือขึ้น "กำลังใช้งาน" ถ้าเป็นโมเดลที่เปิดอยู่. แถวที่กำลังโหลดแสดง % และปุ่มยกเลิก
- **Backend (`rvc_service.py`):** `public_catalog()` ส่ง `installed`, `model_id`, `tag` เพิ่ม. ตรวจว่าโหลดแล้วจาก (1) ไฟล์ `rvc_models/.catalog_downloads.json` ที่บันทึกตอนดาวน์โหลดสำเร็จ (2) จับชื่อไฟล์ `.pth` ในเครื่องกับชื่อใน catalog / ชื่อ zip (ไฟล์หนึ่งนับให้รายการที่ key ยาวที่สุดเท่านั้น กัน Gawr Gura กับ Gawr Gura Talking ชนกัน)
- **ทดสอบแล้ว:** Playwright harness กับ RVCService จริง (fixture engine/downloader) ผ่าน 10/10; `npm run build` + Safety Gate + Smoke Test Gate ผ่าน; `dist/rvc_controls.js` มีโค้ดใหม่. แก้ `tests/verify_compatibility.py` ให้ใช้ selector ใหม่ (ยังไม่ได้รันไฟล์นี้ทั้งไฟล์)
- **ยังไม่ทดสอบ:** ในโปรแกรมจริง (หน้าต่าง Voice Settings แบบ popout) และกับโมเดลจริงของเครื่องเจ้าของ. ข้อจำกัด: โมเดลที่โหลดก่อนมีระบบนี้และชื่อไฟล์ไม่ตรงชื่อตัวละคร (เช่น `model.pth` ของ Hatsune Miku/Vegeta) จะไม่ขึ้นว่าโหลดแล้ว
- **เวอร์ชัน 3.82:** `package.json`, `updater.py`, `copy_dist_assets.py` x2, `src/index.html` (`?v=` x6 + `BUNDLE_VERSION`); `publish_release_v382.py` สร้างจาก v381 (เปลี่ยน changelog/commit message เท่านั้น)

## 🚀 RELEASED v3.81 (ปล่อยอัปเดตเรียบร้อย)
**แก้ไขระบบเฝ้าระวังหน้าต่างโปรแกรมค้าง (Watchdog UI Heartbeat) ให้ทำงานจริง**
- **ปัญหาเดิม (ตั้งแต่ v3.76):** route `/api/ui/heartbeat` ถูกใส่ไว้ในบล็อก `if path.startswith('/api/rvc/')` ของ `QuietHandler.do_GET` ใน `launch_dev.py` ทำให้เซิร์ฟเวอร์ปัดตกคำขอส่งสัญญาณชีพจากหน้าต่าง UI และ Watchdog เฝ้าระวังหน้าจอค้างไม่เคยเริ่มทำงานจริง (ใน `data/ui_health.log` จึงไม่พบบันทึก `ok: page heap`)
- **การแก้ไขใน v3.81:**
  1. ย้าย route `/api/ui/heartbeat` ออกมาอยู่ก่อนบล็อก `/api/rvc/` ใน `launch_dev.py` ส่งผลให้เซิร์ฟเวอร์รับสัญญาณชีพจาก UI ได้อย่างถูกต้องสมบูรณ์
  2. ปรับปรุงเวอร์ชันเป็น 3.81 ใน `package.json`, `updater.py`, `copy_dist_assets.py`, `src/index.html` (`?v=3.81` และ `BUNDLE_VERSION`)
  3. ปล่อยแพตช์ผ่าน `publish_release_v381.py` ขึ้นทั้ง GitHub Release v3.81 และ Hugging Face เรียบร้อย
- **ผลการทดสอบ (Verification):**
  - Vite build & `copy_dist_assets.py` ผ่าน 100%
  - Automated Headless Browser Smoke Test Gate (`smoke_test_gate.py`) ผ่าน 100% (ตรวจ interactive 10 Tool Windows, 0 runtime crashes)
  - Strict Post-Pack SHA-256 Gate ผ่าน 100% ตรงกันทั้ง `patch-v3.81-lite.zip` และ `patch-v3.81-full.zip`
  - เผยแพร่ Dual-Mirror GitHub และ Hugging Face สมบูรณ์, Purge jsDelivr ผ่าน 100%
- **ยืนยันบนเครื่องจริง (Claude, 2026-11-23):** หลังติดตั้ง v3.81 `data/ui_health.log` มี `ok: page heap 5 MB, heartbeats 2` เป็นครั้งแรก → route รับ heartbeat ทำงาน watchdog เริ่มเฝ้าแล้ว. **ยังไม่ยืนยัน:** บรรทัด `ok:` ถัดไปทุก 5 นาที (log หยุดหลังบรรทัดแรก น่าจะปิดแอป), การเปิดทิ้งหลายชั่วโมงโดยไม่มี `UI watchdog:`, และการกู้หน้าต่างที่ค้างจริง (ยังไม่เคยทำงาน ทดสอบแค่ mock). ยังไม่รู้สาเหตุจริงของอาการค้าง/หน้าเทา — ถ้าผู้ใช้ยังเจอ ให้ขอ `ui_health.log` และลองตัวเลือก `disable_gpu` ใน `data/power_settings.json`

## 🚀 RELEASED v3.80 (ปล่อยอัปเดตเรียบร้อย)
**แก้ไขถาวรปัญหาหน้าตาโปรแกรมเพี้ยน (Zero Unstyled UI / Missing CSS / Browser Cache Lockup)**
- **ปัญหา:** ผู้ใช้บางรายหลังกดอัปเดตพบปัญหาหน้าตาโปรแกรมเพี้ยน ไม่มี CSS สไตล์ ตัวอักษรตกไปกองรวมกันทางซ้าย (Unstyled Raw HTML) ซึ่งเดิมต้องบอกให้ผู้ใช้กด `Ctrl + F5` ด้วยตนเอง
- **สาเหตุที่แท้จริง (Root Cause):**
  1. ไฟล์ตกแต่ง CSS และ Companion JS ใน `index.html` เป็นชื่อไฟล์แบบคงที่ ไม่มีเวอร์ชันกำกับ ทำให้ Chromium ดึงข้อมูลแคชเก่า/เสียหายจากหน่วยความจำมาแสดงผล
  2. เซิร์ฟเวอร์ภายในเครื่อง (`QuietHandler.do_GET` ใน `launch_dev.py`) ตอบกลับรหัส `304 Not Modified` เมื่อเบราว์เซอร์ส่ง `If-Modified-Since` ทำให้เบราว์เซอร์ล็อกติดกับแคชเดิม
  3. สคริปต์อัปเดต (`bp3_finish_update.bat`) สั่งรอปิดเฉพาะแบ็กเอนด์ Python แต่ไม่ได้ปิดหน้าต่าง Chromium/Edge ของโปรแกรม ทำให้คำสั่งลบแคชล้มเหลวด้วย Permission Error (Access is denied) เนื่องจากไฟล์แคชยังถูกเปิดค้างอยู่
  4. ไฟล์ `layout_migration.py` ตกหล่นจาก `CORE_FILES` ของแพ็กเกจ Patch
- **การแก้ไขใน v3.80:**
  1. **4-Layer Asset Cache Busting (`copy_dist_assets.py` & `src/index.html`)**: เติมพารามิเตอร์ `?v=3.80` ให้กับไฟล์ CSS (`styles.css`, `ui_readability.css`, `modal.css`, `widget_customizer.css`, `composer_studio.css`, `composer_widget_themes.css`) และ companion JS ทั้งหมดโดยอัตโนมัติในขั้นตอน build
  2. **Auto Sync BUNDLE_VERSION (`copy_dist_assets.py`)**: ซิงค์ `const BUNDLE_VERSION = "{pkg_ver}";` ใน `dist/index.html` ให้ตรงกับ `package.json` อัตโนมัติ ป้องกันปัญหาเวอร์ชัน mismatch
  3. **Zero 304 / Always Fresh 200 OK (`launch_dev.py`)**: ใน `QuietHandler.do_GET` ส่งไฟล์หน้าบ้าน (CSS, JS, HTML, Assets) ด้วยสถานะ `200 OK` เสมอ พร้อมส่ง Header `Cache-Control: no-store, no-cache, must-revalidate` ตัดวงจรแคชค้าง 100%
  4. **Clean Process & Browser Termination (`power_guard.py` & `updater.py`)**: เพิ่มฟังก์ชัน `terminate_browser()` และคำสั่ง `taskkill` หน้าต่างเบราว์เซอร์ของโปรแกรมก่อนเริ่มขั้นตอนลงแพตช์และลบแคช เพื่อให้ล้างไดเรกทอรีแคช (`Default\Cache`, `Default\Code Cache`, `Default\GPUCache`, `Default\DawnCache`, `ShaderCache`, `GrShaderCache`) ได้สะอาดหมดจด 100%
  5. **เพิ่ม `layout_migration.py` ใน `CORE_FILES`**: ป้องกันปัญหา `ModuleNotFoundError: No module named 'layout_migration'` ในรุ่น Full
- **ผลการทดสอบ (Verification):**
  - Vite build & `copy_dist_assets.py` ผ่าน 100%
  - Automated Headless Browser Smoke Test Gate (`smoke_test_gate.py`) ผ่าน 100% (ตรวจ interactive 10 Tool Windows, 0 runtime errors)
  - Strict Post-Pack SHA-256 Gate ผ่าน 100% ตรงกันทั้ง `patch-v3.80-lite.zip` และ `patch-v3.80-full.zip`
  - GitHub Release, Hugging Face Mirror, และ Purge jsDelivr สำเร็จสมบูรณ์

## 🚀 RELEASED v3.79 (ปล่อยอัปเดตเรียบร้อย)
**ปรับปรุงการแสดงผลปุ่มอัปเดตบน Server Rail (#btnRailUpdate)**
- **ปัญหา:** เมื่อดาวน์โหลดไฟล์อัปเดตเสร็จสิ้น (100% หรือพร้อมติดตั้ง) มีเส้นขอบของแถบดาวน์โหลด SVG ซ้อนทับกับเส้นขอบปุ่ม CSS เกิดเป็นเส้นกรอบเบิ้ลสองชั้น (Double Border Overlap) และแสงเรืองซ้อนทับดูไม่สวยงาม
- **การแก้ไขใน v3.79:**
  1. `src/styles.css` & `src/user_controls.js`: ปิดการแสดงผลวงกรอบ SVG อัตโนมัติเมื่อดาวน์โหลดเสร็จสิ้น เหลือเพียงกรอบปุ่มสีเขียวมนเดี่ยวที่คมชัดและสบายตาสไตล์ Discord Server Rail
  2. ลบเงา Inset ด้านในตัวปุ่มที่ทำให้เกิดภาพลวงตาเป็นขอบเบิ้ล และปรับแสง Outer Glow ให้สมูทสวยงาม

## 🚀 RELEASED v3.78 (ปล่อยอัปเดตเรียบร้อย)
**ระบบ Auto Cache-Buster & Self-Healing อัตโนมัติ (แก้ปัญหาแคชค้างหลังอัปเดต)**
- **ปัญหา:** ผู้ใช้บางรายหลังกดอัปเดตพบปัญหาตั้งค่าไม่ได้, ไม่เชื่อมต่อกับช่อง, ไม่จำการตั้งค่า, แชทไม่เข้า, ไม่อ่านเสียง แต่เมื่อกด `Ctrl + F5` จะหายเป็นปกติทันที เกิดจากเบราว์เซอร์เปิดไฟล์หน้าเว็บเก่าจากแคชเครื่อง
- **การแก้ไขใน v3.78:**
  1. **Frontend Auto Cache-Buster (`src/index.html`)**: ฝัง `BUNDLE_VERSION` เช็คกับ `/api/version` หากพบว่าหน้าเว็บที่กำลังรันเป็นเวอร์ชันเก่ากว่าเซิร์ฟเวอร์ จะสั่ง `window.location.replace` ล้างแคชตัวเองทันทีใน 0.1 วินาที โดยผู้ใช้ไม่ต้องกด Ctrl+F5 เอง
  2. **Backend No-Cache Delivery (`launch_dev.py`)**: ปรับ `QuietHandler.do_GET` สำหรับ `/` และ `/index.html` ให้ส่งรหัส 200 พร้อม `Cache-Control: no-store, no-cache, must-revalidate, max-age=0` และไม่ส่ง 304 Not Modified
  3. **Wipe V8 Code Cache (`updater.py`)**: ล้างไดเรกทอรี `Default/GPUCache` และ `Default/DawnCache` ใน `updater.py` ตอนแตกไฟล์แพตช์

## 🚀 RELEASED v3.77 (ปล่อยอัปเดตเรียบร้อย)
**แก้ปัญหาหน้าเทาล้วน (Grey Screen) & GPU Crash Limit & Sleeping Tabs หลังเปิดทิ้งไว้นาน**
**รัน `release.bat` (→ `run_release.py` เลือก `publish_release_v376.py` อัตโนมัติ) แล้วทดสอบบน Windows จริง**
- **ปัญหา:** ผู้ใช้ (รุ่น LITE) แจ้งว่าเปิดนาน ~2 ชม. โปรแกรมค้าง/หายเอง หรือหน้ากลายเป็นสีเทากดไม่ได้. ยังไม่ทราบสาเหตุจริง (สงสัย GPU acceleration / ระบบประหยัดพลังงาน) — แพตช์นี้เป็นการป้องกัน + เก็บข้อมูล
- **แก้:** ไฟล์ใหม่ `power_guard.py` (กัน Windows sleep, ปิด Efficiency mode, watchdog รีสตาร์ตหน้าต่างเมื่อไม่มี heartbeat >180 วิ ขณะ browser ยังอยู่, เขียน `data/ui_health.log`), endpoint `/api/ui/heartbeat`, สคริปต์ heartbeat + Web Lock ใน index.html, รวม `--disable-features=` ที่ซ้ำกันใน `launch_dev.py` เหลือชุดเดียว. ปิดฟีเจอร์ได้ด้วย `data/power_settings.json`
- **ยังไม่ได้ทดสอบ:** Win32 API จริง, การจับ process ของ Chrome/Edge ผ่าน `--user-data-dir`, `--start-minimized`, ชื่อ feature `HighEfficiencyModeAvailable,BatterySaverModeAvailable` (เดา; ถ้าไม่มีชื่อนี้ Chromium จะข้าม). ทดสอบเฉพาะ logic ของ watchdog แบบ mock ในคลาวด์
- **ตรวจหลังอัปเดต:** `data/ui_health.log` มีบรรทัด `power_guard started` และ `ok: page heap ...` ทุก 5 นาที; เปิดทิ้งหลายชั่วโมง; ถ้ายังเกิดให้ผู้ใช้ส่ง `ui_health.log`
- หมายเหตุ: `run_release.py` ซิงค์ไฟล์ลงเครื่องเจ้าของหลัง release จึงไม่ใช่การทดสอบตัวอัปเดตที่สะอาด

## 🚀 RELEASED v3.75 (ปล่อยอัปเดตเรียบร้อย)
**ผู้ทำ release รัน `release.bat` (เรียก `publish_release_v375.py`) แล้วทดสอบอัปเดตบนเครื่องจริง**
- **สาเหตุจริงของ RVC เสียงไม่ทำงานบน production (จาก `rvc_debug.log` ของ v3.74):** `Failed to import 'package_numba_cache.FrozenDataCacheLocator'` → numba/librosa โหลดไม่ได้ → ทุกการแปลงเสียงล้มและถูกกลืนเป็นเสียง Edge ปกติ. ไฟล์ `package_numba_cache.py` มีใน dev แต่ไม่มีในโฟลเดอร์ production (exe ตั้ง env `NUMBA_CACHE_LOCATOR_CLASSES` ให้ FULL). ยังอธิบายไม่ได้ว่าทำไมรุ่นก่อนหน้าเคยใช้ได้
- **แก้:** เพิ่ม `package_numba_cache.py` ใน CORE_FILES ของ `publish_release_v375.py` (ลง `_internal/` ด้วย) + `launch_dev.py` ลบ env ดังกล่าวถ้าหาโมดูลไม่เจอ (ใช้ locator ปกติของ numba) + ไม่แคชเสียงที่ RVC แปลงล้มเหลวเป็นผลลัพธ์ RVC
- **ลบ Wayu TTS ทั้งระบบ (ผู้ใช้สั่ง):** เหลือ Edge-TTS + RVC. แก้ `src/index.html`, `src/styles.css`, `tts_service.py`, `launch_dev.py` (ดูรายละเอียดใน WORKLOG). สวิตช์ลับ 20 คลิกที่จุดเขียวคุมเฉพาะ Giveaway. สำรองไฟล์เดิมไว้ที่ `_to_delete/*.pre_nowayu`
- **เทสต์:** syntax ทั้ง py และ inline JS, Playwright โหลดหน้าด้วย API จำลอง — ยังไม่ได้รันแอปจริง
- **ตรวจหลังอัปเดต:** อ่านแชท 1 ข้อความตอนเปิด RVC ต้องเป็นเสียง RVC; `data/rvc_debug.log` ไม่มี "convert failed" ใหม่; หน้า Setting > TTS ไม่มีปุ่มเลือกโมเดล

## 🚀 RELEASED v3.74 (ปล่อยอัปเดตเรียบร้อย)
**ผู้ทำ release รัน `release.bat` (เรียก `publish_release_v374.py`)**
- v3.73 ปล่อยแล้วและตรวจบนเครื่องจริงว่าไฟล์ `_internal/*.py` ตรงกับไฟล์หลักครบ แต่ RVC บน production ยังไม่กลับ (dev ปกติ)
- หลักฐาน: `/api/rvc/status` หลังเปิดเอง = `ready`, `loaded: true`, `cuda:0` (โหลดโมเดลได้) แต่เสียงอ่านแชทไม่ใช่ RVC; ตอนเปิดแอปใหม่สถานะเป็น `idle`/progress 0 (ยังไม่ชัดว่า autoload ทำงานไหม)
- สมมติฐาน (ยังไม่ยืนยัน): `rvc_service.convert()` ล้มใน production แล้ว `launch_dev` กลืน error (fallback เป็นเสียง Edge) และ warmup ตอนโหลดก็กลืน error ระดับ debug; แอปไม่มี logging config จึงมองไม่เห็น
- v3.74 แก้เฉพาะ `rvc_service.py`: เขียน `rvc_debug.log` ใน data dir (init/restore, load/warmup/convert ล้มพร้อม traceback, "convert skipped" 5 ครั้งแรก) และ `status()` ส่ง `last_convert_error`; พฤติกรรมการแปลงเสียงไม่เปลี่ยน
- หลังอัปเดตให้อ่าน `data/rvc_debug.log` + `/api/rvc/status` เพื่อหาสาเหตุจริง แล้วแก้ใน v3.75
- เทสต์: mock ในคลาวด์เท่านั้น (logging + status) ยังไม่ได้รันแอปจริง

## 🚀 RELEASED v3.73 (ปล่อยอัปเดตเรียบร้อย)
**ผู้ทำ release ต้องรัน `release.bat` (เรียก `publish_release_v373.py`) แล้วทดสอบอัปเดตเครื่องจริง**
- **อาการ:** ฉบับติดตั้งจริง (production) RVC/TTS หลุดเป็นเสียงสำรองตั้งแต่ v3.71 ส่วน dev ปกติ; v3.72 ไม่หาย
- **สาเหตุ (จากการเทียบไฟล์ในเครื่อง production แบบอ่านอย่างเดียว):** `full/_internal/` มีสำเนา `.py` รุ่นเก่าค้าง (`tts_service`, `dictionary_manager`, `chat_bridge`, `chat_tiktok`, `plugin_manager`) และ `package_entry.py` ใส่ `_internal` ไว้หน้าสุดของ `sys.path` จึงบังไฟล์ที่แพตช์ลงโฟลเดอร์หลัก. `launch_dev.py` (3.71+) เรียก `tts_service.generate_audio_bytes(..., model=, voice=)` ซึ่งสำเนาเก่าไม่รองรับ → TypeError → เสียงสำรอง. ไฟล์ใน `full/` ตรงกับ dev ครบ (แพตช์ลงครบ) — ยังไม่ได้รันแอปจริง จึงเป็นข้อสรุปจากการเทียบไฟล์
- **การแก้:** (1) บล็อกบนสุดของ `launch_dev.py` ย้ายโฟลเดอร์ exe ขึ้นหน้า `_internal` เมื่อ frozen (2) `publish_release_v373.py` เขียน `.py` ใน CORE_FILES ลงทั้ง root และ `_internal/` ในแพตช์เพื่อทับสำเนาเก่า (3) เลขเวอร์ชัน 3.73 ใน package.json, updater.py, release.bat, src/index.html (`version.json` สคริปต์สร้างเอง)
- **ข้อควรระวัง:** ตัวบูต `package_entry.py` ถูกคอมไพล์ในตัว exe การแก้ไฟล์บนดิสก์ไม่มีผล — ห้ามพึ่งการแก้ไฟล์นั้น
- **ตรวจหลังอัปเดต:** md5 ของ `full/_internal/tts_service.py` ต้องตรงกับ `full/tts_service.py`; ลองใช้ RVC; ถ้ายังไม่หายให้ดู log ต่อ
- **เทสต์ที่ทำ:** เฉพาะ syntax และจำลองลำดับ sys.path ในคลาวด์เท่านั้น

## 🚀 RELEASED v3.71 (ปล่อยอัปเดตเรียบร้อย)

- ปรับปรุง Setting > TTS และหน้าต่างตั้งค่าเสียงให้กภทัดรัดขื้น, ปุ่มทดลองฟังตาม Speed/Pitch/Volume, Offline Thai TTS ซ่อนหลังจุดเขียว 20 คลิก, Chatbot presets, แก้ Danmaku full screen zone, สลับลำดับคอลัมน์บล็อก TTS -> Overlay -> Replie

## ⚡ ACTIVE DEVELOPMENT (กำลังพัฒนา / รอดำเนินการต่อ)

### 1. 🇹🇭 Wayu-Paxa-TTS-Edge (Offline Thai TTS Engine & 12 Voices Roster)
- **วัตถุประสงค์**: แก้ปัญหา Microsoft Edge-TTS เชื่อมต่อไม่ได้ หรือสำหรับผู้ใช้ที่ต้องการระบบเสียงอ่านภาษาไทยแบบ Offline 100% ในเครื่อง ไม่ต้องต่อเน็ต
- **เทคโนโลยี & โมเดล**:
  - ใช้โมเดล open-weights `wayu-ai/wayu-paxa-tts-edge` (82M parameters, Kokoro/StyleTTS architecture) บน CPU
  - แพ็กเกจที่ติดตั้ง: `wayu-tts-inference` (ปรับแต่งความเข้ากันได้กับ numpy 2 / scikit-learn เรียบร้อย)
  - น้ำหนักโมเดลแคชอยู่ที่ `C:\Users\Meng-PC\.cache\huggingface\hub\models--wayu-ai--wayu-paxa-tts-edge`
- **การเปลี่ยนแปลงในระบบ**:
  1. `tts_service.py`:
     - เพิ่ม `get_wayu_tts()` พร้อม Thread Lock แบบ lazy load ไม่หน่วงตอนเริ่มโปรแกรม
     - เพิ่ม `synthesize_wayu(text, gender, rate, voice)` สังเคราะห์เสียง 24kHz WAV พร้อมแปลงความเร็วเสียง
     - ขยาย `generate_audio_bytes` ให้รับพารามิเตอร์ `model` ('azure' / 'wayu') และ `voice` (ชื่อเสียงย่อย)
  2. `launch_dev.py`:
     - เอนด์พอยต์ `/api/tts` รับพารามิเตอร์ `model` และ `voice`
     - แคชคีย์ `_TTS_AUDIO_CACHE` เพิ่ม `model` และ `voice` ป้องกันการชนกันของเสียง
     - ตรวจสอบ MIME type ถ้าหัวไฟล์เป็น `RIFF` จะส่งกลับเป็น `audio/wav` ถูกต้อง
  3. `rvc_service.py`:
     - รองรับการรับเข้าไฟล์เสียง WAV จาก Wayu และส่งต่อไปแปลงเสียง AI RVC ได้ทันที 100% (ทดสอบแล้ว)
  4. `src/index.html`:
     - เพิ่มการ์ดเลือกโมเดลเสียง **"🤖 โมเดลเสียงสังเคราะห์ (TTS Engine)"** เหนือช่องเลือกเพศ ทั้งใน Settings (`#sec-tts`) และ Voice Tool Window:
       - `🌐 Azure (ตัวปัจจุบัน)`
       - `⚡ Wayu (Offline ในเครื่อง)`
     - ปุ่มเพศ **"👩 หญิง"** และ **"👨 ชาย"** ยังคงใช้งานได้สมบูรณ์ทั้งสองโมเดล
     - เพิ่มกล่องตัวเลือก **"🎙️ โทนเสียงโมเดล Wayu"** พร้อมปุ่ม **"🔊 ทดลองฟังเสียงนี้"** ที่จะแสดงเฉพาะเมื่อเลือก Wayu รองรับทั้ง 12 เสียง:
       - **หญิง (8 เสียง)**: `f_young_clear`, `f_young_bright`, `f_young_warm`, `f_teen_bright`, `f_mid_clear`, `f_mid_warm`, `f_elderly_low`, `f_elderly_soft`
       - **ชาย (4 เสียง)**: `m_young_clear`, `m_teen_bright`, `m_mid_warm`, `m_elderly_deep`
     - ซิงค์พารามิเตอร์ `&model=` และ `&voice=` ในทุกจุดเรียก `/api/tts`

- **เพิ่ม (Claude Cowork, 2026-11-12):** dropdown โทนเสียง Wayu แสดงเฉพาะเพศที่เลือก (แก้ใน `updateWayuContainers()` ใน `src/index.html`; ทดสอบ harness cloud เท่านั้น) backup `_to_delete/index.html.pre_wayugender`

- **เพิ่ม (Claude Cowork, 2026-11-12):** ปุ่มโมเดลเป็น `Azure (Online)`/`Wayu (Offline)`, ชื่อเสียง Wayu ไม่มีรหัสนำหน้า, หน้าต่าง `#win-voice-settings` กระชับขึ้น (รวมการ์ดโมเดล+เพศ; CSS ท้าย `styles.css`) — ดู WORKLOG บนสุด; ทดสอบ harness cloud เท่านั้น

### 2. 🚫 Blacklist System Verification & UI Reordering
- **ตรวจสอบการทำงาน**:
  - TTS (`rule.tts`), Overlay (`rule.overlay`), Replie (`rule.replie`) ใช้งานได้จริง 100%
  - บล็อกทั้งหมด (`rule.all`): ดักทิ้งตั้งแต่ `injectIncomingChat` ไม่แสดงในแชทสดเลยเด็ดขาด
- **สลับลำดับคอลัมน์/ช่องเลือก**:
  - สลับเป็น **`TTS` -> `Overlay` -> `Replie`** ครบ 3 จุด:
    1. ตารางตั้งค่าบล็อกคนดู (`#blockedViewerList`) ใน `src/index.html` และ `src/user_controls.js`
    2. หน้าต่างป๊อปอัปบล็อกด่วนในแชทสด (`#modal-block-user`)
    3. หน้าต่างข้อมูลคนดู (`paneProfTab4` ใน User Profile)

---

## 🧩 PLUGIN API v1 (เฟส 1) — บันทึกการทำงาน (ปล่อยแล้วใน v3.62)

เพิ่มระบบ plugin แบบ JavaScript ล้วน (widget + รับ event อ่านอย่างเดียว) แบบ additive ไม่แตะ logic เดิม:
1. `plugin_manager.py`: ต่อท้ายไฟล์ ส่วน "Plugin API v1 (HTTP part)" (`handle_http`) — ไฟล์นี้อยู่ใน release file list เดิมอยู่แล้ว **ไม่มีไฟล์ใหม่ที่ต้องเพิ่มใน copy_dist_assets.py**
2. `launch_dev.py`: เพิ่ม hook 17 บรรทัดต้น `do_GET` และ `do_POST` (บล็อก `plugin system hook` ครอบ try/except — ถ้า error จะตกไป handler เดิม) ทำงานเฉพาะ path `/plugins*` และ `/api/plugins*`
3. หน้า UI: `http://127.0.0.1:<port>/plugins` (หน้าเปิด/ปิด) และ `/plugins/host/<id>` (ลิงก์ OBS Browser Source) — เป็น HTML ฝังใน plugin_manager.py ไม่มีไฟล์ใหม่ (ตอนนี้เข้าได้จาก ตั้งค่า > เกี่ยวกับระบบ > ปลั๊กอิน ดูข้อ 9)
4. Plugin อยู่ใน `<DATA_ROOT>/plugins/<id>/` (plugin.json ต้องมี `api_version: 1`, `widget`, `permissions` จาก events_read/chat_read) รันใน iframe sandbox (ไม่มี allow-same-origin) + CSP `connect-src 'none'` สถานะเปิด/ปิดเก็บใน `plugins/_state.json` ไม่ใช่ใน manifest
5. ทดสอบ: Playwright บน harness cloud เท่านั้น (20 เคส: สิทธิ์, sandbox, CSP, path traversal, CSRF, auto-disable, safe mode) **ยังไม่ได้ทดสอบบนโปรแกรมจริง/Windows/OBS และไม่ได้ build**
6. ก่อน release ให้ตรวจ: เปิดโปรแกรมตามปกติแล้วทุกปุ่มเดิมต้องทำงาน (hook ต้องไม่กระทบ), เปิด `/plugins` ได้, ตัวอย่างใน `docs/plugin_examples/hello-widget`
7. ยังไม่ทำ (เฟสถัดไป): การเรียก API ภายนอกผ่าน proxy, ตัวตรวจความสมบูรณ์ของ credit/ปุ่มสนับสนุน, golden fixtures ของ event
8. เพิ่ม plugin ตัวอย่าง `demo-cursor` (เมาส์พิเศษ) ฝังอยู่ใน plugin_manager.py — สร้างให้ครั้งแรกใน `<DATA_ROOT>/plugins/demo-cursor/` และ**ปิดไว้เป็นค่าเริ่มต้น** (ถ้าผู้ใช้ลบจะไม่สร้างซ้ำ จำไว้ใน `_state.json`). ขยาย API: manifest ใส่ `cursor` (PNG ≤64x64, ≤32KB) + สิทธิ์ `ui_cursor` ได้, เซิร์ฟเวอร์ตรวจไฟล์แล้วส่ง CSS ผ่าน `GET /api/plugins/ui`. **แก้ `src/index.html` 1 จุด:** `<script>` สั้นๆ ก่อน `</body>` (ครอบ try/catch) ดึง `/api/plugins/ui` แล้วใส่ `<style id="bp3-plugin-cursor">` ถ้ามี plugin เปิดอยู่ — ถ้าไม่มีหรือ error จะไม่ทำอะไร. Backup: `_to_delete/index.html.pre_plugin_cursor`, `_to_delete/plugin_manager.py.pre_demo`. ยังไม่ได้ลองรูปเมาส์ในหน้าต่างโปรแกรมจริง (Chrome app-mode) ทดสอบแค่ computed style ใน harness
9. **หน้า plugin ย้ายเข้า Settings แล้ว:** ตั้งค่า > เกี่ยวกับระบบ > "ปลั๊กอิน (Plugins)" เหนือ Windows Defender (nav `nav-sec-plugins`, pane `sec-plugins`, สคริปต์ `BP3PluginsPane` ก่อน `</body>` ใน `src/index.html`; ใช้คลาสเดิม section-card/cwc-switch/btn-topbar-action). เรียก `/api/plugins*` เดิม. Backup `_to_delete/index.html.pre_plugin_pane`. ทดสอบเฉพาะ harness cloud (Playwright บนสำเนา index.html) ไม่ได้ลองในโปรแกรมจริง. หน้า `/plugins` แบบแยกยังอยู่ใช้ได้
10. **คู่มือสร้าง plugin สำหรับให้ AI อ่าน:** ไฟล์ `docs/PLUGIN_GUIDE_FOR_AI.md` (ต้นฉบับ) ฝังสำเนาไว้ใน `plugin_manager.py` เป็น `PLUGIN_GUIDE_MD` เสิร์ฟที่ `GET /plugins/docs` (`?download=1` = ดาวน์โหลด) — ไม่มีไฟล์ใหม่ใน dist. หน้า ตั้งค่า > ปลั๊กอิน มีปุ่ม อ่าน/คัดลอก/ดาวน์โหลดคู่มือ (ล่างซ้ายของหน้า). **ถ้าแก้คู่มือ ต้องฝังสำเนาใหม่ใน plugin_manager.py ให้ตรงกัน** (สคริปต์ `_to_delete/plg_doc_patch.py` เป็นตัวอย่างวิธีฝัง). Backup `_to_delete/index.html.pre_plugin_doc`, `_to_delete/plugin_manager.py.pre_doc`. ทดสอบเฉพาะ harness cloud
11. **เมาส์พิเศษเห็นผลทันที (ไม่ต้องรีสตาร์ต):** สคริปต์เมาส์ใน `src/index.html` ตอนนี้ดึง `/api/plugins/ui` ซ้ำเมื่อ (ก) กดเปิด/ปิด plugin หรือ Safe Mode ในหน้าตั้งค่า (ส่งสัญญาณผ่าน BroadcastChannel `bp3_plugin_ui` ไปทุกหน้าต่างของโปรแกรม รวมหน้าต่างหลักตอนตั้งค่าเปิดเป็น popout) และ (ข) ตอนหน้าต่างได้โฟกัส. ปิด plugin = ลบ `<style id=bp3-plugin-cursor>` ทันที. Backup `_to_delete/index.html.pre_plugin_live`. ทดสอบ harness cloud เท่านั้น

---

- **Key Enhancements & Architectural Milestones (v3.31 - v3.70)**:
  0. **Comprehensive URL Detection & TTS "แนบลิงก์" Replacement (v3.70)**:
     - Automatically intercepts all URL / web link patterns (`http://`, `https://`, `www.`, and shortlinks such as `youtu.be`, `vt.tiktok.com`, `bit.ly`, etc.) in chat messages, pronouncing them cleanly as `"แนบลิงก์"` via TTS speech.
     - Preserves full URL rendering in UI chat rows while shortening speech input, preventing character limit skips and eliminating tedious character-by-character URL spelling.
     - Fully synchronized across frontend speech preparation (`getSpeakableChatText`), backend pronunciation manager (`dictionary_manager.py`), and default dictionary (`replace_words.json`).
     - Automated test coverage extended to 12 passing test cases in `tests/verify_event_chat_and_tts.py`.
  0. **TikTok/Multi-Platform Event & TTS Optimization (v3.69)**:
     - **TTS Message-Only Filtering**: `playChatMessageSpeech` now exclusively queues speakable text for genuine chat messages (`!msg.event || msg.event === 'message'`), completely eliminating TTS audio flooding from TikTok likes, joins, gifts, or follows. The sender name reading setting (`chkReadAuthorName`) applies uniformly across all platforms.
     - **Inline Compact Gray Activity Stream**: Interactive events (YouTube like, TikTok heart/like, follow, sub/resub, member, donate, superchat, gift, share, bits) now render directly inside `#chatList` as compact gray inline rows (`.chat-event-item`, `11px`, `#94a3b8`) formatted as `{user} {action}` (e.g. `Somchai กดหัวใจ ×15`, `Somchai กดถูกใจไลฟ์`, `Somchai กดติดตาม`, `Somchai ส่ง Super Chat ฿500`) chronologically with live chat, without TTS and without TTS badges.
     - **Events List Synchronization & Performance**: Events are concurrently mirrored into the `#eventsList` panel on the right without audio. Heart count displays as `×N` instead of `฿N`. Added debouncing for `localStorage` persistence of `bp3_live_activity_events` to ensure 60fps smoothness during high-frequency TikTok like bursts.
     - **Complete Join Suppression**: `join` events are completely suppressed across `chat_tiktok.py`, `chat_bridge.py`, and `src/index.html`. Zero messages, zero event entries, and zero TTS triggers are generated when viewers enter the live stream.
     - **Automated Verification**: Fully validated via `tests/verify_event_chat_and_tts.py` (10/10 automated assertions passing) and `smoke_test_gate.py`.
  0. **Lucide Icons Overhaul, Chat Widget Customizer Hide, Sticky Chat Preview & UI Polish (v3.68)**:
     - Hidden unused Chat Widget Customizer card in Chat Setting via non-destructive CSS `display: none`.
     - Replaced emojis with Lucide SVG Icons across Rail (Composer, Replie, ASK, Randomizer, User Manager, Settings), settings navigation (17 categories), section titles, live chat header controls, topbar actions, and footer Discord link.
     - Merged voice gender buttons into a single toggle (`#tbGenderToggle`) with `venus`/`mars` icons.
     - Made Chat Settings live chat preview card `position: sticky`.
     - Blocked users in User Manager now display a red `user-round-x` Lucide badge.
     - Live viewers counter now features `eye` / `eye-closed` icons.
     - Multi-window accent color & theme synchronization with live `storage` listener in main window.
     - Repackaged and distributed with all 27 TikTokLive bundled dependencies in `_internal/`.
  0. **TikTok LIVE 7.0.1+ Bundled Dependencies & Titlebar/Updater Version Sync (v3.66)**:
     - Bundled all 27 runtime packages (`TikTokLive`, `TikTokLiveProto`, `EulerApiSdk`, `betterproto2`, `httpx`, `pydantic`, `websockets_proxy`, etc.) into `_internal/` of the patch distribution archive, allowing standalone `.exe` installations to run TikTok LIVE chat without needing Python or `pip install`.
     - Synced bundled packages into `build_trials/lite` and `build_trials/full` `_internal/` directories.
     - Added auto-loader `_tt_base_dirs` in `chat_tiktok.py` dynamically injecting `_internal` and application directory to `sys.path`.
     - Completely synchronized version numbering across `updater.py` (`CURRENT_VERSION`), window title & header tag in `src/index.html`, `package.json`, and `version.json` to `v3.66`.
  0. **TikTok LIVE Chat Ingestion Stability & TikTokLive 7.0.1 Upgrade (v3.65)**:
     - Resolved "Connected but no chat messages retrieved" issue caused by TikTok Webcast sign server routing through EulerStream fallback proxy (`ws-fallback.eulerstream.com`).
     - Upgraded environment to `TikTokLive==7.0.1` fixing raw unencoded User-Agent route params in WebSocket URI builder (HTTP 400 rejection).
     - Adjusted `chat_tiktok.py` to use `fetch_room_info=False` to prevent `AgeRestrictedError` on 18+ mature broadcasts, relying on continuous `RoomUserSeqEvent` pushes for viewer count.
     - Added runtime version warning in `chat_tiktok.py` alerting users if their environment runs outdated `<7.0.1` packages.
  0. **TTS Audio Preferences Persistence & Multi-Window Sync (v3.64)**:
     - Fixed issue where TTS voice volume, speech rate, pitch (Full build), mixed voice toggle, character limits, limit alert settings, and voice test messages reset to defaults on app restart.
     - Added `restoreTtsAudioPrefs()`, `initTtsTestMessagePersist()`, and a cross-window `storage` listener in `src/index.html` ensuring settings modified in popout Settings windows synchronize seamlessly with the main window.
  0. **Mock Roster Purge & Built-in Demo Plugin (v3.63)**:
     - Automatically purged legacy mock viewers (AlexGamer, KittenLover, etc.) from User Manager roster and localStorage while strictly protecting real viewers with counts > 3.
     - Built-in `demo-cursor` plugin fallback in `plugin_manager.py` without requiring filesystem writes on startup; enhanced error visibility on plugin state persistence failure.
  0. **Plugin System v1 & CPU/RAM Optimizations (v3.62)**:
     - Full Plugin System (JavaScript/iframe sandbox + CSP `connect-src 'none'`) with Settings UI integration (Settings -> Plugins pane), live toggle, Safe Mode, and documentation guide at `/plugins/docs`.
     - CPU/RAM optimizations: Replaced heavy 1254px icons with optimized `bp-icon-64.png` (12KB), switched `updater.py` torch check to non-import spec inspection (`find_spec`), and eliminated duplicate chat poller loop in `initRealChatPoller`.
     - Restored compact view & custom fonts in ASK widget; added popout close guard for User Manager / Author Profile.
  0. **Chat Widget Platform Logo Path Resolution (v3.60, Hotfix)**:
     - Fixed issue where platform icons (Twitch, YouTube, Kick, TikTok, SOOP, MyLive) in Composer Chat Widget & `legacy_chat.html` showed broken images in production builds.
     - Resolved route `/logo/<platform>` in `launch_dev.py` to prioritize `DIST_DIR/assets/<platform>.png` before falling back to `SRC_DIR/assets/`.
  1. **Overlay Locator Redesign & Precision Placement (v3.59)**:
     - Replie / ASK / Randomizer ใช้รูปแบบเดียวกัน: locator 16:9 (พิกัดตรรกะ 1920x1080) ลากวาง/ย่อขยายบนจอตัวอย่าง + ปุ่ม DEMO ที่ขึ้น OBS สด (ปิดอัตโนมัติเมื่อปิดหน้าต่าง)
     - ค้าง Ctrl = ลากอิสระไม่ snap; ลูกศร = 1 พิกเซล; Shift+ลูกศร = 10 พิกเซล; กรอบรับ focus ตอนคลิกเพื่อไม่ให้ลูกศรไปเลื่อน scrollbar
     - Replie: ธีมการ์ด 8 แบบ (`data-theme`), ค่า `pos_x/pos_y/theme` ใน `bp3_replie_settings`; หน้าแก้ไขคำสั่งมีจอตัวอย่างลากได้ แอนิเมชันเข้า/ออก และ "ดูสดบน OBS"
     - Randomizer เหลือวงล้อรูเล็ต + สล็อต; ASK ออกแบบใหม่ (strip compact, 17 bar styles, 11 frame styles, enter/exit animation)
     - หน้าต่างเครื่องมือ popout เปิดที่ 85% ของหน้าต่างหลักแล้วจำขนาด/ตำแหน่ง/จอ; หน้าต่างหลักล็อก min-size ด้วย ClipCursor (`app_window_frame.py` — **ยังไม่ได้ทดสอบบน Windows จริง**)
     - ทดสอบผ่าน Playwright cloud harness เท่านั้น; ต้อง `npm run build` + ทดสอบ dist จริงก่อนปล่อย
  1. **Composer Layer Trash Button & Non-Intrusive Window Interceptor (v3.58)**:
     - Fixed issue where clicking the trash icon in the Composer Studio layer list closed the editor instead of deleting the widget.
     - Changed button class from `.close-red` to `.btn-layer-delete` in `src/composer_studio.js` and `src/composer_studio.css`.
     - Added comprehensive exclusion guards to the popout click capture listener in `src/index.html` ensuring that buttons inside `.composer-layers-container`, `#composerLayersList`, `.composer-sidebar`, `.composer-properties`, tables, forms, and dialog bodies are never intercepted as window-closing actions.
  2. **100% In-App Auto-Update Flow in Settings (v3.58)**:
     - Replaced manual `.zip` download links in Settings -> About with a direct trigger to `showFastUpdateModal()`.
     - Users clicking "ตรวจสอบการอัปเดต" now get a streamlined in-app dialog with live progress bar and a 1-click "OK (รีสตาร์ทเพื่ออัปเดต)" button without ever leaving the application.
  3. **Permanent Topbar Overlay Clean Removal (v3.57)**:
     - Completely excised `#topbar-item-overlay` from DOM and removed `'overlay'` from `_topbarHideableMeta` in `src/index.html`.
     - Guarantees that `applyTopbarHiddenState()` and `localStorage` restoration cannot bring back the redundant topbar button.
  4. **Strict Post-Pack SHA256 Integrity Gate (v3.56)**:
     - Eliminated the "100% download failure" bug caused by post-hash manifest modifications.
     - Release scripts (`publish_release_*.py`) now finalize the `.zip` archive (including `version.json`) *before* computing the SHA-256 hash, backed by strict Python `assert` statements that fail immediately if hashes do not match 100%.
  5. **Dual-Mirror Resilience & Updater Worker Robustness (v3.54 - v3.55)**:
     - Full failover between GitHub Releases and Hugging Face CDN (`men9ch/broadcast-playroom-3`).
     - Fixed `UnboundLocalError: download_url` in `updater.py` background worker with proper scope and mirror list fallback.
     - Fixed integer casting on TTS service timeouts and multi-window settings section synchronization.
  6. **Embedded Patch Installer & Self-Healing Manifest (v3.53)**:
     - Embedded `BP3_PatchInstaller.exe` into the application bundle and patch zip files.
     - Added self-healing in `updater.py`: if `version.json` on disk is older than `CURRENT_VERSION` in code, the local manifest is healed automatically.
  7. **Zero-Cache Architecture (v3.46 - v3.52)**:
     - Injected `--disk-cache-size=1` and `--media-cache-size=1` flags to Chrome/Edge App Mode launcher, completely preventing stale UI cache upon updating.
  8. **Standardized Native Window Frame & Popout Parity (v3.48 - v3.52)**:
     - Standardized native title bar controls (minimize, maximize, close) across all standalone popout windows and tool panels.

## กฎเหล็กการสร้างและปล่อย Patch อัปเดต (Strict Release Invariants)
1. **Dual-Mirror Publishing**: ทุก release ต้องอัปโหลดคู่ขนานทั้ง **GitHub Releases** (`zepiam/broadcast-playroom-3`) และ **HuggingFace Mirror** (`men9ch/broadcast-playroom-3`) เสมอ
2. **Strict SHA-256 Integrity Gate**: ห้ามแก้ไข zip หลังคำนวณ hash; ต้องรัน assertion ตรวจสอบว่า hash ใน `version.json` ตรงกับไฟล์ zip ที่อัปโหลด 100%
3. **Dual-Path Packaging**: แพ็กเกจ patch-v*.zip ทุกตัวต้องมีโครงสร้างไฟล์ทั้ง root (`dist/`) และ `_internal/` เสมอ
4. **Version Manifest Parity**: ใน `version.json` ต้องมีคีย์ `"version"` และ `"latest_version"` คู่กันเสมอ พร้อม changelog ภาษาไทยที่ชัดเจน
5. **Zero GPU Lockup**: โมดอลหรือเอฟเฟกต์แสงต้องไม่มี continuous loop animation หรือ backdrop-filter เต็มจอเด็ดขาด
6. **Permanent Settings Retention**: ห้ามลบหรือเขียนทับไฟล์ config ของผู้ใช้ (`platform_settings.json`, `composer_layout.json`, `rvc_settings.json`, `user_roster.json`) เด็ดขาด



## คู่มือวิเคราะห์และวิธีแก้ไข: ปัญหา "ผู้ใช้งานคลิกปุ่มต่างๆ ไม่ได้ / ปุ่มไม่ตอบสนอง" (Unclickable Buttons Troubleshooting Guide)

จากการวิเคราะห์ประวัติการแก้ไขและพฤติกรรมของระบบใน Broadcast Playroom 3 ปัญหาผู้ใช้งานคลิกปุ่มต่างๆ ไม่ได้ หรือปุ่มไม่ตอบสนอง มักเกิดจาก 5 สาเหตุหลัก ดังนี้:

### 1. การดักจับอีเวนต์ผิดเป้าหมายด้วย Event Capture (`useCapture: true`)
- **สาเหตุที่พบ:** ในระบบหน้าต่างย่อย (Popout Window) เคยมีการใส่ Global Click Listener `document.addEventListener('click', handler, true)` เพื่อคอยดักจับปุ่มปิดหน้าต่าง แต่เช็กเงื่อนไขกว้างเกินไป เช่น ตรวจสอบเพียง `btn.classList.contains('close-red')` หรือ `title="ปิด"` เมื่อผู้ใช้คลิกปุ่มภายในหน้าต่าง (เช่น ปุ่มถังขยะลบวิดเจ็ตใน Composer หรือปุ่มลบแถวในตาราง) ตัว Capture Listener จะชิงดักจับอีเวนต์ก่อน แล้วสั่ง `e.stopPropagation()` / `e.preventDefault()` ทำให้ฟังก์ชันจริงของปุ่มไม่ถูกเรียก หรือกลายเป็นการปิดหน้าต่างแทน
- **แนวทางแก้ไขที่ใช้ได้ผล:**
  1. จำกัดขอบเขตการดักจับเฉพาะปุ่มที่อยู่ใน Header หรือ Title Bar เท่านั้น (`.floating-header`, `.floating-actions-right`, `.desktop-titlebar-controls`)
  2. ใส่ **Exclusion Guard** ป้องกันอย่างเข้มงวด: ข้ามการดักจับทันทีหากปุ่มอยู่ภายในพื้นที่ทำงาน เช่น `.composer-layers-container`, `#composerLayersList`, `table`, `form`, `.modal-body`
  3. ตั้งชื่อคลาสสำหรับปุ่มแอ็กชันทั่วไปให้เฉพาะเจาะจง หลีกเลี่ยงคลาสที่สับสนกับระบบหน้าต่าง (เช่น เปลี่ยนจาก `.close-red` เป็น `.btn-layer-delete`)

### 2. เลเยอร์โปร่งใสหรือ Backdrop บังหน้าจอ (Invisible Overlay with High z-index)
- **สาเหตุที่พบ:** หน้าต่างย่อย (Floating Window), โมดอลเก่า, หรือพื้นที่ลากวาง (Drop Overlay) ที่ถูกซ่อนเพียงแค่ `opacity: 0` หรือมีพื้นหลังโปร่งใส แต่ยังคงอยู่ใน DOM และเปิด `pointer-events: auto` ไว้ พร้อมค่า `z-index` ที่สูงกว่าเลเยอร์ปกติ ทำให้ผู้ใช้มองเห็นปุ่มด้านล่างชัดเจน แต่เมื่อคลิกเมาส์ ตัวคลิกจะถูกเลเยอร์โปร่งใสด้านบนดูดกลืนไปทั้งหมด
- **แนวทางแก้ไขที่ใช้ได้ผล:**
  1. เมื่อองค์ประกอบใดๆ ถูกซ่อน ต้องใส่ทั้ง `display: none !important;` และ `pointer-events: none !important;` เสมอ
  2. กำหนด `pointer-events: auto` เฉพาะเมื่อองค์ประกอบนั้นมีสถานะ Active และกำลังแสดงผลจริงเท่านั้น
  3. ใช้ CSS `contain: strict; isolation: isolate;` เพื่อแยก Layer Stacking Context ไม่ให้เอฟเฟกต์การซ้อนทับรั่วไหล

### 3. แคชของเบราว์เซอร์ค้างข้ามการอัปเดต (Stale Browser Cache Desync)
- **สาเหตุที่พบ:** Chrome หรือ Edge ในโหมด App Mode หรือ WebView2 จดจำไฟล์ `dist/index.html` หรือ `.js` ก้อนเก่าไว้ใน User Data Profile เมื่อโปรแกรมอัปเดตเวอร์ชันใหม่ โครงสร้าง HTML หรือ ID ของปุ่มเปลี่ยนไป แต่สคริปต์ในแคชยังเป็นตัวเดิม ทำให้ `document.getElementById(...)` หา DOM ไม่เจอ เกิดค่า `null` และส่งผลให้ Event Listener ไม่ถูกผูกกับปุ่ม กลายเป็นปุ่มตาย
- **แนวทางแก้ไขที่ใช้ได้ผล:**
  1. บังคับปิดแคชตอนสั่งรันเบราว์เซอร์ด้วยแฟล็ก `--disk-cache-size=1` และ `--media-cache-size=1`
  2. เพิ่ม Parameter Timestamp / Version ต่อท้าย URL ในการโหลด Script เสมอ
  3. ติดตั้งเกตตรวจสอบ Assets (`smoke_test_gate.py` และ `dist_integrity.py`) ในขั้นตอนการ Build

### 4. การขัดกันระหว่างการลากจัดลำดับ (Drag & Drop) กับการคลิกปกติ (Click vs Drag Conflict)
- **สาเหตุที่พบ:** ปุ่มที่อยู่บนคอนเทนเนอร์ที่ลากจัดเรียงได้ (Sortable Containers เช่น Topbar ขวาบน หรือ Rail ด้านซ้าย) จะมีแอตทริบิวต์ `draggable="true"` เมื่อผู้ใช้กดเมาส์ลงบนปุ่ม เบราว์เซอร์จะเตรียมเข้าสู่สถานะ `dragstart` และอาจระงับการยิงอีเวนต์ `click` ส่งผลให้การคลิกติดบ้างไม่ติดบ้าง
- **แนวทางแก้ไขที่ใช้ได้ผล:**
  1. ใช้ฟังก์ชันช่วยตรวจจับ `handleSortableClick(event, callback)` โดยวัดระยะขยับของพิกัดเมาส์ (Movement Delta)
  2. หากระยะการขยับน้อยกว่า 4px ให้ถือว่าเป็นการคลิกปกติ และสั่งรัน Callback ทันที พร้อมตัดการทำงานของ Drag Handler

### 5. ปัญหา Cross-Window Context หลุดในหน้าต่าง Popout
- **สาเหตุที่พบ:** ในหน้าต่างแยก (Standalone Popout) เดิมเคยมีการเรียกฟังก์ชันของหน้าต่างแม่ผ่าน `window.opener.someFunction()` หากหน้าต่างแม่รีโหลดหรือถูกปิด การคลิกปุ่มจะเกิดข้อผิดพลาด Uncaught TypeError: Cannot read properties of null ในคอนโซลอย่างเงียบๆ
- **แนวทางแก้ไขที่ใช้ได้ผล:**
  1. ย้ายการสั่งการระหว่างหน้าต่างไปใช้ Local REST API (`fetch('/api/...')`) หรือ `window.postMessage` ที่มีมาตรฐาน
  2. ครอบฟังก์ชันภายในปุ่มด้วย `try...catch` และ Fallback Handler เสมอ

