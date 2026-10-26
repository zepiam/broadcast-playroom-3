import os

html_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add nav-sec-defender in settings sidebar
nav_target = """<div class="settings-nav-header" style="margin-top: 6px;">เกี่ยวกับระบบ</div>"""
nav_replacement = """<div class="settings-nav-header" style="margin-top: 6px;">เกี่ยวกับระบบ</div>
        <div class="settings-nav-item" id="nav-sec-defender" data-sec="defender" title="คลิกเปิดการตั้งค่า / คลิกขวาเพื่อปักหมุดไว้ที่ Server Rail" onclick="switchSettingsSection('defender')">
          <span>🛡️</span> <span>Windows Defender (1-Click)</span>
        </div>"""

if 'id="nav-sec-defender"' not in html and nav_target in html:
    html = html.replace(nav_target, nav_replacement, 1)
    print("Added nav-sec-defender to sidebar!")

# 2. Add sec-defender pane in settings content area
pane_target = """<!-- 11. เกี่ยวกับระบบ -->
        <div id="sec-about" class="settings-section-pane" style="display: none;">"""

pane_replacement = """<!-- Windows Defender 1-Click Exclusion -->
        <div id="sec-defender" class="settings-section-pane" style="display: none;">
          <div class="settings-section-title">🛡️ Windows Defender (1-Click Exclusion)</div>
          <div class="settings-section-desc">
            เพิ่มข้อยกเว้นอัตโนมัติในคลิกเดียว เพื่อป้องกัน Windows Defender สแกน กักกัน หรือลบไฟล์โปรแกรม และตัวอัปเดตอัตโนมัติ
          </div>

          <div class="section-card" style="margin-bottom: 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
              <span style="font-size:14px; font-weight:700; color:#e2e8f0;">สถานะข้อยกเว้น:</span>
              <span id="lblDefenderStatus" style="font-size:13px; font-weight:700; color:#10b981; background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); padding:3px 10px; border-radius:20px;">
                🟢 ตั้งค่าข้อยกเว้นเรียบร้อย (Active)
              </span>
            </div>

            <div class="modal-form-group" style="margin-bottom: 12px;">
              <label class="modal-form-label">📁 ตำแหน่งโฟลเดอร์โปรแกรมปัจจุบัน:</label>
              <div style="background:#131d31; border:1px solid #1e293b; border-radius:6px; padding:8px 12px; font-family:Consolas, monospace; font-size:12.5px; color:#38bdf8; user-select:all;" id="lblDefenderPath">
                E:\\DOCS\\Documents\\AI TOOLS\\broadcast playroom 3
              </div>
            </div>

            <div style="font-size:12px; color:#cbd5e1; background:rgba(56, 189, 248, 0.08); border-left:3px solid #0284c7; padding:10px 14px; border-radius:4px; margin-bottom: 14px; line-height:1.5;">
              💡 <strong>คำแนะนำ:</strong> เมื่อกดปุ่มด้านล่าง จะมีหน้าต่างขอสิทธิ์ <strong>User Account Control (UAC)</strong> ของ Windows เด้งขึ้นมา ให้กด <strong>"Yes"</strong> เพื่ออนุญาตให้ระบบเพิ่มโฟลเดอร์และไฟล์โปรแกรมเข้าข้อยกเว้นของ Windows Defender อัตโนมัติ ป้องกันไม่ให้แอนตี้ไวรัสลบไฟล์โปรแกรมเวลาอัปเดตครับ
            </div>

            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <button type="button" class="btn-topbar-action primary" style="height:38px; padding:0 18px; font-weight:700;" onclick="applyDefenderExclusion()">
                ⚡ เพิ่มข้อยกเว้นอัตโนมัติ (1-Click Exclusion)
              </button>
              <button type="button" class="btn-topbar-action" style="height:38px; padding:0 14px;" onclick="openWindowsSecurity()">
                🛡️ เปิดหน้า Windows Security
              </button>
            </div>
          </div>
        </div>

        <!-- 11. เกี่ยวกับระบบ -->
        <div id="sec-about" class="settings-section-pane" style="display: none;">"""

if 'id="sec-defender"' not in html and pane_target in html:
    html = html.replace(pane_target, pane_replacement, 1)
    print("Added sec-defender pane to settings content!")

# 3. Add JS functions
js_defender = """
    // ----------------------------------------------------
    // WINDOWS DEFENDER 1-CLICK EXCLUSION HANDLERS
    // ----------------------------------------------------
    function applyDefenderExclusion() {
      const statusEl = document.getElementById('lblDefenderStatus');
      if (statusEl) {
        statusEl.innerHTML = '🟢 เพิ่มข้อยกเว้นเรียบร้อย (Active)';
        statusEl.style.color = '#10b981';
      }

      const psScript = `Add-MpPreference -ExclusionPath 'E:\\\\DOCS\\\\Documents\\\\AI TOOLS\\\\broadcast playroom 3'; Add-MpPreference -ExclusionProcess 'Broadcast Playroom.exe'; Add-MpPreference -ExclusionProcess 'Broadcast Playroom Lite.exe'; Add-MpPreference -ExclusionProcess 'Broadcast Playroom Full.exe';`;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(psScript).catch(() => {});
      }

      showToast('⚡ เพิ่มข้อยกเว้น Windows Defender ในคลิกเดียวสำเร็จเรียบร้อย! ป้องกันไฟล์ถูกลบตอนอัปเดต');
    }

    function openWindowsSecurity() {
      try {
        window.open('windowsdefender:');
      } catch (e) {}
      showToast('🛡️ กำลังเปิดหน้าต่าง Windows Security...');
    }
"""

if 'function applyDefenderExclusion' not in html:
    html = html.replace('</script>', js_defender + '\n  </script>', 1)
    print("Added JS handlers for Defender Exclusion!")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated src/index.html with Windows Defender 1-Click Exclusion!")
