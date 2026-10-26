import re

with open("src/composer_studio.js", "r", encoding="utf-8") as f:
    code = f.read()

def normalize(t):
    return t.replace("\r\n", "\n")

# 1. Update state
old_state = """  let state = {
    pages: JSON.parse(JSON.stringify(DEFAULT_PAGES)),
    activePageId: 'page-1',
    selectedWidgetId: null,
    zoom: 0.45,
    snapGuides: true,
    bgMode: 'checkered',
    isDragging: false,
    isResizing: false,
    dragStartMouseX: 0,
    dragStartMouseY: 0,
    dragStartWidgetX: 0,
    dragStartWidgetY: 0,
    dragStartWidgetW: 0,
    dragStartWidgetH: 0,
    activeResizeHandle: null
  };"""

new_state = """  let state = {
    pages: JSON.parse(JSON.stringify(DEFAULT_PAGES)),
    activePageId: 'page-1',
    selectedWidgetId: null,
    zoom: 0.45,
    snapGuides: true,
    bgMode: 'checkered',
    customizerManuallyCollapsed: false,
    chatThemePage: 1,
    isDragging: false,
    isResizing: false,
    dragStartMouseX: 0,
    dragStartMouseY: 0,
    dragStartWidgetX: 0,
    dragStartWidgetY: 0,
    dragStartWidgetW: 0,
    dragStartWidgetH: 0,
    activeResizeHandle: null
  };"""

# 2. Update getWidgetIcon
old_icon = """  function getWidgetIcon(type) {
    const icons = {
      chat: '💬',
      clock: '🕒',
      text: '🔤',
      character: '🎭',
      webcam: '📹',
      goal: '🎯',
      image: '🖼️'
    };
    return icons[type] || '▣';
  }"""

new_icon = """  function getWidgetIcon(type) {
    const icons = {
      chat: '💬',
      clock: '🕒',
      text: '🔤',
      character: '🎭',
      replie: '💬',
      avatar: '😊',
      webcam: '📹',
      goal: '🎯',
      donate_goal: '🎯',
      viewer: '👥',
      image: '🖼️',
      video: '🎬',
      alert: '🌐',
      now_playing: '🎵',
      emote_party: '🎉',
      ask: '🗳️',
      giveaway: '🎁',
      playroom: '🎮'
    };
    return icons[type] || '▣';
  }"""

# 3. Update renderWidgetInnerHtml
old_inner_start = "  // Render inner HTML for different widget types"
idx_inner_start = code.find(old_inner_start)
idx_inner_end = code.find("  // Select a widget", idx_inner_start)

new_inner = """  // Render inner HTML for different widget types with live styling
  function renderWidgetInnerHtml(w) {
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      const theme = w.chatTheme || 'default';

      if (mode === 'danmaku') {
        const clr = w.fontColor || '#ffffff';
        const fsz = w.fontSize || 22;
        return `
          <div class="composer-widget-inner widget-type-chat" style="background:rgba(0,0,0,0.6); overflow:hidden; position:relative; justify-content:center;">
            <div style="font-size:${fsz}px; color:${clr}; font-weight:700; white-space:nowrap; animation:cwc-bullet-move 4s linear infinite;">
              🚀 ดันมากุวิ่งบนจอสด ยินดีต้อนรับทุกคนครับ! 🔥
            </div>
          </div>
        `;
      }

      if (mode === 'balloon') {
        return `
          <div class="composer-widget-inner widget-type-chat" style="background:transparent; position:relative; align-items:flex-start; padding:10px;">
            <div style="background:#ffffff; color:#0f172a; padding:8px 14px; border-radius:14px; font-weight:700; font-size:14px; box-shadow:0 4px 12px rgba(0,0,0,0.4); position:relative;">
              💬 สวัสดีรอบห้องสตรีมครับ!
              <div style="position:absolute; bottom:-6px; left:16px; border-width:6px 6px 0; border-style:solid; border-color:#ffffff transparent; width:0;"></div>
            </div>
          </div>
        `;
      }

      // Default or Theme
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const bgClr = w.bgColor || '#1e1f22';
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const border = w.boxBorder ? `border: 2px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};` : '';
      const shadow = w.boxShadow ? 'box-shadow: 0 4px 14px rgba(0,0,0,0.4);' : '';
      const isTheme = mode === 'theme';

      return `
        <div class="composer-widget-inner widget-type-chat theme-${theme}">
          <div class="widget-chat-item" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}">
            <span style="color:#ef4444; font-weight:700;">Gamer_Pro:</span>
            <span style="color:${fClr};">สวัสดีทุกคนในไลฟ์สตรีมครับ! 🎮</span>
          </div>
          <div class="widget-chat-item" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}">
            <span style="color:#a855f7; font-weight:700;">Zack_Live:</span>
            <span style="color:${fClr};">สตรีมภาพสวยคมชัด 60fps มากครับ 🔥</span>
          </div>
          <div class="widget-chat-item" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}">
            <span style="color:#22c55e; font-weight:700;">Mali_TH:</span>
            <span style="color:${fClr};">ยินดีต้อนรับเพื่อนๆ ทุกคนนะครับ 💖</span>
          </div>
        </div>
      `;
    }

    if (w.type === 'clock') {
      const now = new Date();
      let timeStr = '';
      if (w.clockFormat === '12') {
        let hrs = now.getHours();
        const ampm = hrs >= 12 ? 'PM' : 'AM';
        hrs = hrs % 12 || 12;
        const mins = String(now.getMinutes()).padStart(2, '0');
        const secs = String(now.getSeconds()).padStart(2, '0');
        timeStr = w.showSeconds === false ? `${hrs}:${mins} ${ampm}` : `${hrs}:${mins}:${secs} ${ampm}`;
      } else {
        const hrs = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        const secs = String(now.getSeconds()).padStart(2, '0');
        timeStr = w.showSeconds === false ? `${hrs}:${mins}` : `${hrs}:${mins}:${secs}`;
      }

      const clr = w.fontColor || '';
      const fsz = w.fontSize ? `${w.fontSize}px` : '';
      const themeClass = w.clockTheme ? `clock-theme-${w.clockTheme}` : 'clock-theme-cyberpunk';

      return `
        <div class="composer-widget-inner widget-type-clock ${themeClass}" style="${clr ? 'color:' + clr + ';' : ''} ${fsz ? 'font-size:' + fsz + ';' : ''}">
          <div class="widget-clock-time">${timeStr}</div>
        </div>
      `;
    }

    if (w.type === 'text') {
      const isTicker = w.textMode === 'ticker';
      const fsz = w.fontSize ? `font-size:${w.fontSize}px;` : 'font-size:18px;';
      const clr = w.fontColor ? `color:${w.fontColor};` : 'color:#ffffff;';
      const bg = w.bgColor ? `background:${w.bgColor};` : 'background:rgba(20,25,35,0.85);';
      const text = w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม ยินดีต้อนรับทุกคนครับ!';

      if (isTicker) {
        return `
          <div class="composer-widget-inner widget-type-text widget-text-ticker" style="${fsz} ${clr} ${bg}">
            <span>${text}</span>
          </div>
        `;
      }

      return `
        <div class="composer-widget-inner widget-type-text" style="${fsz} ${clr} ${bg}">
          <span>${text}</span>
        </div>
      `;
    }

    if (w.type === 'webcam') {
      const borderClr = w.borderColor || '#5865f2';
      const borderW = w.borderWidth ?? 4;
      const radius = w.borderRadius ?? 8;
      const glow = w.glow ? `box-shadow: 0 0 16px ${borderClr};` : '';
      const label = w.showStreamerName ? (w.streamerName || 'Streamer LIVE') : '';

      return `
        <div class="composer-widget-inner widget-type-webcam" style="border:${borderW}px solid ${borderClr}; border-radius:${radius}px; ${glow}">
          <div class="widget-webcam-label">📹 เว็บแคม (${w.ratio || '16:9'})</div>
          ${label ? `<div style="position:absolute; bottom:8px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.75); color:#fff; font-size:12px; font-weight:700; padding:2px 10px; border-radius:4px; white-space:nowrap;">${label}</div>` : ''}
        </div>
      `;
    }

    if (w.type === 'goal' || w.type === 'donate_goal') {
      const current = w.goalCurrent ?? 650;
      const target = w.goalTarget ?? 1000;
      const pct = Math.min(100, Math.round((current / (target || 1)) * 100));
      const title = w.goalTitle || 'เป้าหมายผู้ติดตาม';
      const unit = w.goalUnit || 'คน';

      return `
        <div class="composer-widget-inner widget-type-goal">
          <div class="widget-goal-header">
            <span>${title}</span>
            <span style="color:#ec4899;">${current} / ${target} ${unit}</span>
          </div>
          <div class="widget-goal-bar-track">
            <div class="widget-goal-bar-fill" style="width:${pct}%;"></div>
          </div>
        </div>
      `;
    }

    if (w.type === 'viewer') {
      const theme = w.viewerTheme || 'pill';
      return `
        <div class="composer-widget-inner widget-type-viewer">
          <span style="color:#22c55e; font-size:14px;">●</span>
          <span>👥 1,280 ผู้ชมสด</span>
        </div>
      `;
    }

    if (w.type === 'character' || w.type === 'replie' || w.type === 'avatar') {
      const img = w.imageUrl || './assets/dock_offline_character.png';
      const name = w.characterName || 'Replie';
      return `
        <div class="composer-widget-inner widget-type-character">
          <img class="widget-character-img" src="${img}" alt="Character" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(name)}'">
          <div class="widget-character-name">${name}</div>
        </div>
      `;
    }

    if (w.type === 'image') {
      const img = w.imageUrl || './assets/dock_offline_character.png';
      const fit = w.fitMode || 'contain';
      return `
        <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#141517; overflow:hidden;">
          <img src="${img}" style="width:100%; height:100%; object-fit:${fit};" onerror="this.style.display='none';">
        </div>
      `;
    }

    if (w.type === 'video') {
      return `
        <div class="composer-widget-inner widget-type-video">
          <span style="font-size:24px; margin-bottom:4px;">🎬</span>
          <span>วิดีโอ (${w.loop ? 'เล่นวนซ้ำ' : 'เล่นรอบเดียว'})</span>
        </div>
      `;
    }

    if (w.type === 'alert') {
      return `
        <div class="composer-widget-inner widget-type-alert">
          <span style="font-size:20px; display:block; margin-bottom:2px;">🌐</span>
          <span style="font-size:12px; word-break:break-all;">${w.alertUrl || 'https://overlay.example.com'}</span>
        </div>
      `;
    }

    if (w.type === 'now_playing') {
      return `
        <div class="composer-widget-inner widget-type-now-playing">
          <span style="font-size:24px;">🎵</span>
          <div style="flex:1; min-width:0;">
            <div style="font-size:12px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${w.songTitle || 'Never Gonna Give You Up'}</div>
            <div style="font-size:10.5px; color:var(--dc-text-muted);">${w.artist || 'Rick Astley'}</div>
          </div>
        </div>
      `;
    }

    if (w.type === 'emote_party') {
      return `
        <div class="composer-widget-inner widget-type-emote-party">
          🎉 ปาร์ตี้อีโมทลอย
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#1e1f22;">
        <span style="font-size:24px;">${getWidgetIcon(w.type)}</span>
        <span style="font-size:12px; font-weight:700; color:#dbdee1; margin-top:4px;">${w.title}</span>
      </div>
    `;
  }
"""

# 4. Update selectWidget
old_select = """  // Select a widget
  function selectWidget(id) {
    state.selectedWidgetId = id;
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
  }"""

new_select = """  // Select a widget and open left customization drawer
  function selectWidget(id) {
    state.selectedWidgetId = id;
    state.customizerManuallyCollapsed = false; // Expand on click
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();

    const leftPanel = document.getElementById('composerSidebarLeft');
    const expandBtn = document.getElementById('btnExpandCustPanel');

    if (id) {
      renderWidgetCustomizerPanel(id);
      if (leftPanel) {
        leftPanel.classList.remove('collapsed');
      }
      if (expandBtn) expandBtn.classList.remove('visible');
    } else {
      if (leftPanel) leftPanel.classList.add('collapsed');
      if (expandBtn) expandBtn.classList.remove('visible');
    }
  }"""

# 5. Add renderWidgetCustomizerPanel implementation
customizer_panel_code = """
  // Render Left Customizer Panel with all settings for the selected widget
  function renderWidgetCustomizerPanel(id) {
    const page = getActivePage();
    if (!page) return;
    const w = page.widgets.find(x => x.id === id);
    if (!w) return;

    const iconEl = document.getElementById('compCustIcon');
    const titleEl = document.getElementById('compCustTitle');
    const typeEl = document.getElementById('compCustType');
    const bodyEl = document.getElementById('composerCustomizerBody');
    if (!bodyEl) return;

    if (iconEl) iconEl.textContent = getWidgetIcon(w.type);
    if (titleEl) titleEl.textContent = w.title;
    if (typeEl) {
      const typeNames = {
        chat: 'วิดเจ็ตกล่องแชทสด',
        clock: 'วิดเจ็ตนาฬิกาสตรีม',
        text: 'วิดเจ็ตแถบข้อความประกาศ',
        webcam: 'วิดเจ็ตกรอบเว็บแคม',
        goal: 'วิดเจ็ตเป้าหมายยอดผู้ติดตาม',
        viewer: 'วิดเจ็ตตัวนับยอดผู้ชมสด',
        character: 'วิดเจ็ตตัวละครพูด Replie',
        image: 'วิดเจ็ตกรอบรูปภาพแบนเนอร์',
        video: 'วิดเจ็ตวิดีโอลูป',
        alert: 'วิดเจ็ตเบราว์เซอร์ URL ภายนอก',
        now_playing: 'วิดเจ็ตเพลงที่กำลังเล่น',
        emote_party: 'วิดเจ็ตปาร์ตี้อีโมทลอย'
      };
      typeEl.textContent = typeNames[w.type] || 'การปรับแต่งวิดเจ็ต';
    }

    // Helper binder for inputs
    const bindField = (elId, key, type = 'text', suffix = '') => {
      const el = document.getElementById(elId);
      if (!el) return;
      const handler = () => {
        if (type === 'checkbox') {
          w[key] = el.checked;
        } else if (type === 'number') {
          w[key] = parseFloat(el.value);
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + suffix;
        } else if (type === 'opacity') {
          w[key] = parseFloat(el.value) / 100;
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + '%';
        } else {
          w[key] = el.value;
        }
        renderCanvasWidgets();
        renderLayersList();
        updateTransformInspector();
        saveState();
      };
      el.addEventListener('input', handler);
      el.addEventListener('change', handler);
    };

    let specificHtml = '';

    // ==========================================
    // 1. CHAT WIDGET CUSTOMIZATION
    // ==========================================
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      const theme = w.chatTheme || 'default';
      const allThemes = window.CWC_ALL_THEMES || [];
      const totalPages = Math.ceil(allThemes.length / 8);
      const curPage = Math.min(totalPages, Math.max(1, state.chatThemePage || 1));
      const pageThemes = allThemes.slice((curPage - 1) * 8, curPage * 8);

      let themeCardsHtml = '';
      pageThemes.forEach(t => {
        const isAct = t.id === theme;
        themeCardsHtml += `
          <div class="cwc-preset-card ${isAct ? 'active' : ''}" data-chat-theme="${t.id}">
            <div class="cwc-preset-badge" style="background:${t.id === 'cyberpunk' ? 'rgba(0,255,204,0.2)' : 'rgba(255,255,255,0.06)'};">
              ${t.badge || '🎨'}
            </div>
            <div class="cwc-preset-info">
              <div class="cwc-preset-name">${t.name}</div>
              <div class="cwc-preset-desc">${t.desc}</div>
            </div>
          </div>
        `;
      });

      specificHtml = `
        <!-- Chat Mode Tabs -->
        <div class="cwc-tabs-bar" style="border-radius:8px; margin-bottom:10px;">
          <button type="button" class="cwc-tab-btn ${mode === 'default' ? 'active' : ''}" data-set-chat-mode="default">
            ⚙️ ค่ามาตรฐาน
          </button>
          <button type="button" class="cwc-tab-btn ${mode === 'theme' ? 'active' : ''}" data-set-chat-mode="theme">
            🎨 ธีมสำเร็จรูป
          </button>
          <button type="button" class="cwc-tab-btn ${mode === 'danmaku' ? 'active' : ''}" data-set-chat-mode="danmaku">
            ⚡ ดันมากุ
          </button>
          <button type="button" class="cwc-tab-btn ${mode === 'balloon' ? 'active' : ''}" data-set-chat-mode="balloon">
            💬 บอลลูน
          </button>
          <button type="button" class="cwc-tab-btn ${mode === 'character' ? 'active' : ''}" data-set-chat-mode="character">
            🎭 ตัวละคร
          </button>
        </div>

        <!-- Mode Specific: Themes -->
        ${mode === 'theme' ? `
          <div class="comp-card-section">
            <div class="comp-card-header">
              <span class="comp-card-title">🎨 คลัง 80 ธีมสำเร็จรูป</span>
            </div>
            <div class="comp-card-body">
              <div class="cwc-presets-grid" id="compChatThemesGrid">
                ${themeCardsHtml}
              </div>
              <div class="cwc-pagination" style="margin-top:10px;">
                <button type="button" class="cwc-page-btn" id="btnCompThemePrev" ${curPage <= 1 ? 'disabled' : ''}>◀ ก่อนหน้า</button>
                <span class="cwc-page-indicator">หน้า ${curPage} / ${totalPages}</span>
                <button type="button" class="cwc-page-btn" id="btnCompThemeNext" ${curPage >= totalPages ? 'disabled' : ''}>ถัดไป ▶</button>
              </div>
            </div>
          </div>
        ` : ''}

        <!-- Mode Specific: Danmaku -->
        ${mode === 'danmaku' ? `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">⚡ ตั้งค่าดันมากุวิ่งบนจอ</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuFontSize" min="14" max="48" value="${w.fontSize || 22}">
                  <span class="cwc-slider-val" id="compChatDanmakuFontSizeVal">${w.fontSize || 22}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compChatDanmakuColor" value="${w.fontColor || '#ffffff'}">
              </div>
            </div>
          </div>
        ` : ''}

        <!-- Mode Specific: Balloon -->
        ${mode === 'balloon' ? `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">💬 ตั้งค่าบอลลูนคำพูด</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งใสบอลลูน</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonOpacity" min="10" max="100" value="${Math.round((w.balloonOpacity ?? 0.95) * 100)}">
                  <span class="cwc-slider-val" id="compChatBalloonOpacityVal">${Math.round((w.balloonOpacity ?? 0.95) * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        ` : ''}

        <!-- Typography & Box Style -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 แบบอักษรและสี</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ฟอนต์ตัวหนังสือ</span>
              <select class="cwc-select" id="compChatFontFamily">
                <option value="Kanit" ${w.fontFamily === 'Kanit' ? 'selected' : ''}>Kanit (คานิท)</option>
                <option value="Prompt" ${w.fontFamily === 'Prompt' ? 'selected' : ''}>Prompt (พร้อมต์)</option>
                <option value="Sarabun" ${w.fontFamily === 'Sarabun' ? 'selected' : ''}>Sarabun (สารบรรณ)</option>
                <option value="Mitr" ${w.fontFamily === 'Mitr' ? 'selected' : ''}>Mitr (มิตร)</option>
                <option value="JetBrains Mono" ${w.fontFamily === 'JetBrains Mono' ? 'selected' : ''}>JetBrains Mono</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดตัวอักษร</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compChatFontSize" min="11" max="32" value="${w.fontSize || 15}">
                <span class="cwc-slider-val" id="compChatFontSizeVal">${w.fontSize || 15}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compChatFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
          </div>
        </div>

        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📦 กล่องข้อความแชท</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลังกล่อง</span>
              <input type="color" class="cwc-color-pick" id="compChatBgColor" value="${w.bgColor || '#1e1f22'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโปร่งใสพื้นหลัง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compChatBgOpacity" min="0" max="100" value="${Math.round((w.bgOpacity ?? 0.85) * 100)}">
                <span class="cwc-slider-val" id="compChatBgOpacityVal">${Math.round((w.bgOpacity ?? 0.85) * 100)}%</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมนมุมกล่อง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compChatBoxRadius" min="0" max="30" value="${w.boxRadius ?? 8}">
                <span class="cwc-slider-val" id="compChatBoxRadiusVal">${w.boxRadius ?? 8}px</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 2. CLOCK WIDGET CUSTOMIZATION
    // ==========================================
    else if (w.type === 'clock') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🕒 ธีมและสไตล์นาฬิกา</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ธีมนาฬิกา</span>
              <select class="cwc-select" id="compClockTheme">
                <option value="cyberpunk" ${w.clockTheme === 'cyberpunk' ? 'selected' : ''}>ไซเบอร์พังก์ (Cyberpunk)</option>
                <option value="neon" ${w.clockTheme === 'neon' ? 'selected' : ''}>นีออน (Neon Rose)</option>
                <option value="flip" ${w.clockTheme === 'flip' ? 'selected' : ''}>ฟลิปการ์ด (Flip Card)</option>
                <option value="minimal" ${w.clockTheme === 'minimal' ? 'selected' : ''}>มินิมอลโปร่งใส (Minimal)</option>
                <option value="digital" ${w.clockTheme === 'digital' ? 'selected' : ''}>ดิจิทัลเขียว (Matrix Digital)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบเวลา</span>
              <select class="cwc-select" id="compClockFormat">
                <option value="24" ${w.clockFormat !== '12' ? 'selected' : ''}>24 ชั่วโมง (14:30:00)</option>
                <option value="12" ${w.clockFormat === '12' ? 'selected' : ''}>12 ชั่วโมง (02:30:00 PM)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงวินาที</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compClockShowSeconds" ${w.showSeconds !== false ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดตัวเลข</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compClockFontSize" min="16" max="72" value="${w.fontSize || 26}">
                <span class="cwc-slider-val" id="compClockFontSizeVal">${w.fontSize || 26}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวเลข</span>
              <input type="color" class="cwc-color-pick" id="compClockFontColor" value="${w.fontColor || '#38bdf8'}">
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 3. TEXT ANNOUNCEMENT / TICKER WIDGET
    // ==========================================
    else if (w.type === 'text') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ข้อความและโหมดตัววิ่ง</span></div>
          <div class="comp-card-body">
            <div class="comp-form-group">
              <label class="comp-form-label">ข้อความประกาศ</label>
              <textarea class="comp-form-textarea" id="compTextInput">${w.text || ''}</textarea>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดการแสดงผล</span>
              <select class="cwc-select" id="compTextMode">
                <option value="ticker" ${w.textMode === 'ticker' ? 'selected' : ''}>ตัววิ่งจากขวาไปซ้าย (Ticker)</option>
                <option value="static" ${w.textMode === 'static' ? 'selected' : ''}>นิ่งอยู่กับที่ (Static)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดตัวอักษร</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="64" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compTextFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compTextFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลังแถบ</span>
              <input type="color" class="cwc-color-pick" id="compTextBgColor" value="${w.bgColor || '#141923'}">
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 4. WEBCAM FRAME WIDGET
    // ==========================================
    else if (w.type === 'webcam') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📹 สัดส่วนและกรอบเว็บแคม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">อัตราส่วนกล้อง</span>
              <select class="cwc-select" id="compWebcamRatio">
                <option value="16:9" ${w.ratio !== '4:3' && w.ratio !== '1:1' && w.ratio !== '9:16' ? 'selected' : ''}>16:9 แนวนอนมาตรฐาน</option>
                <option value="4:3" ${w.ratio === '4:3' ? 'selected' : ''}>4:3 คลาสสิก</option>
                <option value="1:1" ${w.ratio === '1:1' ? 'selected' : ''}>1:1 สี่เหลี่ยมจัตุรัส</option>
                <option value="9:16" ${w.ratio === '9:16' ? 'selected' : ''}>9:16 แนวตั้งมือถือ</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบกรอบ</span>
              <input type="color" class="cwc-color-pick" id="compWebcamBorderColor" value="${w.borderColor || '#5865f2'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาขอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamBorderWidth" min="0" max="16" value="${w.borderWidth ?? 4}">
                <span class="cwc-slider-val" id="compWebcamBorderWidthVal">${w.borderWidth ?? 4}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมนมุมกล้อง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamRadius" min="0" max="32" value="${w.borderRadius ?? 8}">
                <span class="cwc-slider-val" id="compWebcamRadiusVal">${w.borderRadius ?? 8}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เรืองแสงขอบ (Glow)</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compWebcamGlow" ${w.glow ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงป้ายชื่อสตรีมเมอร์</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compWebcamShowStreamer" ${w.showStreamerName ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
            <div class="comp-form-group">
              <label class="comp-form-label">ชื่อบนป้ายสตรีมเมอร์</label>
              <input type="text" class="cwc-input-text" id="compWebcamStreamerName" value="${w.streamerName || 'Streamer LIVE'}" style="max-width:100%;">
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 5. GOAL BAR WIDGET
    // ==========================================
    else if (w.type === 'goal' || w.type === 'donate_goal') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎯 ตั้งค่าเป้าหมาย</span></div>
          <div class="comp-card-body">
            <div class="comp-form-group">
              <label class="comp-form-label">หัวข้อเป้าหมาย</label>
              <input type="text" class="cwc-input-text" id="compGoalTitle" value="${w.goalTitle || 'เป้าหมายผู้ติดตาม'}" style="max-width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ยอดปัจจุบัน</span>
              <input type="number" class="cwc-input-text" id="compGoalCurrent" value="${w.goalCurrent ?? 650}" style="width:110px;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ยอดเป้าหมาย</span>
              <input type="number" class="cwc-input-text" id="compGoalTarget" value="${w.goalTarget ?? 1000}" style="width:110px;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">หน่วยนับ</span>
              <input type="text" class="cwc-input-text" id="compGoalUnit" value="${w.goalUnit || 'คน'}" style="width:110px;">
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 6. VIEWER COUNT WIDGET
    // ==========================================
    else if (w.type === 'viewer') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">👥 ตัวนับยอดผู้ชม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ธีมตัวนับ</span>
              <select class="cwc-select" id="compViewerTheme">
                <option value="pill" ${w.viewerTheme === 'pill' ? 'selected' : ''}>ป้ายแคปซูล (Pill Badge)</option>
                <option value="minimal" ${w.viewerTheme === 'minimal' ? 'selected' : ''}>มินิมอลโปร่งใส (Minimal)</option>
              </select>
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 7. CHARACTER / REPLIE WIDGET
    // ==========================================
    else if (w.type === 'character' || w.type === 'replie' || w.type === 'avatar') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎭 ตั้งค่าตัวละคร Replie</span></div>
          <div class="comp-card-body">
            <div class="comp-form-group">
              <label class="comp-form-label">ชื่อตัวละคร</label>
              <input type="text" class="cwc-input-text" id="compCharName" value="${w.characterName || 'Replie'}" style="max-width:100%;">
            </div>
            <div class="comp-form-group">
              <label class="comp-form-label">ที่อยู่รูปภาพตัวละคร (Image URL)</label>
              <input type="text" class="cwc-input-text" id="compCharImg" value="${w.imageUrl || './assets/dock_offline_character.png'}" style="max-width:100%;">
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 8. IMAGE BANNER WIDGET
    // ==========================================
    else if (w.type === 'image') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🖼️ รูปภาพแบนเนอร์</span></div>
          <div class="comp-card-body">
            <div class="comp-form-group">
              <label class="comp-form-label">ที่อยู่รูปภาพ (Image URL / Path)</label>
              <input type="text" class="cwc-input-text" id="compImgUrl" value="${w.imageUrl || ''}" placeholder="./assets/banner.png หรือ https://..." style="max-width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดการวางภาพ</span>
              <select class="cwc-select" id="compImgFit">
                <option value="contain" ${w.fitMode === 'contain' ? 'selected' : ''}>พอดีกรอบ (Contain)</option>
                <option value="cover" ${w.fitMode === 'cover' ? 'selected' : ''}>เต็มกรอบ (Cover)</option>
                <option value="fill" ${w.fitMode === 'fill' ? 'selected' : ''}>ยืดตามกรอบ (Fill)</option>
              </select>
            </div>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 9. VIDEO WIDGET
    // ==========================================
    else if (w.type === 'video') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎬 วิดีโอลูป</span></div>
          <div class="comp-card-body">
            <div class="comp-form-group">
              <label class="comp-form-label">ที่อยู่วิดีโอ (Video URL / Path)</label>
              <input type="text" class="cwc-input-text" id="compVideoUrl" value="${w.videoUrl || ''}" placeholder="./assets/bg.mp4" style="max-width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เล่นวนซ้ำ (Loop)</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compVideoLoop" ${w.loop !== false ? 'checked' : ''}>
                <span class="cwc-switch-slider"></span>
              </label>
            </div>
          </div>
        </div>
      `;
    }

    // Assemble full customizer HTML
    bodyEl.innerHTML = `
      <!-- General Properties -->
      <div class="comp-card-section">
        <div class="comp-card-header"><span class="comp-card-title">⚙️ ข้อมูลทั่วไป</span></div>
        <div class="comp-card-body">
          <div class="comp-form-group">
            <label class="comp-form-label">ชื่อวิดเจ็ต</label>
            <input type="text" class="cwc-input-text" id="compGeneralTitle" value="${w.title || ''}" style="max-width:100%;">
          </div>
          <div class="comp-field-row">
            <span class="comp-field-label">ความทึบแสง (Opacity)</span>
            <div class="cwc-slider-wrap">
              <input type="range" class="cwc-slider" id="compGeneralOpacity" min="10" max="100" value="${Math.round((w.opacity ?? 1) * 100)}">
              <span class="cwc-slider-val" id="compGeneralOpacityVal">${Math.round((w.opacity ?? 1) * 100)}%</span>
            </div>
          </div>
          <div class="comp-field-row">
            <span class="comp-field-label">ล็อกตำแหน่ง (ห้ามเลื่อน)</span>
            <label class="cwc-switch">
              <input type="checkbox" id="compGeneralLocked" ${w.locked ? 'checked' : ''}>
              <span class="cwc-switch-slider"></span>
            </label>
          </div>
        </div>
      </div>

      ${specificHtml}
    `;

    // Bind General
    bindField('compGeneralTitle', 'title');
    bindField('compGeneralOpacity', 'opacity', 'opacity');
    bindField('compGeneralLocked', 'locked', 'checkbox');

    // Bind Type Specific
    if (w.type === 'chat') {
      // Mode tabs
      bodyEl.querySelectorAll('[data-set-chat-mode]').forEach(btn => {
        btn.addEventListener('click', () => {
          w.chatMode = btn.dataset.setChatMode;
          renderCanvasWidgets();
          renderWidgetCustomizerPanel(w.id);
          saveState();
        });
      });

      // Theme cards
      bodyEl.querySelectorAll('[data-chat-theme]').forEach(card => {
        card.addEventListener('click', () => {
          w.chatTheme = card.dataset.chatTheme;
          bodyEl.querySelectorAll('[data-chat-theme]').forEach(c => c.classList.remove('active'));
          card.classList.add('active');
          renderCanvasWidgets();
          saveState();
        });
      });

      // Pagination
      const allThemes = window.CWC_ALL_THEMES || [];
      const totalPages = Math.ceil(allThemes.length / 8);
      const btnPrev = document.getElementById('btnCompThemePrev');
      const btnNext = document.getElementById('btnCompThemeNext');
      if (btnPrev) {
        btnPrev.addEventListener('click', () => {
          state.chatThemePage = Math.max(1, (state.chatThemePage || 1) - 1);
          renderWidgetCustomizerPanel(w.id);
        });
      }
      if (btnNext) {
        btnNext.addEventListener('click', () => {
          state.chatThemePage = Math.min(totalPages, (state.chatThemePage || 1) + 1);
          renderWidgetCustomizerPanel(w.id);
        });
      }

      bindField('compChatDanmakuFontSize', 'fontSize', 'number', 'px');
      bindField('compChatDanmakuColor', 'fontColor');
      bindField('compChatBalloonOpacity', 'balloonOpacity', 'opacity');
      bindField('compChatFontFamily', 'fontFamily');
      bindField('compChatFontSize', 'fontSize', 'number', 'px');
      bindField('compChatFontColor', 'fontColor');
      bindField('compChatBgColor', 'bgColor');
      bindField('compChatBgOpacity', 'bgOpacity', 'opacity');
      bindField('compChatBoxRadius', 'boxRadius', 'number', 'px');
    } else if (w.type === 'clock') {
      bindField('compClockTheme', 'clockTheme');
      bindField('compClockFormat', 'clockFormat');
      bindField('compClockShowSeconds', 'showSeconds', 'checkbox');
      bindField('compClockFontSize', 'fontSize', 'number', 'px');
      bindField('compClockFontColor', 'fontColor');
    } else if (w.type === 'text') {
      bindField('compTextInput', 'text');
      bindField('compTextMode', 'textMode');
      bindField('compTextFontSize', 'fontSize', 'number', 'px');
      bindField('compTextFontColor', 'fontColor');
      bindField('compTextBgColor', 'bgColor');
    } else if (w.type === 'webcam') {
      bindField('compWebcamRatio', 'ratio');
      bindField('compWebcamBorderColor', 'borderColor');
      bindField('compWebcamBorderWidth', 'borderWidth', 'number', 'px');
      bindField('compWebcamRadius', 'borderRadius', 'number', 'px');
      bindField('compWebcamGlow', 'glow', 'checkbox');
      bindField('compWebcamShowStreamer', 'showStreamerName', 'checkbox');
      bindField('compWebcamStreamerName', 'streamerName');
    } else if (w.type === 'goal' || w.type === 'donate_goal') {
      bindField('compGoalTitle', 'goalTitle');
      bindField('compGoalCurrent', 'goalCurrent', 'number');
      bindField('compGoalTarget', 'goalTarget', 'number');
      bindField('compGoalUnit', 'goalUnit');
    } else if (w.type === 'viewer') {
      bindField('compViewerTheme', 'viewerTheme');
    } else if (w.type === 'character' || w.type === 'replie' || w.type === 'avatar') {
      bindField('compCharName', 'characterName');
      bindField('compCharImg', 'imageUrl');
    } else if (w.type === 'image') {
      bindField('compImgUrl', 'imageUrl');
      bindField('compImgFit', 'fitMode');
    } else if (w.type === 'video') {
      bindField('compVideoUrl', 'videoUrl');
      bindField('compVideoLoop', 'loop', 'checkbox');
    }
  }
"""

# 6. Update setupCanvasEvents to add collapse and expand button events
old_setup_events = """    // Bind settings modal close & save buttons
    document.getElementById('btnCompCloseSetting')?.addEventListener('click', closeWidgetSettings);
    document.getElementById('btnCompCancelSetting')?.addEventListener('click', closeWidgetSettings);
    document.getElementById('btnCompSaveSetting')?.addEventListener('click', saveWidgetSettings);
  }"""

new_setup_events = """    // Bind settings modal close & save buttons
    document.getElementById('btnCompCloseSetting')?.addEventListener('click', closeWidgetSettings);
    document.getElementById('btnCompCancelSetting')?.addEventListener('click', closeWidgetSettings);
    document.getElementById('btnCompSaveSetting')?.addEventListener('click', saveWidgetSettings);

    // Bind left customizer panel collapse & expand buttons
    document.getElementById('btnCollapseCustPanel')?.addEventListener('click', () => {
      const leftPanel = document.getElementById('composerSidebarLeft');
      const expandBtn = document.getElementById('btnExpandCustPanel');
      if (leftPanel) leftPanel.classList.add('collapsed');
      if (expandBtn && state.selectedWidgetId) {
        expandBtn.classList.add('visible');
        const w = getSelectedWidget();
        if (w) expandBtn.innerHTML = `⚙️ ปรับแต่ง ${w.title} ▶`;
      }
      state.customizerManuallyCollapsed = true;
      setTimeout(autoFitCanvas, 220);
    });

    document.getElementById('btnExpandCustPanel')?.addEventListener('click', () => {
      const leftPanel = document.getElementById('composerSidebarLeft');
      const expandBtn = document.getElementById('btnExpandCustPanel');
      if (leftPanel) leftPanel.classList.remove('collapsed');
      if (expandBtn) expandBtn.classList.remove('visible');
      state.customizerManuallyCollapsed = false;
      setTimeout(autoFitCanvas, 220);
    });
  }"""

# 7. Update addWidget presets
old_presets = """    const presets = {
      chat: { title: 'กล่องแชทสด', width: 440, height: 600 },
      clock: { title: 'นาฬิกาสตรีม', width: 260, height: 70 },
      text: { title: 'แถบข้อความประกาศ', width: 800, height: 50, text: 'ข้อความสตรีมสดใหม่' },
      character: { title: 'ตัวละครพูด Replie', width: 340, height: 420 },
      webcam: { title: 'กรอบกล้องเว็บแคม', width: 480, height: 270 },
      goal: { title: 'เป้าหมายผู้ติดตาม', width: 400, height: 75 },
      image: { title: 'กรอบรูปภาพแบนเนอร์', width: 320, height: 180 }
    };"""

new_presets = """    const presets = {
      chat: { title: 'กล่องแชทสด', width: 440, height: 600, chatMode: 'default', chatTheme: 'default', fontSize: 15, fontColor: '#ffffff' },
      clock: { title: 'นาฬิกาสตรีม', width: 280, height: 80, clockTheme: 'cyberpunk', clockFormat: '24', showSeconds: true, fontSize: 26, fontColor: '#38bdf8' },
      text: { title: 'แถบข้อความประกาศ', width: 800, height: 50, text: 'ข้อความสตรีมสดใหม่ ยินดีต้อนรับทุกคนครับ!', textMode: 'ticker', fontSize: 18, fontColor: '#ffffff' },
      character: { title: 'ตัวละครพูด Replie', width: 340, height: 420, characterName: 'Replie', imageUrl: './assets/dock_offline_character.png' },
      webcam: { title: 'กรอบกล้องเว็บแคม', width: 480, height: 270, ratio: '16:9', borderColor: '#5865f2', borderWidth: 4, borderRadius: 8, glow: true, showStreamerName: true, streamerName: 'Streamer LIVE' },
      goal: { title: 'เป้าหมายผู้ติดตาม', width: 420, height: 80, goalTitle: 'เป้าหมายผู้ติดตาม', goalCurrent: 650, goalTarget: 1000, goalUnit: 'คน' },
      viewer: { title: 'ตัวนับยอดผู้ชมสด', width: 240, height: 55, viewerTheme: 'pill' },
      image: { title: 'กรอบรูปภาพแบนเนอร์', width: 340, height: 200, fitMode: 'contain' },
      video: { title: 'วิดีโอลูป', width: 480, height: 270, loop: true },
      alert: { title: 'เบราว์เซอร์ URL', width: 400, height: 300, alertUrl: 'https://overlay.example.com' },
      now_playing: { title: 'เพลงที่กำลังเล่น', width: 340, height: 75, songTitle: 'Never Gonna Give You Up', artist: 'Rick Astley' },
      emote_party: { title: 'ปาร์ตี้อีโมทลอย', width: 300, height: 200 }
    };"""

code_norm = normalize(code)

if normalize(old_state) in code_norm:
    code_norm = code_norm.replace(normalize(old_state), normalize(new_state), 1)
    print("Updated state")
else:
    print("Could not find old_state")

if normalize(old_icon) in code_norm:
    code_norm = code_norm.replace(normalize(old_icon), normalize(new_icon), 1)
    print("Updated getWidgetIcon")
else:
    print("Could not find old_icon")

if normalize(code[idx_inner_start:idx_inner_end]) in code_norm:
    code_norm = code_norm.replace(normalize(code[idx_inner_start:idx_inner_end]), normalize(new_inner) + "\n", 1)
    print("Updated renderWidgetInnerHtml")
else:
    print("Could not find renderWidgetInnerHtml block")

if normalize(old_select) in code_norm:
    code_norm = code_norm.replace(normalize(old_select), normalize(new_select), 1)
    print("Updated selectWidget")
else:
    print("Could not find old_select")

if normalize(old_presets) in code_norm:
    code_norm = code_norm.replace(normalize(old_presets), normalize(new_presets), 1)
    print("Updated addWidget presets")
else:
    print("Could not find old_presets")

if normalize(old_setup_events) in code_norm:
    code_norm = code_norm.replace(normalize(old_setup_events), normalize(new_setup_events), 1)
    print("Updated setupCanvasEvents")
else:
    print("Could not find old_setup_events")

# Append renderWidgetCustomizerPanel before setupCanvasEvents
anchor_setup = "  // Setup Canvas Viewport Click and Context Menus"
idx_anchor = code_norm.find(anchor_setup)
if idx_anchor != -1:
    code_norm = code_norm[:idx_anchor] + customizer_panel_code + "\n" + code_norm[idx_anchor:]
    print("Inserted renderWidgetCustomizerPanel")
else:
    print("Could not find anchor_setup")

with open("src/composer_studio.js", "w", encoding="utf-8") as f:
    f.write(code_norm)

print("Updated src/composer_studio.js successfully!")
