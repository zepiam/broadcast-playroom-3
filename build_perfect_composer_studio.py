# -*- coding: utf-8 -*-
import os

with open(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\original_composer_studio.js', 'r', encoding='utf-8') as f:
    orig = f.read()

# Let's inspect each function in orig:
# - loadSavedState
# - saveState
# - getActivePage
# - getSelectedWidget
# - initComposerStudio
# - autoFitCanvas
# - setZoom
# - renderPageTabs
# - addNewPage
# - renderCanvasWidgets
# - getWidgetIcon
# - renderWidgetInnerHtml
# - selectWidget
# - startDrag
# - startResize
# - onMouseMove
# - onMouseUp
# - handleKeyDown
# - addWidget
# - deleteSelectedWidget
# - renderLayersList
# - alignWidget
# - updateTransformInspector
# - setupCanvasEvents
# - setupToolbarEvents
# - copyComposerObsUrl

# We will construct the entire new composer_studio.js with all features!
output_code = r'''/**
 * BROADCAST PLAYROOM 3.0 - IN-APP OVERLAY COMPOSER CANVAS STUDIO
 * Unified Canvas Studio & Full Widget Customizer with Real-Time Live Preview,
 * Interactive Demos, Context Menu Add, and Duplicate Prevention
 */

(function () {
  'use strict';

  const CANVAS_WIDTH = 1920;
  const CANVAS_HEIGHT = 1080;
  const STORAGE_KEY = 'bp_composer_studio_v3';

  // Application State
  const state = {
    pages: [
      {
        id: 'page-1',
        name: 'ฉากหลักสตรีม',
        widgets: [
          {
            id: 'w-chat-1',
            type: 'chat',
            title: 'กล่องแชทมาตรฐาน',
            chatMode: 'default',
            chatTheme: 'default',
            x: 60,
            y: 400,
            width: 440,
            height: 600,
            z: 1,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 15,
            fontColor: '#ffffff',
            bgColor: '#1e1f22',
            bgOpacity: 0.85,
            boxRadius: 8
          },
          {
            id: 'w-clock-1',
            type: 'clock',
            title: 'นาฬิกาสตรีม',
            clockTheme: 'cyberpunk',
            clockFormat: '24',
            showSeconds: true,
            x: 1560,
            y: 50,
            width: 280,
            height: 80,
            z: 2,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 26,
            fontColor: '#38bdf8'
          },
          {
            id: 'w-text-1',
            type: 'text',
            title: 'แถบข้อความประกาศ',
            text: 'ยินดีต้อนรับทุกคนเข้าสู่ไลฟ์สตรีมสดวันนี้ครับ! กดติดตามและพูดคุยในแชทได้เลย',
            textMode: 'ticker',
            x: 560,
            y: 1000,
            width: 800,
            height: 50,
            z: 3,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 18,
            fontColor: '#ffffff',
            bgColor: '#141923'
          }
        ]
      }
    ],
    activePageId: 'page-1',
    selectedWidgetId: null,
    zoom: 0.45,
    snapGuides: true,
    isDragging: false,
    isResizing: false,
    activeResizeHandle: null,
    dragStartMouseX: 0,
    dragStartMouseY: 0,
    dragStartWidgetX: 0,
    dragStartWidgetY: 0,
    dragStartWidgetW: 0,
    dragStartWidgetH: 0,
    customizerManuallyCollapsed: false,
    chatSubTab: 'standard',
    chatThemePage: 1
  };

  let clockInterval = null;

  // ========================================================
  // COMPOSER LIVE DEMO SIMULATION MANAGER
  // ========================================================
  const ComposerDemoManager = {
    timers: {},
    chatMockPool: [
      { user: 'Krit_Live', text: 'สวัสดีทุกคนในไลฟ์สตรีม ภาพคมชัดมากครับ! 🎮', platform: 'youtube', color: '#ef4444' },
      { user: 'Zack_Twitch', text: 'สตรีมภาพสวย 60fps ลื่นไหลดีมากครับ 🔥', platform: 'twitch', color: '#a855f7' },
      { user: 'น้องมุก_ยิ้มสดใส', text: 'ส่งดาว 100 ดวง เป็นกำลังใจให้สตรีมเมอร์นะคะ ⭐', platform: 'facebook', color: '#3b82f6' },
      { user: 'Boy_Gamer', text: 'วันนี้เล่นเกมเนื้อเรื่องสนุกสุดๆ เลยครับ 🚀', platform: 'kick', color: '#22c55e' },
      { user: 'Aom_Channel', text: 'ยินดีต้อนรับเพื่อนๆ ทุกคนที่แวะเข้ามาพูดคุยกันน้า 💖', platform: 'tiktok', color: '#ec4899' },
      { user: 'Captain_Soop', text: 'ภาพแสงและสีในเกมวันนี้ปรับได้สวยงามมากครับ ✨', platform: 'soop', color: '#06b6d4' }
    ],
    charMockPool: [
      'สวัสดีครับทุกคน! วันนี้ยินดีต้อนรับสู่ไลฟ์สตรีมนะครับ 🎮',
      'ขอบคุณทุกคนที่เข้ามาร่วมพูดคุยและส่งกำลังใจให้กันนะครับ ✨',
      'ขอให้ทุกคนมีความสุขและสนุกกับการรับชมสตรีมวันนี้น้า 💖',
      'อย่าลืมกดแชร์และคอมเมนต์พูดคุยกันได้ตลอดเลยนะครับ! 🚀'
    ],
    danmakuPool: [
      '🚀 สตรีมเมอร์สู้ๆ นะครับ!',
      '🎮 ภาพคมชัด 60fps ลื่นมาก',
      '💖 สวัสดีรอบห้องสตรีมจ้า',
      '🔥 คอมเมนต์ด่วน ดันมากุวิ่งบนจอสด',
      '⭐ ยินดีต้อนรับเพื่อนๆ ทุกคนครับ',
      '🎉 สตรีมสนุกมากครับวันนี้'
    ],

    // Default Chat Simulation
    sendChatMsg(w) {
      const feed = document.getElementById(`widget-chat-feed-${w.id}`);
      if (!feed) return;
      const msg = this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      const item = document.createElement('div');
      item.className = 'widget-chat-item';
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const bgClr = w.bgColor || '#1e1f22';
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const border = w.boxBorder ? `border: 2px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};` : '';
      const shadow = w.boxShadow ? 'box-shadow: 0 4px 14px rgba(0,0,0,0.4);' : '';
      const isTheme = w.chatMode === 'theme';

      item.style.cssText = `font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}; animation:cwc-item-pop 0.25s ease-out; margin-bottom:6px;`;
      item.innerHTML = `<span style="color:${msg.color}; font-weight:700;">${msg.user}:</span> <span style="color:${fClr};">${msg.text}</span>`;
      feed.appendChild(item);
      feed.scrollTop = feed.scrollHeight;

      while (feed.children.length > 10) {
        feed.removeChild(feed.children[0]);
      }
    },

    toggleChatLoop(w, btn) {
      if (this.timers[w.id]) {
        clearInterval(this.timers[w.id]);
        delete this.timers[w.id];
        if (btn) {
          btn.innerHTML = '▶ เล่นจำลองแชทสด';
          btn.classList.remove('active');
        }
      } else {
        this.sendChatMsg(w);
        this.timers[w.id] = setInterval(() => this.sendChatMsg(w), 1600);
        if (btn) {
          btn.innerHTML = '⏹ หยุดจำลองแชท';
          btn.classList.add('active');
        }
      }
    },

    // Danmaku Simulation
    sendDanmakuMsg(w) {
      const feed = document.getElementById(`widget-danmaku-feed-${w.id}`);
      if (!feed) return;
      const txt = this.danmakuPool[Math.floor(Math.random() * this.danmakuPool.length)];
      const bullet = document.createElement('div');
      bullet.className = 'danmaku-bullet-item';

      const zone = w.slider_zone || 'middle';
      let minY = 0.05, maxY = 0.90;
      if (zone === 'top') { minY = 0.05; maxY = 0.45; }
      else if (zone === 'middle') { minY = 0.25; maxY = 0.70; }
      else if (zone === 'bottom') { minY = 0.55; maxY = 0.92; }

      const topPct = (minY + Math.random() * (maxY - minY)) * 100;
      const fsz = w.fontSize || 24;
      const clr = w.fontColor || '#ffffff';
      const stroke = w.textStroke !== false ? `-webkit-text-stroke: 1.5px ${w.strokeColor || '#000000'};` : '';
      const shadow = w.textShadow !== false ? 'filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8));' : '';
      const dur = w.speed || 6;

      bullet.style.cssText = `top: ${topPct}%; left: 0; font-size: ${fsz}px; color: ${clr}; opacity: ${w.opacity ?? 1}; ${stroke} ${shadow} animation: danmakuBulletRun ${dur}s linear forwards;`;
      bullet.textContent = txt;
      feed.appendChild(bullet);

      setTimeout(() => bullet.remove(), dur * 1000 + 500);
    },

    toggleDanmakuLoop(w, btn) {
      if (this.timers[w.id]) {
        clearInterval(this.timers[w.id]);
        delete this.timers[w.id];
        if (btn) {
          btn.innerHTML = '▶ เล่นกระสุนดันมากุสด';
          btn.classList.remove('active');
        }
      } else {
        this.sendDanmakuMsg(w);
        this.timers[w.id] = setInterval(() => this.sendDanmakuMsg(w), 1200);
        if (btn) {
          btn.innerHTML = '⏹ หยุดกระสุนดันมากุ';
          btn.classList.add('active');
        }
      }
    },

    // Balloon Simulation
    sendBalloonMsg(w) {
      const feed = document.getElementById(`widget-balloon-feed-${w.id}`);
      if (!feed) return;
      const msg = this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      const bubble = document.createElement('div');
      const bg = w.balloonBg || '#ffffff';
      const color = w.balloonTextColor || '#0f172a';
      const radius = w.balloonRadius ?? 14;
      const fsz = w.fontSize || 15;
      const op = w.balloonOpacity ?? 0.95;

      bubble.style.cssText = `background: ${bg}; color: ${color}; padding: 10px 16px; border-radius: ${radius}px; font-size: ${fsz}px; font-weight: 600; position: relative; box-shadow: 0 6px 18px rgba(0,0,0,0.35); opacity: ${op}; animation: cwc-balloon-pop 0.28s cubic-bezier(0.34, 1.56, 0.64, 1); margin-bottom: 14px; max-width: 90%;`;
      bubble.innerHTML = `<div style="font-weight:700; font-size:12px; color:${msg.color}; margin-bottom:3px;">${msg.user}:</div><div>${msg.text}</div><svg style="position:absolute; bottom:-11px; left:22px; width:18px; height:12px; fill:${bg};" viewBox="0 0 18 12"><path d="M0 0 L18 0 L6 12 Z"/></svg>`;
      feed.appendChild(bubble);
      feed.scrollTop = feed.scrollHeight;

      while (feed.children.length > 5) {
        feed.removeChild(feed.children[0]);
      }
    },

    // Character Chat Simulation
    triggerCharacterTalk(w) {
      const txtEl = document.getElementById(`widget-char-text-${w.id}`);
      const avatarEl = document.getElementById(`widget-char-avatar-${w.id}`);
      if (txtEl) {
        const text = this.charMockPool[Math.floor(Math.random() * this.charMockPool.length)];
        txtEl.textContent = text;
        txtEl.parentElement.style.animation = 'none';
        void txtEl.parentElement.offsetWidth;
        txtEl.parentElement.style.animation = 'cwc-balloon-pop 0.3s ease-out';
      }
      if (avatarEl) {
        avatarEl.style.transform = 'scale(1.08)';
        avatarEl.style.filter = 'drop-shadow(0 0 12px #6366f1)';
        setTimeout(() => {
          avatarEl.style.transform = 'scale(1)';
          avatarEl.style.filter = 'none';
        }, 600);
      }
    },

    // Goal Simulation
    triggerGoalPlus(w) {
      w.goalCurrent = (w.goalCurrent || 0) + 50;
      if (w.goalTarget && w.goalCurrent > w.goalTarget) {
        w.goalCurrent = w.goalTarget;
      }
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
      if (window.showToast) window.showToast(`🎉 เป้าหมายยอดเพิ่มขึ้นเป็น ${w.goalCurrent} แล้ว!`);
    },

    triggerGoalReset(w) {
      w.goalCurrent = 0;
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
    },

    // Viewer Simulation
    triggerViewerPulse(w) {
      const randChange = (Math.floor(Math.random() * 30) - 10);
      w.mockViewerCount = Math.max(1, (w.mockViewerCount || 1250) + randChange);
      const countEl = document.getElementById(`widget-viewer-count-${w.id}`);
      if (countEl) {
        countEl.textContent = Number(w.mockViewerCount).toLocaleString();
        countEl.style.color = randChange >= 0 ? '#22c55e' : '#ef4444';
        setTimeout(() => countEl.style.color = '#ffffff', 800);
      }
    },

    // Emote Party Simulation
    triggerEmoteParty(w) {
      const container = document.getElementById(`widget-emote-party-${w.id}`);
      if (!container) return;
      const emotes = ['🔥', '🎉', '💖', '⭐', '🚀', '👑', '🎮', '✨', '👏', '🥳'];
      for (let i = 0; i < 20; i++) {
        setTimeout(() => {
          const em = document.createElement('div');
          const emo = emotes[Math.floor(Math.random() * emotes.length)];
          const left = Math.random() * 90;
          const dur = 1.5 + Math.random() * 1.5;
          const size = 24 + Math.random() * 24;
          em.style.cssText = `position: absolute; left: ${left}%; bottom: 0; font-size: ${size}px; pointer-events: none; user-select: none; animation: emoteFloatUp ${dur}s ease-out forwards;`;
          em.textContent = emo;
          container.appendChild(em);
          setTimeout(() => em.remove(), dur * 1000);
        }, i * 60);
      }
    }
  };

  // Load saved state from localStorage
  function loadSavedState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          state.pages = parsed;
          state.activePageId = parsed[0].id;
        }
      }
    } catch (e) {
      console.warn('Failed to load composer state from localStorage:', e);
    }
  }

  // Save current layout to localStorage
  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.pages));
      if (window.showToast) {
        window.showToast('บันทึกเลย์เอาต์หน้าจอเรียบร้อยแล้ว');
      }
    } catch (e) {
      console.error('Failed to save composer state:', e);
    }
  }

  // Get active page
  function getActivePage() {
    let p = state.pages.find(p => p.id === state.activePageId);
    if (!p && state.pages.length > 0) {
      p = state.pages[0];
      state.activePageId = p.id;
    }
    return p;
  }

  // Get selected widget
  function getSelectedWidget() {
    const page = getActivePage();
    if (!page) return null;
    return page.widgets.find(w => w.id === state.selectedWidgetId) || null;
  }

  // Initialize Composer Studio
  function initComposerStudio() {
    loadSavedState();
    renderPageTabs();
    setupCanvasEvents();
    setupToolbarEvents();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();

    // Auto-fit zoom when window is opened
    window.addEventListener('resize', autoFitCanvas);

    // Live clock updater
    if (!clockInterval) {
      clockInterval = setInterval(() => {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        document.querySelectorAll('.widget-clock-time').forEach(el => {
          el.textContent = timeStr;
        });
      }, 1000);
    }

    // Keyboard shortcuts
    window.addEventListener('keydown', handleKeyDown);

    // Left Drawer Expand Button Listener
    const btnExpand = document.getElementById('btnExpandCustPanel');
    if (btnExpand) {
      btnExpand.addEventListener('click', () => {
        state.customizerManuallyCollapsed = false;
        const leftPanel = document.getElementById('composerSidebarLeft');
        if (leftPanel) leftPanel.classList.remove('collapsed');
        btnExpand.classList.remove('visible');
      });
    }

    // Left Drawer Collapse Button Listener
    const btnCollapse = document.getElementById('btnCollapseCustPanel');
    if (btnCollapse) {
      btnCollapse.addEventListener('click', () => {
        state.customizerManuallyCollapsed = true;
        const leftPanel = document.getElementById('composerSidebarLeft');
        if (leftPanel) leftPanel.classList.add('collapsed');
        if (btnExpand) btnExpand.classList.add('visible');
      });
    }
  }

  // Auto-fit canvas into viewport
  function autoFitCanvas() {
    const viewport = document.getElementById('composerViewport');
    const stage = document.getElementById('composerCanvasStage');
    const outer = document.getElementById('composerCanvasOuter');
    if (!viewport || !stage || !outer) return;

    const vpW = viewport.clientWidth - 80;
    const vpH = viewport.clientHeight - 80;
    if (vpW <= 100 || vpH <= 100) return;

    const scaleX = vpW / CANVAS_WIDTH;
    const scaleY = vpH / CANVAS_HEIGHT;
    const fitScale = Math.min(scaleX, scaleY, 0.95);

    setZoom(fitScale);
  }

  // Set zoom level
  function setZoom(factor) {
    state.zoom = Math.max(0.15, Math.min(factor, 1.5));
    const stage = document.getElementById('composerCanvasStage');
    const outer = document.getElementById('composerCanvasOuter');
    const zoomVal = document.getElementById('composerZoomVal');

    if (stage) {
      stage.style.transform = `scale(${state.zoom})`;
    }
    if (outer) {
      outer.style.width = `${CANVAS_WIDTH * state.zoom}px`;
      outer.style.height = `${CANVAS_HEIGHT * state.zoom}px`;
    }
    if (zoomVal) {
      zoomVal.textContent = `${Math.round(state.zoom * 100)}%`;
    }
  }

  // Render Page Tabs
  function renderPageTabs() {
    const container = document.getElementById('composerPageTabs');
    if (!container) return;
    container.innerHTML = '';

    state.pages.forEach((page, idx) => {
      const tab = document.createElement('div');
      tab.className = `composer-page-tab ${page.id === state.activePageId ? 'active' : ''}`;
      tab.innerHTML = `
        <span>📄 ${page.name}</span>
        ${state.pages.length > 1 ? `<span class="composer-tab-close" data-id="${page.id}" title="ลบหน้านี้">✕</span>` : ''}
      `;
      tab.addEventListener('click', (e) => {
        if (e.target.classList.contains('composer-tab-close')) {
          e.stopPropagation();
          deletePage(page.id);
        } else {
          switchPage(page.id);
        }
      });
      container.appendChild(tab);
    });

    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className = 'composer-btn-add-page';
    addBtn.title = 'เพิ่มหน้าใหม่';
    addBtn.textContent = '+';
    addBtn.addEventListener('click', addNewPage);
    container.appendChild(addBtn);
  }

  // Switch Active Page
  function switchPage(pageId) {
    state.activePageId = pageId;
    state.selectedWidgetId = null;
    renderPageTabs();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    renderWidgetCustomizerPanel(null);
    saveState();
  }

  // Add New Page
  function addNewPage() {
    const pageNum = state.pages.length + 1;
    const newPage = {
      id: `page-${Date.now()}`,
      name: `หน้า ${pageNum}`,
      widgets: []
    };
    state.pages.push(newPage);
    switchPage(newPage.id);
    if (window.showToast) {
      window.showToast(`สร้าง${newPage.name}เรียบร้อยแล้ว`);
    }
  }

  // Delete Page
  function deletePage(pageId) {
    if (state.pages.length <= 1) return;
    const idx = state.pages.findIndex(p => p.id === pageId);
    if (idx !== -1) {
      state.pages.splice(idx, 1);
      if (state.activePageId === pageId) {
        state.activePageId = state.pages[0].id;
      }
      switchPage(state.activePageId);
    }
  }

  // Render Canvas Widgets
  function renderCanvasWidgets() {
    const stage = document.getElementById('composerCanvasStage');
    if (!stage) return;

    // Clear existing widgets, keep guides container
    const guides = document.getElementById('composerSmartGuides');
    stage.innerHTML = '';
    if (guides) stage.appendChild(guides);

    const page = getActivePage();
    if (!page) return;

    page.widgets.forEach(w => {
      if (w.hidden) return;

      const isDanmaku = w.isDanmaku || w.chatMode === 'danmaku';
      const el = document.createElement('div');
      el.className = `composer-widget ${w.id === state.selectedWidgetId ? 'selected' : ''} ${w.locked ? 'locked' : ''} ${isDanmaku ? 'widget-danmaku-full' : ''}`;
      el.id = `widget-${w.id}`;
      el.dataset.id = w.id;
      el.style.left = `${w.x}px`;
      el.style.top = `${w.y}px`;
      el.style.width = `${w.width}px`;
      el.style.height = `${w.height}px`;
      el.style.zIndex = w.z || 1;
      el.style.opacity = w.opacity ?? 1;

      // Badge
      const badge = document.createElement('div');
      badge.className = 'composer-widget-badge';
      badge.innerHTML = `<span>${getWidgetIcon(w.type)}</span> <span>${w.title}</span> <span style="opacity:0.75; font-size:10px;">${w.width}×${w.height}</span>`;
      el.appendChild(badge);

      // Inner Content
      const inner = document.createElement('div');
      inner.className = 'composer-widget-inner';
      inner.innerHTML = renderWidgetInnerHtml(w);
      el.appendChild(inner);

      // 8 Resize Handles - Do NOT add handles if noResize or Danmaku
      if (!w.noResize && !isDanmaku) {
        const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
        handles.forEach(h => {
          const handle = document.createElement('div');
          handle.className = `composer-resize-handle handle-${h}`;
          handle.dataset.handle = h;
          el.appendChild(handle);
        });
      }

      // Selection & Drag listeners
      el.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('composer-resize-handle')) {
          startResize(e, w, e.target.dataset.handle);
        } else {
          startDrag(e, w);
        }
      });
      el.addEventListener('click', () => {
        selectWidget(w.id);
      });

      stage.appendChild(el);
    });
  }

  // Get Widget Icon
  function getWidgetIcon(type) {
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
      browser: '🌐',
      now_playing: '🎵',
      emote_party: '🎉',
      ask: '🗳️',
      giveaway: '🎁',
      playroom: '🎮'
    };
    return icons[type] || '📦';
  }

  // Render Inner HTML according to Widget Type
  function renderWidgetInnerHtml(w) {
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      const theme = w.chatTheme || 'default';

      if (mode === 'danmaku') {
        const clr = w.fontColor || '#ffffff';
        const fsz = w.fontSize || 24;
        const dur = w.speed || 6;
        const op = w.opacity ?? 1;
        const stroke = w.textStroke !== false ? `-webkit-text-stroke: 1.5px ${w.strokeColor || '#000000'};` : '';
        const shadow = w.textShadow !== false ? 'filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8));' : '';
        return `
          <div class="composer-widget-inner widget-type-chat widget-danmaku-layer" id="widget-danmaku-feed-${w.id}" style="background:transparent; overflow:hidden; position:absolute; inset:0;">
            <div class="danmaku-bullet-item" style="top:25%; left:0; font-size:${fsz}px; color:${clr}; opacity:${op}; ${stroke} ${shadow} animation:danmakuBulletRun ${dur}s linear infinite;">
              🚀 ดันมากุวิ่งบนจอสด ยินดีต้อนรับทุกคนครับ! 🔥
            </div>
            <div class="danmaku-bullet-item" style="top:55%; left:0; font-size:${fsz}px; color:#38bdf8; opacity:${op}; ${stroke} ${shadow} animation:danmakuBulletRun ${dur}s linear 2.5s infinite;">
              ✨ ภาพคมชัด 60fps ลื่นไหลดีมากครับ
            </div>
          </div>
        `;
      }

      if (mode === 'balloon') {
        const bg = w.balloonBg || '#ffffff';
        const clr = w.balloonTextColor || '#0f172a';
        const radius = w.balloonRadius ?? 14;
        const fsz = w.fontSize || 15;
        const op = w.balloonOpacity ?? 0.95;
        return `
          <div class="composer-widget-inner widget-type-chat" id="widget-balloon-feed-${w.id}" style="background:transparent; position:relative; align-items:flex-start; padding:12px; overflow-y:auto; overflow-x:hidden;">
            <div style="background:${bg}; color:${clr}; padding:10px 16px; border-radius:${radius}px; font-weight:600; font-size:${fsz}px; box-shadow:0 6px 18px rgba(0,0,0,0.35); position:relative; margin-bottom:12px; max-width:90%; opacity:${op};">
              <div style="font-weight:700; font-size:12px; color:#6366f1; margin-bottom:3px;">Zack_Channel:</div>
              <div>สวัสดีครับทุกคน ยินดีต้อนรับสู่ไลฟ์สตรีมครับ! ✨</div>
              <svg style="position:absolute; bottom:-11px; left:22px; width:18px; height:12px; fill:${bg};" viewBox="0 0 18 12">
                <path d="M0 0 L18 0 L6 12 Z"/>
              </svg>
            </div>
          </div>
        `;
      }

      if (mode === 'character') {
        const charImg = w.imageUrl || './assets/dock_offline_character.png';
        const charName = w.characterName || 'Replie';
        const bubbleBg = w.charBubbleBg || 'rgba(255,255,255,0.96)';
        const textColor = w.charTextColor || '#0f172a';
        const fsz = w.charFontSize || 15;
        const isRight = w.charAlign === 'right';
        return `
          <div class="composer-widget-inner widget-type-chat" style="background:transparent; position:relative; display:flex; flex-direction:${isRight ? 'row-reverse' : 'row'}; align-items:flex-end; gap:14px; padding:12px; overflow:hidden;">
            <img id="widget-char-avatar-${w.id}" src="${charImg}" style="width:110px; height:110px; object-fit:contain; flex-shrink:0; transition:all 0.3s ease;" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
            <div style="background:${bubbleBg}; color:${textColor}; padding:12px 18px; border-radius:16px; font-size:${fsz}px; font-weight:600; box-shadow:0 8px 24px rgba(0,0,0,0.4); position:relative; flex:1;">
              <div style="font-size:11px; font-weight:700; color:#6366f1; margin-bottom:4px;">${charName}</div>
              <div id="widget-char-text-${w.id}">สวัสดีครับทุกคน! วันนี้ยินดีต้อนรับสู่ไลฟ์สตรีมนะครับ 🎮</div>
              <svg style="position:absolute; bottom:16px; ${isRight ? 'right:-10px; transform:scaleX(-1);' : 'left:-10px;'}; width:12px; height:16px; fill:${bubbleBg};" viewBox="0 0 12 16">
                <path d="M12 0 L12 16 L0 8 Z"/>
              </svg>
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
          <div id="widget-chat-feed-${w.id}" style="width:100%; height:100%; overflow-y:auto; overflow-x:hidden; display:flex; flex-direction:column; gap:6px;">
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

    if (w.type === 'character') {
      const charImg = w.imageUrl || './assets/dock_offline_character.png';
      const charName = w.characterName || 'Replie';
      return `
        <div class="composer-widget-inner widget-type-character">
          <img class="widget-character-img" src="${charImg}" alt="Character" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
          <div class="widget-character-name">${charName}</div>
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
          <div class="webcam-live-indicator">
            <div class="webcam-rec-dot"></div>
            <span>REC</span>
          </div>
          <div class="widget-webcam-label">📹 เว็บแคม (${w.ratio || '16:9'})</div>
          ${label ? `<div style="position:absolute; bottom:8px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.75); color:#fff; font-size:12px; font-weight:700; padding:2px 10px; border-radius:4px; white-space:nowrap;">${label}</div>` : ''}
          <div class="webcam-audio-vu">
            <div class="webcam-vu-bar" style="height:6px;"></div>
            <div class="webcam-vu-bar" style="height:12px;"></div>
            <div class="webcam-vu-bar" style="height:9px;"></div>
            <div class="webcam-vu-bar" style="height:14px;"></div>
            <div class="webcam-vu-bar" style="height:7px;"></div>
          </div>
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
      const count = w.mockViewerCount || 1250;
      return `
        <div class="composer-widget-inner widget-type-viewer">
          <div class="widget-viewer-dot" style="width:8px; height:8px; background:#22c55e; border-radius:50%; box-shadow:0 0 8px #22c55e; animation:pulse 1.5s infinite;"></div>
          <span style="font-size:12px; color:var(--dc-text-muted);">ยอดผู้ชมสด:</span>
          <span id="widget-viewer-count-${w.id}" style="font-weight:700; font-size:15px; color:#ffffff;">${Number(count).toLocaleString()}</span>
        </div>
      `;
    }

    if (w.type === 'emote_party') {
      return `
        <div class="composer-widget-inner widget-type-emote-party" id="widget-emote-party-${w.id}" style="position:relative; overflow:hidden;">
          <span style="font-size:24px;">🎉</span>
          <span>ปาร์ตี้อีโมทลอยสด</span>
        </div>
      `;
    }

    if (w.type === 'image') {
      return `
        <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#1e1f22; border:1px dashed rgba(255,255,255,0.2);">
          <span style="font-size:32px;">🖼️</span>
          <span style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">กรอบรูปภาพ</span>
        </div>
      `;
    }

    if (w.type === 'video') {
      return `
        <div class="composer-widget-inner widget-type-video">
          <span style="font-size:28px;">🎬</span>
          <div style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">วิดีโอลูป</div>
        </div>
      `;
    }

    if (w.type === 'alert') {
      return `
        <div class="composer-widget-inner widget-type-alert">
          <span style="font-size:24px;">🌐</span>
          <div style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">เบราว์เซอร์ URL</div>
        </div>
      `;
    }

    if (w.type === 'now_playing') {
      return `
        <div class="composer-widget-inner widget-type-now-playing">
          <span style="font-size:20px;">🎵</span>
          <div style="min-width:0;">
            <div style="font-weight:700; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${w.songTitle || 'Never Gonna Give You Up'}</div>
            <div style="font-size:11px; color:var(--dc-text-muted);">${w.artist || 'Rick Astley'}</div>
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#1e1f22; border:1px solid rgba(255,255,255,0.1);">
        <span>${w.title}</span>
      </div>
    `;
  }

  // Select Widget
  function selectWidget(widgetId) {
    state.selectedWidgetId = widgetId;
    state.customizerManuallyCollapsed = false;
    document.querySelectorAll('.composer-widget').forEach(el => {
      el.classList.toggle('selected', el.dataset.id === widgetId);
    });
    renderLayersList();
    updateTransformInspector();

    // Toggle Left Drawer
    const leftPanel = document.getElementById('composerSidebarLeft');
    const expandBtn = document.getElementById('btnExpandCustPanel');

    if (widgetId) {
      renderWidgetCustomizerPanel(widgetId);
      if (leftPanel) leftPanel.classList.remove('collapsed');
      if (expandBtn) expandBtn.classList.remove('visible');
    } else {
      if (leftPanel) leftPanel.classList.add('collapsed');
      if (expandBtn) expandBtn.classList.remove('visible');
    }
  }

  // Start Dragging Widget
  function startDrag(e, widget) {
    if (widget.locked || widget.noDrag || widget.isDanmaku || widget.chatMode === 'danmaku') {
      selectWidget(widget.id);
      return;
    }
    e.stopPropagation();
    selectWidget(widget.id);

    state.isDragging = true;
    state.dragStartMouseX = e.clientX;
    state.dragStartMouseY = e.clientY;
    state.dragStartWidgetX = widget.x;
    state.dragStartWidgetY = widget.y;

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }

  // Start Resizing Widget
  function startResize(e, widget, handle) {
    if (widget.locked || widget.noResize || widget.isDanmaku || widget.chatMode === 'danmaku') return;
    e.stopPropagation();
    selectWidget(widget.id);

    state.isResizing = true;
    state.activeResizeHandle = handle;
    state.dragStartMouseX = e.clientX;
    state.dragStartMouseY = e.clientY;
    state.dragStartWidgetX = widget.x;
    state.dragStartWidgetY = widget.y;
    state.dragStartWidgetW = widget.width;
    state.dragStartWidgetH = widget.height;

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }

  // Mouse Move for Drag & Resize
  function onMouseMove(e) {
    const widget = getSelectedWidget();
    if (!widget) return;

    const zoom = state.zoom || 0.45;
    const deltaX = (e.clientX - state.dragStartMouseX) / zoom;
    const deltaY = (e.clientY - state.dragStartMouseY) / zoom;

    if (state.isDragging) {
      let newX = Math.round(state.dragStartWidgetX + deltaX);
      let newY = Math.round(state.dragStartWidgetY + deltaY);

      if (state.snapGuides) {
        newX = Math.round(newX / 10) * 10;
        newY = Math.round(newY / 10) * 10;
      }

      widget.x = newX;
      widget.y = newY;
    } else if (state.isResizing) {
      const handle = state.activeResizeHandle;
      let newX = state.dragStartWidgetX;
      let newY = state.dragStartWidgetY;
      let newW = state.dragStartWidgetW;
      let newH = state.dragStartWidgetH;

      if (handle.includes('e')) newW = Math.max(50, state.dragStartWidgetW + deltaX);
      if (handle.includes('s')) newH = Math.max(30, state.dragStartWidgetH + deltaY);
      if (handle.includes('w')) {
        const potentialW = state.dragStartWidgetW - deltaX;
        if (potentialW >= 50) {
          newW = potentialW;
          newX = state.dragStartWidgetX + deltaX;
        }
      }
      if (handle.includes('n')) {
        const potentialH = state.dragStartWidgetH - deltaY;
        if (potentialH >= 30) {
          newH = potentialH;
          newY = state.dragStartWidgetY + deltaY;
        }
      }

      if (state.snapGuides) {
        newW = Math.round(newW / 10) * 10;
        newH = Math.round(newH / 10) * 10;
        newX = Math.round(newX / 10) * 10;
        newY = Math.round(newY / 10) * 10;
      }

      widget.x = newX;
      widget.y = newY;
      widget.width = newW;
      widget.height = newH;
    }

    const el = document.getElementById(`widget-${widget.id}`);
    if (el) {
      el.style.left = `${widget.x}px`;
      el.style.top = `${widget.y}px`;
      el.style.width = `${widget.width}px`;
      el.style.height = `${widget.height}px`;
      const badge = el.querySelector('.composer-widget-badge');
      if (badge) {
        badge.innerHTML = `<span>${getWidgetIcon(widget.type)}</span> <span>${widget.title}</span> <span style="opacity:0.75; font-size:10px;">${widget.width}×${widget.height}</span>`;
      }
    }

    updateTransformInspector();
  }

  // Mouse Up
  function onMouseUp() {
    if (state.isDragging || state.isResizing) {
      state.isDragging = false;
      state.isResizing = false;
      state.activeResizeHandle = null;
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      saveState();
    }
  }

  // Keyboard Shortcuts
  function handleKeyDown(e) {
    if (!state.selectedWidgetId) return;
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    const widget = getSelectedWidget();
    if (!widget) return;

    if (e.key === 'Delete' || e.key === 'Backspace') {
      e.preventDefault();
      deleteSelectedWidget();
    } else if (e.key === 'd' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      duplicateWidget(widget.id);
    } else if (e.key.startsWith('Arrow') && !widget.locked && !widget.noDrag && !widget.isDanmaku) {
      e.preventDefault();
      const step = e.shiftKey ? 10 : 1;
      if (e.key === 'ArrowLeft') widget.x -= step;
      if (e.key === 'ArrowRight') widget.x += step;
      if (e.key === 'ArrowUp') widget.y -= step;
      if (e.key === 'ArrowDown') widget.y += step;
      renderCanvasWidgets();
      updateTransformInspector();
      saveState();
    }
  }

  // Show Duplicate Confirmation Modal (Zero GPU Lockup)
  function showComposerConfirmModal({ title, message, confirmText, cancelText, onConfirm }) {
    const modal = document.getElementById('composerConfirmModal');
    if (!modal) {
      if (confirm(message)) onConfirm();
      return;
    }
    const titleEl = document.getElementById('composerConfirmTitle');
    const msgEl = document.getElementById('composerConfirmMsg');
    const okBtn = document.getElementById('btnComposerConfirmOk');
    const cancelBtn = document.getElementById('btnComposerConfirmCancel');

    if (titleEl) titleEl.textContent = title || 'วิดเจ็ตนี้มีอยู่ในหน้าจอแล้ว';
    if (msgEl) msgEl.textContent = message || 'หน้าจอนี้มีวิดเจ็ตนี้อยู่แล้ว คุณต้องการเพิ่มซ้ำอีกอันหรือไม่?';
    if (okBtn) okBtn.textContent = confirmText || '➕ ยืนยันเพิ่มซ้ำ';
    if (cancelBtn) cancelBtn.textContent = cancelText || 'ยกเลิก';

    modal.style.display = 'flex';

    const cleanup = () => {
      modal.style.display = 'none';
      okBtn.removeEventListener('click', handleOk);
      cancelBtn.removeEventListener('click', handleCancel);
    };

    const handleOk = () => {
      cleanup();
      if (typeof onConfirm === 'function') onConfirm();
    };

    const handleCancel = () => {
      cleanup();
    };

    okBtn.addEventListener('click', handleOk, { once: true });
    cancelBtn.addEventListener('click', handleCancel, { once: true });
  }

  // Check if widget exists before adding, warn if duplicate
  function checkAndAddWidget(type, chatMode = null) {
    const page = getActivePage();
    if (!page) return;

    let exists = false;
    let widgetName = '';
    if (type === 'chat') {
      const mode = chatMode || 'default';
      const names = {
        default: 'กล่องแชทมาตรฐาน',
        danmaku: 'แชทลอยหน้าจอ ดันมากุ',
        balloon: 'บอลลูนแชท',
        character: 'แชทตัวละคร'
      };
      widgetName = names[mode] || 'กล่องแชท';
      exists = page.widgets.some(w => w.type === 'chat' && (w.chatMode || 'default') === mode);
    } else {
      const names = {
        clock: 'นาฬิกาสตรีม',
        text: 'แถบข้อความประกาศ',
        character: 'ตัวละครพูด Replie',
        webcam: 'กรอบกล้องเว็บแคม',
        goal: 'เป้าหมายผู้ติดตาม',
        viewer: 'ตัวนับยอดผู้ชมสด',
        image: 'กรอบรูปภาพ',
        video: 'วิดีโอลูป',
        alert: 'เบราว์เซอร์ URL',
        now_playing: 'เพลงที่กำลังเล่น',
        emote_party: 'ปาร์ตี้อีโมทลอย'
      };
      widgetName = names[type] || 'วิดเจ็ตนี้';
      exists = page.widgets.some(w => w.type === type);
    }

    if (exists) {
      showComposerConfirmModal({
        title: 'วิดเจ็ตนี้มีอยู่ในหน้าจอแล้ว',
        message: `หน้าจอนี้มี "${widgetName}" อยู่แล้ว คุณต้องการเพิ่มซ้ำอีกอันหรือไม่?`,
        confirmText: '➕ ยืนยันเพิ่มซ้ำ',
        cancelText: 'ยกเลิก',
        onConfirm: () => {
          addWidget(type, chatMode);
        }
      });
    } else {
      addWidget(type, chatMode);
    }
  }

  // Add a new Widget to canvas
  function addWidget(type, chatMode = null) {
    const page = getActivePage();
    if (!page) return;

    const presets = {
      chat: {
        title: 'กล่องแชทมาตรฐาน',
        width: 440,
        height: 600,
        chatMode: chatMode || 'default',
        chatTheme: 'default',
        fontSize: 15,
        fontColor: '#ffffff',
        bgColor: '#1e1f22',
        bgOpacity: 0.85,
        boxRadius: 8
      },
      clock: { title: 'นาฬิกาสตรีม', width: 280, height: 80, clockTheme: 'cyberpunk', clockFormat: '24', showSeconds: true, fontSize: 26, fontColor: '#38bdf8' },
      text: { title: 'แถบข้อความประกาศ', width: 800, height: 50, text: 'ข้อความสตรีมสดใหม่ ยินดีต้อนรับทุกคนครับ!', textMode: 'ticker', fontSize: 18, fontColor: '#ffffff' },
      character: { title: 'ตัวละครพูด Replie', width: 340, height: 420, characterName: 'Replie', imageUrl: './assets/dock_offline_character.png' },
      webcam: { title: 'กรอบกล้องเว็บแคม', width: 480, height: 270, ratio: '16:9', borderColor: '#5865f2', borderWidth: 4, borderRadius: 8, glow: true, showStreamerName: true, streamerName: 'Streamer LIVE' },
      goal: { title: 'เป้าหมายผู้ติดตาม', width: 420, height: 80, goalTitle: 'เป้าหมายผู้ติดตาม', goalCurrent: 650, goalTarget: 1000, goalUnit: 'คน' },
      viewer: { title: 'ตัวนับยอดผู้ชมสด', width: 240, height: 55, viewerTheme: 'pill', mockViewerCount: 1250 },
      image: { title: 'กรอบรูปภาพแบนเนอร์', width: 340, height: 200, fitMode: 'contain' },
      video: { title: 'วิดีโอลูป', width: 480, height: 270, loop: true },
      alert: { title: 'เบราว์เซอร์ URL', width: 400, height: 300, alertUrl: 'https://overlay.example.com' },
      now_playing: { title: 'เพลงที่กำลังเล่น', width: 340, height: 75, songTitle: 'Never Gonna Give You Up', artist: 'Rick Astley' },
      emote_party: { title: 'ปาร์ตี้อีโมทลอย', width: 300, height: 200 }
    };

    const preset = presets[type] || { title: 'วิดเจ็ตใหม่', width: 300, height: 200 };

    if (type === 'chat') {
      const mode = chatMode || 'default';
      preset.chatMode = mode;
      if (mode === 'danmaku') {
        preset.title = 'แชทลอยหน้าจอ ดันมากุ';
        preset.width = CANVAS_WIDTH;
        preset.height = CANVAS_HEIGHT;
        preset.isDanmaku = true;
        preset.noResize = true;
        preset.noDrag = true;
        preset.fontSize = 24;
        preset.fontColor = '#ffffff';
        preset.speed = 6;
        preset.slider_zone = 'middle';
      } else if (mode === 'balloon') {
        preset.title = 'บอลลูนแชท';
        preset.width = 460;
        preset.height = 480;
        preset.balloonBg = '#ffffff';
        preset.balloonTextColor = '#0f172a';
        preset.balloonRadius = 14;
        preset.balloonOpacity = 0.95;
        preset.fontSize = 15;
      } else if (mode === 'character') {
        preset.title = 'แชทตัวละคร';
        preset.width = 480;
        preset.height = 480;
        preset.characterName = 'Replie';
        preset.imageUrl = './assets/dock_offline_character.png';
        preset.charBubbleBg = 'rgba(255,255,255,0.96)';
        preset.charTextColor = '#0f172a';
        preset.charFontSize = 15;
      } else {
        preset.title = 'กล่องแชทมาตรฐาน';
      }
    }

    const newWidget = {
      id: `w-${type}-${Date.now()}`,
      type: type,
      title: preset.title,
      x: (preset.isDanmaku ? 0 : Math.round(CANVAS_WIDTH / 2 - preset.width / 2)),
      y: (preset.isDanmaku ? 0 : Math.round(CANVAS_HEIGHT / 2 - preset.height / 2)),
      width: preset.width,
      height: preset.height,
      z: page.widgets.length + 1,
      opacity: 1,
      locked: false,
      hidden: false,
      text: preset.text || '',
      ...preset
    };

    page.widgets.push(newWidget);
    renderCanvasWidgets();
    selectWidget(newWidget.id);
    saveState();

    // Visual Flash & Temporary Indicator
    setTimeout(() => {
      const el = document.getElementById(`widget-${newWidget.id}`);
      if (el) {
        el.classList.add('composer-widget-flash-highlight');
        const ind = document.createElement('div');
        ind.className = 'composer-widget-new-indicator';
        ind.textContent = `✨ เพิ่ม${preset.title}แล้ว`;
        el.appendChild(ind);
        setTimeout(() => {
          el.classList.remove('composer-widget-flash-highlight');
          ind.remove();
        }, 2200);

        // Center within outer scroll if not danmaku
        const outer = document.getElementById('composerCanvasOuter');
        if (outer && !preset.isDanmaku) {
          const zoom = (state.zoom || 45) / 100;
          const targetX = newWidget.x * zoom;
          const targetY = newWidget.y * zoom;
          outer.scrollTo({
            left: Math.max(0, targetX - outer.clientWidth / 2 + (newWidget.width * zoom) / 2),
            top: Math.max(0, targetY - outer.clientHeight / 2 + (newWidget.height * zoom) / 2),
            behavior: 'smooth'
          });
        }
      }
    }, 50);

    if (window.showToast) {
      window.showToast(`เพิ่ม${preset.title}บนหน้าจอแล้ว`);
    }
  }

  // Duplicate Widget
  function duplicateWidget(id) {
    const page = getActivePage();
    if (!page) return;
    const orig = page.widgets.find(w => w.id === id);
    if (!orig) return;

    const newWidget = JSON.parse(JSON.stringify(orig));
    newWidget.id = `w-${orig.type}-${Date.now()}`;
    newWidget.title = `${orig.title} คัดลอก`;
    if (!newWidget.isDanmaku && newWidget.chatMode !== 'danmaku') {
      newWidget.x += 30;
      newWidget.y += 30;
    }
    newWidget.z = page.widgets.length + 1;

    page.widgets.push(newWidget);
    renderCanvasWidgets();
    selectWidget(newWidget.id);
    saveState();
  }

  // Delete selected widget
  function deleteSelectedWidget() {
    const page = getActivePage();
    if (!page || !state.selectedWidgetId) return;

    const idx = page.widgets.findIndex(w => w.id === state.selectedWidgetId);
    if (idx !== -1) {
      const removed = page.widgets.splice(idx, 1)[0];
      state.selectedWidgetId = null;
      renderCanvasWidgets();
      renderLayersList();
      updateTransformInspector();
      renderWidgetCustomizerPanel(null);
      saveState();

      if (window.showToast) {
        window.showToast(`ลบ${removed.title}เรียบร้อยแล้ว`);
      }
    }
  }

  // Render Layers List
  function renderLayersList() {
    const list = document.getElementById('composerLayersList');
    if (!list) return;

    const page = getActivePage();
    if (!page) {
      list.innerHTML = '<div style="font-size:11.5px; color:var(--dc-text-muted); padding:10px;">ไม่มีวิดเจ็ต</div>';
      return;
    }

    list.innerHTML = '';
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));

    sorted.forEach(w => {
      const item = document.createElement('div');
      item.className = `composer-layer-item ${w.id === state.selectedWidgetId ? 'active' : ''}`;
      item.dataset.id = w.id;
      item.innerHTML = `
        <span class="composer-layer-icon">${getWidgetIcon(w.type)}</span>
        <span class="composer-layer-name" title="${w.title}">${w.title}</span>
        <div class="composer-layer-actions">
          <button type="button" class="composer-btn-layer-action" data-action="toggle-hide" title="${w.hidden ? 'แสดง' : 'ซ่อน'}">
            ${w.hidden ? '👁️‍🗨️' : '👁️'}
          </button>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-lock" title="${w.locked ? 'ปลดล็อค' : 'ล็อค'}">
            ${w.locked ? '🔒' : '🔓'}
          </button>
          <button type="button" class="composer-btn-layer-action close-red" data-action="delete" title="ลบวิดเจ็ต">
            ✕
          </button>
        </div>
      `;

      item.addEventListener('click', (e) => {
        const actionBtn = e.target.closest('.composer-btn-layer-action');
        if (actionBtn) {
          e.stopPropagation();
          const act = actionBtn.dataset.action;
          if (act === 'toggle-hide') {
            w.hidden = !w.hidden;
            renderCanvasWidgets();
            renderLayersList();
            saveState();
          } else if (act === 'toggle-lock') {
            w.locked = !w.locked;
            renderCanvasWidgets();
            renderLayersList();
            saveState();
          } else if (act === 'delete') {
            selectWidget(w.id);
            deleteSelectedWidget();
          }
        } else {
          selectWidget(w.id);
        }
      });

      list.appendChild(item);
    });
  }

  // Align Widget
  function alignWidget(direction) {
    const widget = getSelectedWidget();
    if (!widget || widget.locked || widget.isDanmaku || widget.chatMode === 'danmaku') return;

    if (direction === 'left') widget.x = 0;
    if (direction === 'center') widget.x = Math.round(CANVAS_WIDTH / 2 - widget.width / 2);
    if (direction === 'right') widget.x = CANVAS_WIDTH - widget.width;
    if (direction === 'top') widget.y = 0;
    if (direction === 'middle') widget.y = Math.round(CANVAS_HEIGHT / 2 - widget.height / 2);
    if (direction === 'bottom') widget.y = CANVAS_HEIGHT - widget.height;

    renderCanvasWidgets();
    updateTransformInspector();
    saveState();
  }

  // Update Transform Inspector
  function updateTransformInspector() {
    const widget = getSelectedWidget();
    const inpX = document.getElementById('compPropX');
    const inpY = document.getElementById('compPropY');
    const inpW = document.getElementById('compPropW');
    const inpH = document.getElementById('compPropH');
    const inpOp = document.getElementById('compPropOp');

    if (!widget) {
      if (inpX) { inpX.value = '-'; inpX.disabled = false; }
      if (inpY) { inpY.value = '-'; inpY.disabled = false; }
      if (inpW) { inpW.value = '-'; inpW.disabled = false; }
      if (inpH) { inpH.value = '-'; inpH.disabled = false; }
      if (inpOp) inpOp.value = '100%';
      return;
    }

    const isDanmaku = widget.isDanmaku || widget.chatMode === 'danmaku';
    if (inpX) { inpX.value = isDanmaku ? 0 : widget.x; inpX.disabled = isDanmaku; }
    if (inpY) { inpY.value = isDanmaku ? 0 : widget.y; inpY.disabled = isDanmaku; }
    if (inpW) { inpW.value = isDanmaku ? CANVAS_WIDTH : widget.width; inpW.disabled = isDanmaku; }
    if (inpH) { inpH.value = isDanmaku ? CANVAS_HEIGHT : widget.height; inpH.disabled = isDanmaku; }
    if (inpOp) inpOp.value = isDanmaku ? `${Math.round((widget.opacity ?? 1) * 100)}% (ล็อคเต็มจอ)` : `${Math.round((widget.opacity ?? 1) * 100)}%`;
  }

  // Setup Canvas Events
  function setupCanvasEvents() {
    const viewport = document.getElementById('composerViewport');
    if (!viewport) return;

    viewport.addEventListener('click', (e) => {
      if (e.target.id === 'composerViewport' || e.target.id === 'composerCanvasStage' || e.target.id === 'composerCanvasOuter') {
        selectWidget(null);
      }
    });
  }

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

    let dispTitle = w.title;
    let dispType = 'การปรับแต่งวิดเจ็ต';
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        dispTitle = 'แชทลอยหน้าจอ ดันมากุ';
        dispType = 'วิดเจ็ตแชทลอยหน้าจอแบบ Danmaku';
      } else if (mode === 'balloon') {
        dispTitle = 'บอลลูนแชท';
        dispType = 'วิดเจ็ตแชทสไตล์บอลลูนคำพูด';
      } else if (mode === 'character') {
        dispTitle = 'แชทตัวละคร';
        dispType = 'วิดเจ็ตแชทพร้อมตัวละครสนทนา';
      } else {
        dispTitle = 'กล่องแชทมาตรฐาน';
        dispType = 'วิดเจ็ตกล่องแชทสด';
      }
    } else {
      const typeNames = {
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
      dispType = typeNames[w.type] || 'การปรับแต่งวิดเจ็ต';
    }

    if (iconEl) iconEl.textContent = getWidgetIcon(w.type);
    if (titleEl) titleEl.textContent = dispTitle;
    if (typeEl) typeEl.textContent = dispType;

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

    // Build Demo Action Bar HTML
    let demoHtml = '';
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">⚡ ทดสอบกระสุนดันมากุ</span>
              <span style="font-size:11px; color:#94a3b8;">วิ่งบนจอตามโซน</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuLoop">▶ เล่นกระสุนดันมากุสด</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuSingle">⚡ ปล่อย 1 ข้อความ</button>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">💬 ทดสอบบอลลูนคำพูด</span>
              <span style="font-size:11px; color:#94a3b8;">บอลลูนเด้งสด</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoBalloonSingle">💬 ส่งบอลลูน 1 ข้อความ</button>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">🎭 ทดสอบบทพูดตัวละคร</span>
              <span style="font-size:11px; color:#94a3b8;">ตัวละครขยับพร้อมคำพูด</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoCharTalk">▶ ทดสอบบทพูดตัวละครสด</button>
            </div>
          </div>
        `;
      } else {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">🎮 ทดสอบเล่นเดโมสด</span>
              <span style="font-size:11px; color:#94a3b8;">จำลองแชทแบบสตรีมจริง</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatLoop">▶ เล่นจำลองแชทสด</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatSingle">➕ ส่งแชท 1 ข้อความ</button>
            </div>
          </div>
        `;
      }
    } else if (w.type === 'clock') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🕒 ทดสอบสลับรูปแบบเวลา</span>
            <span style="font-size:11px; color:#94a3b8;">นาฬิกาเดินสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockToggle">🕒 สลับ 12 / 24 ชม.</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockSecs">⏱️ สลับแสดงวินาที</button>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🔤 ทดสอบตัววิ่ง Marquee</span>
            <span style="font-size:11px; color:#94a3b8;">ข้อความเลื่อนวิ่งสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoTextTicker">▶ สลับโหมดตัววิ่ง</button>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">📹 ทดสอบสถานะเว็บแคม</span>
            <span style="font-size:11px; color:#94a3b8;">ไฟกระพริบ REC และมิเตอร์เสียง</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoWebcamRec">🔴 สลับไฟสถานะ REC</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoWebcamAudio">🎙️ ทดสอบมิเตอร์เสียงสด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'goal') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎯 ทดสอบยอดเป้าหมาย</span>
            <span style="font-size:11px; color:#94a3b8;">หลอดเพิ่มแบบอนิเมชัน</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalPlus">🎉 จำลองผู้ติดตามใหม่ (+50)</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalReset">🔄 รีเซ็ตยอด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'viewer') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">👥 ทดสอบยอดผู้ชมสด</span>
            <span style="font-size:11px; color:#94a3b8;">สุ่มความผันผวนยอดคนดู</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerPulse">👥 สุ่มยอดผู้ชมสด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'emote_party') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎉 ทดสอบพลุปาร์ตี้อีโมท</span>
            <span style="font-size:11px; color:#94a3b8;">พุ่งกระจายเต็มจอ</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoEmoteParty">🎉 จุดพลุปาร์ตี้อีโมท</button>
          </div>
        </div>
      `;
    }

    let specificHtml = '';

    // ==========================================
    // 1. CHAT WIDGET
    // ==========================================
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';

      if (mode === 'danmaku') {
        specificHtml = `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">⚡ ตั้งค่าดันมากุวิ่งบนจอ</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">ความเร็วตัววิ่ง</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuSpeed" min="3" max="12" value="${w.speed || 6}">
                  <span class="cwc-slider-val" id="compChatDanmakuSpeedVal">${w.speed || 6} วินาที</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuFontSize" min="16" max="48" value="${w.fontSize || 24}">
                  <span class="cwc-slider-val" id="compChatDanmakuFontSizeVal">${w.fontSize || 24}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">พื้นที่แสดงผลบนจอ</span>
                <select class="cwc-select" id="compChatDanmakuZone">
                  <option value="middle" ${w.slider_zone === 'middle' ? 'selected' : ''}>แถบกลางหน้าจอ</option>
                  <option value="top" ${w.slider_zone === 'top' ? 'selected' : ''}>ครึ่งบนของหน้าจอ</option>
                  <option value="bottom" ${w.slider_zone === 'bottom' ? 'selected' : ''}>ครึ่งล่างของหน้าจอ</option>
                  <option value="full" ${w.slider_zone === 'full' ? 'selected' : ''}>ทั้งหน้าจอผืนผ้าใบ</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compChatDanmakuColor" value="${w.fontColor || '#ffffff'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">เส้นขอบตัวอักษร</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compChatDanmakuStroke" ${w.textStroke !== false ? 'checked' : ''}>
                  <span class="cwc-slider-round"></span>
                </label>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีเส้นขอบ</span>
                <input type="color" class="cwc-color-pick" id="compChatDanmakuStrokeColor" value="${w.strokeColor || '#000000'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งแสง</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuOpacity" min="10" max="100" value="${Math.round((w.opacity ?? 1) * 100)}">
                  <span class="cwc-slider-val" id="compChatDanmakuOpacityVal">${Math.round((w.opacity ?? 1) * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        specificHtml = `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">💬 ตั้งค่าบอลลูนคำพูด</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonFontSize" min="12" max="28" value="${w.fontSize || 15}">
                  <span class="cwc-slider-val" id="compChatBalloonFontSizeVal">${w.fontSize || 15}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compChatBalloonTextColor" value="${w.balloonTextColor || '#0f172a'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีพื้นหลังบอลลูน</span>
                <input type="color" class="cwc-color-pick" id="compChatBalloonBg" value="${w.balloonBg || '#ffffff'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความทึบแสงบอลลูน</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonOpacity" min="10" max="100" value="${Math.round((w.balloonOpacity ?? 0.95) * 100)}">
                  <span class="cwc-slider-val" id="compChatBalloonOpacityVal">${Math.round((w.balloonOpacity ?? 0.95) * 100)}%</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโค้งมนมุม</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonRadius" min="0" max="32" value="${w.balloonRadius ?? 14}">
                  <span class="cwc-slider-val" id="compChatBalloonRadiusVal">${w.balloonRadius ?? 14}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        specificHtml = `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">🎭 ตั้งค่าแชทตัวละคร</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row" style="flex-direction:column; align-items:flex-start; gap:8px;">
                <span class="comp-field-label">รูปภาพตัวละคร</span>
                <div style="display:flex; gap:6px; width:100%;">
                  <button type="button" class="btn-comp-demo-action" id="btnCharPresetReplie">👧 Replie</button>
                  <button type="button" class="btn-comp-demo-action" id="btnCharPresetCat">🐱 แมว VTuber</button>
                  <button type="button" class="btn-comp-demo-action" id="btnCharPresetAnime">🌸 อนิเมะ</button>
                </div>
                <div style="display:flex; gap:6px; width:100%; margin-top:4px;">
                  <input type="file" id="compCharFileInput" accept="image/*" style="display:none;">
                  <button type="button" class="btn-comp-demo-action" id="btnUploadCharImg" style="width:100%; justify-content:center;">📁 อัปโหลดรูปจากเครื่อง</button>
                </div>
                <input type="text" class="cwc-input" id="compCharImgUrl" placeholder="หรือวางลิงก์รูป URL" value="${w.imageUrl || ''}" style="width:100%; margin-top:4px;">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ชื่อตัวละคร</span>
                <input type="text" class="cwc-input" id="compCharName" value="${w.characterName || 'Replie'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ตำแหน่งตัวละคร</span>
                <select class="cwc-select" id="compCharAlign">
                  <option value="left" ${w.charAlign !== 'right' ? 'selected' : ''}>ชิดซ้าย</option>
                  <option value="right" ${w.charAlign === 'right' ? 'selected' : ''}>ชิดขวา</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีกล่องคำพูด</span>
                <input type="color" class="cwc-color-pick" id="compCharBubbleBg" value="${w.charBubbleBg || '#ffffff'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compCharTextColor" value="${w.charTextColor || '#0f172a'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compCharFontSize" min="12" max="28" value="${w.charFontSize || 15}">
                  <span class="cwc-slider-val" id="compCharFontSizeVal">${w.charFontSize || 15}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else {
        const subTab = state.chatSubTab || 'standard';
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
          <!-- 2 Tabs: ค่ามาตรฐาน & ธีมสำเร็จรูป -->
          <div class="cwc-tabs-bar" style="border-radius:8px; margin-bottom:10px;">
            <button type="button" class="cwc-tab-btn ${subTab === 'standard' ? 'active' : ''}" id="tabSubStandard">
              ⚙️ ค่ามาตรฐาน
            </button>
            <button type="button" class="cwc-tab-btn ${subTab === 'theme' ? 'active' : ''}" id="tabSubTheme">
              🎨 ธีมสำเร็จรูป
            </button>
          </div>

          ${subTab === 'theme' ? `
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
          ` : `
            <div class="comp-card-section">
              <div class="comp-card-header"><span class="comp-card-title">⚙️ ค่ามาตรฐานกล่องแชท</span></div>
              <div class="comp-card-body">
                <div class="comp-field-row">
                  <span class="comp-field-label">แบบอักษร</span>
                  <select class="cwc-select" id="compChatFontFamily">
                    <option value="Kanit" ${w.fontFamily === 'Kanit' ? 'selected' : ''}>Kanit</option>
                    <option value="Sarabun" ${w.fontFamily === 'Sarabun' ? 'selected' : ''}>Sarabun</option>
                    <option value="Prompt" ${w.fontFamily === 'Prompt' ? 'selected' : ''}>Prompt</option>
                    <option value="Chonburi" ${w.fontFamily === 'Chonburi' ? 'selected' : ''}>Chonburi</option>
                    <option value="JetBrains Mono" ${w.fontFamily === 'JetBrains Mono' ? 'selected' : ''}>JetBrains Mono</option>
                  </select>
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">ขนาดตัวอักษร</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatFontSize" min="12" max="32" value="${w.fontSize || 15}">
                    <span class="cwc-slider-val" id="compChatFontSizeVal">${w.fontSize || 15}px</span>
                  </div>
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">สีตัวอักษร</span>
                  <input type="color" class="cwc-color-pick" id="compChatFontColor" value="${w.fontColor || '#ffffff'}">
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">สีพื้นหลังกล่อง</span>
                  <input type="color" class="cwc-color-pick" id="compChatBgColor" value="${w.bgColor || '#1e1f22'}">
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">ความทึบแสงพื้นหลัง</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatBgOpacity" min="0" max="100" value="${Math.round((w.bgOpacity ?? 0.85) * 100)}">
                    <span class="cwc-slider-val" id="compChatBgOpacityVal">${Math.round((w.bgOpacity ?? 0.85) * 100)}%</span>
                  </div>
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">ความโค้งมนมุม</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatBoxRadius" min="0" max="32" value="${w.boxRadius ?? 8}">
                    <span class="cwc-slider-val" id="compChatBoxRadiusVal">${w.boxRadius ?? 8}px</span>
                  </div>
                </div>
              </div>
            </div>
          `}
        `;
      }
    } else if (w.type === 'clock') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🕒 ตั้งค่านาฬิกาสตรีม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ธีมนาฬิกา</span>
              <select class="cwc-select" id="compClockTheme">
                <option value="cyberpunk" ${w.clockTheme === 'cyberpunk' ? 'selected' : ''}>Cyberpunk</option>
                <option value="neon" ${w.clockTheme === 'neon' ? 'selected' : ''}>Neon Glow</option>
                <option value="flip" ${w.clockTheme === 'flip' ? 'selected' : ''}>Flip Clock</option>
                <option value="minimal" ${w.clockTheme === 'minimal' ? 'selected' : ''}>Minimal Clean</option>
                <option value="digital" ${w.clockTheme === 'digital' ? 'selected' : ''}>Digital Red</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบเวลา</span>
              <select class="cwc-select" id="compClockFormat">
                <option value="24" ${w.clockFormat === '24' ? 'selected' : ''}>24 ชั่วโมง</option>
                <option value="12" ${w.clockFormat === '12' ? 'selected' : ''}>12 ชั่วโมง พร้อม AM / PM</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงเข็มวินาที</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compClockShowSeconds" ${w.showSeconds !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดตัวอักษร</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compClockFontSize" min="16" max="64" value="${w.fontSize || 26}">
                <span class="cwc-slider-val" id="compClockFontSizeVal">${w.fontSize || 26}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compClockFontColor" value="${w.fontColor || '#38bdf8'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ตั้งค่าข้อความประกาศ</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ข้อความ</span>
              <textarea class="cwc-input" id="compTextInput" rows="2" style="width:100%; resize:vertical;">${w.text || ''}</textarea>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดแสดงผล</span>
              <select class="cwc-select" id="compTextMode">
                <option value="ticker" ${w.textMode === 'ticker' ? 'selected' : ''}>ตัววิ่ง Marquee สด</option>
                <option value="static" ${w.textMode === 'static' ? 'selected' : ''}>ข้อความนิ่ง</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="48" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compTextFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compTextFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <input type="color" class="cwc-color-pick" id="compTextBgColor" value="${w.bgColor || '#141923'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📹 ตั้งค่ากรอบเว็บแคม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">อัตราส่วนภาพ</span>
              <select class="cwc-select" id="compWebcamRatio">
                <option value="16:9" ${w.ratio === '16:9' ? 'selected' : ''}>16:9 แนวนอนมาตรฐาน</option>
                <option value="4:3" ${w.ratio === '4:3' ? 'selected' : ''}>4:3 คลาสสิก</option>
                <option value="1:1" ${w.ratio === '1:1' ? 'selected' : ''}>1:1 จัตุรัส</option>
                <option value="9:16" ${w.ratio === '9:16' ? 'selected' : ''}>9:16 แนวตั้งมือถือ</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาเส้นขอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamBorderWidth" min="0" max="12" value="${w.borderWidth ?? 4}">
                <span class="cwc-slider-val" id="compWebcamBorderWidthVal">${w.borderWidth ?? 4}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compWebcamBorderColor" value="${w.borderColor || '#5865f2'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมนมุม</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamBorderRadius" min="0" max="32" value="${w.borderRadius ?? 8}">
                <span class="cwc-slider-val" id="compWebcamBorderRadiusVal">${w.borderRadius ?? 8}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสงเรืองรอบกรอบ</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compWebcamGlow" ${w.glow ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงป้ายชื่อสตรีมเมอร์</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compWebcamShowName" ${w.showStreamerName ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อสตรีมเมอร์</span>
              <input type="text" class="cwc-input" id="compWebcamName" value="${w.streamerName || 'Streamer LIVE'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'goal') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎯 ตั้งค่าเป้าหมายผู้ติดตาม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อเป้าหมาย</span>
              <input type="text" class="cwc-input" id="compGoalTitle" value="${w.goalTitle || 'เป้าหมายผู้ติดตาม'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ยอดปัจจุบัน</span>
              <input type="number" class="cwc-input" id="compGoalCurrent" value="${w.goalCurrent ?? 650}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ยอดเป้าหมาย</span>
              <input type="number" class="cwc-input" id="compGoalTarget" value="${w.goalTarget ?? 1000}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">หน่วยนับ</span>
              <input type="text" class="cwc-input" id="compGoalUnit" value="${w.goalUnit || 'คน'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'viewer') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">👥 ตั้งค่าตัวนับยอดผู้ชมสด</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">สไตล์ป้ายสถานะ</span>
              <select class="cwc-select" id="compViewerTheme">
                <option value="pill" ${w.viewerTheme === 'pill' ? 'selected' : ''}>Pill Badge</option>
                <option value="minimal" ${w.viewerTheme === 'minimal' ? 'selected' : ''}>Minimal Text</option>
              </select>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'character') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎭 ตั้งค่าตัวละคร Replie</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อตัวละคร</span>
              <input type="text" class="cwc-input" id="compCharWidgetName" value="${w.characterName || 'Replie'}">
            </div>
          </div>
        </div>
      `;
    }

    bodyEl.innerHTML = demoHtml + specificHtml;

    // Bind Demo Action Buttons
    const btnDemoChatLoop = document.getElementById('btnDemoChatLoop');
    const btnDemoChatSingle = document.getElementById('btnDemoChatSingle');
    if (btnDemoChatLoop) btnDemoChatLoop.addEventListener('click', () => ComposerDemoManager.toggleChatLoop(w, btnDemoChatLoop));
    if (btnDemoChatSingle) btnDemoChatSingle.addEventListener('click', () => ComposerDemoManager.sendChatMsg(w));

    const btnDemoDanmakuLoop = document.getElementById('btnDemoDanmakuLoop');
    const btnDemoDanmakuSingle = document.getElementById('btnDemoDanmakuSingle');
    if (btnDemoDanmakuLoop) btnDemoDanmakuLoop.addEventListener('click', () => ComposerDemoManager.toggleDanmakuLoop(w, btnDemoDanmakuLoop));
    if (btnDemoDanmakuSingle) btnDemoDanmakuSingle.addEventListener('click', () => ComposerDemoManager.sendDanmakuMsg(w));

    const btnDemoBalloonSingle = document.getElementById('btnDemoBalloonSingle');
    if (btnDemoBalloonSingle) btnDemoBalloonSingle.addEventListener('click', () => ComposerDemoManager.sendBalloonMsg(w));

    const btnDemoCharTalk = document.getElementById('btnDemoCharTalk');
    if (btnDemoCharTalk) btnDemoCharTalk.addEventListener('click', () => ComposerDemoManager.triggerCharacterTalk(w));

    const btnDemoClockToggle = document.getElementById('btnDemoClockToggle');
    if (btnDemoClockToggle) {
      btnDemoClockToggle.addEventListener('click', () => {
        w.clockFormat = w.clockFormat === '12' ? '24' : '12';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoClockSecs = document.getElementById('btnDemoClockSecs');
    if (btnDemoClockSecs) {
      btnDemoClockSecs.addEventListener('click', () => {
        w.showSeconds = w.showSeconds === false ? true : false;
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoTextTicker = document.getElementById('btnDemoTextTicker');
    if (btnDemoTextTicker) {
      btnDemoTextTicker.addEventListener('click', () => {
        w.textMode = w.textMode === 'ticker' ? 'static' : 'ticker';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoWebcamRec = document.getElementById('btnDemoWebcamRec');
    if (btnDemoWebcamRec) {
      btnDemoWebcamRec.addEventListener('click', () => {
        const dot = document.querySelector(`#widget-${w.id} .webcam-rec-dot`);
        if (dot) dot.style.display = dot.style.display === 'none' ? 'block' : 'none';
      });
    }

    const btnDemoWebcamAudio = document.getElementById('btnDemoWebcamAudio');
    if (btnDemoWebcamAudio) {
      btnDemoWebcamAudio.addEventListener('click', () => {
        const bars = document.querySelectorAll(`#widget-${w.id} .webcam-vu-bar`);
        bars.forEach(b => {
          b.style.height = (4 + Math.random() * 12) + 'px';
        });
      });
    }

    const btnDemoGoalPlus = document.getElementById('btnDemoGoalPlus');
    const btnDemoGoalReset = document.getElementById('btnDemoGoalReset');
    if (btnDemoGoalPlus) btnDemoGoalPlus.addEventListener('click', () => ComposerDemoManager.triggerGoalPlus(w));
    if (btnDemoGoalReset) btnDemoGoalReset.addEventListener('click', () => ComposerDemoManager.triggerGoalReset(w));

    const btnDemoViewerPulse = document.getElementById('btnDemoViewerPulse');
    if (btnDemoViewerPulse) btnDemoViewerPulse.addEventListener('click', () => ComposerDemoManager.triggerViewerPulse(w));

    const btnDemoEmoteParty = document.getElementById('btnDemoEmoteParty');
    if (btnDemoEmoteParty) btnDemoEmoteParty.addEventListener('click', () => ComposerDemoManager.triggerEmoteParty(w));

    // Bind Mode-Specific Inputs
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        bindField('compChatDanmakuSpeed', 'speed', 'number');
        bindField('compChatDanmakuFontSize', 'fontSize', 'number', 'px');
        bindField('compChatDanmakuZone', 'slider_zone');
        bindField('compChatDanmakuColor', 'fontColor');
        bindField('compChatDanmakuStroke', 'textStroke', 'checkbox');
        bindField('compChatDanmakuStrokeColor', 'strokeColor');
        bindField('compChatDanmakuOpacity', 'opacity', 'opacity');
      } else if (mode === 'balloon') {
        bindField('compChatBalloonFontSize', 'fontSize', 'number', 'px');
        bindField('compChatBalloonTextColor', 'balloonTextColor');
        bindField('compChatBalloonBg', 'balloonBg');
        bindField('compChatBalloonOpacity', 'balloonOpacity', 'opacity');
        bindField('compChatBalloonRadius', 'balloonRadius', 'number', 'px');
      } else if (mode === 'character') {
        bindField('compCharName', 'characterName');
        bindField('compCharAlign', 'charAlign');
        bindField('compCharBubbleBg', 'charBubbleBg');
        bindField('compCharTextColor', 'charTextColor');
        bindField('compCharFontSize', 'charFontSize', 'number', 'px');
        bindField('compCharImgUrl', 'imageUrl');

        // Presets & File Upload
        const btnReplie = document.getElementById('btnCharPresetReplie');
        const btnCat = document.getElementById('btnCharPresetCat');
        const btnAnime = document.getElementById('btnCharPresetAnime');
        if (btnReplie) btnReplie.addEventListener('click', () => { w.imageUrl = './assets/dock_offline_character.png'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });
        if (btnCat) btnCat.addEventListener('click', () => { w.imageUrl = 'https://api.dicebear.com/7.x/bottts/svg?seed=CatStreamer'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });
        if (btnAnime) btnAnime.addEventListener('click', () => { w.imageUrl = 'https://api.dicebear.com/7.x/bottts/svg?seed=AnimeHero'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });

        const uploadBtn = document.getElementById('btnUploadCharImg');
        const fileInp = document.getElementById('compCharFileInput');
        if (uploadBtn && fileInp) {
          uploadBtn.addEventListener('click', () => fileInp.click());
          fileInp.addEventListener('change', () => {
            const file = fileInp.files[0];
            if (file) {
              const reader = new FileReader();
              reader.onload = (ev) => {
                w.imageUrl = ev.target.result;
                renderCanvasWidgets();
                renderWidgetCustomizerPanel(w.id);
                saveState();
              };
              reader.readAsDataURL(file);
            }
          });
        }
      } else {
        const tabStd = document.getElementById('tabSubStandard');
        const tabThm = document.getElementById('tabSubTheme');
        if (tabStd) tabStd.addEventListener('click', () => { state.chatSubTab = 'standard'; renderWidgetCustomizerPanel(w.id); });
        if (tabThm) tabThm.addEventListener('click', () => { state.chatSubTab = 'theme'; renderWidgetCustomizerPanel(w.id); });

        // Themes Click & Pagination
        document.querySelectorAll('#compChatThemesGrid .cwc-preset-card').forEach(card => {
          card.addEventListener('click', () => {
            w.chatTheme = card.dataset.chatTheme;
            renderCanvasWidgets();
            renderWidgetCustomizerPanel(w.id);
            saveState();
          });
        });

        const allThemes = window.CWC_ALL_THEMES || [];
        const totalPages = Math.ceil(allThemes.length / 8);
        const btnPrev = document.getElementById('btnCompThemePrev');
        const btnNext = document.getElementById('btnCompThemeNext');
        if (btnPrev) btnPrev.addEventListener('click', () => {
          state.chatThemePage = Math.max(1, (state.chatThemePage || 1) - 1);
          renderWidgetCustomizerPanel(w.id);
        });
        if (btnNext) btnNext.addEventListener('click', () => {
          state.chatThemePage = Math.min(totalPages, (state.chatThemePage || 1) + 1);
          renderWidgetCustomizerPanel(w.id);
        });

        bindField('compChatFontFamily', 'fontFamily');
        bindField('compChatFontSize', 'fontSize', 'number', 'px');
        bindField('compChatFontColor', 'fontColor');
        bindField('compChatBgColor', 'bgColor');
        bindField('compChatBgOpacity', 'bgOpacity', 'opacity');
        bindField('compChatBoxRadius', 'boxRadius', 'number', 'px');
      }
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
      bindField('compWebcamBorderWidth', 'borderWidth', 'number', 'px');
      bindField('compWebcamBorderColor', 'borderColor');
      bindField('compWebcamBorderRadius', 'borderRadius', 'number', 'px');
      bindField('compWebcamGlow', 'glow', 'checkbox');
      bindField('compWebcamShowName', 'showStreamerName', 'checkbox');
      bindField('compWebcamName', 'streamerName');
    } else if (w.type === 'goal') {
      bindField('compGoalTitle', 'goalTitle');
      bindField('compGoalCurrent', 'goalCurrent', 'number');
      bindField('compGoalTarget', 'goalTarget', 'number');
      bindField('compGoalUnit', 'goalUnit');
    } else if (w.type === 'viewer') {
      bindField('compViewerTheme', 'viewerTheme');
    } else if (w.type === 'character') {
      bindField('compCharWidgetName', 'characterName');
    }
  }

  // Setup Toolbar Events
  function setupToolbarEvents() {
    // Zoom buttons
    document.getElementById('btnCompZoomIn')?.addEventListener('click', () => setZoom(state.zoom + 0.1));
    document.getElementById('btnCompZoomOut')?.addEventListener('click', () => setZoom(state.zoom - 0.1));
    document.getElementById('btnCompZoomFit')?.addEventListener('click', autoFitCanvas);

    // Snap toggle
    const btnSnap = document.getElementById('btnCompSnap');
    if (btnSnap) {
      btnSnap.addEventListener('click', () => {
        state.snapGuides = !state.snapGuides;
        btnSnap.classList.toggle('active', state.snapGuides);
        if (window.showToast) {
          window.showToast(state.snapGuides ? 'เปิดระบบแม่เหล็กจัดแนวแล้ว' : 'ปิดระบบแม่เหล็กจัดแนวแล้ว');
        }
      });
    }

    // Background toggle
    document.querySelectorAll('.composer-bg-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.composer-bg-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.dataset.bg;
        const stage = document.getElementById('composerCanvasStage');
        if (stage) {
          stage.className = `composer-canvas-stage bg-${mode}`;
        }
      });
    });

    // Chat Context Dropdown Trigger
    const btnChatMenu = document.getElementById('btnCompAddChatMenu');
    const menuChat = document.getElementById('compChatDropdownMenu');
    if (btnChatMenu && menuChat) {
      btnChatMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = menuChat.style.display === 'block';
        menuChat.style.display = isOpen ? 'none' : 'block';
      });

      menuChat.querySelectorAll('.comp-chat-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
          e.stopPropagation();
          menuChat.style.display = 'none';
          const mode = item.dataset.chatMode || 'default';
          checkAndAddWidget('chat', mode);
        });
      });

      document.addEventListener('click', (e) => {
        if (!e.target.closest('#chatAddBtnWrapper')) {
          menuChat.style.display = 'none';
        }
      });
    }

    // Add Widget Buttons (Excluding the chat dropdown trigger)
    document.querySelectorAll('.btn-add-widget').forEach(btn => {
      if (btn.id === 'btnCompAddChatMenu') return;
      btn.addEventListener('click', () => {
        checkAndAddWidget(btn.dataset.widgetType);
      });
    });

    // Align Buttons
    document.querySelectorAll('.composer-btn-align').forEach(btn => {
      btn.addEventListener('click', () => {
        alignWidget(btn.dataset.align);
      });
    });

    // Transform Inspector inputs
    const bindProp = (id, key, minVal) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', () => {
        const widget = getSelectedWidget();
        if (!widget || widget.locked) return;
        const val = parseInt(el.value, 10);
        if (!isNaN(val)) {
          widget[key] = Math.max(minVal, val);
          renderCanvasWidgets();
          saveState();
        }
      });
    };

    bindProp('compPropX', 'x', -500);
    bindProp('compPropY', 'y', -500);
    bindProp('compPropW', 'width', 50);
    bindProp('compPropH', 'height', 30);

    // Save Button
    document.getElementById('btnCompSave')?.addEventListener('click', saveState);

    // Copy OBS URL Button
    document.getElementById('btnCompCopyObs')?.addEventListener('click', copyComposerObsUrl);
  }

  // Copy OBS URL
  function copyComposerObsUrl() {
    const host = window.location.origin || 'http://127.0.0.1:8080';
    const activePage = getActivePage();
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/overlay.html?p=${pageIndex}`;

    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        if (window.showToast) window.showToast(`คัดลอกลิงก์ OBS สำหรับหน้า ${pageIndex} สำเร็จ`);
      }).catch(() => {
        prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
      });
    } else {
      prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
    }
  }

  // Expose Global Helper
  window.initComposerStudio = initComposerStudio;
  window.autoFitCanvas = autoFitCanvas;
  window.ComposerStudio = {
    init: initComposerStudio,
    autoFitCanvas: autoFitCanvas,
    selectWidget: selectWidget,
    getState: () => state,
    addWidget: addWidget,
    checkAndAddWidget: checkAndAddWidget
  };

  // Auto-init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComposerStudio);
  } else {
    initComposerStudio();
  }

})();
'''

with open(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js', 'w', encoding='utf-8') as f:
    f.write(output_code)

print("Generated complete, clean composer_studio.js! Length:", len(output_code))
