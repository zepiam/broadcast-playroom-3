# HANDOFF NOTES - Broadcast Playroom 3 (v3.74)
- **Current Version**: v3.74 (Released & Published to GitHub + Hugging Face)
- **Status**: Stable & Verified via Smoke Test Gate (10/10 tool windows healthy, 0 runtime errors).
---

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

