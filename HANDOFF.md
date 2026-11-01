# HANDOFF NOTES - Broadcast Playroom 3 (v3.17)
- **Current Version**: v3.17 (Released & Live on GitHub)
- **Status**: Stable & Fully Verified.
- **Key Enhancements (v3.16 - v3.17)**:
  1. **Dual-Path Atomic Update Patches**: Patch zip files are strictly bundled with both root and `_internal/` paths (`_internal/dist`, `_internal/updater.py`, `_internal/launch_dev.py`, `_internal/version.json`) ensuring that PyInstaller builds update cleanly across all existing client versions without ever rolling back.
  2. **Backward-Compatible Version Manifest**: `version.json` permanently retains both `version` and `latest_version` keys at the root level to guarantee 100% compatibility with older updaters (e.g. v3.15).
  3. **Zero GPU Lockup Squircle Progress Bar**: Update button on server rail displays dynamic real-time progress border during background download and encloses completely at 100% without infinite CSS animations.
  4. **Smart Overlay+ Visibility**: Overlay+ button and frame toggle button automatically hide from the topbar when no URLs are configured, and re-appear immediately when configured.
  5. **Permanent User Settings Preservation**: Multi-path backup/restore in updater and platform settings loader permanently retains all user channels, checkboxes, and auto-connect flags across all updates.

## กฎเหล็กการสร้างและปล่อย Patch อัปเดต (Strict Release Invariants)
1. **Dual-Path Packaging**: แพ็กเกจ patch-v*.zip ทุกตัวต้องมีโครงสร้างไฟล์ทั้ง root (`dist/`) และ `_internal/` (`_internal/dist/`) เสมอ ห้ามละเลยเด็ดขาด
2. **Version Manifest Parity**: ใน `version.json` ต้องมีคีย์ `"version"` และ `"latest_version"` คู่กันเสมอ
3. **Zero GPU Lockup**: โมดอลหรือเอฟเฟกต์แสงต้องไม่มี continuous loop animation หรือ backdrop-filter เต็มจอเด็ดขาด
4. **Permanent Settings Retention**: ห้ามลบหรือเขียนทับไฟล์ config ของผู้ใช้ (`platform_settings.json`, `composer_layout.json`, `rvc_settings.json`) เด็ดขาด
