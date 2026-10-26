import os

composer_html = """<!DOCTYPE html>
<html lang="th" class="notranslate" translate="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920, height=1080, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  <title>Broadcast Playroom 3 — OBS Live Overlay</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700;800&family=Noto+Sans+Thai+Looped:wght@400;500;600;700&family=Press+Start+2P&family=Chakra+Petch:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./styles.css">
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
      user-select: none;
      -webkit-user-select: none;
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
    .composer-widget {
      position: absolute !important;
      pointer-events: none !important;
      user-select: none !important;
    }
    /* Hide editor UI markers on OBS */
    .composer-widget::before,
    .composer-widget::after,
    .composer-resize-handle,
    .composer-widget-badge,
    .composer-widget-tools,
    .smart-guide-line {
      display: none !important;
    }
    .composer-widget.selected {
      outline: none !important;
      box-shadow: none !important;
    }
    /* Status banner for browser test mode */
    #obsStatusNotice {
      position: absolute;
      bottom: 20px;
      right: 20px;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #f8fafc;
      padding: 10px 18px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 500;
      display: none;
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
      z-index: 999999;
      pointer-events: auto;
      max-width: 450px;
      backdrop-filter: none;
    }
    #obsStatusNotice b { color: #38bdf8; }
  </style>
</head>
<body class="overlay-mode preview-clean-mode" translate="no" class="notranslate">
  <div id="obsCanvasStage"></div>
  <div id="obsStatusNotice">
    <div>📡 <b>Broadcast Playroom 3 — OBS Live Overlay</b></div>
    <div style="font-size:12px; color:#94a3b8; margin-top:3px;">เชื่อมต่อเรียบร้อยแล้ว กำลังรอรับข้อมูลวิดเจ็ตจาก Composer Studio...</div>
  </div>

  <script src="./cwc_themes_data.js"></script>
  <script src="./composer_studio.js"></script>
  <script>
  (function() {
    const stage = document.getElementById('obsCanvasStage');
    const notice = document.getElementById('obsStatusNotice');
    const params = new URLSearchParams(window.location.search);
    const targetPageParam = params.get('p') || params.get('page') || '1';
    const isBrowserTest = params.has('test') || window.location.protocol === 'http:';

    let lastConfigHash = '';
    let clockTimer = null;

    // Show temporary notice in browser test
    if (params.has('test')) {
      if (notice) {
        notice.style.display = 'block';
        setTimeout(() => { notice.style.display = 'none'; }, 4000);
      }
    }

    // Helper to get active page data
    function resolvePage(data) {
      if (!data) return null;
      let pages = Array.isArray(data) ? data : (data.pages || []);
      if (!pages.length) return null;

      const num = parseInt(targetPageParam, 10);
      if (!isNaN(num) && num >= 1 && num <= pages.length) {
        return pages[num - 1];
      }
      const byId = pages.find(p => p.id === targetPageParam || p.name === targetPageParam);
      if (byId) return byId;

      return pages[0];
    }

    // Render widgets onto OBS stage
    function renderWidgets(page) {
      if (!stage || !page || !Array.isArray(page.widgets)) return;

      const renderer = window.renderWidgetInnerHtml || (window.ComposerStudio && window.ComposerStudio.renderWidgetInnerHtml);
      const isFullFn = window.isFullscreenWidget || (window.ComposerStudio && window.ComposerStudio.isFullscreenWidget);

      stage.innerHTML = '';

      page.widgets.forEach(w => {
        if (w.hidden) return;

        const el = document.createElement('div');
        const isFull = isFullFn ? isFullFn(w) : (
          (w.type === 'chat' && w.chatMode === 'danmaku') ||
          w.type === 'ask' ||
          w.type === 'giveaway' ||
          w.type === 'emote_party' ||
          w.type === 'randomizer' ||
          w.type === 'replie' ||
          w.isFullScreen === true
        );
        
        let classes = ['composer-widget', 'widget', 'type-' + w.type];
        if (isFull) classes.push('widget-fullscreen-fixed', 'widget-danmaku-full');
        if (w.clockTheme) classes.push('clock-theme-' + w.clockTheme);
        if (w.clockStyle && w.clockStyle !== 'none') classes.push('clock-style-set', 'clock-style-' + w.clockStyle);
        if (w.viewerTheme) classes.push('viewer-theme-' + w.viewerTheme);
        if (w.webcamTheme) classes.push('webcam-theme-' + w.webcamTheme);
        if (w.chatTheme) classes.push('chat-theme-' + w.chatTheme);
        if (w.chatMode) classes.push('chat-mode-' + w.chatMode);

        el.className = classes.join(' ');
        el.dataset.id = w.id;
        el.dataset.type = w.type;

        el.style.left = (isFull ? 0 : (w.x || 0)) + 'px';
        el.style.top = (isFull ? 0 : (w.y || 0)) + 'px';
        el.style.width = (isFull ? 1920 : (w.width || 300)) + 'px';
        el.style.height = (isFull ? 1080 : (w.height || 200)) + 'px';
        el.style.zIndex = w.z || 1;
        el.style.opacity = w.opacity ?? 1;

        if (typeof renderer === 'function') {
          el.innerHTML = renderer(w);
        } else {
          el.innerHTML = `<div class="composer-widget-inner">${w.title || w.type}</div>`;
        }

        stage.appendChild(el);
      });

      startClockTicker();
    }

    // Live Clock Ticker
    function startClockTicker() {
      if (clockTimer) clearInterval(clockTimer);
      clockTimer = setInterval(() => {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        const yr = now.getFullYear();
        const mo = String(now.getMonth() + 1).padStart(2, '0');
        const dy = String(now.getDate()).padStart(2, '0');

        document.querySelectorAll('.composer-widget.type-clock').forEach(el => {
          const dotTime = el.querySelector('.dot-time');
          if (dotTime) dotTime.textContent = `${h}:${m}`;
          const ltTime = el.querySelector('.lt-time');
          if (ltTime) ltTime.innerHTML = `${h}<span class="lt-colon">:</span>${m}`;
          const ltSec = el.querySelector('.lt-sec');
          if (ltSec) ltSec.textContent = s;
          const clockTime = el.querySelector('.clock-time');
          if (clockTime) {
            clockTime.textContent = clockTime.textContent.includes(':') ? (clockTime.textContent.split(':').length === 3 ? `${h}:${m}:${s}` : `${h}:${m}`) : `${h}:${m}`;
          }
        });
      }, 1000);
    }

    // Fetch layout from Server or fallback to localStorage
    async function updateLayout() {
      let data = null;

      // 1. Try server API /api/composer/layout
      try {
        const res = await fetch('/api/composer/layout?t=' + Date.now(), { cache: 'no-store' });
        if (res.ok) {
          data = await res.json();
        }
      } catch (e) {
        // Server offline
      }

      // 2. Fallback to localStorage
      if (!data) {
        try {
          const local = localStorage.getItem('bp_composer_studio_v3_full') || localStorage.getItem('bp_composer_studio_v3');
          if (local) data = JSON.parse(local);
        } catch (e) {}
      }

      if (data) {
        const page = resolvePage(data);
        const hash = JSON.stringify(page);
        if (hash !== lastConfigHash) {
          lastConfigHash = hash;
          renderWidgets(page);
        }
      }
    }

    // Initial load
    updateLayout();

    // Fast Polling (700ms hash diff)
    setInterval(updateLayout, 700);

    // BroadcastChannel real-time sync
    if ('BroadcastChannel' in window) {
      try {
        const bus = new BroadcastChannel('bp3_system_channel');
        bus.onmessage = (e) => {
          const { event, payload } = e.data || {};
          if (event === 'CANVAS_LAYOUT_SAVED') {
            updateLayout();
          }
        };
      } catch (e) {}
    }
  })();
  </script>
</body>
</html>
"""

src_composer = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer.html'
src_overlay = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/overlay.html'
dist_composer = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer.html'
dist_overlay = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/overlay.html'

for p in [src_composer, src_overlay, dist_composer, dist_overlay]:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(composer_html)
    print(f'Wrote {p}')
