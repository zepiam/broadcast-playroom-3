/* Legacy ASK renderer: behavior and presentation preserved from the reference project. */
(() => {
  'use strict';
  let _lastAskData=null;
  const config={get widgets(){return window._overlayWidgets || [];}};
  function esc(value){return String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function fmtAskCountdown(secLeft) {
  if (secLeft < 0) secLeft = 0;
  const m = Math.floor(secLeft / 60);
  const s = Math.floor(secLeft % 60);
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}

// ★ หัวข้อคำถามยาว → marquee เลื่อนซ้าย (หยุด 1.5 วิทั้งสองปลาย — แบบเดียวกับ np-title)

function setupAskTitleScroll(inner) {
  const wrapEl = inner.querySelector('.ask-question');
  const textEl = inner.querySelector('.ask-question-text');
  if (!wrapEl || !textEl) return;
  if (textEl._askQAnim) cancelAnimationFrame(textEl._askQAnim);
  textEl.style.transform = 'translateX(0)';
  requestAnimationFrame(function() {
    const containerW = wrapEl.clientWidth || 0;
    const textW = textEl.scrollWidth || 0;
    if (textW <= containerW + 5) return;  // สั้นพอ — จัดกึ่งกลางอยู่แล้ว
    const dist = textW - containerW + 20;
    const pauseStart = 1500, pauseEnd = 1500, speed = 30;  // px/วิ
    const scrollDur = (dist / speed) * 1000;
    const totalDur = pauseStart + scrollDur + pauseEnd;
    let startT = null;
    function frame(ts) {
      if (!textEl.isConnected) { cancelAnimationFrame(textEl._askQAnim); return; }  // โพลจบ/เปลี่ยน → หยุด
      if (!startT) startT = ts;
      const t = (ts - startT) % totalDur;
      let x = 0;
      if (t < pauseStart) x = 0;
      else if (t < pauseStart + scrollDur) x = -((t - pauseStart) / scrollDur) * dist;
      else x = -dist;
      textEl.style.transform = 'translateX(' + x + 'px)';
      textEl._askQAnim = requestAnimationFrame(frame);
    }
    textEl._askQAnim = requestAnimationFrame(frame);
  });
}

// ★ อัปเดตเฉพาะตัวเลข/แถบ/winner โดยไม่ rebuild DOM (marquee หัวข้อเลื่อนต่อเนื่อง)

function updateAskDynamic(inner, d, ctx) {
  try {
    const { ended, showCounts, counts, total, maxI, maxC, tie } = ctx;
    // เรียงลำดับเดียวกับตอนสร้าง (ended = มาก→น้อย / voting = ลำดับเดิม)
    let order = (d.choices || []).map((_, i) => i);
    if (ended) {
      order = order.slice().sort((a, b) => (counts[b] || 0) - (counts[a] || 0));
    }
    const choiceEls = inner.querySelectorAll('.ask-choice');
    order.forEach((i, pos) => {
      const el = choiceEls[pos];
      if (!el) return;
      const c = counts[i] || 0;
      const pct = total > 0 ? Math.round(c / total * 100) : 0;
      const win = ended && maxI === i && maxC > 0 && !tie;
      el.classList.toggle('winner', win);
      const cntEl = el.querySelector('.ask-choice-count');
      if (cntEl) cntEl.textContent = c;
      const barEl = el.querySelector('.ask-bar');
      if (barEl) barEl.style.width = pct + '%';
    });
    // footer — ยอดรวม
    const footer = inner.querySelector('.ask-footer span');
    if (footer) {
      footer.innerHTML = (ended ? '<span class="ask-badge-ended">จบโหวต</span>' : '') +
        'โหวตแล้ว ' + total + ' คน';
    }
  } catch (e) { /* ไม่ให้พัง render */ }
}


function renderAskInto(inner) {
  const d = _lastAskData;
  const idle = !d || !d.active;
  // ★ idle → ซ่อนแผง (overlay หายทั้งก้อน / editor เห็นเส้นประเต็มจอ + ป้าย)
  inner.classList.toggle('ask-idle', idle);
  if (idle) {
    inner.innerHTML = '';
    delete inner.dataset.askSig;  // ★ โพลจบ → เคลียร์ (โพลใหม่ rebuild ใหม่)
    return;
  }
  // ★ config ของ widget (โหมด/สไตล์ countdown)
  const _wEl = inner.closest ? inner.closest('.widget') : null;
  const baseW = (_wEl && typeof config !== 'undefined' && config.widgets)
    ? (config.widgets.find(x => x.id === _wEl.dataset.id) || {}) : {};
  const _w = Object.assign({}, baseW, _lastAskData || {});
  const _mode = { card: 'minimal', bar: 'hband', tower: 'vright' }[_w.ask_layout] || _w.ask_layout || 'vright';
  const cdStyle = _w.ask_countdown_style || 'text';

  const ended = d.phase === 'ended';
  const showCounts = ended || d.realtime;
  const counts = d.counts || [];
  const total = d.total_voters || 0;
  let maxI = -1, maxC = 0, tie = false;
  if (ended) {
    for (let i = 0; i < counts.length; i++) {
      if (counts[i] > maxC) { maxC = counts[i]; maxI = i; tie = false; }
      else if (counts[i] === maxC && maxC > 0) { tie = true; }
    }
  }
  let html = '';
  // ★ แผงโพลจริง — anchor class แยกตามโหมด (hband ใช้ top/middle/bottom, minimal/lite ใช้มุม)
  html += '<div class="ask-panel ' + (_mode === 'hband' ? 'hband-anchor' : '') +
          (_mode === 'minimal' || _mode === 'lite' ? ' min-anchor' : '') + '">';
  html += '<div class="ask-question"><span class="ask-question-text">' + (ended ? 'ผลสรุป : ' : '') + esc(d.question || '') + '</span></div>';
  html += '<div class="ask-choices">';
  // ★ หน้าสรุปผล — เรียงจากโหวตเยอะสุด → น้อยสุด (ไม่เรียง A B C)
  //   ระหว่างโหวตคงลำดับเดิม
  let order = (d.choices || []).map((_, i) => i);
  if (ended) {
    order = order.slice().sort((a, b) => (counts[b] || 0) - (counts[a] || 0));
  }
  order.forEach((i) => {
    const label = d.choices[i];
    const key = (d.keys && d.keys[i]) ? d.keys[i] : String.fromCharCode(65 + i);
    const c = counts[i] || 0;
    const pct = total > 0 ? Math.round(c / total * 100) : 0;
    const win = ended && maxI === i && maxC > 0 && !tie;
    html += '<div class="ask-choice' + (win ? ' winner' : '') + '">';
    // ★ บรรทัด 1: ป้ายวิธีโหวต [พิมพ์ "A"] ซ้าย + ยอดโหวตขวา
    html += '<div class="ask-choice-top">';
    html += '<span class="ask-choice-key">พิมพ์ &quot;' + esc(key) + '&quot;</span>';
    if (showCounts) html += '<span class="ask-choice-count">' + c + '</span>';
    html += '</div>';
    // ★ บรรทัด 2: เนื้อหาช้อยส์ (responsive wrap เต็มข้อความ ไม่มี ...)
    html += '<div class="ask-choice-label">' + esc(label) + '</div>';
    if (showCounts) html += '<div class="ask-bar-wrap"><div class="ask-bar" style="width:' + pct + '%"></div></div>';
    html += '</div>';
  });
  html += '</div>';
  html += '<div class="ask-footer">';
  html += '<span>' + (ended ? '<span class="ask-badge-ended">จบโหวต</span>' : '') +
          'โหวตแล้ว ' + total + ' คน</span>';
  let timebar = '';
  if (ended) {
    // ★ คำว่า "ผลสรุป" ย้ายไปหน้าคำถามแล้ว — footer ขวาเว้นว่าง (ซ้ายมี badge จบโหวต+ยอดรวม)
  } else if (d.end_ts) {
    if (cdStyle === 'text' || cdStyle === 'both') {
      html += '<span class="ask-countdown" data-endts="' + d.end_ts + '">จะหมดเวลาในอีก --:--</span>';
    }
    if (cdStyle === 'bar' || cdStyle === 'both') {
      // ★ สร้างหลอดที่ค่าถูกต้องเลยตั้งแต่ตอน rebuild (ทุกโหวต = rebuild ทั้งแผง)
      //   เดิมเกิดที่ 100% เขียวแล้วดีดไปค่าจริงผ่าน transition = กระตุก
      const _dur = d.duration_sec || 0;
      const _left = d.end_ts - (Date.now() / 1000);
      const _pct = _dur > 0 ? Math.max(0, Math.min(100, (_left / _dur) * 100)) : 0;
      const _cls = _pct <= 10 ? 'tb-red' : (_pct <= 50 ? 'tb-yellow' : 'tb-green');
      timebar = '<div class="ask-timebar" data-endts="' + d.end_ts +
        '" data-dur="' + _dur + '">' +
        '<div class="ask-timebar-fill ' + _cls + '" style="width:' + _pct + '%"></div></div>';
    }
  } else {
    html += '<span>ไม่จำกัดเวลา</span>';
  }
  html += '</div>';
  html += timebar;
  html += '</div>';  // /.ask-panel

  // ★ ถ้าเป็นแค่ "โหวตเพิ่ม" (คำถาม+ช้อยส์+phase เดิม) → อัปเดตเฉพาะตัวเลข/แถบ
  //   ไม่ rebuild ทั้งแผง → marquee หัวข้อไม่ถูกรีเซ็ต + ไม่กระพริบ
  const _prevKey = inner.dataset.askSig || '';
  const _thisKey = [d.question, d.choices.join('|'), d.phase, _mode].join('§');
  if (_prevKey === _thisKey) {
    updateAskDynamic(inner, d, { ended, showCounts, counts, total, maxI, maxC, tie });
    return;  // ★ ไม่แตะ innerHTML → marquee ยังเลื่อนต่อเนื่อง
  }
  inner.dataset.askSig = _thisKey;

  inner.innerHTML = html;
  setupAskTitleScroll(inner);  // ★ หัวข้อยาว → marquee (เหมือน Now Playing — ครั้งแรกเท่านั้น)
  askClampMinimal(_wEl);  // ★ Minimal — clamp กึ่งกลางกล่องกันล้นครึ่งตัวออกนอกขอบ
  tickAskCountdowns();
}

// ★ Minimal — clamp กึ่งกลางกล่องให้อยู่ใน canvas เสมอ (ไม่ให้ล้นครึ่งตัวออกนอกขอบ)
//   เรียกทั้งตอนสร้างแผง (renderAskInto) และตอนลาก slider ตำแหน่งสด (askLivePos)
//   ovX/ovY = ค่าจาก slider ตอนนี้ (override ค่าใน config — ยังไม่ได้กดบันทึก)

function askClampMinimal(wEl, ovX, ovY) {
  if (!wEl) return;
  const inner = wEl.querySelector('.widget-inner');
  if (!inner) return;
  const _w = (typeof config !== 'undefined' && config.widgets)
    ? (config.widgets.find(x => x.id === wEl.dataset.id) || {}) : {};
  const _mode = { card: 'minimal', bar: 'hband', tower: 'vright' }[_w.ask_layout] || _w.ask_layout || 'vright';
  if (_mode !== 'minimal' && _mode !== 'lite') return;
  const panel = inner.querySelector('.ask-panel');
  if (!panel) return;
  const cw = inner.offsetWidth || 1920, ch = inner.offsetHeight || 1080;
  const pw = panel.offsetWidth, ph = panel.offsetHeight;
  const px = (ovX != null) ? ovX : (_w.ask_pos_x != null ? _w.ask_pos_x : 85);
  const py = (ovY != null) ? ovY : (_w.ask_pos_y != null ? _w.ask_pos_y : 12);
  const cx = Math.min(Math.max(px / 100 * cw, pw / 2), cw - pw / 2);
  const cy = Math.min(Math.max(py / 100 * ch, ph / 2), ch - ph / 2);
  panel.style.setProperty('--ask-min-x', cx + 'px');
  panel.style.setProperty('--ask-min-y', cy + 'px');
  panel.classList.add('ask-min-fixed');
}

// ★ ASK widget classes — theme/bar/frame/mode/anchor (ใช้ร่วม update/create + self-heal)

function askWidgetClasses(w) {
  // ★ legacy: glass/mono ถูกถอดออก — map ไปธีมใกล้เคียงให้อัตโนมัติ
  const _th = { glass: 'ice', mono: 'steel' }[w.ask_theme] || w.ask_theme || 'violet';
  // ★ โหมดวาง (vleft/vright/hband/minimal) — เดิม card/bar/tower map ให้อัตโนมัติ
  const _mode = { card: 'minimal', bar: 'hband', tower: 'vright' }[w.ask_layout] || w.ask_layout || 'vright';
  const _anchor = w.ask_anchor || (_mode === 'hband' ? 'middle' : 'tr');
  return [
    'ask-theme-' + _th,
    'ask-bar-' + (w.ask_bar_style || 'classic'),
    'ask-frame-' + (w.ask_frame_style || 'classic'),
    'ask-mode-' + _mode,
    'ask-anchor-' + _anchor,
  ];
}

// ★ live preview — ลาก slider ตำแหน่ง X/Y (Minimal) แล้วแผงขยับทันทีบน editor canvas
//   เดิมต้องหยุดเดโมแล้วเปิดใหม่ถึงเห็น เพราะแผงถูก pin ด้วย px ตอนสร้าง
//   + signature เปรียบเทียบ rebuild ไม่รวมค่าตำแหน่ง → เปลี่ยน config ก็ไม่ rebuild

function tickAskCountdowns() {
  // ★ อัปเดตเฉพาะ "ตัวเลข" นับถอยหลัง (เปลี่ยนทุก 1 วิ — พอ)
  const now = Date.now() / 1000;
  // ★ Demo Mode Loop Support: ถ้ากำลังรัน demo โหวตและเวลาหมด ให้ต่ออายุ endts ใหม่ 10 วินาทีอัตโนมัติ
  if (_lastAskData && _lastAskData.is_demo && _lastAskData.phase === 'voting') {
    if (_lastAskData.end_ts && _lastAskData.end_ts <= now) {
      _lastAskData.end_ts = now + 10;
      _lastAskData.duration_sec = 10;
      document.querySelectorAll('.ask-countdown[data-endts], .ask-timebar[data-endts]').forEach(el => {
        el.dataset.endts = _lastAskData.end_ts;
        el.dataset.dur = 10;
      });
    }
  }

  document.querySelectorAll('.ask-countdown[data-endts]').forEach(el => {
    const left = parseFloat(el.dataset.endts) - now;
    if (left <= 0) {
      el.textContent = 'กำลังปิดโหวต...';
    } else {
      el.textContent = 'จะหมดเวลาในอีก ' + fmtAskCountdown(left);
    }
  });
}
  window.BP3LegacyAsk={render(data){
    _lastAskData = data && data.active ? {
      ...data, choices:(data.choices || []).map(c=>c.text),keys:(data.choices || []).map(c=>c.label),
      counts:(data.choices || []).map(c=>c.votes || 0),total_voters:data.totalVotes || 0,
      duration_sec:data.durationSec || 0,
      end_ts:data.phase==='voting' && data.remainingSec!=null ? Date.now()/1000+data.remainingSec : null
    } : null;
    let widgets = document.querySelectorAll('.widget.type-ask');
    if (!widgets.length && data && data.active) {
      let dynamic = document.getElementById('on-demand-ask-overlay');
      if (!dynamic) {
        dynamic = document.createElement('div');
        dynamic.id = 'on-demand-ask-overlay';
        dynamic.className = 'widget type-ask';
        dynamic.dataset.id = 'dynamic_ask';
        document.body.appendChild(dynamic);
      }
      widgets = [dynamic];
    } else if (!data || !data.active) {
      document.getElementById('on-demand-ask-overlay')?.remove();
    }
    widgets.forEach(el=>{
      const w={ ...(config.widgets?.find(item=>item.id===el.dataset.id) || {}), ...(data?.widget || {}) };
      Array.from(el.classList).filter(c=>/^ask-(theme|bar|frame|mode|anchor)-/.test(c)).forEach(c=>el.classList.remove(c));
      el.classList.add(...askWidgetClasses(w));
      let inner=el.querySelector('.widget-inner');
      if(!inner){inner=document.createElement('div');inner.className='widget-inner composer-widget-inner';inner.id='compAskPanel_'+w.id;el.replaceChildren(inner);}
      inner.style.display=_lastAskData?'block':'none';
      const props={'--ask-scale':w.ask_scale ?? 1,'--ask-extend':w.ask_extend_pct ?? 20,'--ask-px':w.ask_pos_x ?? 85,'--ask-py':w.ask_pos_y ?? 12,'--ask-ox':w.ask_offset_x ?? 0,'--ask-oy':w.ask_offset_y ?? 0,'--ask-opacity':(w.ask_opacity_pct ?? 100)/100,'--ask-minw':w.ask_min_width ?? 340,'--ask-qfs':w.ask_question_fs ?? 24,'--ask-cfs':w.ask_choice_fs ?? 18};
      for(const [name,value] of Object.entries(props))inner.style.setProperty(name,value);
      renderAskInto(inner);askClampMinimal(el);
      const choices=inner.querySelector('.ask-choices');if(choices)choices.id='compAskChoicesList_'+w.id;
      const question=inner.querySelector('.ask-question-text');if(question)question.id='compAskQ_'+w.id;
      const countdown=inner.querySelector('.ask-countdown');
      if(countdown)countdown.textContent='จะหมดเวลาในอีก '+fmtAskCountdown(data.remainingSec || 0);
      if(data?.phase==='paused'){const footer=inner.querySelector('.ask-footer');if(footer)footer.lastElementChild.textContent='พักการโหวต';}
    });
  }};
})();
