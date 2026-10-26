import sys

sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

# ---------------------------------------------------------------------------
# 1. Update renderLayersList with Drag & Drop + Sleek SVG Icons
# ---------------------------------------------------------------------------
old_layers_start = text.find('function renderLayersList() {')
old_layers_end = text.find('// Align Widget', old_layers_start)

assert old_layers_start != -1 and old_layers_end != -1, "renderLayersList not found"

new_layers_fn = """function renderLayersList() {
    const list = document.getElementById('composerLayersList');
    if (!list) return;

    const page = getActivePage();
    if (!page) {
      list.innerHTML = '<div style="font-size:11.5px; color:var(--dc-text-muted); padding:10px;">ไม่มีวิดเจ็ต</div>';
      return;
    }

    list.innerHTML = '';
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));
    const countEl = document.getElementById('composerLayerCount');
    if (countEl) countEl.textContent = `${sorted.length} เลเยอร์`;

    // SVG Icons
    const svgSettings = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`;
    const svgEye = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
    const svgEyeOff = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
    const svgLock = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`;
    const svgUnlock = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>`;
    const svgTrash = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;

    sorted.forEach(w => {
      const item = document.createElement('div');
      item.className = `composer-layer-item ${w.id === state.selectedWidgetId ? 'active' : ''}`;
      item.dataset.id = w.id;
      item.draggable = true;

      item.innerHTML = `
        <div class="composer-layer-handle" title="คลิกค้างเพื่อลากสลับลำดับเลเยอร์">⠿</div>
        <span class="composer-layer-icon">${getWidgetIcon(w.type)}</span>
        <span class="composer-layer-name" title="${w.title}">${w.title}</span>
        <div class="composer-layer-actions">
          <button type="button" class="composer-btn-layer-action btn-layer-setting" data-action="setting" data-layer-id="${w.id}" title="ตั้งค่าวิดเจ็ต">
            ${svgSettings}
          </button>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-hide" title="${w.hidden ? 'แสดง' : 'ซ่อน'}">
            ${w.hidden ? svgEyeOff : svgEye}
          </button>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-lock" title="${w.locked ? 'ปลดล็อค' : 'ล็อค'}">
            ${w.locked ? svgLock : svgUnlock}
          </button>
          <button type="button" class="composer-btn-layer-action close-red" data-action="delete" title="ลบวิดเจ็ต">
            ${svgTrash}
          </button>
        </div>
      `;

      // Drag & Drop Reordering
      item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', w.id);
        item.classList.add('dragging');
      });

      item.addEventListener('dragover', (e) => {
        e.preventDefault();
        const rect = item.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        if (e.clientY < midY) {
          item.classList.add('drag-over-top');
          item.classList.remove('drag-over-bottom');
        } else {
          item.classList.add('drag-over-bottom');
          item.classList.remove('drag-over-top');
        }
      });

      item.addEventListener('dragleave', () => {
        item.classList.remove('drag-over-top', 'drag-over-bottom');
      });

      item.addEventListener('drop', (e) => {
        e.preventDefault();
        item.classList.remove('drag-over-top', 'drag-over-bottom');
        const srcId = e.dataTransfer.getData('text/plain');
        const targetId = w.id;
        if (!srcId || srcId === targetId) return;

        const srcIdx = page.widgets.findIndex(x => x.id === srcId);
        const targetIdx = page.widgets.findIndex(x => x.id === targetId);
        if (srcIdx === -1 || targetIdx === -1) return;

        const [moved] = page.widgets.splice(srcIdx, 1);
        const rect = item.getBoundingClientRect();
        const insertAfter = (e.clientY >= rect.top + rect.height / 2);
        const newTargetIdx = page.widgets.findIndex(x => x.id === targetId);
        page.widgets.splice(insertAfter ? newTargetIdx + 1 : newTargetIdx, 0, moved);

        // Reassign z indices from bottom to top
        page.widgets.forEach((itemW, idx) => {
          itemW.z = idx + 1;
        });

        renderCanvasWidgets();
        renderLayersList();
        saveState();
        if (window.showToast) window.showToast(`✨ สลับลำดับเลเยอร์ ${moved.title} เรียบร้อยแล้ว`);
      });

      item.addEventListener('dragend', () => {
        document.querySelectorAll('.composer-layer-item').forEach(el => {
          el.classList.remove('dragging', 'drag-over-top', 'drag-over-bottom');
        });
      });

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
          } else if (act === 'setting') {
            selectWidget(w.id);
            openWidgetSettings(w.id);
          } else if (act === 'delete') {
            deleteWidget(w.id);
          }
        } else {
          selectWidget(w.id);
        }
      });

      list.appendChild(item);
    });
  }

  """

text = text[:old_layers_start] + new_layers_fn + text[old_layers_end:]
print("Updated renderLayersList with Drag & Drop and sleek SVGs.")

# ---------------------------------------------------------------------------
# 2. Update setupCanvasEvents to add Spacebar Panning & Double-Spacebar Reset
# ---------------------------------------------------------------------------
old_setup_canvas = text.find('function setupCanvasEvents() {')
assert old_setup_canvas != -1, "setupCanvasEvents not found"
old_wheel_zoom = text.find('// Ctrl + Mouse Wheel Canvas Zoom', old_setup_canvas)

spacebar_panning_code = """// Spacebar Canvas Panning & Double-Spacebar Reset (Photoshop / Figma style)
    let isSpacebarDown = false;
    let isPanningCanvas = false;
    let panStartX = 0;
    let panStartY = 0;
    let panStartScrollLeft = 0;
    let panStartScrollTop = 0;
    let lastSpacebarPressTime = 0;

    window.addEventListener('keydown', (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select' || document.activeElement?.isContentEditable) return;

      if (e.code === 'Space' && !e.repeat) {
        const now = Date.now();
        if (now - lastSpacebarPressTime < 350) {
          e.preventDefault();
          autoFitCanvas();
          if (viewport) {
            viewport.scrollLeft = (viewport.scrollWidth - viewport.clientWidth) / 2;
            viewport.scrollTop = (viewport.scrollHeight - viewport.clientHeight) / 2;
          }
          if (window.showToast) window.showToast('🎯 พอดีจอ & จัดกึ่งกลางผ้าใบ (Double Spacebar)');
          lastSpacebarPressTime = 0;
          return;
        }
        lastSpacebarPressTime = now;
        isSpacebarDown = true;
        if (viewport) viewport.style.cursor = 'grab';
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.code === 'Space') {
        isSpacebarDown = false;
        isPanningCanvas = false;
        if (viewport) viewport.style.cursor = '';
      }
    });

    viewport.addEventListener('mousedown', (e) => {
      if (isSpacebarDown) {
        isPanningCanvas = true;
        panStartX = e.clientX;
        panStartY = e.clientY;
        panStartScrollLeft = viewport.scrollLeft;
        panStartScrollTop = viewport.scrollTop;
        viewport.style.cursor = 'grabbing';
        e.preventDefault();
        e.stopPropagation();
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (isPanningCanvas && isSpacebarDown && viewport) {
        const dx = e.clientX - panStartX;
        const dy = e.clientY - panStartY;
        viewport.scrollLeft = panStartScrollLeft - dx;
        viewport.scrollTop = panStartScrollTop - dy;
        e.preventDefault();
      }
    });

    window.addEventListener('mouseup', () => {
      if (isPanningCanvas) {
        isPanningCanvas = false;
        if (viewport) viewport.style.cursor = isSpacebarDown ? 'grab' : '';
      }
    });

    """

text = text[:old_wheel_zoom] + spacebar_panning_code + text[old_wheel_zoom:]
print("Added Spacebar Canvas Panning and Double-Spacebar Reset.")

# ---------------------------------------------------------------------------
# 3. Update renderWidgetInnerHtml for Text Widget (Vertical align & bg toggle)
# ---------------------------------------------------------------------------
text_inner_start = text.find("if (w.type === 'text') {", text.find('function renderWidgetInnerHtml('))
text_inner_end = text.find("if (w.type === 'character') {", text_inner_start)

assert text_inner_start != -1 and text_inner_end != -1, "Text widget innerHTML block not found"

new_text_inner = """if (w.type === 'text') {
      const isTicker = w.textMode === 'ticker';
      const fsz = w.fontSize || 18;
      const clr = w.fontColor || '#ffffff';
      const bgEnabled = w.bgEnabled !== false;
      const bg = bgEnabled ? (w.bgColor || '#141923') : 'transparent';
      const text = w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม ยินดีต้อนรับทุกคนครับ!';
      
      const strokeW = w.textStrokeWidth ?? (w.textStroke ? 2 : 0);
      const strokeCss = strokeW > 0 ? `-webkit-text-stroke:${strokeW}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      
      const shadowB = w.textShadowBlur ?? (w.textShadow ? 3 : 0);
      const shadowCss = shadowB > 0 ? `text-shadow:0 1px ${shadowB}px ${w.textShadowColor || '#000000'};` : '';
      
      const fFam = w.fontFamily || 'Kanit';
      const dur = w.marqueeSpeed || 15;
      const vAlign = w.vAlign || 'center';
      const justifyVal = vAlign === 'top' ? 'flex-start' : (vAlign === 'bottom' ? 'flex-end' : 'center');

      if (isTicker) {
        return `
          <div class="composer-widget-inner widget-type-text widget-text-ticker" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; --marquee-duration:${dur}s; display:flex; flex-direction:column; justify-content:${justifyVal};">
            <span>${text}</span>
          </div>
        `;
      }

      return `
        <div class="composer-widget-inner widget-type-text" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; display:flex; flex-direction:column; justify-content:${justifyVal}; text-align:center;">
          <span>${text}</span>
        </div>
      `;
    }

    """

text = text[:text_inner_start] + new_text_inner + text[text_inner_end:]
print("Updated text widget rendering with vertical alignment and background toggle.")

# ---------------------------------------------------------------------------
# 4. Update renderWidgetCustomizerPanel for Text Widget (Controls)
# ---------------------------------------------------------------------------
text_cust_start = text.find("id=\"compTextInput\"", text.find('function renderWidgetCustomizerPanel'))
# find enclosing section
text_cust_section_start = text.rfind('<div class="comp-card-section">', 0, text_cust_start)
text_cust_section_end = text.find('<!-- การ์ด 3:', text_cust_section_start)

assert text_cust_section_start != -1 and text_cust_section_end != -1, "Text customizer section not found"

new_text_cust_section = """<div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ข้อความและรูปแบบ</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ข้อความประกาศ</span>
              <textarea class="cwc-input" id="compTextInput" rows="2" style="width:100%; resize:vertical;">${w.text || ''}</textarea>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดแสดงผล</span>
              <select class="cwc-select" id="compTextMode">
                <option value="ticker" ${w.textMode === 'ticker' ? 'selected' : ''}>ตัววิ่ง Marquee สด</option>
                <option value="static" ${w.textMode !== 'ticker' ? 'selected' : ''}>ข้อความนิ่ง</option>
              </select>
            </div>
            <div class="comp-field-row" id="compTextSpeedRow" style="display:${w.textMode === 'ticker' ? 'flex' : 'none'};">
              <span class="cwc-label">ความเร็วตัววิ่ง (วินาทีต่อรอบ):</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextSpeed" min="5" max="60" value="${w.marqueeSpeed || 15}">
                <span class="cwc-slider-val" id="compTextSpeedVal">${w.marqueeSpeed || 15} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="64" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compTextFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ตำแหน่งแนวตั้ง</span>
              <div style="display:flex; gap:6px;">
                <button type="button" class="composer-btn-sub ${w.vAlign === 'top' ? 'active' : ''}" id="btnTextVAlignTop">⬆️ บน</button>
                <button type="button" class="composer-btn-sub ${(!w.vAlign || w.vAlign === 'center') ? 'active' : ''}" id="btnTextVAlignMid">↕️ กลาง</button>
                <button type="button" class="composer-btn-sub ${w.vAlign === 'bottom' ? 'active' : ''}" id="btnTextVAlignBot">⬇️ ล่าง</button>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compTextFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <input type="color" class="cwc-color-pick" id="compTextBgColor" value="${w.bgColor || '#141923'}" ${w.bgEnabled === false ? 'disabled style="opacity:0.4;"' : ''}>
                <button type="button" class="composer-btn-sub ${w.bgEnabled === false ? 'active' : ''}" id="btnTextToggleBg">
                  ${w.bgEnabled === false ? '🚫 ไม่ใช้พื้นหลัง (ใส)' : '🎨 เปิดใช้พื้นหลัง'}
                </button>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาเส้นขอบ (Stroke)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextStrokeWidth" min="0" max="10" value="${w.textStrokeWidth ?? 0}">
                <span class="cwc-slider-val" id="compTextStrokeWidthVal">${w.textStrokeWidth ?? 0}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compTextStrokeColor" value="${w.strokeColor || '#000000'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดเงา (Shadow Blur)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextShadowBlur" min="0" max="20" value="${w.textShadowBlur ?? 0}">
                <span class="cwc-slider-val" id="compTextShadowBlurVal">${w.textShadowBlur ?? 0}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเงา</span>
              <input type="color" class="cwc-color-pick" id="compTextShadowColor" value="${w.textShadowColor || '#000000'}">
            </div>
          </div>
        </div>
        """

text = text[:text_cust_section_start] + new_text_cust_section + text[text_cust_section_end:]
print("Updated text customizer form with vertical alignment, background toggle, stroke, and shadow controls.")

# ---------------------------------------------------------------------------
# 5. Update text field bindings in customizer binder
# ---------------------------------------------------------------------------
bind_text_start = text.find("bindField('compTextSpeed', 'marqueeSpeed'", text.find('function renderWidgetCustomizerPanel'))
bind_text_end = text.find("} else if (w.type === 'webcam') {", bind_text_start)

assert bind_text_start != -1 and bind_text_end != -1, "Text binder block not found"

new_text_bindings = """bindField('compTextSpeed', 'marqueeSpeed', 'number', ' วิ');
      bindField('compTextFontSize', 'fontSize', 'number', 'px');
      bindField('compTextFontColor', 'fontColor');
      bindField('compTextBgColor', 'bgColor');

      // Vertical alignment buttons
      const btnVTop = document.getElementById('btnTextVAlignTop');
      const btnVMid = document.getElementById('btnTextVAlignMid');
      const btnVBot = document.getElementById('btnTextVAlignBot');
      if (btnVTop && btnVMid && btnVBot) {
        const updateVAlign = (val) => {
          w.vAlign = val;
          btnVTop.classList.toggle('active', val === 'top');
          btnVMid.classList.toggle('active', val === 'center');
          btnVBot.classList.toggle('active', val === 'bottom');
          renderCanvasWidgets();
          saveState();
        };
        btnVTop.addEventListener('click', () => updateVAlign('top'));
        btnVMid.addEventListener('click', () => updateVAlign('center'));
        btnVBot.addEventListener('click', () => updateVAlign('bottom'));
      }

      // Background toggle
      const btnBgToggle = document.getElementById('btnTextToggleBg');
      const inpBgColor = document.getElementById('compTextBgColor');
      if (btnBgToggle) {
        btnBgToggle.addEventListener('click', () => {
          w.bgEnabled = (w.bgEnabled === false) ? true : false;
          btnBgToggle.textContent = w.bgEnabled ? '🎨 เปิดใช้พื้นหลัง' : '🚫 ไม่ใช้พื้นหลัง (ใส)';
          btnBgToggle.classList.toggle('active', !w.bgEnabled);
          if (inpBgColor) {
            inpBgColor.disabled = !w.bgEnabled;
            inpBgColor.style.opacity = w.bgEnabled ? '1' : '0.4';
          }
          renderCanvasWidgets();
          saveState();
        });
      }

      // Stroke controls (default 0)
      bindField('compTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
      bindField('compTextStrokeColor', 'strokeColor');

      // Shadow controls (default 0)
      bindField('compTextShadowBlur', 'textShadowBlur', 'number', 'px');
      bindField('compTextShadowColor', 'textShadowColor');
    """

text = text[:bind_text_start] + new_text_bindings + text[bind_text_end:]
print("Updated text customizer binder handlers.")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved composer_studio.js successfully.")
