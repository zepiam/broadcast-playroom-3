import os

dock_html_clean = """<!doctype html>
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
      font-size: 13px;
      font-weight: 700;
      color: #38bdf8;
    }

    .server-status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.35);
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
      color: #34d399;
      cursor: pointer;
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background-color: #10b981;
      box-shadow: 0 0 6px rgba(16, 185, 129, 0.8);
    }
    .status-dot.yellow { background-color: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.8); }
    .status-dot.red { background-color: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.8); }

    .dock-section {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 9px;
      margin-bottom: 10px;
    }

    .dock-section-title {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .dock-btn {
      width: 100%;
      padding: 7px 10px;
      border-radius: 6px;
      background: #1e2433;
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #f8fafc;
      font-family: var(--font);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .dock-btn:hover {
      background: #283145;
      border-color: #38bdf8;
    }
    .dock-btn.active {
      background: rgba(16, 185, 129, 0.18);
      border-color: #10b981;
      color: #34d399;
    }
    .dock-btn.danger {
      background: rgba(239, 68, 68, 0.15);
      border-color: rgba(239, 68, 68, 0.35);
      color: #fca5a5;
    }
    .dock-btn.danger:hover {
      background: rgba(239, 68, 68, 0.25);
      border-color: #ef4444;
    }

    .gender-switch {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      background: #0d1117;
      padding: 3px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .gender-btn {
      padding: 5px;
      background: transparent;
      border: none;
      border-radius: 4px;
      color: var(--text-muted);
      font-family: var(--font);
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
    }
    .gender-btn.active {
      background: #38bdf8;
      color: #04121e;
      font-weight: 700;
    }

    .dock-slider {
      width: 100%;
      height: 5px;
      border-radius: 4px;
      background: #252e42;
      outline: none;
      cursor: pointer;
      accent-color: #38bdf8;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .trigger-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }

    .btn-trigger {
      padding: 7px 8px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      background: #1a202c;
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
    <div class="server-status-badge" id="dockServerStatus" title="คลิกเพื่อทดสอบ Ping ไปยัง TTS Server" onclick="pingServer()">
      <span class="status-dot" id="dockStatusDot"></span>
      <span id="dockStatusText">ปกติ</span>
    </div>
  </div>

  <!-- TTS & Voice Control -->
  <div class="dock-section">
    <div class="dock-section-title">
      <span>🔊 เสียงอ่าน TTS หลัก</span>
      <span id="lblVolume">80%</span>
    </div>
    <div style="display:flex; flex-direction:column; gap:8px;">
      <button class="dock-btn active" id="btnDockTts" onclick="toggleTts()">🔊 เสียงหลัก: เปิดอยู่</button>
      <div class="gender-switch">
        <button class="gender-btn active" id="btnDockFemale" onclick="setGender('female')">👩 หญิง</button>
        <button class="gender-btn" id="btnDockMale" onclick="setGender('male')">👨 ชาย</button>
      </div>
      <input type="range" class="dock-slider" id="dockVolume" min="0" max="100" value="80" oninput="setVolume(this.value)">
    </div>
  </div>

  <!-- Quick Overlay Triggers -->
  <div class="dock-section">
    <div class="dock-section-title">⚡ สั่งแสดงผลบน OBS ทันที</div>
    <div class="trigger-grid">
      <button class="btn-trigger" data-action="ask_start" onclick="triggerAsk()">
        <span>📊</span> <span>โพลสำรวจ ASK</span>
      </button>
      <button class="btn-trigger" data-action="giveaway_roll" onclick="triggerGiveaway()">
        <span>🎁</span> <span>สุ่มแจก Giveaway</span>
      </button>
      <button class="btn-trigger" data-action="playroom_clip" onclick="triggerPlayroom()">
        <span>🎬</span> <span>คลิปละคร Playroom</span>
      </button>
      <button class="btn-trigger" data-action="replie_bubble" onclick="triggerReplie()">
        <span>💬</span> <span>Replie ข้อความโต้ตอบ</span>
      </button>
    </div>
  </div>

  <!-- Utility Actions -->
  <div class="dock-section" style="margin-bottom:0;">
    <div class="grid-2">
      <button class="dock-btn" onclick="triggerSimulateChat()">🎮 จำลองแชท</button>
      <button class="dock-btn danger" onclick="triggerClearChat()">🗑️ ล้างแชท</button>
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
      try {
        localStorage.setItem('bp3_dock_cmd', JSON.stringify({ action, ...payload, t: Date.now() }));
      } catch(e){}
    }

    function toggleTts() {
      _ttsEnabled = !_ttsEnabled;
      const btn = document.getElementById('btnDockTts');
      if (btn) {
        if (_ttsEnabled) {
          btn.className = 'dock-btn active';
          btn.innerHTML = '🔊 เสียงหลัก: เปิดอยู่';
        } else {
          btn.className = 'dock-btn danger';
          btn.innerHTML = '🔇 เสียงหลัก: ปิดอยู่';
        }
      }
      sendCmd('set_master_tts', { enabled: _ttsEnabled });
    }

    function setGender(g) {
      _activeGender = g;
      const bF = document.getElementById('btnDockFemale');
      const bM = document.getElementById('btnDockMale');
      if (bF && bM) {
        bF.classList.toggle('active', g === 'female');
        bM.classList.toggle('active', g === 'male');
      }
      sendCmd('set_gender', { gender: g });
    }

    function setVolume(v) {
      document.getElementById('lblVolume').textContent = v + '%';
      sendCmd('set_volume', { volume: parseInt(v, 10) });
    }

    function triggerAsk() {
      sendCmd('trigger_ask', { question: 'คุณชอบตัวละครไหนมากที่สุด?' });
    }

    function triggerGiveaway() {
      sendCmd('trigger_giveaway', { prize: 'บัตรกำนัล 500 บาท' });
    }

    function triggerPlayroom() {
      sendCmd('trigger_playroom', { title: 'ฉากเปิดละคร Playroom' });
    }

    function triggerReplie() {
      sendCmd('trigger_replie', { text: 'ยินดีต้อนรับเข้าสู่การถ่ายทอดสดครับ!' });
    }

    function triggerSimulateChat() {
      sendCmd('simulate_chat');
    }

    function triggerClearChat() {
      sendCmd('clear_chat');
    }

    function pingServer() {
      const dot = document.getElementById('dockStatusDot');
      const txt = document.getElementById('dockStatusText');
      if (txt) txt.textContent = 'เช็ค...';
      const t0 = performance.now();
      setTimeout(() => {
        const ms = Math.round(performance.now() - t0 + 20);
        if (txt) txt.textContent = `${ms}ms`;
        if (dot) dot.className = 'status-dot';
      }, 200);
    }
  </script>
</body>
</html>
"""

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/dock.html', 'w', encoding='utf-8') as f:
    f.write(dock_html_clean)

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/dock.html', 'w', encoding='utf-8') as f:
    f.write(dock_html_clean)

print("Updated src/dock.html and dist/dock.html with clean UTF-8!")
