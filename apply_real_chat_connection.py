import sys
import re
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# 1. UPDATE launch_dev.py
# ==============================================================================
dev_py_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/launch_dev.py'
with open(dev_py_path, 'r', encoding='utf-8') as f:
    dev_py = f.read()

# Add imports for api handling
new_handler = """import urllib.parse
from chat_bridge import chat_bridge

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith('/api/'):
            self.handle_api(parsed)
            return
        super().do_GET()

    def handle_api(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        path = parsed.path
        
        response_data = {}
        if path == '/api/connect':
            platform = qs.get('platform', [''])[0]
            target = qs.get('target', [''])[0]
            response_data = chat_bridge.connect(platform, target)
        elif path == '/api/disconnect':
            platform = qs.get('platform', [''])[0]
            response_data = chat_bridge.disconnect(platform)
        elif path == '/api/status':
            response_data = chat_bridge.get_status()
        elif path == '/api/messages':
            last_id = int(qs.get('last_id', [0])[0])
            response_data = {'messages': chat_bridge.get_messages(last_id)}
        else:
            response_data = {'error': 'Unknown endpoint'}

        payload = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(payload)
"""

# Replace QuietHandler class in launch_dev.py
pattern_handler = r'class QuietHandler\(SimpleHTTPRequestHandler\):.*?def is_port_in_use'
dev_py = re.sub(pattern_handler, new_handler + '\ndef is_port_in_use', dev_py, flags=re.DOTALL)

with open(dev_py_path, 'w', encoding='utf-8') as f:
    f.write(dev_py)
print("✓ Updated launch_dev.py with real chat API endpoints (/api/connect, /api/disconnect, /api/status, /api/messages)!")


# ==============================================================================
# 2. UPDATE src/index.html (Remove demo mock messages & connect real API)
# ==============================================================================
html_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace demo chats inside chatList with clean empty state placeholder
pattern_chatlist = r'<div class="chat-items-list" id="chatList">.*?</div>\s*<!-- \.chat-panel-input'
new_chatlist = """<div class="chat-items-list" id="chatList">
        <!-- สถานะว่างเมื่อเริ่มใช้งานจริง -->
        <div id="chatEmptyState" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; min-height:280px; color:#949ba4; gap:12px; padding:30px; text-align:center;">
          <span style="font-size:38px; opacity:0.65;">💬</span>
          <div style="font-size:14px; font-weight:700; color:#e2e8f0;">พร้อมรับข้อความแชทสด</div>
          <div style="font-size:12px; color:#64748b; max-width:320px; line-height:1.5;">พิมพ์ชื่อแชนแนลแล้วคลิกปุ่ม <strong>"เชื่อมต่อ"</strong> ที่แพลตฟอร์มด้านซ้าย หรือเปิดหน้าต่าง <strong>ตั้งค่า &gt; ช่องทางสตรีม</strong> เพื่อเริ่มดึงแชทจริง</div>
        </div>
      </div>

      <!-- .chat-panel-input"""

html = re.sub(pattern_chatlist, new_chatlist, html, count=1, flags=re.DOTALL)
print("✓ Removed all demo/mock chats from #chatList and added clean real-use empty state!")

# Update togglePlatformConnect to invoke real backend API
old_toggle_func = r'function togglePlatformConnect\(key, name\) \{.*?\n    \}'
new_toggle_func = """function getPlatformChannelTarget(key) {
      if (key === 'twitch') return document.getElementById('cfgTwitchChannel')?.value || 'men9ch';
      if (key === 'youtube') return document.getElementById('cfgYtChannel')?.value || '';
      if (key === 'kick') return document.getElementById('cfgKickChannel')?.value || '';
      if (key === 'tiktok') return document.getElementById('cfgTtChannel')?.value || '';
      if (key === 'soop') return document.getElementById('cfgSpChannel')?.value || '';
      if (key === 'mylive') return document.getElementById('cfgMlChannel')?.value || '';
      return '';
    }

    async function togglePlatformConnect(key, name) {
      const state = _platformStates[key];
      if (!state) return;

      const card = document.getElementById(`card-${key}`);
      const btn = document.getElementById(`btn-plat-${key}`);
      const statusLabel = document.getElementById(`status-${key}`);
      const goBtn = document.getElementById(`go-${key}`);
      const viewersEl = document.getElementById(`viewers-${key}`);

      if (!state.connected) {
        let target = getPlatformChannelTarget(key);
        if (!target) {
          const prompted = prompt(`กรุณาระบุชื่อแชนแนล, Video ID หรือ URL สำหรับ ${name}:`, '');
          if (!prompted) return;
          target = prompted.trim();
          const inp = document.getElementById(`cfg${key.charAt(0).toUpperCase() + key.slice(1)}Channel`);
          if (inp) inp.value = target;
        }

        if (card) {
          card.classList.add('connecting');
          card.classList.remove('connected');
        }
        if (btn) {
          btn.disabled = true;
          btn.textContent = 'กำลังเชื่อมต่อ...';
        }
        if (statusLabel) {
          statusLabel.textContent = 'กำลังเชื่อมต่อ...';
          statusLabel.className = 'plat-status-text connecting';
        }

        try {
          const res = await fetch(`/api/connect?platform=${encodeURIComponent(key)}&target=${encodeURIComponent(target)}`);
          const data = await res.json();
          if (data.success) {
            state.connected = true;
            if (card) {
              card.classList.remove('connecting');
              card.classList.add('connected');
            }
            if (btn) {
              btn.disabled = false;
              btn.textContent = 'หยุดเชื่อมต่อ';
              btn.className = 'btn-plat-connect connected';
            }
            if (statusLabel) {
              statusLabel.textContent = `✅ เชื่อมต่อแล้ว (#${target})`;
              statusLabel.className = 'plat-status-text connected';
            }
            if (goBtn) goBtn.style.display = 'inline-flex';
            if (viewersEl) viewersEl.style.display = 'inline-flex';
            showToast(`🟢 เชื่อมต่อ ${name} (${target}) สำเร็จ! กำลังรับแชทสด...`);
          } else {
            throw new Error(data.error || 'เชื่อมต่อล้มเหลว');
          }
        } catch (err) {
          if (card) card.classList.remove('connecting');
          if (btn) {
            btn.disabled = false;
            btn.textContent = 'เชื่อมต่อ';
            btn.className = 'btn-plat-connect';
          }
          if (statusLabel) {
            statusLabel.textContent = 'เชื่อมต่อไม่สำเร็จ';
            statusLabel.className = 'plat-status-text';
          }
          alert(`ไม่สามารถเชื่อมต่อ ${name}: ${err.message}`);
        }
      } else {
        // Disconnect
        try {
          await fetch(`/api/disconnect?platform=${encodeURIComponent(key)}`);
        } catch(e){}
        state.connected = false;
        if (card) card.classList.remove('connected');
        if (btn) {
          btn.textContent = 'เชื่อมต่อ';
          btn.className = 'btn-plat-connect';
        }
        if (statusLabel) {
          statusLabel.textContent = 'ยังไม่เชื่อมต่อ';
          statusLabel.className = 'plat-status-text';
        }
        if (goBtn) goBtn.style.display = 'none';
        if (viewersEl) viewersEl.style.display = 'none';
        showToast(`⚪ ยกเลิกการเชื่อมต่อ ${name} แล้ว`);
      }
    }"""

html = re.sub(old_toggle_func, new_toggle_func, html, count=1)

# Add real live chat poller logic
poller_code = """
    // ==============================================================================
    // REAL LIVE CHAT POLLER ENGINE
    // ==============================================================================
    let _lastLiveChatId = 0;
    let _realChatPollerTimer = null;

    function initRealChatPoller() {
      if (_realChatPollerTimer) clearInterval(_realChatPollerTimer);
      _realChatPollerTimer = setInterval(pollIncomingRealChats, 800);
      setInterval(pollPlatformStatuses, 4000);
    }

    async function pollIncomingRealChats() {
      try {
        const res = await fetch(`/api/messages?last_id=${_lastLiveChatId}`);
        if (!res.ok) return;
        const data = await res.json();
        if (data && data.messages && data.messages.length > 0) {
          const emptyState = document.getElementById('chatEmptyState');
          if (emptyState) emptyState.remove();

          for (const msg of data.messages) {
            if (msg.id > _lastLiveChatId) {
              _lastLiveChatId = msg.id;
              injectIncomingChat(msg);
            }
          }
        }
      } catch (e) {
        // Dev server not ready or polling paused
      }
    }

    async function pollPlatformStatuses() {
      try {
        const res = await fetch('/api/status');
        if (!res.ok) return;
        const statuses = await res.json();
        for (const [key, info] of Object.entries(statuses)) {
          const viewersEl = document.getElementById(`viewers-${key}`);
          if (viewersEl && info.viewers > 0) {
            viewersEl.textContent = `👥 ${info.viewers.toLocaleString()}`;
            viewersEl.style.display = 'inline-flex';
          }
        }
      } catch (e) {}
    }

    // Auto-start real chat poller on page load
    window.addEventListener('DOMContentLoaded', () => {
      initRealChatPoller();
    });
"""

if 'REAL LIVE CHAT POLLER ENGINE' not in html:
    html = html.replace('</script>\n  <script src="./cwc_themes_data.js">', poller_code + '\n  </script>\n  <script src="./cwc_themes_data.js">')
    print("✓ Added Real Live Chat Poller Engine into src/index.html")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Real chat connection engine configured successfully!")
