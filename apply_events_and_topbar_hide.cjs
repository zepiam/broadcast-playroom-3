const fs = require('fs');
const path = require('path');

const cssPath = path.join(__dirname, 'src', 'styles.css');
const htmlPath = path.join(__dirname, 'src', 'index.html');

let css = fs.readFileSync(cssPath, 'utf8').replace(/\r\n/g, '\n');
let html = fs.readFileSync(htmlPath, 'utf8').replace(/\r\n/g, '\n');

// 1. Add Context Menu CSS
const menuCss = `
/* ── Custom Right-Click Context Menu (Topbar & Widgets) ── */
.custom-context-menu {
  position: fixed;
  background-color: #1e1f22;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  padding: 5px;
  min-width: 200px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.7);
  display: none;
  flex-direction: column;
  gap: 2px;
  z-index: 100000;
  user-select: none;
}

.custom-context-menu.show {
  display: flex;
}

.context-menu-header {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #949ba4;
  padding: 4px 8px 2px 8px;
  letter-spacing: 0.5px;
}

.context-menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 10px;
  font-size: 12.5px;
  color: #dbdee1;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-family);
  transition: all 0.12s ease;
  width: 100%;
}

.context-menu-item:hover {
  background-color: #2b2d31;
  color: #ffffff;
}

.context-menu-item.danger:hover {
  background-color: rgba(237, 66, 69, 0.15);
  color: #f87171;
}

.context-menu-divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.08);
  margin: 4px 0;
}
`;

css += menuCss;
fs.writeFileSync(cssPath, css, 'utf8');
console.log('styles.css updated with context menu styles.');

// 2. Remove Events button from Topbar Right
const oldTopbarRight = `    <div class="topbar-right sortable-container" id="topbarSortable" data-sort-key="bp3_sort_topbar">
      <!-- 1. แปลภาษา / อ่านทุกภาษา ▼ (สลับ 2 โหมดแท้จริงจาก V2) -->
      <div class="split-btn-group sortable-item" data-item-id="translate" draggable="true" title="คลิกเพื่อสลับ: แปลภาษา ↔ อ่านทุกภาษา (คลิกค้างเพื่อลากย้าย)">
        <button class="split-btn-main" id="btnTranslateToggle" style="color: #fbbf24; border-color: #f59e0b;" onclick="handleSortableClick(event, () => toggleTranslateMode())">
          <span id="txtTranslateIcon">🔄</span> <span id="txtTranslateLabel">แปลภาษา</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropTranslate', event)">▾</button>
        <div class="dropdown-menu" id="dropTranslate">
          <button class="dropdown-item" onclick="setTranslateMode('translate')">🔄 แปลภาษา (แปลเป็นไทยก่อนอ่าน)</button>
          <button class="dropdown-item" onclick="setTranslateMode('multilang')">🌐 อ่านทุกภาษา (อ่านสำเนียงต้นฉบับ)</button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('translate')">⚙️ ตั้งค่าการแปลภาษา...</button>
        </div>
      </div>

      <!-- 2. Overlay ▼ (Composer + copy URL) -->
      <div class="split-btn-group sortable-item" data-item-id="overlay" draggable="true" title="คลิกค้างเพื่อลากจัดลำดับ">
        <button class="split-btn-main active" onclick="handleSortableClick(event, () => copyObsUrl())" title="คลิกเพื่อคัดลอกลิงก์ Overlay OBS">
          <span>🖥️</span> <span>Overlay</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropOverlay', event)">▾</button>
        <div class="dropdown-menu" id="dropOverlay">
          <button class="dropdown-item" onclick="copyObsUrl()">📋 คัดลอก Overlay URL</button>
          <button class="dropdown-item" onclick="showToast('🎛️ เปิด Composer Canvas Studio ในเบราว์เซอร์')">🖥️ เปิด Composer Studio</button>
        </div>
      </div>

      <!-- 3. Game Overlay ▼ -->
      <div class="split-btn-group sortable-item" data-item-id="game-overlay" draggable="true" title="คลิกค้างเพื่อลากจัดลำดับ">
        <button class="split-btn-main" onclick="handleSortableClick(event, () => showToast('🎮 สลับการแสดง Game Overlay'))">
          <span>🎮</span> <span>Game Overlay</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropGameOverlay', event)">▾</button>
        <div class="dropdown-menu" id="dropGameOverlay">
          <button class="dropdown-item" onclick="showToast('👥 เปิด Viewer Overlay สำหรับแสดงคนดูเล่นเกม')">👥 Viewer Overlay</button>
          <button class="dropdown-item" onclick="showToast('👁️ ซ่อน/แสดงกรอบ Game Overlay (Edit Mode)')">👁️ ซ่อน/แสดงกรอบ</button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('obs')">⚙️ ตั้งค่า Game Overlay</button>
        </div>
      </div>

      <!-- 4. Overlay+ ▼ -->
      <div class="split-btn-group sortable-item" data-item-id="overlay-plus" draggable="true" title="คลิกค้างเพื่อลากจัดลำดับ">
        <button class="split-btn-main" onclick="handleSortableClick(event, () => showToast('🪟 สลับการแสดง Overlay+ (Custom Web URL)'))">
          <span>🪟</span> <span>Overlay+</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropOverlayPlus', event)">▾</button>
        <div class="dropdown-menu" id="dropOverlayPlus">
          <button class="dropdown-item" onclick="showToast('👁️ ซ่อน/แสดงกรอบ Overlay+ (Edit Mode)')">👁️ ซ่อน/แสดงกรอบ</button>
          <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('docks')">⚙️ ตั้งค่า Overlay+</button>
        </div>
      </div>

      <!-- 5. ปุ่มกดเปิด-ปิดแถบ Events ด้านขวา -->
      <div class="sortable-item" data-item-id="events" draggable="true" title="คลิกค้างเพื่อลากจัดลำดับ">
        <button class="btn-topbar-action events-btn" id="btnEventsToggle" onclick="handleSortableClick(event, () => toggleEventsPanel())">
          <span>⚡</span> <span>กิจกรรม (Events)</span>
        </button>
      </div>
    </div>`;

const newTopbarRight = `    <div class="topbar-right sortable-container" id="topbarSortable" data-sort-key="bp3_sort_topbar" title="คลิกขวาบนพื้นที่ว่างเพื่อเรียกคืนปุ่มที่ซ่อน">
      <!-- 1. แปลภาษา / อ่านทุกภาษา ▼ (สลับ 2 โหมด) -->
      <div class="split-btn-group sortable-item" id="topbar-item-translate" data-item-id="translate" draggable="true" title="คลิกสลับโหมด / คลิกขวาเพื่อซ่อนปุ่ม">
        <button class="split-btn-main" id="btnTranslateToggle" style="color: #fbbf24; border-color: #f59e0b;" onclick="handleSortableClick(event, () => toggleTranslateMode())">
          <span id="txtTranslateIcon">🔄</span> <span id="txtTranslateLabel">แปลภาษา</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropTranslate', event)">▾</button>
        <div class="dropdown-menu" id="dropTranslate">
          <button class="dropdown-item" onclick="setTranslateMode('translate')">🔄 แปลภาษา (แปลเป็นไทยก่อนอ่าน)</button>
          <button class="dropdown-item" onclick="setTranslateMode('multilang')">🌐 อ่านทุกภาษา (อ่านสำเนียงต้นฉบับ)</button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('translate')">⚙️ ตั้งค่าการแปลภาษา...</button>
        </div>
      </div>

      <!-- 2. Overlay ▼ (Composer + copy URL) -->
      <div class="split-btn-group sortable-item" id="topbar-item-overlay" data-item-id="overlay" draggable="true" title="คลิกคัดลอกลิงก์ OBS / คลิกขวาเพื่อซ่อนปุ่ม">
        <button class="split-btn-main active" onclick="handleSortableClick(event, () => copyObsUrl())">
          <span>🖥️</span> <span>Overlay</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropOverlay', event)">▾</button>
        <div class="dropdown-menu" id="dropOverlay">
          <button class="dropdown-item" onclick="copyObsUrl()">📋 คัดลอก Overlay URL</button>
          <button class="dropdown-item" onclick="showToast('🎛️ เปิด Composer Canvas Studio ในเบราว์เซอร์')">🖥️ เปิด Composer Studio</button>
        </div>
      </div>

      <!-- 3. Game Overlay ▼ -->
      <div class="split-btn-group sortable-item" id="topbar-item-game-overlay" data-item-id="game-overlay" draggable="true" title="คลิกสลับ Game Overlay / คลิกขวาเพื่อซ่อนปุ่ม">
        <button class="split-btn-main" onclick="handleSortableClick(event, () => showToast('🎮 สลับการแสดง Game Overlay'))">
          <span>🎮</span> <span>Game Overlay</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropGameOverlay', event)">▾</button>
        <div class="dropdown-menu" id="dropGameOverlay">
          <button class="dropdown-item" onclick="showToast('👥 เปิด Viewer Overlay สำหรับแสดงคนดูเล่นเกม')">👥 Viewer Overlay</button>
          <button class="dropdown-item" onclick="showToast('👁️ ซ่อน/แสดงกรอบ Game Overlay (Edit Mode)')">👁️ ซ่อน/แสดงกรอบ</button>
          <div class="dropdown-divider"></div>
          <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('obs')">⚙️ ตั้งค่า Game Overlay</button>
        </div>
      </div>

      <!-- 4. Overlay+ ▼ -->
      <div class="split-btn-group sortable-item" id="topbar-item-overlay-plus" data-item-id="overlay-plus" draggable="true" title="คลิกสลับ Overlay+ / คลิกขวาเพื่อซ่อนปุ่ม">
        <button class="split-btn-main" onclick="handleSortableClick(event, () => showToast('🪟 สลับการแสดง Overlay+ (Custom Web URL)'))">
          <span>🪟</span> <span>Overlay+</span>
        </button>
        <button class="split-btn-arrow" onclick="toggleDropdown('dropOverlayPlus', event)">▾</button>
        <div class="dropdown-menu" id="dropOverlayPlus">
          <button class="dropdown-item" onclick="showToast('👁️ ซ่อน/แสดงกรอบ Overlay+ (Edit Mode)')">👁️ ซ่อน/แสดงกรอบ</button>
          <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('docks')">⚙️ ตั้งค่า Overlay+</button>
        </div>
      </div>
    </div>`;

if (html.includes(oldTopbarRight)) {
  html = html.replace(oldTopbarRight, newTopbarRight);
  console.log('Topbar right updated (Events button removed from topbar).');
} else {
  console.error('oldTopbarRight not found in index.html!');
}

// 3. Add Events button into Chat Header Actions
const oldChatHeader = `        <!-- แถบปุ่มควบคุมแชทสด (คลิกค้างลากย้ายสลับตำแหน่งได้ทุกปุ่มเหมือนไอคอนมือถือ) -->
        <div class="chat-header-actions sortable-container" id="chatHeaderSortable" data-sort-key="bp3_sort_chat">
          <!-- 1. ลดขนาดฟอนต์ A- -->
          <button class="btn-chat-header sortable-item" data-item-id="font-dec" draggable="true" title="ลดขนาดฟอนต์ (A-) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => adjustFontSize(-1))">A-</button>
          
          <!-- 2. เพิ่มขนาดฟอนต์ A+ -->
          <button class="btn-chat-header sortable-item" data-item-id="font-inc" draggable="true" title="เพิ่มขนาดฟอนต์ (A+) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => adjustFontSize(1))">A+</button>
          
          <!-- 3. กระดิ่ง: แสดงสถานะระบบในแชท -->
          <button class="btn-chat-header toggled-on sortable-item" id="btnChatSystem" data-item-id="system-msg" draggable="true" title="🔔 แสดงสถานะระบบ (✅/⚪/⚠️) ในแชท (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => toggleSystemMsg(this))">🔔</button>
          
          <!-- 4. ดาว: ⭐ Clip Marker (SplitButton) -->
          <div class="split-btn-group sortable-item" data-item-id="clip-marker" draggable="true" style="height: 28px;" title="⭐ Clip Marker (คลิกค้างลากย้ายได้)">
            <button class="split-btn-main" style="height: 28px; padding: 0 8px; font-size: 13px;" onclick="handleSortableClick(event, () => markClip())">⭐</button>
            <button class="split-btn-arrow" style="height: 28px; padding: 0 4px;" onclick="toggleDropdown('dropClipMarker', event)">▾</button>
            <div class="dropdown-menu" id="dropClipMarker">
              <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('obs')">⚙️ ตั้งค่าปุ่มลัด (Hotkey)...</button>
              <button class="dropdown-item" onclick="showToast('📂 เปิดไฟล์ clip_markers.txt แล้ว')">📂 เปิดไฟล์บันทึกคลิป</button>
              <button class="dropdown-item" onclick="showToast('📁 เปิดโฟลเดอร์เก็บไฟล์คลิปแล้ว')">📁 เปิดโฟลเดอร์ที่เก็บไฟล์</button>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item" onclick="showToast('🗑️ ล้างประวัติมาร์กคลิปเรียบร้อย')">🗑️ ล้างประวัติมาร์กคลิป</button>
            </div>
          </div>

          <!-- 5. ปิดเสียงโค้ดลับ 🎟️ -->
          <button class="btn-chat-header sortable-item" id="btnChatCodeMute" data-item-id="code-mute" draggable="true" title="🎟️ ปิดเสียงโค้ดลับ (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => toggleCodeMute(this))">🎟️</button>
          
          <!-- 6. ล้างแชท 🗑️ -->
          <button class="btn-chat-header danger-btn sortable-item" data-item-id="clear-chat" draggable="true" title="🗑️ ล้างประวัติแชทสด (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => clearChat())">🗑️</button>
          
          <!-- 7. ตั้งค่าแชทสด 🛠️ -->
          <button class="btn-chat-header sortable-item" id="btnChatSettings" data-item-id="chat-settings" draggable="true" title="🛠️ ตั้งค่าการแสดงผลแชทสด (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => openToolWindow('chat-settings'))">🛠️</button>
          
          <!-- 8. แยกจอ ↗ -->
          <button class="btn-chat-header sortable-item" data-item-id="popout-chat" draggable="true" title="แยกจอแชทสด (Popout) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => showToast('↗ แยกหน้าต่างแชทสดออกมาภายนอก'))">↗</button>
        </div>`;

const newChatHeader = `        <!-- แถบปุ่มควบคุมแชทสด (มีปุ่มเปิด/ปิด Events ย้ายมาไว้ที่นี่แล้ว + ลากย้ายจัดลำดับได้) -->
        <div class="chat-header-actions sortable-container" id="chatHeaderSortable" data-sort-key="bp3_sort_chat">
          <!-- 1. ลดขนาดฟอนต์ A- -->
          <button class="btn-chat-header sortable-item" data-item-id="font-dec" draggable="true" title="ลดขนาดฟอนต์ (A-) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => adjustFontSize(-1))">A-</button>
          
          <!-- 2. เพิ่มขนาดฟอนต์ A+ -->
          <button class="btn-chat-header sortable-item" data-item-id="font-inc" draggable="true" title="เพิ่มขนาดฟอนต์ (A+) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => adjustFontSize(1))">A+</button>
          
          <!-- 3. กระดิ่ง: แสดงสถานะระบบในแชท -->
          <button class="btn-chat-header toggled-on sortable-item" id="btnChatSystem" data-item-id="system-msg" draggable="true" title="🔔 แสดงสถานะระบบ (✅/⚪/⚠️) ในแชท (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => toggleSystemMsg(this))">🔔</button>
          
          <!-- 4. ดาว: ⭐ Clip Marker (SplitButton) -->
          <div class="split-btn-group sortable-item" data-item-id="clip-marker" draggable="true" style="height: 28px;" title="⭐ Clip Marker (คลิกค้างลากย้ายได้)">
            <button class="split-btn-main" style="height: 28px; padding: 0 8px; font-size: 13px;" onclick="handleSortableClick(event, () => markClip())">⭐</button>
            <button class="split-btn-arrow" style="height: 28px; padding: 0 4px;" onclick="toggleDropdown('dropClipMarker', event)">▾</button>
            <div class="dropdown-menu" id="dropClipMarker">
              <button class="dropdown-item" onclick="openToolWindow('settings'); switchSettingsSection('obs')">⚙️ ตั้งค่าปุ่มลัด (Hotkey)...</button>
              <button class="dropdown-item" onclick="showToast('📂 เปิดไฟล์ clip_markers.txt แล้ว')">📂 เปิดไฟล์บันทึกคลิป</button>
              <button class="dropdown-item" onclick="showToast('📁 เปิดโฟลเดอร์เก็บไฟล์คลิปแล้ว')">📁 เปิดโฟลเดอร์ที่เก็บไฟล์</button>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item" onclick="showToast('🗑️ ล้างประวัติมาร์กคลิปเรียบร้อย')">🗑️ ล้างประวัติมาร์กคลิป</button>
            </div>
          </div>

          <!-- 5. ปิดเสียงโค้ดลับ 🎟️ -->
          <button class="btn-chat-header sortable-item" id="btnChatCodeMute" data-item-id="code-mute" draggable="true" title="🎟️ ปิดเสียงโค้ดลับ (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => toggleCodeMute(this))">🎟️</button>
          
          <!-- 6. ล้างแชท 🗑️ -->
          <button class="btn-chat-header danger-btn sortable-item" data-item-id="clear-chat" draggable="true" title="🗑️ ล้างประวัติแชทสด (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => clearChat())">🗑️</button>
          
          <!-- 7. ตั้งค่าแชทสด 🛠️ -->
          <button class="btn-chat-header sortable-item" id="btnChatSettings" data-item-id="chat-settings" draggable="true" title="🛠️ ตั้งค่าการแสดงผลแชทสด (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => openToolWindow('chat-settings'))">🛠️</button>

          <!-- 8. เปิด/ปิดกิจกรรม (Events List) ย้ายมาจากด้านบน -->
          <button class="btn-chat-header sortable-item active" id="btnEventsToggle" data-item-id="events" draggable="true" title="⚡ เปิด/ปิด แถบกิจกรรมสด (Events) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => toggleEventsPanel())" style="color: #38bdf8; border-color: rgba(56, 189, 248, 0.4);">
            <span>⚡</span> <span style="font-size: 11px; margin-left: 2px;">Events</span>
          </button>
          
          <!-- 9. แยกจอ ↗ -->
          <button class="btn-chat-header sortable-item" data-item-id="popout-chat" draggable="true" title="แยกจอแชทสด (Popout) (คลิกค้างลากย้ายได้)" onclick="handleSortableClick(event, () => showToast('↗ แยกหน้าต่างแชทสดออกมาภายนอก'))">↗</button>
        </div>`;

if (html.includes(oldChatHeader)) {
  html = html.replace(oldChatHeader, newChatHeader);
  console.log('Chat header updated with Events button.');
} else {
  console.error('oldChatHeader not found in index.html!');
}

// 4. Add Context Menu Container and Logic to index.html
const contextMenuHtml = `
  <!-- Custom Context Menu for Topbar Buttons -->
  <div id="topbarContextMenu" class="custom-context-menu"></div>
`;

if (!html.includes('id="topbarContextMenu"')) {
  html = html.replace('</body>', `${contextMenuHtml}\n</body>`);
}

const contextMenuJs = `
    // ----------------------------------------------------
    // Topbar Button Hide & Restore Context Menu System
    // ----------------------------------------------------
    const _topbarHideableMeta = {
      'game-overlay': { label: '🎮 Game Overlay' },
      'overlay-plus': { label: '🪟 Overlay+' },
      'overlay': { label: '🖥️ Overlay' },
      'translate': { label: '🌐 แปลภาษา / อ่านทุกภาษา' }
    };

    let _topbarHiddenKeys = [];
    try {
      _topbarHiddenKeys = JSON.parse(localStorage.getItem('bp3_topbar_hidden')) || [];
    } catch (e) {
      _topbarHiddenKeys = [];
    }

    function applyTopbarHiddenState() {
      for (const key in _topbarHideableMeta) {
        const el = document.getElementById(\`topbar-item-\${key}\`);
        if (el) {
          el.style.display = _topbarHiddenKeys.includes(key) ? 'none' : '';
        }
      }
    }

    function hideTopbarButton(key) {
      if (!_topbarHiddenKeys.includes(key)) {
        _topbarHiddenKeys.push(key);
        localStorage.setItem('bp3_topbar_hidden', JSON.stringify(_topbarHiddenKeys));
        applyTopbarHiddenState();
        const meta = _topbarHideableMeta[key];
        showToast(\`🚫 ซ่อนปุ่ม \${meta ? meta.label : key} แล้ว (คลิกขวาบนแถบเพื่อคืนค่า)\`);
      }
    }

    function restoreTopbarButton(key) {
      const idx = _topbarHiddenKeys.indexOf(key);
      if (idx !== -1) {
        _topbarHiddenKeys.splice(idx, 1);
        localStorage.setItem('bp3_topbar_hidden', JSON.stringify(_topbarHiddenKeys));
        applyTopbarHiddenState();
        const meta = _topbarHideableMeta[key];
        showToast(\`👁️ คืนค่าแสดงปุ่ม \${meta ? meta.label : key} เรียบร้อย\`);
      }
    }

    function showTopbarContextMenu(e, targetKey) {
      e.preventDefault();
      e.stopPropagation();

      const menu = document.getElementById('topbarContextMenu');
      if (!menu) return;

      let html = '';

      if (targetKey && _topbarHideableMeta[targetKey]) {
        const meta = _topbarHideableMeta[targetKey];
        html += \`
          <div class="context-menu-header">จัดการปุ่มแถบบน</div>
          <button class="context-menu-item danger" onclick="hideTopbarButton('\${targetKey}'); hideContextMenu();">
            <span>🚫 ซ่อนปุ่ม \${meta.label}</span>
          </button>
        \`;
      }

      if (_topbarHiddenKeys.length > 0) {
        if (html) html += '<div class="context-menu-divider"></div>';
        html += '<div class="context-menu-header">👁️ คืนค่าปุ่มที่ซ่อนอยู่</div>';
        _topbarHiddenKeys.forEach(k => {
          const meta = _topbarHideableMeta[k] || { label: k };
          html += \`
            <button class="context-menu-item" onclick="restoreTopbarButton('\${k}'); hideContextMenu();">
              <span>+ แสดง \${meta.label}</span>
              <span style="color:#34d399; font-size:11px;">คืนค่า</span>
            </button>
          \`;
        });
      } else if (!targetKey) {
        html += \`
          <div class="context-menu-header">ปุ่มแถบบน (Topbar)</div>
          <div style="font-size:11.5px; color:#949ba4; padding:6px 10px;">ไม่มีปุ่มที่ซ่อนอยู่</div>
        \`;
      }

      menu.innerHTML = html;
      menu.style.left = \`\${Math.min(window.innerWidth - 220, e.clientX)}px\`;
      menu.style.top = \`\${Math.min(window.innerHeight - 200, e.clientY)}px\`;
      menu.classList.add('show');
    }

    function hideContextMenu() {
      const menu = document.getElementById('topbarContextMenu');
      if (menu) menu.classList.remove('show');
    }

    window.addEventListener('click', (e) => {
      if (!e.target.closest('#topbarContextMenu')) hideContextMenu();
    });

    window.addEventListener('contextmenu', (e) => {
      const topbarItem = e.target.closest('#topbarSortable .sortable-item');
      const topbarContainer = e.target.closest('#topbarSortable');

      if (topbarItem) {
        const itemId = topbarItem.getAttribute('data-item-id');
        showTopbarContextMenu(e, itemId);
      } else if (topbarContainer) {
        showTopbarContextMenu(e, null);
      }
    });

    window.addEventListener('DOMContentLoaded', () => {
      applyTopbarHiddenState();
    });
`;

const globalTarget = `    // Global bindings`;
if (html.includes(globalTarget)) {
  html = html.replace(globalTarget, `${contextMenuJs}\n    // Global bindings`);
  html = html.replace(`window.setTranslateMode = setTranslateMode;`, `window.setTranslateMode = setTranslateMode;\n    window.hideTopbarButton = hideTopbarButton;\n    window.restoreTopbarButton = restoreTopbarButton;`);
}

fs.writeFileSync(htmlPath, html, 'utf8');
console.log('index.html fully updated with Events in chat header and right-click context menu.');
