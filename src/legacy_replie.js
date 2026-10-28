/* Replie rendering preserved from broadcast playroom dev. */
(() => {
'use strict';
const isEditor=false;
let _currentReplieTimeout = null;
let _currentReplieEl = null;

function renderReplieInto(inner) {
  if (!inner) return;
  // inner serves as container for replie-wrapper
}

function getReplieContainers() {
  const inners = document.querySelectorAll('.widget.type-replie .widget-inner');
  if (inners.length > 0) {
    return Array.from(inners);
  }
  const fallback = document.getElementById('replie-layer');
  return fallback ? [fallback] : [];
}

let _guideLinesTimer = null;

function showReplieGuideLines(posX, posY) {
  const guide = document.getElementById('replie-guide-lines');
  if (!guide) return;
  const guideH = document.getElementById('replieGuideH');
  const guideV = document.getElementById('replieGuideV');

  guide.style.opacity = '1';

  // Highlight snapped gold when near center (48% - 52%)
  const isCenterV = Math.abs(posX - 50) <= 2;
  const isCenterH = Math.abs(posY - 50) <= 2;
  if (guideV) guideV.classList.toggle('snapped', isCenterV);
  if (guideH) guideH.classList.toggle('snapped', isCenterH);

  if (_guideLinesTimer) {
    clearTimeout(_guideLinesTimer);
  }
  _guideLinesTimer = setTimeout(() => {
    guide.style.opacity = '0';
  }, 1400);
}

let _currentReplieTimers = [];

function clearAllReplieTimers() {
  if (_currentReplieTimers && _currentReplieTimers.length > 0) {
    _currentReplieTimers.forEach(t => clearTimeout(t));
    _currentReplieTimers = [];
  }
}

function updateRepliePositionLive(data) {
  if (!data) return;
  const target = data.target || 'all';

  const posX = (data.pos_x !== null && data.pos_x !== undefined) ? data.pos_x : 50;
  const posY = (data.pos_y !== null && data.pos_y !== undefined) ? data.pos_y : 50;
  const offX = data.offset_x || 0;
  const offY = data.offset_y || 0;
  const scale = data.scale || 1.0;
  const opacity = (data.opacity !== undefined) ? data.opacity : 0.95;

  // Show guide lines on canvas
  showReplieGuideLines(posX, posY);

  const selector = target === 'ticker' ? '.replie-el-ticker' : (target === 'image' ? '.replie-el-image' : '.replie-wrapper');
  const wrappers = document.querySelectorAll(selector);
  if (!wrappers || wrappers.length === 0) return;

  wrappers.forEach(wrap => {
    const layout = wrap.dataset.layout || 'side_card';
    wrap.style.opacity = opacity;
    wrap.style.transformOrigin = `${posX}% ${posY}%`;

    if (layout === 'full_ticker') {
      wrap.style.top = `${posY}%`;
      wrap.style.transform = `translateY(calc(-1 * ${posY}%)) translateY(${offY}px) scale(${scale})`;
    } else {
      wrap.style.left = `${posX}%`;
      wrap.style.top = `${posY}%`;
      wrap.style.transform = `translate(calc(-1 * ${posX}%), calc(-1 * ${posY}%)) translate(${offX}px, ${offY}px) scale(${scale})`;
    }
  });
}

function mountReplieElement(type, elData, durSec, progStyle, isLoop, skipAnimIn) {
  const containers = getReplieContainers();
  if (!containers || containers.length === 0) return;

  const wrap = document.createElement('div');
  wrap.className = `replie-wrapper replie-el-${type}`;
  const layout = elData.layout || (type === 'ticker' ? 'bottom_ticker' : 'card');
  wrap.dataset.layout = layout;

  const posX = elData.pos_x !== undefined && elData.pos_x !== null ? elData.pos_x : (type === 'ticker' ? 50 : 85);
  const posY = elData.pos_y !== undefined && elData.pos_y !== null ? elData.pos_y : (type === 'ticker' ? 88 : 50);
  const offX = elData.offset_x || 0;
  const offY = elData.offset_y || 0;
  const scale = elData.scale || 1.0;
  const opacity = (elData.opacity !== undefined) ? elData.opacity : 0.95;
  const animIn = elData.anim_in || (type === 'ticker' ? 'slide-up' : 'slide-left');
  wrap.dataset.animOut = elData.anim_out || (type === 'ticker' ? 'slide-down' : 'slide-right');

  const box = document.createElement('div');
  if (!skipAnimIn && animIn) {
    box.classList.add(`replie-in-${animIn}`);
  }
  if (elData.frameless) {
    box.classList.add('replie-frameless');
  }

  const cdType = elData.countdown_type || 'number';
  const animStyle = elData.anim_style || 'together';

  if (type === 'ticker') {
    if (layout === 'full_ticker') {
      wrap.classList.add('replie-full-ticker-wrap');
      wrap.style.left = '0';
      wrap.style.right = '0';
      wrap.style.width = '100%';
      wrap.style.top = `${posY}%`;
      wrap.style.transformOrigin = `50% ${posY}%`;
      wrap.style.transform = `translateY(calc(-1 * ${posY}%)) translateY(${offY}px) scale(${scale})`;

      box.className = 'replie-ticker replie-full-ticker' + (elData.frameless ? ' replie-frameless' : '');
      if (!skipAnimIn && animIn) {
        box.classList.add(`replie-in-${animIn}`);
      }

      if (elData.title && elData.title.trim()) {
        const badge = document.createElement('span');
        badge.className = 'replie-badge';
        badge.textContent = elData.title.trim();
        box.appendChild(badge);
      }

      const track = document.createElement('div');
      track.className = 'replie-danmaku-track';
      const textEl = document.createElement('div');
      textEl.className = 'replie-danmaku-text ' + (isLoop ? 'replie-danmaku-loop' : 'replie-danmaku-once');
      textEl.textContent = elData.text || '';
      if (elData.ticker_font_size) textEl.style.fontSize = `${elData.ticker_font_size}px`;
      if (elData.ticker_font) textEl.style.fontFamily = `"${elData.ticker_font}", sans-serif`;
      if (elData.ticker_color) textEl.style.color = elData.ticker_color;
      if (elData.ticker_bold !== undefined) textEl.style.fontWeight = elData.ticker_bold ? '700' : '400';
      track.appendChild(textEl);
      box.appendChild(track);
    } else {
      wrap.style.left = `${posX}%`;
      wrap.style.top = `${posY}%`;
      wrap.style.transformOrigin = `${posX}% ${posY}%`;
      wrap.style.transform = `translate(calc(-1 * ${posX}%), calc(-1 * ${posY}%)) translate(${offX}px, ${offY}px) scale(${scale})`;

      box.className = 'replie-ticker' + (elData.frameless ? ' replie-frameless' : '');
      if (!skipAnimIn && animIn) {
        box.classList.add(`replie-in-${animIn}`);
      }

      if (elData.title && elData.title.trim()) {
        const badge = document.createElement('span');
        badge.className = 'replie-badge';
        badge.textContent = elData.title.trim();
        box.appendChild(badge);
      }

      const track = document.createElement('div');
      track.className = 'replie-ticker-track';

      const txt = document.createElement('div');
      txt.className = 'replie-ticker-text';
      txt.textContent = elData.text || '';
      if (elData.ticker_font_size) txt.style.fontSize = `${elData.ticker_font_size}px`;
      if (elData.ticker_font) txt.style.fontFamily = `"${elData.ticker_font}", sans-serif`;
      if (elData.ticker_color) txt.style.color = elData.ticker_color;
      if (elData.ticker_bold !== undefined) txt.style.fontWeight = elData.ticker_bold ? '700' : '400';
      track.appendChild(txt);
      box.appendChild(track);
    }

    // Countdown Display for Ticker (แสดงทั้งแบบมีกรอบและไร้กรอบ)
    if (cdType !== 'none') {
      if (cdType === 'bar') {
        const bar = document.createElement('div');
        bar.className = `replie-progress-bar prog-${progStyle || 'cyan'}`;
        bar.style.animationDuration = `${durSec}s`;
        bar.style.setProperty('--cd-dur', `${durSec}s`);
        box.appendChild(bar);
      } else if (cdType === 'number') {
        const numBadge = document.createElement('div');
        numBadge.className = 'replie-countdown-number';
        if (elData.countdown_font) numBadge.style.fontFamily = `"${elData.countdown_font}", sans-serif`;
        if (elData.countdown_color) numBadge.style.color = elData.countdown_color;
        if (elData.countdown_shadow === false) {
          numBadge.style.textShadow = 'none';
        } else {
          numBadge.style.textShadow = '0 0 6px rgba(0,0,0,0.85), 0 2px 4px rgba(0,0,0,0.9)';
        }
        numBadge.innerHTML = `<span class="replie-cd-icon">⏱️</span> <span class="replie-cd-val">${Math.ceil(durSec)}</span>s`;
        box.appendChild(numBadge);
      }
    }
  } else {
    // Image Element
    wrap.style.left = `${posX}%`;
    wrap.style.top = `${posY}%`;
    wrap.style.transformOrigin = `${posX}% ${posY}%`;
    wrap.style.transform = `translate(calc(-1 * ${posX}%), calc(-1 * ${posY}%)) translate(${offX}px, ${offY}px) scale(${scale})`;

    box.className = 'replie-card' + (elData.frameless ? ' replie-frameless' : '');
    if (!skipAnimIn && animIn) {
      box.classList.add(`replie-in-${animIn}`);
    }

    // If framed image has top text
    if (!elData.frameless && elData.top_text && elData.top_text.trim()) {
      const topTitle = document.createElement('div');
      topTitle.className = 'replie-card-title';
      topTitle.textContent = elData.top_text.trim();
      box.appendChild(topTitle);
    }

    if (elData.image_url) {
      const img = document.createElement('img');
      img.className = 'replie-card-image';
      img.src = elData.image_url;
      box.appendChild(img);
    }

    // If framed image has bottom text
    if (!elData.frameless && elData.bottom_text && elData.bottom_text.trim()) {
      const botCaption = document.createElement('div');
      botCaption.className = 'replie-card-caption';
      botCaption.textContent = elData.bottom_text.trim();
      box.appendChild(botCaption);
    }

    // Countdown Display for Image (แสดงทั้งแบบมีกรอบและไร้กรอบ)
    if (cdType !== 'none') {
      if (cdType === 'bar') {
        const bar = document.createElement('div');
        bar.className = `replie-progress-bar prog-${progStyle || 'cyan'}`;
        bar.style.animationDuration = `${durSec}s`;
        bar.style.setProperty('--cd-dur', `${durSec}s`);
        box.appendChild(bar);
      } else if (cdType === 'number') {
        const numBadge = document.createElement('div');
        numBadge.className = 'replie-countdown-number';
        if (elData.countdown_font) numBadge.style.fontFamily = `"${elData.countdown_font}", sans-serif`;
        if (elData.countdown_color) numBadge.style.color = elData.countdown_color;
        if (elData.countdown_shadow === false) {
          numBadge.style.textShadow = 'none';
        } else {
          numBadge.style.textShadow = '0 0 6px rgba(0,0,0,0.85), 0 2px 4px rgba(0,0,0,0.9)';
        }
        numBadge.innerHTML = `<span class="replie-cd-icon">⏱️</span> <span class="replie-cd-val">${Math.ceil(durSec)}</span>s`;
        box.appendChild(numBadge);
      }
    }
  }

  wrap.style.opacity = opacity;
  wrap.appendChild(box);

  containers.forEach(c => {
    const node = wrap.cloneNode(true);
    c.appendChild(node);

    // Dynamic Animation Handling on Live Mounted DOM Node
    if (type === 'ticker' && layout !== 'full_ticker') {
      const track = node.querySelector('.replie-ticker-track');
      const txt = node.querySelector('.replie-ticker-text');
      if (track && txt) {
        if (animStyle === 'staged_slide') {
          // กรอบขึ้นมาก่อน แล้วข้อความค่อยๆ ไหลมาจากขวาสุดของกรอบแบบช้าๆ สมูทๆ จนกว่าจะจบข้อความ หายไปทางซ้ายหมด
          txt.style.opacity = '0';
          _currentReplieTimers.push(setTimeout(() => {
            if (!track.isConnected) return;
            const trackW = track.clientWidth || 360;
            const textW = txt.scrollWidth || 200;
            const totalDistance = trackW + textW;
            txt.style.opacity = '1';

            // ความเร็วสม่ำเสมอ สมูท ไม่เร็วและไม่ช้าเกินไป (~65px/วินาที)
            const remainSec = Math.max(3.5, durSec - 0.7);
            const computedSec = Math.min(remainSec, Math.max(4.0, totalDistance / 65.0));
            const animDur = Math.max(computedSec, remainSec) * 1000;

            txt.animate([
              { transform: `translateX(${trackW}px)` },
              { transform: `translateX(-${textW}px)` }
            ], {
              duration: animDur,
              easing: 'linear',
              fill: 'forwards'
            });
          }, 380));
        } else if (animStyle === 'staged_fade') {
          // สไลด์กรอบขึ้นมาก่อน แล้วข้อความค่อยๆ Fade ปรากฏ
          txt.style.opacity = '0';
          _currentReplieTimers.push(setTimeout(() => {
            if (!track.isConnected) return;
            txt.animate([
              { opacity: 0, transform: 'scale(0.97)' },
              { opacity: 1, transform: 'scale(1)' }
            ], {
              duration: 450,
              easing: 'ease-out',
              fill: 'forwards'
            });
            txt.style.opacity = '1';

            // หากข้อความยาวเกินกล่อง หลังจากขึ้นมาแล้ว 5 วิ ให้เลื่อนดูข้อความส่วนที่เหลือ
            _currentReplieTimers.push(setTimeout(() => {
              if (!track.isConnected) return;
              const trackW = track.clientWidth || 360;
              const textW = txt.scrollWidth || 200;
              const overflow = textW - trackW;
              if (overflow > 15) {
                const scrollDist = overflow + 24;
                const remainSec = Math.max(3.0, durSec - 5.8);
                const scrollDur = Math.min(remainSec * 1000, Math.max(3000, (scrollDist / 50.0) * 1000));
                txt.animate([
                  { transform: 'translateX(0px)' },
                  { transform: `translateX(-${scrollDist}px)` }
                ], {
                  duration: scrollDur,
                  easing: 'ease-in-out',
                  fill: 'forwards'
                });
              }
            }, 4600));
          }, 380));
        } else {
          // together mode: กรอบและข้อความขึ้นมาพร้อมกันทันที
          // ถ้าข้อความยาวกว่ากล่อง: แสดงข้อความแรกๆ ซัก 5 วิ แล้วค่อยๆ scroll ไปทางซ้ายเพื่อให้เห็นข้อความครบ
          txt.style.opacity = '1';
          _currentReplieTimers.push(setTimeout(() => {
            if (!track.isConnected) return;
            const trackW = track.clientWidth || 360;
            const textW = txt.scrollWidth || 200;
            const overflow = textW - trackW;

            if (overflow > 15) {
              // ค้างไว้ 5 วิ ให้ผู้ชมอ่านข้อความส่วนต้นได้สบายๆ
              _currentReplieTimers.push(setTimeout(() => {
                if (!track.isConnected) return;
                const scrollDist = overflow + 24;
                const remainSec = Math.max(3.0, durSec - 5.8);
                const scrollDur = Math.min(remainSec * 1000, Math.max(3000, (scrollDist / 50.0) * 1000));

                txt.animate([
                  { transform: 'translateX(0px)' },
                  { transform: `translateX(-${scrollDist}px)` }
                ], {
                  duration: scrollDur,
                  easing: 'ease-in-out',
                  fill: 'forwards'
                });
              }, 4600));
            }
          }, 400));
        }
      }
    }

    // Countdown Display Timer
    if (cdType === 'number') {
      const valEl = node.querySelector('.replie-cd-val');
      if (valEl) {
        let remSec = Math.ceil(durSec);
        const cdTimer = setInterval(() => {
          remSec--;
          if (remSec < 0) {
            clearInterval(cdTimer);
            return;
          }
          valEl.textContent = remSec;
        }, 1000);
        _currentReplieTimers.push(cdTimer);
      }
    }
  });
}

function renderReplieOverlay(data) {
  if (!data) return;
  const containers = getReplieContainers();
  if (!containers || containers.length === 0) return;

  clearAllReplieTimers();
  containers.forEach(c => { c.innerHTML = ''; });

  const isTestIn = (data.test_mode === 'in');
  const isTestOut = (data.test_mode === 'out');
  const totalDur = (isTestIn || isTestOut) ? 3 : (data.duration_sec || 15);
  const progStyle = data.progress_style || 'cyan';

  // Resolve Ticker Data
  let tickerData = null;
  if (data.ticker && data.ticker.enabled) {
    tickerData = data.ticker;
  } else if (!data.ticker && (data.type !== 'image' && (data.text || data.title))) {
    tickerData = {
      enabled: true,
      title: data.title,
      text: data.text,
      layout: data.layout || 'bottom_ticker',
      anim_style: data.ticker_anim_style || 'together',
      frameless: data.frameless,
      pos_x: data.pos_x !== undefined ? data.pos_x : 50,
      pos_y: data.pos_y !== undefined ? data.pos_y : 88,
      scale: data.scale || 1.0,
      opacity: data.opacity !== undefined ? data.opacity : 0.95,
      anim_in: data.anim_in || 'slide-up',
      anim_out: data.anim_out || 'slide-down',
      delay_sec: 0,
    };
  }

  // Resolve Image Data
  let imageData = null;
  if (data.image && data.image.enabled) {
    imageData = data.image;
  } else if (!data.image && (data.type === 'image' || data.image_url)) {
    imageData = {
      enabled: true,
      image_url: data.image_url,
      frameless: data.frameless !== undefined ? data.frameless : true,
      pos_x: data.pos_x !== undefined ? data.pos_x : 85,
      pos_y: data.pos_y !== undefined ? data.pos_y : 50,
      scale: data.scale || 1.0,
      opacity: data.opacity !== undefined ? data.opacity : 0.95,
      anim_in: data.anim_in || 'slide-left',
      anim_out: data.anim_out || 'slide-right',
      delay_sec: 0,
    };
  }

  // Mount Ticker
  if (tickerData) {
    const tDelay = isTestOut ? 0 : Math.max(0, (tickerData.delay_sec || 0) * 1000);
    const tLife = Math.max(1, totalDur - (isTestOut ? 0 : (tickerData.delay_sec || 0)));
    if (tDelay === 0) {
      mountReplieElement('ticker', tickerData, tLife, progStyle, data.is_loop, isTestOut);
    } else {
      _currentReplieTimers.push(setTimeout(() => {
        mountReplieElement('ticker', tickerData, tLife, progStyle, data.is_loop, isTestOut);
      }, tDelay));
    }
  }

  // Mount Image
  if (imageData) {
    const iDelay = isTestOut ? 0 : Math.max(0, (imageData.delay_sec || 0) * 1000);
    const iLife = Math.max(1, totalDur - (isTestOut ? 0 : (imageData.delay_sec || 0)));
    if (iDelay === 0) {
      mountReplieElement('image', imageData, iLife, progStyle, data.is_loop, isTestOut);
    } else {
      _currentReplieTimers.push(setTimeout(() => {
        mountReplieElement('image', imageData, iLife, progStyle, data.is_loop, isTestOut);
      }, iDelay));
    }
  }

  // Synchronized Finish: เมื่อหมดเวลา totalDur ให้เล่น anim_out และปิด Overlay (ยกเว้นโหมด in_hold)
  if (!data.is_loop && data.test_mode !== 'in_hold') {
    _currentReplieTimers.push(setTimeout(() => {
      dismissReplieOverlay();
    }, totalDur * 1000));
  }
}

function dismissReplieOverlay() {
  clearAllReplieTimers();
  const containers = getReplieContainers();
  if (!containers || containers.length === 0) return;

  containers.forEach(c => {
    const wrappers = c.querySelectorAll('.replie-wrapper');
    wrappers.forEach(wrap => {
      const animOut = wrap.dataset.animOut || 'slide-right';
      const box = wrap.querySelector('.replie-ticker, .replie-card');
      if (box) {
        box.className = box.className.replace(/replie-in-\S+/g, '');
        box.classList.add(`replie-out-${animOut}`);
      }
    });
  });

  setTimeout(() => {
    containers.forEach(c => { c.innerHTML = ''; });
  }, 380);
}

window.BP3LegacyReplie={
 render(data){
   document.querySelectorAll('.widget.type-replie').forEach(el=>{let inner=el.querySelector('.widget-inner');if(!inner){inner=document.createElement('div');inner.className='widget-inner composer-widget-inner';inner.style.cssText='position:relative;width:100%;height:100%;background:transparent;border:none;';el.replaceChildren(inner);}});
   if(!document.querySelector('.widget.type-replie')){let layer=document.getElementById('replie-layer');if(!layer){layer=document.createElement('div');layer.id='replie-layer';(document.getElementById('obsCanvasStage') || document.getElementById('composerCanvasStage'))?.append(layer);}}
   if(data.legacyPayload){renderReplieOverlay({...data.legacyPayload,duration_sec:data.legacyPayload.duration_sec || data.duration || 8});return;}
   const positions={'top-left':[5,10],'top':[50,10],'top-right':[95,10],'left':[5,50],'center':[50,50],'right':[95,50],'bottom-left':[5,90],'bottom':[50,90],'bottom-right':[95,90]};
   const [x,y]=positions[data.anchor] || positions['bottom-right'];
   const shared={pos_x:x,pos_y:y,scale:(Number(data.scale)||100)/100,opacity:.95};
   renderReplieOverlay({duration_sec:data.duration || 4,is_loop:data.isLoop || false,
     ticker:{...shared,enabled:Boolean(data.text),text:data.text,title:data.title || '',layout:'bottom_ticker',anim_style:'together',anim_in:'slide-up',anim_out:'slide-down'},
     image:{...shared,enabled:Boolean(data.imageUrl),image_url:data.imageUrl,frameless:true,anim_in:'slide-left',anim_out:'slide-right'}
   });
 },dismiss(){dismissReplieOverlay();}
};
})();
