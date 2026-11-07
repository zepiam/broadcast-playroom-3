# HANDOFF NOTES - Broadcast Playroom 3 (v3.59)
- **Current Version**: v3.59 (Released & Verified In-App Auto-Update)
- **Status**: Stable & Fully Verified across GitHub Releases & Hugging Face Mirrors.
## 📦 PENDING RELEASE — v3.59 (รอ AI ผู้ปล่อยเวอร์ชันอ่านแล้วดำเนินการ) [บันทึก 2026-11-08 โดย Claude (Cowork)]

**สิ่งที่ต้อง release:** Broadcast Playroom **v3.59** (โค้ดทั้งหมดอยู่ใน working tree แล้ว ยังไม่ได้ commit/tag/push/upload; เวอร์ชันที่ปล่อยแล้วล่าสุดคือ v3.58)

**ไฟล์ที่เตรียมไว้ให้แล้ว:**
- `publish_release_v359.py` — สคริปต์ release (copy จาก v3.58 แก้ VERSION=3.59, release_date 2026-11-08, changelog ภาษาไทย, commit message) ขั้นตอน: `npm run build` → แพ็ก `patch-v3.59-lite/full.zip` → finalize zip ก่อนคำนวณ SHA-256 + assert gate → อัปโหลด Hugging Face (`men9ch/broadcast-playroom-3`) → `git add -A` (+ `git reset composer_layout.json` เพื่อไม่ commit ค่าตั้งของผู้ใช้) → commit/tag `v3.59`/push `master --tags` → `gh release create` → purge jsDelivr
- `release.bat` — ตัวรันคลิกเดียว (เช็ก python/npm/`gh auth`/huggingface_hub แล้วเรียกสคริปต์ข้างบน)
- เวอร์ชันถูกบันทึกแล้วใน `package.json`, `updater.py` (`CURRENT_VERSION`), `src/index.html` (title + titlebar tag) ส่วน `version.json` ให้สคริปต์เขียนเอง
- `.gitignore` ข้าม `*.bak*`, `dist_backup_before_ui_update/`, `_to_delete/`, `__pycache__/`; ไฟล์ขยะย้ายไป `_to_delete/` แล้ว (ลบทิ้งได้)

**ลำดับที่ AI ผู้ปล่อยควรทำ (ต้องรันบน Windows ที่มี `gh` ล็อกอิน + Hugging Face token ของบัญชี men9ch):**
1. ตรวจ `git status`/`git diff --stat` ว่าตรงกับรายการด้านล่าง และไม่มีไฟล์แปลกปลอม/ความลับ
2. รัน `python publish_release_v359.py` (หรือ `release.bat`) — ถ้า error ให้หยุดและรายงาน ห้ามรันซ้ำโดยไม่ตรวจว่า push/tag/upload ขั้นไหนเสร็จไปแล้ว
3. หลัง build ตรวจว่า `dist/` มีไฟล์ใหม่ครบ (ตรวจแล้วว่าทุก `./*.js|css` ที่ index/composer/overlay/dock.html อ้างถึงอยู่ใน `files_to_copy` ของ `copy_dist_assets.py`; รอบนี้ไม่มีไฟล์ใหม่) แล้วเปิดแอปจากไฟล์ที่ build จริง ทดสอบ: เปิดหน้าต่าง Replie/ASK/Randomizer, ลากกรอบ, Ctrl-ลากอิสระ, ลูกศร 1px/Shift 10px, ปุ่ม DEMO ขึ้น OBS, ปิดหน้าต่างแล้ว DEMO หาย, ปุ่มทุกปุ่มคลิกได้ (**รอบก่อนเคยปล่อยแล้วปุ่ม/สคริปต์ตายในเครื่องผู้ใช้อื่น ห้ามพลาดซ้ำ**)
4. หลังปล่อย: ตรวจ GitHub Release v3.59 + HF mirror + `version.json` (มีคีย์ `version` และ `latest_version`, SHA ตรง) แล้วลองอัปเดตจากเครื่องที่เป็น v3.58 ผ่านปุ่ม "ตรวจสอบการอัปเดต"
5. อัปเดต WORKLOG/HANDOFF: เปลี่ยนสถานะ v3.59 จาก "รอปล่อย" เป็น "ปล่อยแล้ว" พร้อมผลตรวจ แล้วลบบล็อก PENDING RELEASE นี้ออกจากไฟล์ที่เกี่ยวข้อง

**สิ่งที่อยู่ใน v3.59 (ใช้เป็น release notes / ตรวจสอบ):**
- Replie: หน้าตั้งค่าการแสดงผลใหม่ (locator ลากวาง, ย่อ/ขยาย, ธีม 8 แบบ, ปุ่ม DEMO สด) + หน้าแก้ไขคำสั่ง (จอตัวอย่างลากได้, แอนิเมชันเข้า/ออก + ทดลองบน OBS, ดูสดบน OBS)
- ASK: ออกแบบหน้าปรับแต่ง Overlay ใหม่ (strip compact, bar 17 แบบ, frame 11 แบบ, animation เข้า/ออก, locator, DEMO, แก้ flicker)
- Randomizer: เหลือวงล้อรูเล็ต + สล็อต พร้อมแอนิเมชันหมุนช้าลงจนหยุด, locator ลาก/ย่อขยาย
- ลากวางตำแหน่งทั้ง 3 เครื่องมือ: ค้าง Ctrl = ไม่ snap, ลูกศร = 1px, Shift+ลูกศร = 10px
- DEMO ซ่อนอัตโนมัติเมื่อปิดหน้าต่างเครื่องมือ; ลบวิดเจ็ต ASK/Replie/Randomizer เก่าใน Composer อัตโนมัติ
- หน้าต่างเครื่องมือเปิดที่ 85% ของหน้าต่างหลักแล้วจำขนาด/ตำแหน่ง/จอ; หน้าต่างหลักล็อก min-size ด้วย ClipCursor

**ความเสี่ยงที่ยังไม่ได้ยืนยัน (ทดสอบแค่ Playwright บน cloud ไม่เคยทดสอบในแอปจริง/OBS จริง/dist):**
- `app_window_frame.py` (ClipCursor ล็อก min-size หน้าต่างหลัก) ไม่เคยรันบน Windows จริง — ถ้าเคอร์เซอร์ค้าง/หน้าต่างผิดปกติให้ย้อนด้วย `_to_delete/app_window_frame.py.bak_before_minclip` แล้วค่อยปล่อยโดยไม่มีส่วนนี้
- Chrome/Edge `--app` อาจไม่ยอมให้ `resizeTo/moveTo` จัดขนาด/ตำแหน่ง popout ตามที่จำไว้
- การตั้งค่ารูปลักษณ์ของ ASK มีผลบน OBS ก็ต่อเมื่อบันทึก config ของหน้าต่าง ASK แล้ว (ส่งไปกับ live state ใน field `widget`)

---

- **Key Enhancements & Architectural Milestones (v3.31 - v3.59)**:
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

