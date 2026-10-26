# -*- coding: utf-8 -*-
import sys, io, re

file_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update selectWidget so it DOES NOT automatically toggle or open the drawer
old_select_widget = """  // Select Widget
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
  }"""

new_select_widget = """  // Select Widget (Does NOT open or close drawer automatically)
  function selectWidget(widgetId) {
    state.selectedWidgetId = widgetId;
    document.querySelectorAll('.composer-widget').forEach(el => {
      el.classList.toggle('selected', el.dataset.id === widgetId);
    });
    renderLayersList();
    updateTransformInspector();

    // If Left Drawer is ALREADY open, smoothly update customizer to the newly selected widget
    const leftPanel = document.getElementById('composerSidebarLeft');
    if (widgetId && leftPanel && !leftPanel.classList.contains('collapsed')) {
      renderWidgetCustomizerPanel(widgetId);
    }
  }"""

if old_select_widget in code:
    code = code.replace(old_select_widget, new_select_widget)
    print("Replaced selectWidget successfully.")
else:
    print("WARNING: old_select_widget pattern not exact match, using regex...")
    code = re.sub(
        r'// Select Widget\s+function selectWidget\(widgetId\)\s*\{[\s\S]*?renderLayersList\(\);[\s\S]*?updateTransformInspector\(\);[\s\S]*?if\s*\(widgetId\)[\s\S]*?\}\s*\}',
        new_select_widget.strip(),
        code,
        count=1
    )

# 2. Update renderCanvasWidgets to add theme/layout classes, badge gear button, draggable=false, and viewer ticker init
old_render_canvas_start = "page.widgets.forEach(w => {\n      if (w.hidden) return;\n\n      const isDanmaku = w.isDanmaku || w.chatMode === 'danmaku';\n      const el = document.createElement('div');\n      el.className = `composer-widget ${w.id === state.selectedWidgetId ? 'selected' : ''} ${w.locked ? 'locked' : ''} ${isDanmaku ? 'widget-danmaku-full' : ''}`;"

new_render_canvas_start = """page.widgets.forEach(w => {
      if (w.hidden) return;

      const isDanmaku = w.isDanmaku || w.chatMode === 'danmaku';
      const el = document.createElement('div');
      const classes = ['composer-widget', 'widget', `type-${w.type}`];
      if (w.id === state.selectedWidgetId) classes.push('selected');
      if (w.locked) classes.push('locked');
      if (isDanmaku) classes.push('widget-danmaku-full');

      if (w.type === 'clock') {
        classes.push('clock-theme-' + (w.clockTheme || 'default'));
        if (w.clockStyle && w.clockStyle !== 'none') {
          classes.push('clock-style-set', 'clock-style-' + w.clockStyle);
        }
      }
      if (w.type === 'viewer') {
        classes.push('viewer-theme-' + (w.viewerTheme || 'default'));
        classes.push('viewer-align-' + (w.viewerAlign || 'left'));
        classes.push('viewer-direction-' + (w.viewerDirection || 'horizontal'));
      }
      if (w.type === 'webcam') {
        classes.push('webcam-theme-' + (w.webcamTheme || 'simple-white'));
        classes.push('ratio-' + (w.ratio || '16:9').replace(':', '-'));
        el.style.setProperty('--wc-border-width', (w.borderWidth || 4) + 'px');
      }
      if (w.type === 'chat') {
        classes.push('theme-' + (w.chatTheme || 'default'));
      }
      if (w.type === 'text') {
        classes.push('text-' + (w.textMode || 'ticker'));
        el.style.setProperty('--marquee-duration', (w.marqueeSpeed || 15) + 's');
      }

      el.className = classes.join(' ');"""

if old_render_canvas_start in code:
    code = code.replace(old_render_canvas_start, new_render_canvas_start)
    print("Replaced renderCanvasWidgets start.")
else:
    print("renderCanvasWidgets start not matched exactly, checking...")

# Badge gear button replacement
old_badge = """badge.className = 'composer-widget-badge';
      badge.innerHTML = `<span>${getWidgetIcon(w.type)}</span> <span>${w.title}</span> <span style="opacity:0.75; font-size:10px;">${w.width}×${w.height}</span>`;
      el.appendChild(badge);"""

new_badge = """badge.className = 'composer-widget-badge';
      badge.innerHTML = `<span>${getWidgetIcon(w.type)}</span> <span>${w.title}</span> <span style="opacity:0.75; font-size:10px;">${w.width}×${w.height}</span> <button type="button" class="btn-widget-gear" title="ตั้งค่าวิดเจ็ต" style="background:transparent; border:none; cursor:pointer; font-size:12px; margin-left:6px; padding:0 2px; color:#ffffff;">⚙️</button>`;
      
      const btnGear = badge.querySelector('.btn-widget-gear');
      if (btnGear) {
        btnGear.addEventListener('mousedown', (e) => e.stopPropagation());
        btnGear.addEventListener('click', (e) => {
          e.stopPropagation();
          openWidgetSettings(w.id);
        });
      }
      el.appendChild(badge);"""

if old_badge in code:
    code = code.replace(old_badge, new_badge)
    print("Replaced badge with gear button.")

# Selection listeners in renderCanvasWidgets
old_sel_listener = """      // Selection & Drag listeners
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

      stage.appendChild(el);"""

new_sel_listener = """      // Selection & Drag listeners
      el.addEventListener('mousedown', (e) => {
        if (e.target.closest('.btn-widget-gear')) return;
        if (e.target.classList.contains('composer-resize-handle')) {
          startResize(e, w, e.target.dataset.handle);
        } else {
          startDrag(e, w);
        }
      });
      el.addEventListener('click', (e) => {
        if (e.target.closest('.btn-widget-gear')) return;
        selectWidget(w.id);
      });

      stage.appendChild(el);

      // Initialize Number Ticker for viewer widget
      if (w.type === 'viewer') {
        const ticker = el.querySelector('.viewer-ticker');
        if (ticker) {
          updateNumberTicker(ticker, w.mockViewerCount || 1250);
        }
      }"""

if old_sel_listener in code:
    code = code.replace(old_sel_listener, new_sel_listener)
    print("Replaced selection listeners and added viewer ticker init.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Part 1 finished.")
