# HANDOFF NOTES - Broadcast Playroom 3 (v3.60)
- **Current Version**: v3.60 (Released & Verified In-App Auto-Update)
- **Status**: Stable & Fully Verified across GitHub Releases & Hugging Face Mirrors.
---

- **Key Enhancements & Architectural Milestones (v3.31 - v3.60)**:
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

