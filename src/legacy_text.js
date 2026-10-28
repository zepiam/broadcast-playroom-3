// Legacy text renderer: static, scroll and scheduled lines.
(()=>{
const config={font_family:'Kanit'};
const mounted=new Set();
function computeSlideIntervalMs(interval,unit){const n=Math.max(1,Number(interval)||10);return n*(unit==='minutes'?60000:unit==='hours'?3600000:1000);}
function setupTextWidget(inner, w) {
  const signature=JSON.stringify(Object.fromEntries(Object.entries(w).filter(([key])=>!['x','y','width','height','w','h','z','opacity'].includes(key))));if(inner._bpRuntimeConfig===signature)return;inner._bpRuntimeConfig=signature;
  const mode = w.text_mode || 'static';
  const content = w.text_content || '';
  const ff = (config.font_family || 'Kanit');
  const fs = (w.font_size || 24);
  const fc = (w.font_color || '#ffffff');
  const fw = (w.font_weight || '600');
  const align = (w.text_align || 'center');
  // stroke
  const ts = w.text_stroke !== false;
  const tsw = w.text_stroke_width || 2;
  const tsc = w.text_stroke_color || '#000000';
  const strokeType = w.text_stroke_type || 'inner';
  // shadow
  const tsh = w.text_shadow !== false;
  const tshb = w.text_shadow_blur || 3;
  const tshc = w.text_shadow_color || '#000000';

  // ★ Stroke: Inner = -webkit-text-stroke | Outer = text-shadow 8 ทิศทาง
  let webkitStroke = '0 transparent';
  let outerStrokeShadows = '';
  if (ts) {
    if (strokeType === 'inner') {
      webkitStroke = `${tsw}px ${tsc}`;
    } else {
      // ★ Outer stroke — สร้างเงา 8 ทิศทางล้อมรอบตัวอักษร
      const dirs = [
        `${tsw}px 0`, `-${tsw}px 0`, `0 ${tsw}px`, `0 -${tsw}px`,
        `${tsw}px ${tsw}px`, `-${tsw}px -${tsw}px`, `${tsw}px -${tsw}px`, `-${tsw}px ${tsw}px`
      ];
      outerStrokeShadows = dirs.map(d => `${d} 0 ${tsc}`).join(', ');
    }
  }

  // ★ รวม shadow: outer stroke + regular shadow
  const allShadows = [
    outerStrokeShadows,
    tsh ? `0 1px ${tshb}px ${tshc}` : ''
  ].filter(s => s).join(', ') || 'none';

  // ★ inline style (apply ทั้งหมด — กัน theme CSS ทับ)
  const textStyle = `
    font-family: "${ff}", "Leelawadee UI", "Segoe UI", sans-serif;
    font-size: ${fs}px;
    color: ${fc};
    font-weight: ${fw};
    -webkit-text-stroke: ${webkitStroke};
    text-shadow: ${allShadows};
    --text-align: ${align};
  `;
  inner.style.setProperty('--text-align', align);
  // ★ map align → justify-content (flex-start/center/flex-end)
  const justify = align === 'left' ? 'flex-start' : align === 'right' ? 'flex-end' : 'center';
  inner.style.setProperty('--text-justify', justify);

  // ★ Text widget background (ถ้าเปิดใช้) — apply ที่ widget element (parent) เพื่อให้แน่ใจว่าแสดง
  const widgetEl = inner.closest('.widget');
  if (w.text_bg_enabled) {
    const bgColor = w.text_bg_color || '#1a1a2e';
    const bgOpacity = w.text_bg_opacity !== undefined ? w.text_bg_opacity : 1.0;
    const bgRadius = w.text_bg_radius !== undefined ? w.text_bg_radius : 8;
    // ★ แปลง hex + opacity → rgba (alpha=1 → solid hex เพื่อกันปัญหา compositing ใน OBS)
    let bgCss;
    if (bgOpacity >= 0.999) {
      bgCss = bgColor;  // ★ solid hex — ทึบ 100%
    } else {
      const r = parseInt(bgColor.slice(1,3), 16) || 0;
      const g = parseInt(bgColor.slice(3,5), 16) || 0;
      const b = parseInt(bgColor.slice(5,7), 16) || 0;
      bgCss = `rgba(${r},${g},${b},${bgOpacity})`;
    }
    // ★ apply ที่ทั้ง widget + inner (กัน CSS rule background:transparent ทับ)
    if (widgetEl) widgetEl.style.background = bgCss;
    inner.style.background = bgCss;
    inner.style.borderRadius = bgRadius + 'px';
    inner.style.padding = '8px 16px';
  } else {
    if (widgetEl) widgetEl.style.background = '';
    inner.style.background = '';
    inner.style.borderRadius = '';
    inner.style.padding = '';
  }

  const structure=JSON.stringify([mode,content]);
  const retained=inner.querySelectorAll('.text-content');
  if(inner._bpTextStructure===structure && retained.length){
    const authored=document.createElement('span');authored.style.cssText=textStyle;
    for(const el of retained)for(const prop of authored.style)el.style.setProperty(prop,authored.style.getPropertyValue(prop));
    return;
  }
  inner._bpTextStructure=structure;
  // clear timer + content
  // ★ clear timer (รองรับทั้ง setInterval สำหรับ schedule + requestAnimationFrame/timeout สำหรับ scroll)
  if (inner._textCleanup) { inner._textCleanup(); inner._textCleanup = null; }
  if (inner._textTimer) {
    clearInterval(inner._textTimer);
    cancelAnimationFrame(inner._textTimer);
    clearTimeout(inner._textTimer);
    inner._textTimer = null;
  }
  while (inner.firstChild) inner.removeChild(inner.firstChild);

  if (mode === 'scroll') {
    // ★ scroll loop — JS animation (วิ่งซ้ายจนหมดจอ → delay 2s → เริ่มใหม่)
    const el = document.createElement('div');
    el.className = 'text-content';
    el.style.cssText = textStyle;
    el.textContent = content;
    inner.appendChild(el);
    // ★ speed: 1-20 → pixels per second (ระบบพิกัด canvas)
    //   ใช้ px/วิ + timestamp → ไม่ขึ้นกับ frame rate และไม่ขึ้นกับ zoom
    //   → ความเร็วเท่ากันทุก mode (Editor / Overlay / OBS)
    //   ก่อนหน้านี้คำนวณเป็น px/frame และหารด้วย zoomLevel → ใน Editor เร็วกว่า OBS 3-5 เท่า
    //   ค่าคงที่: speed 1 = 30 px/วิ (อ่านสบาย), speed 10 = 300 px/วิ, speed 20 = 600 px/วิ
    const speed = w.text_scroll_speed || 10;
    const pxPerSec = Math.max(30, speed * 30);   // px/วิ (ขั้นต่ำ 30 px/วิ)
    // ★ Timing ในการเริ่ม Loop ข้อความ (หน่วยวินาที — default 2 วิ)
    const delayMs = Math.max(0.5, Number(w.text_scroll_delay) || 2) * 1000;
    // ★ animation loop — วัดความกว้างจริงหลัง render (double rAF)
    let scrollPos = 0;
    let isPaused = false;
    let animId = null;
    let lastTs = 0;
    function startScrollLoop() {
      const containerW = inner.offsetWidth || 400;
      // ★ วัด textW จริง — ใช้ scrollWidth เพราะ absolute + nowrap อาจให้ offsetWidth ผิด
      const textW = el.scrollWidth || el.offsetWidth || 200;
      scrollPos = containerW;   // เริ่มที่ขอบขวา (มองไม่เห็น)
      el.style.left = scrollPos + 'px';
      lastTs = 0;
      function step(ts) {
        if(!inner.isConnected)return;
        if (isPaused) return;
        if (!lastTs) lastTs = ts;
        const dt = (ts - lastTs) / 1000;   // วินาที
        lastTs = ts;
        scrollPos -= pxPerSec * dt;        // เลื่อนตามเวลาจริง (px/วิ × วิ)
        el.style.left = scrollPos + 'px';
        // ★ ข้อความออกจากจอซ้ายหมดแล้ว = ขอบขวาของข้อความ (left + textW) น้อยกว่า 0
        if (scrollPos + textW <= 0) {
          isPaused = true;
          // ★ ซ่อนทันทีที่ออกจากจอ (กัน flash ตอน reset)
          el.style.visibility = 'hidden';
          animId = setTimeout(() => {
            isPaused = false;
            startScrollLoop();
            // ★ โชว์หลังจัดตำแหน่งที่ขอบขวาเรียบร้อยแล้ว
            requestAnimationFrame(() => { el.style.visibility = ''; });
          }, delayMs);
          return;
        }
        animId = requestAnimationFrame(step);
      }
      animId = requestAnimationFrame(step);
    }
    inner._textTimer = animId;
    // ★ double rAF — รอ 2 frames ให้ browser layout เสร็จก่อนวัดความกว้าง
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if(!inner.isConnected)return;
      // เก็บ cleanup function ไว้ใน inner._textCleanup
      inner._textCleanup = () => {
        if (animId) { cancelAnimationFrame(animId); clearTimeout(animId); animId = null; }
      };
      startScrollLoop();
    }));
  } else if (mode === 'schedule') {
    // ★ schedule — หลายข้อความ → สลับตาม interval (เหมือน slideshow)
    const lines = content.split('\n').map(s => s.trim()).filter(s => s);
    if (lines.length === 0) {
      const el = document.createElement('div');
      el.className = 'text-content editor-only';
      el.style.cssText = textStyle;
      el.textContent = '';
      el.style.color = '#64748b';
      inner.appendChild(el);
      return;
    }
    // สร้างทุกบรรทัด
    lines.forEach((line, i) => {
      const el = document.createElement('div');
      el.className = 'text-line' + (i === 0 ? ' active' : '');
      el.style.cssText = textStyle;
      el.textContent = line;
      inner.appendChild(el);
    });
    // ถ้ามีแค่ 1 บรรทัด → ไม่ต้อง timer
    if (lines.length > 1) {
      let idx = 0;
      const intervalMs = computeSlideIntervalMs(w.text_interval, w.text_interval_unit);
      inner._textTimer = setInterval(() => {
        const allLines = inner.querySelectorAll('.text-line');
        allLines.forEach(l => l.classList.remove('active'));
        idx = (idx + 1) % lines.length;
        if (allLines[idx]) allLines[idx].classList.add('active');
      }, intervalMs);
    }
  } else {
    // ★ static — แสดงข้อความเดียวตรงกลาง
    const el = document.createElement('div');
    el.className = content ? 'text-content' : 'text-content editor-only';
    el.style.cssText = textStyle;
    el.textContent = content;
    if (!content) el.style.color = '#64748b';
    inner.appendChild(el);
  }
}

// ════════════════════════════════════════════════════════════
// Video widget — <video> loop (webcam frame animation ฯลฯ)
// ════════════════════════════════════════════════════════════

window.BP3LegacyText={
 dispose(){mounted.forEach(inner=>{if(inner._textCleanup)inner._textCleanup();if(inner._textTimer){clearInterval(inner._textTimer);clearTimeout(inner._textTimer);cancelAnimationFrame(inner._textTimer);}});mounted.clear();},
 mount(){
  (window._overlayWidgets || []).filter(w=>w.type==='text' && !w.hidden && (Object.hasOwn(w,'text_mode') || Object.hasOwn(w,'text_content')) && (!w.textMode || w.textMode===w.text_mode)).forEach(w=>{
   const el=document.querySelector('.widget[data-id="'+CSS.escape(String(w.id))+'"]');if(!el)return;
   const inner=el.querySelector('.composer-widget-inner');if(!inner)return;
   const cfg={...w,text_mode:w.text_mode || (w.textMode==='ticker'?'scroll':w.textMode) || 'static',text_content:w.text_content ?? w.textContent ?? w.text ?? '',text_interval:w.text_interval ?? w.textInterval ?? 10};
   config.font_family=w.fontFamily || w.font_family || 'Kanit';el.classList.add('text-'+cfg.text_mode);setupTextWidget(inner,cfg);mounted.add(inner);
  });
 }
};
})();
