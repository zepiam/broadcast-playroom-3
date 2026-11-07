/* Quick Randomizer visuals v2.
 * One renderer shared by: OBS page (composer.html), Studio canvas (composer_studio.js) and the settings preview.
 * Rules kept: no backdrop-filter, no infinite animation (everything is finite and stops, idle GPU = 0),
 * overlay exists only while active (standby transparency), no sound.
 */
(() => {
  'use strict';
  if (window.BP3RandomizerVisual && window.BP3RandomizerVisual.version >= 3) return;

  const NS = 'http://www.w3.org/2000/svg';
  const STYLES = [
    {id: 'wheel', label: 'Roulette Wheel', icon: '🎡', hint: 'หมุนเร็วแล้วค่อย ๆ ช้าลง จนหยุดที่ช่องผู้ชนะ'},
    {id: 'reel', label: 'Slot', icon: '🎰', hint: 'ชื่อเลื่อนผ่านเร็ว ๆ แล้วชะลอ จนหยุดกลางกรอบ'}
  ];
  const THEMES = {
    pastel: {label: 'Pastel', a: '#c4b5fd', b: '#f9a8d4', ink: '#1f2937', rim: '#f5f3ff', hub: '#6d28d9',
      slices: ['#c4b5fd', '#f9a8d4', '#a5f3fc', '#fde68a', '#bbf7d0', '#fdba74', '#93c5fd', '#fca5a5']},
    candy: {label: 'Candy', a: '#f472b6', b: '#67e8f9', ink: '#1f1147', rim: '#f9a8d4', hub: '#701a75',
      slices: ['#f472b6', '#67e8f9', '#fde047', '#c084fc', '#86efac', '#fb923c', '#a5b4fc', '#fda4af']},
    sakura: {label: 'Sakura', a: '#f9a8d4', b: '#fbcfe8', ink: '#3b0a24', rim: '#fce7f3', hub: '#9d174d',
      slices: ['#f9a8d4', '#fce7f3', '#f472b6', '#fbcfe8', '#ec4899', '#fda4af', '#db2777', '#fecdd3']},
    sunset: {label: 'Sunset', a: '#fb7185', b: '#fdba74', ink: '#2a0a12', rim: '#fed7aa', hub: '#7f1d1d',
      slices: ['#fb7185', '#f97316', '#fbbf24', '#e11d48', '#fb923c', '#be123c', '#fdba74', '#f43f5e']},
    ruby: {label: 'Ruby', a: '#f43f5e', b: '#fecdd3', ink: '#2d0a14', rim: '#fda4af', hub: '#881337',
      slices: ['#be123c', '#fecdd3', '#e11d48', '#fda4af', '#9f1239', '#fb7185']},
    gold: {label: 'Gold', a: '#f59e0b', b: '#fde68a', ink: '#3b1d03', rim: '#fcd34d', hub: '#78350f',
      slices: ['#fbbf24', '#92400e', '#f59e0b', '#78350f', '#fcd34d', '#b45309']},
    royal: {label: 'Royal', a: '#a78bfa', b: '#fcd34d', ink: '#1e1b4b', rim: '#c4b5fd', hub: '#312e81',
      slices: ['#4c1d95', '#fbbf24', '#6d28d9', '#f59e0b', '#4338ca', '#fde68a', '#5b21b6', '#d97706']},
    neon: {label: 'Neon', a: '#22d3ee', b: '#e879f9', ink: '#0b1020', rim: '#22d3ee', hub: '#0b1020',
      slices: ['#d946ef', '#22d3ee', '#a3e635', '#fb923c', '#818cf8', '#fb7185', '#2dd4bf', '#facc15']},
    ocean: {label: 'Ocean', a: '#38bdf8', b: '#67e8f9', ink: '#04202e', rim: '#bae6fd', hub: '#0c4a6e',
      slices: ['#0ea5e9', '#0369a1', '#22d3ee', '#1d4ed8', '#38bdf8', '#0e7490', '#60a5fa', '#155e75']},
    mint: {label: 'Mint', a: '#10b981', b: '#a7f3d0', ink: '#052e22', rim: '#6ee7b7', hub: '#064e3b',
      slices: ['#34d399', '#065f46', '#6ee7b7', '#047857', '#a7f3d0', '#064e3b']},
    forest: {label: 'Forest', a: '#4ade80', b: '#bef264', ink: '#052e16', rim: '#bbf7d0', hub: '#14532d',
      slices: ['#16a34a', '#166534', '#84cc16', '#15803d', '#65a30d', '#14532d', '#4ade80', '#3f6212']}
  };
  const ANCHORS = {
    'center': [{top: '50%', left: '50%'}, 'translate(-50%,-50%)', 'center center'],
    'top-left': [{top: '40px', left: '40px'}, '', 'top left'],
    'top-center': [{top: '40px', left: '50%'}, 'translate(-50%,0)', 'top center'],
    'top-right': [{top: '40px', right: '40px'}, '', 'top right'],
    'middle-left': [{top: '50%', left: '40px'}, 'translate(0,-50%)', 'left center'],
    'middle-right': [{top: '50%', right: '40px'}, 'translate(0,-50%)', 'right center'],
    'bottom-left': [{bottom: '40px', left: '40px'}, '', 'bottom left'],
    'bottom-center': [{bottom: '40px', left: '50%'}, 'translate(-50%,0)', 'bottom center'],
    'bottom-right': [{bottom: '40px', right: '40px'}, '', 'bottom right']
  };
  const STAGE_SIZE = {wheel: [520, 520], reel: [560, 320], flip: [520, 330], box: [420, 380]};

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const num = (v, d) => (Number.isFinite(Number(v)) && v !== '' && v !== null ? Number(v) : d);
  const pow = (p) => (t) => 1 - Math.pow(1 - t, p);
  const easeOut = pow(3.2);
  const easeOutBack = (t) => {const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);};

  /* WCAG relative luminance + contrast ratio (SC 1.4.3 needs 4.5:1 for normal text) */
  function relLum(hex) {
    const m = /^#?([0-9a-f]{6})$/i.exec(hex || '');
    if (!m) return 0.5;
    const n = parseInt(m[1], 16);
    const f = (c) => {c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);};
    return 0.2126 * f((n >> 16) & 255) + 0.7152 * f((n >> 8) & 255) + 0.0722 * f(n & 255);
  }
  function contrast(h1, h2) {
    const a = relLum(h1), b = relLum(h2);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }
  const lum = relLum;
  /* pick whichever of near-black / white reads better on this background */
  const inkFor = (hex) => (contrast(hex, '#111827') >= contrast(hex, '#ffffff') ? '#111827' : '#ffffff');
  function sliceColor(theme, i, n) {
    const k = theme.slices.length;
    let c = i % k;
    if (n > 1 && i === n - 1 && c === 0) c = Math.floor(k / 2);
    if (n > 2 && i > 0 && theme.slices[c] === theme.slices[(i - 1) % k]) c = (c + 1) % k;
    return theme.slices[c];
  }
  // fonts with Thai glyphs, loaded from Google Fonts only when chosen (system fonts take over when offline)
  const FONTS = {
    prompt: {label: 'Prompt', family: "'Prompt'", css: 'Prompt:wght@500;700;800;900'},
    kanit: {label: 'Kanit', family: "'Kanit'", css: 'Kanit:wght@500;700;800;900'},
    mitr: {label: 'Mitr', family: "'Mitr'", css: 'Mitr:wght@500;600;700'},
    chakra: {label: 'Chakra Petch', family: "'Chakra Petch'", css: 'Chakra+Petch:wght@500;600;700'},
    bai: {label: 'Bai Jamjuree', family: "'Bai Jamjuree'", css: 'Bai+Jamjuree:wght@500;600;700'},
    itim: {label: 'Itim', family: "'Itim'", css: 'Itim'},
    mali: {label: 'Mali', family: "'Mali'", css: 'Mali:wght@500;600;700'},
    pridi: {label: 'Pridi', family: "'Pridi'", css: 'Pridi:wght@500;600;700'}
  };
  const FONT_FALLBACK = ", 'Prompt', 'Kanit', 'Noto Sans Thai', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
  const fontStack = (id) => (FONTS[id] || FONTS.prompt).family + FONT_FALLBACK;
  // resolves when the font is usable (or after a short timeout); never rejects
  function loadFont(doc, id) {
    const f = FONTS[id];
    if (!f) return Promise.resolve();
    try {
      const lid = 'bp3rz-font-' + id;
      if (!doc.getElementById(lid)) {
        const link = doc.createElement('link');
        link.id = lid; link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=' + f.css + '&display=swap';
        (doc.head || doc.documentElement).appendChild(link);
      }
      if (!doc.fonts || !doc.fonts.load) return Promise.resolve();
      const load = Promise.all([doc.fonts.load('700 24px ' + f.family, 'สุ่มAa'), doc.fonts.load('500 24px ' + f.family, 'สุ่มAa')]).catch(() => {});
      return Promise.race([load, new Promise((r) => setTimeout(r, 2500))]);
    } catch (_) {return Promise.resolve();}
  }

  function normalize(raw) {
    const s = Object.assign({}, raw || {});
    const ALIAS = { gachapon: 'wheel', box: 'wheel', flip: 'wheel', shuffle: 'wheel', slot: 'reel', slotmachine: 'reel', slot_reel: 'reel' };
    if (ALIAS[s.style]) s.style = ALIAS[s.style];
    if (ALIAS[s.mode] && !STYLES.some((x) => x.id === s.style)) s.mode = ALIAS[s.mode];
    const style = STYLES.some((x) => x.id === s.style) ? s.style : (STYLES.some((x) => x.id === s.mode) ? s.mode : 'wheel');
    return {
      style,
      scale: clamp(num(s.scale, 100), 20, 300),
      offset_x: clamp(num(s.offset_x, 0), -1920, 1920),
      offset_y: clamp(num(s.offset_y, 0), -1080, 1080),
      anchor: ANCHORS[s.anchor] ? s.anchor : 'center',
      spin_duration: clamp(num(s.spin_duration, 4), 1.5, 12),
      hold: s.duration === undefined || s.duration === null ? 5 : clamp(num(s.duration, 5), 1, 120),
      color_theme: THEMES[s.color_theme] ? s.color_theme : 'pastel',
      font: FONTS[s.font] ? s.font : 'prompt',
      reduce_motion: s.reduce_motion === true || s.reduce_motion === 'on' || s.reduce_motion === 1
    };
  }

  function injectStyle(doc) {
    if (doc.getElementById('bp3rz-style')) return;
    const css = `
.bp3rz-root{position:fixed;z-index:9999999;pointer-events:none;width:640px;box-sizing:border-box;font-family:'Prompt','Kanit','Noto Sans Thai',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#fff;contain:layout style;isolation:isolate;}
.bp3rz-card{display:flex;flex-direction:column;align-items:center;gap:14px;opacity:0;transform:translateY(16px) scale(.96);transition:opacity .35s ease-out,transform .45s cubic-bezier(.16,1,.3,1);}
.bp3rz-root.on .bp3rz-card{opacity:1;transform:none;}
.bp3rz-root.out .bp3rz-card{opacity:0;transform:translateY(-14px) scale(.97);transition:opacity .35s ease-in,transform .35s ease-in;}
.bp3rz-title{display:flex;flex-direction:column;align-items:center;padding:8px 26px 9px;border-radius:26px;background:rgba(11,17,32,.92);border:2px solid var(--rz-a);box-shadow:0 8px 26px rgba(0,0,0,.5);max-width:620px;box-sizing:border-box;}
.bp3rz-title-text{font-size:28px;font-weight:800;line-height:1.2;color:var(--rz-b);max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.bp3rz-sub{font-size:14px;font-weight:600;color:#cbd5e1;letter-spacing:.04em;}
.bp3rz-sub.done{color:var(--rz-b);}
.bp3rz-stage{position:relative;flex:none;}
.bp3rz-winner{min-height:84px;max-width:620px;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px 38px 12px;border-radius:24px;background:linear-gradient(135deg,var(--rz-a),var(--rz-b));color:var(--rz-ink);box-shadow:0 12px 32px rgba(0,0,0,.5),inset 0 0 0 3px rgba(255,255,255,.55);opacity:0;transform:scale(.7) translateY(10px);}
.bp3rz-winner.show{opacity:1;transform:none;transition:opacity .25s ease-out,transform .55s cubic-bezier(.34,1.56,.64,1);}
.bp3rz-winner-label{font-size:14px;font-weight:800;letter-spacing:.12em;}
.bp3rz-winner-row{display:flex;align-items:center;justify-content:center;gap:14px;max-width:100%;min-width:0;}
.bp3rz-ico{flex:none;object-fit:contain;display:block;filter:drop-shadow(0 2px 4px rgba(0,0,0,.35));}
.bp3rz-reel-txt-wrap{display:flex;align-items:center;justify-content:center;gap:12px;max-width:100%;min-width:0;}
.bp3rz-winner-name{min-width:0;font-weight:900;line-height:1.15;text-align:center;overflow-wrap:anywhere;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.bp3rz-slice{transition:opacity .45s ease-out;}
.bp3rz-reel{position:absolute;left:20px;top:10px;width:520px;height:300px;border-radius:24px;overflow:hidden;background:rgba(11,17,32,.94);border:3px solid var(--rz-a);box-shadow:0 14px 34px rgba(0,0,0,.55);}
.bp3rz-reel-strip{position:absolute;left:0;right:0;top:0;will-change:transform;}
.bp3rz-reel-row{height:100px;box-sizing:border-box;padding:9px 16px;}
.bp3rz-reel-txt{display:block;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:1.35;}
.bp3rz-reel-item{height:100%;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:800;padding:0 20px;box-sizing:border-box;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;transition:opacity .4s ease-out,transform .5s cubic-bezier(.34,1.56,.64,1),box-shadow .4s;}
.bp3rz-reel-fade{position:absolute;left:0;right:0;height:100px;pointer-events:none;}
.bp3rz-reel-fade.t{top:0;background:linear-gradient(rgba(11,17,32,.92),rgba(11,17,32,0));}
.bp3rz-reel-fade.b{bottom:0;background:linear-gradient(rgba(11,17,32,0),rgba(11,17,32,.92));}
.bp3rz-reel-line{position:absolute;left:0;right:0;height:3px;background:var(--rz-b);opacity:.9;pointer-events:none;}
.bp3rz-reel-mark{position:absolute;top:140px;font-size:34px;color:var(--rz-b);text-shadow:0 2px 8px rgba(0,0,0,.7);}
.bp3rz-deck{position:absolute;left:50%;top:50%;width:420px;height:262px;margin:-131px 0 0 -210px;perspective:1400px;}
.bp3rz-deck-bg{position:absolute;inset:0;border-radius:24px;background:rgba(11,17,32,.9);border:3px solid var(--rz-a);box-shadow:0 10px 24px rgba(0,0,0,.5);}
.bp3rz-card3d{position:absolute;inset:0;transform-style:preserve-3d;will-change:transform;}
.bp3rz-face{position:absolute;inset:0;border-radius:24px;backface-visibility:hidden;-webkit-backface-visibility:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:18px 28px;box-sizing:border-box;text-align:center;box-shadow:0 12px 30px rgba(0,0,0,.5);}
.bp3rz-face.front{background:linear-gradient(145deg,#1e293b,#0b1120);border:4px solid var(--rz-a);}
.bp3rz-face.back{background:linear-gradient(145deg,var(--rz-a),var(--rz-b));color:var(--rz-ink);transform:rotateY(180deg);border:4px solid rgba(255,255,255,.7);}
.bp3rz-face-text{font-size:44px;font-weight:900;line-height:1.15;overflow-wrap:anywhere;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
.bp3rz-face-cap{font-size:15px;font-weight:700;letter-spacing:.1em;margin-top:8px;}
.bp3rz-sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}
.bp3rz-root.calm .bp3rz-card,.bp3rz-root.calm .bp3rz-winner.show,.bp3rz-root.calm .bp3rz-reel-item,.bp3rz-root.calm .bp3rz-slice{transition-duration:.01s !important;}
`;
    const style = doc.createElement('style');
    style.id = 'bp3rz-style';
    style.textContent = css;
    (doc.head || doc.documentElement).appendChild(style);
  }

  function svg(doc, tag, attrs) {
    const node = doc.createElementNS(NS, tag);
    for (const k in attrs || {}) node.setAttribute(k, attrs[k]);
    return node;
  }
  function html(doc, tag, cls, text) {
    const node = doc.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  /* ---------- confetti: finite, removes itself ---------- */
  function confetti(doc, stage, theme) {
    if (!stage.animate) return;
    const layer = html(doc, 'div');
    layer.style.cssText = 'position:absolute;left:50%;top:46%;width:0;height:0;pointer-events:none;overflow:visible;';
    stage.appendChild(layer);
    const colors = theme.slices.concat([theme.a, theme.b, '#ffffff']);
    let pending = 0;
    for (let i = 0; i < 44; i++) {
      const piece = html(doc, 'span');
      const w = 8 + Math.random() * 8, h = 12 + Math.random() * 12;
      piece.style.cssText = `position:absolute;left:0;top:0;width:${w}px;height:${h}px;background:${colors[i % colors.length]};border-radius:${Math.random() < 0.3 ? '50%' : '2px'};`;
      layer.appendChild(piece);
      const dx = (Math.random() - 0.5) * 760, up = 160 + Math.random() * 260, rot = (Math.random() - 0.5) * 900;
      pending++;
      const a = piece.animate([
        {transform: 'translate(0,0) rotate(0deg)', opacity: 1},
        {transform: `translate(${dx * 0.7}px,${-up}px) rotate(${rot * 0.5}deg)`, opacity: 1, offset: 0.4, easing: 'cubic-bezier(.3,0,.8,1)'},
        {transform: `translate(${dx}px,${260 + Math.random() * 120}px) rotate(${rot}deg)`, opacity: 0}
      ], {duration: 1500 + Math.random() * 700, easing: 'cubic-bezier(.1,.7,.3,1)', fill: 'forwards'});
      a.onfinish = () => {if (--pending <= 0) layer.remove();};
    }
    setTimeout(() => layer.remove(), 2600);
  }

  /* ---------- style builders. Each returns {play(ms, done), finish(), stop()} ---------- */
  function raf(win, fn) {
    let id = 0, alive = true, last = 0;
    const loop = (ts) => {
      if (!alive) return;
      const dt = last ? Math.min(64, ts - last) : 16;
      last = ts;
      if (fn(ts, dt) === false) {alive = false; return;}
      id = win.requestAnimationFrame(loop);
    };
    id = win.requestAnimationFrame(loop);
    return () => {alive = false; try {win.cancelAnimationFrame(id);} catch (_) {}};
  }

  function buildWheel(ctx) {
    const {doc, win, items, theme, stage} = ctx;
    const n = items.length, C = 260, R = 232, RIM = 248, a = 360 / n;
    const root = svg(doc, 'svg', {viewBox: '0 0 520 520', width: '520', height: '520'});
    root.style.cssText = 'display:block;overflow:visible;';
    const U = ctx.uid;
    const defs = svg(doc, 'defs', {});
    const lg = svg(doc, 'linearGradient', {id: 'rzRim' + U, x1: '0', y1: '0', x2: '1', y2: '1'});
    lg.append(svg(doc, 'stop', {offset: '0%', 'stop-color': theme.b}), svg(doc, 'stop', {offset: '50%', 'stop-color': theme.a}), svg(doc, 'stop', {offset: '100%', 'stop-color': theme.b}));
    const shade = svg(doc, 'radialGradient', {id: 'rzShade' + U, cx: '50%', cy: '50%', r: '50%'});
    shade.append(svg(doc, 'stop', {offset: '55%', 'stop-color': '#000', 'stop-opacity': 0}), svg(doc, 'stop', {offset: '100%', 'stop-color': '#000', 'stop-opacity': 0.08}));
    const hubg = svg(doc, 'radialGradient', {id: 'rzHub' + U, cx: '35%', cy: '30%', r: '80%'});
    hubg.append(svg(doc, 'stop', {offset: '0%', 'stop-color': '#ffffff', 'stop-opacity': 0.55}), svg(doc, 'stop', {offset: '45%', 'stop-color': theme.hub}), svg(doc, 'stop', {offset: '100%', 'stop-color': '#050814'}));
    const glowF = svg(doc, 'filter', {id: 'rzGlowF' + U, x: '-20%', y: '-20%', width: '140%', height: '140%'});
    glowF.append(svg(doc, 'feGaussianBlur', {stdDeviation: 9}));
    defs.append(lg, shade, hubg, glowF);
    root.appendChild(defs);
    // soft coloured glow + ground shadow, then gradient rim and a dark bezel that holds the LED dots
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C + 14, r: RIM, fill: 'rgba(0,0,0,.45)', filter: `url(#rzGlowF${U})`}));
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: RIM + 2, fill: theme.a, opacity: 0.35, filter: `url(#rzGlowF${U})`}));
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: RIM, fill: `url(#rzRim${U})`}));
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: RIM - 9, fill: '#0a0f1e'}));
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: RIM - 9, fill: 'none', stroke: 'rgba(255,255,255,.22)', 'stroke-width': 1.5}));
    const rot = svg(doc, 'g', {});
    root.appendChild(rot);
    const pt = (deg, r) => [C + r * Math.sin(deg * Math.PI / 180), C - r * Math.cos(deg * Math.PI / 180)];
    const slices = [];
    for (let i = 0; i < n; i++) {
      const color = sliceColor(theme, i, n);
      const g = svg(doc, 'g', {class: 'bp3rz-slice'});
      if (n === 1) g.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: R, fill: color}));
      else {
        const p0 = pt(i * a, R), p1 = pt((i + 1) * a, R);
        g.appendChild(svg(doc, 'path', {d: `M${C} ${C}L${p0[0].toFixed(2)} ${p0[1].toFixed(2)}A${R} ${R} 0 ${a > 180 ? 1 : 0} 1 ${p1[0].toFixed(2)} ${p1[1].toFixed(2)}Z`, fill: color, stroke: 'rgba(255,255,255,.55)', 'stroke-width': n > 40 ? 0.5 : 1.6, 'stroke-linejoin': 'round'}));
      }
      if (n <= 40) {
        const fs = clamp(Math.round(26 - Math.max(0, n - 6) * 0.7), 12, 26);
        // labels on the left half are flipped so they never read upside down
        const mid = (i + 0.5) * a, flip = mid > 180 && mid < 360;
        const label = svg(doc, 'text', {x: flip ? C - R + 22 : C + R - 22, y: C, 'text-anchor': flip ? 'start' : 'end', 'dominant-baseline': 'central', 'font-size': fs, 'font-weight': 800, fill: inkFor(color),
          transform: `rotate(${flip ? mid + 90 : mid - 90} ${C} ${C})`});
        label.textContent = String(items[i]);
        label.dataset.fs = fs;
        g.appendChild(label);
      }
      rot.appendChild(g);
      slices.push(g);
    }
    // depth: soft edge shading and a glossy sheen above the slices (under the labels is not needed, they stay crisp)
    root.insertBefore(svg(doc, 'circle', {cx: C, cy: C, r: R, fill: `url(#rzShade${U})`, 'pointer-events': 'none'}), rot.nextSibling);
    root.insertBefore(svg(doc, 'path', {d: `M${C - 150} ${C - 170}A190 190 0 0 1 ${C + 120} ${C - 190}A230 230 0 0 0 ${C - 150} ${C - 170}Z`, fill: 'rgba(255,255,255,.10)', 'pointer-events': 'none'}), rot.nextSibling.nextSibling);
    // LED dots on the bezel (static; they turn white when the result lands)
    const leds = [];
    const LN = 28;
    for (let i = 0; i < LN; i++) {
      const p = pt(i * 360 / LN, RIM - 4.5);
      const led = svg(doc, 'circle', {cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 3.4, fill: i % 2 ? theme.b : theme.a});
      root.appendChild(led); leds.push(led);
    }
    // hub: glossy dome with a ring
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: 60, fill: 'rgba(0,0,0,.35)'}));
    root.appendChild(svg(doc, 'circle', {cx: C, cy: C, r: 54, fill: `url(#rzHub${U})`, stroke: `url(#rzRim${U})`, 'stroke-width': 7}));
    const star = svg(doc, 'text', {x: C, y: C + 2, 'text-anchor': 'middle', 'dominant-baseline': 'central', 'font-size': 40, fill: '#ffffff'});
    star.textContent = '★';
    root.appendChild(star);
    // pointer: modern pin, fixed at the top
    const pointer = svg(doc, 'g', {});
    pointer.appendChild(svg(doc, 'path', {d: 'M260 70C252 55 236 42 236 24A24 24 0 0 1 284 24C284 42 268 55 260 70Z', fill: 'rgba(0,0,0,.35)', transform: 'translate(0 5)'}));
    pointer.appendChild(svg(doc, 'path', {d: 'M260 70C252 55 236 42 236 24A24 24 0 0 1 284 24C284 42 268 55 260 70Z', fill: '#ffffff', stroke: theme.a, 'stroke-width': 4, 'stroke-linejoin': 'round'}));
    pointer.appendChild(svg(doc, 'circle', {cx: 260, cy: 24, r: 9, fill: theme.hub}));
    root.appendChild(pointer);
    stage.appendChild(root);

    // fit labels to the slice length once they are measurable
    const fitLabels = () => {
      if (n > 40) return;
      const avail = R - 22 - 66;
      root.querySelectorAll('text[data-fs]').forEach((t) => {
        try {
          const full = String(t.textContent);
          let len = t.getComputedTextLength();
          if (!len) return;
          if (len > avail) {
            t.setAttribute('font-size', Math.max(14, Math.floor(Number(t.dataset.fs) * avail / len)));
            len = t.getComputedTextLength();
          }
          let s = full;
          while (len > avail && s.length > 2) {s = s.slice(0, -1); t.textContent = s + '…'; len = t.getComputedTextLength();}
        } catch (_) {}
      });
    };
    fitLabels();

    let theta = 0, kick = 0, lastIdx = 0;
    const draw = () => {
      rot.setAttribute('transform', `rotate(${theta.toFixed(3)} ${C} ${C})`);
      pointer.setAttribute('transform', `rotate(${(-22 * Math.min(1, kick)).toFixed(2)} 260 28)`);
    };
    draw();
    const idxAt = (th) => Math.floor((((-th) % 360) + 360) % 360 / a) % n;
    return {
      fit: fitLabels,
      snap() {
        theta = 360 - ((ctx.winnerIndex + 0.5) * a) % 360; draw();
      },
      play(ms, done) {
        const jitter = n > 1 ? (Math.random() - 0.5) * 0.7 : 0;
        const turns = Math.round(clamp(ms / 1000 * 1.4 + 3, 4, 14));
        const target = turns * 360 + (360 - ((ctx.winnerIndex + 0.5 + jitter) * a) % 360);
        const t0 = performance.now();
        lastIdx = idxAt(0);
        return raf(win, (ts, dt) => {
          const t = clamp((performance.now() - t0) / ms, 0, 1);
          theta = target * easeOut(t);
          const idx = idxAt(theta);
          if (idx !== lastIdx) {lastIdx = idx; kick = 1;}
          kick = Math.max(0, kick - dt / 150);
          draw();
          if (t >= 1) {kick = 0; draw(); done(); return false;}
        });
      },
      finish() {
        slices.forEach((g, i) => {g.style.opacity = i === ctx.winnerIndex ? '1' : '0.38';});
        leds.forEach((l) => l.setAttribute('fill', '#ffffff'));
        if (n > 1) {
          const wi = ctx.winnerIndex, p0 = pt(wi * a, R), p1 = pt((wi + 1) * a, R);
          const ring = svg(doc, 'path', {d: `M${C} ${C}L${p0[0].toFixed(2)} ${p0[1].toFixed(2)}A${R} ${R} 0 ${a > 180 ? 1 : 0} 1 ${p1[0].toFixed(2)} ${p1[1].toFixed(2)}Z`, fill: 'none', stroke: '#ffffff', 'stroke-width': 6, 'stroke-linejoin': 'round'});
          rot.appendChild(ring);
        }
      }
    };
  }

  function buildReel(ctx) {
    const {doc, win, items, theme, stage} = ctx;
    const n = items.length, ROW = 100;
    const frame = html(doc, 'div', 'bp3rz-reel');
    const strip = html(doc, 'div', 'bp3rz-reel-strip');
    frame.appendChild(strip);
    frame.appendChild(html(doc, 'div', 'bp3rz-reel-fade t'));
    frame.appendChild(html(doc, 'div', 'bp3rz-reel-fade b'));
    const l1 = html(doc, 'div', 'bp3rz-reel-line'); l1.style.top = '100px';
    const l2 = html(doc, 'div', 'bp3rz-reel-line'); l2.style.top = '197px';
    frame.append(l1, l2);
    stage.appendChild(frame);
    const mL = html(doc, 'div', 'bp3rz-reel-mark', '▶'); mL.style.left = '-4px';
    const mR = html(doc, 'div', 'bp3rz-reel-mark', '◀'); mR.style.right = '-4px';
    stage.append(mL, mR);

    const cv = doc.createElement('canvas').getContext('2d');
    const measure = (str) => {cv.font = '800 40px ' + ctx.fontStack; return cv.measureText(str).width;};
    const rows = [];
    const addRow = (idx) => {
      const row = html(doc, 'div', 'bp3rz-reel-row');
      const item = html(doc, 'div', 'bp3rz-reel-item');
      const txt = html(doc, 'span', 'bp3rz-reel-txt', String(items[idx]));
      const ic = ctx.icons && ctx.icons[idx];
      if (ic) {
        const wrap = html(doc, 'span', 'bp3rz-reel-txt-wrap');
        const im = html(doc, 'img', 'bp3rz-ico'); im.src = ic.src; im.alt = ''; im.style.width = im.style.height = '44px';
        im.addEventListener('error', () => {im.style.display = 'none';});
        wrap.append(im, txt); item.appendChild(wrap);
      } else item.appendChild(txt);
      // long names: shrink to fit the row first, ellipsis only as the last resort
      try {
        const w = measure(String(items[idx]));
        const room = ic ? 400 : 456;
        if (w > room) txt.style.fontSize = Math.max(22, Math.floor(40 * room / w)) + 'px';
      } catch (_) {}
      const c = sliceColor(theme, rows.length, 99);
      item.style.background = c;
      item.style.color = inkFor(c);
      row.appendChild(item);
      strip.appendChild(row);
      rows.push(item);
    };
    // idle = first item centred; the winner row is appended at play()
    addRow((n - 1) % n); addRow(0); addRow(1 % n);
    let y = 0;
    const setY = () => {strip.style.transform = `translate3d(0,${y.toFixed(2)}px,0)`;};
    setY();
    const prepare = (ms) => {
        const L = clamp(Math.round(ms / 1000 * 8.3) + 6, 18, 90), P = L - 3;
        let prev = 1 % n;
        for (let k = 3; k < L + 2; k++) {
          let idx;
          if (k === P) idx = ctx.winnerIndex;
          else {
            idx = Math.floor(Math.random() * n);
            if (n > 1) {let guard = 0; while ((idx === prev || (Math.abs(k - P) <= 1 && idx === ctx.winnerIndex)) && guard++ < 12) idx = Math.floor(Math.random() * n);}
          }
          prev = idx;
          addRow(idx);
        }
        ctx.reelWinnerRow = rows[P];
        return (P - 1) * ROW;
    };
    return {
      snap() {y = -prepare(1500); setY();},
      play(ms, done) {
        const dist = prepare(ms), t0 = performance.now();
        return raf(win, () => {
          const t = clamp((performance.now() - t0) / ms, 0, 1);
          y = -dist * easeOut(t);
          setY();
          if (t >= 1) {done(); return false;}
        });
      },
      finish() {
        const win = ctx.reelWinnerRow || rows[1];
        rows.forEach((r) => {if (r !== win) r.style.opacity = '0.4';});
        win.style.transform = 'scale(1.06)';
        win.style.background = `linear-gradient(135deg,${theme.a},${theme.b})`;
        win.style.color = theme.ink;
        win.style.boxShadow = '0 0 0 4px rgba(255,255,255,.7),0 0 30px ' + theme.b;
      }
    };
  }

  function buildFlip(ctx) {
    const {doc, win, items, theme, stage} = ctx;
    const n = items.length;
    const deck = html(doc, 'div', 'bp3rz-deck');
    const bg2 = html(doc, 'div', 'bp3rz-deck-bg'); bg2.style.transform = 'translate(14px,12px) rotate(4deg)';
    const bg1 = html(doc, 'div', 'bp3rz-deck-bg'); bg1.style.transform = 'translate(-10px,7px) rotate(-3deg)';
    const card = html(doc, 'div', 'bp3rz-card3d');
    const front = html(doc, 'div', 'bp3rz-face front');
    const ftext = html(doc, 'div', 'bp3rz-face-text', '?');
    ftext.style.color = theme.b;
    const fcap = html(doc, 'div', 'bp3rz-face-cap', ctx.total + ' ตัวเลือก');
    fcap.style.color = theme.a;
    front.append(ftext, fcap);
    const back = html(doc, 'div', 'bp3rz-face back');
    const btext = html(doc, 'div', 'bp3rz-face-text', String(items[ctx.winnerIndex]));
    const bcap = html(doc, 'div', 'bp3rz-face-cap', 'ผู้ถูกเลือก');
    const bic = ctx.icons && ctx.icons[ctx.winnerIndex];
    if (bic) {const im = html(doc, 'img', 'bp3rz-ico'); im.src = bic.src; im.alt = ''; im.style.cssText = 'width:34px;height:34px;margin:6px auto 0;'; im.addEventListener('error', () => {im.style.display = 'none';}); bcap.prepend(im);}
    back.append(btext, bcap);
    const fitText = (node, str) => {node.style.fontSize = (str.length <= 8 ? 52 : str.length <= 16 ? 42 : str.length <= 28 ? 32 : 24) + 'px';};
    fitText(btext, String(items[ctx.winnerIndex]));
    card.append(front, back);
    deck.append(bg2, bg1, card);
    stage.appendChild(deck);
    let rotY = 0, rotZ = 0, lift = 0, scale = 1;
    const draw = () => {card.style.transform = `translateY(${lift.toFixed(1)}px) rotateY(${rotY.toFixed(2)}deg) rotateZ(${rotZ.toFixed(2)}deg) scale(${scale.toFixed(3)})`;};
    draw();
    return {
      snap() {rotY = 180; draw();},
      play(ms, done) {
        const shuffleMs = ms * 0.7, flipMs = ms * 0.3;
        fcap.textContent = 'กำลังสับไพ่';
        // tick times: start fast, slow down
        const ticks = [];
        let tt = 0, gap = 70;
        while (tt < shuffleMs) {ticks.push(tt); tt += gap; gap *= 1.16;}
        let ti = 0, kick = 0, last = -1;
        const t0 = performance.now();
        return raf(win, (ts, dt) => {
          const el = performance.now() - t0;
          while (ti < ticks.length && el >= ticks[ti]) {
            let idx = Math.floor(Math.random() * n);
            if (n > 1 && idx === last) idx = (idx + 1) % n;
            last = idx;
            const s = String(items[idx]);
            ftext.textContent = s; fitText(ftext, s);
            kick = 1; rotZ = (Math.random() - 0.5) * 10;
            ti++;
          }
          kick = Math.max(0, kick - dt / 170);
          if (el < shuffleMs) {lift = -16 * kick; rotZ *= 0.9; rotY = Math.sin(el / 55) * 5 * kick;}
          else {
            const t = clamp((el - shuffleMs) / flipMs, 0, 1);
            rotY = 180 * easeOutBack(t); rotZ *= 0.8; lift = -26 * Math.sin(Math.PI * t); scale = 1 + 0.07 * Math.sin(Math.PI * t);
          }
          draw();
          if (el >= ms) {rotY = 180; rotZ = 0; lift = 0; scale = 1; draw(); done(); return false;}
        });
      },
      finish() {
        back.style.boxShadow = '0 0 0 4px rgba(255,255,255,.75),0 0 38px ' + theme.b;
      }
    };
  }

  function buildBox(ctx) {
    const {doc, win, theme, stage} = ctx;
    const root = svg(doc, 'svg', {viewBox: '0 0 420 380', width: '420', height: '380'});
    root.style.cssText = 'display:block;overflow:visible;';
    const defs = svg(doc, 'defs', {});
    const grad = svg(doc, 'radialGradient', {id: 'rzGlow' + ctx.uid, cx: '50%', cy: '50%', r: '50%'});
    grad.append(svg(doc, 'stop', {offset: '0%', 'stop-color': '#ffffff', 'stop-opacity': 0.95}), svg(doc, 'stop', {offset: '45%', 'stop-color': theme.b, 'stop-opacity': 0.6}), svg(doc, 'stop', {offset: '100%', 'stop-color': theme.a, 'stop-opacity': 0}));
    defs.appendChild(grad);
    root.appendChild(defs);
    const glow = svg(doc, 'circle', {cx: 210, cy: 190, r: 170, fill: `url(#rzGlow${ctx.uid})`, opacity: 0});
    root.appendChild(glow);
    root.appendChild(svg(doc, 'ellipse', {cx: 210, cy: 350, rx: 120, ry: 14, fill: 'rgba(0,0,0,.4)'}));
    const dark = (hex) => (lum(hex) > 0.35 ? '#00000033' : '#ffffff22');
    const body = svg(doc, 'g', {});
    body.appendChild(svg(doc, 'rect', {x: 120, y: 190, width: 180, height: 150, rx: 12, fill: theme.a, stroke: 'rgba(11,17,32,.6)', 'stroke-width': 4}));
    body.appendChild(svg(doc, 'rect', {x: 120, y: 190, width: 180, height: 150, rx: 12, fill: dark(theme.a)}));
    body.appendChild(svg(doc, 'rect', {x: 199, y: 190, width: 22, height: 150, fill: theme.b}));
    const q = svg(doc, 'text', {x: 160, y: 300, 'text-anchor': 'middle', 'font-size': 64, 'font-weight': 900, fill: 'rgba(255,255,255,.9)'});
    q.textContent = '?';
    body.appendChild(q);
    const lid = svg(doc, 'g', {});
    lid.appendChild(svg(doc, 'rect', {x: 105, y: 146, width: 210, height: 52, rx: 12, fill: theme.b, stroke: 'rgba(11,17,32,.6)', 'stroke-width': 4}));
    lid.appendChild(svg(doc, 'rect', {x: 199, y: 146, width: 22, height: 52, fill: theme.a}));
    lid.appendChild(svg(doc, 'ellipse', {cx: 180, cy: 134, rx: 28, ry: 16, fill: theme.a, stroke: 'rgba(11,17,32,.6)', 'stroke-width': 3, transform: 'rotate(-22 180 134)'}));
    lid.appendChild(svg(doc, 'ellipse', {cx: 240, cy: 134, rx: 28, ry: 16, fill: theme.a, stroke: 'rgba(11,17,32,.6)', 'stroke-width': 3, transform: 'rotate(22 240 134)'}));
    lid.appendChild(svg(doc, 'circle', {cx: 210, cy: 140, r: 11, fill: theme.b, stroke: 'rgba(11,17,32,.6)', 'stroke-width': 3}));
    const whole = svg(doc, 'g', {});
    whole.append(body, lid);
    root.appendChild(whole);
    stage.appendChild(root);
    let shake = 0, scl = 1, lidY = 0, lidR = 0, lidO = 1, glowO = 0, glowS = 0.2, bodyO = 1;
    const draw = () => {
      whole.setAttribute('transform', `translate(210 340) rotate(${shake.toFixed(2)}) scale(${scl.toFixed(3)}) translate(-210 -340)`);
      lid.setAttribute('transform', `translate(210 172) translate(0 ${lidY.toFixed(1)}) rotate(${lidR.toFixed(1)}) translate(-210 -172)`);
      lid.setAttribute('opacity', lidO.toFixed(2));
      body.setAttribute('opacity', bodyO.toFixed(2));
      glow.setAttribute('opacity', glowO.toFixed(2));
      glow.setAttribute('transform', `translate(210 190) scale(${glowS.toFixed(3)}) translate(-210 -190)`);
    };
    draw();
    return {
      snap() {lidY = -190; lidR = 34; lidO = 0; glowO = 0.6; glowS = 1.3; bodyO = 0.7; draw();},
      play(ms, done) {
        const shakeMs = ms * 0.68, popMs = Math.max(500, ms * 0.32);
        const t0 = performance.now();
        let popped = false;
        return raf(win, () => {
          const el = performance.now() - t0;
          if (el < shakeMs) {
            const p = el / shakeMs;
            shake = Math.sin(el / (46 - 20 * p)) * (2 + 9 * p);
            scl = 1 + 0.045 * Math.sin(el / 90) * p;
          } else {
            if (!popped) {popped = true; ctx.onPop && ctx.onPop();}
            const t = clamp((el - shakeMs) / popMs, 0, 1), e = pow(3)(t);
            shake *= 0.7; scl = 1 + 0.08 * Math.sin(Math.PI * Math.min(1, t * 1.5));
            lidY = -190 * e; lidR = 34 * e; lidO = 1 - clamp((t - 0.35) / 0.65, 0, 1);
            glowO = Math.min(0.95, t * 2.2) * (1 - 0.35 * t); glowS = 0.2 + 1.1 * e;
            bodyO = 1 - 0.3 * t;
          }
          draw();
          if (el >= ms) {shake = 0; scl = 1; draw(); done(); return false;}
        });
      },
      finish() {}
    };
  }
  const BUILDERS = {wheel: buildWheel, reel: buildReel, flip: buildFlip, box: buildBox};

  let UID = 0;
  /* ---------- controller ---------- */
  function create(host, data, opts) {
    opts = opts || {};
    const doc = host.ownerDocument, win = doc.defaultView || window;
    injectStyle(doc);
    const uid = ++UID;
    const position = opts.position || 'fixed';
    let items = (Array.isArray(data.items) && data.items.length ? data.items : ['ตัวเลือก 1', 'ตัวเลือก 2']).map(String);
    let settings = normalize(data.settings);
    let title = String(data.title || 'สุ่มกิจกรรม');
    const cleanIcons = (arr, n) => Array.from({length: n}, (_, i) => {const x = Array.isArray(arr) ? arr[i] : null; return x && x.src ? {src: String(x.src), name: String(x.name || '')} : null;});
    let icons = cleanIcons(data.icons, items.length);
    let winnerIndex = Number.isInteger(data.winnerIndex) && data.winnerIndex >= 0 && data.winnerIndex < items.length ? data.winnerIndex : Math.max(0, items.indexOf(String(data.winner)));
    if (winnerIndex < 0) winnerIndex = 0;
    const keepVisible = !!opts.keepVisible;
    const L = Object.assign({winner: 'ผลการสุ่ม', live: 'ผลการสุ่ม', done: 'ได้ผลแล้ว', idle: 'พร้อมสุ่ม', running: 'กำลังสุ่ม...'}, opts.labels || {});
    const root = html(doc, 'div', 'bp3rz-root');
    if (opts.id) root.id = opts.id;
    const card = html(doc, 'div', 'bp3rz-card');
    const titleBox = html(doc, 'div', 'bp3rz-title');
    const titleText = html(doc, 'div', 'bp3rz-title-text');
    const sub = html(doc, 'div', 'bp3rz-sub', L.idle);
    titleBox.append(titleText, sub);
    const stage = html(doc, 'div', 'bp3rz-stage');
    const winner = html(doc, 'div', 'bp3rz-winner');
    const wlabel = html(doc, 'div', 'bp3rz-winner-label', L.winner);
    const wname = html(doc, 'div', 'bp3rz-winner-name');
    const wrow = html(doc, 'div', 'bp3rz-winner-row');
    const wico = html(doc, 'img', 'bp3rz-ico');
    wico.alt = ''; wico.style.display = 'none';
    wico.addEventListener('error', () => {wico.style.display = 'none';});
    wrow.append(wico, wname);
    winner.append(wlabel, wrow);
    stage.setAttribute('aria-hidden', 'true');
    const live = html(doc, 'div', 'bp3rz-sr');
    live.setAttribute('role', 'status'); live.setAttribute('aria-live', 'polite'); live.setAttribute('aria-atomic', 'true');
    root.setAttribute('role', 'region');
    card.append(titleBox, stage, winner, live);
    root.appendChild(card);
    host.appendChild(root);

    let impl = null, stopAnim = null, holdTimer = null, outTimer = null, running = false, finished = false, destroyed = false;
    const api = {root, demo: !!opts.keepVisible};
    // text widths depend on the font: rebuild once it arrives, but never while an animation runs
    const refreshFont = () => loadFont(doc, settings.font).then(() => {if (!destroyed && !running && !finished) buildStage();});
    api.fontReady = refreshFont();

    function isCalm() {
      if (settings.reduce_motion) return true;
      return false; // OS-level reduced-motion no longer skips the spin; only the explicit option does
    }
    api.isCalm = isCalm;
    function applyTheme() {
      const th = THEMES[settings.color_theme];
      root.style.setProperty('--rz-a', th.a);
      root.style.setProperty('--rz-b', th.b);
      root.style.setProperty('--rz-ink', th.ink);
      root.style.fontFamily = fontStack(settings.font);
    }
    function applyLayout() {
      if (position === 'static') {
        root.style.position = 'relative';
        root.style.zIndex = '0';
        root.style.transformOrigin = 'top left';
        root.style.transform = `scale(${(opts.fitScale || 1)})`;
        return;
      }
      const a = ANCHORS[settings.anchor];
      root.style.position = position;
      root.style.top = root.style.left = root.style.right = root.style.bottom = '';
      Object.assign(root.style, a[0]);
      root.style.transformOrigin = a[2];
      root.style.transform = `${a[1]} translate(${settings.offset_x}px,${settings.offset_y}px) scale(${(settings.scale / 100).toFixed(4)})`;
    }
    function buildStage() {
      stage.textContent = '';
      const size = STAGE_SIZE[settings.style];
      stage.style.width = size[0] + 'px';
      stage.style.height = size[1] + 'px';
      root.dataset.randomizerMode = settings.style;
      titleText.textContent = title;
      root.setAttribute('aria-label', 'การสุ่ม ' + title);
      const ctx = {fontStack: fontStack(settings.font), icons, total: Math.max(items.length, parseInt(data.total, 10) || 0), doc, win, items, theme: THEMES[settings.color_theme], stage, winnerIndex, uid, onPop: () => confetti(doc, stage, THEMES[settings.color_theme])};
      impl = BUILDERS[settings.style](ctx);
      api.ctx = ctx;
    }
    function showWinner() {
      const text = String(items[winnerIndex]);
      const ic = icons[winnerIndex];
      if (ic) {wico.src = ic.src; wico.style.width = wico.style.height = (text.length <= 20 ? 50 : 38) + 'px'; wico.style.display = 'block';} else wico.style.display = 'none';
      wname.textContent = text;
      wname.style.fontSize = (text.length <= 10 ? 46 : text.length <= 20 ? 38 : text.length <= 34 ? 30 : 24) + 'px';
      winner.classList.add('show');
      sub.textContent = L.done;
      sub.classList.add('done');
      live.textContent = L.live + ' ' + title + ' คือ ' + text + (ic && ic.name ? ' จาก ' + ic.name : '');
    }
    function scheduleHide() {
      if (keepVisible) return;
      holdTimer = setTimeout(() => api.hide(), settings.hold * 1000);
    }
    api.show = () => {
      applyTheme(); applyLayout(); buildStage();
      win.requestAnimationFrame(() => {root.classList.add('on'); impl.fit && impl.fit();});
      return api;
    };
    api.start = () => {
      if (running || destroyed) return api;
      running = true; finished = false;
      winner.classList.remove('show');
      live.textContent = '';
      sub.classList.remove('done'); sub.textContent = L.running;
      const calm = isCalm();
      root.classList.toggle('calm', calm);
      const complete = () => {
        stopAnim = null; running = false; finished = true;
        impl.finish();
        showWinner();
        if (!calm) confetti(doc, stage, THEMES[settings.color_theme]);
        scheduleHide();
        opts.onDone && opts.onDone(api);
      };
      if (calm && impl.snap) {
        // reduced motion: no spinning, jump straight to the result state
        impl.snap();
        stopAnim = null;
        holdTimer = setTimeout(complete, 250);
        return api;
      }
      stopAnim = impl.play(settings.spin_duration * 1000, complete);
      return api;
    };
    // live layout change: transform only, never restarts the animation
    api.setLayout = (partial) => {
      if (destroyed || !partial) return api;
      const merged = Object.assign({}, partial);
      const next = normalize(Object.assign({style: settings.style, color_theme: settings.color_theme, duration: settings.hold, spin_duration: settings.spin_duration,
        scale: settings.scale, offset_x: settings.offset_x, offset_y: settings.offset_y, anchor: settings.anchor}, merged));
      settings.scale = next.scale; settings.offset_x = next.offset_x; settings.offset_y = next.offset_y; settings.anchor = next.anchor;
      applyLayout();
      return api;
    };
    // look change (style/theme/items/title); only while idle, an animation in flight is never interrupted
    api.setLook = (d) => {
      if (destroyed || !d || running) return api;
      if (Array.isArray(d.items) && d.items.length) {
        items = d.items.map(String);
        icons = cleanIcons(d.icons, items.length);
        winnerIndex = Number.isInteger(d.winnerIndex) && d.winnerIndex >= 0 && d.winnerIndex < items.length ? d.winnerIndex : Math.max(0, items.indexOf(String(d.winner)));
        if (winnerIndex < 0) winnerIndex = 0;
      }
      if (d.title !== undefined) title = String(d.title || 'สุ่มกิจกรรม');
      if (d.settings) {
        const merged = normalize(Object.assign({}, settings, {mode: undefined}, d.settings, {duration: d.settings.duration !== undefined ? d.settings.duration : settings.hold}));
        settings = Object.assign(settings, merged);
      }
      finished = false; winner.classList.remove('show'); sub.classList.remove('done'); sub.textContent = L.idle;
      applyTheme(); applyLayout(); buildStage();
      api.fontReady = refreshFont();
      return api;
    };
    // abort a running animation and return to the idle state (used by the settings preview)
    api.stop = () => {
      if (destroyed) return api;
      if (stopAnim) {try {stopAnim();} catch (_) {} stopAnim = null;}
      clearTimeout(holdTimer);
      running = false;
      return api.setLook({});
    };
    api.setFit = (s) => {opts.fitScale = s; applyLayout();};
    api.naturalSize = () => ({w: root.offsetWidth, h: root.offsetHeight});
    api.hide = () => {
      if (destroyed) return;
      clearTimeout(holdTimer);
      root.classList.remove('on'); root.classList.add('out');
      outTimer = setTimeout(() => api.destroy(), 420);
    };
    api.destroy = () => {
      if (destroyed) return;
      destroyed = true;
      clearTimeout(holdTimer); clearTimeout(outTimer);
      if (stopAnim) {try {stopAnim();} catch (_) {} stopAnim = null;}
      root.remove();
    };
    Object.defineProperty(api, 'running', {get: () => running});
    Object.defineProperty(api, 'finished', {get: () => finished});
    Object.defineProperty(api, 'destroyed', {get: () => destroyed});
    Object.defineProperty(api, 'settings', {get: () => Object.assign({}, settings)});
    return api;
  }

  /* One manager per host page. payload.action: spin (default) | demo_start | demo_layout | demo_stop */
  function createManager(cfg) {
    let ctl = null, demoTimer = null;
    const clear = () => {clearTimeout(demoTimer); if (ctl) {ctl.destroy(); ctl = null;}};
    // a demo that stops receiving updates (app closed, link lost) removes itself so it can never stay on air
    const touchDemo = () => {clearTimeout(demoTimer); demoTimer = setTimeout(() => clear(), 60000);};
    return {
      get current() {return ctl;},
      clear,
      handle(payload) {
        if (!payload) return null;
        const host = cfg.getHost && cfg.getHost();
        const action = payload.action || 'spin';
        if (action === 'demo_stop') {clear(); return null;}
        if (!host) return null;
        const opts = {position: cfg.position || 'fixed', id: cfg.id};
        if (action === 'demo_layout') {
          if (ctl && !ctl.destroyed && ctl.demo) {ctl.setLayout(payload.settings); ctl.setLook(payload); touchDemo();}
          return ctl;
        }
        if (action === 'demo_start') {
          clear();
          ctl = create(host, payload, Object.assign({keepVisible: true}, opts)).show();
          touchDemo();
          return ctl;
        }
        clear();
        ctl = create(host, payload, Object.assign({keepVisible: !!payload.demo}, opts)).show().start();
        return ctl;
      }
    };
  }

  window.BP3RandomizerVisual = {version: 3, FONTS, loadFont, STYLES, THEMES, ANCHORS, create, createManager, normalize, contrast, inkFor};
})();
