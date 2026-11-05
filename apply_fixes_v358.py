import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

# 1. Update src/composer_studio.js
comp_path = ROOT / "src" / "composer_studio.js"
comp_code = comp_path.read_text(encoding="utf-8")
old_trash_btn = '<button type="button" class="composer-btn-layer-action close-red" data-action="delete" title="ลบวิดเจ็ต">'
new_trash_btn = '<button type="button" class="composer-btn-layer-action btn-layer-delete" data-action="delete" title="ลบวิดเจ็ต">'
if old_trash_btn in comp_code:
    comp_code = comp_code.replace(old_trash_btn, new_trash_btn)
    comp_path.write_text(comp_code, encoding="utf-8")
    print("[OK] src/composer_studio.js: Replaced close-red with btn-layer-delete.")
else:
    print("[WARN] old_trash_btn not found directly, checking regex...")
    comp_code = re.sub(
        r'<button type="button" class="composer-btn-layer-action close-red" data-action="delete"[^>]*>',
        '<button type="button" class="composer-btn-layer-action btn-layer-delete" data-action="delete" title="ลบวิดเจ็ต">',
        comp_code
    )
    comp_path.write_text(comp_code, encoding="utf-8")
    print("[OK] src/composer_studio.js: Replaced via regex.")

# 2. Update src/composer_studio.css
css_path = ROOT / "src" / "composer_studio.css"
css_code = css_path.read_text(encoding="utf-8")
old_css_hover = ".composer-btn-layer-action.close-red:hover {"
new_css_hover = ".composer-btn-layer-action.btn-layer-delete:hover,\n.composer-btn-layer-action.close-red:hover {"
if old_css_hover in css_code and ".btn-layer-delete" not in css_code:
    css_code = css_code.replace(old_css_hover, new_css_hover)
    css_path.write_text(css_code, encoding="utf-8")
    print("[OK] src/composer_studio.css: Updated hover style for btn-layer-delete.")

# 3. Update src/index.html
index_path = ROOT / "src" / "index.html"
index_code = index_path.read_text(encoding="utf-8")

# 3.1 Bump version 3.57 -> 3.58
index_code = index_code.replace("<title>Broadcast Playroom v3.57</title>", "<title>Broadcast Playroom v3.58</title>")
index_code = index_code.replace('<span class="desktop-titlebar-tag">v3.57</span>', '<span class="desktop-titlebar-tag">v3.58</span>')
index_code = index_code.replace('>v3.57</span>', '>v3.58</span>')
print("[OK] src/index.html: Bumped version to 3.58.")

# 3.2 Fix popout click capture listener in openToolWindow
popout_handler_pattern = re.compile(
    r"// Capture all clicks on close buttons inside the popout window\s*document\.addEventListener\('click', \(e\) => \{.*?\}, true\);",
    re.DOTALL
)

new_popout_handler = """// Capture all clicks on close buttons inside the popout window
        document.addEventListener('click', (e) => {
          const btn = e.target.closest('button, .btn-win-action');
          if (!btn) return;
          if (btn.classList.contains('settings-nav-item') || btn.closest('.settings-sidebar')) return;
          if (btn.closest('.tab-header') || btn.closest('.chat-header') || btn.closest('.header-left')) return;
          if (btn.closest('.composer-layers-container, .composer-layers-list, .composer-layer-item, #composerLayersList, .composer-canvas-container, .composer-sidebar, #composerPropertiesPanel, .composer-properties, table, tr, td, .ask-choice-row, .modal-body, .window-body, .panel-body')) return;

          const text = (btn.textContent || '').trim();
          const title = (btn.getAttribute('title') || '').trim();
          const onclickAttr = btn.getAttribute('onclick') || '';
          const isTitlebar = !!btn.closest('.floating-actions-right, .floating-header, .desktop-titlebar-controls, .win-header, .window-header');

          if (onclickAttr.includes('closeToolWindow') || btn.classList.contains('win-close') || (isTitlebar && (btn.classList.contains('close-red') || text === 'ปิดหน้าต่าง' || text === 'ปิด' || title === 'ปิดหน้าต่าง' || title === 'ปิด' || text === '✕' || text === 'x'))) {
            e.preventDefault();
            e.stopPropagation();
            closeToolWindow(targetName);
          }
        }, true);"""

if popout_handler_pattern.search(index_code):
    index_code = popout_handler_pattern.sub(new_popout_handler, index_code)
    print("[OK] src/index.html: Fixed popout click capture listener.")
else:
    print("[WARN] popout_handler_pattern not found!")

# 3.3 Fix popout closeBtns.forEach querySelector
close_btns_pattern = re.compile(
    r"const closeBtns = win\.querySelectorAll\('\.btn-win-action\.win-close, \.btn-win-action\.close-red, button\.btn-win-action, button\.btn-topbar-action, button'\);\s*closeBtns\.forEach\(btn => \{.*?\}\);",
    re.DOTALL
)

new_close_btns = """const closeBtns = win.querySelectorAll('.floating-header .btn-win-action, .floating-actions-right .btn-win-action, .win-close');
        closeBtns.forEach(btn => {
          if (btn.classList.contains('settings-nav-item') || btn.closest('.settings-sidebar')) return;
          if (btn.closest('.tab-header') || btn.closest('.chat-header') || btn.closest('.header-left')) return;
          if (btn.closest('.composer-layers-container, .composer-layer-item, .composer-layers-list, #composerLayersList, .composer-canvas-container, .composer-sidebar, table')) return;
          const text = (btn.textContent || '').trim();
          const title = (btn.getAttribute('title') || '').trim();
          const onclickAttr = btn.getAttribute('onclick') || '';
          if (text === 'ปิดหน้าต่าง' || text === 'ปิด' || title === 'ปิดหน้าต่าง' || title === 'ปิด' || text === '✕' || text === 'x' || btn.classList.contains('win-close') || btn.classList.contains('close-red') || onclickAttr.includes('closeToolWindow')) {
            btn.onclick = doClose;
          }
        });"""

if close_btns_pattern.search(index_code):
    index_code = close_btns_pattern.sub(new_close_btns, index_code)
    print("[OK] src/index.html: Fixed closeBtns assignment in popout.")
else:
    print("[WARN] close_btns_pattern not found!")

# 3.4 In checkAppUpdate: Replace manual zip download with in-app updater popup
old_dl_btn_pattern = re.compile(
    r'<button class="btn btn-primary btn-sm" onclick="openExternalUrl\(\'\$\{data\.download_url[^}]*\}\'\)"[^>]*>.*?ดาวน์โหลด / ดูการอัปเดต.*?</button>',
    re.DOTALL
)

new_inapp_btn = """<button class="btn btn-primary btn-sm" onclick="showFastUpdateModal()" style="font-size:12px; padding:7px 16px; background:#23a55a; border-color:#23a55a; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:5px;">
                    ⚡ อัปเดตในโปรแกรมทันที
                  </button>
                  <button class="btn btn-secondary btn-sm" onclick="openExternalUrl('https://github.com/zepiam/broadcast-playroom-3/releases')" style="font-size:12px; padding:7px 14px; cursor:pointer;">
                    🌐 ดูบันทึกการอัปเดต (Changelog)
                  </button>"""

if old_dl_btn_pattern.search(index_code):
    index_code = old_dl_btn_pattern.sub(new_inapp_btn, index_code)
    print("[OK] src/index.html: Replaced manual download button with in-app update trigger.")
else:
    print("[WARN] old_dl_btn_pattern not found!")

# Also ensure when manual is true, showFastUpdateModal is launched automatically
old_manual_toast = "if (manual) {\n            showToast(`"
if old_manual_toast in index_code:
    index_code = index_code.replace(
        old_manual_toast,
        "if (manual) {\n            showFastUpdateModal();\n            showToast(`"
    )
    print("[OK] src/index.html: Added auto showFastUpdateModal() on manual check.")

index_path.write_text(index_code, encoding="utf-8")

# 4. Update package.json
pkg_path = ROOT / "package.json"
pkg_json = pkg_path.read_text(encoding="utf-8")
pkg_json = pkg_json.replace('"version": "3.57"', '"version": "3.58"')
pkg_path.write_text(pkg_json, encoding="utf-8")
print("[OK] package.json updated to 3.58.")

# 5. Update updater.py
updater_path = ROOT / "updater.py"
updater_py = updater_path.read_text(encoding="utf-8")
updater_py = re.sub(r'CURRENT_VERSION\s*=\s*"[^"]+"', 'CURRENT_VERSION = "3.58"', updater_py)
updater_path.write_text(updater_py, encoding="utf-8")
print("[OK] updater.py CURRENT_VERSION updated to 3.58.")
