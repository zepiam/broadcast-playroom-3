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
