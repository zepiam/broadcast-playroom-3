/* Legacy Giveaway presentation and draw animation from the reference project. */
(() => {
'use strict';
function esc(v){return String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
let _giveawayState = null;
let _gwIsAnimatingOut = false;
let _giveawayConfig = {
  overlay_display_mode: 'banner',
  overlay_has_image: false,
  overlay_position: 'right',
  overlay_offset_x: 0,
  overlay_offset_y: 0,
  overlay_scale: 100,
  overlay_anim_in: 'slide',
  overlay_anim_out: 'slide',
  overlay_show_countdown_border: true,
  overlay_show_toast: true,
  overlay_show_stats: true,
  sound_enabled: false,
  draw_autohide_sec: 15
};

let _gwAudioCtx = null;
function _getGwAudioCtx() {
  if (!_gwAudioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) _gwAudioCtx = new AudioContext();
  }
  if (_gwAudioCtx && _gwAudioCtx.state === 'suspended') {
    _gwAudioCtx.resume();
  }
  return _gwAudioCtx;
}

function playGwTickSound() {
  if (_giveawayConfig.sound_enabled === false) return;
  try {
    const ctx = _getGwAudioCtx();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(580 + Math.random() * 80, ctx.currentTime);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.05);
  } catch(e) {}
}

function playGwDropSound() {
  if (_giveawayConfig.sound_enabled === false) return;
  try {
    const ctx = _getGwAudioCtx();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(240, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(70, ctx.currentTime + 0.12);
    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.12);
  } catch(e) {}
}

function playGwRattleSound() {
  if (_giveawayConfig.sound_enabled === false) return;
  try {
    const ctx = _getGwAudioCtx();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(620 + Math.random() * 80, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(320, ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.04);
  } catch(e) {}
}

function playGwChargeTickSound(pitchMult = 1) {
  if (_giveawayConfig.sound_enabled === false) return;
  try {
    const ctx = _getGwAudioCtx();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    const baseFreq = 480 * pitchMult;
    osc.frequency.setValueAtTime(baseFreq, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.35, ctx.currentTime + 0.035);
    gain.gain.setValueAtTime(0.07, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.035);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.035);
  } catch(e) {}
}

function playGwPopSound() {
  if (_giveawayConfig.sound_enabled === false) return;
  try {
    const ctx = _getGwAudioCtx();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(950, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(140, ctx.currentTime + 0.09);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.09);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.09);
  } catch(e) {}
}

function playGwFanfareSound() {
  if (_giveawayConfig.sound_enabled === false) return;
  try {
    const ctx = _getGwAudioCtx();
    if (!ctx) return;
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const startTime = ctx.currentTime + idx * 0.12;
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, startTime);
      gain.gain.setValueAtTime(0.12, startTime);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.6);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(startTime);
      osc.stop(startTime + 0.6);
    });
  } catch(e) {}
}

let _gwConfettiAnimId = null;
function triggerGwConfetti(canvas) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  canvas.style.display = 'block';

  let particles = [];
  const colors = ['#fbbf24', '#38bdf8', '#34d399', '#f472b6', '#a78bfa', '#f87171'];
  for (let i = 0; i < 70; i++) {
    particles.push({
      x: canvas.width / 2 + (Math.random() * 200 - 100),
      y: canvas.height / 2,
      vx: (Math.random() - 0.5) * 16,
      vy: Math.random() * -14 - 4,
      size: Math.random() * 8 + 5,
      color: colors[Math.floor(Math.random() * colors.length)],
      rotation: Math.random() * 360,
      vRot: (Math.random() - 0.5) * 10,
      alpha: 1
    });
  }

  const startTime = performance.now();
  if (_gwConfettiAnimId) cancelAnimationFrame(_gwConfettiAnimId);

  function loop(now) {
    const elapsed = now - startTime;
    if (elapsed > 3500) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      canvas.style.display = 'none';
      _gwConfettiAnimId = null;
      return;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const fade = Math.max(0, 1 - (elapsed - 2000) / 1500);

    for (let p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.38;
      p.vx *= 0.98;
      p.rotation += p.vRot;

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rotation * Math.PI / 180);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha * fade;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      ctx.restore();
    }

    _gwConfettiAnimId = requestAnimationFrame(loop);
  }
  _gwConfettiAnimId = requestAnimationFrame(loop);
}

let _gwCpTotalDuration = 0;
let _gwCpDismissTimer = null;
let _gwCpHideTimer = null;
let _gwToastTimer = null;
let _gwSlotRollInterval = null;
let _gwSlotReelSpinInterval = null;
let _gwSlotReelDecelTimers = [];
let _gwCandidatesPool = [];
let _gwDrawWinner = '';
let _gwIsDrawRunning = false;
let _gwDrawAutoHideTimer = null;

function scheduleDrawAutoHide(inner) {
  if (_gwDrawAutoHideTimer) {
    clearTimeout(_gwDrawAutoHideTimer);
    _gwDrawAutoHideTimer = null;
  }
  const autoHideSec = _giveawayConfig.draw_autohide_sec !== undefined ? Number(_giveawayConfig.draw_autohide_sec) : 15;
  if (autoHideSec <= 0) return;

  _gwDrawAutoHideTimer = setTimeout(() => {
    const drawBox = inner.querySelector('.giveaway-draw-box');
    if (drawBox && drawBox.classList.contains('visible')) {
      drawBox.classList.add('fadeout');
      setTimeout(() => {
        drawBox.classList.remove('visible', 'winner', 'style-gachapon', 'fadeout');
        const gachaStage = inner.querySelector('.giveaway-gacha-stage');
        if (gachaStage) gachaStage.classList.remove('shaking', 'revealed', 'gacha-entering', 'gacha-wobble', 'gacha-charging');
        const strip = inner.querySelector('.giveaway-slot-strip');
        if (strip) {
          strip.classList.remove('spinning');
          strip.style.transition = 'none';
          strip.style.transform = 'translateY(0px)';
          strip.innerHTML = '';
        }
        inner.classList.add('giveaway-idle');
      }, 450);
    }
  }, autoHideSec * 1000);
}

function startSmoothReelDraw(inner, winnerName, pool) {
  const drawBox = inner.querySelector('.giveaway-draw-box');
  const strip = inner.querySelector('.giveaway-slot-strip');
  const drawStatus = inner.querySelector('.giveaway-draw-status-label');
  const confettiCanvas = inner.querySelector('.giveaway-confetti-canvas');
  if (!strip) return;

  _gwSlotReelDecelTimers.forEach(t => clearTimeout(t));
  _gwSlotReelDecelTimers = [];
  if (_gwSlotReelSpinInterval) { clearInterval(_gwSlotReelSpinInterval); _gwSlotReelSpinInterval = null; }

  // Clean candidate pool
  const cleanPool = (pool && pool.length > 0) ? pool.filter(n => Boolean(n)) : ['ผู้เข้าร่วมกิจกรรม'];
  const others = cleanPool.filter(n => n !== winnerName);
  const fallbackList = others.length > 0 ? others : cleanPool;

  // สร้างรายชื่อสลับกัน 32 ช่อง โดยชื่อผู้ชนะจะอยู่ตำแหน่งสุดท้ายอย่างสมบูรณ์แบบ
  const totalItems = 32;
  const reelItems = [];
  let lastPick = '';
  for (let i = 0; i < totalItems - 1; i++) {
    let pick = fallbackList[Math.floor(Math.random() * fallbackList.length)];
    if (fallbackList.length > 1 && pick === lastPick) {
      pick = fallbackList[(fallbackList.indexOf(pick) + 1) % fallbackList.length];
    }
    reelItems.push(pick);
    lastPick = pick;
  }
  reelItems.push(winnerName);

  strip.classList.remove('spinning');
  strip.style.transition = 'none';
  strip.style.transform = 'translateY(0px)';
  strip.innerHTML = reelItems.map((name, idx) => {
    const isTarget = (idx === reelItems.length - 1);
    return `<div class="slot-reel-item ${isTarget ? 'target-winner' : ''}"><span class="slot-reel-item-text">${name}</span></div>`;
  }).join('');

  const itemHeight = 130;
  const targetOffset = -((reelItems.length - 1) * itemHeight);

  void strip.offsetHeight; // Force reflow

  const durationMs = 3500;
  strip.style.transition = `transform ${durationMs}ms cubic-bezier(0.12, 0.88, 0.18, 1)`;
  strip.style.transform = `translateY(${targetOffset}px)`;

  // จังหวะเสียงหมุนที่ค่อยๆ ชะลอช้าลงตามการเคลื่อนที่ของตู้สล็อต
  const tickIntervals = [
    40, 75, 115, 160, 210, 265, 325, 390, 465, 545, 635, 735,
    845, 970, 1110, 1265, 1440, 1635, 1855, 2100, 2380, 2690, 3040, 3380
  ];
  tickIntervals.forEach(delay => {
    if (delay < durationMs - 40) {
      const timer = setTimeout(() => playGwTickSound(), delay);
      _gwSlotReelDecelTimers.push(timer);
    }
  });

  const landTimer = setTimeout(() => {
    if (drawBox) drawBox.classList.add('winner');
    const targetEl = strip.querySelector('.target-winner');
    if (targetEl) targetEl.classList.add('winner-item');
    if (drawStatus) drawStatus.textContent = '🎉 ขอแสดงความยินดีกับผู้โชคดี! 🎉';
    playGwFanfareSound();
    triggerGwConfetti(confettiCanvas);
    scheduleDrawAutoHide(inner);
  }, durationMs + 20);
  _gwSlotReelDecelTimers.push(landTimer);
}

function startSmoothShuffleDraw(inner, winnerName, pool) {
  const drawBox = inner.querySelector('.giveaway-draw-box');
  const slotName = inner.querySelector('.giveaway-slot-reel-name');
  const drawStatus = inner.querySelector('.giveaway-draw-status-label');
  const confettiCanvas = inner.querySelector('.giveaway-confetti-canvas');
  if (!slotName) return;

  _gwSlotReelDecelTimers.forEach(t => clearTimeout(t));
  _gwSlotReelDecelTimers = [];
  if (_gwSlotRollInterval) { clearInterval(_gwSlotRollInterval); _gwSlotRollInterval = null; }

  const cleanPool = (pool && pool.length > 0) ? pool.filter(n => Boolean(n)) : ['ผู้เข้าร่วมกิจกรรม'];
  const others = cleanPool.filter(n => n !== winnerName);
  const fallbackList = others.length > 0 ? others : cleanPool;

  slotName.classList.add('rolling');
  if (drawBox) drawBox.classList.remove('winner');
  if (drawStatus) drawStatus.textContent = '⚡ กำลังสลับรายชื่อ...';

  // ช่วงสับชื่อเร็วรัวๆ 42 ครั้ง (35ms) ให้ดูตื่นเต้น เร้าใจ
  const delays = [];
  for (let i = 0; i < 42; i++) {
    delays.push(35);
  }
  // ช่วงค่อยๆ ชะลอความเร็ว (Deceleration Curve) ให้ลุ้นระทึก รวม ~5.7 วินาที (+2 วินาที)
  const decelSteps = [60, 60, 60, 60, 100, 100, 100, 100, 160, 160, 160, 280, 280, 280, 450, 450, 650];
  decelSteps.forEach(d => delays.push(d));

  // จังหวะสุดท้าย: หน่วงเวลา 750ms จากชื่อก่อนหน้า แล้วลงที่ชื่อผู้ชนะตัวจริงทันที
  delays.push(750);

  let acc = 0;
  let lastDummy = '';
  const totalSteps = delays.length;

  delays.forEach((delay, idx) => {
    acc += delay;
    const isFinalStep = (idx === totalSteps - 1);

    const t = setTimeout(() => {
      if (isFinalStep) {
        // ลงที่ชื่อผู้ชนะตัวจริงทันที ไม่หยุดที่ชื่อคนอื่นก่อน
        slotName.classList.remove('rolling');
        slotName.textContent = winnerName;
        if (drawBox) drawBox.classList.add('winner');
        if (drawStatus) drawStatus.textContent = '🎉 ขอแสดงความยินดีกับผู้โชคดี! 🎉';
        playGwFanfareSound();
        triggerGwConfetti(confettiCanvas);
        scheduleDrawAutoHide(inner);
      } else {
        let dummy = fallbackList[Math.floor(Math.random() * fallbackList.length)];
        if (fallbackList.length > 1 && dummy === lastDummy) {
          dummy = fallbackList[(fallbackList.indexOf(dummy) + 1) % fallbackList.length];
        }
        lastDummy = dummy;
        slotName.textContent = dummy;
        playGwTickSound();
      }
    }, acc);

    _gwSlotReelDecelTimers.push(t);
  });
}

function startGachaponDraw(inner, winnerName, prizeName) {
  const drawBox = inner.querySelector('.giveaway-draw-box');
  const gachaStage = inner.querySelector('.giveaway-gacha-stage');
  const gachaWinnerName = inner.querySelector('.gacha-winner-name');
  const gachaPrizeText = inner.querySelector('.gacha-prize-text');
  const confettiCanvas = inner.querySelector('.giveaway-confetti-canvas');

  _gwSlotReelDecelTimers.forEach(t => clearTimeout(t));
  _gwSlotReelDecelTimers = [];

  if (!gachaStage) return;

  // รีเซ็ตสถานะและคลาสก่อนหน้าให้พร้อมสำหรับรอบใหม่
  gachaStage.classList.remove('revealed', 'shaking', 'gacha-entering', 'gacha-wobble', 'gacha-charging');
  if (drawBox) drawBox.classList.remove('winner');
  if (gachaPrizeText) {gachaPrizeText.textContent='';gachaPrizeText.style.display='none';}
  if (gachaWinnerName) gachaWinnerName.textContent = '...';

  // ── Phase 1: ลูกบอลหล่นลงมาจากด้านบนพร้อมเด้งดึ๋งนุ่มนวล (0 - 450ms) ──
  gachaStage.classList.add('gacha-entering');
  playGwDropSound();

  // ── Phase 2: แกว่งส่ายแบบลูกตุ้มต่อเนื่อง ไร้รอยต่อ 100% (450ms - 2100ms) ──
  const t1 = setTimeout(() => {
    gachaStage.classList.remove('gacha-entering');
    gachaStage.classList.add('gacha-wobble');

    // เสียงเคาะคลิกเบาๆ ตามจังหวะการเอียงของลูกบอล
    const wobbleTicks = [180, 480, 800, 1120, 1420];
    wobbleTicks.forEach(dt => {
      const wt = setTimeout(() => {
        playGwRattleSound();
      }, dt);
      _gwSlotReelDecelTimers.push(wt);
    });
  }, 450);
  _gwSlotReelDecelTimers.push(t1);

  // ── Phase 3: ชาร์จพลังงาน สั่นสะเทือนเร็วขึ้นเรื่อยๆ และขยายขนาดต่อเนื่อง (2100ms - 3400ms) ──
  const t2 = setTimeout(() => {
    gachaStage.classList.remove('gacha-wobble');
    gachaStage.classList.add('gacha-charging');

    // เสียงชาร์จพลังงานถี่รัวขึ้นพร้อมระดับเสียงที่สูงขึ้น
    const chargeSchedule = [
      { t: 0, mult: 1.0 },
      { t: 180, mult: 1.1 },
      { t: 340, mult: 1.2 },
      { t: 480, mult: 1.3 },
      { t: 600, mult: 1.4 },
      { t: 710, mult: 1.5 },
      { t: 810, mult: 1.6 },
      { t: 900, mult: 1.7 },
      { t: 980, mult: 1.8 },
      { t: 1050, mult: 1.9 },
      { t: 1120, mult: 2.0 },
      { t: 1180, mult: 2.1 },
      { t: 1240, mult: 2.2 }
    ];
    chargeSchedule.forEach(item => {
      const ct = setTimeout(() => {
        playGwChargeTickSound(item.mult);
      }, item.t);
      _gwSlotReelDecelTimers.push(ct);
    });
  }, 2100);
  _gwSlotReelDecelTimers.push(t2);

  // ── Phase 4: POP! ลูกบอลระเบิดเปิดออก ฝาแยก แสงช็อคเวฟ และผู้ชนะพุ่งออกมา (3400ms) ──
  const t3 = setTimeout(() => {
    if (drawBox) drawBox.classList.add('winner');
    gachaStage.classList.remove('gacha-charging', 'shaking');
    gachaStage.classList.add('revealed');
    if (gachaWinnerName) gachaWinnerName.textContent = winnerName;
    if (gachaPrizeText) {gachaPrizeText.textContent='';gachaPrizeText.style.display='none';}

    playGwPopSound();
    playGwFanfareSound();
    triggerGwConfetti(confettiCanvas);
    scheduleDrawAutoHide(inner);
  }, 3400);
  _gwSlotReelDecelTimers.push(t3);
}

function applyGiveawayConfigToInner(inner, cfg) {
  if (!inner) return;
  if (cfg) Object.assign(_giveawayConfig, cfg);
  const c = _giveawayConfig;
  const cpBox = inner.querySelector('.giveaway-cp-box');
  const imgBox = inner.querySelector('.giveaway-image-box');
  const allBoxes = [cpBox, imgBox].filter(Boolean);
  const allCountdownSvgs = inner.querySelectorAll('.giveaway-countdown-svg');
  const imgStatsBar = inner.querySelector('.giveaway-img-stats-bar');
  const customImg = inner.querySelector('.giveaway-custom-img');

  const pos = c.overlay_position || 'top-right';
  const posClasses = [
    'pos-top-right', 'pos-top-left', 'pos-bottom-right', 'pos-bottom-left',
    'pos-top', 'pos-bottom', 'pos-left', 'pos-right', 'pos-center'
  ];
  const fontScale = (c.overlay_font_size || 100) / 100;
  allBoxes.forEach(box => {
    posClasses.forEach(p => box.classList.remove(p));
    box.classList.add(`pos-${pos}`);
    box.style.setProperty('--offset-x', (c.overlay_offset_x || 0) + 'px');
    box.style.setProperty('--offset-y', (c.overlay_offset_y || 0) + 'px');
    box.style.setProperty('--scale', ((c.overlay_scale || 100) / 100));
    box.style.setProperty('--font-scale', fontScale);
  });

  if (cpBox) {
    const codeEl = cpBox.querySelector('.giveaway-cp-code');
    if (codeEl) codeEl.style.fontSize = Math.round(26 * fontScale) + 'px';
    const instEl = cpBox.querySelector('.giveaway-cp-instruction');
    if (instEl) instEl.style.fontSize = Math.round(13 * fontScale) + 'px';
    const titleEl = cpBox.querySelector('.giveaway-cp-badge');
    if (titleEl) titleEl.style.fontSize = Math.round(13 * fontScale) + 'px';
    const timerEl = cpBox.querySelector('.giveaway-cp-timer');
    if (timerEl) timerEl.style.fontSize = Math.round(12.5 * fontScale) + 'px';
    const countEl = cpBox.querySelector('.giveaway-cp-count');
    if (countEl) countEl.style.fontSize = Math.round(11.5 * fontScale) + 'px';
  }
  if (imgBox) {
    const timerEl = imgBox.querySelector('.giveaway-img-timer-text');
    if (timerEl) timerEl.style.fontSize = Math.round(12 * fontScale) + 'px';
    const countEl = imgBox.querySelector('.giveaway-img-count-text');
    if (countEl) countEl.style.fontSize = Math.round(12 * fontScale) + 'px';
  }

  // Real-time display mode toggle during preview/active (ignore if currently animating out)
  if (!_gwIsAnimatingOut) {
    const isCpVis = cpBox && cpBox.classList.contains('visible');
    const isImgVis = imgBox && imgBox.classList.contains('visible');
    if (isCpVis || isImgVis) {
      if (c.overlay_display_mode === 'none') {
        if (cpBox) { cpBox.style.display = 'none'; cpBox.classList.remove('visible'); }
        if (imgBox) { imgBox.style.display = 'none'; imgBox.classList.remove('visible'); }
      } else if (c.overlay_display_mode === 'image' && c.overlay_has_image) {
        if (cpBox) { cpBox.style.display = 'none'; cpBox.classList.remove('visible'); }
        if (imgBox) { imgBox.style.display = 'block'; imgBox.classList.add('visible'); }
      } else {
        if (imgBox) { imgBox.style.display = 'none'; imgBox.classList.remove('visible'); }
        if (cpBox) { cpBox.style.display = 'block'; cpBox.classList.add('visible'); }
      }
    }
  }

  const borderTheme = c.overlay_border_theme || 'rainbow';
  const themes = ['rainbow', 'cyberpunk', 'gold', 'ice', 'sakura', 'emerald', 'ruby', 'violet', 'blue'];

  if (allCountdownSvgs.length) {
    const showBorder = (c.overlay_show_countdown_border !== false);
    allCountdownSvgs.forEach(svg => {
      svg.style.display = showBorder ? 'block' : 'none';
      themes.forEach(t => svg.classList.remove(`border-theme-${t}`));
      svg.classList.add(`border-theme-${borderTheme}`);
    });
  }

  // Progress bar display & theme for both standard card and image mode
  const showProgressBar = (c.overlay_show_progress_bar !== false);
  const cpTrack = inner.querySelector('.giveaway-progress-track');
  if (cpTrack) cpTrack.style.display = showProgressBar ? 'block' : 'none';
  const imgTrack = inner.querySelector('.giveaway-img-progress-track');
  if (imgTrack) imgTrack.style.display = showProgressBar ? 'block' : 'none';

  allBoxes.forEach(box => {
    themes.forEach(t => box.classList.remove(`progress-theme-${t}`));
    box.classList.add(`progress-theme-${borderTheme}`);
  });

  if (imgStatsBar) {
    imgStatsBar.style.display = (c.overlay_show_stats !== false) ? 'flex' : 'none';
  }
  if (customImg && c.overlay_display_mode === 'image' && c.overlay_has_image) {
    const imageUrl=c.overlay_image_url || '/giveaway/image';
    if(customImg.getAttribute('src')!==imageUrl)customImg.src=imageUrl;
  }

  const drawBox = inner.querySelector('.giveaway-draw-box');
  if (drawBox) {
    const scale = (c.draw_scale !== undefined ? c.draw_scale : 100) / 100;
    const ox = c.draw_offset_x || 0;
    const oy = c.draw_offset_y || 0;
    const style = c.draw_animation_style || 'gachapon';
    let nameSize = c.draw_name_size || 52;
    if (style === 'slot' || style === 'slot_reel') {
      nameSize = Math.min(nameSize, 50);
    }
    const prizeSize = c.draw_prize_size || 20;

    drawBox.style.setProperty('--draw-scale', scale);
    drawBox.style.setProperty('--draw-offset-x', ox + 'px');
    drawBox.style.setProperty('--draw-offset-y', oy + 'px');
    drawBox.style.setProperty('--winner-name-size', nameSize + 'px');
    drawBox.style.setProperty('--prize-text-size', prizeSize + 'px');

    if (style === 'gachapon') {
      drawBox.classList.add('style-gachapon');
    } else {
      drawBox.classList.remove('style-gachapon');
    }

    // Theme class synchronization
    const theme = c.draw_theme || 'gold';
    const themeClasses = ['gw-theme-gold', 'gw-theme-cyberpunk', 'gw-theme-violet', 'gw-theme-emerald', 'gw-theme-sakura', 'gw-theme-ice', 'gw-theme-ruby'];
    themeClasses.forEach(cls => drawBox.classList.remove(cls));
    drawBox.classList.add(`gw-theme-${theme}`);

    // Update SVG sunburst gradient colors
    const sunburstStops = {
      gold: ['#fbbf24', '#ea580c', '#7c2d12'],
      cyberpunk: ['#22d3ee', '#d946ef', '#4a044e'],
      violet: ['#c084fc', '#7c3aed', '#31104b'],
      emerald: ['#34d399', '#059669', '#022c22'],
      sakura: ['#f472b6', '#db2777', '#500724'],
      ice: ['#38bdf8', '#0284c7', '#082f49'],
      ruby: ['#fb7185', '#e11d48', '#4c0519']
    };
    const sCols = sunburstStops[theme] || sunburstStops.gold;
    const grad = inner.querySelector('#gwSunburstGrad');
    if (grad) {
      const stops = grad.querySelectorAll('stop');
      if (stops.length >= 3) {
        stops[0].setAttribute('stop-color', sCols[0]);
        stops[1].setAttribute('stop-color', sCols[1]);
        stops[2].setAttribute('stop-color', sCols[2]);
      }
    }
  }
}

function renderGiveawayInto(inner) {
  if (!inner) return;
  if (!inner.querySelector('.giveaway-cp-box')) {
    inner.innerHTML = `
      <!-- CHECKPOINT BANNER (STANDARD TEXT) -->
      <div class="giveaway-cp-box">
        <svg class="giveaway-countdown-svg border-theme-rainbow cp-countdown-svg">
          <defs>
            <linearGradient id="gwBorderGradRainbow" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#ff0055" />
              <stop offset="20%" stop-color="#ff7700" />
              <stop offset="40%" stop-color="#ffdd00" />
              <stop offset="60%" stop-color="#00ff88" />
              <stop offset="80%" stop-color="#00ddff" />
              <stop offset="100%" stop-color="#aa00ff" />
            </linearGradient>
            <linearGradient id="gwBorderGradCyberpunk" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#22d3ee" />
              <stop offset="100%" stop-color="#d946ef" />
            </linearGradient>
            <linearGradient id="gwBorderGradGold" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#fde047" />
              <stop offset="100%" stop-color="#ea580c" />
            </linearGradient>
            <linearGradient id="gwBorderGradIce" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#a5f3fc" />
              <stop offset="100%" stop-color="#0284c7" />
            </linearGradient>
            <linearGradient id="gwBorderGradSakura" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#fbcfe8" />
              <stop offset="100%" stop-color="#db2777" />
            </linearGradient>
            <linearGradient id="gwBorderGradEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6ee7b7" />
              <stop offset="100%" stop-color="#059669" />
            </linearGradient>
            <linearGradient id="gwBorderGradRuby" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#fda4af" />
              <stop offset="100%" stop-color="#e11d48" />
            </linearGradient>
            <linearGradient id="gwBorderGradViolet" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#d8b4fe" />
              <stop offset="100%" stop-color="#7c3aed" />
            </linearGradient>
            <linearGradient id="gwBorderGradBlue" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#93c5fd" />
              <stop offset="100%" stop-color="#2563eb" />
            </linearGradient>
          </defs>
          <rect class="giveaway-countdown-rect" x="2" y="2" width="calc(100% - 4px)" height="calc(100% - 4px)" rx="14" ry="14"
                fill="none" pathLength="100" />
        </svg>
        <div class="giveaway-cp-header">
          <span class="giveaway-cp-badge">🎁 กิจกรรมเช็คชื่อลุ้นรางวัล</span>
          <span class="giveaway-cp-status-pill">กำลังเปิดรับ</span>
        </div>
        <div class="giveaway-cp-code-row">
          <div class="giveaway-cp-instruction">พิมพ์คำสั่งนี้ในแชทเพื่อรับสิทธิ์:</div>
          <div class="giveaway-cp-code">#join</div>
        </div>
        <div class="giveaway-progress-track">
          <div class="giveaway-progress-fill"></div>
        </div>
        <div class="giveaway-cp-footer">
          <span class="giveaway-cp-timer">⏱️ เวลา: 01:00</span>
          <span class="giveaway-cp-count">👥 ผู้เข้าร่วม: 0 คน</span>
        </div>
        <div class="giveaway-cp-toast"></div>
      </div>

      <!-- CUSTOM IMAGE BANNER -->
      <div class="giveaway-image-box">
        <div class="giveaway-image-card-wrapper">
          <svg class="giveaway-countdown-svg border-theme-rainbow">
            <defs>
              <linearGradient id="gwBorderGradRainbow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ff0055" />
                <stop offset="20%" stop-color="#ff7700" />
                <stop offset="40%" stop-color="#ffdd00" />
                <stop offset="60%" stop-color="#00ff88" />
                <stop offset="80%" stop-color="#00ddff" />
                <stop offset="100%" stop-color="#aa00ff" />
              </linearGradient>
              <linearGradient id="gwBorderGradCyberpunk" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#22d3ee" />
                <stop offset="100%" stop-color="#d946ef" />
              </linearGradient>
              <linearGradient id="gwBorderGradGold" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#fde047" />
                <stop offset="100%" stop-color="#ea580c" />
              </linearGradient>
              <linearGradient id="gwBorderGradIce" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#a5f3fc" />
                <stop offset="100%" stop-color="#0284c7" />
              </linearGradient>
              <linearGradient id="gwBorderGradSakura" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#fbcfe8" />
                <stop offset="100%" stop-color="#db2777" />
              </linearGradient>
              <linearGradient id="gwBorderGradEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#6ee7b7" />
                <stop offset="100%" stop-color="#059669" />
              </linearGradient>
              <linearGradient id="gwBorderGradRuby" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#fda4af" />
                <stop offset="100%" stop-color="#e11d48" />
              </linearGradient>
              <linearGradient id="gwBorderGradViolet" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#d8b4fe" />
                <stop offset="100%" stop-color="#7c3aed" />
              </linearGradient>
              <linearGradient id="gwBorderGradBlue" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#93c5fd" />
                <stop offset="100%" stop-color="#2563eb" />
              </linearGradient>
            </defs>
            <rect class="giveaway-countdown-rect" x="2" y="2" width="calc(100% - 4px)" height="calc(100% - 4px)" rx="18" ry="18"
                  fill="none" pathLength="100" />
          </svg>
          <img class="giveaway-custom-img" src="" alt="Giveaway Banner" />
          <div class="giveaway-img-progress-track">
            <div class="giveaway-img-progress-fill"></div>
          </div>
          <div class="giveaway-img-stats-bar">
            <span class="giveaway-img-timer-text" style="color:#e2e8f0;">⏱️ 01:00</span>
            <span class="giveaway-img-count-text" style="color:#34d399;">👥 0 คน</span>
          </div>
        </div>
      </div>

      <!-- SLOT MACHINE / GACHAPON LUCKY DRAW STAGE -->
      <div class="giveaway-draw-box style-gachapon">
        <!-- SLOT STAGE (Reel Strip / Classic Shuffle) -->
        <div class="giveaway-slot-stage">
          <div class="giveaway-draw-header-title">✨ ผลการสุ่มผู้โชคดี ✨</div>
          <div class="giveaway-slot-reel-box">
            <div class="giveaway-slot-reel-vignette"></div>
            <div class="giveaway-slot-reel-guides"></div>
            <div class="giveaway-slot-reel-name">...</div>
            <div class="giveaway-slot-strip-container">
              <div class="giveaway-slot-strip"></div>
            </div>
          </div>
          <div class="giveaway-draw-status-label">เตรียมพร้อมสุ่มผู้โชคดี...</div>
        </div>

        <!-- GACHAPON STAGE (Takayu Studio Style) -->
        <div class="giveaway-gacha-stage">
          <svg class="gacha-sunburst" viewBox="0 0 600 600">
            <defs>
              <radialGradient id="gwSunburstGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.9" />
                <stop offset="50%" stop-color="#ea580c" stop-opacity="0.45" />
                <stop offset="100%" stop-color="#7c2d12" stop-opacity="0" />
              </radialGradient>
            </defs>
            <g fill="url(#gwSunburstGrad)">
              <polygon points="300,300 280,0 320,0" />
              <polygon points="300,300 375,12 408,36" />
              <polygon points="300,300 460,55 487,93" />
              <polygon points="300,300 525,130 545,172" />
              <polygon points="300,300 565,220 575,265" />
              <polygon points="300,300 580,315 570,360" />
              <polygon points="300,300 545,410 525,450" />
              <polygon points="300,300 490,490 460,525" />
              <polygon points="300,300 410,550 375,575" />
              <polygon points="300,300 320,585 280,585" />
              <polygon points="300,300 225,575 190,550" />
              <polygon points="300,300 140,525 110,490" />
              <polygon points="300,300 75,450 55,410" />
              <polygon points="300,300 30,360 20,315" />
              <polygon points="300,300 25,265 35,220" />
              <polygon points="300,300 55,172 75,130" />
              <polygon points="300,300 110,93 140,55" />
              <polygon points="300,300 190,36 225,12" />
            </g>
          </svg>
          <div class="gacha-aura"></div>
          <div class="gacha-burst-ring"></div>
          <div class="gacha-capsule-wrap">
            <div class="gacha-cap-top"></div>
            <div class="gacha-cap-belt"></div>
            <div class="gacha-cap-bottom"></div>
          </div>
          <div class="gacha-result">
            <div class="gacha-winner-badge">🎉 ขอแสดงความยินดีกับผู้โชคดี! 🎉</div>
            <div class="gacha-winner-name">...</div>
          </div>
        </div>
      </div>

      <canvas class="giveaway-confetti-canvas"></canvas>
    `;
    inner.classList.add('giveaway-idle');
  }

  applyGiveawayConfigToInner(inner, _giveawayConfig);
  if (_giveawayState) {
    handleGiveawayEvent({ type: 'giveaway_state', state: _giveawayState });
  }
}

function handleGiveawayEvent(data) {
  if (!data) return;
  const evtType = data.type;

  if (data.state) {
    _giveawayState = data.state;
    Object.assign(_giveawayConfig, data.state);
  }

  const widgets = document.querySelectorAll('.widget.type-giveaway .widget-inner');
  if (!widgets.length) return;

  widgets.forEach(inner => {
    applyGiveawayConfigToInner(inner, _giveawayConfig);

    const cpBox = inner.querySelector('.giveaway-cp-box');
    const cpCountdownRect = inner.querySelector('.giveaway-cp-box .giveaway-countdown-rect');
    const cpBadge = inner.querySelector('.giveaway-cp-badge');
    const cpStatus = inner.querySelector('.giveaway-cp-status-pill');
    const cpCode = inner.querySelector('.giveaway-cp-code');
    const cpFill = inner.querySelector('.giveaway-progress-fill');
    const cpTimer = inner.querySelector('.giveaway-cp-timer');
    const cpCount = inner.querySelector('.giveaway-cp-count');
    const cpToast = inner.querySelector('.giveaway-cp-toast');

    const imgBox = inner.querySelector('.giveaway-image-box');
    const imgCountdownRect = inner.querySelector('.giveaway-image-box .giveaway-countdown-rect');
    const imgTimerText = inner.querySelector('.giveaway-img-timer-text');
    const imgCountText = inner.querySelector('.giveaway-img-count-text');

    const drawBox = inner.querySelector('.giveaway-draw-box');
    const drawPrize = inner.querySelector('.giveaway-draw-prize-text');
    const drawTier = inner.querySelector('.giveaway-draw-tier-pill');
    const slotName = inner.querySelector('.giveaway-slot-reel-name');
    const drawStatus = inner.querySelector('.giveaway-draw-status-label');
    const confettiCanvas = inner.querySelector('.giveaway-confetti-canvas');

    const imgFill = inner.querySelector('.giveaway-img-progress-fill');

    function resolveFlyInClass(animIn, pos) {
      if (!animIn || animIn === 'slide') {
        if (pos === 'top-right' || pos === 'bottom-right' || pos === 'right') return 'anim-in-from-right';
        if (pos === 'top-left' || pos === 'bottom-left' || pos === 'left') return 'anim-in-from-left';
        if (pos === 'top') return 'anim-in-from-top';
        if (pos === 'bottom') return 'anim-in-from-bottom';
        return 'anim-in-from-top';
      }
      if (animIn.startsWith('from-')) return `anim-in-${animIn}`;
      return `anim-in-${animIn}`;
    }

    function applyFlyOut(box, animOut, pos) {
      if (!box) return;
      pos = pos || 'top-right';
      animOut = animOut || 'slide';

      let dir = animOut;
      if (dir === 'slide') {
        if (pos.includes('right')) dir = 'to-right';
        else if (pos.includes('left')) dir = 'to-left';
        else if (pos.includes('bottom')) dir = 'to-bottom';
        else dir = 'to-top';
      } else if (dir.startsWith('from-')) {
        dir = dir.replace('from-', 'to-');
      }

      let dx = 0, dy = 0, scale = 1;
      const isAtRight = pos.includes('right');
      const isAtLeft = pos.includes('left');
      const isAtTop = pos.includes('top');
      const isAtBottom = pos.includes('bottom');

      if (dir === 'to-right') {
        dx = isAtLeft ? 2200 : 600;
      } else if (dir === 'to-left') {
        dx = isAtRight ? -2200 : -600;
      } else if (dir === 'to-top') {
        dy = isAtBottom ? -1300 : -450;
      } else if (dir === 'to-bottom') {
        dy = isAtTop ? 1300 : 450;
      } else if (dir === 'to-top-left') {
        dx = isAtRight ? -2200 : -600;
        dy = isAtBottom ? -1300 : -450;
      } else if (dir === 'to-top-right') {
        dx = isAtLeft ? 2200 : 600;
        dy = isAtBottom ? -1300 : -450;
      } else if (dir === 'to-bottom-left') {
        dx = isAtRight ? -2200 : -600;
        dy = isAtTop ? 1300 : 450;
      } else if (dir === 'to-bottom-right') {
        dx = isAtLeft ? 2200 : 600;
        dy = isAtTop ? 1300 : 450;
      } else if (dir === 'zoom') {
        scale = 0.2;
      } else if (dir === 'bounce') {
        scale = 0.5;
      }

      const prevAnimClasses = allAnimClasses.filter(c => c !== 'visible');
      box.classList.remove('anim-out-active', ...prevAnimClasses);
      box.style.setProperty('--exit-dx', dx + 'px');
      box.style.setProperty('--exit-dy', dy + 'px');
      box.style.setProperty('--exit-scale', scale);
      void box.offsetWidth;
      box.classList.remove('visible');
      box.classList.add('anim-out-active');
    }

    function resolveFlyOutClass(animOut, pos) {
      if (!animOut || animOut === 'slide') {
        if (pos === 'top-right' || pos === 'bottom-right' || pos === 'right') return 'anim-in-from-right';
        if (pos === 'top-left' || pos === 'bottom-left' || pos === 'left') return 'anim-in-from-left';
        if (pos === 'top') return 'anim-in-from-top';
        if (pos === 'bottom') return 'anim-in-from-bottom';
        return 'anim-in-from-top';
      }
      if (animOut.startsWith('from-')) return `anim-in-${animOut}`;
      return `anim-in-${animOut}`;
    }

    const allAnimClasses = [
      'visible', 'anim-in-slide', 'anim-in-fade', 'anim-in-zoom', 'anim-in-bounce',
      'anim-in-from-top', 'anim-in-from-bottom', 'anim-in-from-left', 'anim-in-from-right',
      'anim-in-from-top-left', 'anim-in-from-top-right', 'anim-in-from-bottom-left', 'anim-in-from-bottom-right'
    ];

    if (evtType === 'giveaway_state') {
      if (data.state && (data.state.active || data.state.checkpoint_active)) {
        handleGiveawayEvent({
          type: 'giveaway_checkpoint_start',
          cp_index: data.state.cp_index || data.state.current_checkpoint || 1,
          code: data.state.code || ((data.state.checkpoints && data.state.checkpoints[data.state.current_checkpoint - 1]) ? data.state.checkpoints[data.state.current_checkpoint - 1].code : '!join'),
          duration: (typeof data.state.duration_sec !== 'undefined') ? data.state.duration_sec : (data.state.checkpoint_duration || 0),
          remaining: data.state.remaining_sec,
          mode: data.state.mode,
          total_checkpoints: data.state.total_checkpoints
        });
      }
    } else if (evtType === 'giveaway_checkpoint_start') {
      _gwIsAnimatingOut = false;
      inner.classList.remove('giveaway-idle');
      if (_gwCpDismissTimer) { clearTimeout(_gwCpDismissTimer); _gwCpDismissTimer = null; }
      if (_gwCpHideTimer) { clearTimeout(_gwCpHideTimer); _gwCpHideTimer = null; }
      _gwCpTotalDuration = (typeof data.duration !== 'undefined') ? data.duration : (_giveawayConfig.duration_sec || 0);

      // ถ้าตั้งโหมดแสดงผลเป็น none (ซ่อนบนจอ / โหมดเบื้องหลัง) ให้เปิดรับเงียบๆ ไม่แสดง overlay ใดๆ บนจอ
      if (_giveawayConfig.overlay_display_mode === 'none') {
        if (cpBox) { cpBox.style.display = 'none'; cpBox.classList.remove('visible'); }
        if (imgBox) { imgBox.style.display = 'none'; imgBox.classList.remove('visible'); }
        return;
      }

      const isImageMode = (_giveawayConfig.overlay_display_mode === 'image' && _giveawayConfig.overlay_has_image);
      const targetPos = _giveawayConfig.overlay_position || 'top-right';

      if (isImageMode && imgBox) {
        if (cpBox) { cpBox.style.display = 'none'; cpBox.classList.remove('visible'); }
        if (imgFill) imgFill.style.width = '100%';
        if (imgCountdownRect) {
          if (_gwCpTotalDuration > 0 && typeof data.remaining !== 'undefined') {
            const pct = Math.max(0, Math.min(100, (data.remaining / _gwCpTotalDuration) * 100));
            imgCountdownRect.style.strokeDashoffset = String(100 - pct);
            if (imgFill) imgFill.style.width = pct + '%';
          } else {
            imgCountdownRect.style.strokeDashoffset = '0';
          }
        }
        if (data.duration > 0) {
          const remSec = (typeof data.remaining !== 'undefined') ? data.remaining : data.duration;
          const m = Math.floor(remSec / 60), s = Math.floor(remSec % 60);
          if (imgTimerText) imgTimerText.textContent = `⏱️ ${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        } else {
          if (imgTimerText) imgTimerText.textContent = '⏱️ เปิดรับต่อเนื่อง';
        }
        const initialCount = (data.total !== undefined) ? data.total : ((data.state && data.state.participants && data.state.participants.length) || 0);
        if (imgCountText) imgCountText.textContent = `👥 ${initialCount} คน`;

        const animInClass = resolveFlyInClass(_giveawayConfig.overlay_anim_in, targetPos);
        imgBox.classList.remove('anim-out-active', ...allAnimClasses);
        imgBox.style.removeProperty('--exit-dx');
        imgBox.style.removeProperty('--exit-dy');
        imgBox.style.removeProperty('--exit-scale');
        imgBox.classList.add(animInClass);
        imgBox.style.display = 'block';
        void imgBox.offsetWidth;
        requestAnimationFrame(() => requestAnimationFrame(() => imgBox.classList.add('visible')));
      } else if (cpBox) {
        if (imgBox) { imgBox.style.display = 'none'; imgBox.classList.remove('visible'); }
        if (cpBadge) {
          cpBadge.textContent = (data.mode === 'single') ? '🎯 เช็คชื่อรับสิทธิ์สุ่มรางวัล' : `📍 ด่านที่ ${data.cp_index} (สะสมแต้ม ${data.total_checkpoints || 2} ด่าน)`;
        }
        if (cpStatus) {
          cpStatus.textContent = '🟢 กำลังเปิดรับ';
          cpStatus.style.color = '#10b981';
          cpStatus.style.background = 'rgba(16, 185, 129, 0.2)';
        }
        if (cpCode) cpCode.textContent = data.code || '!join';
        if (cpFill) cpFill.style.width = '100%';
        if (cpCountdownRect) {
          if (_gwCpTotalDuration > 0 && typeof data.remaining !== 'undefined') {
            const pct = Math.max(0, Math.min(100, (data.remaining / _gwCpTotalDuration) * 100));
            cpCountdownRect.style.strokeDashoffset = String(100 - pct);
            if (cpFill) cpFill.style.width = pct + '%';
          } else {
            cpCountdownRect.style.strokeDashoffset = '0';
          }
        }
        if (data.duration > 0) {
          const m = Math.floor(data.duration / 60), s = Math.floor(data.duration % 60);
          if (cpTimer) cpTimer.textContent = `⏱️ เหลือเวลา: ${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        } else {
          if (cpTimer) cpTimer.textContent = '⏱️ เปิดรับต่อเนื่อง';
        }
        const initialCount = (data.total !== undefined) ? data.total : ((data.state && data.state.participants && data.state.participants.length) || 0);
        if (cpCount) cpCount.textContent = `👥 ผู้เข้าร่วมรอบนี้: ${initialCount} คน`;

        const animInClass = resolveFlyInClass(_giveawayConfig.overlay_anim_in, targetPos);
        cpBox.classList.remove('anim-out-active', ...allAnimClasses);
        cpBox.style.removeProperty('--exit-dx');
        cpBox.style.removeProperty('--exit-dy');
        cpBox.style.removeProperty('--exit-scale');
        cpBox.classList.add(animInClass);
        cpBox.style.display = 'block';
        void cpBox.offsetWidth;
        requestAnimationFrame(() => requestAnimationFrame(() => cpBox.classList.add('visible')));
      }
    } else if (evtType === 'giveaway_tick') {
      if (typeof data.duration !== 'undefined' && (!_gwCpTotalDuration || _gwCpTotalDuration <= 0)) {
        _gwCpTotalDuration = data.duration;
      }
      if (_gwCpTotalDuration > 0) {
        const pct = Math.max(0, Math.min(100, (data.remaining / _gwCpTotalDuration) * 100));
        const m = Math.floor(data.remaining / 60), s = Math.floor(data.remaining % 60);
        const timeStr = `⏱️ ${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        if (cpFill) cpFill.style.width = pct + '%';
        if (imgFill) imgFill.style.width = pct + '%';
        if (cpTimer) cpTimer.textContent = `⏱️ เหลือเวลา: ${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        if (cpCountdownRect) cpCountdownRect.style.strokeDashoffset = String(100 - pct);
        if (imgCountdownRect) imgCountdownRect.style.strokeDashoffset = String(100 - pct);
        if (imgTimerText) imgTimerText.textContent = timeStr;
      } else {
        if (cpCountdownRect) cpCountdownRect.style.strokeDashoffset = '0';
        if (imgCountdownRect) imgCountdownRect.style.strokeDashoffset = '0';
        if (imgTimerText) imgTimerText.textContent = '⏱️ เปิดรับต่อเนื่อง';
      }
      if (typeof data.total !== 'undefined') {
        if (cpCount) cpCount.textContent = `👥 ผู้เข้าร่วมรอบนี้: ${data.total} คน`;
        if (imgCountText) imgCountText.textContent = `👥 ${data.total} คน`;
      }
    } else if (evtType === 'giveaway_checkpoint_end') {
      if (_gwCpDismissTimer) { clearTimeout(_gwCpDismissTimer); _gwCpDismissTimer = null; }
      if (_gwCpHideTimer) { clearTimeout(_gwCpHideTimer); _gwCpHideTimer = null; }

      _gwIsAnimatingOut = true;
      const isImageMode = (_giveawayConfig.overlay_display_mode === 'image' && _giveawayConfig.overlay_has_image);
      const targetPos = _giveawayConfig.overlay_position || 'top-right';
      const animOutClass = resolveFlyOutClass(_giveawayConfig.overlay_anim_out, targetPos);
      const prevAnimClasses = allAnimClasses.filter(c => c !== 'visible');

      if (isImageMode && imgBox) {
        if (imgFill) imgFill.style.width = '0%';
        if (imgCountdownRect) imgCountdownRect.style.strokeDashoffset = '100';
        applyFlyOut(imgBox, _giveawayConfig.overlay_anim_out, targetPos);
        _gwCpHideTimer = setTimeout(() => {
          imgBox.style.display = 'none';
          imgBox.classList.remove('anim-out-active', ...allAnimClasses);
          imgBox.style.removeProperty('--exit-dx');
          imgBox.style.removeProperty('--exit-dy');
          imgBox.style.removeProperty('--exit-scale');
          inner.classList.add('giveaway-idle');
          _gwIsAnimatingOut = false;
        }, 480);
      } else if (cpBox) {
        if (cpFill) cpFill.style.width = '0%';
        if (cpCountdownRect) cpCountdownRect.style.strokeDashoffset = '100';
        applyFlyOut(cpBox, _giveawayConfig.overlay_anim_out, targetPos);
        _gwCpHideTimer = setTimeout(() => {
          cpBox.style.display = 'none';
          cpBox.classList.remove('anim-out-active', ...allAnimClasses);
          cpBox.style.removeProperty('--exit-dx');
          cpBox.style.removeProperty('--exit-dy');
          cpBox.style.removeProperty('--exit-scale');
          inner.classList.add('giveaway-idle');
          _gwIsAnimatingOut = false;
        }, 480);
      }
    } else if (evtType === 'giveaway_participant') {
      if (cpCount) cpCount.textContent = `👥 ผู้เข้าร่วมรอบนี้: ${data.round_participants} คน`;
      if (imgCountText) imgCountText.textContent = `👥 ${data.round_participants} คน`;
      if (_giveawayConfig.overlay_show_toast && cpToast) {
        cpToast.textContent = `✨ ${data.author} เข้าร่วมแล้ว!`;
        cpToast.classList.add('show');
        if (_gwToastTimer) clearTimeout(_gwToastTimer);
        _gwToastTimer = setTimeout(() => cpToast.classList.remove('show'), 1600);
      }
    } else if (evtType === 'giveaway_draw_start') {
      inner.classList.remove('giveaway-idle');
      if (_gwDrawAutoHideTimer) { clearTimeout(_gwDrawAutoHideTimer); _gwDrawAutoHideTimer = null; }
      if (_gwSlotRollInterval) { clearInterval(_gwSlotRollInterval); _gwSlotRollInterval = null; }
      if (_gwSlotReelSpinInterval) { clearInterval(_gwSlotReelSpinInterval); _gwSlotReelSpinInterval = null; }
      _gwSlotReelDecelTimers.forEach(t => clearTimeout(t));
      _gwSlotReelDecelTimers = [];

      const chosenStyle = data.style || _giveawayConfig.draw_animation_style || 'gachapon';
      const isGacha = (chosenStyle === 'gachapon');
      const isReel = (chosenStyle === 'slot' || chosenStyle === 'slotmachine' || chosenStyle === 'slot_reel');

      _gwCandidatesPool = (data.candidates && data.candidates.length > 0) ? data.candidates : [];
      _gwDrawWinner = data.winner || '';
      _gwIsDrawRunning = false;

      if (drawBox) {
        drawBox.classList.remove('winner', 'fadeout');
        drawBox.classList.remove('style-gachapon');
        if (isGacha) drawBox.classList.add('style-gachapon');
        drawBox.classList.add('visible');
      }

      const slotStage = inner.querySelector('.giveaway-slot-stage');
      if (slotStage) {
        if (isReel) slotStage.classList.add('is-reel');
        else slotStage.classList.remove('is-reel');
      }

      if (drawPrize) { drawPrize.textContent = ''; drawPrize.style.display = 'none'; }
      if (drawTier) { drawTier.textContent = ''; drawTier.style.display = 'none'; }
      if (drawStatus) drawStatus.textContent = '⚡ กำลังสุ่มผู้โชคดี...';

      const pool = (_gwCandidatesPool.length > 0) ? _gwCandidatesPool : ['ผู้เข้าร่วมกิจกรรม'];

      if (_gwDrawWinner) {
        // รู้ชื่อผู้ชนะตั้งแต่เริ่มสุ่ม -> รันอนิเมชั่นเลื่อนชะลอความเร็วแบบต่อเนื่องทันที ไม่มีการสะดุด
        _gwIsDrawRunning = true;
        if (isGacha) {
          startGachaponDraw(inner, _gwDrawWinner, '');
        } else if (isReel) {
          startSmoothReelDraw(inner, _gwDrawWinner, pool);
        } else {
          startSmoothShuffleDraw(inner, _gwDrawWinner, pool);
        }
      } else {
        // กรณีสำรอง (ถ้ายังไม่มีการส่งผู้ชนะมาใน draw_start)
        if (isGacha) {
          startGachaponDraw(inner, 'ผู้โชคดี', '');
        } else if (isReel) {
          const strip = inner.querySelector('.giveaway-slot-strip');
          if (strip) {
            strip.style.transition = 'none';
            strip.style.transform = 'translateY(0px)';
            let itemsHtml = '';
            for (let r = 0; r < 14; r++) {
              const name = pool[r % pool.length];
              itemsHtml += `<div class="slot-reel-item"><span class="slot-reel-item-text">${name}</span></div>`;
            }
            strip.innerHTML = itemsHtml;
            strip.classList.add('spinning');
          }
          let tick = 0;
          _gwSlotReelSpinInterval = setInterval(() => {
            tick++;
            if (tick % 2 === 0) playGwTickSound();
          }, 65);
        } else {
          if (slotName) slotName.classList.add('rolling');
          let tick = 0;
          _gwSlotRollInterval = setInterval(() => {
            tick++;
            const dummy = pool[Math.floor(Math.random() * pool.length)];
            if (slotName) slotName.textContent = dummy;
            if (tick % 2 === 0) playGwTickSound();
          }, 75);
        }
      }
    } else if (evtType === 'giveaway_draw_winner') {
      const chosenStyle = data.style || _giveawayConfig.draw_animation_style || 'gachapon';
      const isGacha = (chosenStyle === 'gachapon');
      const isReel = (chosenStyle === 'slot' || chosenStyle === 'slotmachine' || chosenStyle === 'slot_reel');
      const winnerName = data.author || _gwDrawWinner || 'Streamer';
      const prizeName = '';
      const pool = (data.candidates && data.candidates.length > 0) ? data.candidates : (_gwCandidatesPool.length > 0 ? _gwCandidatesPool : [winnerName]);

      if (drawBox) {
        drawBox.classList.remove('fadeout');
        if (isGacha) drawBox.classList.add('style-gachapon');
      }
      if (drawPrize) { drawPrize.textContent = ''; drawPrize.style.display = 'none'; }

      if (_gwIsDrawRunning && _gwDrawWinner === winnerName) {
        // อนิเมชั่นกำลังเลื่อนชะลอตัวและมุ่งสู่ผู้ชนะอยู่แล้ว ปล่อยให้ทำงานอย่างสมูทจนจบ
        return;
      }

      // ถ้ายังไม่ได้เริ่มสุ่มมาก่อน ให้เริ่มเลื่อนชะลอความเร็วสู่ผู้ชนะทันที
      _gwIsDrawRunning = true;
      _gwDrawWinner = winnerName;
      if (isGacha) {
        startGachaponDraw(inner, winnerName, prizeName);
      } else if (isReel) {
        startSmoothReelDraw(inner, winnerName, pool);
      } else {
        startSmoothShuffleDraw(inner, winnerName, pool);
      }
    } else if (evtType === 'giveaway_draw_reset') {
      _gwIsDrawRunning = false;
      _gwDrawWinner = '';
      if (_gwDrawAutoHideTimer) { clearTimeout(_gwDrawAutoHideTimer); _gwDrawAutoHideTimer = null; }
      if (_gwSlotRollInterval) { clearInterval(_gwSlotRollInterval); _gwSlotRollInterval = null; }
      if (_gwSlotReelSpinInterval) { clearInterval(_gwSlotReelSpinInterval); _gwSlotReelSpinInterval = null; }
      _gwSlotReelDecelTimers.forEach(t => clearTimeout(t));
      _gwSlotReelDecelTimers = [];

      if (drawBox && drawBox.classList.contains('visible')) {
        drawBox.classList.add('fadeout');
        setTimeout(() => {
          drawBox.classList.remove('visible', 'winner', 'style-gachapon', 'fadeout');
          const gachaStage = inner.querySelector('.giveaway-gacha-stage');
          if (gachaStage) gachaStage.classList.remove('shaking', 'revealed', 'gacha-entering', 'gacha-wobble', 'gacha-charging');
          const strip = inner.querySelector('.giveaway-slot-strip');
          if (strip) {
            strip.classList.remove('spinning');
            strip.style.transition = 'none';
            strip.style.transform = 'translateY(0px)';
            strip.innerHTML = '';
          }
        }, 450);
      } else if (drawBox) {
        drawBox.classList.remove('visible', 'winner', 'style-gachapon', 'fadeout');
        const gachaStage = inner.querySelector('.giveaway-gacha-stage');
        if (gachaStage) gachaStage.classList.remove('shaking', 'revealed', 'gacha-entering', 'gacha-wobble', 'gacha-charging');
        const strip = inner.querySelector('.giveaway-slot-strip');
        if (strip) {
          strip.classList.remove('spinning');
          strip.style.transition = 'none';
          strip.style.transform = 'translateY(0px)';
          strip.innerHTML = '';
        }
      }
    } else if (evtType === 'giveaway_data_cleared') {
      if (cpBox) { cpBox.style.display = 'none'; cpBox.classList.remove('visible'); }
      if (imgBox) { imgBox.style.display = 'none'; imgBox.classList.remove('visible'); }
      if (drawBox) { drawBox.style.display = 'none'; drawBox.classList.remove('visible'); }
      inner.classList.add('giveaway-idle');
    } else if (evtType === 'giveaway_preview') {
      if (data.action === 'draw_preview') {
        inner.classList.remove('giveaway-idle');
        const st = data.style || _giveawayConfig.draw_animation_style || 'gachapon';
        const cand = data.candidates || ['LuckyViewer_A', 'StreamFan_99', 'SuperChat_Pro'];
        const win = data.winner || '🎉 ผู้โชคดีตัวอย่าง 🎉';
        handleGiveawayEvent({
          type: 'giveaway_draw_start',
          candidates: cand,
          winner: win,
          style: st
        });
        return;
      }
      if (data.action === 'stop' || data.show === false) {
        if (_gwCpDismissTimer) { clearTimeout(_gwCpDismissTimer); _gwCpDismissTimer = null; }
        if (_gwCpHideTimer) { clearTimeout(_gwCpHideTimer); _gwCpHideTimer = null; }
        const targetPos = _giveawayConfig.overlay_position || 'top-right';
        _gwIsAnimatingOut = true;
        if (cpBox && (cpBox.classList.contains('visible') || cpBox.style.display === 'block')) {
          applyFlyOut(cpBox, _giveawayConfig.overlay_anim_out, targetPos);
          setTimeout(() => {
            cpBox.style.display = 'none';
            cpBox.classList.remove('anim-out-active', ...allAnimClasses);
            cpBox.style.removeProperty('--exit-dx');
            cpBox.style.removeProperty('--exit-dy');
            cpBox.style.removeProperty('--exit-scale');
            inner.classList.add('giveaway-idle');
            _gwIsAnimatingOut = false;
          }, 480);
        }
        if (imgBox && (imgBox.classList.contains('visible') || imgBox.style.display === 'block')) {
          applyFlyOut(imgBox, _giveawayConfig.overlay_anim_out, targetPos);
          setTimeout(() => {
            imgBox.style.display = 'none';
            imgBox.classList.remove('anim-out-active', ...allAnimClasses);
            imgBox.style.removeProperty('--exit-dx');
            imgBox.style.removeProperty('--exit-dy');
            imgBox.style.removeProperty('--exit-scale');
            inner.classList.add('giveaway-idle');
            _gwIsAnimatingOut = false;
          }, 480);
        }
        return;
      }
      inner.classList.remove('giveaway-idle');
      handleGiveawayEvent({
        type: 'giveaway_checkpoint_start',
        cp_index: data.cp_index || 1,
        code: data.code || '!join',
        duration: data.duration || 60,
        mode: data.mode || 'single',
        total_checkpoints: data.total_checkpoints || 1
      });
      if (!data.stay) {
        setTimeout(() => {
          handleGiveawayEvent({ type: 'giveaway_checkpoint_end', total: 5 });
        }, (data.duration || 4) * 1000);
      }
    }
  });
}

// ════════════════════════════════════════════════════════════
// Now Playing handler (Windows System Media)
// ════════════════════════════════════════════════════════════

let lastSignature='';
function stopDraw(){
  clearTimeout(_gwDrawAutoHideTimer);clearTimeout(_gwCpDismissTimer);clearTimeout(_gwCpHideTimer);clearTimeout(_gwToastTimer);
  clearInterval(_gwSlotRollInterval);clearInterval(_gwSlotReelSpinInterval);
  _gwSlotReelDecelTimers.forEach(clearTimeout);_gwSlotReelDecelTimers=[];
  if(_gwConfettiAnimId)cancelAnimationFrame(_gwConfettiAnimId);
  _gwIsDrawRunning=false;_gwDrawWinner='';
}
window.BP3LegacyGiveaway={render(data){
  const targets=Array.from(document.querySelectorAll('.widget.type-giveaway'));
  let rebuilt=false;
  targets.forEach(el=>{
    let inner=el.querySelector('.widget-inner');
    if(!inner){inner=document.createElement('div');inner.className='widget-inner composer-widget-inner';inner.id='compGwPanel_'+el.dataset.id;el.replaceChildren(inner);renderGiveawayInto(inner);rebuilt=true;}
    inner.style.cssText='position:relative;width:100%;height:100%;background:transparent;border:none;display:'+(data?.active?'block':'none')+' !important;';
  });
  const signature=JSON.stringify([data?.active,data?.phase,data?.code,data?.winner,data?.drawId,data?.cp_index,data?.style,data?.config]);
  if(!data?.active){stopDraw();lastSignature='';targets.forEach(el=>el.querySelector('.widget-inner')?.replaceChildren());return;}
  targets.forEach(el=>{const inner=el.querySelector('.widget-inner');if(!inner.querySelector('.giveaway-cp-box')){renderGiveawayInto(inner);rebuilt=true;}});
  Object.assign(_giveawayConfig,data.config || {},{sound_enabled:false,overlay_position:data.anchor || 'right',draw_autohide_sec:data.holdDuration ?? 15});
  if(signature!==lastSignature || rebuilt){
    stopDraw();
    if(data.phase==='winner'){
      handleGiveawayEvent({type:'giveaway_draw_start',winner:data.winner,prize:data.prize,candidates:data.candidates || [data.winner],style:data.style || 'gachapon'});
    }else{
      handleGiveawayEvent({type:'giveaway_draw_reset'});
      handleGiveawayEvent({type:'giveaway_checkpoint_start',code:data.code,total:data.count || 0,duration:data.duration || 0,remaining:data.remainingSec,mode:data.mode || 'single',cp_index:data.cp_index || 1,total_checkpoints:data.total_checkpoints || 1});
    }
    lastSignature=signature;
  }
  targets.forEach(el=>{const count=el.querySelector('.giveaway-cp-count');if(count)count.textContent='👥 '+(data.count || 0)+' คน';});
}};
})();
