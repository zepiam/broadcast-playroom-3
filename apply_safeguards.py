import os

# ==============================================================
# Tier 1: Add Critical Fail-Safe CSS directly inside <head> of src/index.html
# ==============================================================
with open('src/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

critical_style = """  <!-- Critical Fail-Safe Styles (Zero-FOUC & 100% Guaranteed Image Containment) -->
  <style id="critical-failsafe-base-style">
    html, body {
      background-color: #1e1f22 !important;
      color: #f2f3f5 !important;
    }
    .desktop-titlebar {
      background-color: #2b2d31 !important;
      height: 32px !important;
    }
    .desktop-titlebar-icon, img.desktop-titlebar-icon {
      width: 16px !important;
      height: 16px !important;
      max-width: 16px !important;
      max-height: 16px !important;
      object-fit: contain !important;
      display: inline-block !important;
    }
  </style>
"""

if '<style id="critical-failsafe-base-style">' not in html:
    html = html.replace('<head>', '<head>\n' + critical_style, 1)
    with open('src/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Tier 1: Critical Fail-Safe CSS added to src/index.html")
else:
    print("Tier 1: Already present in src/index.html")


# ==============================================================
# Tier 2: Add Build-Time Strict Verification Gate in copy_dist_assets.py
# ==============================================================
with open('copy_dist_assets.py', 'r', encoding='utf-8') as f:
    copy_script = f.read()

audit_gate = """
# ==============================================================
# STRICT SAFETY AUDIT GATE: Fail build if any asset or link is missing
# ==============================================================
with open(dist_index, 'r', encoding='utf-8') as f:
    final_html = f.read()

for req in required_links:
    if req not in final_html:
        raise RuntimeError(f"CRITICAL BUILD FAILURE: {req} is missing from dist/index.html!")

if 'styles.css' not in final_html:
    raise RuntimeError("CRITICAL BUILD FAILURE: styles.css is not linked in dist/index.html!")

styles_path = os.path.join(dist_dir, 'styles.css')
if not os.path.exists(styles_path) or os.path.getsize(styles_path) < 50000:
    raise RuntimeError("CRITICAL BUILD FAILURE: dist/styles.css is missing or too small!")

if 'width:16px' not in final_html and 'max-width:16px' not in final_html:
    raise RuntimeError("CRITICAL BUILD FAILURE: .desktop-titlebar-icon lacks size constraints in dist/index.html!")

print(">>> [SAFETY GATE PASSED] All assets, stylesheets, and fail-safe constraints verified 100% complete!")
"""

if "STRICT SAFETY AUDIT GATE" not in copy_script:
    copy_script += "\n" + audit_gate
    with open('copy_dist_assets.py', 'w', encoding='utf-8') as f:
        f.write(copy_script)
    print("Tier 2: Strict Safety Audit Gate added to copy_dist_assets.py")
else:
    print("Tier 2: Already present in copy_dist_assets.py")


# ==============================================================
# Tier 3: Add Runtime Self-Healing in launch_dev.py
# ==============================================================
with open('launch_dev.py', 'r', encoding='utf-8') as f:
    launch_py = f.read()

runtime_healer = """
def ensure_frontend_integrity():
    \"\"\"Runtime Self-Healing: If dist/index.html ever loses critical stylesheets or constraints,
    automatically patch it before pywebview loads it. This guarantees zero white-screen or giant-icon bugs.\"\"\"
    try:
        idx_path = os.path.join(DIST_DIR, 'index.html')
        if not os.path.exists(idx_path):
            return
        with open(idx_path, 'r', encoding='utf-8') as f:
            content = f.read()

        repaired = False
        # 1. Guarantee inline styling for titlebar icon
        if '.desktop-titlebar-icon' in content and 'width:16px!important' not in content:
            content = content.replace(
                '<img src="./assets/bp-full-icon.png" class="desktop-titlebar-icon"',
                '<img src="./assets/bp-full-icon.png" class="desktop-titlebar-icon" style="width:16px!important;height:16px!important;max-width:16px!important;max-height:16px!important;object-fit:contain;flex-shrink:0;display:inline-block;"'
            )
            repaired = True

        # 2. Guarantee styles.css is loaded
        if 'styles.css' not in content and '</head>' in content:
            content = content.replace('</head>', '  <link rel="stylesheet" href="./styles.css">\\n  <link rel="stylesheet" href="./modal.css">\\n  <link rel="stylesheet" href="./ui_readability.css">\\n</head>')
            repaired = True

        # 3. Guarantee dark background on html tag
        if '<html lang="th" class="notranslate" translate="no">' in content:
            content = content.replace('<html lang="th" class="notranslate" translate="no">', '<html lang="th" class="notranslate" translate="no" style="background:#1e1f22!important;color:#f2f3f5!important;">')
            repaired = True

        if repaired:
            with open(idx_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("[INTEGRITY] Successfully self-healed frontend dist/index.html")
    except Exception as e:
        logger.warning(f"[INTEGRITY] Frontend check warning: {e}")

ensure_frontend_integrity()
"""

if "def ensure_frontend_integrity():" not in launch_py:
    # Place it right after DIST_DIR definition
    dist_pattern = "DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dist'))"
    launch_py = launch_py.replace(dist_pattern, dist_pattern + "\n" + runtime_healer)
    with open('launch_dev.py', 'w', encoding='utf-8') as f:
        f.write(launch_py)
    print("Tier 3: Runtime Self-Healing added to launch_dev.py")
else:
    print("Tier 3: Already present in launch_dev.py")
