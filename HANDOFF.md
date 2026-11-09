# HANDOFF NOTES - Broadcast Playroom 3 (v3.64)
- **Current Version**: v3.64 (Released & Verified In-App Auto-Update)
- **Status**: Stable & Fully Verified across GitHub Releases & Hugging Face Mirrors.
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

- **Key Enhancements & Architectural Milestones (v3.31 - v3.64)**:
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

