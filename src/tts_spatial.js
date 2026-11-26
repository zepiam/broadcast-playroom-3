/* TTS spatial position: place the chat-reading voice around the listener (left/right, front/back, near/far).
   Engine: Web Audio PannerNode (HRTF). Front/back needs headphones; left/right and distance work on speakers.
   Default = centre: audio is NOT routed through Web Audio at all, so playback is identical to before.
   Setting: localStorage 'bp3_tts_spatial' = {x, y} in [-1, 1] (x: right +, y: front +); synced across windows. */
(() => {
  'use strict';
  const KEY = 'bp3_tts_spatial';
  const CENTER_EPS = 0.06;
  const PRESETS = [
    { id: 'center', label: 'ตรงกลาง', x: 0, y: 0 },
    { id: 'front', label: 'ข้างหน้า', x: 0, y: 0.7 },
    { id: 'left', label: 'ข้างหูซ้าย', x: -0.75, y: 0 },
    { id: 'right', label: 'ข้างหูขวา', x: 0.75, y: 0 },
    { id: 'back', label: 'ด้านหลัง', x: 0, y: -0.7 },
    { id: 'whisper', label: 'กระซิบข้างหู', x: 0.22, y: 0.05 },
    { id: 'far', label: 'ไกลออกไป', x: 0, y: 1 },
  ];

  const DEFAULT_SPOT = { x: 0.55, y: 0.35 };   // used when 3D is switched on without a chosen spot
  function clamp(v) { v = Number(v); return Number.isFinite(v) ? Math.max(-1, Math.min(1, v)) : 0; }
  function normalizePos(p) {
    let x = clamp(p && p.x), y = clamp(p && p.y);
    const r = Math.hypot(x, y);
    if (r > 1) { x /= r; y /= r; }
    if (Math.hypot(x, y) < CENTER_EPS) { x = 0; y = 0; }
    return { x, y };
  }
  const posIsCenter = p => p.x === 0 && p.y === 0;
  // state: {x, y} = remembered position, on = 3D enabled. Effective 3D = on && position not centre.
  function normalize(raw) {
    const pos = normalizePos(raw);
    const on = raw && typeof raw.on === 'boolean' ? raw.on : !posIsCenter(pos);   // older saves had no flag
    return { ...pos, on: on && !posIsCenter(pos) };
  }
  function load() {
    try { return normalize(JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (_) { return { x: 0, y: 0, on: false }; }
  }
  let state = load();
  // "centre" = no spatial processing (3D off, or position in the middle).
  const isCenter = (p = state) => !p.on || posIsCenter(p);

  // ---- engine -------------------------------------------------------------------------------
  let ctx = null;
  const routed = new Set();   // {audio, panner}
  function getCtx() {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      try { ctx = new AC(); } catch (_) { return null; }
    }
    if (ctx.state === 'suspended') ctx.resume().catch(() => {});
    return ctx;
  }
  // Map the pad position to metres around the listener (Web Audio: x right, -z front, listener at origin).
  function placement(p) {
    const r = Math.hypot(p.x, p.y);
    const meters = 0.35 + r * 3.2;                 // whisper ~0.4 m ... far ~3.5 m
    const ang = Math.atan2(p.x, p.y);              // 0 = front, +90deg = right
    return { x: Math.sin(ang) * meters, y: 0, z: -Math.cos(ang) * meters };
  }
  function applyTo(panner, p) {
    // 3D switched off while a voice is already routed: bring it to just in front (closest to normal sound).
    const pos = isCenter(p) ? { x: 0, y: 0, z: -1 } : placement(p);
    const t = ctx ? ctx.currentTime : 0;
    if (panner.positionX) {
      panner.positionX.setTargetAtTime(pos.x, t, 0.03);
      panner.positionY.setTargetAtTime(pos.y, t, 0.03);
      panner.positionZ.setTargetAtTime(pos.z, t, 0.03);
    } else panner.setPosition(pos.x, pos.y, pos.z);
  }
  /** Route one TTS <audio> element through the panner (no-op when centred or Web Audio unavailable). */
  function attach(audio) {
    try {
      if (!audio || audio._bp3Spatial || isCenter()) return audio;
      const c = getCtx();
      if (!c || c.state !== 'running') return audio;          // never risk silence: play normally instead
      const src = c.createMediaElementSource(audio);
      const panner = new PannerNode(c, { panningModel: 'HRTF', distanceModel: 'inverse', refDistance: 1, rolloffFactor: 0.45, maxDistance: 50 });
      applyTo(panner, state);
      // HRTF raises the near ear by up to ~4 dB: a brick-wall limiter near 0 dBFS stops loud speech clipping
      // without changing normal levels.
      const limiter = new DynamicsCompressorNode(c, { threshold: -2, knee: 0, ratio: 20, attack: 0.002, release: 0.08 });
      src.connect(panner).connect(limiter).connect(c.destination);
      const entry = { audio, panner };
      audio._bp3Spatial = entry;
      routed.add(entry);
      const drop = () => routed.delete(entry);
      audio.addEventListener('ended', drop, { once: true });
      audio.addEventListener('error', drop, { once: true });
    } catch (err) {
      console.warn('[BP3] spatial TTS unavailable, playing normally:', err);
    }
    return audio;
  }
  function commit(next, persist = true) {
    state = normalize(next);
    if (persist) { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) {} }
    for (const e of routed) applyTo(e.panner, state);   // live update for voices already playing
    if (!isCenter()) getCtx();                          // have the context running before the next message
    renderAll();
  }
  /** Choose a position (pad / preset / arrows). Picking a spot turns 3D on; picking the centre turns it off. */
  function setPosition(p) {
    const pos = normalizePos(p);
    commit({ ...pos, on: !posIsCenter(pos) });
  }
  /** Top-bar toggle: off = normal TTS but remember the spot; on = back to the remembered (or a default) spot. */
  function setOn(on) {
    if (on) {
      const pos = posIsCenter(state) ? DEFAULT_SPOT : { x: state.x, y: state.y };
      commit({ ...pos, on: true });
    } else commit({ x: state.x, y: state.y, on: false });
  }
  window.addEventListener('storage', e => { if (e.key === KEY) commit(load(), false); });
  // Prime the context early so it is already running when the first chat message plays.
  if (!isCenter()) getCtx();
  window.bp3SpatialAudio = {
    attach, get: () => ({ ...state }), set: p => setPosition(p), setOn, toggle: () => setOn(isCenter()),
    isCenter: () => isCenter(), isOn: () => !isCenter(),
  };

  // ---- UI: position pad card ----------------------------------------------------------------
  function direction(p) {
    const deg = (Math.atan2(p.x, p.y) * 180 / Math.PI + 360) % 360;
    return ['ข้างหน้า', 'ขวาหน้า', 'ขวา', 'ขวาหลัง', 'ด้านหลัง', 'ซ้ายหลัง', 'ซ้าย', 'ซ้ายหน้า'][Math.round(deg / 45) % 8];
  }
  function describe(p) {
    if (!p.on && !posIsCenter(p)) return 'ปิด 3D อยู่ • เสียงปกติ';
    if (isCenter(p)) return 'ตรงกลาง • เสียงปกติ';
    const r = Math.hypot(p.x, p.y);
    const dir = direction(p);
    const dist = r < 0.3 ? 'ใกล้มาก' : r < 0.6 ? 'ใกล้' : r < 0.85 ? 'ปานกลาง' : 'ไกล';
    return dir + ' • ระยะ' + dist;
  }
  const CSS = `
.bp3-spatial-card .sp-body{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.bp3-spatial-card .sp-wrap{position:relative;flex:0 0 268px;width:268px;height:258px;display:flex;align-items:center;justify-content:center}
.bp3-spatial-card .sp-pad{position:relative;width:220px;height:220px;flex:0 0 220px;border-radius:50%;background:radial-gradient(circle,rgba(124,58,237,.10) 0,rgba(15,23,42,.6) 70%);border:1px solid rgba(148,163,184,.25);touch-action:none;cursor:crosshair;outline:none}
.bp3-spatial-card .sp-pad:focus-visible{box-shadow:0 0 0 2px #a78bfa}
.bp3-spatial-card .sp-ring{position:absolute;border:1px dashed rgba(148,163,184,.22);border-radius:50%;pointer-events:none}
.bp3-spatial-card .sp-axis{position:absolute;background:rgba(148,163,184,.14);pointer-events:none}
.bp3-spatial-card .sp-lbl{position:absolute;font-size:11px;color:#94a3b8;pointer-events:none;transform:translate(-50%,-50%);white-space:nowrap}
.bp3-spatial-card .sp-head{position:absolute;left:50%;top:50%;width:46px;height:52px;transform:translate(-50%,-50%);pointer-events:none}
.bp3-spatial-card .sp-dot{position:absolute;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:#a78bfa;border:2px solid #fff;box-shadow:0 0 0 4px rgba(167,139,250,.28);pointer-events:none;display:flex;align-items:center;justify-content:center}
.bp3-spatial-card .sp-dot svg{width:12px;height:12px}
.bp3-spatial-card .sp-dot.center{background:#64748b;box-shadow:none}
.bp3-spatial-card .sp-side{flex:1;min-width:200px;display:flex;flex-direction:column;gap:10px}
.bp3-spatial-card .sp-readout{font-size:14px;font-weight:600;color:#e2e8f0}
.bp3-spatial-card .sp-hint{font-size:12px;color:#94a3b8;line-height:1.5}
.bp3-spatial-card .sp-presets{display:flex;flex-wrap:wrap;gap:6px}
.bp3-spatial-card .sp-chip{background:rgba(30,41,59,.9);color:#cbd5e1;border:1px solid rgba(148,163,184,.3);border-radius:999px;padding:4px 11px;font-size:12px;cursor:pointer}
.bp3-spatial-card .sp-chip:hover{border-color:#a78bfa;color:#fff}
.bp3-spatial-card .sp-chip.active{background:#7c3aed;border-color:#7c3aed;color:#fff}
.bp3-spatial-card .sp-test{align-self:flex-start;display:inline-flex;align-items:center;gap:6px}
`;
  const HEAD_SVG = '<svg class="sp-head" viewBox="0 0 46 52" aria-hidden="true"><ellipse cx="4" cy="28" rx="4" ry="7" fill="#475569"/><ellipse cx="42" cy="28" rx="4" ry="7" fill="#475569"/><ellipse cx="23" cy="28" rx="18" ry="21" fill="#64748b"/><path d="M23 3 l5 8 h-10z" fill="#94a3b8"/><circle cx="23" cy="28" r="18" fill="none" stroke="#94a3b8" stroke-opacity=".5"/></svg>';
  const SPEAKER_SVG = '<svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z"/></svg>';
  const cards = new Set();

  function testText() {
    let t = '';
    try { t = localStorage.getItem('bp3_tts_test_message') || ''; } catch (_) {}
    if (!t) t = document.getElementById('txtVoiceTestMessage')?.value || document.getElementById('secTxtVoiceTestMessage')?.value || '';
    return (t || 'สวัสดีครับ ยินดีต้อนรับทุกคนเข้าสู่ห้องแชทไลฟ์สตรีม!').trim();
  }
  let testAudio = null;
  function stopTest() {
    if (testAudio) { try { testAudio.pause(); } catch (_) {} testAudio = null; }
    renderAll();
  }
  async function playTest() {
    if (testAudio) { stopTest(); return; }
    const pr = (window.getTtsProsodyForPreview && window.getTtsProsodyForPreview()) || { query: '', volume: 0.8 };
    const gender = window._currentVoiceGender || 'female';
    const url = '/api/tts?text=' + encodeURIComponent(testText()) + '&gender=' + encodeURIComponent(gender) + (pr.query || '');
    const audio = new Audio(url);
    audio.volume = Math.max(0, Math.min(1, pr.volume ?? 0.8));
    // A click is a user gesture: make sure the context is running before routing (popouts lack the autoplay flag).
    if (!isCenter()) { const c = getCtx(); if (c && c.state !== 'running') { try { await c.resume(); } catch (_) {} } }
    attach(audio);
    testAudio = audio;
    audio.addEventListener('ended', () => { if (testAudio === audio) { testAudio = null; renderAll(); } });
    audio.addEventListener('error', () => { if (testAudio === audio) { testAudio = null; renderAll(); if (window.showToast) window.showToast('ทดสอบเสียงไม่สำเร็จ'); } });
    renderAll();
    try { await audio.play(); } catch (_) { if (testAudio === audio) { testAudio = null; renderAll(); } }
  }

  function buildCard(doc) {
    if (!doc.getElementById('bp3-spatial-style')) {
      const st = doc.createElement('style'); st.id = 'bp3-spatial-style'; st.textContent = CSS; doc.head.appendChild(st);
    }
    const card = doc.createElement('div');
    card.className = 'voice-setting-card bp3-spatial-card';
    card.style.marginBottom = '12px';
    card.innerHTML = `
      <div class="voice-setting-card-title"><span>🎧 ตำแหน่งเสียงอ่าน</span></div>
      <div class="sp-body">
        <div class="sp-wrap">
          <span class="sp-lbl" style="left:50%;top:8px">หน้า</span><span class="sp-lbl" style="left:50%;bottom:-6px;top:auto">หลัง</span>
          <span class="sp-lbl" style="left:12px;top:50%">ซ้าย</span><span class="sp-lbl" style="left:calc(100% - 12px);top:50%">ขวา</span>
          <div class="sp-pad" tabindex="0" role="slider" aria-label="ตำแหน่งเสียงอ่านรอบตัวผู้ฟัง">
            <div class="sp-ring" style="inset:22%"></div><div class="sp-ring" style="inset:44%"></div>
            <div class="sp-axis" style="left:50%;top:6%;bottom:6%;width:1px"></div><div class="sp-axis" style="top:50%;left:6%;right:6%;height:1px"></div>
            ${HEAD_SVG}<div class="sp-dot">${SPEAKER_SVG}</div>
          </div>
        </div>
        <div class="sp-side">
          <div class="sp-readout"></div>
          <div class="sp-hint">ลากจุดไปวางรอบตัวคนตรงกลาง ยิ่งห่างจากหัวเสียงยิ่งไกล ซ้ายและขวาได้ยินทั้งลำโพงและหูฟัง ส่วนหน้าและหลังต้องใส่หูฟังจึงจะรู้สึก</div>
          <div class="sp-presets">${PRESETS.map(p => `<button type="button" class="sp-chip" data-preset="${p.id}">${p.label}</button>`).join('')}</div>
          <button type="button" class="btn-topbar-action sp-test"></button>
        </div>
      </div>`;
    const pad = card.querySelector('.sp-pad');
    const fromEvent = ev => {
      const r = pad.getBoundingClientRect();
      return { x: ((ev.clientX - r.left) / r.width) * 2 - 1, y: -(((ev.clientY - r.top) / r.height) * 2 - 1) };
    };
    let dragging = false;
    pad.addEventListener('pointerdown', ev => { dragging = true; try { pad.setPointerCapture(ev.pointerId); } catch (_) {} pad.focus(); setPosition(fromEvent(ev)); ev.preventDefault(); });
    pad.addEventListener('pointermove', ev => { if (dragging) setPosition(fromEvent(ev)); });
    const end = () => { dragging = false; };
    pad.addEventListener('pointerup', end); pad.addEventListener('pointercancel', end);
    pad.addEventListener('keydown', ev => {
      const step = ev.shiftKey ? 0.2 : 0.05, s = { ...state };
      if (ev.key === 'ArrowLeft') s.x -= step; else if (ev.key === 'ArrowRight') s.x += step;
      else if (ev.key === 'ArrowUp') s.y += step; else if (ev.key === 'ArrowDown') s.y -= step;
      else if (ev.key === 'Home') { s.x = 0; s.y = 0; } else return;   // (Escape is the app's close-window key)
      ev.preventDefault(); setPosition(s);
    });
    card.querySelectorAll('.sp-chip').forEach(b => b.addEventListener('click', () => { const p = PRESETS.find(q => q.id === b.dataset.preset); if (p) setPosition(p); }));
    card.querySelector('.sp-test').addEventListener('click', () => { playTest(); });
    cards.add({ doc, card });
    return card;
  }
  const testing = () => !!testAudio;
  function renderAll() {
    renderTopbar();
    for (const { card } of cards) {
      if (!card.isConnected) continue;
      const dot = card.querySelector('.sp-dot');
      dot.style.left = (50 + state.x * 45) + '%';
      dot.style.top = (50 - state.y * 45) + '%';
      dot.classList.toggle('center', isCenter());
      card.querySelector('.sp-readout').textContent = describe(state);
      card.querySelector('.sp-pad').setAttribute('aria-valuetext', describe(state));
      card.querySelectorAll('.sp-chip').forEach(b => {
        const p = PRESETS.find(q => q.id === b.dataset.preset);
        b.classList.toggle('active', !!p && (p.id === 'center' ? isCenter() : (!isCenter() && Math.abs(p.x - state.x) < 0.02 && Math.abs(p.y - state.y) < 0.02)));
      });
      const t = card.querySelector('.sp-test');
      const on = testing();
      t.textContent = on ? '⏹ หยุดทดสอบ' : '▶ ทดสอบฟังตำแหน่งนี้';
    }
  }
  // ---- Top bar: 3D on/off toggle ---------------------------------------------------------------
  const TOPBAR_CSS = `
.topbar-rvc-badge.tts3d-badge{font-family:inherit}
.topbar-rvc-badge.tts3d-badge .tts3d-icon{display:inline-flex}
.topbar-rvc-badge.tts3d-badge .tts3d-icon svg{width:14px;height:14px}
.topbar-rvc-badge.tts3d-badge.tts3d-off{opacity:.6;border-color:rgba(255,255,255,.08);color:#64748b}
.topbar-rvc-badge.tts3d-badge.tts3d-off:hover{opacity:.9;color:#94a3b8}
.topbar-rvc-badge.tts3d-badge.tts3d-on{background:rgba(124,58,237,.16);border-color:rgba(167,139,250,.55);color:#c4b5fd}
.topbar-rvc-badge.tts3d-badge.tts3d-on:hover{background:rgba(124,58,237,.24)}
`;
  const HEADPHONES_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>';
  let topbarBtn = null;
  function mountTopbar() {
    if (topbarBtn && topbarBtn.isConnected) return;
    const anchor = document.getElementById('topbarRvcBadge') || document.querySelector('.topbar-gender-switch');
    if (!anchor || !anchor.parentElement) return;
    if (!document.getElementById('bp3-tts3d-style')) {
      const st = document.createElement('style'); st.id = 'bp3-tts3d-style'; st.textContent = TOPBAR_CSS; document.head.appendChild(st);
    }
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'topbarTts3dToggle';
    btn.className = 'topbar-rvc-badge tts3d-badge tts3d-off';
    btn.innerHTML = '<span class="tts3d-icon">' + HEADPHONES_SVG + '</span><span class="tts3d-text">3D</span>';
    btn.addEventListener('click', () => setOn(isCenter()));
    btn.addEventListener('contextmenu', ev => { ev.preventDefault(); if (window.openToolWindow) window.openToolWindow('voice-settings'); });
    anchor.after(btn);
    topbarBtn = btn;
  }
  function renderTopbar() {
    if (!topbarBtn || !topbarBtn.isConnected) return;
    const on = !isCenter();
    topbarBtn.classList.toggle('tts3d-on', on);
    topbarBtn.classList.toggle('tts3d-off', !on);
    topbarBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    topbarBtn.querySelector('.tts3d-text').textContent = on ? '3D ' + direction(state) : '3D';
    topbarBtn.title = on
      ? 'เสียงอ่าน 3 มิติ: ' + describe(state) + '\nคลิกเพื่อกลับเป็นเสียงอ่านปกติ • คลิกขวาเพื่อตั้งตำแหน่งเสียง'
      : 'เสียงอ่านปกติ\nคลิกเพื่อเปิดเสียงอ่าน 3 มิติ • คลิกขวาเพื่อตั้งตำแหน่งเสียง';
  }

  function mount() {
    mountTopbar();
    // Put the card right after the "Volume, Speed & Pitch" card in Voice Settings and Settings > TTS.
    const titles = Array.from(document.querySelectorAll('.voice-setting-card-title > span')).filter(s => /Volume, Speed/.test(s.textContent));
    for (const span of titles) {
      const host = span.closest('.voice-setting-card');
      if (!host || host.nextElementSibling?.classList?.contains('bp3-spatial-card')) continue;
      host.after(buildCard(document));
    }
    renderAll();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, { once: true }); else mount();
})();
