# HANDOFF NOTES - Broadcast Playroom 3 (v3.30)
- **Current Version**: v3.30 (Tested & Verified In-App Update by User)
- **Status**: Stable & Fully Verified.
- **Key Enhancements (v3.18 - v3.30)**:
  1. **Single Instance Guard**: Windows Named Mutex (`Local\BroadcastPlayroom3_App_Mutex_{APP_PROJECT_ID}`) and `bring_main_window_to_front()` Win32 API prevent duplicate app instances from launching and deadlocking WebView2/GPU. Clicking a second instance brings the existing window to front cleanly.
  2. **Multi-Platform Real-Time Avatar Fetching & Caching**: Added persistent avatar extraction across Twitch, Kick, YouTube (InnerTube thumbnails and API `profileImageUrl`), and TikTok.
  3. **Resilient In-App Updater Engine**:
     - Fastly/GitHub CDN cache-busting on manifest fetching (`RELEASE_MANIFEST_URL` first + `?t=timestamp` + `Cache-Control: no-cache, no-store`).
     - SSL Multi-Context support in `download_update_file` (Windows certs, standard, and unverified fallback for users with Antivirus HTTPS scanning).
     - Antivirus file lock retry loop during `.zip` swap/rename.
     - Interactive retry handling in modal UI; failure displays error details and a retry button without prematurely closing the app.
  4. **Compact Master + 3-Grid Block Rules Layout in Viewer Profile**:
     - Re-architected `paneProfTab4` in `author-profile` from a cramped 1-column vertical list with scrollbar into a modern 2-tier card layout:
       - Top Master Card: `[ 🛑 บล็อกทั้งหมด (Block All) ]` with large switch and red accent.
       - Bottom Sub-Grid: 3 compact columns side-by-side (`🖥️ ซ่อนจาก OBS`, `🔇 ปิดเสียง TTS`, `🤖 ปิดบอท Replie`).
     - Fits 100% within ~110px without vertical scrollbars or sliding needed.
     - Adjusted popout window default dimensions for `author-profile` to `(680, 620)` for optimal breathing room.
  5. **Dual-Mirror Release Protocol (Mandatory)**: Releases are published to both **GitHub Releases** (Primary) and **HuggingFace** (`men9ch/broadcast-playroom-3`) (Secondary Mirror) with identical SHA-256 checksums and auto-failover support.
  5. **Dual-Path Atomic Update Patches**: Patch zip files are strictly bundled with both root and `_internal/` paths (`_internal/dist`, `_internal/updater.py`, `_internal/launch_dev.py`, `_internal/version.json`) ensuring that PyInstaller builds update cleanly across all existing client versions without ever rolling back.
  6. **Backward-Compatible Version Manifest**: `version.json` permanently retains both `version` and `latest_version` keys at the root level to guarantee 100% compatibility with older updaters.
  7. **Permanent User Settings Preservation**: Multi-path backup/restore in updater and platform settings loader permanently retains all user channels, checkboxes, and auto-connect flags across all updates.

## กฎเหล็กการสร้างและปล่อย Patch อัปเดต (Strict Release Invariants)
1. **Dual-Mirror Publishing**: ทุก release ต้องอัปโหลดคู่ขนานทั้ง **GitHub Releases** และ **HuggingFace Mirror** (`men9ch/broadcast-playroom-3`) เสมอ พร้อมค่า SHA-256 ตรงกัน 100%
2. **Dual-Path Packaging**: แพ็กเกจ patch-v*.zip ทุกตัวต้องมีโครงสร้างไฟล์ทั้ง root (`dist/`) และ `_internal/` (`_internal/dist/`) เสมอ ห้ามละเลยเด็ดขาด
3. **Version Manifest Parity**: ใน `version.json` ต้องมีคีย์ `"version"` และ `"latest_version"` คู่กันเสมอ
4. **Zero GPU Lockup**: โมดอลหรือเอฟเฟกต์แสงต้องไม่มี continuous loop animation หรือ backdrop-filter เต็มจอเด็ดขาด
5. **Permanent Settings Retention**: ห้ามลบหรือเขียนทับไฟล์ config ของผู้ใช้ (`platform_settings.json`, `composer_layout.json`, `rvc_settings.json`) เด็ดขาด
