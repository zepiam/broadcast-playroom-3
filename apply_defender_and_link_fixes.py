import os
import re

BASE_DIR = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"

# 1. Update launch_dev.py for os.startfile in /api/open-external
ld_path = os.path.join(BASE_DIR, "launch_dev.py")
with open(ld_path, "r", encoding="utf-8") as f:
    ld = f.read()

open_ext_target = """                import webbrowser
                webbrowser.open(url)"""

open_ext_replacement = """                if os.name == 'nt':
                    try:
                        os.startfile(url)
                    except Exception:
                        import webbrowser
                        webbrowser.open(url)
                else:
                    import webbrowser
                    webbrowser.open(url)"""

ld = ld.replace(open_ext_target, open_ext_replacement)
with open(ld_path, "w", encoding="utf-8") as f:
    f.write(ld)
print("[OK] launch_dev.py updated with os.startfile for Windows native browser launching")

# 2. Update src/index.html
html_path = os.path.join(BASE_DIR, "src", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Fix switchSettingsSection to call checkDefenderSettingsPane
target_switch = "if (sectionId === 'supporters') window.SupportersUI?.load();"
replacement_switch = """if (sectionId === 'supporters') window.SupportersUI?.load();
      if (sectionId === 'defender') {
        if (typeof checkDefenderSettingsPane === 'function') checkDefenderSettingsPane();
      }"""
assert target_switch in html, "target_switch not found"
html = html.replace(target_switch, replacement_switch)

# Fix checkDefenderSettingsPane to handle errors and fallback
target_cdsp = """    async function checkDefenderSettingsPane() {
      const statusEl = document.getElementById('lblDefenderStatus');
      const pathEl = document.getElementById('lblDefenderPath');
      try {
        const res = await fetch('/api/defender/status');
        const data = await res.json();
        if (pathEl) pathEl.textContent = data.current_dir || '-';
        if (statusEl) {
          if (data.is_excluded) {
            statusEl.textContent = '✅ ยกเว้นเรียบร้อย';
            statusEl.style.color = '#10b981';
            statusEl.style.background = 'rgba(16,185,129,0.15)';
            statusEl.style.borderColor = 'rgba(16,185,129,0.3)';
          } else if (data.status === 'relocated') {
            statusEl.textContent = '⚠️ โฟลเดอร์ถูกย้ายที่ตั้ง';
            statusEl.style.color = '#f59e0b';
            statusEl.style.background = 'rgba(245,158,11,0.15)';
            statusEl.style.borderColor = 'rgba(245,158,11,0.3)';
          } else {
            statusEl.textContent = '❌ ยังไม่ได้รับการยกเว้น';
            statusEl.style.color = '#ef4444';
            statusEl.style.background = 'rgba(239,68,68,0.15)';
            statusEl.style.borderColor = 'rgba(239,68,68,0.3)';
          }
        }
      } catch (_) {}
    }"""

replacement_cdsp = """    async function checkDefenderSettingsPane() {
      const statusEl = document.getElementById('lblDefenderStatus');
      const pathEl = document.getElementById('lblDefenderPath');
      try {
        const res = await fetch('/api/defender/status');
        const data = await res.json();
        if (pathEl) pathEl.textContent = data.current_dir || '-';
        if (statusEl) {
          if (data.is_excluded) {
            statusEl.textContent = '✅ ยกเว้นเรียบร้อย';
            statusEl.style.color = '#10b981';
            statusEl.style.background = 'rgba(16,185,129,0.15)';
            statusEl.style.borderColor = 'rgba(16,185,129,0.3)';
          } else if (data.status === 'relocated') {
            statusEl.textContent = '⚠️ โฟลเดอร์ถูกย้ายที่ตั้ง';
            statusEl.style.color = '#f59e0b';
            statusEl.style.background = 'rgba(245,158,11,0.15)';
            statusEl.style.borderColor = 'rgba(245,158,11,0.3)';
          } else {
            statusEl.textContent = '❌ ยังไม่ได้รับการยกเว้น';
            statusEl.style.color = '#ef4444';
            statusEl.style.background = 'rgba(239,68,68,0.15)';
            statusEl.style.borderColor = 'rgba(239,68,68,0.3)';
          }
        }
      } catch (_) {
        if (pathEl && (pathEl.textContent === 'กำลังโหลด...' || !pathEl.textContent)) pathEl.textContent = '-';
        if (statusEl) {
          statusEl.textContent = '❌ ยังไม่ได้รับการยกเว้น';
          statusEl.style.color = '#ef4444';
          statusEl.style.background = 'rgba(239,68,68,0.15)';
          statusEl.style.borderColor = 'rgba(239,68,68,0.3)';
        }
      }
    }"""

if target_cdsp in html:
    html = html.replace(target_cdsp, replacement_cdsp)
    print("[OK] checkDefenderSettingsPane replaced")

# Ensure checkDefenderSettingsPane runs on boot
boot_target = "window.addEventListener('DOMContentLoaded', () => {"
if boot_target in html:
    html = html.replace(boot_target, boot_target + "\n      setTimeout(() => { if (typeof checkDefenderSettingsPane === 'function') checkDefenderSettingsPane(); }, 1200);")
    print("[OK] checkDefenderSettingsPane added to DOMContentLoaded")

# Fix refreshStreamTitle to ensure streamInfo is displayed
target_rst = """        if (data && data.title) {
          if (titleEl) titleEl.textContent = data.title;
          showToast('✅ อัปเดต Title ไลฟ์สตรีมเรียบร้อย');
        } else {
          showToast('⚠️ ไม่พบข้อมูล Title หรือช่องยังไม่ได้ออนไลน์');
        }"""

replacement_rst = """        const infoBox = document.getElementById('stream-info-' + key);
        if (infoBox) infoBox.style.display = 'flex';
        if (data && data.title) {
          if (titleEl) titleEl.textContent = data.title;
          showToast('✅ อัปเดต Title ไลฟ์สตรีม: ' + data.title);
        } else {
          showToast('⚠️ ไม่พบข้อมูล Title หรือช่องยังไม่ได้ออนไลน์');
        }"""

if target_rst in html:
    html = html.replace(target_rst, replacement_rst)
    print("[OK] refreshStreamTitle updated to reveal infoBox")

# Change Edit link from <a> to <button> to eliminate # and javascript:void(0)
for plat in ['twitch', 'youtube', 'kick']:
    old_a1 = f'<a href="#" class="plat-edit-link" onclick="editPlatformStreamInfo(\'{plat}\'); return false;" title="แก้ไขข้อมูลสตรีม {plat.capitalize()}">Edit</a>'
    new_btn = f'<button type="button" class="plat-edit-link" onclick="editPlatformStreamInfo(\'{plat}\');" title="แก้ไขข้อมูลสตรีม {plat.capitalize()}">Edit</button>'
    if old_a1 in html:
        html = html.replace(old_a1, new_btn)

# Ensure openExternalUrl executes dual action
target_oeu = """    function openExternalUrl(url) {
      if (!url) return;
      try {
        fetch('/api/open-external', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url })
        }).then(res => {
          if (!res.ok) {
            fetch('/api/open-external?url=' + encodeURIComponent(url)).catch(() => {
              window.open(url, '_blank');
            });
          }
        }).catch(() => {
          fetch('/api/open-external?url=' + encodeURIComponent(url)).catch(() => {
            window.open(url, '_blank');
          });
        });
      } catch (_) {
        window.open(url, '_blank');
      }
    }"""

replacement_oeu = """    function openExternalUrl(url) {
      if (!url) return;
      try {
        fetch('/api/open-external', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url })
        }).catch(() => {
          fetch('/api/open-external?url=' + encodeURIComponent(url)).catch(() => {});
        });
      } catch (_) {}
      try {
        window.open(url, '_blank');
      } catch (_) {}
    }"""

if target_oeu in html:
    html = html.replace(target_oeu, replacement_oeu)
    print("[OK] openExternalUrl updated with dual action")

# Add CSS for button.plat-edit-link
css_inject = """button.plat-edit-link {
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  color: #5865f2 !important;
  padding: 0 !important;
  text-decoration: underline !important;
  line-height: inherit !important;
}
button.plat-edit-link:hover {
  color: #7983f5 !important;
}"""

if "button.plat-edit-link" not in html:
    html = html.replace("</style>", css_inject + "\n</style>", 1)
    print("[OK] button.plat-edit-link CSS added")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] src/index.html updated successfully!")
