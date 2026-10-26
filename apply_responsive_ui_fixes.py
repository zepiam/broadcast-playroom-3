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

# Remove brand-badge ("Broadcast Playroom v3.0.0") and its following topbar-divider
brand_regex = r'<div class="brand-badge">.*?</div>\s*<div class="topbar-divider"></div>'
if re.search(brand_regex, html, re.DOTALL):
    html = re.sub(brand_regex, '', html, count=1)
    print("✓ Removed brand-badge (Broadcast Playroom v3.0.0)")
else:
    # Alternative pattern if already slightly modified
    brand_regex2 = r'<div class="brand-badge">.*?</div>'
    if re.search(brand_regex2, html, re.DOTALL):
        html = re.sub(brand_regex2, '', html, count=1)
        print("✓ Removed brand-badge")

# Wrap topbarServerStatus label with btn-label-text
html = html.replace('<span class="server-status-label">Server Status :</span>', '<span class="server-status-label btn-label-text">Server Status :</span>')

# Update gender switch buttons with btn-label-text
html = html.replace('<button class="topbar-gender-btn active" id="tbGenderFemale" onclick="selectVoiceGender(this, \'female\')">👩 หญิง</button>', '<button class="topbar-gender-btn active" id="tbGenderFemale" title="เสียงอ่าน: หญิง" onclick="selectVoiceGender(this, \'female\')"><span>👩</span><span class="btn-label-text"> หญิง</span></button>')
html = html.replace('<button class="topbar-gender-btn" id="tbGenderMale" onclick="selectVoiceGender(this, \'male\')">👨 ชาย</button>', '<button class="topbar-gender-btn" id="tbGenderMale" title="เสียงอ่าน: ชาย" onclick="selectVoiceGender(this, \'male\')"><span>👨</span><span class="btn-label-text"> ชาย</span></button>')

# Update btnMasterTts to have icon and btn-label-text
html = re.sub(
    r'<button class="tts-btn-toggle" id="btnMasterTts" onclick="toggleMasterTts\(\)">.*?</button>',
    r'<button class="tts-btn-toggle" id="btnMasterTts" title="สวิตช์เปิด/ปิด อ่านแชท Master TTS" onclick="toggleMasterTts()"><span class="tts-icon">🔊</span><span class="btn-label-text"> อ่านแชท: เปิด</span></button>',
    html,
    count=1
)

# Update topbar single buttons (translate, overlay, game-overlay, overlay-plus) with btn-label-text
html = html.replace('<span id="txtTranslateLabel">แปลภาษา</span>', '<span id="txtTranslateLabel" class="btn-label-text"> แปลภาษา</span>')
html = html.replace('<span>🖥️</span> <span>Overlay</span>', '<span>🖥️</span> <span class="btn-label-text">Overlay</span>')
html = html.replace('<span>🎮</span> <span>Game Overlay</span>', '<span>🎮</span> <span class="btn-label-text">Game Overlay</span>')
html = html.replace('<span>🪟</span> <span>Overlay+</span>', '<span>🪟</span> <span class="btn-label-text">Overlay+</span>')

# Update btnSimulateChat in chat header
html = re.sub(
    r'<button class="btn-chat-header sortable-item" id="btnSimulateChat"[^>]*>.*?</button>',
    r'''<button class="btn-chat-header sortable-item" id="btnSimulateChat" data-item-id="sim-chat" draggable="true" title="🎮 จำลองแชทสดไหลอัตโนมัติ" onclick="handleSortableClick(event, () => toggleSimulateLiveChats())" style="color:#10b981; border-color:rgba(16,185,129,0.4);">
            <span>🎮</span> <span id="lblSimChat" class="btn-label-text">จำลองแชท</span>
          </button>''',
    html,
    count=1,
    flags=re.DOTALL
)

# Update btnEventsToggle in chat header
html = re.sub(
    r'<button class="btn-chat-header sortable-item active" id="btnEventsToggle"[^>]*>.*?</button>',
    r'''<button class="btn-chat-header sortable-item active" id="btnEventsToggle" data-item-id="events" draggable="true" title="⚡ เปิด/ปิด แถบกิจกรรมสด" onclick="handleSortableClick(event, () => toggleEventsPanel())" style="color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);">
            <span>⚡</span> <span class="btn-label-text" style="font-size: 11px; margin-left: 2px;">Events</span>
          </button>''',
    html,
    count=1,
    flags=re.DOTALL
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("✓ Updated src/index.html with responsive label wrappers and removed brand-badge!")

# ==============================================================================
# 2. UPDATE styles.css
# ==============================================================================
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 2.1 Update .col-events width from 300px to 220px
css = re.sub(
    r'\.col-events\s*\{\s*width:\s*300px;',
    r'.col-events {\n  width: 220px;',
    css,
    count=1
)
print("✓ Reduced .col-events width from 300px to 220px")

# 2.2 Add complete responsive compact rules at the end of styles.css
responsive_css = """

/* ==============================================================================
   RESPONSIVE COMPACT UI RULES & ZERO TEXT-WRAPPING ON BUTTONS
   ============================================================================== */
.topbar,
.topbar-left,
.topbar-right,
.chat-panel-header,
.chat-header-actions,
.master-tts-wrap,
.topbar-gender-switch,
.topbar-server-status {
  white-space: nowrap !important;
}

.topbar-single-btn,
.tts-btn-toggle,
.topbar-gender-btn,
.btn-chat-header,
.chat-viewers-pill,
.chat-tts-latency-pill,
.split-btn-group,
.topbar-server-status {
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  line-height: 1.2 !important;
  box-sizing: border-box !important;
}

/* Ensure chat header action buttons don't wrap into multiple vertical lines */
.chat-header-actions.sortable-container {
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  scrollbar-width: none !important;
  -ms-overflow-style: none !important;
}
.chat-header-actions.sortable-container::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

/* Default compact styling for buttons inside chat header */
.chat-header-actions .btn-chat-header {
  min-width: 28px !important;
  height: 28px !important;
  padding: 0 6px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* Master TTS button styling */
.tts-btn-toggle {
  height: 28px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  padding: 0 10px !important;
}

/* Topbar single buttons */
.topbar-single-btn {
  height: 28px !important;
  padding: 0 8px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
}

/* Responsive collapse: Hide text labels when screen width is <= 1550px */
@media (max-width: 1550px) {
  .chat-header-actions .btn-label-text {
    display: none !important;
  }
}

@media (max-width: 1400px) {
  .topbar .btn-label-text,
  .server-status-label {
    display: none !important;
  }
  .topbar-gender-btn {
    padding: 2px 6px !important;
  }
  .topbar-slider {
    width: 50px !important;
  }
  .chat-panel-header {
    padding: 0 8px !important;
  }
}

@media (max-width: 1200px) {
  .chat-header-title h2 {
    font-size: 13px !important;
  }
  .chat-tts-latency-pill {
    padding: 2px 6px !important;
    font-size: 10px !important;
  }
}
"""

if 'RESPONSIVE COMPACT UI RULES & ZERO TEXT-WRAPPING' not in css:
    css += responsive_css
    print("✓ Added responsive compact rules to styles.css")

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("All UI improvements applied successfully!")
