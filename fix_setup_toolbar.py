# -*- coding: utf-8 -*-
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

target_old = """  // Bind Toolbar Buttons & Chat Dropdown Menu
  function initComposerToolbarEvents() {
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
  }

    initComposerToolbarEvents();"""

replacement = """  // Setup Toolbar Events
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
    });"""

if target_old in code:
    code = code.replace(target_old, replacement)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Fixed setupToolbarEvents successfully!")
else:
    print("Could not find target_old in code")
