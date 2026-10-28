/* Original legacy Emote Party physics, bounded and stopped when idle. */
(()=>{'use strict';
const _epActive=[];let _epRafId=null;
function _spawnEmote(inner, w, em) {
  const size = w.ep_emote_size || 64;
  const animType = w.ep_animation || 'float';
  const ttl = (w.ep_duration || 5) * 1000;  // ms
  const now = performance.now();
  const rect = inner.getBoundingClientRect();
  const W = rect.width || 400;
  const H = rect.height || 300;

  const el = document.createElement('div');
  el.style.cssText = 'position:absolute;will-change:transform,opacity;pointer-events:none;display:flex;align-items:center;justify-content:center;';
  el.style.width = size + 'px';
  el.style.height = size + 'px';
  // ★ content — image หรือ text (emoji)
  if (em.url) {
    const img = document.createElement('img');
    img.src = em.url;
    // ★ width/height 100% บังคับให้รูปเต็ม container (ตาม ep_emote_size)
    //    ใช้ max-width/max-height อย่างเดียวไม่พอ — รูปเล็กจะไม่ถูกขยาย
    img.style.cssText = 'width:100%;height:100%;object-fit:contain;';
    img.onerror = () => { try { el.remove(); } catch(e){} };
    el.appendChild(img);
  } else if (em.text) {
    el.textContent = em.text;
    el.style.fontSize = (size * 0.8) + 'px';
    el.style.lineHeight = '1';
  } else {
    return;  // ไม่มี content → skip
  }
  el.dataset.liveEmote='true';el.dataset.emoteAnimation=animType;
  inner.appendChild(el);

  // ★ วัดขนาดจริง (หลัง append) เพื่อคำนวณ physics แบบแม่นยำ
  const ew = el.offsetWidth || size;
  const eh = el.offsetHeight || size;

  // ★ ตั้งค่า physics ตาม animation type
  let item = {
    el: el,
    widgetId: w.id,
    animType: animType,
    born: now,
    ttl: ttl,
    config: w,
  };

  if (animType === 'float') {
    // 🎈 Float — เริ่มจากด้านล่าง ลอยขึ้นบน + แกว่งซ้ายขวา
    item.x = Math.random() * Math.max(1, W - ew);
    item.y = H;  // เริ่มใต้กรอบ
    item.vx = (Math.random() - 0.5) * 30;   // px/s แนวนอน
    item.vy = -(40 + Math.random() * 30);    // px/s ขึ้นบน
    item.swayPhase = Math.random() * Math.PI * 2;
    item.swayAmp = 20 + Math.random() * 20;
  } else if (animType === 'dvd') {
    // 📺 DVD Bounce — เริ่มกลางจอ + ความเร็วคงที่ เด้งติดผนัง
    item.x = (W - ew) / 2 + (Math.random() - 0.5) * Math.min(W * 0.3, 100);
    item.y = (H - eh) / 2 + (Math.random() - 0.5) * Math.min(H * 0.3, 100);
    const speed = 80 + Math.random() * 40;
    const angle = Math.random() * Math.PI * 2;
    item.vx = Math.cos(angle) * speed;
    item.vy = Math.sin(angle) * speed;
    item.W = W; item.H = H; item.ew = ew; item.eh = eh;
  } else if (animType === 'drop') {
    // 💥 Pop & Drop — โผล่กลางจอ (pop) แล้วตกลงข้างล่าง (gravity)
    item.x = Math.random() * Math.max(1, W - ew);
    item.y = Math.random() * Math.max(1, H * 0.4);  // เริ่มด้านบน
    item.vx = (Math.random() - 0.5) * 20;
    item.vy = 0;
    item.gravity = 200;  // px/s²
    item.bounceDamping = 0.5;
    item.W = W; item.H = H; item.ew = ew; item.eh = eh;
    item.popStart = now;
    item.popDur = 200;  // ms — ขยายจาก 0 → 1
  } else if (animType === 'shake') {
    // 🌀 Shake/Spin — สุ่มตำแหน่ง + หมุน + สั่น
    item.x = Math.random() * Math.max(1, W - ew);
    item.y = Math.random() * Math.max(1, H - eh);
    item.rot = 0;
    item.vrot = (Math.random() - 0.5) * 360;  // deg/s
    item.shakePhase = Math.random() * Math.PI * 2;
    item.shakeAmpX = 5 + Math.random() * 10;
    item.shakeAmpY = 5 + Math.random() * 10;
    item.shakeFreq = 8 + Math.random() * 6;  // Hz
  }

  // ★ วาดตำแหน่งเริ่มต้น
  _drawEmote(item, now);
  _epActive.push(item);
}

// ★ วาด emote ตาม physics state (ปัจจุบัน)
function _drawEmote(item, now) {
  const age = now - item.born;
  const lifeRatio = age / item.ttl;
  let opacity = 1;
  // ★ fade-in 10% แรก, fade-out 20% สุดท้าย
  if (lifeRatio < 0.1) opacity = lifeRatio / 0.1;
  else if (lifeRatio > 0.8) opacity = Math.max(0, (1 - lifeRatio) / 0.2);

  let tx = item.x || 0;
  let ty = item.y || 0;
  let rot = item.rot || 0;
  let scale = 1;

  if (item.animType === 'shake') {
    // ★ เพิ่ม shake offset
    const t = (now - item.born) / 1000;
    tx += Math.sin(t * item.shakeFreq * Math.PI + item.shakePhase) * item.shakeAmpX;
    ty += Math.cos(t * item.shakeFreq * Math.PI + item.shakePhase) * item.shakeAmpY;
  }

  if (item.animType === 'drop') {
    // ★ pop-in (scale 0→1) ตอนเริ่ม
    if (item.popStart != null) {
      const popAge = now - item.popStart;
      if (popAge < item.popDur) {
        scale = popAge / item.popDur;
      }
    }
  }

  item.el.style.opacity = opacity.toFixed(3);
  item.el.style.transform = 'translate(' + tx.toFixed(1) + 'px,' + ty.toFixed(1) + 'px) rotate(' + rot.toFixed(1) + 'deg) scale(' + scale.toFixed(3) + ')';
}

// ★ update physics ตามเวลาที่ผ่านไป (dt = seconds)
function _updatePhysics(item, dt, now) {
  if (item.animType === 'float') {
    item.x += item.vx * dt;
    item.y += item.vy * dt;
    // ★ sway แนวนอน
    const swayT = (now - item.born) / 1000;
    const sway = Math.sin(swayT * 2 + item.swayPhase) * item.swayAmp;
    item.el.style.transform = 'translate(' + (item.x + sway).toFixed(1) + 'px,' + item.y.toFixed(1) + 'px)';
  } else if (item.animType === 'dvd') {
    item.x += item.vx * dt;
    item.y += item.vy * dt;
    // ★ เด้งติดผนัง
    if (item.x <= 0) { item.x = 0; item.vx = Math.abs(item.vx); }
    else if (item.x >= item.W - item.ew) { item.x = item.W - item.ew; item.vx = -Math.abs(item.vx); }
    if (item.y <= 0) { item.y = 0; item.vy = Math.abs(item.vy); }
    else if (item.y >= item.H - item.eh) { item.y = item.H - item.eh; item.vy = -Math.abs(item.vy); }
  } else if (item.animType === 'drop') {
    item.vy += item.gravity * dt;
    item.x += item.vx * dt;
    item.y += item.vy * dt;
    // ★ เด้งพื้น (ครั้งเดียว — หลังจากนั้นให้หยุด)
    if (item.y >= item.H - item.eh) {
      item.y = item.H - item.eh;
      if (Math.abs(item.vy) > 30) {
        item.vy = -item.vy * item.bounceDamping;
      } else {
        item.vy = 0;
        item.vx *= 0.8;  // เสียดทาน
      }
    }
  } else if (item.animType === 'shake') {
    item.rot += item.vrot * dt;
  }
}

// ★ main animation loop — เรียก requestAnimationFrame เดียวรันทุก emote
function _epTick(now) {
  const dt = Math.min(0.05, (now - (_epLastTime || now)) / 1000);  // จำกัด dt กันกระตุก
  _epLastTime = now;
  // ★ update ทุก emote
  for (let i = _epActive.length - 1; i >= 0; i--) {
    const item = _epActive[i];
    const age = now - item.born;
    // ★ หมดอายุ → เอาออก
    if (!item.el.isConnected || age >= item.ttl) {
      _removeEmote(item);
      _epActive.splice(i, 1);
      continue;
    }
    _updatePhysics(item, dt, now);
    _drawEmote(item, now);
  }
  // ★ ถ้ายังมี emote → รันต่อ
  if (_epActive.length > 0) {
    _epRafId = requestAnimationFrame(_epTick);
  } else {
    _epRafId = null;
  }
}
let _epLastTime = 0;

function _ensureRafRunning() {
  if (_epRafId === null) {
    _epLastTime = performance.now();
    _epRafId = requestAnimationFrame(_epTick);
  }
}

function _removeEmote(item) {
  if (item && item.el) {
    try { item.el.remove(); } catch (e) {}
  }
}


function clear(){for(const item of _epActive)_removeEmote(item);_epActive.length=0;if(_epRafId!==null)cancelAnimationFrame(_epRafId);_epRafId=null;}
function show(widget,emotes){
 const inner=document.getElementById('widget-emote-party-'+widget.id);if(!inner)return;
 inner.style.position='relative';inner.style.overflow='hidden';
 const w={...widget,ep_animation:widget.epAnimation ?? widget.ep_animation ?? 'float',ep_duration:widget.epDuration ?? widget.ep_duration ?? 5,ep_emote_size:widget.epEmoteSize ?? widget.ep_emote_size ?? 64};
 if(!['float','dvd','drop','shake'].includes(w.ep_animation))w.ep_animation='float';
 const max=Math.max(1,Number(widget.epMaxEmotes ?? widget.ep_max_emotes ?? 15));
 for(const em of emotes){if(!em.url && (widget.epEmojiEnabled ?? widget.ep_emoji_enabled)===false)continue;
  while(_epActive.filter(item=>item.widgetId===w.id).length>=max){const index=_epActive.findIndex(item=>item.widgetId===w.id);_removeEmote(_epActive[index]);_epActive.splice(index,1);}
  _spawnEmote(inner,w,em);
 }if(_epActive.length)_ensureRafRunning();
}
window.BP3LegacyEmotes={show,clear,stats:()=>({active:_epActive.length,running:_epRafId!==null})};
window.addEventListener('pagehide',clear);
})();
