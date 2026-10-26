// Broadcast Playroom 3 - Studio Controller with Discord Server Rail & Modals

function openModal(name) {
  const modal = document.getElementById(`modal-${name}`);
  if (!modal) return;
  modal.classList.add('active');
}

function closeModal(name) {
  const modal = document.getElementById(`modal-${name}`);
  if (!modal) return;
  modal.classList.remove('active');
}

function switchModalTab(btn, tabName) {
  const parentModal = btn.closest('.modal-window');
  if (!parentModal) return;

  parentModal.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  parentModal.querySelectorAll('.modal-tab-pane').forEach(pane => {
    pane.style.display = 'none';
  });

  const targetPane = document.getElementById(`tab-${tabName}`);
  if (targetPane) {
    targetPane.style.display = 'block';
  }
}

function selectCardOption(card) {
  const parentGrid = card.closest('.modal-grid-3') || card.parentElement;
  parentGrid.querySelectorAll('.modal-mode-card').forEach(c => c.classList.remove('active'));
  card.classList.add('active');
  const title = card.querySelector('strong')?.textContent || '';
  showToast(`เลือกรูปแบบ: ${title}`);
}

let _isTestDrawRunning = false;
function toggleTestDraw(btn) {
  _isTestDrawRunning = !_isTestDrawRunning;
  if (_isTestDrawRunning) {
    btn.textContent = '⏹️ ปิดการทดสอบหน้าสุ่ม';
    btn.style.backgroundColor = 'var(--dc-red)';
    btn.style.color = 'white';
    showToast('👁️ เปิดทดสอบหน้าจอสุ่มบน OBS เรียบร้อย');
  } else {
    btn.textContent = '👁️ เปิด/ปิด ทดสอบหน้าสุ่ม';
    btn.style.backgroundColor = 'var(--dc-blurple)';
    btn.style.color = 'white';
    showToast('⏹️ ปิดการทดสอบหน้าสุ่มบนจอ OBS แล้ว');
  }
}

function selectRailBtn(btn, toastMsg) {
  document.querySelectorAll('.rail-icon-btn').forEach(b => {
    if (!b.classList.contains('toggled-on')) {
      b.classList.remove('active');
    }
  });
  btn.classList.add('active');

  if (toastMsg) {
    showToast(toastMsg);
  } else {
    const title = btn.getAttribute('title') || 'เมนู';
    showToast(`📂 ${title}`);
  }
}

function toggleSystemMsg(btn) {
  btn.classList.toggle('toggled-on');
  const isOn = btn.classList.contains('toggled-on');
  showToast(isOn ? '🔔 แสดงสถานะระบบ (✅/⚪/⚠️) ในแชท' : '🔕 ซ่อนสถานะระบบในแชท');
}

function toggleCodeMute(btn) {
  btn.classList.toggle('toggled-on');
  const isOn = btn.classList.contains('toggled-on');
  showToast(isOn ? '🎟️ ปิดเสียงอ่านโค้ดลับ (Secret Code Muted)' : '🎟️ เปิดเสียงอ่านโค้ดลับตามปกติ');
}

let _chatFontSize = 13.5;
function adjustFontSize(delta) {
  _chatFontSize = Math.max(10, Math.min(22, _chatFontSize + delta));
  document.querySelectorAll('.chat-body-msg').forEach(el => {
    el.style.fontSize = `${_chatFontSize}px`;
  });
  showToast(`🔤 ขนาดฟอนต์แชท: ${_chatFontSize}px`);
}

function toggleMasterTts() {
  const btn = document.getElementById('btnMasterTts');
  if (!btn) return;

  const isOff = btn.classList.contains('off');
  if (isOff) {
    btn.classList.remove('off');
    btn.textContent = '🔊 อ่านแชท: เปิด';
    showToast('🔊 เปิดระบบอ่านออกเสียงแชท (Master TTS)');
  } else {
    btn.classList.add('off');
    btn.textContent = '🔇 อ่านแชท: ปิด';
    showToast('🔇 ปิดเสียงอ่านแชทชั่วคราว');
  }
}

function togglePlat(btn, dotId, platName) {
  const dot = document.getElementById(dotId);
  const isConnected = btn.classList.contains('connected');

  if (isConnected) {
    btn.classList.remove('connected');
    btn.textContent = 'เชื่อมต่อ';
    if (dot) dot.classList.remove('connected');
    showToast(`🛑 ตัดการเชื่อมต่อ ${platName} แล้ว`);
  } else {
    btn.classList.add('connected');
    btn.textContent = 'ตัดการเชื่อมต่อ';
    if (dot) dot.classList.add('connected');
    showToast(`⚡ เชื่อมต่อ ${platName} สำเร็จ! กำลังดึงแชทสด...`);
  }
}

function toggleEventsPanel() {
  const eventsCol = document.getElementById('eventsCol');
  const btn = document.getElementById('btnEventsToggle');
  if (!eventsCol) return;

  eventsCol.classList.toggle('collapsed');
  const isOpen = !eventsCol.classList.contains('collapsed');

  if (btn) {
    if (isOpen) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  }

  showToast(isOpen ? '⚡ เปิดแถบแสดงกิจกรรมสด (Event List)' : '🔒 ปิดแถบแสดงกิจกรรม');
}

function sendChat() {
  const input = document.getElementById('txtChatInput');
  const chatList = document.getElementById('chatList');

  if (!input || !chatList || !input.value.trim()) return;

  const msg = input.value.trim();
  input.value = '';

  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

  const row = document.createElement('div');
  row.className = 'chat-row';
  row.innerHTML = `
    <div class="chat-avatar" style="color: #5865f2;">👤</div>
    <div class="chat-text-area">
      <div class="chat-user-line">
        <span class="chat-username" style="color: #7983f5;">คุณ (สตรีมเมอร์)</span>
        <span class="chat-timestamp">${timeStr}</span>
      </div>
      <div class="chat-body-msg" style="font-size: ${_chatFontSize}px;">${escapeHtml(msg)}</div>
    </div>
  `;

  chatList.appendChild(row);
  chatList.scrollTop = chatList.scrollHeight;
  showToast('💬 ส่งข้อความแชทสดแล้ว');
}

function clearChat() {
  const chatList = document.getElementById('chatList');
  if (chatList) {
    chatList.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--dc-text-dim); font-size: 13px;">(ล้างประวัติแชทเรียบร้อยแล้ว)</div>';
  }
  showToast('🧹 ล้างรายการแชทสดเรียบร้อยแล้ว');
}

function copyObsUrl() {
  const url = 'http://127.0.0.1:8080/composer.html';
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).catch(() => {});
  }
  showToast('📋 คัดลอกลิงก์ OBS สำเร็จแล้ว!');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  const text = document.getElementById('toastText');
  if (!toast || !text) return;

  text.textContent = msg;
  toast.classList.add('show');

  if (window._toastTimer) clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 2200);
}

// Close modal on Escape
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.active').forEach(m => m.classList.remove('active'));
  }
});

// Global functions for inline HTML event handlers
window.openModal = openModal;
window.closeModal = closeModal;
window.switchModalTab = switchModalTab;
window.selectCardOption = selectCardOption;
window.toggleTestDraw = toggleTestDraw;
window.selectRailBtn = selectRailBtn;
window.toggleSystemMsg = toggleSystemMsg;
window.toggleCodeMute = toggleCodeMute;
window.adjustFontSize = adjustFontSize;
window.toggleMasterTts = toggleMasterTts;
window.togglePlat = togglePlat;
window.toggleEventsPanel = toggleEventsPanel;
window.sendChat = sendChat;
window.clearChat = clearChat;
window.copyObsUrl = copyObsUrl;
window.showToast = showToast;
