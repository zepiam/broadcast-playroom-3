# Broadcast Playroom 3 - Handoff Guide

## Release Status: v3.8 (Live on GitHub Releases)
- **Version:** `3.8`
- **Release Tag:** `v3.8`
- **Patches Published:**
  - `BroadcastPlayroom3-Lite-Patch-3.8.zip`
  - `BroadcastPlayroom3-Full-Patch-3.8.zip`
- **Manifest:** Synced on GitHub `master` branch at `version.json`

## Summary of Fixes in v3.8
1. **Game Overlay Suite Restored:**
   - Modern full tool suite with 4 modes: Default, Theme (10 custom themes with pagination), Balloon (speech bubble), and Character Talk (VTuber avatars with image upload).
   - Global hotkey rebinds (Ctrl+Shift+G / Ctrl+Shift+H).
   - Fluid range sliders with live preview for both Game Overlay and Viewer Overlay.
   - Dedicated Overlay+ dialog (`#win-overlay-plus-settings`) for up to 3 floating browser windows.
2. **Settings Sidebar Restored:**
   - Fixed popout suppression rule so `.settings-sidebar` displays properly (`display: flex !important; visibility: visible !important;`).
   - All 16 settings categories (Platforms, Chatbot, TTS, Themes, Translate, OBS, Docks, Networking, NG, Replace, Block, Secret, Defender, About, Supporters, Log) are visible and navigable.
3. **Desktop Window Dragging Fixed:**
   - Restored `webview.settings['DRAG_REGION_SELECTOR'] = '.pywebview-drag-region, .desktop-titlebar'` with `easy_drag=True`.
   - Added fluid requestAnimationFrame client-side drag fallback to `/api/window/frame`.
4. **Popout Lifecycle & DOM Re-adoption Fixed:**
   - `closeToolWindow` properly closes popup windows via `window.opener.closeToolWindow`.
   - Node re-adoption dynamically rebinds event handlers so embedded window buttons remain fully functional after popup close.

## Verification
- `tests/verify_game_overlay_settings.py` -> **PASS 100%**
- `tests/verify_window_frame.py` -> **PASS 100%**
- `tests/verify_ui_fixes.py` -> **PASS 100%**
- Popout Settings Sidebar Check -> **PASS 100%** (16/16 visible categories)
