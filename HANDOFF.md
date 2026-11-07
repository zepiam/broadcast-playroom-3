# HANDOFF NOTES - Broadcast Playroom 3 (v3.58)
- **Current Version**: v3.58 (Released & Verified In-App Auto-Update)
- **Status**: Stable & Fully Verified across GitHub Releases & Hugging Face Mirrors.
- **Key Enhancements & Architectural Milestones (v3.31 - v3.58)**:
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

