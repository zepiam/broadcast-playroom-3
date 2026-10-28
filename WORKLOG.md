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
