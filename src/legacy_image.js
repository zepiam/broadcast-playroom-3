/* Image/slideshow runtime preserved from broadcast playroom dev. */
(() => {
'use strict';
const isEditor=false;
function computeSlideIntervalMs(interval, unit) {
  const n = Math.max(1, parseInt(interval) || 10);
  if (unit === 'minutes') return n * 60 * 1000;
  if (unit === 'hours') return n * 60 * 60 * 1000;
  return n * 1000; // seconds (default)
}

// ★ setup image widget: สร้าง slides + เริ่ม slideshow loop
function setupImageWidget(inner, w) {
  const signature=JSON.stringify(Object.fromEntries(Object.entries(w).filter(([key])=>!['x','y','width','height','w','h','z','opacity'].includes(key))));if(inner._bpRuntimeConfig===signature)return;inner._bpRuntimeConfig=signature;
  const structure=JSON.stringify([w.images,w.image_mode,w.shuffle,w.slide_interval,w.slide_interval_unit,w.timer_interval_sec,w.timer_slide_duration,w.timer_anim_in,w.timer_anim_out,w.timer_anim_in_ms,w.timer_anim_out_ms]);
  if(inner._bpImageStructure===structure && inner.querySelector('img')){inner.querySelectorAll('img').forEach(img=>img.style.objectFit=w.fitMode || w.fit_mode || 'cover');return;}
  inner._bpImageStructure=structure;
  // ★ clear ทุก timer (slideshow + timer mode)
  if (inner._slideTimer) { clearInterval(inner._slideTimer); inner._slideTimer = null; }
  if (inner._timerCycle) { clearInterval(inner._timerCycle); inner._timerCycle = null; }
  if (inner._timerSlide) { clearInterval(inner._timerSlide); inner._timerSlide = null; }
  if (inner._timerAnimTOs) { inner._timerAnimTOs.forEach(clearTimeout); inner._timerAnimTOs = []; }
  if (inner._timerRAF) { cancelAnimationFrame(inner._timerRAF); inner._timerRAF = null; }
  while (inner.firstChild) inner.removeChild(inner.firstChild);
  const _widgetEl = inner.closest('.widget');
  if (_widgetEl) _widgetEl.classList.remove('timer-hidden');

  const images = w.images || [];
  if (images.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'image-empty editor-only';
    empty.textContent = '📷 ยังไม่มีรูป — คลิก ⚙ เพื่ออัปโหลด';
    inner.appendChild(empty);
    return;
  }

  const fitMode = w.fit_mode || 'cover';
  // ★ shuffle: สุ่มลำดับ (เก็บ original ไว้)
  let imgList = images.slice();
  if (w.shuffle) {
    for (let i = imgList.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [imgList[i], imgList[j]] = [imgList[j], imgList[i]];
    }
  }

  // ★ สร้าง <img> slides ทั้งหมด (preload + cache-bust)
  const slides = imgList.map(img => {
    const el = document.createElement('img');
    el.className = 'slide';
    el.src = `/widget-image/${encodeURIComponent(w.id)}/${encodeURIComponent(img.id)}?t=${Date.now()}`;
    el.style.objectFit = fitMode;
    el.draggable = false;
    return el;
  });
  slides.forEach(s => inner.appendChild(s));

  // ★ slide counter (editor only)
  let counterEl = null;
  if (isEditor) {
    counterEl = document.createElement('div');
    counterEl.className = 'slide-counter';
    inner.appendChild(counterEl);
  }

  // ★ Timer mode → วงจร ขึ้นมา → เลื่อนภาพ → หายไป → รอรอบหน้า
  if (w.image_mode === 'timer') {
    setupImageTimer(inner, inner.closest('.widget'), slides, w, counterEl);
    return;
  }

  // ★ single image → ไม่ต้อง slideshow
  if (slides.length === 1) {
    slides[0].classList.add('active');
    if (counterEl) counterEl.textContent = '1/1';
    return;
  }

  // ★ slideshow loop
  let currentIdx = 0;
  slides[0].classList.add('active');
  if (counterEl) counterEl.textContent = `1/${slides.length}`;

  const intervalMs = computeSlideIntervalMs(w.slide_interval, w.slide_interval_unit);
  const transition = w.transition || 'fade';
  inner._slideTimer = setInterval(() => {
    if(!inner.isConnected){clearInterval(inner._slideTimer);return;}
    const prev = slides[currentIdx];
    const nextIdx = (currentIdx + 1) % slides.length;
    const next = slides[nextIdx];
    // ★ transition: สลับ active class (CSS จัดการ animation)
    //    สำหรับ slide-* transitions → ต้องมี exiting class ชั่วคราว
    if (transition.startsWith('slide-')) {
      prev.classList.add('exiting');
      next.classList.add('active');
      // ลบ exiting หลัง transition จบ (0.6s)
      setTimeout(() => prev.classList.remove('active', 'exiting'), 650);
    } else {
      prev.classList.remove('active');
      next.classList.add('active');
    }
    currentIdx = nextIdx;
    if (counterEl) counterEl.textContent = `${nextIdx + 1}/${slides.length}`;
  }, intervalMs);
}


// ════════════════════════════════════════════════════════════
// ★ Image Timer Mode — setTimeout chain (ไม่ใช้ setInterval กัน drift)
//   โฟลว์: ซ่อน → [รอ waitSec] → anim IN → [แต่ละภาพ slideDurSec] → anim OUT → ซ่อน → วนซ้ำ
// ════════════════════════════════════════════════════════════
function setupImageTimer(inner, widgetEl, slides, w, counterEl) {
  if (!widgetEl) return;
  const TOs = [];
  inner._timerAnimTOs = TOs;
  const clearAll = () => {
    TOs.forEach(clearTimeout); TOs.length = 0;
    if (inner._timerSlide) { clearInterval(inner._timerSlide); inner._timerSlide = null; }
    if (inner._timerRAF) { cancelAnimationFrame(inner._timerRAF); inner._timerRAF = null; }
  };

  // ★ config
  const waitSec = Math.max(1, Number(w.timer_interval_sec) || 600);   // รอกี่วิหลังหายไป
  const slideDurSec = Math.max(1, Number(w.timer_slide_duration) || 10); // แต่ละภาพกี่วิ
  const animIn = w.timer_anim_in || 'fade';
  // ★ auto = กลับทางเดิมอัตโนมัติ (ใช้ทางเดียวกับ entrance)
  const animOut = (!w.timer_anim_out || w.timer_anim_out === 'auto') ? animIn : w.timer_anim_out;
  const ANIM_IN_MS = Math.max(100, Number(w.timer_anim_in_ms) || 2000);
  const ANIM_OUT_MS = Math.max(100, Number(w.timer_anim_out_ms) || 2000);
  // ★ set CSS var ให้ animation duration ตรงกับที่ตั้ง
  inner.style.setProperty('--t-anim-in-dur', (ANIM_IN_MS / 1000) + 's');
  inner.style.setProperty('--t-anim-out-dur', (ANIM_OUT_MS / 1000) + 's');
  const TRANS_SEC = 0.5; // transition ระหว่างภาพ

  // ★ progress bar
  const progWrap = document.createElement('div');
  progWrap.className = 't-progress-wrap';
  const progBar = document.createElement('div');
  progBar.className = 't-progress-bar';
  progWrap.appendChild(progBar);
  progWrap.style.display = 'none';
  inner.appendChild(progWrap);

  let rafId = null;
  function startProgress(totalMs) {
    if (rafId) cancelAnimationFrame(rafId);
    const t0 = performance.now();
    progWrap.style.display = '';
    progBar.style.width = '0%';
    function tick() {
      if(!inner.isConnected)return;
      const pct = Math.min(100, ((performance.now() - t0) / totalMs) * 100);
      progBar.style.width = pct + '%';
      if (pct < 100) rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);
    inner._timerRAF = rafId;
  }
  function stopProgress() {
    if (rafId) cancelAnimationFrame(rafId);
    progWrap.style.display = 'none';
  }

  function hide() {
    widgetEl.classList.add('timer-hidden');
    inner.style.opacity = '0';
    inner.className = 'widget-inner';
    stopProgress();
    // ★ หลังหาย → รอ waitSec → กลับมาอีกครั้ง
    TOs.push(setTimeout(showCycle, waitSec * 1000));
  }

  function showCycle() {
    clearAll();
    // ★ entrance animation
    widgetEl.classList.remove('timer-hidden');
    inner.style.opacity = '';
    inner.className = 'widget-inner';
    inner.classList.add('t-anim-in', 't-anim-in-' + animIn);
    slides.forEach(s => s.classList.remove('active', 'exiting'));
    slides[0].classList.add('active');
    if (counterEl) counterEl.textContent = `1/${slides.length}`;
    let idx = 0;

    // ★ หลัง anim IN เสร็จ → เริ่มเลื่อนภาพ + progress
    TOs.push(setTimeout(() => {
      inner.classList.remove('t-anim-in', 't-anim-in-' + animIn);

      // เวลาแสดงทั้งหมด = ภาพแรก (slideDurSec) + transition ต่อ (slides.length - 1) ภาพ × (TRANS_SEC + slideDurSec)
      const totalShowMs = (slideDurSec + (slides.length - 1) * (TRANS_SEC + slideDurSec)) * 1000;
      startProgress(totalShowMs);

      if (slides.length > 1) {
        inner._timerSlide = setInterval(() => {
          const prev = slides[idx];
          idx = idx + 1;
          if (idx >= slides.length) {
            // ★ ครบทุกภาพแล้ว — หยุด ไม่วนกลับภาพ 1 (ให้ exit timer ทำงานต่อ)
            clearInterval(inner._timerSlide);
            return;
          }
          const next = slides[idx];
          const trans = w.transition || 'fade';
          if (trans.startsWith('slide-')) {
            prev.classList.add('exiting');
            next.classList.add('active');
            setTimeout(() => prev.classList.remove('active', 'exiting'), 650);
          } else {
            prev.classList.remove('active');
            next.classList.add('active');
          }
          if (counterEl) counterEl.textContent = `${idx + 1}/${slides.length}`;
        }, (slideDurSec + TRANS_SEC) * 1000);
      }

      // ★ exit — หลังแสดงครบทุกภาพ
      const exitTO = setTimeout(() => {
        if (inner._timerSlide) clearInterval(inner._timerSlide);
        stopProgress();
        inner.classList.add('t-anim-out', 't-anim-out-' + animOut);
        TOs.push(setTimeout(() => hide(), ANIM_OUT_MS + 100));
      }, totalShowMs + ANIM_IN_MS);
      TOs.push(exitTO);
    }, ANIM_IN_MS + 100));
  }

  // ★ เริ่ม: ซ่อน → รอ 1 วิ → รอบแรก
  widgetEl.classList.add('timer-hidden');
  inner.style.opacity = '0';
  TOs.push(setTimeout(showCycle, 1000));
}

// ════════════════════════════════════════════════════════════
// Webcam Frame widget — กรอบตกแต่งล้วน (ไม่มี video)
// ════════════════════════════════════════════════════════════

// ★ คำนวณ height จาก width + ratio (บังคับสัดส่วน)

window.BP3LegacyImages={
 dispose(){document.querySelectorAll('.widget.type-image .widget-inner').forEach(inner=>{
   ['_slideTimer','_timerCycle','_timerSlide'].forEach(key=>clearInterval(inner[key]));
   (inner._timerAnimTOs || []).forEach(clearTimeout);if(inner._timerRAF)cancelAnimationFrame(inner._timerRAF);
 });},
 mount(){(window._overlayWidgets || []).filter(w=>w.type==='image' && w.images?.length).forEach(w=>{
   const el=document.querySelector(`.widget[data-id="${CSS.escape(w.id)}"]`);if(!el)return;
   el.classList.add('tr-'+(w.transition || 'fade'));
   let inner=el.querySelector('.composer-widget-inner');if(!inner)return;
   inner.classList.add('widget-inner');inner.style.cssText='position:relative;width:100%;height:100%;background:transparent;overflow:hidden;';
   setupImageWidget(inner,w);
 });}
};
})();
