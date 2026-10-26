import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

html_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html'
css_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/styles.css'

# ==============================================================================
# 1. UPDATE index.html
# ==============================================================================
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1.1 Expand win-settings window size slightly for spacious comfort
html = html.replace('id="win-settings" style="width: 880px; height: 600px;', 'id="win-settings" style="width: 920px; height: 620px;')

# 1.2 Polish Twitch Chatbot Sub-card
old_twitch_subcard = """            <!-- 🤖 Twitch Chatbot Connection Sub-card -->
            <div style="margin-top:10px; padding:10px 12px; background:rgba(145, 70, 255, 0.08); border:1px solid rgba(145, 70, 255, 0.25); border-radius:8px;">
              <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:12px; font-weight:700; color:#c084fc;">
                  <span>🤖</span> <span>Twitch Chatbot (ส่งแชท + ตอบคำสั่งอัตโนมัติ)</span>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                  <span id="twitchBotBadge" style="font-size:11px; padding:2px 8px; border-radius:10px; background:rgba(35, 165, 90, 0.18); color:#4ade80; border:1px solid rgba(35,165,90,0.4);">🟢 Bot เชื่อมต่อแล้ว (@Men9Bot)</span>
                  <button type="button" class="btn-topbar-action" style="height:22px; padding:0 8px; font-size:10.5px;" onclick="toggleTwitchBotAuth()">🔄 สลับบัญชี Bot</button>
                  <button type="button" class="btn-topbar-action" style="height:22px; padding:0 8px; font-size:10.5px;" onclick="switchSettingsSection('chatbot')">⚙️ ตั้งค่า Bot</button>
                </div>
              </div>"""

new_twitch_subcard = """            <!-- 🤖 Twitch Chatbot Connection Sub-card -->
            <div style="margin-top:10px; padding:10px 12px; background:rgba(145, 70, 255, 0.08); border:1px solid rgba(145, 70, 255, 0.25); border-radius:8px;">
              <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:12px; font-weight:700; color:#c084fc; white-space:nowrap;">
                  <span>🤖</span> <span>Twitch Chatbot</span>
                  <span style="font-size:11px; color:#a855f7; font-weight:normal;">(ตอบแชทอัตโนมัติ)</span>
                </div>
                <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                  <span id="twitchBotBadge" style="font-size:11px; padding:2px 8px; border-radius:10px; background:rgba(35, 165, 90, 0.18); color:#4ade80; border:1px solid rgba(35,165,90,0.4); white-space:nowrap;">🟢 เชื่อมต่อแล้ว (@Men9Bot)</span>
                  <button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="สลับบัญชี Twitch Bot" onclick="toggleTwitchBotAuth()">🔄 สลับบัญชี</button>
                  <button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="ตั้งค่าคำสั่ง Twitch Bot" onclick="switchSettingsSection('chatbot')">⚙️ ตั้งค่า</button>
                </div>
              </div>"""

if old_twitch_subcard in html:
    html = html.replace(old_twitch_subcard, new_twitch_subcard)
    print("✓ Polished Twitch Chatbot Sub-card layout")
else:
    # Try regex replacement if whitespace differed
    pattern_twitch = r'<!-- 🤖 Twitch Chatbot Connection Sub-card -->.*?<div style="display:flex; flex-direction:column; gap:5px;">'
    replacement_twitch = new_twitch_subcard + '\n              <div style="display:flex; flex-direction:column; gap:5px;">'
    html = re.sub(pattern_twitch, replacement_twitch, html, count=1, flags=re.DOTALL)
    print("✓ Polished Twitch Chatbot Sub-card via regex")

# 1.3 Polish KICK Chatbot Sub-card
old_kick_subcard = """            <!-- 🤖 KICK Chatbot Connection Sub-card -->
            <div style="margin-top:10px; padding:10px 12px; background:rgba(83, 252, 24, 0.08); border:1px solid rgba(83, 252, 24, 0.25); border-radius:8px;">
              <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:12px; font-weight:700; color:#53fc18;">
                  <span>🤖</span> <span>KICK Chatbot (ส่งแชท + ข้อความแจ้งเตือน Live + Bot)</span>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                  <span id="kickBotBadge" style="font-size:11px; padding:2px 8px; border-radius:10px; background:rgba(83, 252, 24, 0.18); color:#53fc18; border:1px solid rgba(83,252,24,0.4);">🟢 Bot เชื่อมต่อแล้ว (@Men9Bot_Kick)</span>
                  <button type="button" class="btn-topbar-action" style="height:22px; padding:0 8px; font-size:10.5px;" onclick="toggleKickBotAuth()">🔄 สลับบัญชี Bot</button>
                  <button type="button" class="btn-topbar-action" style="height:22px; padding:0 8px; font-size:10.5px;" onclick="switchSettingsSection('chatbot')">⚙️ ตั้งค่า Bot</button>
                </div>
              </div>"""

new_kick_subcard = """            <!-- 🤖 KICK Chatbot Connection Sub-card -->
            <div style="margin-top:10px; padding:10px 12px; background:rgba(83, 252, 24, 0.08); border:1px solid rgba(83, 252, 24, 0.25); border-radius:8px;">
              <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:6px; font-size:12px; font-weight:700; color:#53fc18; white-space:nowrap;">
                  <span>🤖</span> <span>KICK Chatbot</span>
                  <span style="font-size:11px; color:#4ade80; font-weight:normal;">(ตอบแชทอัตโนมัติ)</span>
                </div>
                <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                  <span id="kickBotBadge" style="font-size:11px; padding:2px 8px; border-radius:10px; background:rgba(83, 252, 24, 0.18); color:#53fc18; border:1px solid rgba(83,252,24,0.4); white-space:nowrap;">🟢 เชื่อมต่อแล้ว (@Men9Bot_Kick)</span>
                  <button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="สลับบัญชี KICK Bot" onclick="toggleKickBotAuth()">🔄 สลับบัญชี</button>
                  <button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="ตั้งค่าคำสั่ง KICK Bot" onclick="switchSettingsSection('chatbot')">⚙️ ตั้งค่า</button>
                </div>
              </div>"""

if old_kick_subcard in html:
    html = html.replace(old_kick_subcard, new_kick_subcard)
    print("✓ Polished KICK Chatbot Sub-card layout")
else:
    pattern_kick = r'<!-- 🤖 KICK Chatbot Connection Sub-card -->.*?<div style="display:flex; flex-direction:column; gap:5px;">'
    replacement_kick = new_kick_subcard + '\n              <div style="display:flex; flex-direction:column; gap:5px;">'
    html = re.sub(pattern_kick, replacement_kick, html, count=1, flags=re.DOTALL)
    print("✓ Polished KICK Chatbot Sub-card via regex")

# 1.4 In sec-chatbot, shorten button texts so they fit in 2-column cards
html = html.replace('<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px;" onclick="toggleTwitchBotAuth()">🔄 สลับบัญชี Bot</button>', '<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="สลับบัญชี Twitch Bot" onclick="toggleTwitchBotAuth()">🔄 สลับบัญชี</button>')
html = html.replace('<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px;" onclick="showToast(\'🧪 ทดสอบส่งแชทผ่าน Twitch Bot สำเร็จ\')">💬 ทดสอบแชท</button>', '<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="ทดสอบส่งแชทผ่าน Twitch Bot" onclick="showToast(\'🧪 ทดสอบส่งแชทผ่าน Twitch Bot สำเร็จ\')">💬 ทดสอบ</button>')

html = html.replace('<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px;" onclick="toggleKickBotAuth()">🔄 สลับบัญชี Bot</button>', '<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="สลับบัญชี KICK Bot" onclick="toggleKickBotAuth()">🔄 สลับบัญชี</button>')
html = html.replace('<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px;" onclick="showToast(\'🧪 ทดสอบส่งแชทผ่าน KICK Bot สำเร็จ\')">💬 ทดสอบแชท</button>', '<button type="button" class="btn-topbar-action" style="height:24px; padding:0 8px; font-size:11px; white-space:nowrap;" title="ทดสอบส่งแชทผ่าน KICK Bot" onclick="showToast(\'🧪 ทดสอบส่งแชทผ่าน KICK Bot สำเร็จ\')">💬 ทดสอบ</button>')

# 1.5 In sec-networking, shorten long button text
html = html.replace('⚡ ทดสอบความเร็วและทดสอบ TTS Server', '⚡ ทดสอบความเร็ว & TTS Server')

# 1.6 In sec-defender, shorten long button text
html = html.replace('⚡ เพิ่มข้อยกเว้นอัตโนมัติ (1-Click Exclusion)', '⚡ เพิ่มข้อยกเว้นอัตโนมัติ (1 คลิก)')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ Updated src/index.html settings layout")

# ==============================================================================
# 2. UPDATE styles.css FOR SETTINGS WINDOW
# ==============================================================================
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

settings_fix_css = """
/* ==============================================================================
   SETTINGS WINDOW COMPACT & ANTI-OVERFLOW BUTTON RULES
   ============================================================================== */
#win-settings button,
#win-settings .btn-topbar-action,
#win-settings .plat-quick-pill,
#win-settings span[id$="Badge"] {
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  box-sizing: border-box !important;
  line-height: 1.2 !important;
}

#win-settings .btn-topbar-action {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
}

#win-settings .settings-section-pane {
  overflow-y: auto !important;
  overflow-x: hidden !important;
}

#win-settings .section-card {
  overflow: visible !important;
}
"""

if 'SETTINGS WINDOW COMPACT & ANTI-OVERFLOW BUTTON RULES' not in css:
    css += settings_fix_css
    print("✓ Added settings window anti-overflow rules to styles.css")

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("All settings improvements applied successfully!")
