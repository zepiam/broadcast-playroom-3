# Broadcast Playroom 3 - Session Handoff

## Current Status (2026-11-01 12:30)
- **Active Release:** `v3.7` (LIVE on GitHub Releases)
- **Repo:** `zepiam/broadcast-playroom-3`
- **Key Changes in v3.7:**
  1. **Fixed Giant Anime Icon / White Screen Bug:** Auto-inject all required stylesheets (`styles.css`, `modal.css`, `widget_customizer.css`, etc.) into `dist/index.html`. Added inline CSS dimensions `16px!important` to `.desktop-titlebar-icon`.
  2. **Removed Splash Screen Permanently:** Converted `splash.py` to dummy no-op and set `no_splash = True` in `launch_dev.py` for instant 0.9s cold startup.
  3. **Fixed Duplicate Controls in Popout Windows:** Hid `.floating-actions-right` and `#desktopTitlebar` in standalone popouts, keeping only the native OS window frame.
  4. **Synchronized Platform Hiding:** Sidebar and Settings platform cards immediately reflect visibility changes across all views.
- **Verification:** All tests passed with Playwright (`tests/verify_ui_fixes.py`).
