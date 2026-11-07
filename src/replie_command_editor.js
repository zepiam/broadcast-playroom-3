/* Replie: command list, defaults panel and the create/edit dialog. Commands keep the original ticker/image/combo payload and renderer. */
(() => {
  'use strict';
  const doc = () => getToolDocument('replie');
  const CMD_KEY = 'bp3_replie_commands', SET_KEY = 'bp3_replie_settings';
  const ZONES = [['top-left', 'บนซ้าย'], ['top', 'บนกลาง'], ['top-right', 'บนขวา'], ['left', 'ซ้าย'], ['center', 'กลาง'], ['right', 'ขวา'], ['bottom-left', 'ล่างซ้าย'], ['bottom', 'ล่างกลาง'], ['bottom-right', 'ล่างขวา']];
  const ZNAME = Object.fromEntries(ZONES);
  // preset positions (percent of the screen) used by the 3x3 picker of the editor
  const PX = [15, 50, 85], PY = [12, 50, 88];
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const num = (v, d) => (Number.isFinite(Number(v)) && v !== '' && v !== null ? Number(v) : d);

  /* ---------- default settings (used by simple commands only) ---------- */
  const ANCHOR_XY = {'top-left': [5, 10], 'top': [50, 10], 'top-right': [95, 10], 'left': [5, 50], 'center': [50, 50], 'right': [95, 50], 'bottom-left': [5, 90], 'bottom': [50, 90], 'bottom-right': [95, 90]};
  const THEMES = [
    ['default', 'ฟ้าเดิม', 'rgb(4,9,24)', '#38bdf8', '#f8fafc'], ['neon', 'นีออน', 'rgb(18,3,31)', '#ff3df2', '#ffffff'],
    ['gold', 'ทอง', 'rgb(27,20,5)', '#fbbf24', '#fff7d6'], ['emerald', 'เขียว', 'rgb(4,23,15)', '#34d399', '#eafff6'],
    ['sunset', 'ส้ม', 'rgb(42,15,10)', '#fb923c', '#fff1e6'], ['violet', 'ม่วง', 'rgb(22,10,46)', '#a78bfa', '#f5f0ff'],
    ['light', 'ขาว', '#ffffff', '#cbd5e1', '#0f172a'], ['glass', 'กระจก', 'rgba(120,130,150,.55)', 'rgba(255,255,255,.6)', '#ffffff']];
  const THEME_IDS = THEMES.map(t => t[0]);
  const nearestAnchor = (x, y) => {let best = 'bottom-right', bd = 1e9; for (const [k, v] of Object.entries(ANCHOR_XY)) {const d = (v[0] - x) ** 2 + (v[1] - y) ** 2; if (d < bd) {bd = d; best = k;}} return best;};
  function loadSettings() {
    let s = {};
    try {s = JSON.parse(localStorage.getItem(SET_KEY)) || {};} catch (_) {}
    const anchor = ZNAME[s.anchor] ? s.anchor : 'bottom-right', base = ANCHOR_XY[anchor];
    const pos_x = clamp(num(s.pos_x, base[0]), 0, 100), pos_y = clamp(num(s.pos_y, base[1]), 0, 100);
    return {duration: clamp(num(s.duration, 4), 1, 60), scale: clamp(num(s.scale, 100), 50, 200), anchor: nearestAnchor(pos_x, pos_y), pos_x, pos_y, theme: THEME_IDS.includes(s.theme) ? s.theme : 'default', isLoop: !!s.isLoop};
  }
  function saveSettings(s) {try {localStorage.setItem(SET_KEY, JSON.stringify(s));} catch (_) {}}
  const commands = () => window._replieCommands || (window._replieCommands = {});
  function saveCommands() {try {localStorage.setItem(CMD_KEY, JSON.stringify(commands()));} catch (_) {}}

  function announce(text) {
    const node = doc().getElementById('rpAnnounce');
    if (!node) return;
    node.textContent = '';
    setTimeout(() => {node.textContent = text;}, 30);
  }
  let savedTimer = 0;
  function savedNote() {
    const node = doc().getElementById('rpSaveStatus');
    if (!node) return;
    node.textContent = 'บันทึกแล้ว';
    clearTimeout(savedTimer);
    savedTimer = setTimeout(() => {node.textContent = 'การตั้งค่าบันทึกให้อัตโนมัติ';}, 1800);
  }

  /* ---------- show on screen (same payload as before) ---------- */
  window.demoReplieAction = function(cmd, text, emotion) {
    const command = commands()[cmd] || {};
    const s = loadSettings();
    if (demoOn) setDemo(false, 'หยุดตัวอย่างเพราะมีการส่งคำสั่งขึ้นจอ');
    window._rpPanelTest = true;
    window.BP3_BUS?.emit('REPLIE_ACTION', {...command, duration: s.duration, scale: s.scale, anchor: s.anchor, pos_x: s.pos_x, pos_y: s.pos_y, theme: s.theme, isLoop: s.isLoop, cmd, text: text || command.text, emotion: emotion || command.emotion});
  };
  window.saveReplieSettings = function() {saveCommands(); saveSettings(loadSettings()); if (typeof showToast === 'function') showToast('บันทึกการตั้งค่า Replie แล้ว');};

  /* ---------- helpers for the cards ---------- */
  function zoneOf(x, y) {
    const c = x < 34 ? 0 : x < 67 ? 1 : 2, r = y < 34 ? 0 : y < 67 ? 1 : 2;
    return ZONES[r * 3 + c][1];
  }
  function describe(name, rule) {
    const p = rule.legacyPayload;
    const mine = !!p;
    let hasText, hasImage, text = '', where = '';
    if (mine) {
      const t = p.ticker || {}, i = p.image || {};
      hasText = !!t.enabled; hasImage = !!i.enabled;
      text = hasText ? (t.text || t.title || '') : '';
      const parts = [];
      if (hasText) parts.push((hasImage ? 'ข้อความ ' : '') + zoneOf(num(t.pos_x, 50), num(t.pos_y, 88)));
      if (hasImage) parts.push((hasText ? 'รูป ' : '') + zoneOf(num(i.pos_x, 85), num(i.pos_y, 50)));
      where = parts.join(' · ');
    } else {
      hasText = !!rule.text; hasImage = !!rule.imageUrl; text = rule.text || '';
      where = zoneOf(loadSettings().pos_x, loadSettings().pos_y);
    }
    const kind = hasText && hasImage ? 'ข้อความ + รูป' : hasImage ? 'รูปภาพ' : 'ข้อความ';
    const seconds = mine ? num(p.duration_sec, num(rule.duration, 8)) : loadSettings().duration;
    const loop = mine ? !!p.is_loop : loadSettings().isLoop;
    const image = hasImage ? (mine ? (p.image && p.image.image_url) : rule.imageUrl) : '';
    return {mine, kind, text, where, seconds, loop, image, hasImage, hasText};
  }

  /* ---------- command list ---------- */
  let pendingDelete = null, focusAfter = null;
  function el(d, tag, cls, text) {const n = d.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n;}

  function renderList() {
    const d = doc(), list = d.getElementById('rpList');
    if (!list) return;
    const entries = Object.entries(commands());
    const countNode = d.getElementById('rpCount');
    if (countNode) countNode.textContent = entries.length ? '(' + entries.length + ' คำสั่ง)' : '';
    const empty = d.getElementById('rpEmpty');
    if (empty) empty.hidden = entries.length > 0;
    // the defaults box only matters for simple commands: fold it away when there are none
    const simple = entries.filter(([, r]) => !r.legacyPayload).length;
    const det = d.getElementById('rpDefaults'), dc = d.getElementById('rpDefCount');
    if (det) {
      if (det.dataset.simple !== String(simple)) {det.open = simple > 0 || entries.length === 0; det.dataset.simple = String(simple);}
      if (dc) dc.textContent = entries.length ? '(ใช้กับ ' + simple + ' คำสั่ง)' : '';
    }
    list.replaceChildren();
    for (const [name, rule] of entries) {
      const info = describe(name, rule);
      const on = rule.enabled !== false;
      const li = el(d, 'li', 'rp-item' + (on ? '' : ' off'));
      li.dataset.cmd = name;
      const top = el(d, 'div', 'rp-item-top');
      if (info.image) {
        const img = el(d, 'img', 'rp-thumb'); img.src = info.image; img.alt = ''; img.loading = 'lazy';
        img.addEventListener('error', () => {const f = el(d, 'span', 'rp-thumb none', '🖼️'); f.setAttribute('aria-hidden', 'true'); img.replaceWith(f);});
        top.append(img);
      } else {
        const f = el(d, 'span', 'rp-thumb none', info.hasText ? '💬' : '🖼️'); f.setAttribute('aria-hidden', 'true'); top.append(f);
      }
      const box = el(d, 'div', 'rp-info');
      const row = el(d, 'div', 'rp-cmdrow');
      row.append(el(d, 'h4', 'rp-cmd', name), el(d, 'span', 'rp-badge', info.kind), el(d, 'span', 'rp-badge' + (info.mine ? ' mine' : ''), info.mine ? 'ตั้งค่าเอง' : 'ใช้ค่าเริ่มต้น'));
      if (!on) row.append(el(d, 'span', 'rp-badge state-off', 'ปิดอยู่'));
      box.append(row);
      box.append(el(d, 'p', 'rp-text' + (info.text ? '' : ' empty'), info.text ? info.text : (info.hasImage ? 'แสดงเฉพาะรูปภาพ' : 'ยังไม่มีข้อความ')));
      const meta = el(d, 'dl', 'rp-meta');
      for (const [k, v] of [['แสดงบนจอ', info.loop ? 'ค้างไว้' : info.seconds + ' วินาที'], ['ตำแหน่ง', info.where || '-'], ['กันสแปม', (num(rule.cooldown, 0) > 0 ? num(rule.cooldown, 0) + ' วินาที' : 'ไม่จำกัด')]]) {
        const g = el(d, 'div'); g.append(el(d, 'dt', '', k + ':'), el(d, 'dd', '', v)); meta.append(g);
      }
      box.append(meta);
      top.append(box);
      li.append(top);

      if (pendingDelete === name) {
        const c = el(d, 'div', 'rp-confirm');
        c.setAttribute('role', 'group'); c.setAttribute('aria-label', 'ยืนยันการลบ ' + name);
        const yes = el(d, 'button', 'rp-btn danger solid', 'ยืนยันลบ ' + name); yes.type = 'button';
        const no = el(d, 'button', 'rp-btn', 'ไม่ลบ'); no.type = 'button';
        yes.onclick = () => {delete commands()[name]; pendingDelete = null; saveCommands(); focusAfter = '#btnRpNew'; renderList(); announce('ลบคำสั่ง ' + name + ' แล้ว');};
        no.onclick = () => {pendingDelete = null; focusAfter = '[data-del="' + name + '"]'; renderList();};
        c.append(el(d, 'span', '', 'ลบคำสั่งนี้ถาวรใช่ไหม'), yes, no);
        li.append(c);
        focusAfter = focusAfter || 'confirm';
        li._confirmYes = yes;
      } else {
        const acts = el(d, 'div', 'rp-actions');
        const sw = el(d, 'button', 'rp-switch'); sw.type = 'button'; sw.setAttribute('role', 'switch'); sw.setAttribute('aria-checked', String(on));
        sw.setAttribute('aria-label', 'เปิดใช้คำสั่ง ' + name);
        sw.append(el(d, 'span', 'track'), el(d, 'span', '', on ? 'เปิดใช้' : 'ปิดอยู่'));
        sw.onclick = () => {rule.enabled = rule.enabled === false; saveCommands(); focusAfter = '[data-sw="' + name + '"]'; renderList(); announce('คำสั่ง ' + name + (rule.enabled === false ? ' ปิดแล้ว' : ' เปิดแล้ว'));};
        sw.dataset.sw = name;
        const test = el(d, 'button', 'rp-btn', '▶ ทดสอบบนจอ'); test.type = 'button'; test.setAttribute('aria-label', 'ทดสอบคำสั่ง ' + name + ' บนจอ');
        test.onclick = () => {window.demoReplieAction(name, rule.text, rule.emotion); announce('ส่งคำสั่ง ' + name + ' ไปแสดงบนจอ OBS แล้ว');};
        const edit = el(d, 'button', 'rp-btn', '✏️ แก้ไข'); edit.type = 'button'; edit.setAttribute('aria-label', 'แก้ไขคำสั่ง ' + name);
        edit.dataset.edit = name; edit.onclick = () => window.editReplieCommand(name);
        const del = el(d, 'button', 'rp-btn danger', 'ลบ'); del.type = 'button'; del.setAttribute('aria-label', 'ลบคำสั่ง ' + name);
        del.dataset.del = name; del.onclick = () => {pendingDelete = name; focusAfter = 'confirm'; renderList();};
        acts.append(sw, test, edit, del);
        li.append(acts);
      }
      list.append(li);
    }
    // keep keyboard focus where the person was
    if (focusAfter) {
      const target = focusAfter === 'confirm' ? [...list.querySelectorAll('.rp-confirm button')][0] : (list.ownerDocument.querySelector(focusAfter));
      focusAfter = null;
      try {target && target.focus();} catch (_) {}
    }
  }
  window.renderReplieCommands = renderList;

  /* ---------- defaults panel: stream locator, theme, live demo ---------- */
  let demoOn = false, demoKeep = 0, demoPend = false, panelApi = null;
  const DEMO_TEXT = 'ตัวอย่างข้อความ Replie';
  function demoPayload(noAnim) {
    const s = loadSettings();
    return {demo: true, noAnim: !!noAnim, cmd: '__rp_demo', text: DEMO_TEXT, title: '', duration: s.duration, scale: s.scale, anchor: s.anchor, pos_x: s.pos_x, pos_y: s.pos_y, theme: s.theme, isLoop: true};
  }
  function demoStatus(msg) {const n = doc().getElementById('rpDemoStatus'); if (n) n.textContent = msg;}
  function setDemo(on, msg) {
    if (on === demoOn) return;
    demoOn = on;
    const d = doc(), b = d.getElementById('rpDemoBtn');
    if (b) {b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.textContent = on ? 'หยุดตัวอย่างบนจอ OBS' : 'แสดงตัวอย่างจริงบนจอ OBS';}
    clearInterval(demoKeep);
    if (on) {
      window._rpPanelTest = true;
      window.BP3_BUS?.emit('REPLIE_ACTION', demoPayload(false));
      demoKeep = setInterval(() => {if (demoOn) window.BP3_BUS?.emit('REPLIE_ACTION', demoPayload(true));}, 5000);
      demoStatus('กำลังแสดงบนจอ OBS ลองลากกรอบ ย่อ/ขยาย หรือเปลี่ยนธีมได้เลย เห็นผลทันที กดปุ่มอีกครั้งเมื่อพอใจ');
    } else {
      window.BP3_BUS?.emit('REPLIE_DISMISS', {});
      window._rpPanelTest = false;
      demoStatus(msg || 'ปิดอยู่ เปิดแล้วจะเห็นข้อความตัวอย่างบนจอ OBS ทันที และปรับตำแหน่ง ขนาด ธีมได้แบบสด');
    }
  }
  function demoSync() {
    if (!demoOn || demoPend) return;
    demoPend = true;
    setTimeout(() => {demoPend = false; if (demoOn) window.BP3_BUS?.emit('REPLIE_ACTION', demoPayload(true));}, 90);
  }
  let dlgLiveStop = null;
  window.BP3ReplieStopDemo = function() {if (demoOn) setDemo(false, 'ปิดอัตโนมัติเพราะปิดหน้าต่าง Replie แล้ว'); if (dlgLiveStop) dlgLiveStop();};
  window.addEventListener('pagehide', () => {if (demoOn) window.BP3_BUS?.emit('REPLIE_DISMISS', {});});

  function bindDefaults() {
    const d = doc(), loc = d.getElementById('rpLocator');
    if (!loc || loc.dataset.bound) return;
    loc.dataset.bound = '1';
    const s = loadSettings();
    const rect = d.getElementById('rpLocRect'), handle = d.getElementById('rpLocHandle'), themesBox = d.getElementById('rpThemes');
    const scale = d.getElementById('rpScale'), out = d.getElementById('rpScaleOut'), dur = d.getElementById('rpDuration'), loop = d.getElementById('rpLoop');
    const gv = loc.querySelector('.rp-guide.v'), gh = loc.querySelector('.rp-guide.h'), posText = d.getElementById('rpPosText');
    const BASE_W = 0.30, BASE_H = 0.13; // box size at 100% as a share of the screen
    let cur = {...s};
    const wOf = () => Math.min(0.96, BASE_W * cur.scale / 100), hOf = () => Math.min(0.96, BASE_H * cur.scale / 100);
    const persist = (silent) => {cur.anchor = nearestAnchor(cur.pos_x, cur.pos_y); saveSettings(cur); if (!silent) {savedNote(); renderList();} demoSync();};
    function paint() {
      const w = wOf(), h = hOf(), th = THEMES.find(t => t[0] === cur.theme) || THEMES[0];
      rect.style.width = (w * 100) + '%'; rect.style.height = (h * 100) + '%';
      rect.style.left = (cur.pos_x / 100 * (1 - w) * 100) + '%'; rect.style.top = (cur.pos_y / 100 * (1 - h) * 100) + '%';
      rect.style.background = th[2]; rect.style.borderColor = th[3]; rect.style.color = th[4];
      rect.style.fontSize = Math.max(8, 11 * cur.scale / 100) + 'px';
      rect.setAttribute('aria-valuetext', 'แนวนอน ' + Math.round(cur.pos_x) + ' เปอร์เซ็นต์ แนวตั้ง ' + Math.round(cur.pos_y) + ' เปอร์เซ็นต์');
      scale.value = cur.scale; out.textContent = cur.scale + '%';
      if (posText) posText.textContent = 'แนวนอน ' + Math.round(cur.pos_x) + '% · แนวตั้ง ' + Math.round(cur.pos_y) + '%';
      for (const b of themesBox.children) b.setAttribute('aria-checked', b.dataset.id === cur.theme ? 'true' : 'false');
    }
    // themes
    for (const [id, label, bg, bd, tx] of THEMES) {
      const b = el(d, 'button', 'rp-theme'); b.type = 'button'; b.dataset.id = id; b.setAttribute('role', 'radio'); b.setAttribute('aria-label', 'ธีม ' + label);
      const sw = el(d, 'span', 'sw', 'Aa'); sw.style.background = bg; sw.style.borderColor = bd; sw.style.color = tx;
      b.append(sw, el(d, 'span', '', label));
      b.onclick = () => {cur.theme = id; paint(); persist(); announce('เลือกธีม ' + label);};
      themesBox.append(b);
    }
    // drag / resize
    const snap = (v, pts, tol) => {for (const p of pts) if (Math.abs(v - p) <= tol) return [p, true]; return [v, false];};
    function guides(sx, sy) {gv.classList.toggle('on', sx); gh.classList.toggle('on', sy);}
    function startDrag(ev, mode) {
      ev.preventDefault(); ev.stopPropagation();
      try {rect.focus({preventScroll: true});} catch (_) {}
      const l = loc.getBoundingClientRect(), x0 = ev.clientX, y0 = ev.clientY, c0 = {...cur}, w0 = wOf(), h0 = hOf();
      try {(mode === 'move' ? rect : handle).setPointerCapture(ev.pointerId);} catch (_) {}
      rect.classList.add('dragging');
      const move = e => {
        const dx = (e.clientX - x0) / l.width, dy = (e.clientY - y0) / l.height;
        if (mode === 'move') {
          const rx = Math.max(0.0001, 1 - w0), ry = Math.max(0.0001, 1 - h0);
          let px = clamp(c0.pos_x + dx / rx * 100, 0, 100), py = clamp(c0.pos_y + dy / ry * 100, 0, 100);
          const tx = 14 / (l.width * rx) * 100, ty = 14 / (l.height * ry) * 100;
          const free = e.ctrlKey || e.metaKey;
          const [sx, hx] = free ? [px, false] : snap(px, [0, 50, 100], tx), [sy, hy] = free ? [py, false] : snap(py, [0, 50, 100], ty);
          cur.pos_x = Math.round(sx * 1000) / 1000; cur.pos_y = Math.round(sy * 1000) / 1000;
          guides(hx && sx === 50, hy && sy === 50);
        } else {
          const nw = w0 + dx; // corner pull changes the width; height follows
          cur.scale = clamp(Math.round(nw / BASE_W * 100 / 5) * 5, 50, 200);
        }
        paint(); persist(true);
      };
      const up = () => {rect.classList.remove('dragging'); guides(false, false); rect.removeEventListener('pointermove', move); handle.removeEventListener('pointermove', move); rect.removeEventListener('pointerup', up); handle.removeEventListener('pointerup', up); rect.removeEventListener('pointercancel', up); handle.removeEventListener('pointercancel', up); persist();};
      const t = mode === 'move' ? rect : handle;
      t.addEventListener('pointermove', move); t.addEventListener('pointerup', up); t.addEventListener('pointercancel', up);
    }
    rect.addEventListener('pointerdown', e => {if (e.target === handle) return; startDrag(e, 'move');});
    handle.addEventListener('pointerdown', e => startDrag(e, 'size'));
    rect.addEventListener('keydown', e => {
      const px = e.shiftKey ? 10 : 1, k = e.key;
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(k)) return;
      e.preventDefault();
      const stx = px * 100 / (1920 * Math.max(0.0001, 1 - wOf())), sty = px * 100 / (1080 * Math.max(0.0001, 1 - hOf()));
      if (k === 'ArrowLeft') cur.pos_x = clamp(cur.pos_x - stx, 0, 100); if (k === 'ArrowRight') cur.pos_x = clamp(cur.pos_x + stx, 0, 100);
      if (k === 'ArrowUp') cur.pos_y = clamp(cur.pos_y - sty, 0, 100); if (k === 'ArrowDown') cur.pos_y = clamp(cur.pos_y + sty, 0, 100);
      paint(); persist();
    });
    d.getElementById('rpPosReset').onclick = () => {cur.pos_x = 50; cur.pos_y = 90; paint(); persist(); announce('จัดตำแหน่งกลางล่างแล้ว');};
    // scale / duration / loop / demo
    scale.value = cur.scale; dur.value = cur.duration; loop.checked = cur.isLoop;
    scale.addEventListener('input', () => {cur.scale = clamp(num(scale.value, 100), 50, 200); paint(); persist(true);});
    scale.addEventListener('change', () => {cur.scale = clamp(num(scale.value, 100), 50, 200); paint(); persist();});
    dur.addEventListener('change', () => {dur.value = cur.duration = clamp(num(dur.value, 4), 1, 60); persist();});
    loop.addEventListener('change', () => {cur.isLoop = loop.checked; if (!loop.checked) window.BP3_BUS?.emit('REPLIE_DISMISS', {}); persist(); announce(loop.checked ? 'เปิดการแสดงค้างไว้' : 'ปิดการแสดงค้างไว้');});
    d.getElementById('rpDemoBtn').onclick = () => setDemo(!demoOn);
    panelApi = {paint};
    paint();
  }

  /* ---------- create / edit dialog ---------- */
  const FONTS = ['Kanit', 'Noto Sans Thai Looped', 'Chakra Petch'];
  const ANIM_IN = [['none', 'ไม่มี'], ['fade', 'เลือนเข้า'], ['slide-up', 'เลื่อนขึ้น'], ['slide-down', 'เลื่อนลง'], ['slide-left', 'เลื่อนจากซ้าย'], ['slide-right', 'เลื่อนจากขวา'], ['zoom', 'ขยายเข้า'], ['bounce', 'เด้งกระดอน']];
  const ANIM_OUT = [['none', 'ไม่มี'], ['fade', 'เลือนหาย'], ['slide-up', 'เลื่อนขึ้นหาย'], ['slide-down', 'เลื่อนลงหาย'], ['zoom', 'ย่อหาย']];
  const PROGRESS = [['cyan', 'สีฟ้า'], ['gold', 'สีทอง'], ['violet', 'สีม่วง'], ['emerald', 'สีเขียว'], ['sunset', 'สีส้ม']];
  const TICKER_LAYOUT = [['bottom_ticker', 'แถบยาวล่างจอ'], ['full_ticker', 'เต็มความกว้าง'], ['side_card', 'การ์ดด้านข้าง']];
  const IMAGE_LAYOUT = [['card', 'การ์ดมาตรฐาน'], ['full', 'เต็มกรอบ'], ['frameless', 'ไม่มีกรอบ']];
  const MODES = [['ticker', '💬', 'ข้อความ', 'แถบข้อความขึ้นบนจอ'], ['image', '🖼️', 'รูปภาพ', 'รูปหรือ GIF ขึ้นบนจอ'], ['combo', '✨', 'ข้อความ + รูป', 'ขึ้นพร้อมกันทั้งสองอย่าง']];

  function injectDialogStyle(d) {
    if (d.getElementById('replie-dialog-style')) return;
    const st = d.createElement('style'); st.id = 'replie-dialog-style';
    st.textContent = `
.rp-dlg{position:fixed;inset:0;margin:auto;height:fit-content;width:min(980px,96vw);max-height:92vh;padding:0;overflow:hidden;background:var(--dc-bg-card,#232428);color:#f2f3f5;border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.85);font-family:inherit;}
.rp-dlg::backdrop{background:rgba(0,0,0,.65);}
.rp-dlg form{display:flex;flex-direction:column;max-height:92vh;margin:0;}
.rp-dlg *{box-sizing:border-box;}
.rp-dlg .rp-dh{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 20px;background:var(--dc-bg-input,#1e1f22);border-bottom:1px solid var(--dc-border-hover,rgba(255,255,255,.16));}
.rp-dlg .rp-dh h2{margin:0;font-size:17px;font-weight:800;color:var(--dc-text-primary,#f2f3f5);}
.rp-dlg .rp-db{overflow-y:auto;padding:16px 20px;}
.rp-dlg .rp-cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(250px,320px);gap:20px;align-items:start;}
@media (max-width:760px){.rp-dlg .rp-cols{grid-template-columns:minmax(0,1fr);}}
.rp-dlg .rp-steps{display:flex;flex-direction:column;gap:14px;min-width:0;}
.rp-dlg .rp-sec{background:var(--dc-bg-card,#232428);border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:12px;padding:14px 16px 16px;margin:0;min-width:0;}
.rp-dlg .rp-sec[hidden]{display:none;}
.rp-dlg h3{margin:0 0 4px;font-size:15.5px;font-weight:800;display:flex;flex-direction:column;gap:2px;align-items:flex-start;line-height:1.4;}
.rp-dlg .num{display:block;font-size:12px;font-weight:700;letter-spacing:.05em;color:var(--app-accent,var(--dc-blurple,#5865f2));line-height:1.3;}
.rp-dlg .help{margin:0 0 10px;font-size:13px;line-height:1.55;color:#b5bac1;}
.rp-dlg .fld{display:flex;flex-direction:column;gap:5px;margin:0 0 12px;min-width:0;}
.rp-dlg label.lb,.rp-dlg legend{font-size:14px;font-weight:700;color:#f2f3f5;padding:0;}
.rp-dlg fieldset{border:0;padding:0;margin:0 0 12px;min-width:0;}
.rp-dlg legend{margin-bottom:6px;}
.rp-dlg input[type=text],.rp-dlg input[type=url],.rp-dlg input[type=number],.rp-dlg select,.rp-dlg textarea{width:100%;min-height:40px;padding:8px 10px;border:2px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:8px;background:var(--dc-bg-input,#1e1f22);color:#fff;font-family:inherit;font-size:14.5px;}
.rp-dlg :is(input,select,textarea):focus{border-color:var(--app-accent,var(--dc-blurple,#5865f2));outline:none;}
.rp-dlg textarea{min-height:92px;resize:vertical;line-height:1.55;}
.rp-dlg input[type=number]{width:110px;text-align:right;}
.rp-dlg input[type=color]{width:56px;height:40px;padding:2px;border:2px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:8px;background:var(--dc-bg-input,#1e1f22);cursor:pointer;}
.rp-dlg input[aria-invalid="true"],.rp-dlg textarea[aria-invalid="true"]{border-color:#f87171;}
.rp-dlg .err{font-size:13.5px;font-weight:700;color:#fca5a5;}
.rp-dlg .err:empty{display:none;}
.rp-dlg .inl{display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
.rp-dlg .inl2{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;}
.rp-dlg .btn{min-height:38px;padding:6px 16px;border-radius:8px;border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));background:var(--dc-bg-input,#1e1f22);color:#f2f3f5;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;display:inline-flex;align-items:center;gap:6px;}
.rp-dlg .btn:hover{border-color:var(--app-accent,var(--dc-blurple,#5865f2));}
.rp-dlg .btn.primary{background:var(--app-accent,var(--dc-blurple,#5865f2));color:#fff;border-color:var(--app-accent,var(--dc-blurple,#5865f2));font-weight:700;}
.rp-dlg .btn.primary:hover{filter:brightness(1.12);}
.rp-dlg .btn.danger{background:transparent;border-color:var(--dc-red,#f23f43);color:var(--dc-red,#f23f43);}
.rp-dlg .btn:disabled{opacity:.6;cursor:wait;}
.rp-dlg .opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;}
.rp-dlg .opt{position:relative;display:block;margin:0;cursor:pointer;}
.rp-dlg .opt input{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:pointer;z-index:1;}
.rp-dlg .face{display:flex;flex-direction:column;gap:3px;align-items:flex-start;height:100%;min-height:44px;padding:10px 12px;border:2px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:10px;background:var(--dc-bg-input,#1e1f22);position:relative;}
.rp-dlg .face .ic{font-size:22px;line-height:1;}
.rp-dlg .face b{font-size:14px;}
.rp-dlg .face small{font-size:12.5px;color:#b5bac1;line-height:1.4;}
.rp-dlg .opt:hover .face{border-color:var(--app-accent,var(--dc-blurple,#5865f2));}
.rp-dlg .opt input:checked+.face{border-color:var(--app-accent,var(--dc-blurple,#5865f2));background:color-mix(in srgb,var(--app-accent,var(--dc-blurple,#5865f2)) 16%,transparent);box-shadow:inset 0 0 0 1px var(--app-accent,var(--dc-blurple,#5865f2));}
.rp-dlg .opt input:checked+.face::after{content:"✓";position:absolute;top:8px;right:10px;width:22px;height:22px;border-radius:50%;background:var(--app-accent,var(--dc-blurple,#5865f2));color:#fff;font-weight:900;display:flex;align-items:center;justify-content:center;font-size:13px;}
.rp-dlg .opt input:focus-visible+.face,.rp-dlg :is(button,input,select,textarea,summary):focus-visible{outline:2px solid var(--app-accent,var(--dc-blurple,#5865f2));outline-offset:2px;}
.rp-dlg .pos3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;max-width:320px;}
.rp-dlg .pos3 .face{flex-direction:row;gap:4px;align-items:center;justify-content:center;text-align:center;font-size:13px;font-weight:700;min-height:40px;padding:6px 4px;}
.rp-dlg .pos3 .opt input:checked+.face::after{display:none;}
.rp-dlg .pos3 .opt input:checked+.face::before{content:"✓";font-weight:900;}
.rp-dlg details{border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:10px;padding:0;margin-top:6px;background:var(--dc-bg-input,#1e1f22);}
.rp-dlg summary{cursor:pointer;padding:10px 12px;font-size:14px;font-weight:700;min-height:40px;}
.rp-dlg details>.in{padding:2px 12px 12px;}
.rp-dlg .tick{display:flex;gap:10px;align-items:flex-start;font-size:14px;line-height:1.5;margin:0 0 10px;cursor:pointer;}
.rp-dlg .tick input{width:22px;height:22px;margin:1px 0 0;flex:none;accent-color:var(--app-accent,var(--dc-blurple,#5865f2));}
.rp-dlg .tick small{display:block;font-size:13px;color:#b5bac1;font-weight:400;}
.rp-dlg .rp-prev{position:sticky;top:0;background:var(--dc-bg-card,#232428);border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:12px;padding:14px 16px 16px;}
.rp-dlg .screen{position:relative;width:100%;aspect-ratio:16/9;background:linear-gradient(135deg,#0b1220,#1e293b);border:2px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:10px;overflow:hidden;}
.rp-dlg .screen{touch-action:none;user-select:none;background-image:linear-gradient(rgba(255,255,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.07) 1px,transparent 1px),linear-gradient(135deg,#0b1220,#1e293b);background-size:25% 25%,25% 25%,auto;}
.rp-dlg .screen .it{position:absolute;box-sizing:border-box;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;border-radius:6px;padding:2px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;box-shadow:0 2px 8px rgba(0,0,0,.5);cursor:grab;touch-action:none;border:2px solid transparent;}
.rp-dlg .screen .it[hidden]{display:none;}
.rp-dlg .screen .it.drag{cursor:grabbing;}
.rp-dlg .screen .it:focus-visible{outline:3px solid #fff;outline-offset:1px;}
.rp-dlg .screen .it .hd{position:absolute;right:0;bottom:0;width:12px;height:12px;background:#fff;opacity:.85;border-radius:3px 0 4px 0;cursor:nwse-resize;touch-action:none;}
.rp-dlg .screen .gd{position:absolute;background:#ef4444;opacity:0;pointer-events:none;}
.rp-dlg .screen .gd.v{top:0;bottom:0;left:50%;width:1px;}.rp-dlg .screen .gd.h{left:0;right:0;top:50%;height:1px;}.rp-dlg .screen .gd.on{opacity:.95;}
.rp-dlg .rp-prevbtns{display:flex;flex-direction:column;gap:8px;margin-top:10px;}
.rp-dlg .rp-prevbtns .btn[aria-pressed="true"]{background:var(--app-accent,var(--dc-blurple,#5865f2));color:#fff;border-color:transparent;}
.rp-dlg .rp-anim{margin-top:10px;padding:10px 12px;border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));border-radius:10px;background:var(--dc-bg-input,#1e1f22);}
.rp-dlg .rp-anim .help{margin:0 0 8px;}
.rp-dlg .screen .it.t{background:var(--app-accent,var(--dc-blurple,#5865f2));color:#fff;}
.rp-dlg .screen .it.i{background:var(--dc-green,#23a55a);color:#fff;}
.rp-dlg .rp-df{display:flex;justify-content:flex-end;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 20px;background:var(--dc-bg-input,#1e1f22);border-top:1px solid var(--dc-border-hover,rgba(255,255,255,.16));}
.rp-dlg .rp-df .msg{margin-right:auto;font-size:14px;font-weight:700;color:var(--dc-amber,#f0b232);}
.rp-dlg .rp-df .msg:empty{display:none;}
.rp-dlg .sum{margin:0 0 12px;padding:10px 12px;border:2px solid #f87171;border-radius:10px;background:#3b1d1d;color:#fee2e2;font-size:14px;font-weight:700;}
.rp-dlg .sum:empty{display:none;}
.rp-dlg .rp-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;}
.rp-dlg .thumbrow{display:flex;gap:12px;align-items:center;flex-wrap:wrap;}
.rp-dlg .thumb{width:84px;height:84px;object-fit:contain;border-radius:10px;background:#111214;border:1px solid var(--dc-border-hover,rgba(255,255,255,.16));}
`;
    (d.head || d.documentElement).append(st);
  }

  window.editReplieCommand = function(previous) {
    const d = doc();
    injectDialogStyle(d);
    const old = commands()[previous] || {};
    const payload = structuredClone(old.legacyPayload || {});
    payload.ticker ||= {enabled: !!old.text, text: old.text || '', layout: 'bottom_ticker'};
    payload.image ||= {enabled: !!old.imageUrl, image_url: old.imageUrl || '', layout: 'card'};
    const T = payload.ticker, I = payload.image;
    const isNew = !previous;
    const startMode = isNew ? 'ticker' : (T.enabled && I.enabled ? 'combo' : I.enabled ? 'image' : 'ticker');

    const dlg = d.createElement('dialog'); dlg.className = 'rp-dlg'; dlg.id = 'replieCommandEditor';
    dlg.setAttribute('aria-labelledby', 'rpDlgTitle');
    const form = d.createElement('form'); form.method = 'dialog'; form.noValidate = true; dlg.append(form);
    const uid = (k) => 'rpe_' + k;
    const E = (tag, cls, text) => el(d, tag, cls, text);

    // header
    const head = E('div', 'rp-dh');
    const h2 = E('h2', '', isNew ? 'สร้างคำสั่งใหม่' : 'แก้ไขคำสั่ง ' + previous); h2.id = 'rpDlgTitle';
    const x = E('button', 'btn', '×'); x.type = 'button'; x.setAttribute('aria-label', 'ปิดโดยไม่บันทึก');
    head.append(h2, x); form.append(head);

    const body = E('div', 'rp-db'); form.append(body);
    const summary = E('div', 'sum'); summary.setAttribute('role', 'alert'); body.append(summary);
    const cols = E('div', 'rp-cols'); body.append(cols);
    const steps = E('div', 'rp-steps'); cols.append(steps);

    const inputs = {};
    function field(parent, key, label, kind, value, opts) {
      const wrap = E('div', 'fld');
      const lb = E('label', 'lb', label); lb.htmlFor = uid(key);
      let input;
      if (opts) {
        input = d.createElement('select');
        const list = opts.slice();
        if (kind !== 'check' && value && !list.some(o => String(o[0]) === String(value))) list.push([value, String(value)]);
        for (const o of list) {const op = d.createElement('option'); op.value = o[0]; op.textContent = o[1]; input.append(op);}
        input.value = value;
      } else if (kind === 'textarea') {input = d.createElement('textarea'); input.value = value ?? '';}
      else {input = d.createElement('input'); input.type = kind; input.value = value ?? ''; if (kind === 'number') input.step = 'any';}
      input.id = uid(key);
      wrap.append(lb, input);
      parent.append(wrap);
      inputs[key] = input;
      return {wrap, input, lb};
    }
    function tick(parent, key, label, hint, value) {
      const l = E('label', 'tick'); const input = d.createElement('input'); input.type = 'checkbox'; input.id = uid(key); input.checked = !!value;
      const s = E('span'); const b = E('b', '', label); s.append(b); if (hint) s.append(E('small', '', hint));
      l.append(input, s); parent.append(l); inputs[key] = input; return input;
    }
    function section(num, title, help) {
      const s = E('section', 'rp-sec'); s.setAttribute('aria-labelledby', 'rps_' + num);
      const h = E('h3'); h.id = 'rps_' + num; const n = E('span', 'num', 'ขั้นที่ ' + num); n.setAttribute('aria-hidden', 'true'); const tx = d.createElement('span'); tx.textContent = title; h.append(n, tx);
      s.append(h); if (help) s.append(E('p', 'help', help)); steps.append(s); s._num = n; return s;
    }

    // 1. name
    const s1 = section(1, 'ตั้งชื่อคำสั่ง', 'คำที่ผู้ชมพิมพ์ในแชทเพื่อเรียกให้ขึ้นจอ');
    const fCmd = field(s1, 'command', 'คำสั่งแชท', 'text', previous || '');
    fCmd.input.placeholder = 'เช่น !hi'; fCmd.input.autocomplete = 'off'; fCmd.input.setAttribute('aria-describedby', 'rpe_command_err');
    const errCmd = E('div', 'err'); errCmd.id = 'rpe_command_err'; fCmd.wrap.append(errCmd);
    const fCool = field(s1, 'cooldown', 'กันสแปม รอก่อนใช้ซ้ำได้อีกกี่วินาที', 'number', num(old.cooldown, 0));
    fCool.input.min = '0'; fCool.input.setAttribute('aria-describedby', 'rpe_cool_help');
    const coolHelp = E('div', 'help', 'ใส่ 0 ถ้าไม่ต้องการจำกัด'); coolHelp.id = 'rpe_cool_help'; fCool.wrap.append(coolHelp);
    tick(s1, 'enabled', 'เปิดใช้คำสั่งนี้', 'ถ้าปิด ผู้ชมพิมพ์แล้วจะไม่มีอะไรขึ้นจอ', old.enabled !== false);

    // 2. mode
    const s2 = section(2, 'จะแสดงอะไรบนจอ', 'เลือกอย่างใดอย่างหนึ่ง');
    const modeSet = E('fieldset'); const lg = E('legend', 'rp-sr', 'ประเภทการแสดงผล'); modeSet.append(lg);
    const opts = E('div', 'opts');
    for (const [id, icon, name, hint] of MODES) {
      const l = E('label', 'opt'); const i = d.createElement('input'); i.type = 'radio'; i.name = 'rpe_mode'; i.value = id; i.checked = startMode === id;
      const f = E('span', 'face'); const ic = E('span', 'ic', icon); ic.setAttribute('aria-hidden', 'true'); f.append(ic, E('b', '', name), E('small', '', hint));
      l.append(i, f); opts.append(l);
    }
    modeSet.append(opts); s2.append(modeSet);

    // position picker helper (sets x/y of one element)
    function posPicker(parent, kind, data) {
      const set = E('fieldset'); set.append(E('legend', '', 'ตำแหน่งบนจอ (กดเลือกจุดสำเร็จรูป หรือลากเองในภาพตัวอย่าง)'));
      const grid = E('div', 'pos3');
      const gname = 'rpe_pos_' + kind;
      ZONES.forEach(([code, label], idx) => {
        const l = E('label', 'opt'); const i = d.createElement('input'); i.type = 'radio'; i.name = gname; i.value = String(idx);
        l.append(i, E('span', 'face', label)); grid.append(l);
      });
      set.append(grid);
      const custom = E('div', 'help'); custom.style.margin = '8px 0 0'; set.append(custom);
      parent.append(set);
      const sync = () => {
        const px = num(inputs[kind + '.pos_x'].value, NaN), py = num(inputs[kind + '.pos_y'].value, NaN);
        let hit = -1;
        ZONES.forEach((z, idx) => {if (PX[idx % 3] === px && PY[Math.floor(idx / 3)] === py) hit = idx;});
        grid.querySelectorAll('input').forEach((r, idx) => {r.checked = idx === hit;});
        custom.textContent = hit < 0 ? 'ตำแหน่งกำหนดเอง (แนวนอน ' + Math.round(px) + '%, แนวตั้ง ' + Math.round(py) + '%) ลากกล่องในภาพตัวอย่างด้านขวาเพื่อปรับต่อได้' : 'ลากกล่องในภาพตัวอย่างด้านขวาเพื่อวางเองได้ ค้าง Ctrl เพื่อลากอิสระไม่ดูด คลิกกล่องแล้วกดลูกศร = ขยับทีละ 1 พิกเซล (ค้าง Shift = 10 พิกเซล)';
      };
      grid.addEventListener('change', (e) => {
        const idx = Number(e.target.value);
        inputs[kind + '.pos_x'].value = PX[idx % 3]; inputs[kind + '.pos_y'].value = PY[Math.floor(idx / 3)];
        sync(); redrawPreview();
      });
      return sync;
    }
    function advanced(parent, kind, data, defaults) {
      const ani = E('div', 'rp-anim'); ani.append(E('p', 'help', 'แอนิเมชันตอนขึ้นจอและตอนหายไป เลือกแล้วจะเล่นทดลองบนจอ OBS ให้ดูทันที'));
      const ag = E('div', 'inl2'); ani.append(ag);
      field(ag, kind + '.anim_in', 'แอนิเมชันตอนเข้า', 'text', data.anim_in || defaults.in, ANIM_IN).input.addEventListener('change', () => {testAnim();});
      field(ag, kind + '.anim_out', 'แอนิเมชันตอนออก', 'text', data.anim_out || defaults.out, ANIM_OUT).input.addEventListener('change', () => {testAnim();});
      parent.append(ani);
      const det = E('details'); const sm = E('summary', '', 'ตั้งค่าขั้นสูง ตำแหน่งแบบตัวเลข ขนาด และความทึบ'); det.append(sm);
      const inn = E('div', 'in'); det.append(inn);
      const g = E('div', 'inl2'); inn.append(g);
      field(g, kind + '.pos_x', 'ตำแหน่งแนวนอน (% จากซ้าย)', 'number', num(data.pos_x, defaults.x)).input.addEventListener('input', () => {syncs[kind](); redrawPreview();});
      field(g, kind + '.pos_y', 'ตำแหน่งแนวตั้ง (% จากบน)', 'number', num(data.pos_y, defaults.y)).input.addEventListener('input', () => {syncs[kind](); redrawPreview();});
      field(g, kind + '.scale', 'ขนาด (1 = ปกติ)', 'number', num(data.scale, 1)).input.addEventListener('input', redrawPreview);
      field(g, kind + '.opacity', 'ความทึบ (0.1 ถึง 1)', 'number', num(data.opacity, 0.95));
      parent.append(det);
    }
    const syncs = {};

    // 3. text
    const s3 = section(3, 'ข้อความ', 'ข้อความที่จะขึ้นบนจอ');
    const fText = field(s3, 'ticker.text', 'ข้อความตอบกลับ', 'textarea', T.text || '');
    fText.input.setAttribute('aria-describedby', 'rpe_text_err');
    const errText = E('div', 'err'); errText.id = 'rpe_text_err'; fText.wrap.append(errText);
    field(s3, 'ticker.title', 'หัวข้อเล็ก (ไม่ใส่ก็ได้)', 'text', T.title || '');
    const tg = E('div', 'inl2'); s3.append(tg);
    field(tg, 'ticker.ticker_font', 'ฟอนต์', 'text', T.ticker_font || 'Kanit', FONTS.map(f => [f, f]));
    field(tg, 'ticker.ticker_font_size', 'ขนาดตัวอักษร (px)', 'number', num(T.ticker_font_size, 28)).input.min = '8';
    const colorWrap = E('div', 'fld'); const cl = E('label', 'lb', 'สีตัวอักษร'); cl.htmlFor = uid('ticker.ticker_color');
    const color = d.createElement('input'); color.type = 'color'; color.id = uid('ticker.ticker_color'); color.value = /^#[0-9a-f]{6}$/i.test(T.ticker_color || '') ? T.ticker_color : '#ffffff';
    colorWrap.append(cl, color); tg.append(colorWrap); inputs['ticker.ticker_color'] = color;
    field(tg, 'ticker.layout', 'รูปแบบการจัดวาง', 'text', T.layout || 'bottom_ticker', TICKER_LAYOUT);
    tick(s3, 'ticker.ticker_bold', 'ตัวหนา', '', T.ticker_bold !== false);
    syncs.ticker = posPicker(s3, 'ticker', T);
    advanced(s3, 'ticker', T, {x: 50, y: 88, in: 'slide-up', out: 'slide-down'});
    syncs.ticker();

    // 4. image
    const s4 = section(4, 'รูปภาพ', 'รูปหรือ GIF ที่จะขึ้นบนจอ');
    const fImg = field(s4, 'image.image_url', 'ลิงก์รูปภาพ', 'text', I.image_url || '');
    fImg.input.placeholder = 'วางลิงก์รูป หรือกดเลือกจากเครื่อง'; fImg.input.setAttribute('aria-describedby', 'rpe_img_err');
    const errImg = E('div', 'err'); errImg.id = 'rpe_img_err'; fImg.wrap.append(errImg);
    const tr = E('div', 'thumbrow'); const thumb = E('img', 'thumb'); thumb.alt = 'ตัวอย่างรูปที่เลือก'; thumb.hidden = true;
    const up = E('button', 'btn', '📁 เลือกรูปจากเครื่อง'); up.type = 'button';
    tr.append(up, thumb); s4.append(tr);
    const showThumb = () => {const v = fImg.input.value.trim(); if (!v) {thumb.hidden = true; return;} thumb.src = v; thumb.hidden = false;};
    thumb.addEventListener('error', () => {thumb.hidden = true;});
    fImg.input.addEventListener('input', showThumb); showThumb();
    up.onclick = () => {
      const picker = d.createElement('input'); picker.type = 'file'; picker.accept = 'image/*'; picker.style.display = 'none'; d.body.append(picker);
      picker.onchange = async () => {
        const file = picker.files && picker.files[0]; picker.remove(); if (!file) return;
        try {
          up.textContent = '⏳ กำลังอัปโหลด...'; up.disabled = true;
          const response = await fetch('/api/playroom/import', {method: 'POST', headers: {'Content-Type': 'application/octet-stream', 'X-Filename': encodeURIComponent(file.name)}, body: file});
          const result = await response.json();
          if (response.ok && result.url) {fImg.input.value = result.url; showThumb(); errImg.textContent = '';} else errImg.textContent = 'อัปโหลดไม่สำเร็จ ลองใหม่หรือวางลิงก์แทน';
        } catch (_) {errImg.textContent = 'อัปโหลดไม่สำเร็จ ลองใหม่หรือวางลิงก์แทน';}
        finally {up.textContent = '📁 เลือกรูปจากเครื่อง'; up.disabled = false;}
      };
      picker.click();
    };
    const ig = E('div', 'inl2'); s4.append(ig);
    field(ig, 'image.top_text', 'ข้อความเหนือรูป (ไม่ใส่ก็ได้)', 'text', I.top_text || '');
    field(ig, 'image.bottom_text', 'ข้อความใต้รูป (ไม่ใส่ก็ได้)', 'text', I.bottom_text || '');
    field(s4, 'image.layout', 'รูปแบบการจัดวาง', 'text', I.layout || 'card', IMAGE_LAYOUT);
    syncs.image = posPicker(s4, 'image', I);
    advanced(s4, 'image', I, {x: 85, y: 50, in: 'slide-left', out: 'slide-right'});
    syncs.image();

    // 5. time
    const s5 = section(5, 'เวลาที่แสดงบนจอ', 'ตั้งว่าจะอยู่บนจอนานเท่าไร');
    const fDur = field(s5, 'duration_sec', 'แสดงบนจอนาน (วินาที)', 'number', num(payload.duration_sec, num(old.duration, 8)));
    fDur.input.min = '1';
    tick(s5, 'is_loop', 'แสดงค้างไว้ไม่หายเอง', 'ใช้กับป้ายหรือรูปที่อยากให้อยู่จนกว่าจะสั่งปิด', payload.is_loop || false);
    field(s5, 'progress_style', 'สีแถบนับเวลาถอยหลัง', 'text', payload.progress_style || 'cyan', PROGRESS);

    // preview column
    const prev = E('aside', 'rp-prev'); prev.setAttribute('aria-label', 'ตัวอย่างตำแหน่งบนจอ'); cols.append(prev);
    prev.append(E('h3', '', 'ตัวอย่างตำแหน่งบนจอ'), E('p', 'help', 'ภาพจำลองโดยประมาณ ใช้ดูว่าข้อความและรูปจะอยู่ตรงไหนของจอ'));
    const screen = E('div', 'screen'); screen.setAttribute('role', 'group'); prev.append(screen);
    const pt = E('div', 'it t'), pi = E('div', 'it i');
    pt.tabIndex = 0; pi.tabIndex = 0;
    pt.setAttribute('aria-label', 'กล่องข้อความ ลากหรือใช้ปุ่มลูกศรเพื่อย้าย'); pi.setAttribute('aria-label', 'กล่องรูปภาพ ลากหรือใช้ปุ่มลูกศรเพื่อย้าย');
    const ptl = E('span', '', 'ข้อความ'), pil = E('span', '', 'รูปภาพ');
    const hT = E('span', 'hd'), hI = E('span', 'hd');
    pt.append(ptl, hT); pi.append(pil, hI);
    const gdv = E('span', 'gd v'), gdh = E('span', 'gd h');
    screen.append(pt, pi, gdv, gdh);
    const note = E('p', 'help'); note.style.margin = '8px 0 0'; prev.append(note);
    const btns = E('div', 'rp-prevbtns'); prev.append(btns);
    const liveBtn = E('button', 'btn', '👁 ดูสดบนจอ OBS'); liveBtn.type = 'button'; liveBtn.setAttribute('aria-pressed', 'false');
    const playBtn = E('button', 'btn', '▶ ทดลองแอนิเมชันเข้า-ออก'); playBtn.type = 'button';
    const liveNote = E('p', 'help', 'ดูสดจะโชว์ค้างบนจอ OBS และขยับตามที่แก้ไข ปิดอัตโนมัติเมื่อปิดหน้าต่างนี้'); liveNote.style.margin = '0'; liveNote.setAttribute('role', 'status');
    btns.append(liveBtn, playBtn, liveNote);
    const BASE = {ticker: [0.30, 0.11], image: [0.16, 0.28]};
    const sizeOf = (kind) => {
      const sc = clamp(num(inputs[kind + '.scale'].value, 1), 0.3, 3);
      const full = kind === 'ticker' && inputs['ticker.layout'].value === 'full_ticker';
      return {w: full ? 1 : Math.min(0.96, BASE[kind][0] * sc), h: Math.min(0.96, BASE[kind][1] * sc), full, sc};
    };
    function dragWire(node, handle, kind) {
      const guides = (a, b) => {gdv.classList.toggle('on', a); gdh.classList.toggle('on', b);};
      const snap = (v, tol) => [0, 50, 100].some(q => Math.abs(v - q) <= tol) ? [0, 50, 100].find(q => Math.abs(v - q) <= tol) : v;
      const begin = (ev, mode) => {
        ev.preventDefault(); ev.stopPropagation();
        try {node.focus({preventScroll: true});} catch (_) {}
        const L = screen.getBoundingClientRect(), x0 = ev.clientX, y0 = ev.clientY, sz = sizeOf(kind);
        const px0 = num(inputs[kind + '.pos_x'].value, 50), py0 = num(inputs[kind + '.pos_y'].value, 50);
        const target = mode === 'move' ? node : handle;
        try {target.setPointerCapture(ev.pointerId);} catch (_) {}
        node.classList.add('drag');
        const mv = (e) => {
          const dx = (e.clientX - x0) / L.width, dy = (e.clientY - y0) / L.height;
          if (mode === 'move') {
            const rx = Math.max(0.0001, 1 - sz.w), ry = Math.max(0.0001, 1 - sz.h);
            const nx = sz.full ? px0 : clamp(px0 + dx / rx * 100, 0, 100), ny = clamp(py0 + dy / ry * 100, 0, 100);
            const free = e.ctrlKey || e.metaKey;
            const sx = (sz.full || free) ? nx : snap(nx, 14 / (L.width * rx) * 100), sy = free ? ny : snap(ny, 14 / (L.height * ry) * 100);
            inputs[kind + '.pos_x'].value = Math.round(sx * 1000) / 1000; inputs[kind + '.pos_y'].value = Math.round(sy * 1000) / 1000;
            guides(!sz.full && sx === 50, sy === 50);
          } else {
            const nw = sz.w + dx, base = BASE[kind][0];
            inputs[kind + '.scale'].value = clamp(Math.round(nw / base / 0.05) * 0.05, 0.3, 3).toFixed(2).replace(/0$/, '').replace(/\.$/, '');
          }
          syncs[kind](); redrawPreview(); liveSync();
        };
        const up = () => {node.classList.remove('drag'); guides(false, false); target.removeEventListener('pointermove', mv); target.removeEventListener('pointerup', up); target.removeEventListener('pointercancel', up);};
        target.addEventListener('pointermove', mv); target.addEventListener('pointerup', up); target.addEventListener('pointercancel', up);
      };
      node.addEventListener('pointerdown', (e) => {if (e.target === handle) return; begin(e, 'move');});
      handle.addEventListener('pointerdown', (e) => begin(e, 'size'));
      node.addEventListener('keydown', (e) => {
        const px = e.shiftKey ? 10 : 1, k = e.key; if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(k)) return; e.preventDefault();
        const sz = sizeOf(kind), X = inputs[kind + '.pos_x'], Y = inputs[kind + '.pos_y'];
        const stx = px * 100 / (1920 * Math.max(0.0001, 1 - sz.w)), sty = px * 100 / (1080 * Math.max(0.0001, 1 - sz.h));
        const r3 = (v) => Math.round(v * 1000) / 1000;
        if (k === 'ArrowLeft' && !sz.full) X.value = r3(clamp(num(X.value, 50) - stx, 0, 100)); if (k === 'ArrowRight' && !sz.full) X.value = r3(clamp(num(X.value, 50) + stx, 0, 100));
        if (k === 'ArrowUp') Y.value = r3(clamp(num(Y.value, 50) - sty, 0, 100)); if (k === 'ArrowDown') Y.value = r3(clamp(num(Y.value, 50) + sty, 0, 100));
        syncs[kind](); redrawPreview(); liveSync();
      });
    }

    const mode = () => (form.querySelector('input[name="rpe_mode"]:checked') || {}).value || 'ticker';
    function redrawPreview() {
      const m = mode(), showT = m !== 'image', showI = m !== 'ticker';
      pt.hidden = !showT; pi.hidden = !showI;
      const place = (node, kind) => {
        const px = clamp(num(inputs[kind + '.pos_x'].value, 50), 0, 100), py = clamp(num(inputs[kind + '.pos_y'].value, 50), 0, 100);
        const sz = sizeOf(kind);
        node.style.width = (sz.w * 100) + '%'; node.style.height = (sz.h * 100) + '%';
        node.style.left = (sz.full ? 0 : px / 100 * (1 - sz.w) * 100) + '%'; node.style.top = (py / 100 * (1 - sz.h) * 100) + '%';
      };
      place(pt, 'ticker'); place(pi, 'image');
      const names = []; if (showT) names.push('ข้อความ: ' + zoneOf(num(inputs['ticker.pos_x'].value, 50), num(inputs['ticker.pos_y'].value, 88)));
      if (showI) names.push('รูป: ' + zoneOf(num(inputs['image.pos_x'].value, 85), num(inputs['image.pos_y'].value, 50)));
      note.textContent = names.join(' · ');
      screen.setAttribute('aria-label', 'ตัวอย่างตำแหน่ง ' + names.join(' และ '));
      s3.hidden = !showT; s4.hidden = !showI;
      let k = 0; [s1, s2, s3, s4, s5].forEach((sec) => {if (!sec.hidden) sec._num.textContent = 'ขั้นที่ ' + (++k);});
    }
    form.addEventListener('change', (e) => {if (e.target.name === 'rpe_mode' || e.target.id === 'rpe_ticker.layout') redrawPreview(); liveSync();});
    dragWire(pt, hT, 'ticker'); dragWire(pi, hI, 'image');
    redrawPreview();

    /* live view + animation test on the OBS overlay (never saved) */
    let liveOn = false, liveFirst = true, livePend = false, testTimer = 0;
    function buildPreviewPayload(loop) {
      const p = structuredClone(payload), m = mode();
      for (const [key, input] of Object.entries(inputs)) {
        const v = input.type === 'checkbox' ? input.checked : input.type === 'number' ? num(input.value, 0) : input.value;
        if (key.includes('.')) {const [g, k] = key.split('.'); (p[g] ||= {})[k] = v;} else if (!['command', 'cooldown', 'enabled'].includes(key)) p[key] = v;
      }
      p.ticker.enabled = m !== 'image'; p.image.enabled = m !== 'ticker' && !!String(p.image.image_url || '').trim();
      if (p.ticker.enabled && !String(p.ticker.text || '').trim()) p.ticker.text = 'ตัวอย่างข้อความ Replie';
      if (m !== 'image' && !p.ticker.enabled) p.ticker.enabled = true;
      p.is_loop = !!loop;
      if (loop) {p.ticker.countdown_type = 'none'; p.image.countdown_type = 'none';}
      return p;
    }
    function emitPreview(p) {window._rpPanelTest = true; window.BP3_BUS?.emit('REPLIE_ACTION', {legacyPayload: p, duration: p.duration_sec || 4});}
    function setLive(on, msg) {
      if (on === liveOn) return; liveOn = on; liveBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
      liveBtn.textContent = on ? '⏹ หยุดดูสดบนจอ OBS' : '👁 ดูสดบนจอ OBS';
      if (on) {
        if (demoOn) setDemo(false); clearTimeout(testTimer);
        liveFirst = true; emitPreview(buildPreviewPayload(true)); liveFirst = false;
        liveNote.textContent = 'กำลังแสดงสดบนจอ OBS ลากกล่อง ย่อ/ขยาย หรือแก้ข้อความได้เลย เห็นผลทันที';
      } else {
        window.BP3_BUS?.emit('REPLIE_DISMISS', {}); window._rpPanelTest = false;
        liveNote.textContent = msg || 'ดูสดจะโชว์ค้างบนจอ OBS และขยับตามที่แก้ไข ปิดอัตโนมัติเมื่อปิดหน้าต่างนี้';
      }
    }
    function liveSync() {
      if (!liveOn || livePend) return; livePend = true;
      setTimeout(() => {livePend = false; if (liveOn) {const p = buildPreviewPayload(true); p.test_mode = 'out'; emitPreview(p);}}, 100);
    }
    function testAnim() {
      if (liveOn) setLive(false); if (demoOn) setDemo(false);
      clearTimeout(testTimer);
      const p = buildPreviewPayload(false); p.duration_sec = 3.6; p.ticker.countdown_type = 'none'; p.image.countdown_type = 'none';
      emitPreview(p);
      liveNote.textContent = 'กำลังเล่นทดลองบนจอ OBS ดูตอนเข้าแล้วตอนออก';
      testTimer = setTimeout(() => {window._rpPanelTest = false; liveNote.textContent = 'ทดลองจบแล้ว เลือกแอนิเมชันอื่นหรือกดทดลองซ้ำได้';}, 4200);
    }
    liveBtn.onclick = () => setLive(!liveOn);
    playBtn.onclick = testAnim;
    form.addEventListener('input', liveSync);
    dlgLiveStop = () => {clearTimeout(testTimer); if (liveOn) setLive(false, 'ปิดดูสดแล้ว');};

    // footer
    const foot = E('div', 'rp-df');
    const msg = E('div', 'msg'); msg.setAttribute('role', 'status');
    const cancel = E('button', 'btn', 'ยกเลิก'); cancel.type = 'button';
    const save = E('button', 'btn primary', '💾 บันทึกคำสั่ง'); save.type = 'submit';
    foot.append(msg, cancel, save); form.append(foot);

    // closing: ask before throwing away typed changes
    const snapshot = () => JSON.stringify([...form.elements].filter(n => n.name !== 'rpe_mode' || n.checked).map(n => n.type === 'checkbox' || n.type === 'radio' ? n.checked : n.value));
    const initial = snapshot();
    let confirming = false;
    function requestClose() {
      if (snapshot() === initial || confirming) {dlg.close(); return;}
      confirming = true;
      msg.textContent = 'ยังไม่ได้บันทึก กดปิดอีกครั้งเพื่อทิ้งการแก้ไข หรือกดบันทึก';
      setTimeout(() => {confirming = false; msg.textContent = '';}, 6000);
    }
    x.onclick = cancel.onclick = requestClose;
    dlg.addEventListener('cancel', (e) => {if (snapshot() !== initial && !confirming) {e.preventDefault(); requestClose();}});

    form.addEventListener('input', (e) => {
      const t = e.target;
      if (t && t.getAttribute && t.getAttribute('aria-invalid')) {
        t.removeAttribute('aria-invalid');
        const n = d.getElementById(t.id + '_err') || ({'rpe_ticker.text': errText, 'rpe_image.image_url': errImg}[t.id]);
        if (n) n.textContent = '';
        if (!form.querySelector('[aria-invalid="true"]')) summary.textContent = '';
      }
    });

    form.onsubmit = (event) => {
      event.preventDefault();
      // validate
      const problems = [];
      const mark = (input, errNode, text) => {if (errNode) errNode.textContent = text || ''; if (input) {if (text) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');}};
      const name = inputs.command.value.trim();
      const taken = name && name !== previous && Object.keys(commands()).some(k => k.toLowerCase() === name.toLowerCase());
      let t = !name ? 'กรุณาใส่คำสั่งแชท เช่น !hi' : taken ? 'มีคำสั่งนี้อยู่แล้ว กรุณาใช้ชื่ออื่น' : /\s/.test(name) ? 'คำสั่งต้องไม่มีช่องว่าง' : '';
      mark(inputs.command, errCmd, t); if (t) problems.push([inputs.command, t]);
      const m = mode();
      t = (m !== 'image' && !inputs['ticker.text'].value.trim()) ? 'กรุณาใส่ข้อความที่จะแสดง' : '';
      mark(inputs['ticker.text'], errText, t); if (t) problems.push([inputs['ticker.text'], t]);
      t = (m !== 'ticker' && !inputs['image.image_url'].value.trim()) ? 'กรุณาใส่ลิงก์รูป หรือเลือกรูปจากเครื่อง' : '';
      mark(inputs['image.image_url'], errImg, t); if (t) problems.push([inputs['image.image_url'], t]);
      summary.textContent = problems.length ? 'ยังบันทึกไม่ได้ ' + problems.length + ' จุดที่ต้องแก้: ' + problems.map(p => p[1]).join(' / ') : '';
      if (problems.length) {problems[0][0].focus(); return;}

      const values = {};
      for (const [key, input] of Object.entries(inputs)) values[key] = input.type === 'checkbox' ? input.checked : input.type === 'number' ? num(input.value, 0) : input.value;
      for (const [key, value] of Object.entries(values)) {
        if (key.includes('.')) {const [group, k] = key.split('.'); payload[group][k] = value;}
        else if (!['command', 'cooldown', 'enabled'].includes(key)) payload[key] = value;
      }
      payload.ticker.enabled = m !== 'image';
      payload.image.enabled = m !== 'ticker';
      if (previous && previous !== name) delete commands()[previous];
      commands()[name] = {
        ...old,
        enabled: values.enabled,
        text: payload.ticker.enabled ? payload.ticker.text : '',
        imageUrl: payload.image.enabled ? payload.image.image_url : '',
        duration: Math.max(1, values.duration_sec),
        cooldown: Math.max(0, values.cooldown),
        legacyPayload: payload
      };
      saveCommands();
      focusAfter = '[data-edit="' + name + '"]';
      renderList();
      announce('บันทึกคำสั่ง ' + name + ' แล้ว');
      dlg.close();
    };

    dlg.onclose = () => {if (dlgLiveStop) dlgLiveStop(); else window.BP3_BUS?.emit('REPLIE_DISMISS', {}); dlgLiveStop = null; dlg.remove();};
    d.body.append(dlg);
    dlg.showModal();
    inputs.command.focus();
  };

  function init() {
    if (!document.getElementById('rpList')) return;
    bindDefaults();
    renderList();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true}); else init();
})();
