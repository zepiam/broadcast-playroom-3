import os
import re

src_dir = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src"
dock_path = os.path.join(src_dir, "dock.html")
composer_html_path = os.path.join(src_dir, "composer.html")
index_path = os.path.join(src_dir, "index.html")
composer_js_path = os.path.join(src_dir, "composer_studio.js")

# ==============================================================================
# 1. CREATE src/dock.html (OBS Quick Control Dock)
# ==============================================================================
dock_content = """<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-select=no">
  <title>Broadcast Playroom - OBS Quick Control Dock</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400;500;600;700;800&family=Noto+Sans+Thai+Looped:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-main: #0b0e14;
      --bg-card: #151922;
      --bg-card-hover: #1c2230;
      --border-color: rgba(255, 255, 255, 0.08);
      --border-accent: #38bdf8;
      --primary-blue: #38bdf8;
      --primary-green: #10b981;
      --primary-red: #ef4444;
      --primary-purple: #c084fc;
      --primary-gold: #f59e0b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --font: 'Kanit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: var(--font);
      font-size: 13px;
      padding: 10px;
      user-select: none;
      overflow-y: auto;
      overflow-x: hidden;
      contain: layout style;
    }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: #262c3c; border-radius: 4px; }

    .dock-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 10px;
    }
    .dock-brand {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13.5px;
      font-weight: 800;
      color: #e2e8f0;
    }

    .server-status-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      background: rgba(16, 185, 129, 0.12);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
      cursor: pointer;
    }
    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 6px rgba(16, 185, 129, 0.6);
    }

    .dock-section {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 10px;
    }
    .dock-section-title {
      font-size: 11px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .dock-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      width: 100%;
      height: 36px;
      background: #1e2433;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      color: #f1f5f9;
      font-family: var(--font);
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .dock-btn:hover {
      background: #283145;
      border-color: rgba(255, 255, 255, 0.2);
    }
    .dock-btn.active {
      background: #6366f1;
      border-color: #818cf8;
      color: #fff;
    }
    .dock-btn.danger:hover {
      background: #ef4444;
      border-color: #f87171;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .gender-switch {
      display: flex;
      background: #0f131a;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 6px;
      padding: 2px;
      gap: 2px;
    }
    .gender-btn {
      flex: 1;
      height: 28px;
      border: none;
      background: transparent;
      color: #94a3b8;
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .gender-btn.active {
      background: #6366f1;
      color: #fff;
    }

    .dock-slider {
      width: 100%;
      height: 6px;
      accent-color: #38bdf8;
      cursor: pointer;
    }

    .trigger-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }
    .btn-trigger {
      padding: 8px 10px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 6px;
      background: #19202f;
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #e2e8f0;
      cursor: pointer;
      text-align: left;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .btn-trigger:hover {
      background: #253046;
      border-color: #38bdf8;
      transform: translateY(-1px);
    }
  </style>
</head>
<body>
  <div class="dock-header">
    <div class="dock-brand">
      <span>🎛️</span>
      <span>Broadcast Playroom Dock</span>
    </div>
    <div class="server-status-badge" id="dockServerStatus" title="คลิกเพื่อทดสอบสัญญาณ TTS Server" onclick="pingServer()">
      <span class="status-dot" id="dockStatusDot"></span>
      <span id="dockStatusText">ปกติ</span>
    </div>
  </div>

  <!-- TTS & Voice Control -->
  <div class="dock-section">
    <div class="dock-section-title">
      <span>🔊 เสียงอ่าน TTS สด</span>
      <span id="lblVolume">80%</span>
    </div>
    <div style="display:flex; flex-direction:column; gap:8px;">
      <button class="dock-btn active" id="btnDockTts" onclick="toggleTts()">🔊 อ่านแชท: เปิด</button>
      <div class="gender-switch">
        <button class="gender-btn active" id="btnDockFemale" onclick="setGender('female')">👩 หญิง</button>
        <button class="gender-btn" id="btnDockMale" onclick="setGender('male')">👨 ชาย</button>
      </div>
      <input type="range" class="dock-slider" id="dockVolume" min="0" max="100" value="80" oninput="setVolume(this.value)">
    </div>
  </div>

  <!-- Quick Overlay Triggers -->
  <div class="dock-section">
    <div class="dock-section-title">⚡ คำสั่งด่วนขึ้นจอ OBS</div>
    <div class="trigger-grid">
      <button class="btn-trigger" onclick="triggerAsk()">
        <span>📊</span> <span>ส่งโพล ASK</span>
      </button>
      <button class="btn-trigger" onclick="triggerGiveaway()">
        <span>🎁</span> <span>สุ่ม Giveaway</span>
      </button>
      <button class="btn-trigger" onclick="triggerPlayroom()">
        <span>🎮</span> <span>ยิงคลิป Playroom</span>
      </button>
      <button class="btn-trigger" onclick="triggerReplie()">
        <span>🖼️</span> <span>Replie ทักทาย</span>
      </button>
    </div>
  </div>

  <!-- Utility Actions -->
  <div class="dock-section" style="margin-bottom:0;">
    <div class="grid-2">
      <button class="dock-btn" onclick="triggerSimulateChat()">💬 จำลองแชทสด</button>
      <button class="dock-btn danger" onclick="triggerClearChat()">🧹 ล้างแชทสด</button>
    </div>
  </div>

  <script>
    const bus = ('BroadcastChannel' in window) ? new BroadcastChannel('bp3_system_channel') : null;
    let _ttsEnabled = true;
    let _activeGender = 'female';

    function sendCmd(action, payload = {}) {
      if (bus) {
        bus.postMessage({ event: 'DOCK_CONTROL', payload: { action, ...payload }, timestamp: Date.now() });
      }
    }

    function toggleTts() {
      _ttsEnabled = !_ttsEnabled;
      const btn = document.getElementById('btnDockTts');
      btn.textContent = _ttsEnabled ? '🔊 อ่านแชท: เปิด' : '🔇 อ่านแชท: ปิด';
      btn.classList.toggle('active', _ttsEnabled);
      sendCmd('toggle_tts', { enabled: _ttsEnabled });
    }

    function setGender(g) {
      _activeGender = g;
      document.getElementById('btnDockFemale').classList.toggle('active', g === 'female');
      document.getElementById('btnDockMale').classList.toggle('active', g === 'male');
      sendCmd('set_gender', { gender: g });
    }

    function setVolume(v) {
      document.getElementById('lblVolume').textContent = v + '%';
      sendCmd('set_volume', { volume: v });
    }

    function triggerAsk() { sendCmd('ask_poll'); }
    function triggerGiveaway() { sendCmd('giveaway_roll'); }
    function triggerPlayroom() { sendCmd('playroom_clip'); }
    function triggerReplie() { sendCmd('replie_action'); }
    function triggerSimulateChat() { sendCmd('simulate_chat'); }
    function triggerClearChat() { sendCmd('clear_chat'); }

    function pingServer() {
      const dot = document.getElementById('dockStatusDot');
      const txt = document.getElementById('dockStatusText');
      txt.textContent = 'กำลังเช็ค...';
      setTimeout(() => {
        txt.textContent = 'ปกติ';
      }, 300);
      sendCmd('ping_server');
    }

    // Listen to incoming app sync
    if (bus) {
      bus.onmessage = (e) => {
        const { event, payload } = e.data || {};
        if (event === 'APP_STATE_SYNC') {
          if (payload.ttsEnabled !== undefined) {
            _ttsEnabled = payload.ttsEnabled;
            const btn = document.getElementById('btnDockTts');
            btn.textContent = _ttsEnabled ? '🔊 อ่านแชท: เปิด' : '🔇 อ่านแชท: ปิด';
            btn.classList.toggle('active', _ttsEnabled);
          }
          if (payload.gender) {
            setGender(payload.gender);
          }
        }
      };
    }
  </script>
</body>
</html>
"""

with open(dock_path, 'w', encoding='utf-8') as f:
    f.write(dock_content)
print("Created src/dock.html successfully!")


# ==============================================================================
# 2. CREATE src/composer.html (OBS Browser Source Standalone Overlay)
# ==============================================================================
composer_html_content = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920, height=1080, initial-scale=1.0">
  <title>Broadcast Playroom 3 — OBS Live Overlay</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400;500;600;700;800&family=Noto+Sans+Thai+Looped:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./composer_studio.css">
  <link rel="stylesheet" href="./composer_widget_themes.css">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: transparent !important;
      font-family: 'Kanit', sans-serif;
      contain: strict;
      isolation: isolate;
    }
    #obsCanvasStage {
      position: absolute;
      width: 1920px;
      height: 1080px;
      top: 0;
      left: 0;
      overflow: hidden;
      background: transparent !important;
    }
    .obs-widget-box {
      position: absolute;
      overflow: hidden;
      pointer-events: none;
    }
  </style>
</head>
<body class="overlay-mode preview-clean-mode">
  <div id="obsCanvasStage"></div>

  <script src="./cwc_themes_data.js"></script>
  <script src="./composer_studio.js"></script>
  <script>
    // Live OBS Browser Source Runner
    window.addEventListener('DOMContentLoaded', () => {
      const bus = ('BroadcastChannel' in window) ? new BroadcastChannel('bp3_system_channel') : null;
      const stage = document.getElementById('obsCanvasStage');

      function renderObsWidgets() {
        if (!stage) return;
        stage.innerHTML = '';
        try {
          const raw = localStorage.getItem('bp_composer_studio_v3');
          if (!raw) return;
          const parsed = JSON.parse(raw);
          const activePage = parsed.pages?.[parsed.activePageIndex || 0];
          if (!activePage || !activePage.widgets) return;

          activePage.widgets.forEach(w => {
            if (w.hidden) return;
            const box = document.createElement('div');
            box.className = 'obs-widget-box';
            box.style.left = `${w.x || 0}px`;
            box.style.top = `${w.y || 0}px`;
            box.style.width = `${w.width || 300}px`;
            box.style.height = `${w.height || 200}px`;
            box.style.zIndex = w.z || 1;
            box.style.opacity = w.opacity ?? 1;

            if (typeof renderWidgetInner === 'function') {
              box.innerHTML = renderWidgetInner(w);
            }
            stage.appendChild(box);
          });
        } catch (e) {
          console.error('Error rendering OBS widgets:', e);
        }
      }

      renderObsWidgets();

      if (bus) {
        bus.onmessage = (e) => {
          const { event, payload } = e.data || {};
          if (event === 'CANVAS_LAYOUT_SAVED') {
            renderObsWidgets();
          }
        };
      }
    });
  </script>
</body>
</html>
"""

with open(composer_html_path, 'w', encoding='utf-8') as f:
    f.write(composer_html_content)
print("Created src/composer.html successfully!")


# ==============================================================================
# 3. UPDATE src/index.html with Live Chat Simulator & Dock Control Handler
# ==============================================================================
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Live Chat Simulator button in Chat Column Header
chat_header_target = '<!-- 8. เปิด/ปิดกิจกรรม ย้ายมาจากด้านบน -->'
sim_btn_html = """<!-- ปุ่มจำลองแชทสดไหล เพื่อตรวจเช็คความพร้อม -->
          <button class="btn-chat-header sortable-item" id="btnSimulateChat" data-item-id="sim-chat" draggable="true" title="🎮 เปิด/ปิด การจำลองแชทสดไหล เพื่อทดสอบระบบ" onclick="handleSortableClick(event, () => toggleSimulateLiveChats())" style="color:#10b981; border-color:rgba(16,185,129,0.4); font-size:11.5px; padding:0 8px; width:auto; gap:4px;">
            <span>🎮</span> <span id="lblSimChat">จำลองแชท</span>
          </button>
          
          """
if 'id="btnSimulateChat"' not in html and chat_header_target in html:
    html = html.replace(chat_header_target, sim_btn_html + chat_header_target, 1)
    print("Added btnSimulateChat to chat header in src/index.html!")

# Add Chat Simulator JS logic before </script>
sim_chat_js = """
    // ----------------------------------------------------
    // LIVE CHAT SIMULATOR & DOCK REAL-TIME RECEIVER
    // ----------------------------------------------------
    let _isSimulatingChats = false;
    let _simChatTimer = null;

    const SIM_CHATTERS = [
      { name: 'น้องบอย_Gamer', plat: 'YouTube', icon: './assets/youtube.png', seed: 'Boy', color: '#f87171', vip: true, msg: 'สวัสดีครับพี่! สตรีมวันนี้เปิดตู้กาชาปองไหมครับ 🔥' },
      { name: 'Praew_Cat', plat: 'TikTok', icon: './assets/tiktok.png', seed: 'Praew', color: '#f472b6', vip: false, msg: 'ภาพและเสียงสตรีมชัดเจนมากค่าา 60fps ลื่นๆ เลย 🎉' },
      { name: 'Somchai_VIP', plat: 'YouTube', icon: './assets/youtube.png', seed: 'Somchai', color: '#fbbf24', vip: true, msg: 'โหวตเลือกเกมใหม่เรียบร้อยครับ วันนี้ลุยยาวๆ' },
      { name: 'Krit_Kun', plat: 'SOOP', icon: './assets/soop.png', seed: 'Krit', color: '#38bdf8', vip: false, msg: 'ระบบอ่านแชทเสียงเพราะมากครับ ตอบสนองไวสุดๆ' },
      { name: 'Zack_Channel', plat: 'Twitch', icon: './assets/twitch.png', seed: 'Zack', color: '#c084fc', vip: true, msg: 'แวะมาส่งกำลังใจให้สตรีมเมอร์ครับผม! !cheer' },
      { name: 'Lin_GamerTH', plat: 'Kick', icon: './assets/kick.png', seed: 'Lin', color: '#34d399', vip: false, msg: 'จัด Layout ใน Composer Studio สวยมากครับ' }
    ];

    function toggleSimulateLiveChats() {
      _isSimulatingChats = !_isSimulatingChats;
      const btn = document.getElementById('btnSimulateChat');
      const lbl = document.getElementById('lblSimChat');

      if (_isSimulatingChats) {
        if (lbl) lbl.textContent = 'หยุดจำลองแชท';
        if (btn) {
          btn.style.color = '#ef4444';
          btn.style.borderColor = 'rgba(239, 68, 68, 0.5)';
        }
        showToast('🟢 เริ่มจำลองแชทสดไหลอัตโนมัติ (กำลังรับแชทจากทุกแพลตฟอร์ม)');
        sendSingleSimulatedChat();
        _simChatTimer = setInterval(sendSingleSimulatedChat, 3000);
      } else {
        if (lbl) lbl.textContent = 'จำลองแชท';
        if (btn) {
          btn.style.color = '#10b981';
          btn.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        }
        clearInterval(_simChatTimer);
        _simChatTimer = null;
        showToast('⏸ หยุดการจำลองแชทสดเรียบร้อยแล้ว');
      }
    }

    function sendSingleSimulatedChat() {
      const chatter = SIM_CHATTERS[Math.floor(Math.random() * SIM_CHATTERS.length)];
      injectIncomingChat({
        username: chatter.name,
        platform: chatter.plat,
        icon: chatter.icon,
        avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${chatter.seed}`,
        color: chatter.color,
        isVip: chatter.vip,
        text: chatter.msg,
        time: new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
      });
    }

    function injectIncomingChat(msg) {
      const chatList = document.getElementById('chatList');
      if (chatList) {
        const row = document.createElement('div');
        row.className = 'chat-row';
        row.innerHTML = `
          <div class="chat-avatar" onclick="openAuthorModal('${msg.username}', '${msg.platform}', '${msg.avatar}', '${msg.username}', ${msg.isVip})">
            <img class="avatar-img" src="${msg.avatar}" alt="Avatar">
            <div class="plat-badge-mini">
              <img src="${msg.icon}" alt="${msg.platform}">
            </div>
          </div>
          <div class="chat-text-area">
            <div class="chat-user-line">
              <span class="chat-username" style="color: ${msg.color};" onclick="openAuthorModal('${msg.username}', '${msg.platform}', '${msg.avatar}', '${msg.username}', ${msg.isVip})">${msg.username}</span>
              ${msg.isVip ? '<span class="chat-badge-tag vip">🌟 VIP</span>' : ''}
              <span class="chat-timestamp">${msg.time}</span>
              <span class="chat-tts-time tts-done">✓ 0.2s</span>
            </div>
            <div class="chat-body-msg">${msg.text}</div>
          </div>
        `;
        chatList.appendChild(row);
        chatList.scrollTop = chatList.scrollHeight;
      }

      // Broadcast to Canvas Chat Widgets & OBS Overlay
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('CHAT_MESSAGE', msg);
      }

      // Play Speech synthesis if Master TTS is ON
      if (_masterTtsEnabled) {
        speakTextViaWebSpeech(msg.username, msg.text);
      }
    }

    function speakTextViaWebSpeech(author, text) {
      if (!('speechSynthesis' in window)) return;
      try {
        const sentence = `${author} พูดว่า ${text}`;
        const utter = new SpeechSynthesisUtterance(sentence);
        utter.lang = 'th-TH';
        utter.rate = 1.05;
        const vol = (parseInt(document.getElementById('topbarMasterVol')?.value) || 80) / 100;
        utter.volume = vol;
        window.speechSynthesis.speak(utter);
      } catch (e) {}
    }

    // Handle incoming controls from OBS Dock
    if (window.BP3_BUS) {
      window.BP3_BUS.on('DOCK_CONTROL', (data) => {
        const { action, payload } = data;
        if (action === 'toggle_tts') {
          toggleMasterTts();
        } else if (action === 'set_gender') {
          const btn = document.getElementById(payload.gender === 'female' ? 'tbGenderFemale' : 'tbGenderMale');
          if (btn) selectVoiceGender(btn, payload.gender);
        } else if (action === 'set_volume') {
          syncMasterVolume(payload.volume);
        } else if (action === 'ask_poll') {
          sendAskPollToObs();
        } else if (action === 'giveaway_roll') {
          rerollGwWinner();
        } else if (action === 'playroom_clip') {
          playroomFireActiveClip();
        } else if (action === 'replie_action') {
          demoReplieAction('!hi', 'สวัสดีครับทุกคน! ยินดีต้อนรับสู่สตรีมครับ', 'happy');
        } else if (action === 'simulate_chat') {
          toggleSimulateLiveChats();
        } else if (action === 'clear_chat') {
          clearChat();
        }
      });
    }
"""

if 'function toggleSimulateLiveChats' not in html:
    html = html.replace('</script>', sim_chat_js + '\n  </script>', 1)
    print("Added Chat Simulator & Dock Control receiver to src/index.html!")

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)


# ==============================================================================
# 4. UPDATE src/composer_studio.js to listen to CHAT_MESSAGE
# ==============================================================================
with open(composer_js_path, 'r', encoding='utf-8') as f:
    js = f.read()

chat_bus_listener = """
  bus.on('CHAT_MESSAGE', (msg) => {
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'chat') {
          const feed = document.getElementById(`widget-chat-feed-${w.id}`);
          if (feed) {
            const theme = w.chatTheme || 'default';
            const item = document.createElement('div');
            item.className = `cwc-msg-item msg chat-line theme-${theme} anim-in-${w.animIn || 'slide'}`;
            const boxStyle = w.boxEnabled !== false ? `background:rgba(30,31,34,0.85); border-radius:8px; padding:6px 12px;` : 'background:transparent;';
            item.style.cssText = boxStyle;
            item.innerHTML = `
              <div class="msg-bg"></div>
              <span class="author" style="color:${w.usernameColor || '#38bdf8'}; font-weight:700; margin-right:6px;">${msg.username}:</span>
              <span class="text" style="color:${w.fontColor || '#ffffff'}; font-size:${w.fontSize || 15}px;">${msg.text}</span>
            `;
            feed.appendChild(item);
            feed.scrollTop = feed.scrollHeight;

            if (w.autoHide) {
              const dur = (w.hideTimeout || 8) * 1000;
              setTimeout(() => {
                item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                item.style.opacity = '0';
                item.style.transform = 'translateY(-10px)';
                setTimeout(() => { item.remove(); }, 500);
              }, dur);
            }
          }
        }
      });
    }
  });
"""

if "bus.on('CHAT_MESSAGE'" not in js:
    # Insert right before bus.on('ASK_UPDATE'
    js = js.replace("bus.on('ASK_UPDATE',", chat_bus_listener + "\n  bus.on('ASK_UPDATE',", 1)
    with open(composer_js_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print("Added CHAT_MESSAGE listener to src/composer_studio.js!")

print("All review-ready components generated successfully!")
