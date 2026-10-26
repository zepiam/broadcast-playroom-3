/* ========================================================
   BROADCAST PLAYROOM 3 - IN-APP COMPOSER STUDIO LOGIC
   Native Canvas Layout Engine for Live Stream Overlays
   Zero External Browser Needed - 100% In-App
   ======================================================== */

(function () {
  'use strict';

  const STORAGE_KEY = 'bp3_composer_pages';

  // Default Canvas Dimensions
  const CANVAS_WIDTH = 1920;
  const CANVAS_HEIGHT = 1080;

  // Default Pages & Sample Widgets
  const DEFAULT_PAGES = [
    {
      id: 'page-1',
      name: 'หน้า 1',
      widgets: [
        {
          id: 'w-chat-1',
          type: 'chat',
          title: 'กล่องแชทสด',
          x: 40,
          y: 420,
          width: 440,
          height: 620,
          z: 10,
          opacity: 1,
          locked: false,
          hidden: false
        },
        {
          id: 'w-clock-1',
          type: 'clock',
          title: 'นาฬิกาสตรีม',
          x: 1620,
          y: 40,
          width: 260,
          height: 70,
          z: 20,
          opacity: 1,
          locked: false,
          hidden: false
        },
        {
          id: 'w-text-1',
          type: 'text',
          title: 'แถบประกาศเลื่อน',
          x: 0,
          y: 1030,
          width: 1920,
          height: 50,
          z: 30,
          opacity: 0.95,
          locked: false,
          hidden: false,
          text: '⭐ ยินดีต้อนรับสู่สตรีม! อย่าลืมกดติดตามและกดกระดิ่งแจ้งเตือนด้วยนะครับ ⭐'
        }
      ]
    }
  ];

  let state = {
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
  };

  // Clock ticker timer
  let clockInterval = null;

  // Load saved layout from localStorage
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

    state.pages.forEach((p, idx) => {
      const btn = document.createElement('button');
      btn.className = `composer-page-btn ${p.id === state.activePageId ? 'active' : ''}`;
      btn.innerHTML = `<span>📄</span> ${p.name}`;
      btn.addEventListener('click', () => {
        state.activePageId = p.id;
        state.selectedWidgetId = null;
        renderPageTabs();
        renderCanvasWidgets();
        renderLayersList();
        updateTransformInspector();
      });
      container.appendChild(btn);
    });

    // Add page button
    const btnAdd = document.createElement('button');
    btnAdd.className = 'composer-page-btn';
    btnAdd.innerHTML = '+ เพิ่มหน้า';
    btnAdd.title = 'เพิ่มหน้าจอใหม่';
    btnAdd.addEventListener('click', addNewPage);
    container.appendChild(btnAdd);
  }

  // Add new page
  function addNewPage() {
    const newIdx = state.pages.length + 1;
    const newPage = {
      id: `page-${Date.now()}`,
      name: `หน้า ${newIdx}`,
      widgets: []
    };
    state.pages.push(newPage);
    state.activePageId = newPage.id;
    state.selectedWidgetId = null;
    renderPageTabs();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    if (window.showToast) {
      window.showToast(`สร้าง${newPage.name}เรียบร้อยแล้ว`);
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

      const el = document.createElement('div');
      el.className = `composer-widget ${w.id === state.selectedWidgetId ? 'selected' : ''} ${w.locked ? 'locked' : ''}`;
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

      // 8 Resize Handles
      const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
      handles.forEach(h => {
        const handle = document.createElement('div');
        handle.className = `composer-resize-handle handle-${h}`;
        handle.dataset.handle = h;
        el.appendChild(handle);
      });

      // Selection & Drag listeners
      el.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('composer-resize-handle')) {
          startResize(e, w, e.target.dataset.handle);
        } else {
          startDrag(e, w);
        }
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
      image: '🖼️',
      character: '🎭',
      webcam: '📹',
      goal: '🎯',
      browser: '🌐'
    };
    return icons[type] || '📦';
  }

  // Render Inner HTML according to Widget Type
  function renderWidgetInnerHtml(w) {
    if (w.type === 'chat') {
      return `
        <div class="composer-widget-inner widget-type-chat">
          <div class="widget-chat-item">
            <span style="color:#ef4444; font-weight:700;">Gamer_Pro:</span>
            <span>สวัสดีทุกคนในไลฟ์สตรีมครับ! 🎮</span>
          </div>
          <div class="widget-chat-item">
            <span style="color:#a855f7; font-weight:700;">Zack_Live:</span>
            <span>สตรีมภาพสวยคมชัด 60fps มากครับ 🔥</span>
          </div>
          <div class="widget-chat-item">
            <span style="color:#22c55e; font-weight:700;">Mali_TH:</span>
            <span>ยินดีต้อนรับเพื่อนๆ ทุกคนนะครับ 💖</span>
          </div>
        </div>
      `;
    }

    if (w.type === 'clock') {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      return `
        <div class="composer-widget-inner widget-type-clock">
          <div class="widget-clock-time">${timeStr}</div>
        </div>
      `;
    }

    if (w.type === 'text') {
      return `
        <div class="composer-widget-inner widget-type-text">
          <span>${w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม'}</span>
        </div>
      `;
    }

    if (w.type === 'character') {
      return `
        <div class="composer-widget-inner widget-type-character">
          <img class="widget-character-img" src="./assets/dock_offline_character.png" alt="Character" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
          <div class="widget-character-name">ตัวละครพูด Replie</div>
        </div>
      `;
    }

    if (w.type === 'webcam') {
      return `
        <div class="composer-widget-inner widget-type-webcam">
          <div class="widget-webcam-label">📹 กรอบกล้องเว็บแคม (16:9)</div>
        </div>
      `;
    }

    if (w.type === 'goal') {
      return `
        <div class="composer-widget-inner widget-type-goal">
          <div class="widget-goal-header">
            <span>เป้าหมายยอดผู้ติดตาม (Followers)</span>
            <span style="color:#ec4899;">65 / 100</span>
          </div>
          <div class="widget-goal-bar-track">
            <div class="widget-goal-bar-fill"></div>
          </div>
        </div>
      `;
    }

    if (w.type === 'image') {
      return `
        <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#1e1f22; border:1px dashed rgba(255,255,255,0.2);">
          <span style="font-size:32px;">🖼️</span>
          <span style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">กรอบรูปภาพ / โลโก้</span>
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
    document.querySelectorAll('.composer-widget').forEach(el => {
      el.classList.toggle('selected', el.dataset.id === widgetId);
    });
    renderLayersList();
    updateTransformInspector();
  }

  // Start Dragging Widget
  function startDrag(e, widget) {
    if (widget.locked) {
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
    if (widget.locked) return;
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

    const deltaX = (e.clientX - state.dragStartMouseX) / state.zoom;
    const deltaY = (e.clientY - state.dragStartMouseY) / state.zoom;

    if (state.isDragging) {
      let newX = Math.round(state.dragStartWidgetX + deltaX);
      let newY = Math.round(state.dragStartWidgetY + deltaY);

      // Snapping to Canvas Edges and Center
      if (state.snapGuides) {
        const SNAP = 12;
        // Snap X
        if (Math.abs(newX) < SNAP) newX = 0;
        if (Math.abs(newX + widget.width - CANVAS_WIDTH) < SNAP) newX = CANVAS_WIDTH - widget.width;
        if (Math.abs(newX + widget.width / 2 - CANVAS_WIDTH / 2) < SNAP) newX = Math.round(CANVAS_WIDTH / 2 - widget.width / 2);

        // Snap Y
        if (Math.abs(newY) < SNAP) newY = 0;
        if (Math.abs(newY + widget.height - CANVAS_HEIGHT) < SNAP) newY = CANVAS_HEIGHT - widget.height;
        if (Math.abs(newY + widget.height / 2 - CANVAS_HEIGHT / 2) < SNAP) newY = Math.round(CANVAS_HEIGHT / 2 - widget.height / 2);
      }

      widget.x = newX;
      widget.y = newY;

      const el = document.getElementById(`widget-${widget.id}`);
      if (el) {
        el.style.left = `${newX}px`;
        el.style.top = `${newY}px`;
      }
      updateTransformInspector();
    } else if (state.isResizing) {
      const h = state.activeResizeHandle;
      let newW = state.dragStartWidgetW;
      let newH = state.dragStartWidgetH;
      let newX = state.dragStartWidgetX;
      let newY = state.dragStartWidgetY;

      if (h.includes('e')) newW = Math.max(80, Math.round(state.dragStartWidgetW + deltaX));
      if (h.includes('s')) newH = Math.max(40, Math.round(state.dragStartWidgetH + deltaY));
      if (h.includes('w')) {
        const calculatedW = Math.max(80, Math.round(state.dragStartWidgetW - deltaX));
        newX = state.dragStartWidgetX + (state.dragStartWidgetW - calculatedW);
        newW = calculatedW;
      }
      if (h.includes('n')) {
        const calculatedH = Math.max(40, Math.round(state.dragStartWidgetH - deltaY));
        newY = state.dragStartWidgetY + (state.dragStartWidgetH - calculatedH);
        newH = calculatedH;
      }

      widget.x = newX;
      widget.y = newY;
      widget.width = newW;
      widget.height = newH;

      const el = document.getElementById(`widget-${widget.id}`);
      if (el) {
        el.style.left = `${newX}px`;
        el.style.top = `${newY}px`;
        el.style.width = `${newW}px`;
        el.style.height = `${newH}px`;
        const badge = el.querySelector('.composer-widget-badge');
        if (badge) {
          badge.innerHTML = `<span>${getWidgetIcon(widget.type)}</span> <span>${widget.title}</span> <span style="opacity:0.75; font-size:10px;">${newW}×${newH}</span>`;
        }
      }
      updateTransformInspector();
    }
  }

  // Mouse Up
  function onMouseUp() {
    state.isDragging = false;
    state.isResizing = false;
    state.activeResizeHandle = null;

    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);

    // Save state automatically
    saveState();
  }

  // Keyboard navigation & deletion
  function handleKeyDown(e) {
    const win = document.getElementById('win-composer');
    if (!win || !win.classList.contains('active')) return;

    const widget = getSelectedWidget();
    if (!widget) return;

    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    // Delete or Backspace
    if (e.key === 'Delete' || e.key === 'Backspace') {
      deleteSelectedWidget();
      e.preventDefault();
    }

    // Arrow keys nudge
    const step = e.shiftKey ? 10 : 1;
    if (e.key === 'ArrowLeft') { widget.x -= step; e.preventDefault(); }
    if (e.key === 'ArrowRight') { widget.x += step; e.preventDefault(); }
    if (e.key === 'ArrowUp') { widget.y -= step; e.preventDefault(); }
    if (e.key === 'ArrowDown') { widget.y += step; e.preventDefault(); }

    const el = document.getElementById(`widget-${widget.id}`);
    if (el) {
      el.style.left = `${widget.x}px`;
      el.style.top = `${widget.y}px`;
    }
    updateTransformInspector();
  }

  // Add a new Widget to canvas
  function addWidget(type) {
    const page = getActivePage();
    if (!page) return;

    const presets = {
      chat: { title: 'กล่องแชทสด', width: 440, height: 600 },
      clock: { title: 'นาฬิกาสตรีม', width: 260, height: 70 },
      text: { title: 'แถบข้อความประกาศ', width: 800, height: 50, text: 'ข้อความสตรีมสดใหม่' },
      character: { title: 'ตัวละครพูด Replie', width: 340, height: 420 },
      webcam: { title: 'กรอบกล้องเว็บแคม', width: 480, height: 270 },
      goal: { title: 'เป้าหมายผู้ติดตาม', width: 400, height: 75 },
      image: { title: 'กรอบรูปภาพแบนเนอร์', width: 320, height: 180 }
    };

    const preset = presets[type] || { title: 'วิดเจ็ตใหม่', width: 300, height: 200 };
    const newWidget = {
      id: `w-${type}-${Date.now()}`,
      type: type,
      title: preset.title,
      x: Math.round(CANVAS_WIDTH / 2 - preset.width / 2),
      y: Math.round(CANVAS_HEIGHT / 2 - preset.height / 2),
      width: preset.width,
      height: preset.height,
      z: page.widgets.length + 1,
      opacity: 1,
      locked: false,
      hidden: false,
      text: preset.text || ''
    };

    page.widgets.push(newWidget);
    state.selectedWidgetId = newWidget.id;

    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    saveState();

    if (window.showToast) {
      window.showToast(`เพิ่ม${preset.title}บนหน้าจอแล้ว`);
    }
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
    // Reverse order for layers (top z-index on top of list)
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));

    sorted.forEach(w => {
      const item = document.createElement('div');
      item.className = `composer-layer-item ${w.id === state.selectedWidgetId ? 'active' : ''}`;
      item.dataset.id = w.id;

      item.innerHTML = `
        <span style="font-size:14px;">${getWidgetIcon(w.type)}</span>
        <span class="composer-layer-name">${w.title}</span>
        <div class="composer-layer-actions">
          <button class="composer-layer-icon-btn ${w.hidden ? 'active' : ''}" data-act="hide" title="${w.hidden ? 'แสดง' : 'ซ่อน'}">
            ${w.hidden ? '👁️‍🗨️' : '👁️'}
          </button>
          <button class="composer-layer-icon-btn ${w.locked ? 'active' : ''}" data-act="lock" title="${w.locked ? 'ปลดล็อก' : 'ล็อก'}">
            ${w.locked ? '🔒' : '🔓'}
          </button>
          <button class="composer-layer-icon-btn" data-act="delete" title="ลบวิดเจ็ต">
            🗑️
          </button>
        </div>
      `;

      item.addEventListener('click', (e) => {
        const act = e.target.closest('button')?.dataset.act;
        if (act === 'hide') {
          w.hidden = !w.hidden;
          renderCanvasWidgets();
          renderLayersList();
          saveState();
        } else if (act === 'lock') {
          w.locked = !w.locked;
          renderCanvasWidgets();
          renderLayersList();
          saveState();
        } else if (act === 'delete') {
          state.selectedWidgetId = w.id;
          deleteSelectedWidget();
        } else {
          selectWidget(w.id);
        }
      });

      list.appendChild(item);
    });
  }

  // Quick Align Tools
  function alignWidget(direction) {
    const widget = getSelectedWidget();
    if (!widget || widget.locked) return;

    if (direction === 'left') widget.x = 0;
    if (direction === 'center') widget.x = Math.round(CANVAS_WIDTH / 2 - widget.width / 2);
    if (direction === 'right') widget.x = CANVAS_WIDTH - widget.width;
    if (direction === 'top') widget.y = 0;
    if (direction === 'middle') widget.y = Math.round(CANVAS_HEIGHT / 2 - widget.height / 2);
    if (direction === 'bottom') widget.y = CANVAS_HEIGHT - widget.height;

    const el = document.getElementById(`widget-${widget.id}`);
    if (el) {
      el.style.left = `${widget.x}px`;
      el.style.top = `${widget.y}px`;
    }
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
      if (inpX) inpX.value = '-';
      if (inpY) inpY.value = '-';
      if (inpW) inpW.value = '-';
      if (inpH) inpH.value = '-';
      if (inpOp) inpOp.value = '100%';
      return;
    }

    if (inpX) inpX.value = widget.x;
    if (inpY) inpY.value = widget.y;
    if (inpW) inpW.value = widget.width;
    if (inpH) inpH.value = widget.height;
    if (inpOp) inpOp.value = `${Math.round((widget.opacity ?? 1) * 100)}%`;
  }

  // Setup Canvas Viewport Click
  function setupCanvasEvents() {
    const viewport = document.getElementById('composerViewport');
    if (!viewport) return;

    viewport.addEventListener('click', (e) => {
      if (e.target.id === 'composerViewport' || e.target.id === 'composerCanvasStage' || e.target.id === 'composerCanvasOuter') {
        selectWidget(null);
      }
    });
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

    // Add Widget Buttons
    document.querySelectorAll('.btn-add-widget').forEach(btn => {
      btn.addEventListener('click', () => {
        addWidget(btn.dataset.widgetType);
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

  // Auto-init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComposerStudio);
  } else {
    initComposerStudio();
  }

})();
