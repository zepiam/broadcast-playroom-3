// Original PNGTuber renderer and explicit TTS playback state.
(()=>{
'use strict';const isEditor=false;const _lastAvatarState={};let lastTalking=false;
const _avatarWidgets = {};  // {widget_id: {state, imgs, timers, ...}}

function setupAvatarWidget(inner, w) {
  const signature=JSON.stringify(Object.fromEntries(Object.entries(w).filter(([key])=>!['x','y','width','height','w','h','z','opacity'].includes(key))));if(inner._bpAvatarConfig===signature)return;inner._bpAvatarConfig=signature;
  // Keep the same live avatar images and talking state when settings change.
  inner.style.pointerEvents='none';

  const fitMode = w.avatar_fit_mode || 'contain';
  // ★ resolve URLs — ถ้า avatar_preset != "" ใช้ URL จาก preset แทน (man/girl default)
  const preset = w.avatar_preset || '';
  let idleUrl, talkUrl, blinkIdleUrl, blinkTalkUrl;
  if (preset && (preset === 'man' || preset === 'girl')) {
    idleUrl = `/avatar-preset/${preset}/idle`;
    talkUrl = `/avatar-preset/${preset}/talk`;
    blinkIdleUrl = `/avatar-preset/${preset}/blink_idle`;
    blinkTalkUrl = `/avatar-preset/${preset}/blink_talk`;
  } else {
    idleUrl = w.avatar_idle_url || '';
    talkUrl = w.avatar_talk_url || '';
    blinkIdleUrl = w.avatar_blink_idle_url || '';
    blinkTalkUrl = w.avatar_blink_talk_url || '';
  }

  const existing=_avatarWidgets[w.id];
  if(existing && inner.querySelector('.avatar-stage')){
    const urls={idle:idleUrl,talk:talkUrl,'blink-idle':blinkIdleUrl,'blink-talk':blinkTalkUrl};
    for(const [role,url] of Object.entries(urls)){const image=existing.imgs[role];image.style.objectFit=fitMode;if(existing.urls[role]!==url){existing.urls[role]=url;image.dataset.loaded='0';image.src=url || '';image.style.display=url?'':'none';}}
    const stage=inner.querySelector('.avatar-stage');stage.classList.toggle('avatar-anim-breathing',w.avatar_breathing!==false);stage.classList.toggle('avatar-anim-sway',w.avatar_sway!==false);
    inner.querySelector('.avatar-flip-wrap').style.transform=`scale(${w.avatar_flip_h?-1:1},${w.avatar_flip_v?-1:1})`;
    existing.bounceEnabled=w.avatar_bounce!==false;existing.blinkRate=w.avatar_blink_rate || 4;existing.mode=w.avatar_mode || 'tts';existing.setTalking(existing.state.talking);return;
  }
  if(existing)_destroyAvatarInstance(w.id);inner.innerHTML='';
  // placeholder ถ้ายังไม่มีภาพ
  if (!idleUrl && !talkUrl) {
    inner.innerHTML = '<div class="editor-only" style="display:flex;align-items:center;justify-content:center;height:100%;color:rgba(255,255,255,0.4);font-size:13px;text-align:center;padding:12px;">😊 Avatar<br><span style="font-size:11px;opacity:0.7;">กด ⚙ เพื่ออัปรูป</span></div>';
    return;
  }

  // ★ สร้าง stage + 4 imgs ซ้อนกัน (absolute ทั้งหมด → ใช้ opacity สลับ)
  const stage = document.createElement('div');
  stage.className = 'avatar-stage';
  if (w.avatar_breathing !== false) stage.classList.add('avatar-anim-breathing');
  if (w.avatar_sway !== false) stage.classList.add('avatar-anim-sway');
  stage.style.cssText = 'position:relative;width:100%;height:100%;';

  function _mkImg(url, cls) {
    const img = document.createElement('img');
    img.className = 'avatar-img ' + cls;
    // ★ ใช้ visibility แทน opacity — สลับทันที ไม่มี transition (กัน blink ดำระหว่าง fade)
    //   PNGTuber ต้องการการสลับที่ฉับพลัน ไม่ใช่ cross-fade
    img.style.cssText = `position:absolute;inset:0;width:100%;height:100%;object-fit:${fitMode};opacity:1;visibility:hidden;pointer-events:none;user-select:none;-webkit-user-drag:none;`;
    if (url) {
      img.src = url;
      img.alt = '';
      // ★ mark ว่ายังโหลดไม่เสร็จ (กัน blink ดำตอนสลับภาพ)
      img.dataset.loaded = '0';
      img.onload = () => { img.dataset.loaded = '1'; };
      // ★ error → mark loaded anyway (กันค้าง)
      img.onerror = () => { img.dataset.loaded = '1'; };
    } else {
      img.style.display = 'none';  // ไม่มีภาพนี้ → ซ่อน (fallback ใช้ idle แทน)
      img.dataset.loaded = '1';
    }
    return img;
  }

  const imgIdle = _mkImg(idleUrl, 'av-idle');
  const imgTalk = _mkImg(talkUrl, 'av-talk');
  const imgBlinkIdle = _mkImg(blinkIdleUrl, 'av-blink-idle');
  const imgBlinkTalk = _mkImg(blinkTalkUrl, 'av-blink-talk');
  // ★ default — แสดง idle เฉพาะตอนโหลดเสร็จแล้ว (กัน blink ดำตอนเริ่ม)
  if (imgIdle.dataset.loaded === '1') imgIdle.style.visibility = 'visible';
  else imgIdle.onload = () => { imgIdle.dataset.loaded = '1'; imgIdle.style.visibility = 'visible'; };
  stage.appendChild(imgIdle);
  stage.appendChild(imgTalk);
  stage.appendChild(imgBlinkIdle);
  stage.appendChild(imgBlinkTalk);
  // ★ flip wrapper — ห่อ stage เพื่อสะท้อนภาพ (ไม่ขัดกับ breathing/sway/bounce animation)
  const flipWrap = document.createElement('div');
  flipWrap.className = 'avatar-flip-wrap';
  flipWrap.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
  const flipX = w.avatar_flip_h ? -1 : 1;
  const flipY = w.avatar_flip_v ? -1 : 1;
  if (flipX !== 1 || flipY !== 1) {
    flipWrap.style.transform = `scale(${flipX}, ${flipY})`;
  }
  flipWrap.appendChild(stage);
  inner.appendChild(flipWrap);

  // ★ instance state
  const inst = {
    widgetId: w.id,
    mode: w.avatar_mode || 'tts',
    imgs: { idle: imgIdle, talk: imgTalk, 'blink-idle': imgBlinkIdle, 'blink-talk': imgBlinkTalk },
    urls: { idle: idleUrl, talk: talkUrl, 'blink-idle': blinkIdleUrl, 'blink-talk': blinkTalkUrl },
    state: { talking: false, blinking: false },
    blinkRate: w.avatar_blink_rate || 4,
    bounceEnabled: w.avatar_bounce !== false,
    blinkTimer: null,
    talkTimer: null,
    micStream: null,
    micCtx: null,
    micRaf: null,
    micThreshold: (w.avatar_mic_threshold != null) ? w.avatar_mic_threshold : 30,
    micDeviceId: w.avatar_mic_device || '',
  };
  _avatarWidgets[w.id] = inst;

  // ★ เลือกภาพที่จะแสดงจาก state {talking, blinking}
  // ★ helper — แสดงภาพ target โดยไม่เกิดช่องว่างดำ
  //   ★ ใช้ visibility แทน opacity — สลับทันที ไม่มี transition (กัน blink ดำระหว่าง fade)
  //   ถ้า target ยังโหลดไม่เสร็จ → ถือภาพเก่าไว้ (กัน blink ดำ)
  function _showOnly(targetKey) {
    const targetImg = inst.imgs[targetKey];
    // ★ ถ้า target ยังโหลดไม่เสร็จ → อย่าสลับ (ถือภาพเดิมไว้ กัน blink ดำ)
    if (targetImg && targetImg.dataset.loaded !== '1') return;
    // ★ สลับ visibility ทันที — ไม่มี transition จึงไม่มีช่องว่างดำ
    for (const k in inst.imgs) {
      inst.imgs[k].style.visibility = (k === targetKey) ? 'visible' : 'hidden';
    }
  }

  function _pickImage() {
    const { talking, blinking } = inst.state;
    let key;
    if (blinking && talking) key = 'blink-talk';
    else if (blinking && !talking) key = 'blink-idle';
    else if (!blinking && talking) key = 'talk';
    else key = 'idle';
    // ★ fallback: ถ้าไม่มีภาพ blink ให้ใช้ภาพหลัก (idle/talk)
    if (!inst.urls[key]) {
      key = talking ? 'talk' : 'idle';
    }
    // ★ ถ้าไม่มี talk ด้วย → ใช้ idle
    if (!inst.urls[key]) key = 'idle';
    _showOnly(key);
    // ★ bounce class — ตอน talking ถ้าเปิดไว้
    if (inst.bounceEnabled && talking) {
      stage.classList.add('avatar-anim-bounce');
    } else {
      stage.classList.remove('avatar-anim-bounce');
    }
  }

  // ★ auto-blink — schedule สุ่ม blinkRate ± 2s → blink 150ms → idle ใหม่
  function _scheduleBlink() {
    if(_avatarWidgets[w.id]!==inst)return;
    const base = inst.blinkRate;
    const delay = Math.max(800, (base + (Math.random() * 4 - 2)) * 1000);
    inst.blinkTimer = setTimeout(() => {
      if(_avatarWidgets[w.id]!==inst)return;
      inst.state.blinking = true;
      _pickImage();
      setTimeout(() => {
        if(_avatarWidgets[w.id]!==inst)return;
        inst.state.blinking = false;
        _pickImage();
        _scheduleBlink();
      }, 150);
    }, delay);
  }
  _scheduleBlink();

  // ★ talk animation — ตอน talking=true สลับ idle↔talk ทุก ~150ms (ดูเหมือนปากพะงาบ)
  //   ทำงานเฉพาะตอน talking — สร้างความรู้สึกว่ากำลังพูด (ไม่ใช่ภาพปากเปิดนิ่งๆ)
  //   ★ ใช้ _showOnly (cross-fade safe — กัน blink ดำ)
  function _startTalkFlicker() {
    if (inst.talkTimer) return;
    let toggle = false;
    inst.talkTimer = setInterval(() => {
      if (!inst.state.talking) return;
      toggle = !toggle;
      const { blinking } = inst.state;
      const key = toggle ? (blinking ? 'blink-talk' : 'talk') : (blinking ? 'blink-idle' : 'idle');
      const fallback = toggle ? 'talk' : 'idle';
      const finalKey = inst.urls[key] ? key : fallback;
      _showOnly(finalKey);
    }, 150);
  }
  function _stopTalkFlicker() {
    if (inst.talkTimer) { clearInterval(inst.talkTimer); inst.talkTimer = null; }
  }

  // ★ set talking state (จาก WS push หรือ mic RMS)
  inst.setTalking = function(talking) {
    talking = !!talking;
    if (inst.state.talking === talking) return;  // no change
    inst.state.talking = talking;
    if (talking) _startTalkFlicker();
    else _stopTalkFlicker();
    _pickImage();
  };

  // ★ Mic mode — Python (PyAudio) วัดเสียงแล้ว push talking state มาทาง WS
  //   เหมือน TTS mode ทุกอย่าง — browser ไม่ต้องทำอะไร (ลดความซับซ้อน)
  //   ★ editor mode — แสดง badge ว่า Python กำลังวัดเสียง
  if (inst.mode === 'mic' && isEditor) {
    const badge = document.createElement('div');
    badge.style.cssText = 'position:absolute;bottom:6px;left:6px;right:6px;background:rgba(59,130,246,0.9);color:#fff;font-size:10px;padding:4px 8px;border-radius:4px;text-align:center;pointer-events:none;';
    badge.textContent = '🎤 Python วัดเสียง — ดูระดับได้ใน ⚙ Settings';
    stage.appendChild(badge);
  }

  // ★ ถ้ามี last avatar state สำหรับ widget นี้ (TTS/Mic mode reconnect) → restore
  if (_lastAvatarState && _lastAvatarState[w.id]) {
    inst.setTalking(true);
  }
}

// ★ WS handler — รับ push จากโปรแกรม (ทั้ง TTS mode และ Mic mode)
//   ★ Mic mode ใช้ Python วัดเสียงแล้ว push talking state มาทางนี้
//     (แก้ปัญหา OBS Browser Source เข้าถึงไมค์ไม่ได้)
function _destroyAvatarInstance(widgetId) {
  const inst = _avatarWidgets[widgetId];
  if (!inst) return;
  if (inst.blinkTimer) clearTimeout(inst.blinkTimer);
  if (inst.talkTimer) clearInterval(inst.talkTimer);
  if (inst.micRaf) cancelAnimationFrame(inst.micRaf);
  if (inst.micStream) {
    inst.micStream.getTracks().forEach(t => t.stop());
  }
  if (inst.micCtx) {
    try { inst.micCtx.close(); } catch(e) {}
  }
  delete _avatarWidgets[widgetId];
}


function receive(data){
 if(data.widget_id){_lastAvatarState[data.widget_id]=!!data.talking;_avatarWidgets[data.widget_id]?.setTalking(!!data.talking);return;}
 lastTalking=!!data.talking;Object.values(_avatarWidgets).forEach(inst=>{if(inst.mode!=='mic')inst.setTalking(lastTalking);});
}
window.addEventListener('bp3:remote-event',event=>{if(!window._overlayWidgets && event.detail?.event==='AVATAR_STATE')receive(event.detail.payload || {});});
window.BP3LegacyAvatar={
 dispose(){Object.keys(_avatarWidgets).forEach(_destroyAvatarInstance);},
 mount(){const widgets=(window._overlayWidgets || window.ComposerStudio?.getActivePage?.()?.widgets || []).filter(w=>w.type==='avatar' && !w.hidden);if(widgets.some(w=>(w.avatar_mode || w.avatarMode || 'tts')==='mic'))fetch('/api/avatar/sync').catch(()=>{});widgets.forEach(w=>{const inner=(document.getElementById('widget-'+w.id)?.querySelector('.composer-widget-inner') || document.querySelector('.widget[data-id="'+CSS.escape(String(w.id))+'"] .composer-widget-inner'));if(!inner)return;setupAvatarWidget(inner,w);if(_avatarWidgets[w.id]?.mode!=='mic')_avatarWidgets[w.id]?.setTalking(lastTalking);});},receive
};
})();
