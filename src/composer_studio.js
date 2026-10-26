/**
 * BROADCAST PLAYROOM 3.0 - IN-APP OVERLAY COMPOSER CANVAS STUDIO
 * Unified Canvas Studio & Full Widget Customizer with Real-Time Live Preview,
 * Interactive Demos, Context Menu Add, and Duplicate Prevention
 */

(function () {
  'use strict';

  const CANVAS_WIDTH = 1920;
  const CANVAS_HEIGHT = 1080;
  const STORAGE_KEY = 'bp_composer_studio_v3';

  // Application State
  const state = {
    pages: [
      {
        id: 'page-1',
        name: 'ฉากหลักสตรีม',
        widgets: [
          {
            id: 'w-chat-1',
            type: 'chat',
            title: 'กล่องแชทมาตรฐาน',
            chatMode: 'default',
            chatTheme: 'default',
            x: 60,
            y: 400,
            width: 440,
            height: 600,
            z: 1,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 15,
            fontColor: '#ffffff',
            bgColor: '#1e1f22',
            bgOpacity: 0.85,
            boxRadius: 8
          },
          {
            id: 'w-clock-1',
            type: 'clock',
            title: 'นาฬิกาสตรีม',
            clockTheme: 'cyberpunk',
            clockFormat: '24',
            showSeconds: true,
            x: 1560,
            y: 50,
            width: 280,
            height: 80,
            z: 2,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 26,
            fontColor: '#38bdf8'
          },
          {
            id: 'w-text-1',
            type: 'text',
            title: 'แถบข้อความประกาศ',
            text: 'ยินดีต้อนรับทุกคนเข้าสู่ไลฟ์สตรีมสดวันนี้ครับ! กดติดตามและพูดคุยในแชทได้เลย',
            textMode: 'ticker',
            x: 560,
            y: 1000,
            width: 800,
            height: 50,
            z: 3,
            opacity: 1,
            locked: false,
            hidden: false,
            fontSize: 18,
            fontColor: '#ffffff',
            bgColor: '#141923'
          }
        ]
      }
    ],
    activePageId: 'page-1',
    selectedWidgetId: null,
    zoom: 0.45,
    snapGuides: true,
    isDragging: false,
    isResizing: false,
    activeResizeHandle: null,
    dragStartMouseX: 0,
    dragStartMouseY: 0,
    dragStartWidgetX: 0,
    dragStartWidgetY: 0,
    dragStartWidgetW: 0,
    dragStartWidgetH: 0,
    customizerManuallyCollapsed: false,
    chatSubTab: 'standard',
    chatThemePage: 1
  };

  let clockInterval = null;

  // ========================================================
  // COMPOSER LIVE DEMO SIMULATION MANAGER
  // ========================================================
  
  // ── Vertical Ticker Helper for Viewer Widget ──
  const _VT_DIGITS = [];
  for (let loop = 0; loop < 3; loop++) {
    for (let d = 0; d <= 9; d++) {
      _VT_DIGITS.push(d);
    }
  }
  const _VT_TOTAL_ITEMS = _VT_DIGITS.length;
  const _VT_STEP_PCT = 100 / _VT_TOTAL_ITEMS;

  function createVtDigitColumn(initDigit) {
    const col = document.createElement('span');
    col.className = 'vt-col';
    col.dataset.digit = initDigit;
    col.dataset.idx = 10 + initDigit;

    const track = document.createElement('span');
    track.className = 'vt-track';
    for (let i = 0; i < _VT_TOTAL_ITEMS; i++) {
      const item = document.createElement('span');
      item.className = 'vt-num';
      item.textContent = _VT_DIGITS[i];
      track.appendChild(item);
    }

    const initIdx = 10 + initDigit;
    track.style.transform = `translateY(-${(initIdx * _VT_STEP_PCT).toFixed(4)}%)`;
    col.appendChild(track);

    track.addEventListener('transitionend', (e) => {
      if (e.propertyName !== 'transform') return;
      const curIdx = parseInt(col.dataset.idx, 10);
      const normDigit = ((curIdx % 10) + 10) % 10;
      const normIdx = 10 + normDigit;
      col.dataset.idx = normIdx;
      col.dataset.digit = normDigit;
      track.classList.remove('animated');
      track.style.transform = `translateY(-${(normIdx * _VT_STEP_PCT).toFixed(4)}%)`;
      void track.offsetHeight;
    });

    return col;
  }

  function createVtCharSpan(char) {
    const sp = document.createElement('span');
    sp.className = 'vt-char';
    sp.textContent = char;
    return sp;
  }

  function updateNumberTicker(tickerEl, targetNumber) {
    if (!tickerEl) return;
    const targetVal = targetNumber || 0;
    const formatted = targetVal.toLocaleString();
    const targetChars = formatted.split('');
    const prevVal = tickerEl._lastVal != null ? tickerEl._lastVal : null;
    const isIncrease = prevVal == null || targetVal >= prevVal;
    tickerEl._lastVal = targetVal;

    let curCols = Array.from(tickerEl.children);

    while (curCols.length < targetChars.length) {
      const c = targetChars[targetChars.length - curCols.length - 1];
      let newEl;
      if (c >= '0' && c <= '9') {
        newEl = createVtDigitColumn(parseInt(c, 10));
      } else {
        newEl = createVtCharSpan(c);
      }
      tickerEl.insertBefore(newEl, tickerEl.firstChild);
      curCols.unshift(newEl);
    }
    while (curCols.length > targetChars.length) {
      const rem = curCols.shift();
      if (rem) rem.remove();
    }

    targetChars.forEach((c, i) => {
      const el = curCols[i];
      if (c >= '0' && c <= '9') {
        if (!el.classList.contains('vt-col')) {
          const col = createVtDigitColumn(parseInt(c, 10));
          tickerEl.replaceChild(col, el);
          curCols[i] = col;
          return;
        }
        const targetDigit = parseInt(c, 10);
        const curDigit = parseInt(el.dataset.digit || 0, 10);
        let curIdx = parseInt(el.dataset.idx || 10, 10);

        if (curDigit === targetDigit && curIdx >= 10 && curIdx < 20) {
          return;
        }

        let nextIdx;
        if (isIncrease) {
          if (targetDigit >= curDigit) {
            nextIdx = curIdx + (targetDigit - curDigit);
          } else {
            nextIdx = curIdx + (10 + targetDigit - curDigit);
          }
        } else {
          if (targetDigit <= curDigit) {
            nextIdx = curIdx - (curDigit - targetDigit);
          } else {
            nextIdx = curIdx - (10 + curDigit - targetDigit);
          }
        }

        el.dataset.digit = targetDigit;
        el.dataset.idx = nextIdx;

        const track = el.querySelector('.vt-track');
        if (track) {
          track.classList.add('animated');
          track.style.transform = `translateY(-${(nextIdx * _VT_STEP_PCT).toFixed(4)}%)`;
        }
      } else {
        if (!el.classList.contains('vt-char')) {
          const sp = createVtCharSpan(c);
          tickerEl.replaceChild(sp, el);
          curCols[i] = sp;
        } else {
          el.textContent = c;
        }
      }
    });
  }

  const PEOPLE_ICON_SVG = `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;">
    <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
  </svg>`;
  function peopleIconSpan(iconSize = 20) {
    return `<span style="display:inline-flex;align-items:center;width:${iconSize}px;height:${iconSize}px;flex-shrink:0;">${PEOPLE_ICON_SVG}</span>`;
  }
  const PLATFORM_LOGOS = {"youtube": "data:image/png;base64,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", "twitch": "data:image/png;base64,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", "tiktok": "data:image/png;base64,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", "kick": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAADNElEQVR4nO2bS0hUYRTH//fM3Dv4HPNRaJGPTCfB1B60KrBFtIqKKKIgamVEhG3KkqigtLRCKALbGNQiDNsE1a5V7czIirFmTMUwlAy1prmPuTEjQqXfKDnPe/rBbOZxzzn/7/J95/4PIzmdThOMITCHwBwCcwjMITCHwBwCcwjMITCHwBwCcwjMITCHwBwCc+yRvFhNp4KcrbZZ7490GuitUxd8HUeBhA2PHUgplITfGWrX4W7QYLk7QMmTsP5R+OI/3zPgPrP44hNOAHmJhHVdClJLxcV/6TLwvl4FIuRjERIEewZQ81BBeoU4pdGnBnqPqjADkYtLSABsqUD1Awcyq8XpfH0ewJsjKkw9srEpspf7hwQcQNV9B7I2iVP59jKA1wf9CPijEB9xRJKBtR0KsreI05joCaBnvx+GLzo5EOKEZAMq2xXkbpt9bM4w9S6AV3tU6JPRy4MQByQCKm4qWLpDXPwPj4nu3Sq08eiOLQhxwNUqI3+vuHjfoInuXX6oo9Gf2RBiTNklGcsPiRtQ/0hw5f34ORybgRUhhqxqlLGyTly8Oja98r7+2E3rKFaBiuvtoVc4Pl7Q8L0vtqNKikWQ7FoKrf58FB6XQQqsJ4CSK+7tfyetTELRyfmFslQn+DdFJ+xIK1+YYJYUgBSgok0J9QoxiYc4MXhbhz4x94bn3EhYcTiiXk1iCeC9oqGvUYO3RfxoV3pODjlDlhPA26zBe3W68KE7uvDYs6UDrhbZWgJ4mv5cdVMD3A1irzBvuw3Ldopb5qQSwNOkob9Vn9PoGH1iCH9X3ixDzpKSW4CxZ8acxc/Qd1YTmh1Bk3T1RTm5BdAnwn/uGzAxcEssUMEBG7I3k7X7gE/XtbBPgK4bSsg+s6wAhg/4cF7s9acWSyg5JVtXgBnPf/yF2PMuPGZHRiVZV4Ag7tMaTMGhINmBNW1yyE+0rABTbwMYviveEDOrKKypkvQCBPFc1sOaoSUNctjZYdILoI2b8DSJ7wJbCuC6plhXgCDDHTome8UbYk4tIX/f4jcD6f//BZhDYA6BOQTmEJhDYA6BOQTmEJhDYA6BOQTmEJhDYA7FO4F48wvOIuBp+CZSdAAAAABJRU5ErkJggg==", "facebook": "data:image/png;base64,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", "soop": "data:image/png;base64,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", "obs_icon": "data:image/png;base64,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"};

  function getPlatformLogoSrc(plat) {
    const p = (plat || '').toLowerCase().trim();
    return PLATFORM_LOGOS[p] || `assets/platforms/${p}.png`;
  }

  function getPlatformIconHtml(plat, size = 20, extraStyle = '') {
    const p = (plat || '').toLowerCase().trim();
    const src = getPlatformLogoSrc(p);
    return `<img src="${src}" class="plat-icon plat-icon-${p}" alt="${p}" style="width:${size}px; height:${size}px; object-fit:contain; vertical-align:middle; display:inline-block; flex-shrink:0; pointer-events:none; ${extraStyle}" onerror="this.src='assets/platforms/${p}.png'; this.onerror=function(){this.style.display='none';};">`;
  }

  const MUSIC_LOGOS = {
    spotify: `<svg viewBox="0 0 24 24" fill="#1ED760" style="width:14px;height:14px;vertical-align:middle;display:inline-block;flex-shrink:0;"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>`,
    ytmusic: `<svg viewBox="0 0 24 24" style="width:14px;height:14px;vertical-align:middle;display:inline-block;flex-shrink:0;"><circle cx="12" cy="12" r="12" fill="#FF0000"/><circle cx="12" cy="12" r="7" fill="none" stroke="#FFFFFF" stroke-width="2"/><polygon points="10,8 16,12 10,16" fill="#FFFFFF"/></svg>`,
    desktop_player: `<svg viewBox="0 0 24 24" fill="#60A5FA" style="width:14px;height:14px;vertical-align:middle;display:inline-block;flex-shrink:0;"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>`
  };

  function updateAllViewerTickers(container, w) {
    if (!container || !w) return;
    const count = w.mockViewerCount || 1250;
    const totalTicker = container.querySelector('.viewer-total .viewer-ticker');
    if (totalTicker) {
      updateNumberTicker(totalTicker, count);
    }
    const platWeights = {
      youtube: 0.45,
      twitch: 0.30,
      tiktok: 0.15,
      kick: 0.10,
      facebook: 0.08,
      soop: 0.05
    };
    const activePlats = (w.viewerPlatforms && w.viewerPlatforms.length > 0) ? w.viewerPlatforms : ['youtube', 'twitch', 'tiktok', 'kick'];
    let sumWeight = 0;
    activePlats.forEach(p => { sumWeight += (platWeights[p] || 0.1); });
    if (sumWeight <= 0) sumWeight = 1;

    activePlats.forEach(p => {
      const chipTicker = container.querySelector(`.viewer-chip[data-platform="${p}"] .viewer-ticker`);
      if (chipTicker) {
        const platShare = Math.round(count * ((platWeights[p] || 0.1) / sumWeight));
        updateNumberTicker(chipTicker, platShare);
      }
    });
  }


  const ComposerDemoManager = {
    timers: {},
    chatMockPool: [
      { user: 'Krit_Live', text: 'สวัสดีทุกคนในไลฟ์สตรีม ภาพคมชัดมากครับ! 🎮', platform: 'youtube', color: '#ef4444' },
      { user: 'Zack_Twitch', text: 'สตรีมภาพสวย 60fps ลื่นไหลดีมากครับ 🔥', platform: 'twitch', color: '#a855f7' },
      { user: 'น้องมุก_ยิ้มสดใส', text: 'ส่งดาว 100 ดวง เป็นกำลังใจให้สตรีมเมอร์นะคะ ⭐', platform: 'facebook', color: '#3b82f6' },
      { user: 'Boy_Gamer', text: 'วันนี้เล่นเกมเนื้อเรื่องสนุกสุดๆ เลยครับ 🚀', platform: 'kick', color: '#22c55e' },
      { user: 'Aom_Channel', text: 'ยินดีต้อนรับเพื่อนๆ ทุกคนที่แวะเข้ามาพูดคุยกันน้า 💖', platform: 'tiktok', color: '#ec4899' },
      { user: 'Captain_Soop', text: 'ภาพแสงและสีในเกมวันนี้ปรับได้สวยงามมากครับ ✨', platform: 'soop', color: '#06b6d4' }
    ],
    charMockPool: [
      'สวัสดีครับทุกคน! วันนี้ยินดีต้อนรับสู่ไลฟ์สตรีมนะครับ 🎮',
      'ขอบคุณทุกคนที่เข้ามาร่วมพูดคุยและส่งกำลังใจให้กันนะครับ ✨',
      'ขอให้ทุกคนมีความสุขและสนุกกับการรับชมสตรีมวันนี้น้า 💖',
      'อย่าลืมกดแชร์และคอมเมนต์พูดคุยกันได้ตลอดเลยนะครับ! 🚀'
    ],
    danmakuPool: [
      '🚀 สตรีมเมอร์สู้ๆ นะครับ!',
      '🎮 ภาพคมชัด 60fps ลื่นมาก',
      '💖 สวัสดีรอบห้องสตรีมจ้า',
      '🔥 คอมเมนต์ด่วน ดันมากุวิ่งบนจอสด',
      '⭐ ยินดีต้อนรับเพื่อนๆ ทุกคนครับ',
      '🎉 สตรีมสนุกมากครับวันนี้'
    ],

    // Default Chat Simulation with full scoped theme & box style support
    sendChatMsg(w, customText = null) {
      const feed = document.getElementById(`widget-chat-feed-${w.id}`);
      if (!feed) return;
      const msg = customText ? { user: 'สตรีมเมอร์', text: customText, platform: 'youtube', color: '#38bdf8' } : this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      
      const theme = w.chatTheme || 'default';
      const isTheme = w.chatMode === 'theme';
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const fWeight = w.fontWeight || '600';
      const uClr = w.usernameColor || '#38bdf8';
      const hex = w.bgColor || '#1e1f22';
      const r = parseInt(hex.slice(1, 3), 16) || 30;
      const g = parseInt(hex.slice(3, 5), 16) || 31;
      const b = parseInt(hex.slice(5, 7), 16) || 34;
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const pad = w.boxPadding ?? 6;
      const boxEnabled = w.boxEnabled !== false;

      let boxStyle = '';
      if (isTheme) {
        boxStyle = 'background:transparent;';
      } else if (boxEnabled) {
        boxStyle = `background:rgba(${r}, ${g}, ${b}, ${bgOp}); border-radius:${radius}px; padding:${pad}px 12px;`;
        if (w.boxWidth === 'full') boxStyle += ' width:100%;';
        if (w.boxBorder) boxStyle += ` border:${w.boxBorderWidth || 2}px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};`;
        if (w.boxGlow) boxStyle += ` box-shadow:0 0 12px ${w.boxGlowColor || '#a855f7'};`;
        else if (w.boxShadow) boxStyle += ' box-shadow:0 4px 12px rgba(0,0,0,0.3);';
      } else {
        boxStyle = 'background:transparent; padding:2px 0;';
      }

      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur || 3}px ${w.textShadowColor || '#000000'};` : '';
      const alignCss = w.align === 'center' ? 'center' : (w.align === 'right' ? 'flex-end' : 'flex-start');

      const item = document.createElement('div');
      item.className = `cwc-msg-item msg chat-line theme-${theme}`;
      item.style.cssText = `align-self:${alignCss}; ${boxStyle} animation:cwc-item-pop 0.25s ease-out; margin-bottom:4px;`;
      item.innerHTML = `
        <div class="msg-bg"></div>
        ${getPlatformIconHtml(msg.platform, 16, 'margin-right:6px;')}
        <span class="author" style="color:${uClr}; font-weight:700; margin-right:6px;">${msg.user}:</span>
        <span class="text" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; font-weight:${fWeight}; color:${fClr}; ${strokeCss} ${shadowCss}">${msg.text}</span>
      `;
      feed.appendChild(item);
      feed.scrollTop = feed.scrollHeight;

      while (feed.children.length > 12) {
        feed.removeChild(feed.children[0]);
      }
    },

    toggleChatLoop(w, btn) {
      if (this.timers[w.id]) {
        clearInterval(this.timers[w.id]);
        delete this.timers[w.id];
        if (btn) {
          btn.innerHTML = '▶ เล่นจำลองแชทสด';
          btn.classList.remove('active');
        }
      } else {
        this.sendChatMsg(w);
        this.timers[w.id] = setInterval(() => this.sendChatMsg(w), 1600);
        if (btn) {
          btn.innerHTML = '⏹ หยุดจำลองแชท';
          btn.classList.add('active');
        }
      }
    },

    // Danmaku Simulation
    sendDanmakuMsg(w, customText = null) {
      const feed = document.getElementById(`widget-danmaku-feed-${w.id}`);
      if (!feed) return;
      const txt = customText || this.danmakuPool[Math.floor(Math.random() * this.danmakuPool.length)];
      const bullet = document.createElement('div');
      bullet.className = 'danmaku-bullet-item';

      const zone = w.slider_zone || 'middle';
      let minY = 0.05, maxY = 0.90;
      if (zone === 'top') { minY = 0.05; maxY = 0.45; }
      else if (zone === 'middle') { minY = 0.25; maxY = 0.70; }
      else if (zone === 'bottom') { minY = 0.55; maxY = 0.92; }

      const topPct = (minY + Math.random() * (maxY - minY)) * 100;
      const fsz = w.fontSize || 24;
      const clr = w.fontColor || '#ffffff';
      const stroke = w.textStroke === true ? `-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadow = w.textShadow !== false ? `filter:drop-shadow(0 2px 4px ${w.textShadowColor || 'rgba(0,0,0,0.6)'});` : '';
      const dur = w.speed || 6;

      bullet.style.cssText = `top:${topPct}%; left:0; font-size:${fsz}px; color:${clr}; opacity:${w.opacity ?? 1}; ${stroke} ${shadow} animation:danmakuBulletRun ${dur}s linear forwards;`;
      bullet.textContent = txt;
      feed.appendChild(bullet);

      setTimeout(() => bullet.remove(), dur * 1000 + 500);
    },

    toggleDanmakuLoop(w, btn) {
      if (this.timers[w.id]) {
        clearInterval(this.timers[w.id]);
        delete this.timers[w.id];
        if (btn) {
          btn.innerHTML = '▶ เล่นกระสุนดันมากุสด';
          btn.classList.remove('active');
        }
      } else {
        this.sendDanmakuMsg(w);
        this.timers[w.id] = setInterval(() => this.sendDanmakuMsg(w), 1200);
        if (btn) {
          btn.innerHTML = '⏹ หยุดกระสุนดันมากุ';
          btn.classList.add('active');
        }
      }
    },

    // Balloon Simulation
    sendBalloonMsg(w) {
      const feed = document.getElementById(`widget-balloon-feed-${w.id}`);
      if (!feed) return;
      const msg = this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      const bubble = document.createElement('div');
      const bg = w.balloonBg || '#ffffff';
      const clr = w.balloonTextColor || '#0f172a';
      const radius = w.balloonRadius ?? 14;
      const fsz = w.fontSize || 15;
      const op = w.balloonOpacity ?? 0.95;

      bubble.style.cssText = `background:${bg}; color:${clr}; padding:10px 16px; border-radius:${radius}px; font-weight:600; font-size:${fsz}px; box-shadow:0 6px 18px rgba(0,0,0,0.35); position:relative; margin-bottom:12px; max-width:90%; opacity:${op}; animation:cwc-item-pop 0.25s ease-out;`;
      bubble.innerHTML = `
        <div style="font-weight:700; font-size:12px; color:${msg.color}; margin-bottom:3px;">${msg.user}:</div>
        <div>${msg.text}</div>
        <svg style="position:absolute; bottom:-11px; left:22px; width:18px; height:12px; fill:${bg};" viewBox="0 0 18 12">
          <path d="M0 0 L18 0 L6 12 Z"/>
        </svg>
      `;
      feed.appendChild(bubble);
      feed.scrollTop = feed.scrollHeight;
      while (feed.children.length > 8) {
        feed.removeChild(feed.children[0]);
      }
    },

    // Character Speech Simulation
    triggerCharacterTalk(w) {
      const textEl = document.getElementById(`widget-char-text-${w.id}`);
      const avatarEl = document.getElementById(`widget-char-avatar-${w.id}`);
      if (!textEl) return;
      const txt = this.charMockPool[Math.floor(Math.random() * this.charMockPool.length)];
      textEl.textContent = txt;
      if (avatarEl) {
        avatarEl.style.transform = 'scale(1.08) translateY(-4px)';
        setTimeout(() => avatarEl.style.transform = 'none', 300);
      }
    },

    // Goal Simulation
    triggerGoalPlus(w) {
      w.goalCurrent = (w.goalCurrent || 0) + 50;
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
      if (window.showToast) window.showToast(`🎉 เป้าหมายยอดเพิ่มขึ้นเป็น ${w.goalCurrent} แล้ว`);
    },

    triggerGoalReset(w) {
      w.goalCurrent = 0;
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
    },

    // Viewer Simulation with Smooth Column Rolling Ticker
    triggerViewerRandom(w) {
      const target = Math.floor(800 + Math.random() * 3200);
      w.mockViewerCount = target;
      const el = document.getElementById(`widget-${w.id}`);
      if (el) {
        updateAllViewerTickers(el, w);
      }
      renderLayersList();
    },

    triggerViewerAdd(w, delta = 50) {
      const current = w.mockViewerCount || 1250;
      const target = current + delta;
      w.mockViewerCount = target;
      const el = document.getElementById(`widget-${w.id}`);
      if (el) {
        updateAllViewerTickers(el, w);
      }
      renderLayersList();
    },

    triggerViewerSub(w, delta = 30) {
      const current = w.mockViewerCount || 1250;
      const target = Math.max(0, current - delta);
      w.mockViewerCount = target;
      const el = document.getElementById(`widget-${w.id}`);
      if (el) {
        updateAllViewerTickers(el, w);
      }
      renderLayersList();
    },

    // ASK Poll Simulation
    triggerAskVote(w) {
      if (window.showToast) window.showToast('📊 จำลองผู้ร่วมโหวตเพิ่มขึ้นแบบ Real-time!');
      renderCanvasWidgets();
    },

    // Giveaway Simulation
    triggerGiveawayDraw(w) {
      if (window.showToast) window.showToast('🎁 จำลองสุ่มผู้โชคดี: Gamer_Pro123 ได้รับรางวัล!');
      renderCanvasWidgets();
    },

    // Emote Party Simulation
    triggerEmoteParty(w) {
      const container = document.getElementById(`widget-emote-party-${w.id}`) || document.getElementById(`widget-${w.id}`);
      if (!container) return;
      const emotes = ['🔥', '🎉', '💖', '⭐', '🚀', '👑', '🎮', '✨', '👏', '🥳', '😎', '💯'];
      const maxEmotes = w.epMaxEmotes || 15;
      const anim = w.epAnimation || 'float';
      const dur = w.epDuration || 4;
      const size = w.epEmoteSize || 48;

      for (let i = 0; i < maxEmotes; i++) {
        setTimeout(() => {
          const em = document.createElement('div');
          const emo = emotes[Math.floor(Math.random() * emotes.length)];
          const left = Math.random() * 85 + 5;
          em.style.cssText = `position: absolute; left: ${left}%; bottom: 0; font-size: ${size}px; pointer-events: none; user-select: none; animation: emoteFloatUp ${dur}s ease-out forwards; z-index: 100;`;
          em.textContent = emo;
          container.appendChild(em);
          setTimeout(() => em.remove(), dur * 1000 + 200);
        }, i * 120);
      }
    },

    // Now Playing Simulation (Source-specific)
    triggerNowPlayingNext(w) {
      const src = w.npSource || w.np_source || 'auto';
      let songs = [];
      if (src === 'spotify') {
        songs = [
          { title: 'Stay With Me', artist: 'Miki Matsubara (Spotify)' },
          { title: 'Blinding Lights', artist: 'The Weeknd (Spotify)' },
          { title: 'Cruel Summer', artist: 'Taylor Swift (Spotify)' },
          { title: 'Starboy', artist: 'The Weeknd ft. Daft Punk (Spotify)' }
        ];
      } else if (src === 'ytmusic') {
        songs = [
          { title: 'Specialz', artist: 'King Gnu (YouTube Music)' },
          { title: 'アイドル (Idol)', artist: 'YOASOBI (YouTube Music)' },
          { title: 'Bling-Bang-Bang-Born', artist: 'Creepy Nuts (YouTube Music)' },
          { title: 'Lemon', artist: 'Kenshi Yonezu (YouTube Music)' }
        ];
      } else if (src === 'desktop_player') {
        songs = [
          { title: 'Canon in D Major.flac', artist: 'Local Media Player (VLC)' },
          { title: 'Chopin - Nocturne No. 2.mp3', artist: 'Windows Media Player' },
          { title: 'Cyberpunk 2077 OST.wav', artist: 'Foobar2000' },
          { title: 'Track 01 - Master Audio.alac', artist: 'AIMP Player' }
        ];
      } else {
        songs = [
          { title: 'Stay With Me', artist: 'Miki Matsubara' },
          { title: 'Blinding Lights', artist: 'The Weeknd' },
          { title: 'Specialz', artist: 'King Gnu' },
          { title: 'アイドル (Idol)', artist: 'YOASOBI' }
        ];
      }
      const nextSong = songs[Math.floor(Math.random() * songs.length)];
      w.songTitle = nextSong.title;
      w.artist = nextSong.artist;
      renderCanvasWidgets();
      renderWidgetCustomizerPanel(w.id);
      saveState();
    }
  };

  // ═══ V2/V3 Universal Schema Migration & Dual-Key Normalizer ═══
  // Helper to identify widgets that are forced to cover the full canvas (1920x1080)
  function isFullscreenWidget(w) {
    if (!w) return false;
    return !!(
      w.isDanmaku ||
      w.chatMode === 'danmaku' ||
      w.isFullScreen ||
      w.is_fullscreen ||
      w.type === 'ask' ||
      w.type === 'giveaway' ||
      w.type === 'replie' ||
      w.type === 'emote_party' ||
      w.type === 'randomizer'
    );
  }

  function normalizeWidget(w) {
    if (!w || typeof w !== 'object') return w;
    // Normalize type aliases
    if (w.type === 'avatar' || w.type === 'replie') {
      w.type = 'character';
    } else if (w.type === 'donate_goal') {
      w.type = 'goal';
    }

    // Geometry
    if (isFullscreenWidget(w)) {
      w.x = 0;
      w.y = 0;
      w.width = CANVAS_WIDTH;
      w.w = CANVAS_WIDTH;
      w.height = CANVAS_HEIGHT;
      w.h = CANVAS_HEIGHT;
      w.noDrag = true;
      w.noResize = true;
      w.isFullScreen = true;
    } else {
      w.x = parseInt(w.x ?? 0, 10);
      w.y = parseInt(w.y ?? 0, 10);
      const widthVal = w.width ?? w.w ?? 300;
      const heightVal = w.height ?? w.h ?? 180;
      w.width = parseInt(widthVal, 10);
      w.w = w.width;
      w.height = parseInt(heightVal, 10);
      w.h = w.height;
    }

    // Typography & Styling (Dual-Key for V2/V3 compatibility)
    w.fontSize = parseInt(w.fontSize ?? w.font_size ?? 16, 10);
    w.font_size = w.fontSize;
    w.fontColor = w.fontColor || w.font_color || '#ffffff';
    w.font_color = w.fontColor;
    w.fontWeight = w.fontWeight || w.font_weight || '600';
    w.font_weight = w.fontWeight;
    w.fontFamily = w.fontFamily || w.font_family || 'Kanit';
    w.font_family = w.fontFamily;

    // Stroke & Shadow
    w.textStroke = w.textStroke ?? w.text_stroke ?? false;
    w.text_stroke = w.textStroke;
    w.textStrokeWidth = parseInt(w.textStrokeWidth ?? w.text_stroke_width ?? 2, 10);
    w.text_stroke_width = w.textStrokeWidth;
    w.textStrokeColor = w.textStrokeColor || w.text_stroke_color || w.strokeColor || '#000000';
    w.text_stroke_color = w.textStrokeColor;
    w.strokeColor = w.textStrokeColor;
    w.textShadow = w.textShadow ?? w.text_shadow ?? true;
    w.text_shadow = w.textShadow;
    w.textShadowBlur = parseInt(w.textShadowBlur ?? w.text_shadow_blur ?? 3, 10);
    w.text_shadow_blur = w.textShadowBlur;
    w.textShadowColor = w.textShadowColor || w.text_shadow_color || '#000000';
    w.text_shadow_color = w.textShadowColor;

    // Background
    w.bgColor = w.bgColor || w.bg_color || '#1e1f22';
    w.bg_color = w.bgColor;
    w.bgOpacity = parseFloat(w.bgOpacity ?? w.bg_opacity ?? 0.85);
    w.bg_opacity = w.bgOpacity;
    w.boxRadius = parseInt(w.boxRadius ?? w.box_radius ?? 8, 10);
    w.box_radius = w.boxRadius;

    // Viewer Widget
    w.viewerTheme = w.viewerTheme || w.viewer_theme || 'default';
    w.viewer_theme = w.viewerTheme;
    w.viewerMode = w.viewerMode || w.viewer_mode || 'both';
    w.viewer_mode = w.viewerMode;
    w.viewerDirection = w.viewerDirection || w.viewer_direction || 'horizontal';
    w.viewer_direction = w.viewerDirection;
    w.viewerAlign = w.viewerAlign || w.viewer_align || 'left';
    w.viewer_align = w.viewerAlign;
    w.iconSize = parseInt(w.iconSize ?? w.viewer_icon_size ?? 20, 10);
    w.viewer_icon_size = w.iconSize;
    w.viewerPlatforms = w.viewerPlatforms || w.viewer_platforms || ['youtube', 'twitch', 'tiktok', 'kick'];
    w.viewer_platforms = w.viewerPlatforms;

    // Chat Widget
    w.chatTheme = w.chatTheme || w.chat_theme || 'default';
    w.chat_theme = w.chatTheme;
    w.chatMode = w.chatMode || w.chat_mode || 'default';
    w.chat_mode = w.chatMode;

    // Chat Animation & Auto-Hide
    w.animation = w.animation || w.anim_in || w.animIn || 'slide';
    w.anim_in = w.animation;
    w.animIn = w.animation;
    w.exitAnimation = w.exitAnimation || w.exit_animation || w.anim_out || w.animOut || 'auto';
    w.exit_animation = w.exitAnimation;
    w.anim_out = w.exitAnimation;
    w.animOut = w.exitAnimation;
    w.autoHide = w.autoHide ?? w.auto_hide ?? false;
    w.auto_hide = w.autoHide;
    w.hideAfter = parseFloat(w.hideAfter ?? w.hide_after ?? 8);
    w.hide_after = w.hideAfter;

    // Chat Container Background Box (Default false: completely transparent, only message boxes visible)
    w.containerBgEnabled = w.containerBgEnabled ?? w.container_bg_enabled ?? false;
    w.container_bg_enabled = w.containerBgEnabled;
    w.containerBgColor = w.containerBgColor || w.container_bg_color || '#0a0e1a';
    w.container_bg_color = w.containerBgColor;
    w.containerBgOpacity = parseFloat(w.containerBgOpacity ?? w.container_bg_opacity ?? 0.75);
    w.container_bg_opacity = w.containerBgOpacity;
    w.containerRadius = parseInt(w.containerRadius ?? w.container_radius ?? 8, 10);
    w.container_radius = w.containerRadius;
    w.containerBorder = w.containerBorder ?? w.container_border ?? false;
    w.container_border = w.containerBorder;
    w.containerBorderWidth = parseInt(w.containerBorderWidth ?? w.container_border_width ?? 1, 10);
    w.container_border_width = w.containerBorderWidth;
    w.containerBorderColor = w.containerBorderColor || w.container_border_color || '#38bdf8';
    w.container_border_color = w.containerBorderColor;

    // Now Playing Widget
    w.npTheme = w.npTheme || w.np_theme || 'custom';
    w.np_theme = w.npTheme;
    w.npStyle = w.npStyle || w.np_style || 'flat';
    w.np_style = w.npStyle;
    w.npSource = w.npSource || w.np_source || 'auto';
    w.np_source = w.npSource;
    w.npShowArt = w.npShowArt ?? w.np_show_art ?? true;
    w.np_show_art = w.npShowArt;
    w.npShowProgress = w.npShowProgress ?? w.np_show_progress ?? true;
    w.np_show_progress = w.npShowProgress;
    w.npScrollTitle = w.npScrollTitle ?? w.np_scroll_title ?? true;
    w.np_scroll_title = w.npScrollTitle;
    w.npBgColor = w.npBgColor || w.np_bg_color || '#1a1a2e';
    w.np_bg_color = w.npBgColor;
    w.npBgOpacity = parseFloat(w.npBgOpacity ?? w.np_bg_opacity ?? 0.85);
    w.np_bg_opacity = w.npBgOpacity;
    w.npRadius = parseInt(w.npRadius ?? w.np_radius ?? 8, 10);
    w.np_radius = w.npRadius;
    w.npArtRadius = parseInt(w.npArtRadius ?? w.np_art_radius ?? 6, 10);
    w.np_art_radius = w.npArtRadius;
    w.npArtSize = parseInt(w.npArtSize ?? w.np_art_size ?? 48, 10);
    w.np_art_size = w.npArtSize;
    w.npAccentColor = w.npAccentColor || w.np_accent_color || '#1db954';
    w.np_accent_color = w.npAccentColor;
    w.npTextColor = w.npTextColor || w.np_text_color || '#ffffff';
    w.np_text_color = w.npTextColor;
    w.npFontSize = parseInt(w.npFontSize ?? w.np_font_size ?? 14, 10);
    w.np_font_size = w.npFontSize;
    w.npArtistFontSize = parseInt(w.npArtistFontSize ?? w.np_artist_font_size ?? 12, 10);
    w.np_artist_font_size = w.npArtistFontSize;
    w.npTimeFontSize = parseInt(w.npTimeFontSize ?? w.np_time_font_size ?? 10, 10);
    w.np_time_font_size = w.npTimeFontSize;

    // Webcam Widget
    w.webcamRatio = w.webcamRatio || w.webcam_ratio || '16:9';
    w.webcam_ratio = w.webcamRatio;
    w.webcamTheme = w.webcamTheme || w.webcam_theme || 'border';
    w.webcam_theme = w.webcamTheme;
    w.borderWidth = parseInt(w.borderWidth ?? w.webcam_border_width ?? 3, 10);
    w.webcam_border_width = w.borderWidth;
    w.borderColor = w.borderColor || w.webcam_border_color || '#6366f1';
    w.webcam_border_color = w.borderColor;

    // Clock Widget
    w.clockMode = w.clockMode || w.clock_mode || (w.clock_style && w.clock_style !== 'none' ? 'style' : 'theme');
    w.clock_mode = w.clockMode;
    w.clockTheme = w.clockTheme || w.clock_theme || 'default';
    w.clock_theme = w.clockTheme;
    w.clockStyle = w.clockStyle || w.clock_style || 'none';
    w.clock_style = w.clockStyle;
    w.clockFormat = w.clockFormat || w.clock_format || 'HH:MM';
    w.clock_format = w.clockFormat;
    w.showDate = w.showDate ?? w.show_date ?? false;
    w.show_date = w.showDate;
    w.dateLang = w.dateLang || w.date_lang || 'th';
    w.date_lang = w.dateLang;
    w.dateFormat = w.dateFormat || w.date_format || 'short';
    w.date_format = w.dateFormat;
    w.dateFontSize = parseInt(w.dateFontSize ?? w.date_font_size ?? 14, 10);
    w.date_font_size = w.dateFontSize;
    w.dateColor = w.dateColor || w.date_color || '#cccccc';
    w.date_color = w.dateColor;
    w.timeColor = w.timeColor || w.time_color || '#ffffff';
    w.time_color = w.timeColor;
    w.themeOpacity = parseFloat(w.themeOpacity ?? w.theme_opacity ?? 1.0);
    w.theme_opacity = w.themeOpacity;
    w.styleOpacity = parseFloat(w.styleOpacity ?? w.style_opacity ?? 1.0);
    w.style_opacity = w.styleOpacity;

    // Media & Browser Source
    w.imageUrl = w.imageUrl || w.image_url || '';
    w.image_url = w.imageUrl;
    w.videoUrl = w.videoUrl || w.video_url || '';
    w.video_url = w.videoUrl;
    w.fitMode = w.fitMode || w.fit_mode || 'cover';
    w.fit_mode = w.fitMode;
    w.url = w.url || '';

    return w;
  }

  // Load saved state from localStorage (with full V2 fallback & migration)
  function loadSavedState() {
    try {
      let saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) {
        saved = localStorage.getItem('composer_pages') || localStorage.getItem('composer_layout');
      }
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          if (parsed[0].widgets) {
            state.pages = parsed.map(p => {
              p.widgets = (p.widgets || []).map(normalizeWidget);
              return p;
            });
            state.activePageId = state.pages[0].id;
          } else {
            state.pages = [{
              id: 'page-1',
              name: 'หน้า 1',
              widgets: parsed.map(normalizeWidget)
            }];
            state.activePageId = 'page-1';
          }
        }
      }
    } catch (e) {
      console.warn('Failed to load composer state:', e);
    }
  }

  // Save current layout to localStorage & sync to OBS Server
  function saveState(silent) {
    try {
      const payload = {
        pages: state.pages,
        activePageId: state.activePageId,
        updatedAt: Date.now()
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.pages));
      localStorage.setItem(STORAGE_KEY + '_full', JSON.stringify(payload));

      // Push to backend server API for OBS Studio Browser Source
      fetch('/api/composer/layout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(() => {});

      // Broadcast to any open windows
      try {
        if ('BroadcastChannel' in window) {
          const bus = new BroadcastChannel('bp3_system_channel');
          bus.postMessage({ event: 'CANVAS_LAYOUT_SAVED', payload });
        }
      } catch (e) {}

      if (!silent && window.showToast) {
        window.showToast('บันทึกเลย์เอาต์หน้าจอและส่งไปยัง OBS เรียบร้อยแล้ว');
      }
    } catch (e) {
      console.error('Failed to save composer state:', e);
    }
  }

  // Get active page
  function getActivePage() {
    let p = state.pages.find(p => p.id === state.activePageId);
    if (!p && state.pages.length > 0) {
      p = state.pages[0];
      state.activePageId = p.id;
    }
    return p;
  }

  // Get selected widget
  function getSelectedWidget() {
    const page = getActivePage();
    if (!page) return null;
    return page.widgets.find(w => w.id === state.selectedWidgetId) || null;
  }

  // Initialize Composer Studio
  function initComposerStudio() {
    loadSavedState();
    renderPageTabs();
    setupCanvasEvents();
    setupToolbarEvents();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();

    // Auto-fit zoom when window is opened
    window.addEventListener('resize', autoFitCanvas);

    // Live clock updater
    if (!clockInterval) {
      clockInterval = setInterval(() => {
        const now = new Date();
        document.querySelectorAll('.composer-widget.type-clock').forEach(el => {
          const wid = el.dataset.id;
          const page = getActivePage();
          const w = page ? page.widgets.find(x => x.id === wid) : null;
          if (!w) return;
          const hasStyle = (w.clockMode === 'style') || (w.clockStyle && w.clockStyle !== 'none');
          if (hasStyle && w.clockStyle && w.clockStyle !== 'none') {
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            const yr = now.getFullYear();
            const mo = String(now.getMonth() + 1).padStart(2, '0');
            const dy = String(now.getDate()).padStart(2, '0');
            const dotTime = el.querySelector('.dot-time');
            if (dotTime) {
              if (w.clockStyle === 'dot1') dotTime.textContent = `${h}:${m}`;
              else if (w.clockStyle === 'dot2') dotTime.textContent = `${yr}.${mo}.${dy} ${h}:${m}`;
              else dotTime.textContent = `${dy}.${mo}.${yr} ${h}:${m}`;
            }
            const ltTime = el.querySelector('.lt-time');
            if (ltTime) ltTime.innerHTML = `${h}<span class="lt-colon">:</span>${m}`;
            const ltSec = el.querySelector('.lt-sec');
            if (ltSec) ltSec.textContent = s;
            const fpsTime = el.querySelector('.fps-time');
            if (fpsTime) fpsTime.innerHTML = `${h}<span class="fps-colon">:</span>${m}<span class="fps-colon">:</span>${s}`;
            const ccOc = el.querySelector('.cc-oc');
            if (ccOc) {
              const colorNum = parseInt((w.clockStyle || '').replace(/[^0-9]/g, '')) || 1;
              const colors = CC_COLOR_SCHEMES[colorNum] || CC_COLOR_SCHEMES[1];
              const deg = 6 * (now.getSeconds() + now.getMilliseconds() / 1000);
              const phase = Math.floor(now.getMinutes()) % 2;
              const [active, inactive] = phase === 0 ? colors : [colors[1], colors[0]];
              ccOc.style.background = `conic-gradient(${active} 0deg ${deg}deg, ${inactive} ${deg}deg 360deg)`;
            }
            const ccT1 = el.querySelector('.cc-t1');
            if (ccT1) ccT1.textContent = `${h}:${m}`;
            const ccT2 = el.querySelector('.cc-t2');
            if (ccT2 && (w.clockStyle || '').startsWith('ccsec')) ccT2.textContent = s;
          } else {
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            let timeStr = `${h}:${m}`;
            if (w.clockFormat === 'HH:MM:SS') timeStr = `${h}:${m}:${s}`;
            else if (w.clockFormat === '12') {
              let hrs = now.getHours();
              const ampm = hrs >= 12 ? 'PM' : 'AM';
              hrs = hrs % 12 || 12;
              timeStr = w.showSeconds === false ? `${hrs}:${m} ${ampm}` : `${hrs}:${m}:${s} ${ampm}`;
            }
            const timeEl = el.querySelector('.clock-time');
            if (timeEl) timeEl.textContent = timeStr;
            const dateEl = el.querySelector('.clock-date');
            if (dateEl && (w.showDate ?? w.show_date)) {
              dateEl.textContent = formatClockDate(now, w.dateFormat || w.date_format || 'short', w.dateLang || w.date_lang || 'th');
            }
          }
        });
      }, 1000);
    }

    // Keyboard shortcuts
    window.addEventListener('keydown', handleKeyDown);

    // Layers List Expand/Collapse Button Listener
    const btnToggleLayers = document.getElementById('btnToggleLayersExpand');
    const layersList = document.getElementById('composerLayersList');
    if (btnToggleLayers && layersList) {
      btnToggleLayers.addEventListener('click', () => {
        const isExpanded = layersList.classList.toggle('expanded');
        btnToggleLayers.textContent = isExpanded ? '🗗 ย่อขนาด' : '⛶ ขยายดูทั้งหมด';
        btnToggleLayers.style.background = isExpanded ? 'rgba(88, 101, 242, 0.25)' : 'rgba(255,255,255,0.06)';
        btnToggleLayers.style.borderColor = isExpanded ? 'var(--dc-blurple)' : 'rgba(255,255,255,0.15)';
        btnToggleLayers.style.color = isExpanded ? '#ffffff' : '#cbd5e1';
      });
    }

        // Right Sidebar Collapsible Sections (Quick Align & Props)
    document.querySelectorAll('.composer-collapsible-header').forEach(header => {
      header.addEventListener('click', () => {
        const targetId = header.dataset.target;
        if (!targetId) return;
        const targetEl = document.getElementById(targetId);
        const toggleIcon = header.querySelector('.composer-section-toggle');
        if (!targetEl) return;
        const isHidden = targetEl.style.display === 'none';
        targetEl.style.display = isHidden ? '' : 'none';
        if (toggleIcon) toggleIcon.textContent = isHidden ? '▼' : '▶';
      });
    });

    // Left Drawer Expand Button Listener
    const btnExpand = document.getElementById('btnExpandCustPanel');
    if (btnExpand) {
      btnExpand.addEventListener('click', () => {
        state.customizerManuallyCollapsed = false;
        const leftPanel = document.getElementById('composerSidebarLeft');
        if (leftPanel) leftPanel.classList.remove('collapsed');
        btnExpand.classList.remove('visible');
      });
    }

    // Left Drawer Collapse Button Listener
    const btnCollapse = document.getElementById('btnCollapseCustPanel');
    if (btnCollapse) {
      btnCollapse.addEventListener('click', () => {
        state.customizerManuallyCollapsed = true;
        const leftPanel = document.getElementById('composerSidebarLeft');
        if (leftPanel) leftPanel.classList.add('collapsed');
        if (btnExpand) btnExpand.classList.add('visible');
      });
    }
  }

  // Auto-fit canvas into viewport
  function autoFitCanvas() {
    const viewport = document.getElementById('composerViewport');
    const stage = document.getElementById('composerCanvasStage');
    const outer = document.getElementById('composerCanvasOuter');
    if (!viewport || !stage || !outer) return;

    const vpW = viewport.clientWidth - 80;
    const vpH = viewport.clientHeight - 80;
    if (vpW <= 100 || vpH <= 100) return;

    const scaleX = vpW / CANVAS_WIDTH;
    const scaleY = vpH / CANVAS_HEIGHT;
    const fitScale = Math.min(scaleX, scaleY, 0.95);

    setZoom(fitScale);
  }

  // Set zoom level
  function setZoom(factor) {
    state.zoom = Math.max(0.15, Math.min(factor, 1.5));
    const stage = document.getElementById('composerCanvasStage');
    const outer = document.getElementById('composerCanvasOuter');
    const zoomVal = document.getElementById('composerZoomVal');

    if (stage) {
      stage.style.transform = `scale(${state.zoom})`;
    }
    if (outer) {
      outer.style.width = `${CANVAS_WIDTH * state.zoom}px`;
      outer.style.height = `${CANVAS_HEIGHT * state.zoom}px`;
    }
    if (zoomVal) {
      zoomVal.textContent = `${Math.round(state.zoom * 100)}%`;
    }
  }

  // Render Page Tabs & Multi-Page Bar
  function renderPageTabs() {
    const container = document.getElementById('composerPageTabs');
    if (!container) return;
    container.innerHTML = '';

    const pageBar = document.createElement('div');
    pageBar.className = 'composer-page-bar';

    const tabsList = document.createElement('div');
    tabsList.className = 'composer-page-tabs-list';

    state.pages.forEach((page, idx) => {
      const isActive = page.id === state.activePageId;
      const tab = document.createElement('button');
      tab.type = 'button';
      tab.className = `composer-page-tab ${isActive ? 'active' : ''}`;
      tab.title = `สลับไปยัง ${page.name}`;
      const count = page.widgets ? page.widgets.length : 0;
      tab.innerHTML = `<span>📄 ${page.name} <small style="opacity:0.75;">(${count})</small></span>`;
      tab.addEventListener('click', () => switchPage(page.id));
      tabsList.appendChild(tab);
    });

    pageBar.appendChild(tabsList);

    // Action Buttons for current active page
    const actions = document.createElement('div');
    actions.className = 'composer-page-actions';
    actions.innerHTML = `
      <button type="button" class="composer-btn-page-action" id="btnPageNew" title="สร้างหน้าเลย์เอาต์ใหม่">➕ เพิ่มหน้า</button>
      <button type="button" class="composer-btn-page-action" id="btnPageReorder" title="สลับเรียงลำดับหน้าใหม่">🔀 เรียงหน้าใหม่</button>
      <button type="button" class="composer-btn-page-action" id="btnPageDup" title="ทำสำเนาหน้านี้พร้อมวิดเจ็ตทั้งหมด">📋 สำเนา</button>
      <button type="button" class="composer-btn-page-action" id="btnPageRename" title="เปลี่ยนชื่อหน้านี้">✎ เปลี่ยนชื่อ</button>
      ${state.pages.length > 1 ? `<button type="button" class="composer-btn-page-action btn-danger" id="btnPageDel" title="ลบหน้านี้">🗑 ลบ</button>` : ''}
    `;

    const btnNew = actions.querySelector('#btnPageNew');
    if (btnNew) btnNew.addEventListener('click', addNewPage);
    const btnReorder = actions.querySelector('#btnPageReorder');
    if (btnReorder) btnReorder.addEventListener('click', reorderPages);
    const btnDup = actions.querySelector('#btnPageDup');
    if (btnDup) btnDup.addEventListener('click', duplicateCurrentPage);
    const btnRename = actions.querySelector('#btnPageRename');
    if (btnRename) btnRename.addEventListener('click', renameCurrentPage);
    const btnDel = actions.querySelector('#btnPageDel');
    if (btnDel) btnDel.addEventListener('click', () => deletePage(state.activePageId));

    pageBar.appendChild(actions);
    container.appendChild(pageBar);
  }

  function reorderPages() {
    if (state.pages.length <= 1) {
      if (window.showToast) window.showToast('ℹ️ มีหน้าเลย์เอาต์เพียง 1 หน้า กรุณากด "➕ เพิ่มหน้า" ก่อนครับ');
      return;
    }
    const curIdx = state.pages.findIndex(p => p.id === state.activePageId);
    if (curIdx !== -1) {
      const nextIdx = (curIdx + 1) % state.pages.length;
      const [moved] = state.pages.splice(curIdx, 1);
      state.pages.splice(nextIdx, 0, moved);
      renderPageTabs();
      saveState();
      if (window.showToast) window.showToast(`🔀 ย้ายหน้า "${moved.name}" ไปยังลำดับที่ ${nextIdx + 1} แล้ว`);
    }
  }

  // Switch Active Page
  function switchPage(pageId) {
    if (!pageId) return;
    state.activePageId = pageId;
    state.selectedWidgetId = null;
    renderPageTabs();
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    renderWidgetCustomizerPanel(null);
    saveState();
  }

  // Add New Page
  function addNewPage() {
    const pageNum = state.pages.length + 1;
    const newPage = {
      id: `page-${Date.now()}`,
      name: `หน้า ${pageNum}`,
      widgets: []
    };
    state.pages.push(newPage);
    switchPage(newPage.id);
    if (window.showToast) {
      window.showToast(`สร้าง ${newPage.name} เรียบร้อยแล้ว`);
    }
  }

  // Duplicate Current Page
  function duplicateCurrentPage() {
    const curPage = getActivePage();
    if (!curPage) return;
    const clonedWidgets = JSON.parse(JSON.stringify(curPage.widgets || [])).map(w => {
      w.id = `w-${w.type}-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`;
      return w;
    });
    const newPage = {
      id: `page-${Date.now()}`,
      name: `${curPage.name} (สำเนา)`,
      widgets: clonedWidgets
    };
    state.pages.push(newPage);
    switchPage(newPage.id);
    if (window.showToast) {
      window.showToast(`ทำสำเนา ${newPage.name} สำเร็จ`);
    }
  }

  // Rename Current Page
  function renameCurrentPage() {
    const curPage = getActivePage();
    if (!curPage) return;
    const newName = prompt('ระบุชื่อหน้าใหม่:', curPage.name);
    if (newName && newName.trim() && newName.trim() !== curPage.name) {
      curPage.name = newName.trim();
      renderPageTabs();
      saveState();
      if (window.showToast) window.showToast(`เปลี่ยนชื่อเป็น "${curPage.name}" สำเร็จ`);
    }
  }

  // Delete Page
  function deletePage(pageId) {
    if (state.pages.length <= 1) {
      if (window.showToast) window.showToast('ต้องมีเลย์เอาต์อย่างน้อย 1 หน้า');
      return;
    }
    const page = state.pages.find(p => p.id === pageId);
    if (!page) return;
    if (confirm(`คุณต้องการลบหน้า "${page.name}" หรือไม่? วิดเจ็ตทั้งหมดในหน้านี้จะหายไปด้วย`)) {
      const idx = state.pages.findIndex(p => p.id === pageId);
      if (idx !== -1) {
        state.pages.splice(idx, 1);
        if (state.activePageId === pageId) {
          state.activePageId = state.pages[0].id;
        }
        switchPage(state.activePageId);
        if (window.showToast) window.showToast('ลบหน้าเรียบร้อยแล้ว');
      }
    }
  }

  // Render Canvas Widgets
  function renderCanvasWidgets() {
    ensureChatThemesStyleSheet();
    const stage = document.getElementById('composerCanvasStage');
    if (!stage) return;

    // Clear existing widgets, keep guides container
    const guides = document.getElementById('composerSmartGuides');
    stage.innerHTML = '';
    if (guides) stage.appendChild(guides);

    const page = getActivePage();
    if (!page) return;

    page.widgets.forEach(w => {
      if (w.hidden) return;

      const isFull = isFullscreenWidget(w);
      if (isFull) {
        w.x = 0;
        w.y = 0;
        w.width = CANVAS_WIDTH;
        w.height = CANVAS_HEIGHT;
        w.noDrag = true;
        w.noResize = true;
        w.isFullScreen = true;
      }
      const isDanmaku = isFull;
      const el = document.createElement('div');
      const classes = ['composer-widget', 'widget', `type-${w.type}`];
      if (w.id === state.selectedWidgetId) classes.push('selected');
      if (w.locked) classes.push('locked');
      if (isFull) classes.push('widget-fullscreen-fixed', 'widget-danmaku-full');

      if (w.type === 'clock') {
        classes.push('clock-theme-' + (w.clockTheme || 'default'));
        if (w.clockStyle && w.clockStyle !== 'none') {
          classes.push('clock-style-set', 'clock-style-' + w.clockStyle);
        }
      }
      if (w.type === 'viewer') {
        classes.push('viewer-theme-' + (w.viewerTheme || 'default'));
        classes.push('viewer-align-' + (w.viewerAlign || 'left'));
        classes.push('viewer-direction-' + (w.viewerDirection || 'horizontal'));
      }
      if (w.type === 'webcam') {
        classes.push('webcam-theme-' + (w.webcamTheme || 'simple-white'));
        classes.push('ratio-' + (w.ratio || '16:9').replace(':', '-'));
        el.style.setProperty('--wc-border-width', (w.borderWidth || 4) + 'px');
      }
      if (w.type === 'chat') {
        classes.push('theme-' + (w.chatTheme || 'default'));
      }
      if (w.type === 'text') {
        classes.push('text-' + (w.textMode || 'ticker'));
        el.style.setProperty('--marquee-duration', (w.marqueeSpeed || 15) + 's');
      }

      el.className = classes.join(' ');
      el.id = `widget-${w.id}`;
      el.dataset.id = w.id;
      el.style.left = `${w.x}px`;
      el.style.top = `${w.y}px`;
      el.style.width = `${w.width}px`;
      el.style.height = `${w.height}px`;
      el.style.zIndex = w.z || 1;
      el.style.opacity = w.opacity ?? 1;

      // Badge - Move beneath widget frame if at the very top of canvas
      const isAtTop = (!isFull && w.y < 26);
      if (isAtTop) {
        el.classList.add('badge-at-bottom');
      }
      const badge = document.createElement('div');
      badge.className = `composer-widget-badge${isAtTop ? ' badge-bottom' : ''}`;
      badge.innerHTML = `<span>${getWidgetIcon(w.type)}</span> <span>${w.title}</span> <span style="opacity:0.75; font-size:10px;">${isFull ? 'เต็มจอ 1920×1080' : `${w.width}×${w.height}`}</span> <button type="button" class="btn-widget-gear" title="ตั้งค่าวิดเจ็ต" style="background:transparent; border:none; cursor:pointer; font-size:12px; margin-left:6px; padding:0 2px; color:#ffffff;">⚙️</button>`;
      
      const btnGear = badge.querySelector('.btn-widget-gear');
      if (btnGear) {
        btnGear.addEventListener('mousedown', (e) => e.stopPropagation());
        btnGear.addEventListener('click', (e) => {
          e.stopPropagation();
          openWidgetSettings(w.id);
        });
      }
      el.appendChild(badge);

      // Inner Content
      const inner = document.createElement('div');
      inner.className = 'composer-widget-inner';
      inner.innerHTML = renderWidgetInnerHtml(w);
      el.appendChild(inner);

      // 8 Resize Handles - Do NOT add handles if noResize or Danmaku
      if (!w.noResize && !isDanmaku) {
        const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
        handles.forEach(h => {
          const handle = document.createElement('div');
          handle.className = `composer-resize-handle handle-${h}`;
          handle.dataset.handle = h;
          el.appendChild(handle);
        });
      }

      // Selection & Drag listeners
      el.addEventListener('mousedown', (e) => {
        if (e.target.closest('.btn-widget-gear')) return;
        if (e.target.classList.contains('composer-resize-handle')) {
          startResize(e, w, e.target.dataset.handle);
        } else {
          startDrag(e, w);
        }
      });
      el.addEventListener('click', (e) => {
        if (e.target.closest('.btn-widget-gear')) return;
        selectWidget(w.id);
      });

      stage.appendChild(el);

      // Initialize Number Ticker for viewer widget
      if (w.type === 'viewer') {
        updateAllViewerTickers(el, w);
      }
    });
  }

  // Get Widget Icon
  function getWidgetIcon(type) {
    const icons = {
      chat: '💬',
      clock: '🕒',
      text: '🔤',
      character: '🎭',
      replie: '💬',
      avatar: '😊',
      webcam: '📹',
      goal: '🎯',
      donate_goal: '🎯',
      viewer: '👥',
      image: '🖼️',
      video: '🎬',
      alert: '🌐',
      browser: '🌐',
      now_playing: '🎵',
      emote_party: '🎉',
      ask: '🗳️',
      giveaway: '🎁',
      playroom: '🎮',
      randomizer: '🎲'
    };
    return icons[type] || '📦';
  }


  // === Takayu & Mooncape Clock Constants & Data ===
  const CC_COLOR_SCHEMES = {
    1: ['#FF5D5D', '#FFC3C3'],  // ดำ/แดง
    2: ['#1363DF', '#DFF6FF'],  // ฟ้า/เหลือง
    3: ['#07D01D', '#E0F3D2'],  // เขียว
    4: ['#F77E21', '#FEF9A7'],  // ส้ม/ชมพู
    5: ['#8D8DAA', '#F7F5F2'],  // ม่วง/ฟ้า
  };
  const CC_DAY_NAMES = ['Sun.', 'Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.'];

  const FPS_SVGS = {
    2: '<svg viewBox="0 0 300 50" preserveAspectRatio="none"><g class="fps-bg"><path d="M645.64,0H360.36L356,7.45,379.93,50H626.07L650,7.45Z" transform="translate(-353)"/></g><g class="fps-frame"><path d="M360.36,0h-3L353,7.45,376.93,50h3L356,7.45ZM648.64,0h-3L650,7.45,626.07,50h3L653,7.45Z" transform="translate(-353)"/></g></svg>',
    3: '<svg viewBox="0 0 244 50" preserveAspectRatio="none"><g class="fps-bg"><path d="M355.53-102.22h-220l-10-10v-26l10-10h220l10,10v26Z" transform="translate(-123.53 150.22)"/></g><g class="fps-frame"><path d="M128.53-150.22h68l2,2h-63l-10,10v26l-2-2v-31Zm237,12v26l-10,10h-63l2,2h68l5-5v-31Z" transform="translate(-123.53 150.22)"/></g></svg>',
    4: '<svg viewBox="0 0 300 50" preserveAspectRatio="none"><g class="fps-bg"><polygon points="5.44 49 1.18 42.19 26.92 1 294.56 1 298.82 7.81 273.08 49 5.44 49"/></g><g class="fps-frame"><path d="M1914-64.15l3.63,5.82-25.12,40.18H1626L1622.36-24l25.12-40.19H1914m1.11-2H1646.37L1620-24l4.88,7.81h268.75L1920-58.33l-4.88-7.82Z" transform="translate(-1620 66.15)"/></g></svg>',
  };

  const THAI_MONTHS_SHORT = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  const THAI_MONTHS_LONG = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'];
  const THAI_DAYS_SHORT = ['อา.', 'จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.'];
  const THAI_DAYS_LONG = ['วันอาทิตย์', 'วันจันทร์', 'วันอังคาร', 'วันพุธ', 'วันพฤหัสบดี', 'วันศุกร์', 'วันเสาร์'];
  const EN_MONTHS_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const EN_MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const EN_DAYS_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const EN_DAYS_LONG = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function formatClockDate(now, fmt = 'short', lang = 'th') {
    const isEn = lang === 'en';
    const month = now.getMonth();
    const day = now.getDate();
    const year = now.getFullYear();
    const dayName = isEn ? EN_DAYS_SHORT[now.getDay()] : THAI_DAYS_SHORT[now.getDay()];
    const dayNameLong = isEn ? EN_DAYS_LONG[now.getDay()] : THAI_DAYS_LONG[now.getDay()];

    if (fmt === 'long') {
      const mLong = isEn ? EN_MONTHS_LONG[month] : THAI_MONTHS_LONG[month];
      const yr = isEn ? year : year + 543;
      return `${dayNameLong} ${day} ${mLong} ${yr}`;
    } else if (fmt === 'iso') {
      return `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    } else if (fmt === 'weekday') {
      const mShort = isEn ? EN_MONTHS_SHORT[month] : THAI_MONTHS_SHORT[month];
      const yr = isEn ? year : String(year+543).slice(-2);
      return `${dayName} ${day} ${mShort} ${yr}`;
    }
    // short
    const mShort = isEn ? EN_MONTHS_SHORT[month] : THAI_MONTHS_SHORT[month];
    const yr = isEn ? year : String(year+543).slice(-2);
    return `${day} ${mShort} ${yr}`;
  }

  // Ensure scoped stylesheet for all 80 chat themes exists in head
  function ensureChatThemesStyleSheet() {
    let styleTag = document.getElementById('composer-chat-themes-styles');
    if (!styleTag) {
      styleTag = document.createElement('style');
      styleTag.id = 'composer-chat-themes-styles';
      document.head.appendChild(styleTag);
    }
    const allThemes = window.CWC_ALL_THEMES || [];
    if (!allThemes.length || styleTag.dataset.loaded === 'true') return;

    let cssText = `
      /* Base rule for chat messages to seamlessly adopt theme CSS variables */
      :is(.composer-widget, .widget).type-chat :is(.msg, .cwc-msg-item, .chat-line),
      :is(.composer-widget, .widget)[class*="theme-"] :is(.msg, .cwc-msg-item, .chat-line) {
        background: var(--box-bg, rgba(30, 31, 34, 0.85)) !important;
        border: var(--box-border, none) !important;
        border-radius: var(--box-radius, 8px) !important;
        box-shadow: var(--box-shadow, none) !important;
        color: var(--text-color, #ffffff);
        text-shadow: var(--text-shadow, none);
        padding: 8px 14px;
        box-sizing: border-box;
        transition: all 0.2s ease;
      }
    `;

    allThemes.forEach(t => {
      if (!t.css) return;
      const tid = t.id || t.key;
      const scoped = t.css
        .replace(/:root\b/g, `:is(.composer-widget, .widget).theme-${tid}, :is(.composer-widget, .widget)[data-theme="${tid}"]`)
        .replace(/(^|[\s,;{}])\.msg([:\s\.\-_\[{]|$)/g, `$1:is(.composer-widget, .widget).theme-${tid} :is(.msg, .cwc-msg-item, .chat-line)$2`)
        .replace(/(^|[\s,;{}])\.chat-line([:\s\.\-_\[{]|$)/g, `$1:is(.composer-widget, .widget).theme-${tid} :is(.msg, .cwc-msg-item, .chat-line)$2`);
      cssText += '\n' + scoped;
    });

    styleTag.textContent = cssText;
    styleTag.dataset.loaded = 'true';
  }

  function renderClockStyleHtml(w, now) {
    const style = w.clockStyle || w.clock_style || 'none';
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    const yr = now.getFullYear();
    const mo = String(now.getMonth() + 1).padStart(2, '0');
    const dy = String(now.getDate()).padStart(2, '0');
    const op = w.styleOpacity ?? w.style_opacity ?? 1.0;

    if (style === 'dot1' || style === 'dot2' || style === 'dot3') {
      let timeText = `${h}:${m}`;
      let waitChar = '◯';
      if (style === 'dot2') timeText = `${yr}.${mo}.${dy} ${h}:${m}`;
      else if (style === 'dot3') { timeText = `${dy}.${mo}.${yr} ${h}:${m}`; waitChar = '◎'; }
      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="dot-outbox">
            <div class="dot-inbox">
              <span class="dot-time">${timeText}</span>
              <span class="dot-wait">${waitChar}</span>
            </div>
          </div>
        </div>
      `;
    }

    if (style.startsWith('cc')) {
      const colorNum = parseInt(style.replace(/[^0-9]/g, '')) || 1;
      const variant = style.startsWith('ccdate') ? 'date' :
                      style.startsWith('cclive') ? 'live' :
                      style.startsWith('ccsec') ? 'sec' : 'normal';
      const colors = CC_COLOR_SCHEMES[colorNum] || CC_COLOR_SCHEMES[1];
      const ms = now.getMilliseconds();
      const deg = 6 * (now.getSeconds() + ms / 1000);
      const phase = Math.floor(now.getMinutes()) % 2;
      const [active, inactive] = phase === 0 ? colors : [colors[1], colors[0]];

      let extra = '';
      if (variant === 'date') {
        extra = `<div class="cc-t2">${mo}/${dy} ${CC_DAY_NAMES[now.getDay()]}</div>`;
      } else if (variant === 'live') {
        extra = `<div class="cc-live">LIVE</div>`;
      } else if (variant === 'sec') {
        extra = `<div class="cc-t2">${s}</div>`;
      }

      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="cc-main" style="width:140px; height:140px;">
            <div class="cc-oc" style="background:conic-gradient(${active} 0deg ${deg}deg, ${inactive} ${deg}deg 360deg);"></div>
            <div class="cc-ic"></div>
            <div class="cc-t1">${h}:${m}</div>
            ${extra}
          </div>
        </div>
      `;
    }

    if (style.startsWith('lt')) {
      let ltInner = '';
      if (style === 'lt1') {
        ltInner = `<div class="lt-live">LIVE</div><div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><div class="lt-date">${mo}/${dy} ${CC_DAY_NAMES[now.getDay()]}</div>`;
      } else if (style === 'lt2') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><div class="lt-date">${mo}/${dy} ${CC_DAY_NAMES[now.getDay()]}</div>`;
      } else if (style === 'lt3') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div>`;
      } else if (style === 'lt4') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><span class="lt-sec">${s}</span>`;
      } else if (style === 'lt5') {
        ltInner = `<div class="lt-time">${h}<span class="lt-colon">:</span>${m}</div><span class="lt-bolt-svg"><svg viewBox="0 0 20 30" style="width:14px; height:20px; fill:#ff0055;"><polygon points="12.4 0 1 18 9.2 18 7.617 30 19 12 10.8 12 12.4 0"/></svg></span><span class="lt-live-inline" style="font-size:18px; letter-spacing:4px; font-weight:700; color:#ff0055;">LIVE</span>`;
      }
      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="lt-nowtime">${ltInner}</div>
        </div>
      `;
    }

    if (style.startsWith('fps')) {
      const fpsNum = parseInt(style.replace(/[^0-9]/g, '')) || 2;
      return `
        <div class="composer-widget-inner widget-type-clock clock-style-set clock-style-${style}" style="opacity:${op}; justify-content:center; align-items:center;">
          <div class="fps-overlay">
            <div class="fps-svg">${FPS_SVGS[fpsNum] || FPS_SVGS[2]}</div>
            <div class="fps-time">${h}<span class="fps-colon">:</span>${m}<span class="fps-colon">:</span>${s}</div>
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner widget-type-clock" style="opacity:${op};">
        <div class="clock-time">${h}:${m}</div>
      </div>
    `;
  }

  // Render Inner HTML according to Widget Type
  function renderWidgetInnerHtml(w) {
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      const theme = w.chatTheme || 'default';

      if (mode === 'danmaku') {
        const clr = w.fontColor || '#ffffff';
        const fsz = w.fontSize || 24;
        const dur = w.speed || 6;
        const op = w.opacity ?? 1;
        const stroke = w.textStroke === true ? `-webkit-text-stroke: ${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order: stroke fill;` : '';
        const shadow = w.textShadow !== false ? `filter: drop-shadow(0 2px 4px ${w.textShadowColor || 'rgba(0,0,0,0.6)'});` : '';
        return `
          <div class="composer-widget-inner widget-type-chat widget-danmaku-layer" id="widget-danmaku-feed-${w.id}" style="background:transparent; overflow:hidden; position:absolute; inset:0;">
            <div class="danmaku-bullet-item" style="top:25%; left:0; font-size:${fsz}px; color:${clr}; opacity:${op}; ${stroke} ${shadow} animation:danmakuBulletRun ${dur}s linear infinite;">
              🚀 ดันมากุวิ่งบนจอสด ยินดีต้อนรับทุกคนครับ! 🔥
            </div>
            <div class="danmaku-bullet-item" style="top:55%; left:0; font-size:${fsz}px; color:#38bdf8; opacity:${op}; ${stroke} ${shadow} animation:danmakuBulletRun ${dur}s linear 2.5s infinite;">
              ✨ ภาพคมชัด 60fps ลื่นไหลดีมากครับ
            </div>
          </div>
        `;
      }

      if (mode === 'balloon') {
        const bg = w.balloonBg || '#ffffff';
        const clr = w.balloonTextColor || '#0f172a';
        const radius = w.balloonRadius ?? 14;
        const fsz = w.fontSize || 15;
        const op = w.balloonOpacity ?? 0.95;
        return `
          <div class="composer-widget-inner widget-type-chat" id="widget-balloon-feed-${w.id}" style="background:transparent; position:relative; align-items:flex-start; padding:12px; overflow-y:auto; overflow-x:hidden;">
            <div style="background:${bg}; color:${clr}; padding:10px 16px; border-radius:${radius}px; font-weight:600; font-size:${fsz}px; box-shadow:0 6px 18px rgba(0,0,0,0.35); position:relative; margin-bottom:12px; max-width:90%; opacity:${op};">
              <div style="font-weight:700; font-size:12px; color:#6366f1; margin-bottom:3px;">Zack_Channel:</div>
              <div>สวัสดีครับทุกคน ยินดีต้อนรับสู่ไลฟ์สตรีมครับ! ✨</div>
              <svg style="position:absolute; bottom:-11px; left:22px; width:18px; height:12px; fill:${bg};" viewBox="0 0 18 12">
                <path d="M0 0 L18 0 L6 12 Z"/>
              </svg>
            </div>
          </div>
        `;
      }

      if (mode === 'character') {
        const charImg = w.imageUrl || './assets/dock_offline_character.png';
        const charName = w.characterName || 'Replie';
        const bubbleBg = w.charBubbleBg || 'rgba(255,255,255,0.96)';
        const textColor = w.charTextColor || '#0f172a';
        const fsz = w.charFontSize || 15;
        const isRight = w.charAlign === 'right';
        return `
          <div class="composer-widget-inner widget-type-chat" style="background:transparent; position:relative; display:flex; flex-direction:${isRight ? 'row-reverse' : 'row'}; align-items:flex-end; gap:14px; padding:12px; overflow:hidden;">
            <img id="widget-char-avatar-${w.id}" src="${charImg}" draggable="false" style="width:110px; height:110px; object-fit:contain; flex-shrink:0; pointer-events:none; -webkit-user-drag:none; transition:all 0.3s ease;" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
            <div style="background:${bubbleBg}; color:${textColor}; padding:12px 18px; border-radius:16px; font-size:${fsz}px; font-weight:600; box-shadow:0 8px 24px rgba(0,0,0,0.4); position:relative; flex:1;">
              <div style="font-size:11px; font-weight:700; color:#6366f1; margin-bottom:4px;">${charName}</div>
              <div id="widget-char-text-${w.id}">สวัสดีครับทุกคน! วันนี้ยินดีต้อนรับสู่ไลฟ์สตรีมนะครับ 🎮</div>
              <svg style="position:absolute; bottom:16px; ${isRight ? 'right:-10px; transform:scaleX(-1);' : 'left:-10px;'}; width:12px; height:16px; fill:${bubbleBg};" viewBox="0 0 12 16">
                <path d="M12 0 L12 16 L0 8 Z"/>
              </svg>
            </div>
          </div>
        `;
      }

      // Default or Theme with Full Scoped CSS Themes and Live Typography Sync
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const fWeight = w.fontWeight || '600';
      const uClr = w.usernameColor || '#38bdf8';
      const hex = w.bgColor || '#1e1f22';
      const r = parseInt(hex.slice(1, 3), 16) || 30;
      const g = parseInt(hex.slice(3, 5), 16) || 31;
      const b = parseInt(hex.slice(5, 7), 16) || 34;
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const pad = w.boxPadding ?? 6;
      const isTheme = (mode === 'theme') || (w.chatSubTab === 'theme') || (w.chatTheme && w.chatTheme !== 'default');
      const boxEnabled = w.boxEnabled !== false;

      let boxStyle = '';
      if (isTheme && !w.customBoxStyle) {
        boxStyle = ''; // Let theme variables take full effect
      } else if (boxEnabled) {
        boxStyle = `background:rgba(${r}, ${g}, ${b}, ${bgOp}); border-radius:${radius}px; padding:${pad}px 12px;`;
        if (w.boxWidth === 'full') boxStyle += ' width:100%;';
        if (w.boxBorder) boxStyle += ` border:${w.boxBorderWidth || 2}px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};`;
        if (w.boxGlow) boxStyle += ` box-shadow:0 0 12px ${w.boxGlowColor || '#a855f7'};`;
        else if (w.boxShadow) boxStyle += ' box-shadow:0 4px 12px rgba(0,0,0,0.3);';
      } else {
        boxStyle = 'background:transparent; padding:2px 0;';
      }

      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth || 1.5}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur || 3}px ${w.textShadowColor || '#000000'};` : '';
      const alignCss = w.align === 'center' ? 'center' : (w.align === 'right' ? 'flex-end' : 'flex-start');
      const dir = w.direction === 'top' ? 'column' : 'column-reverse';
      const justify = w.direction === 'top' ? 'flex-start' : 'flex-end';
      const spacing = w.msgSpacing ?? 6;

      // Container Background Box: transparent by default unless user enables it
      let containerStyle = 'background:transparent !important; border:none !important; padding:0;';
      if (w.containerBgEnabled) {
        const cHex = w.containerBgColor || '#0a0e1a';
        const cr = parseInt(cHex.slice(1, 3), 16) || 10;
        const cg = parseInt(cHex.slice(3, 5), 16) || 14;
        const cb = parseInt(cHex.slice(5, 7), 16) || 26;
        const cOp = (w.containerBgOpacity !== undefined) ? w.containerBgOpacity : 0.75;
        const cRadius = (w.containerRadius !== undefined) ? w.containerRadius : 8;
        containerStyle = `background:rgba(${cr}, ${cg}, ${cb}, ${cOp}) !important; border-radius:${cRadius}px; padding:8px;`;
        if (w.containerBorder) {
          containerStyle += ` border:${w.containerBorderWidth || 1}px solid ${w.containerBorderColor || 'rgba(255,255,255,0.2)'} !important;`;
        }
      }

      return `
        <div class="composer-widget-inner widget-type-chat theme-${theme}" style="${containerStyle}">
          <div id="widget-chat-feed-${w.id}" style="width:100%; height:100%; overflow-y:auto; overflow-x:hidden; display:flex; flex-direction:${dir}; justify-content:${justify}; gap:${spacing}px; padding:6px;">
            <div class="cwc-msg-item msg chat-line theme-${theme}" style="align-self:${alignCss}; ${boxStyle}">
              <div class="msg-bg"></div>
              <span class="author" style="color:${uClr}; font-weight:700; margin-right:6px;">Gamer_Pro:</span>
              <span class="text" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; font-weight:${fWeight}; color:${fClr}; ${strokeCss} ${shadowCss}">สวัสดีทุกคนในไลฟ์สตรีมครับ! 🎮</span>
            </div>
            <div class="cwc-msg-item msg chat-line theme-${theme}" style="align-self:${alignCss}; ${boxStyle}">
              <div class="msg-bg"></div>
              <span class="author" style="color:${uClr}; font-weight:700; margin-right:6px;">Zack_Live:</span>
              <span class="text" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; font-weight:${fWeight}; color:${fClr}; ${strokeCss} ${shadowCss}">สตรีมภาพสวยคมชัด 60fps มากครับ 🔥</span>
            </div>
            <div class="cwc-msg-item msg chat-line theme-${theme}" style="align-self:${alignCss}; ${boxStyle}">
              <div class="msg-bg"></div>
              <span class="author" style="color:${uClr}; font-weight:700; margin-right:6px;">Mali_TH:</span>
              <span class="text" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; font-weight:${fWeight}; color:${fClr}; ${strokeCss} ${shadowCss}">ยินดีต้อนรับเพื่อนๆ ทุกคนนะครับ 💖</span>
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'clock') {
      const now = new Date();
      const hasStyle = (w.clockMode === 'style') || (w.clockStyle && w.clockStyle !== 'none');
      if (hasStyle && w.clockStyle && w.clockStyle !== 'none') {
        return renderClockStyleHtml(w, now);
      }

      // Theme Mode (Default / 32 Themes)
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      const s = String(now.getSeconds()).padStart(2, '0');
      let timeStr = `${h}:${m}`;
      if (w.clockFormat === 'HH:MM:SS') {
        timeStr = `${h}:${m}:${s}`;
      } else if (w.clockFormat === '12') {
        let hrs = now.getHours();
        const ampm = hrs >= 12 ? 'PM' : 'AM';
        hrs = hrs % 12 || 12;
        timeStr = w.showSeconds === false ? `${hrs}:${m} ${ampm}` : `${hrs}:${m}:${s} ${ampm}`;
      }

      const theme = w.clockTheme || w.clock_theme || 'default';
      const fsz = w.fontSize || w.font_size || 28;
      const clr = w.timeColor || w.time_color || w.fontColor || '';
      const op = w.themeOpacity ?? w.theme_opacity ?? 1.0;
      const showDate = w.showDate ?? w.show_date ?? false;
      const dateStr = showDate ? formatClockDate(now, w.dateFormat || w.date_format || 'short', w.dateLang || w.date_lang || 'th') : '';
      const dateFsz = w.dateFontSize || w.date_font_size || 14;
      const dateClr = w.dateColor || w.date_color || '#cccccc';

      return `
        <div class="composer-widget-inner widget-type-clock clock-theme-${theme}" style="opacity:${op}; font-size:${fsz}px; flex-direction:column; gap:2px; justify-content:center; align-items:center;">
          <div class="clock-time" style="${clr ? 'color:' + clr + ';' : ''}">${timeStr}</div>
          ${showDate ? `<div class="clock-date" style="color:${dateClr}; font-size:${dateFsz}px;">${dateStr}</div>` : ''}
        </div>
      `;
    }

    if (w.type === 'text') {
      const isTicker = w.textMode === 'ticker';
      const fsz = w.fontSize || 18;
      const clr = w.fontColor || '#ffffff';
      const bgEnabled = w.bgEnabled !== false;
      const bg = bgEnabled ? (w.bgColor || '#141923') : 'transparent';
      const text = w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม ยินดีต้อนรับทุกคนครับ!';
      
      const strokeW = w.textStrokeWidth ?? (w.textStroke ? 2 : 0);
      const strokeCss = strokeW > 0 ? `-webkit-text-stroke:${strokeW}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      
      const shadowB = w.textShadowBlur ?? (w.textShadow ? 3 : 0);
      const shadowCss = shadowB > 0 ? `text-shadow:0 1px ${shadowB}px ${w.textShadowColor || '#000000'};` : '';
      
      const fFam = w.fontFamily || 'Kanit';
      const dur = w.marqueeSpeed || 15;
      const vAlign = w.vAlign || 'center';
      const justifyVal = vAlign === 'top' ? 'flex-start' : (vAlign === 'bottom' ? 'flex-end' : 'center');

      if (isTicker) {
        return `
          <div class="composer-widget-inner widget-type-text widget-text-ticker" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; --marquee-duration:${dur}s; display:flex; flex-direction:column; justify-content:${justifyVal};">
            <span>${text}</span>
          </div>
        `;
      }

      return `
        <div class="composer-widget-inner widget-type-text" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; display:flex; flex-direction:column; justify-content:${justifyVal}; text-align:center;">
          <span>${text}</span>
        </div>
      `;
    }

    if (w.type === 'character') {
      const charImg = w.imageUrl || './assets/dock_offline_character.png';
      const charName = w.characterName || 'Replie';
      return `
        <div class="composer-widget-inner widget-type-character" id="compInnerChar_${w.id}" style="position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; width:100%; height:100%;">
          <div class="char-bubble-container" id="compCharBubble_${w.id}" style="display:none; position:absolute; bottom:calc(100% - 10px); left:50%; transform:translateX(-50%); background:rgba(15,23,42,0.95); border:1.5px solid #38bdf8; border-radius:12px; padding:6px 14px; font-size:12px; font-weight:600; color:#fff; white-space:nowrap; box-shadow:0 4px 20px rgba(0,0,0,0.5); z-index:30; pointer-events:none; transition:opacity 0.3s ease;">
            <span class="char-bubble-text" id="compCharBubbleText_${w.id}">สวัสดีครับทุกคน!</span>
          </div>
          <img class="widget-character-img" id="compCharImg_${w.id}" src="${charImg}" alt="Character" draggable="false" style="pointer-events:none; -webkit-user-drag:none; transition:transform 0.25s ease;" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
          <div class="widget-character-name" id="compCharName_${w.id}">${charName}</div>
        </div>
      `;
    }

    if (w.type === 'webcam') {
      return `
        <div class="composer-widget-inner widget-type-webcam" style="background:transparent !important; border:none !important;">
          <div class="webcam-frame" style="width:100%; height:100%; background:transparent !important;"></div>
        </div>
      `;
    }

    if (w.type === 'ask') {
      const liveAsk = window._liveAskState || {};
      const isAskActive = liveAsk && liveAsk.active === true && (liveAsk.phase === 'voting' || liveAsk.phase === 'ended');
      const q = liveAsk.question || w.askQuestion || '';
      const choices = liveAsk.choices || [];

      const choicesHtml = choices.map(c => `
        <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
          <div style="position:absolute; inset:0; width:${c.pct}%; background:${c.color || '#38bdf8'}; opacity:0.25; border-radius:6px; transition:width 0.4s ease;"></div>
          <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
            <span>${c.label}: ${c.text}</span>
            <span style="color:${c.color || '#38bdf8'}; font-weight:700;">${c.pct}% (${c.votes || 0})</span>
          </div>
        </div>
      `).join('');

      return `
        <div class="composer-widget-inner widget-type-ask" id="compInnerAsk_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center; pointer-events:none;">
          <!-- Standby: hidden. Only displays during active poll -->
          <div class="ask-panel" id="compAskPanel_${w.id}" style="${isAskActive ? 'display:block;' : 'display:none;'} background:rgba(15, 23, 42, 0.92); border:1.5px solid rgba(56, 189, 248, 0.35); border-radius:12px; padding:12px 16px; box-shadow:0 8px 30px rgba(0,0,0,0.5); pointer-events:auto;">
            <div style="font-weight:700; font-size:14px; color:#38bdf8; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
              <span id="compAskQ_${w.id}">📊 ${q}</span>
              <span id="compAskTimer_${w.id}" style="font-size:11px; color:#94a3b8; background:rgba(255,255,255,0.08); padding:2px 8px; border-radius:4px;">⏱</span>
            </div>
            <div id="compAskChoicesList_${w.id}" style="display:flex; flex-direction:column; gap:6px;">
              ${choicesHtml}
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'giveaway') {
      const liveGw = window._liveGwState || {};
      const isGwActive = liveGw && liveGw.active === true && (liveGw.phase === 'running' || liveGw.phase === 'winner');
      const prize = liveGw.prize || w.prizeTitle || '';
      const code = liveGw.code || '#join';
      const count = liveGw.count ?? 0;
      const winner = liveGw.winner;

      return `
        <div class="composer-widget-inner widget-type-giveaway" id="compInnerGw_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center; pointer-events:none;">
          <!-- Standby: hidden. Only displays during active giveaway -->
          <div class="giveaway-panel" id="compGwPanel_${w.id}" style="${isGwActive ? 'display:block;' : 'display:none;'} background:rgba(15, 23, 42, 0.92); border:1.5px solid rgba(244, 63, 94, 0.4); border-radius:14px; padding:14px 18px; text-align:center; box-shadow:0 8px 30px rgba(0,0,0,0.5); pointer-events:auto;">
            <div style="font-size:24px; margin-bottom:4px;">🎁</div>
            <div id="compGwPrize_${w.id}" style="font-weight:700; font-size:15px; color:#f43f5e; margin-bottom:4px;">${prize}</div>
            <div id="compGwHint_${w.id}" style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">พิมพ์ <strong style="color:#fb7185;">${code}</strong> ในแชทเพื่อเข้าร่วมสุ่ม</div>
            <div id="compGwWinner_${w.id}" style="${winner ? 'display:block;' : 'display:none;'} background:linear-gradient(135deg, #f59e0b, #d97706); color:#fff; font-weight:800; font-size:13px; padding:6px 12px; border-radius:8px; margin-bottom:10px; box-shadow:0 4px 15px rgba(245,158,11,0.4);">
              🏆 ผู้ชนะ: <span id="compGwWinnerName_${w.id}">${winner || ''}</span>
            </div>
            <div style="background:rgba(255,255,255,0.08); border-radius:6px; height:6px; overflow:hidden; margin-bottom:8px;">
              <div style="width:70%; height:100%; background:linear-gradient(90deg, #f43f5e, #fb7185); border-radius:6px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
              <span id="compGwCount_${w.id}">ผู้เข้าร่วม: ${count} คน</span>
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'playroom') {
      return `
        <div class="composer-widget-inner widget-type-playroom" id="compInnerPlayroom_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; position:relative; display:flex; align-items:center; justify-content:center;">
          <!-- Active Playroom Media Stage -->
          <div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; position:absolute; inset:0; z-index:10; flex-direction:column; align-items:center; justify-content:center;">
            <div class="playroom-clip-card" id="compPlayroomCard_${w.id}" style="background:rgba(15,23,42,0.95); border:2px solid #a855f7; border-radius:16px; padding:16px 22px; box-shadow:0 12px 40px rgba(0,0,0,0.8); text-align:center; max-width:92%; transition:transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);">
              <div style="font-size:36px; margin-bottom:4px;">🎮</div>
              <div class="playroom-clip-title" id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#c084fc; margin-bottom:4px;">เซียมซี: ดวงมหาเฮง</div>
              <div id="compPlayroomTag_${w.id}" style="font-size:11px; color:#cbd5e1; background:rgba(255,255,255,0.08); padding:3px 10px; border-radius:20px; display:inline-block;">คำสั่ง !fortune</div>
              <div style="margin-top:12px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;">
                <div id="compPlayroomBar_${w.id}" style="height:100%; width:100%; background:linear-gradient(90deg, #a855f7, #ec4899); transition:width linear;"></div>
              </div>
            </div>
          </div>
          <!-- Idle Waiting Banner (Hidden on Standby) -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="display:none !important;"></div>
        </div>
      `;
    }

    if (w.type === 'goal' || w.type === 'donate_goal') {
      const current = w.goalCurrent ?? 650;
      const target = w.goalTarget ?? 1000;
      const pct = Math.min(100, Math.round((current / (target || 1)) * 100));
      const title = w.goalTitle || 'เป้าหมายผู้ติดตาม';
      const unit = w.goalUnit || 'คน';

      return `
        <div class="composer-widget-inner widget-type-goal">
          <div class="widget-goal-header">
            <span>${title}</span>
            <span style="color:#ec4899;">${current} / ${target} ${unit}</span>
          </div>
          <div class="widget-goal-bar-track">
            <div class="widget-goal-bar-fill" style="width:${pct}%;"></div>
          </div>
        </div>
      `;
    }

    if (w.type === 'viewer') {
      const iconSize = w.iconSize || 20;
      const showIcon = w.showIcon !== false;
      const mode = w.viewerMode || 'both';
      const count = w.mockViewerCount || 1250;
      const fFam = w.fontFamily || 'Kanit';
      const fsz = w.fontSize || 18;
      const clr = w.fontColor || '#ffffff';
      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth || 2}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur || 3}px ${w.textShadowColor || '#000000'};` : '';

      const wantTotal = (mode === 'total' || mode === 'both');
      const wantPerPlat = (mode === 'per_platform' || mode === 'both');

      let totalHtml = '';
      if (wantTotal) {
        totalHtml = `<span class="viewer-total">${showIcon ? peopleIconSpan(iconSize) : ''}<span class="viewer-ticker" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; ${strokeCss} ${shadowCss}"></span></span>`;
      }

      let chipsHtml = '';
      if (wantPerPlat) {
        const activePlats = (w.viewerPlatforms && w.viewerPlatforms.length > 0) ? w.viewerPlatforms : ['youtube', 'twitch', 'tiktok', 'kick'];
        chipsHtml = activePlats.map(plat => `
          <span class="viewer-chip" data-platform="${plat}" style="font-family:'${fFam}',sans-serif; font-size:${Math.round(fsz * 0.9)}px; color:${clr}; ${strokeCss} ${shadowCss}">
            ${showIcon ? getPlatformIconHtml(plat, iconSize) : ''}
            <span class="viewer-ticker" data-platform-ticker="${plat}" style="font-family:'${fFam}',sans-serif; font-size:${Math.round(fsz * 0.9)}px; color:${clr}; ${strokeCss} ${shadowCss}"></span>
          </span>
        `).join('');
      }

      return `
        <div class="composer-widget-inner widget-type-viewer viewer-theme-${w.viewerTheme || 'default'} viewer-align-${w.viewerAlign || 'left'} viewer-direction-${w.viewerDirection || 'horizontal'}" style="background:transparent !important; border:none !important;">
          ${totalHtml}
          ${chipsHtml}
        </div>
      `;
    }

    if (w.type === 'randomizer') {
      return `
        <div class="composer-widget-inner widget-type-randomizer" id="compInnerRandomizer_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; align-items:center; justify-content:center; pointer-events:none;">
          <!-- Standby: completely transparent. Only reveals card during active spin -->
          <div class="randomizer-card-box" id="compRandomizerCard_${w.id}" style="display:none; background:rgba(2, 6, 23, 0.95); border:2px solid #1e293b; border-radius:18px; padding:20px 32px; text-align:center; box-shadow:0 12px 40px rgba(0,0,0,0.8); pointer-events:auto; min-width:320px;">
            <div style="font-size:12px; color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">🎲 QUICK RANDOMIZER</div>
            <div id="compRandomizerResult_${w.id}" style="font-size:28px; font-weight:800; color:#38bdf8; text-shadow:0 0 16px rgba(56,189,248,0.5); margin-bottom:8px;"></div>
            <div id="compRandomizerHint_${w.id}" style="font-size:11.5px; color:#cbd5e1; background:rgba(255,255,255,0.06); padding:4px 12px; border-radius:20px; display:inline-block;">สุ่มสำเร็จ 🎉</div>
          </div>
        </div>
      `;
    }

    if (w.type === 'emote_party') {
      return `
        <div class="composer-widget-inner widget-type-emote-party" id="widget-emote-party-${w.id}" style="background:transparent !important; border:none !important; position:relative; overflow:hidden; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'image') {
      if (w.imageUrl) {
        return `
          <div class="composer-widget-inner widget-type-image" style="background:transparent !important; border:none !important; width:100%; height:100%;">
            <img src="${w.imageUrl}" draggable="false" style="width:100%; height:100%; object-fit:${w.fitMode || 'cover'}; pointer-events:none; -webkit-user-drag:none; display:block;" onerror="this.style.display='none';">
          </div>
        `;
      }
      return `
        <div class="composer-widget-inner widget-type-image" style="background:transparent !important; border:none !important; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'video') {
      if (w.videoUrl) {
        return `
          <div class="composer-widget-inner widget-type-video" style="background:transparent !important; border:none !important; width:100%; height:100%;">
            <video src="${w.videoUrl}" autoplay loop muted playsinline style="width:100%; height:100%; object-fit:${w.fitMode || 'cover'}; pointer-events:none; background:transparent; display:block;"></video>
          </div>
        `;
      }
      return `
        <div class="composer-widget-inner widget-type-video" style="background:transparent !important; border:none !important; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'alert') {
      if (w.url) {
        return `
          <div class="composer-widget-inner widget-type-alert" style="background:transparent !important; border:none !important; width:100%; height:100%;">
            <iframe src="${w.url}" allow="autoplay; fullscreen" referrerpolicy="no-referrer" style="width:100%; height:100%; border:none; background:transparent; pointer-events:none;"></iframe>
          </div>
        `;
      }
      return `
        <div class="composer-widget-inner widget-type-alert" style="background:transparent !important; border:none !important; width:100%; height:100%;"></div>
      `;
    }

    if (w.type === 'now_playing') {
      const isTrans = w.npTransparent === true;
      const bgStyle = isTrans ? 'background:transparent !important;' : `background:${w.npBgColor || '#1a1a2e'}; opacity:${w.npBgOpacity ?? 0.85};`;
      const artRadius = w.npArtRadius ?? 6;
      const artSize = w.npArtSize ?? 48;
      const radius = w.npRadius ?? 8;
      const accent = w.npAccentColor || '#1db954';
      const textClr = w.npTextColor || '#ffffff';
      const fontSize = w.npFontSize || 14;
      const artistFontSize = w.npArtistFontSize || 12;
      const timeFontSize = w.npTimeFontSize || 10;
      const styleName = w.npStyle || 'flat';
      const showArt = w.npShowArt !== false;
      const showProgress = w.npShowProgress !== false;

      const songTitle = w.songTitle || 'Never Gonna Give You Up';
      const artistName = w.artist || 'Rick Astley';

      return `
        <div class="composer-widget-inner widget-type-now-playing" style="--np-accent:${accent}; position:relative; ${bgStyle} border-radius:${radius}px; padding:8px 12px; display:flex !important; flex-direction:row !important; align-items:center !important; gap:12px; width:100%; height:100%; box-sizing:border-box; overflow:hidden;">
          <div class="np-style-overlay np-style-${styleName}" style="position:absolute; inset:0; pointer-events:none; border-radius:${radius}px;"></div>
          ${showArt ? `
            <div class="np-art" style="width:${artSize}px; height:${artSize}px; min-width:${artSize}px; max-width:${artSize}px; border-radius:${artRadius}px; background:rgba(255,255,255,0.1); overflow:hidden; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:22px; z-index:1;">
              ${w.thumbnailUrl ? `<img src="${w.thumbnailUrl}" style="width:100%; height:100%; object-fit:cover; display:block;">` : `🎵`}
            </div>
          ` : ''}
          <div class="np-info" style="flex:1; min-width:0; overflow:hidden; display:flex; flex-direction:column; justify-content:center; gap:2px; z-index:1;">
            <div class="np-title-wrap" style="overflow:hidden; white-space:nowrap; position:relative;">
              <span class="np-title-text" style="display:inline-block; font-weight:600; font-size:${fontSize}px; color:${textClr}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100%;">${songTitle}</span>
            </div>
            <div class="np-artist" style="font-size:${artistFontSize}px; color:rgba(255,255,255,0.7); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${artistName}</div>
            ${showProgress ? `
              <div class="np-progress-row" style="display:flex; align-items:center; gap:6px; margin-top:4px; width:100%;">
                <span style="font-size:${timeFontSize}px; color:rgba(255,255,255,0.5); min-width:28px;">1:24</span>
                <div style="flex:1; height:4px; background:rgba(255,255,255,0.18); border-radius:2px; overflow:hidden;">
                  <div style="width:45%; height:100%; background:${accent}; border-radius:2px;"></div>
                </div>
                <span style="font-size:${timeFontSize}px; color:rgba(255,255,255,0.5); min-width:28px; text-align:right;">3:32</span>
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:transparent; border:none;">
        <span>${w.title}</span>
      </div>
    `;
  }

  // Select Widget (Does NOT open or close drawer automatically)
  function selectWidget(widgetId) {
    state.selectedWidgetId = widgetId;
    document.querySelectorAll('.composer-widget').forEach(el => {
      el.classList.toggle('selected', el.dataset.id === widgetId);
    });
    renderLayersList();
    updateTransformInspector();

    // If Left Drawer is ALREADY open, smoothly update customizer to the newly selected widget
    const leftPanel = document.getElementById('composerSidebarLeft');
    if (widgetId && leftPanel && !leftPanel.classList.contains('collapsed')) {
      renderWidgetCustomizerPanel(widgetId);
    }
  }

  // Helper to get all active window contexts where Composer UI or cursor may be active
  function getActiveComposerWindows() {
    const list = [window];
    if (typeof window._popoutWindows === 'object' && window._popoutWindows) {
      const pop = window._popoutWindows['composer'];
      if (pop && !pop.closed && !list.includes(pop)) {
        list.push(pop);
      }
    }
    return list;
  }

  // Start Dragging Widget (Multi-window aware)
  function startDrag(e, widget) {
    if (widget.locked || widget.noDrag || isFullscreenWidget(widget)) {
      selectWidget(widget.id);
      return;
    }
    e.stopPropagation();
    if (e.cancelable) e.preventDefault();
    selectWidget(widget.id);

    state.isDragging = true;
    state.dragStartMouseX = e.clientX;
    state.dragStartMouseY = e.clientY;
    state.dragStartWidgetX = widget.x;
    state.dragStartWidgetY = widget.y;

    const targetWin = e.view || (e.target && e.target.ownerDocument && e.target.ownerDocument.defaultView) || window;
    const wins = getActiveComposerWindows();
    if (!wins.includes(targetWin)) wins.push(targetWin);

    state.activeDragWindows = wins;
    wins.forEach(w => {
      try {
        w.addEventListener('mousemove', onMouseMove);
        w.addEventListener('mouseup', onMouseUp);
      } catch (err) {}
    });
  }

  // Start Resizing Widget
  function startResize(e, widget, handle) {
    if (widget.locked || widget.noResize || isFullscreenWidget(widget)) return;
    e.stopPropagation();
    if (e.cancelable) e.preventDefault();
    selectWidget(widget.id);

    state.isResizing = true;
    state.activeResizeHandle = handle;
    state.dragStartMouseX = e.clientX;
    state.dragStartMouseY = e.clientY;
    state.dragStartWidgetX = widget.x;
    state.dragStartWidgetY = widget.y;
    state.dragStartWidgetW = widget.width;
    state.dragStartWidgetH = widget.height;

    const targetWin = e.view || (e.target && e.target.ownerDocument && e.target.ownerDocument.defaultView) || window;
    const wins = getActiveComposerWindows();
    if (!wins.includes(targetWin)) wins.push(targetWin);

    state.activeDragWindows = wins;
    wins.forEach(w => {
      try {
        w.addEventListener('mousemove', onMouseMove);
        w.addEventListener('mouseup', onMouseUp);
      } catch (err) {}
    });
  }

  // Mouse Move for Drag & Resize
  function onMouseMove(e) {
    const widget = getSelectedWidget();
    if (!widget) return;

    const zoom = (state.zoom > 2 ? state.zoom / 100 : (state.zoom || 0.45));
    const deltaX = (e.clientX - state.dragStartMouseX) / zoom;
    const deltaY = (e.clientY - state.dragStartMouseY) / zoom;

    if (state.isDragging) {
      let newX = Math.round(state.dragStartWidgetX + deltaX);
      let newY = Math.round(state.dragStartWidgetY + deltaY);

      if (state.snapGuides) {
        newX = Math.round(newX / 10) * 10;
        newY = Math.round(newY / 10) * 10;
      }

      // Clamp strictly within canvas boundary
      newX = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, newX));
      newY = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, newY));

      widget.x = newX;
      widget.y = newY;
    } else if (state.isResizing) {
      const handle = state.activeResizeHandle;
      let newX = state.dragStartWidgetX;
      let newY = state.dragStartWidgetY;
      let newW = state.dragStartWidgetW;
      let newH = state.dragStartWidgetH;

      if (handle.includes('e')) {
        const maxW = CANVAS_WIDTH - newX;
        newW = Math.max(50, Math.min(maxW, state.dragStartWidgetW + deltaX));
      }
      if (handle.includes('s')) {
        const maxH = CANVAS_HEIGHT - newY;
        newH = Math.max(30, Math.min(maxH, state.dragStartWidgetH + deltaY));
      }
      if (handle.includes('w')) {
        const rightEdge = state.dragStartWidgetX + state.dragStartWidgetW;
        let potentialX = state.dragStartWidgetX + deltaX;
        potentialX = Math.max(0, potentialX);
        let potentialW = rightEdge - potentialX;
        if (potentialW < 50) {
          potentialW = 50;
          potentialX = rightEdge - 50;
        }
        newW = potentialW;
        newX = potentialX;
      }
      if (handle.includes('n')) {
        const bottomEdge = state.dragStartWidgetY + state.dragStartWidgetH;
        let potentialY = state.dragStartWidgetY + deltaY;
        potentialY = Math.max(0, potentialY);
        let potentialH = bottomEdge - potentialY;
        if (potentialH < 30) {
          potentialH = 30;
          potentialY = bottomEdge - 30;
        }
        newH = potentialH;
        newY = potentialY;
      }

      if (state.snapGuides) {
        newW = Math.round(newW / 10) * 10;
        newH = Math.round(newH / 10) * 10;
        newX = Math.round(newX / 10) * 10;
        newY = Math.round(newY / 10) * 10;
      }

      // Final boundary clamp: widget must NEVER overflow canvas boundaries in any direction
      newX = Math.max(0, Math.min(CANVAS_WIDTH - 50, newX));
      newY = Math.max(0, Math.min(CANVAS_HEIGHT - 30, newY));
      newW = Math.max(50, Math.min(CANVAS_WIDTH - newX, newW));
      newH = Math.max(30, Math.min(CANVAS_HEIGHT - newY, newH));

      widget.x = newX;
      widget.y = newY;
      widget.width = newW;
      widget.height = newH;
    }

    const el = document.getElementById(`widget-${widget.id}`);
    if (el) {
      el.style.left = `${widget.x}px`;
      el.style.top = `${widget.y}px`;
      el.style.width = `${widget.width}px`;
      el.style.height = `${widget.height}px`;

      // Update badge position dynamically (flip beneath widget frame if at the very top of canvas)
      const isDanmakuFull = widget.isDanmaku || widget.chatMode === 'danmaku';
      const isAtTop = (!isDanmakuFull && widget.y < 26);
      el.classList.toggle('badge-at-bottom', isAtTop);
      const badge = el.querySelector('.composer-widget-badge');
      if (badge) {
        badge.classList.toggle('badge-bottom', isAtTop);
        badge.innerHTML = `<span>${getWidgetIcon(widget.type)}</span> <span>${widget.title}</span> <span style="opacity:0.75; font-size:10px;">${widget.width}×${widget.height}</span> <button type="button" class="btn-widget-gear" title="ตั้งค่าวิดเจ็ต" style="background:transparent; border:none; cursor:pointer; font-size:12px; margin-left:6px; padding:0 2px; color:#ffffff;">⚙️</button>`;
        const btnGear = badge.querySelector('.btn-widget-gear');
        if (btnGear) {
          btnGear.addEventListener('mousedown', (ev) => ev.stopPropagation());
          btnGear.addEventListener('click', (ev) => {
            ev.stopPropagation();
            openWidgetSettings(widget.id);
          });
        }
      }
    }

    updateTransformInspector();
  }

  // Mouse Up
  function onMouseUp() {
    if (state.isDragging || state.isResizing) {
      state.isDragging = false;
      state.isResizing = false;
      state.activeResizeHandle = null;
      state.suppressCanvasDeselectUntil = Date.now() + 200;

      const wins = state.activeDragWindows || getActiveComposerWindows();
      wins.forEach(w => {
        try {
          w.removeEventListener('mousemove', onMouseMove);
          w.removeEventListener('mouseup', onMouseUp);
        } catch (err) {}
      });
      state.activeDragWindows = null;
      saveState();
    }
  }

  // Move Layer by one step: dir = -1 (ขึ้นบน / bring forward), dir = +1 (ลงล่าง / send backward)
  function moveLayerByOne(id, dir) {
    const page = getActivePage();
    if (!page || !page.widgets || page.widgets.length <= 1) return;

    // Sort descending by z (index 0 is topmost with highest z)
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));
    const idx = sorted.findIndex(w => w.id === id);
    if (idx < 0) return;

    const targetIdx = idx + dir;
    if (targetIdx < 0 || targetIdx >= sorted.length) {
      if (window.showToast) {
        window.showToast(dir < 0 ? 'เลเยอร์อยู่บนสุดแล้ว' : 'เลเยอร์อยู่ล่างสุดแล้ว');
      }
      return;
    }

    // Swap positions
    const temp = sorted[idx];
    sorted[idx] = sorted[targetIdx];
    sorted[targetIdx] = temp;

    // Reassign z values: index 0 gets highest z
    const total = sorted.length;
    sorted.forEach((w, i) => {
      w.z = total - i;
    });

    renderCanvasWidgets();
    renderLayersList();
    saveState();

    if (window.showToast) {
      window.showToast(dir < 0 ? 'สลับ Layer ขึ้นบน ⬆️ (Ctrl+[)' : 'สลับ Layer ลงล่าง ⬇️ (Ctrl+])');
    }
  }

  // Keyboard Shortcuts
  function handleKeyDown(e) {
    if (!state.selectedWidgetId) return;
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    const widget = getSelectedWidget();
    if (!widget) return;

    const isCtrl = e.ctrlKey || e.metaKey;

    if (e.key === 'Delete' || e.key === 'Backspace') {
      e.preventDefault();
      deleteSelectedWidget();
    } else if (e.key === 'd' && isCtrl) {
      e.preventDefault();
      duplicateWidget(widget.id);
    } else if (isCtrl && (e.key === '[' || e.code === 'BracketLeft')) {
      e.preventDefault();
      moveLayerByOne(widget.id, -1); // สลับ layer ขึ้นบน
    } else if (isCtrl && (e.key === ']' || e.code === 'BracketRight')) {
      e.preventDefault();
      moveLayerByOne(widget.id, +1); // สลับ layer ลงล่าง
    } else if (e.key.startsWith('Arrow') && !widget.locked && !widget.noDrag && !widget.isDanmaku) {
      e.preventDefault();
      const step = e.shiftKey ? 10 : 1;
      if (e.key === 'ArrowLeft') widget.x -= step;
      if (e.key === 'ArrowRight') widget.x += step;
      if (e.key === 'ArrowUp') widget.y -= step;
      if (e.key === 'ArrowDown') widget.y += step;
      widget.x = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, widget.x));
      widget.y = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, widget.y));
      renderCanvasWidgets();
      updateTransformInspector();
      saveState();
    }
  }

  // Show Duplicate Confirmation Modal (Zero GPU Lockup)
  function showComposerConfirmModal({ title, message, confirmText, cancelText, onConfirm }) {
    const modal = document.getElementById('composerConfirmModal');
    if (!modal) {
      if (confirm(message)) onConfirm();
      return;
    }
    const titleEl = document.getElementById('composerConfirmTitle');
    const msgEl = document.getElementById('composerConfirmMsg');
    const okBtn = document.getElementById('btnComposerConfirmOk');
    const cancelBtn = document.getElementById('btnComposerConfirmCancel');

    if (titleEl) titleEl.textContent = title || 'วิดเจ็ตนี้มีอยู่ในหน้าจอแล้ว';
    if (msgEl) msgEl.textContent = message || 'หน้าจอนี้มีวิดเจ็ตนี้อยู่แล้ว คุณต้องการเพิ่มซ้ำอีกอันหรือไม่?';
    if (okBtn) okBtn.textContent = confirmText || '➕ ยืนยันเพิ่มซ้ำ';
    if (cancelBtn) cancelBtn.textContent = cancelText || 'ยกเลิก';

    modal.style.display = 'flex';

    const cleanup = () => {
      modal.style.display = 'none';
      okBtn.removeEventListener('click', handleOk);
      cancelBtn.removeEventListener('click', handleCancel);
    };

    const handleOk = () => {
      cleanup();
      if (typeof onConfirm === 'function') onConfirm();
    };

    const handleCancel = () => {
      cleanup();
    };

    okBtn.addEventListener('click', handleOk, { once: true });
    cancelBtn.addEventListener('click', handleCancel, { once: true });
  }

  // Check if widget exists before adding, warn if duplicate
  function checkAndAddWidget(type, chatMode = null) {
    const page = getActivePage();
    if (!page) return;

    let exists = false;
    let widgetName = '';
    if (type === 'chat') {
      const mode = chatMode || 'default';
      const names = {
        default: 'กล่องแชทมาตรฐาน',
        danmaku: 'แชทลอยหน้าจอ ดันมากุ',
        balloon: 'บอลลูนแชท',
        character: 'แชทตัวละคร'
      };
      widgetName = names[mode] || 'กล่องแชท';
      exists = page.widgets.some(w => w.type === 'chat' && (w.chatMode || 'default') === mode);
    } else {
      const names = {
        clock: 'นาฬิกาสตรีม',
        text: 'แถบข้อความประกาศ',
        character: 'ตัวละครพูด Replie',
        webcam: 'กรอบกล้องเว็บแคม',
        goal: 'เป้าหมายผู้ติดตาม',
        viewer: 'ตัวนับยอดผู้ชมสด',
        image: 'กรอบรูปภาพ',
        video: 'วิดีโอลูป',
        alert: 'เบราว์เซอร์ URL',
        now_playing: 'เพลงที่กำลังเล่น',
        emote_party: 'ปาร์ตี้อีโมทลอย'
      };
      widgetName = names[type] || 'วิดเจ็ตนี้';
      exists = page.widgets.some(w => w.type === type);
    }

    if (exists) {
      showComposerConfirmModal({
        title: 'วิดเจ็ตนี้มีอยู่ในหน้าจอแล้ว',
        message: `หน้าจอนี้มี "${widgetName}" อยู่แล้ว คุณต้องการเพิ่มซ้ำอีกอันหรือไม่?`,
        confirmText: '➕ ยืนยันเพิ่มซ้ำ',
        cancelText: 'ยกเลิก',
        onConfirm: () => {
          addWidget(type, chatMode);
        }
      });
    } else {
      addWidget(type, chatMode);
    }
  }

  // Add a new Widget to canvas
  function addWidget(type, chatMode = null) {
    const page = getActivePage();
    if (!page) return;

    const presets = {
      chat: {
        title: 'กล่องแชทมาตรฐาน',
        width: 440,
        height: 600,
        chatMode: chatMode || 'default',
        chatTheme: 'default',
        fontSize: 15,
        fontColor: '#ffffff',
        bgColor: '#1e1f22',
        bgOpacity: 0.85,
        boxRadius: 8,
        containerBgEnabled: false,
        containerBgColor: '#0a0e1a',
        containerBgOpacity: 0.75,
        containerRadius: 8,
        animation: 'slide',
        exitAnimation: 'auto',
        autoHide: false,
        hideAfter: 8
      },
      clock: { title: 'นาฬิกาสตรีม', width: 280, height: 80, clockTheme: 'cyberpunk', clockFormat: '24', showSeconds: true, fontSize: 26, fontColor: '#38bdf8' },
      text: { title: 'แถบข้อความประกาศ', width: 800, height: 50, text: 'ข้อความสตรีมสดใหม่ ยินดีต้อนรับทุกคนครับ!', textMode: 'ticker', fontSize: 18, fontColor: '#ffffff' },
      character: { title: 'ตัวละครพูด Replie', width: 340, height: 420, characterName: 'Replie', imageUrl: './assets/dock_offline_character.png' },
      webcam: { title: 'กรอบกล้องเว็บแคม', width: 480, height: 270, ratio: '16:9', borderColor: '#5865f2', borderWidth: 4, borderRadius: 8, glow: true, showStreamerName: true, streamerName: 'Streamer LIVE' },
      goal: { title: 'เป้าหมายผู้ติดตาม', width: 420, height: 80, goalTitle: 'เป้าหมายผู้ติดตาม', goalCurrent: 650, goalTarget: 1000, goalUnit: 'คน' },
      viewer: { title: 'ตัวนับยอดผู้ชมสด', width: 240, height: 55, viewerTheme: 'pill', mockViewerCount: 1250 },
      image: { title: 'กรอบรูปภาพแบนเนอร์', width: 340, height: 200, fitMode: 'contain' },
      video: { title: 'วิดีโอลูป', width: 480, height: 270, loop: true },
      alert: { title: 'เบราว์เซอร์ URL', width: 400, height: 300, alertUrl: 'https://overlay.example.com' },
      now_playing: { title: 'เพลงที่กำลังเล่น', width: 340, height: 75, songTitle: 'Never Gonna Give You Up', artist: 'Rick Astley', npSource: 'auto', np_source: 'auto' },
      emote_party: { title: 'ปาร์ตี้อีโมทลอย (Emote Party)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true },
      ask: { title: 'โพลสำรวจความคิดเห็น (ASK)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true, askQuestion: 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?', askChoices: ['Valorant', 'ROV / Garena'] },
      giveaway: { title: 'สุ่มแจกรางวัล (Giveaway)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true, prizeTitle: 'รางวัลพิเศษประจำสตรีม', code: '#join' },
      replie: { title: 'ตัวละครพูด Replie เต็มจอ', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true, characterName: 'Replie', imageUrl: './assets/dock_offline_character.png' },
      randomizer: { title: 'สุ่มด่วน (Quick Randomizer)', width: CANVAS_WIDTH, height: CANVAS_HEIGHT, isFullScreen: true, noDrag: true, noResize: true },
      playroom: { title: 'Playroom Studio มินิเกม', width: 480, height: 320 }
    };

    const preset = presets[type] || { title: 'วิดเจ็ตใหม่', width: 300, height: 200 };

    if (type === 'chat') {
      const mode = chatMode || 'default';
      preset.chatMode = mode;
      if (mode === 'danmaku') {
        preset.title = 'แชทลอยหน้าจอ ดันมากุ';
        preset.width = CANVAS_WIDTH;
        preset.height = CANVAS_HEIGHT;
        preset.isDanmaku = true;
        preset.noResize = true;
        preset.noDrag = true;
        preset.fontSize = 24;
        preset.fontColor = '#ffffff';
        preset.textStroke = false;
        preset.textStrokeWidth = 2;
        preset.strokeColor = '#000000';
        preset.textShadow = true;
        preset.textShadowBlur = 3;
        preset.textShadowColor = 'rgba(0,0,0,0.6)';
        preset.speed = 6;
        preset.slider_zone = 'middle';
      } else if (mode === 'balloon') {
        preset.title = 'บอลลูนแชท';
        preset.width = 460;
        preset.height = 480;
        preset.balloonBg = '#ffffff';
        preset.balloonTextColor = '#0f172a';
        preset.balloonRadius = 14;
        preset.balloonOpacity = 0.95;
        preset.fontSize = 15;
      } else if (mode === 'character') {
        preset.title = 'แชทตัวละคร';
        preset.width = 480;
        preset.height = 480;
        preset.characterName = 'Replie';
        preset.imageUrl = './assets/dock_offline_character.png';
        preset.charBubbleBg = 'rgba(255,255,255,0.96)';
        preset.charTextColor = '#0f172a';
        preset.charFontSize = 15;
      } else {
        preset.title = 'กล่องแชทมาตรฐาน';
      }
    }

    const isFull = isFullscreenWidget(preset) || (type === 'chat' && chatMode === 'danmaku');
    const newWidget = {
      id: `w-${type}-${Date.now()}`,
      type: type,
      title: preset.title,
      x: isFull ? 0 : Math.round(CANVAS_WIDTH / 2 - preset.width / 2),
      y: isFull ? 0 : Math.round(CANVAS_HEIGHT / 2 - preset.height / 2),
      width: isFull ? CANVAS_WIDTH : preset.width,
      height: isFull ? CANVAS_HEIGHT : preset.height,
      z: page.widgets.length + 1,
      opacity: 1,
      locked: false,
      hidden: false,
      noDrag: isFull,
      noResize: isFull,
      isFullScreen: isFull,
      text: preset.text || '',
      ...preset
    };
    if (isFull) {
      newWidget.x = 0;
      newWidget.y = 0;
      newWidget.width = CANVAS_WIDTH;
      newWidget.height = CANVAS_HEIGHT;
      newWidget.noDrag = true;
      newWidget.noResize = true;
      newWidget.isFullScreen = true;
    }

    page.widgets.push(newWidget);
    renderCanvasWidgets();
    selectWidget(newWidget.id);
    saveState();

    // Visual Flash & Temporary Indicator
    setTimeout(() => {
      const el = document.getElementById(`widget-${newWidget.id}`);
      if (el) {
        el.classList.add('composer-widget-flash-highlight');
        const ind = document.createElement('div');
        ind.className = 'composer-widget-new-indicator';
        ind.textContent = `✨ เพิ่ม${preset.title}แล้ว`;
        el.appendChild(ind);
        setTimeout(() => {
          el.classList.remove('composer-widget-flash-highlight');
          ind.remove();
        }, 2200);

        // Center within outer scroll if not danmaku
        const outer = document.getElementById('composerCanvasOuter');
        if (outer && !preset.isDanmaku) {
          const zoom = (state.zoom || 45) / 100;
          const targetX = newWidget.x * zoom;
          const targetY = newWidget.y * zoom;
          outer.scrollTo({
            left: Math.max(0, targetX - outer.clientWidth / 2 + (newWidget.width * zoom) / 2),
            top: Math.max(0, targetY - outer.clientHeight / 2 + (newWidget.height * zoom) / 2),
            behavior: 'smooth'
          });
        }
      }
    }, 50);

    if (window.showToast) {
      window.showToast(`เพิ่ม${preset.title}บนหน้าจอแล้ว`);
    }
  }

  // Duplicate Widget
  function duplicateWidget(id) {
    const page = getActivePage();
    if (!page) return;
    const orig = page.widgets.find(w => w.id === id);
    if (!orig) return;

    const newWidget = JSON.parse(JSON.stringify(orig));
    newWidget.id = `w-${orig.type}-${Date.now()}`;
    newWidget.title = `${orig.title} คัดลอก`;
    if (!newWidget.isDanmaku && newWidget.chatMode !== 'danmaku') {
      newWidget.x += 30;
      newWidget.y += 30;
      newWidget.x = Math.max(0, Math.min(CANVAS_WIDTH - newWidget.width, newWidget.x));
      newWidget.y = Math.max(0, Math.min(CANVAS_HEIGHT - newWidget.height, newWidget.y));
    }
    newWidget.z = page.widgets.length + 1;

    page.widgets.push(newWidget);
    renderCanvasWidgets();
    selectWidget(newWidget.id);
    saveState();
  }

  // Delete a widget by id
  function deleteWidget(id) {
    const page = getActivePage();
    if (!page || !id) return;

    const idx = page.widgets.findIndex(w => w.id === id);
    if (idx !== -1) {
      const removed = page.widgets.splice(idx, 1)[0];
      if (state.selectedWidgetId === id) {
        state.selectedWidgetId = null;
        renderWidgetCustomizerPanel(null);
      }
      renderCanvasWidgets();
      renderLayersList();
      updateTransformInspector();
      saveState();

      if (window.showToast) {
        window.showToast(`ลบ${removed.title}เรียบร้อยแล้ว`);
      }
    }
  }

  // Delete selected widget
  function deleteSelectedWidget() {
    deleteWidget(state.selectedWidgetId);
  }

  // Render Layers List
  function renderLayersList() {
    const list = document.getElementById('composerLayersList');
    if (!list) return;

    const page = getActivePage();
    if (!page) {
      list.innerHTML = '<div style="font-size:11.5px; color:var(--dc-text-muted); padding:10px;">ไม่มีวิดเจ็ต</div>';
      return;
    }

    list.innerHTML = '';
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));
    const countEl = document.getElementById('composerLayerCount');
    if (countEl) countEl.textContent = `${sorted.length} เลเยอร์`;

    // SVG Icons
    const svgSettings = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`;
    const svgEye = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
    const svgEyeOff = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
    const svgLock = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`;
    const svgUnlock = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 9.9-1"></path></svg>`;
    const svgTrash = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;

    sorted.forEach(w => {
      const item = document.createElement('div');
      item.className = `composer-layer-item ${w.id === state.selectedWidgetId ? 'active' : ''}`;
      item.dataset.id = w.id;
      item.draggable = true;

      item.innerHTML = `
        <div class="composer-layer-handle" title="คลิกค้างเพื่อลากสลับลำดับเลเยอร์">⠿</div>
        <span class="composer-layer-icon">${getWidgetIcon(w.type)}</span>
        <span class="composer-layer-name" title="${w.title}">${w.title}</span>
        <div class="composer-layer-actions">
          <button type="button" class="composer-btn-layer-action btn-layer-setting" data-action="setting" data-layer-id="${w.id}" title="ตั้งค่าวิดเจ็ต">
            ${svgSettings}
          </button>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-hide" title="${w.hidden ? 'แสดง' : 'ซ่อน'}">
            ${w.hidden ? svgEyeOff : svgEye}
          </button>
          <button type="button" class="composer-btn-layer-action" data-action="toggle-lock" title="${w.locked ? 'ปลดล็อค' : 'ล็อค'}">
            ${w.locked ? svgLock : svgUnlock}
          </button>
          <button type="button" class="composer-btn-layer-action close-red" data-action="delete" title="ลบวิดเจ็ต">
            ${svgTrash}
          </button>
        </div>
      `;

      // Drag & Drop Reordering
      item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', w.id);
        item.classList.add('dragging');
      });

      item.addEventListener('dragover', (e) => {
        e.preventDefault();
        const rect = item.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        if (e.clientY < midY) {
          item.classList.add('drag-over-top');
          item.classList.remove('drag-over-bottom');
        } else {
          item.classList.add('drag-over-bottom');
          item.classList.remove('drag-over-top');
        }
      });

      item.addEventListener('dragleave', () => {
        item.classList.remove('drag-over-top', 'drag-over-bottom');
      });

      item.addEventListener('drop', (e) => {
        e.preventDefault();
        item.classList.remove('drag-over-top', 'drag-over-bottom');
        const srcId = e.dataTransfer.getData('text/plain');
        const targetId = w.id;
        if (!srcId || srcId === targetId) return;

        const srcIdx = page.widgets.findIndex(x => x.id === srcId);
        const targetIdx = page.widgets.findIndex(x => x.id === targetId);
        if (srcIdx === -1 || targetIdx === -1) return;

        const [moved] = page.widgets.splice(srcIdx, 1);
        const rect = item.getBoundingClientRect();
        const insertAfter = (e.clientY >= rect.top + rect.height / 2);
        const newTargetIdx = page.widgets.findIndex(x => x.id === targetId);
        page.widgets.splice(insertAfter ? newTargetIdx + 1 : newTargetIdx, 0, moved);

        // Reassign z indices from bottom to top
        page.widgets.forEach((itemW, idx) => {
          itemW.z = idx + 1;
        });

        renderCanvasWidgets();
        renderLayersList();
        saveState();
        if (window.showToast) window.showToast(`✨ สลับลำดับเลเยอร์ ${moved.title} เรียบร้อยแล้ว`);
      });

      item.addEventListener('dragend', () => {
        document.querySelectorAll('.composer-layer-item').forEach(el => {
          el.classList.remove('dragging', 'drag-over-top', 'drag-over-bottom');
        });
      });

      item.addEventListener('click', (e) => {
        const actionBtn = e.target.closest('.composer-btn-layer-action');
        if (actionBtn) {
          e.stopPropagation();
          const act = actionBtn.dataset.action;
          if (act === 'toggle-hide') {
            w.hidden = !w.hidden;
            renderCanvasWidgets();
            renderLayersList();
            saveState();
          } else if (act === 'toggle-lock') {
            w.locked = !w.locked;
            renderCanvasWidgets();
            renderLayersList();
            saveState();
          } else if (act === 'setting') {
            selectWidget(w.id);
            openWidgetSettings(w.id);
          } else if (act === 'delete') {
            deleteWidget(w.id);
          }
        } else {
          selectWidget(w.id);
        }
      });

      list.appendChild(item);
    });
  }

  // Align Widget
  function alignWidget(direction) {
    const widget = getSelectedWidget();
    if (!widget || widget.locked || isFullscreenWidget(widget)) return;

    if (direction === 'left') widget.x = 0;
    if (direction === 'center') widget.x = Math.round(CANVAS_WIDTH / 2 - widget.width / 2);
    if (direction === 'right') widget.x = CANVAS_WIDTH - widget.width;
    if (direction === 'top') widget.y = 0;
    if (direction === 'middle') widget.y = Math.round(CANVAS_HEIGHT / 2 - widget.height / 2);
    if (direction === 'bottom') widget.y = CANVAS_HEIGHT - widget.height;

    widget.x = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, widget.x));
    widget.y = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, widget.y));

    renderCanvasWidgets();
    updateTransformInspector();
    saveState();
  }

  // Update Transform Inspector
  function updateTransformInspector() {
    const widget = getSelectedWidget();
    const inpX = document.getElementById('compPropX');
    const inpY = document.getElementById('compPropY');
    const inpW = document.getElementById('compPropW');
    const inpH = document.getElementById('compPropH');
    const inpOp = document.getElementById('compPropOp');

    if (!widget) {
      if (inpX) { inpX.value = '-'; inpX.disabled = false; }
      if (inpY) { inpY.value = '-'; inpY.disabled = false; }
      if (inpW) { inpW.value = '-'; inpW.disabled = false; }
      if (inpH) { inpH.value = '-'; inpH.disabled = false; }
      if (inpOp) inpOp.value = '100%';
      return;
    }

    const isFull = isFullscreenWidget(widget);
    if (inpX) { inpX.value = isFull ? 0 : widget.x; inpX.disabled = isFull; }
    if (inpY) { inpY.value = isFull ? 0 : widget.y; inpY.disabled = isFull; }
    if (inpW) { inpW.value = isFull ? CANVAS_WIDTH : widget.width; inpW.disabled = isFull; }
    if (inpH) { inpH.value = isFull ? CANVAS_HEIGHT : widget.height; inpH.disabled = isFull; }
    if (inpOp) inpOp.value = isFull ? `${Math.round((widget.opacity ?? 1) * 100)}% - ล็อคเต็มจอ (1920×1080)` : `${Math.round((widget.opacity ?? 1) * 100)}%`;
  }

  // Open Left Widget Customizer Drawer
  function openWidgetSettings(widgetId) {
    if (!widgetId) return;
    state.selectedWidgetId = widgetId;
    state.customizerManuallyCollapsed = false;
    renderCanvasWidgets();
    renderLayersList();
    updateTransformInspector();
    renderWidgetCustomizerPanel(widgetId);

    const leftPanel = document.getElementById('composerSidebarLeft');
    const expandBtn = document.getElementById('btnExpandCustPanel');
    if (leftPanel) leftPanel.classList.remove('collapsed');
    if (expandBtn) expandBtn.classList.remove('visible');
  }

  const openWidgetCustomizer = openWidgetSettings;

  // Setup Canvas Events with flicker-free deselect, Ctrl+Wheel Zoom, and Overlapping Context Menu
  function setupCanvasEvents() {
    const viewport = document.getElementById('composerViewport');
    const stage = document.getElementById('composerCanvasStage');
    if (!viewport || !stage) return;

    // Suppress deselect when clicking a widget
    viewport.addEventListener('click', (e) => {
      if (Date.now() < (state.suppressCanvasDeselectUntil || 0)) return;
      if (e.target.id === 'composerViewport' || e.target.id === 'composerCanvasStage' || e.target.id === 'composerCanvasOuter') {
        selectWidget(null);
      }
    });

    // Spacebar Canvas Panning & Double-Spacebar Reset (Photoshop / Figma style)
    let isSpacebarDown = false;
    let isPanningCanvas = false;
    let panStartX = 0;
    let panStartY = 0;
    let panStartScrollLeft = 0;
    let panStartScrollTop = 0;
    let lastSpacebarPressTime = 0;

    function bindSpacebarPanning(winTarget) {
      if (!winTarget || winTarget.__bpSpacebarPanningBound) return;
      winTarget.__bpSpacebarPanningBound = true;

      winTarget.addEventListener('keydown', (e) => {
        const activeTag = winTarget.document?.activeElement ? winTarget.document.activeElement.tagName.toLowerCase() : '';
        if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select' || winTarget.document?.activeElement?.isContentEditable) return;

        if (e.code === 'Space' && !e.repeat) {
          const now = Date.now();
          if (now - lastSpacebarPressTime < 350) {
            e.preventDefault();
            autoFitCanvas();
            const vp = document.getElementById('composerViewport');
            if (vp) {
              vp.scrollLeft = (vp.scrollWidth - vp.clientWidth) / 2;
              vp.scrollTop = (vp.scrollHeight - vp.clientHeight) / 2;
            }
            if (window.showToast) window.showToast('🎯 พอดีจอ & จัดกึ่งกลางผ้าใบ (Double Spacebar)');
            lastSpacebarPressTime = 0;
            return;
          }
          lastSpacebarPressTime = now;
          isSpacebarDown = true;
          const vp = document.getElementById('composerViewport');
          if (vp) vp.style.cursor = 'grab';
        }
      });

      winTarget.addEventListener('keyup', (e) => {
        if (e.code === 'Space') {
          isSpacebarDown = false;
          isPanningCanvas = false;
          const vp = document.getElementById('composerViewport');
          if (vp) vp.style.cursor = '';
        }
      });

      winTarget.addEventListener('mousemove', (e) => {
        if (isPanningCanvas && isSpacebarDown) {
          const vp = document.getElementById('composerViewport');
          if (vp) {
            const dx = e.clientX - panStartX;
            const dy = e.clientY - panStartY;
            vp.scrollLeft = panStartScrollLeft - dx;
            vp.scrollTop = panStartScrollTop - dy;
            e.preventDefault();
          }
        }
      });

      winTarget.addEventListener('mouseup', () => {
        if (isPanningCanvas) {
          isPanningCanvas = false;
          const vp = document.getElementById('composerViewport');
          if (vp) vp.style.cursor = isSpacebarDown ? 'grab' : '';
        }
      });
    }

    bindSpacebarPanning(window);

    viewport.addEventListener('mousedown', (e) => {
      if (isSpacebarDown) {
        isPanningCanvas = true;
        panStartX = e.clientX;
        panStartY = e.clientY;
        panStartScrollLeft = viewport.scrollLeft;
        panStartScrollTop = viewport.scrollTop;
        viewport.style.cursor = 'grabbing';
        e.preventDefault();
        e.stopPropagation();
      }
    });

    // Ctrl + Mouse Wheel Canvas Zoom
    viewport.addEventListener('wheel', (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.05 : -0.05;
        const currentZoom = state.zoom || 0.45;
        const newZoom = Math.min(1.5, Math.max(0.2, currentZoom + delta));
        setZoom(newZoom);
      }
    }, { passive: false });

    // Right-Click Context Menu on Canvas Stage
    const hideContextMenu = () => {
      const existing = document.getElementById('composerContextMenu');
      if (existing) existing.remove();
    };

    document.addEventListener('click', (e) => {
      if (!e.target.closest('#composerContextMenu')) {
        hideContextMenu();
      }
    });

    stage.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      hideContextMenu();

      const page = getActivePage();
      if (!page || !page.widgets || page.widgets.length === 0) return;

      const rect = stage.getBoundingClientRect();
      const scale = state.zoom > 2 ? state.zoom / 100 : (state.zoom || 0.45);
      const canvasX = (e.clientX - rect.left) / scale;
      const canvasY = (e.clientY - rect.top) / scale;

      // Find all widgets at this coordinate (Fullscreen widgets cover [0, 0, CANVAS_WIDTH, CANVAS_HEIGHT])
      const widgetsAtPoint = page.widgets.filter(w => {
        if (isFullscreenWidget(w)) {
          return canvasX >= 0 && canvasX <= CANVAS_WIDTH && canvasY >= 0 && canvasY <= CANVAS_HEIGHT;
        }
        return canvasX >= w.x && canvasX <= (w.x + w.width) &&
               canvasY >= w.y && canvasY <= (w.y + w.height);
      }).sort((a, b) => (b.z || 0) - (a.z || 0));

      if (widgetsAtPoint.length === 0) return;

      const menu = document.createElement('div');
      menu.id = 'composerContextMenu';
      menu.className = 'composer-context-menu';
      menu.style.left = `${e.clientX + 4}px`;
      menu.style.top = `${e.clientY + 4}px`;

      let menuHtml = `
        <div class="composer-ctx-header">
          <span>📦 วิดเจ็ตที่จุดนี้</span>
          <span style="color:#38bdf8; font-weight:700;">${widgetsAtPoint.length} เลเยอร์</span>
        </div>
        <div class="composer-ctx-list">
      `;

      widgetsAtPoint.forEach(targetW => {
        menuHtml += `
          <div class="composer-ctx-widget-row" data-widget-id="${targetW.id}">
            <div class="composer-ctx-widget-info">
              <span class="composer-ctx-widget-icon">${getWidgetIcon(targetW.type)}</span>
              <span class="composer-ctx-widget-title">${targetW.title}</span>
            </div>
            <span class="composer-ctx-arrow">▶</span>
            <div class="composer-ctx-flyout-menu">
              <div class="composer-ctx-action" data-action="setting">⚙️ ตั้งค่าวิดเจ็ต</div>
              <div class="composer-ctx-action" data-action="duplicate">📋 ทำซ้ำ</div>
              <div class="composer-ctx-action" data-action="toggle-hide">${targetW.hidden ? '👁️‍🗨️ แสดงวิดเจ็ต' : '👁️ ซ่อนวิดเจ็ต'}</div>
              <div class="composer-ctx-action" data-action="toggle-lock">${targetW.locked ? '🔓 ปลดล็อควิดเจ็ต' : '🔒 ล็อควิดเจ็ต'}</div>
              <div class="composer-ctx-divider"></div>
              <div class="composer-ctx-action danger" data-action="delete">🗑️ ลบวิดเจ็ต</div>
            </div>
          </div>
        `;
      });

      menuHtml += `</div>`;
      menu.innerHTML = menuHtml;
      document.body.appendChild(menu);

      // Bind flyout actions
      menu.querySelectorAll('.composer-ctx-widget-row').forEach(row => {
        const wid = row.dataset.widgetId;
        const targetW = page.widgets.find(w => w.id === wid);
        if (!targetW) return;

        row.querySelectorAll('.composer-ctx-action').forEach(actBtn => {
          actBtn.addEventListener('click', (ev) => {
            ev.stopPropagation();
            hideContextMenu();
            const action = actBtn.dataset.action;
            if (action === 'setting') {
              selectWidget(targetW.id);
              openWidgetSettings(targetW.id);
            } else if (action === 'duplicate') {
              duplicateWidget(targetW.id);
            } else if (action === 'toggle-hide') {
              targetW.hidden = !targetW.hidden;
              renderCanvasWidgets();
              renderLayersList();
              saveState();
            } else if (action === 'toggle-lock') {
              targetW.locked = !targetW.locked;
              renderCanvasWidgets();
              renderLayersList();
              saveState();
            } else if (action === 'delete') {
              deleteWidget(targetW.id);
            }
          });
        });
      });
    });
  }

  // Render Left Customizer Panel with all settings for the selected widget
  function renderWidgetCustomizerPanel(id) {
    let demoHtml = '';
    let specificHtml = '';
    const page = getActivePage();
    if (!page) return;
    const w = page.widgets.find(x => x.id === id);
    if (!w) return;

    const iconEl = document.getElementById('compCustIcon');
    const titleEl = document.getElementById('compCustTitle');
    const typeEl = document.getElementById('compCustType');
    const bodyEl = document.getElementById('composerCustomizerBody');
    if (!bodyEl) return;

    let dispTitle = w.title;
    let dispType = 'การปรับแต่งวิดเจ็ต';
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        dispTitle = 'แชทลอยหน้าจอ ดันมากุ';
        dispType = 'วิดเจ็ตแชทลอยหน้าจอแบบ Danmaku';
      } else if (mode === 'balloon') {
        dispTitle = 'บอลลูนแชท';
        dispType = 'วิดเจ็ตแชทสไตล์บอลลูนคำพูด';
      } else if (mode === 'character') {
        dispTitle = 'แชทตัวละคร';
        dispType = 'วิดเจ็ตแชทพร้อมตัวละครสนทนา';
      } else {
        dispTitle = 'กล่องแชทมาตรฐาน';
        dispType = 'วิดเจ็ตกล่องแชทสด';
      }
    } else {
      const typeNames = {
        clock: 'วิดเจ็ตนาฬิกาสตรีม',
        text: 'วิดเจ็ตแถบข้อความประกาศ',
        webcam: 'วิดเจ็ตกรอบเว็บแคม',
        goal: 'วิดเจ็ตเป้าหมายยอดผู้ติดตาม',
        viewer: 'วิดเจ็ตตัวนับยอดผู้ชมสด',
        character: 'วิดเจ็ตตัวละครพูด Replie',
        image: 'วิดเจ็ตกรอบรูปภาพแบนเนอร์',
        video: 'วิดเจ็ตวิดีโอลูป',
        alert: 'วิดเจ็ตเบราว์เซอร์ URL ภายนอก',
        now_playing: 'วิดเจ็ตเพลงที่กำลังเล่น',
        emote_party: 'วิดเจ็ตปาร์ตี้อีโมทลอย'
      };
      dispType = typeNames[w.type] || 'การปรับแต่งวิดเจ็ต';
    }

    if (iconEl) iconEl.textContent = getWidgetIcon(w.type);
    if (titleEl) titleEl.textContent = dispTitle;
    if (typeEl) typeEl.textContent = dispType;

    // Helper binder for inputs
    const bindField = (elId, key, type = 'text', suffix = '') => {
      const el = document.getElementById(elId);
      if (!el) return;
      const handler = () => {
        if (type === 'checkbox') {
          w[key] = el.checked;
        } else if (type === 'number') {
          w[key] = parseFloat(el.value);
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + suffix;
        } else if (type === 'opacity') {
          w[key] = parseFloat(el.value) / 100;
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + '%';
        } else {
          w[key] = el.value;
        }
        renderCanvasWidgets();
        renderLayersList();
        updateTransformInspector();
        saveState();
      };
      el.addEventListener('input', handler);
      el.addEventListener('change', handler);
    };

    // Build Demo Action Bar HTML with interactive custom input and live test
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">⚡ ทดสอบกระสุนดันมากุบนจอ</span>
              <span style="font-size:11px; color:#94a3b8;">วิ่งบนจอตามโซน</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ข้อความกระสุนที่นี่..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions" style="display:flex; gap:6px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuLoop" style="flex:1;">▶ เล่นกระสุนดันมากุสด</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuSingle" style="flex:1;">⚡ ปล่อย 1 ข้อความ</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatClear" style="padding:6px 10px;" title="ล้างข้อความทั้งหมด">🧹</button>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">💬 ทดสอบบอลลูนคำพูด</span>
              <span style="font-size:11px; color:#94a3b8;">บอลลูนเด้งสด</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ข้อความบอลลูน..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions" style="display:flex; gap:6px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoBalloonSingle" style="flex:1;">💬 ส่งบอลลูน 1 ข้อความ</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatClear" style="padding:6px 10px;" title="ล้างข้อความทั้งหมด">🧹</button>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">🎭 ทดสอบบทพูดตัวละคร</span>
              <span style="font-size:11px; color:#94a3b8;">ตัวละครขยับพร้อมคำพูด</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ให้ตัวละครพูด..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoCharTalk" style="width:100%;">▶ สุ่มบทพูดตัวละครสด</button>
            </div>
          </div>
        `;
      } else {
        demoHtml = `
          <div class="comp-demo-section" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:10px; margin-bottom:12px;">
            <div class="comp-demo-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="comp-demo-title" style="font-size:12.5px; font-weight:700; color:#38bdf8;">🎮 ทดสอบจำลองส่งข้อความแชท</span>
              <span style="font-size:11px; color:#94a3b8;">พิมพ์ส่งข้อความขึ้นจอสด</span>
            </div>
            <div style="display:flex; gap:6px; margin-bottom:8px;">
              <input type="text" class="cwc-input-text" id="compChatDemoInput" placeholder="พิมพ์ข้อความทดสอบที่นี่..." style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              <button type="button" class="btn-comp-demo-action" id="btnCompChatDemoSend" style="padding:6px 14px; font-weight:700; background:#3b82f6; color:#ffffff;">ส่ง</button>
            </div>
            <div class="comp-demo-actions" style="display:flex; gap:6px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatLoop" style="flex:1;">▶ เล่นแชทต่อเนื่อง</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatSingle" style="flex:1;">➕ สุ่ม 1 ข้อความ</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatClear" style="padding:6px 10px;" title="ล้างข้อความทั้งหมด">🧹</button>
            </div>
          </div>
        `;
      }
    } else if (w.type === 'clock') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🕒 ทดสอบสลับรูปแบบเวลา</span>
            <span style="font-size:11px; color:#94a3b8;">นาฬิกาเดินสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockToggle">🕒 สลับ 12 / 24 ชม.</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockSecs">⏱️ สลับแสดงวินาที</button>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🔤 ทดสอบตัววิ่ง Marquee</span>
            <span style="font-size:11px; color:#94a3b8;">ข้อความเลื่อนวิ่งสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoTextTicker">▶ สลับโหมดตัววิ่ง</button>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">📹 ทดสอบสถานะเว็บแคม</span>
            <span style="font-size:11px; color:#94a3b8;">ไฟกระพริบ REC และมิเตอร์เสียง</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoWebcamRec">🔴 สลับไฟสถานะ REC</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoWebcamAudio">🎙️ ทดสอบมิเตอร์เสียงสด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'goal') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎯 ทดสอบยอดเป้าหมาย</span>
            <span style="font-size:11px; color:#94a3b8;">หลอดเพิ่มแบบอนิเมชัน</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalPlus">🎉 จำลองผู้ติดตามใหม่ (+50)</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalReset">🔄 รีเซ็ตยอด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'viewer') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">👥 ทดสอบตัวนับยอดผู้ชมสด</span>
            <span style="font-size:11px; color:#94a3b8;">อนิเมชันตัวเลขหมุนนุ่มนวล</span>
          </div>
          <div class="comp-demo-actions" style="display:flex; gap:6px;">
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerRandom" style="flex:1;">🎲 สุ่มยอดคนดู</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerAdd" style="flex:1;">📈 เพิ่ม +50 คน</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerSub" style="flex:1;">📉 ลด -30 คน</button>
          </div>
        </div>
      `;
    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ชื่อของรางวัล</span>
              <input type="text" class="cwc-input" id="compGiveawayPrize" value="${w.prizeTitle || 'รางวัลพิเศษประจำสตรีม'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;

    } else if (w.type === 'emote_party') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎉 ทดสอบปาร์ตี้อีโมทสด</span>
            <span style="font-size:11px; color:#94a3b8;">พุ่งลอยบนจอสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoEmoteParty">🎉 ปล่อยอีโมททดสอบ</button>
          </div>
        </div>
      `;
    } else if (w.type === 'now_playing') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎵 ทดสอบเพลงที่กำลังเล่น</span>
            <span style="font-size:11px; color:#94a3b8;">เปลี่ยนเพลงสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoNowPlayingNext">🎵 จำลองเพลงถัดไป</button>
          </div>
        </div>
      `;
    }

    // ==========================================
    // 1. CHAT WIDGET CUSTOMIZER (INTEGRATED FULL CHAT WIDGET CUSTOMIZER ACCORDIONS)
    // ==========================================
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';

      // Helper function for full categorized accordion sections
      function renderFullChatAccordionSections(w) {
        const fonts = [
          'Kanit',
          'Noto Sans Thai Looped',
          'Sarabun',
          'Prompt',
          'Mitr',
          'Chonburi',
          'Mali',
          'Bai Jamjuree',
          'Krub',
          'Taviraj',
          'Pattaya',
          'Itim',
          'Pridi',
          'Athiti',
          'Chakra Petch',
          'Kavivanar',
          'Charmonman',
          'Sriracha',
          'KoHo',
          'Fahkwang',
          'Roboto',
          'Inter',
          'Outfit',
          'Fredoka',
          'Bebas Neue',
          'Montserrat',
          'Poppins',
          'Open Sans',
          'Press Start 2P'
        ];

        let fontOpts = fonts.map(f => `<option value="${f}" ${(w.fontFamily || 'Kanit') === f ? 'selected' : ''}>${f}</option>`).join('');

        return `
          <!-- SECTION 1: LAYOUT & STRUCTURE -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">📐 การจัดวาง & สไตล์โครงสร้าง</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">รูปแบบการจัดวาง:</span>
                <select class="cwc-select" id="cwcLayout">
                  <option value="compact" ${(w.layout || 'compact') === 'compact' ? 'selected' : ''}>ข้อความกระชับติดกัน</option>
                  <option value="bubble" ${w.layout === 'bubble' ? 'selected' : ''}>บอลลูนแยกกล่องชัดเจน</option>
                  <option value="inline" ${w.layout === 'inline' ? 'selected' : ''}>ชื่อและข้อความบรรทัดเดียว</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ทิศทางข้อความ:</span>
                <select class="cwc-select" id="cwcDirection">
                  <option value="bottom-up" ${(w.direction || 'bottom-up') === 'bottom-up' ? 'selected' : ''}>ข้อความใหม่ดันจากล่างขึ้นบน</option>
                  <option value="top-down" ${w.direction === 'top-down' ? 'selected' : ''}>ข้อความใหม่ไหลจากบนลงล่าง</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">จัดตำแหน่งชิด:</span>
                <select class="cwc-select" id="cwcAlign">
                  <option value="left" ${(w.align || 'left') === 'left' ? 'selected' : ''}>ชิดซ้าย</option>
                  <option value="center" ${w.align === 'center' ? 'selected' : ''}>กึ่งกลาง</option>
                  <option value="right" ${w.align === 'right' ? 'selected' : ''}>ชิดขวา</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ระยะห่างระหว่างข้อความ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcMsgSpacing" min="2" max="24" step="1" value="${w.msgSpacing ?? 6}">
                  <span class="cwc-slider-val" id="cwcMsgSpacingVal">${w.msgSpacing ?? 6}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">จำนวนข้อความสูงสุด:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcMaxMessages" min="5" max="50" step="1" value="${w.maxMessages || 15}">
                  <span class="cwc-slider-val" id="cwcMaxMessagesVal">${w.maxMessages || 15}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 2: TYPOGRAPHY & FONT -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">✍️ ฟอนต์ & ขนาดตัวอักษร</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ตระกูลฟอนต์:</span>
                <select class="cwc-select" id="cwcFontFamily">
                  ${fontOpts}
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดตัวอักษร:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcFontSize" min="11" max="36" step="1" value="${w.fontSize || 15}">
                  <span class="cwc-slider-val" id="cwcFontSizeVal">${w.fontSize || 15}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความหนาตัวอักษร:</span>
                <select class="cwc-select" id="cwcFontWeight">
                  <option value="300" ${w.fontWeight === '300' ? 'selected' : ''}>300 บางเบา</option>
                  <option value="400" ${(w.fontWeight || '500') === '400' ? 'selected' : ''}>400 ปกติ</option>
                  <option value="500" ${(w.fontWeight || '500') === '500' ? 'selected' : ''}>500 ปานกลาง</option>
                  <option value="600" ${w.fontWeight === '600' ? 'selected' : ''}>600 หนาแน่น</option>
                  <option value="700" ${w.fontWeight === '700' ? 'selected' : ''}>700 หนาพิเศษ</option>
                  <option value="900" ${w.fontWeight === '900' ? 'selected' : ''}>900 หนาที่สุด</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีชื่อผู้ส่ง:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcUsernameColor" value="${w.usernameColor || '#38bdf8'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีข้อความแชท:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcMessageColor" value="${w.fontColor || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เส้นขอบตัวอักษร:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcTextStroke" ${w.textStroke ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcTextStrokeWidthRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">ความหนาขอบตัวอักษร:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcTextStrokeWidth" min="1" max="5" step="0.5" value="${w.textStrokeWidth || 1.5}">
                  <span class="cwc-slider-val" id="cwcTextStrokeWidthVal">${w.textStrokeWidth || 1.5}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcTextStrokeColorRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">สีขอบตัวอักษร:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcTextStrokeColor" value="${w.strokeColor || '#000000'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เงาตัวอักษร:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcTextShadow" ${w.textShadow !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcTextShadowBlurRow" style="display:${w.textShadow !== false ? 'flex' : 'none'};">
                <span class="cwc-label">ระยะเบลอเงา:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcTextShadowBlur" min="0" max="12" step="1" value="${w.textShadowBlur ?? 3}">
                  <span class="cwc-slider-val" id="cwcTextShadowBlurVal">${w.textShadowBlur ?? 3}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcTextShadowColorRow" style="display:${w.textShadow !== false ? 'flex' : 'none'};">
                <span class="cwc-label">สีเงาตัวอักษร:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcTextShadowColor" value="${w.textShadowColor || '#000000'}">
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 3: MESSAGE BOX & BUBBLE (กล่องข้อความแต่ละอัน) -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">💬 กล่องข้อความ & บับเบิล</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">เปิดใช้งานกล่องข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxEnabled" ${w.boxEnabled !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความกว้างกล่อง:</span>
                <select class="cwc-select" id="cwcBoxWidth">
                  <option value="fit" ${(w.boxWidth || 'fit') === 'fit' ? 'selected' : ''}>พอดีเนื้อหาข้อความ</option>
                  <option value="full" ${w.boxWidth === 'full' ? 'selected' : ''}>เต็มความกว้างแถว</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีพื้นหลังกล่องข้อความ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBgColor" value="${w.bgColor || '#1e1f22'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความโปร่งใสกล่องข้อความ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBgOpacity" min="0" max="100" step="5" value="${Math.round((w.bgOpacity ?? 0.85) * 100)}">
                  <span class="cwc-slider-val" id="cwcBgOpacityVal">${Math.round((w.bgOpacity ?? 0.85) * 100)}%</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความโค้งมนมุมกล่อง:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBoxRadius" min="0" max="28" step="1" value="${w.boxRadius ?? 8}">
                  <span class="cwc-slider-val" id="cwcBoxRadiusVal">${w.boxRadius ?? 8}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ระยะขอบภายใน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBoxPadding" min="4" max="24" step="1" value="${w.boxPadding || 10}">
                  <span class="cwc-slider-val" id="cwcBoxPaddingVal">${w.boxPadding || 10}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เส้นขอบกล่องข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxBorder" ${w.boxBorder ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcBoxBorderWidthRow" style="display:${w.boxBorder ? 'flex' : 'none'};">
                <span class="cwc-label">ความหนาเส้นขอบ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBoxBorderWidth" min="1" max="6" step="1" value="${w.boxBorderWidth || 1}">
                  <span class="cwc-slider-val" id="cwcBoxBorderWidthVal">${w.boxBorderWidth || 1}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcBoxBorderColorRow" style="display:${w.boxBorder ? 'flex' : 'none'};">
                <span class="cwc-label">สีเส้นขอบ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBoxBorderColor" value="${w.boxBorderColor || '#38bdf8'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เงากล่องข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxShadow" ${w.boxShadow !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เรืองแสงนีออนรอบกล่อง:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcBoxGlow" ${w.boxGlow ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcBoxGlowColorRow" style="display:${w.boxGlow ? 'flex' : 'none'};">
                <span class="cwc-label">สีเรืองแสง:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBoxGlowColor" value="${w.boxGlowColor || '#38bdf8'}">
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION: CHAT CONTAINER BOX (กล่องพื้นหลังรวมของแชท) -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">🖼 กล่องพื้นหลังแชท (Container Box)</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">เปิดใช้งานกล่องพื้นหลัง:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compChatContainerBgEnabled" ${w.containerBgEnabled ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div id="compChatContainerSettingsWrap" style="display:${w.containerBgEnabled ? 'block' : 'none'};">
                <div class="cwc-row">
                  <span class="cwc-label">สีพื้นหลังกล่อง:</span>
                  <div class="cwc-color-wrap">
                    <input type="color" class="cwc-color-pick" id="compChatContainerBgColor" value="${w.containerBgColor || '#0a0e1a'}">
                  </div>
                </div>
                <div class="cwc-row">
                  <span class="cwc-label">ความโปร่งใสกล่อง:</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatContainerBgOpacity" min="0" max="100" step="5" value="${Math.round(((w.containerBgOpacity !== undefined) ? w.containerBgOpacity : 0.75) * 100)}">
                    <span class="cwc-slider-val" id="compChatContainerBgOpacityVal">${Math.round(((w.containerBgOpacity !== undefined) ? w.containerBgOpacity : 0.75) * 100)}%</span>
                  </div>
                </div>
                <div class="cwc-row">
                  <span class="cwc-label">ความโค้งมนของกล่อง:</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatContainerRadius" min="0" max="32" step="1" value="${(w.containerRadius !== undefined) ? w.containerRadius : 8}">
                    <span class="cwc-slider-val" id="compChatContainerRadiusVal">${(w.containerRadius !== undefined) ? w.containerRadius : 8}px</span>
                  </div>
                </div>
                <div class="cwc-row">
                  <span class="cwc-label">เส้นขอบกล่อง:</span>
                  <label class="cwc-switch">
                    <input type="checkbox" id="compChatContainerBorder" ${w.containerBorder ? 'checked' : ''}>
                    <span class="cwc-switch-slider"></span>
                  </label>
                </div>
                <div class="cwc-row" id="compChatContainerBorderWidthRow" style="display:${w.containerBorder ? 'flex' : 'none'};">
                  <span class="cwc-label">ความหนาขอบกล่อง:</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatContainerBorderWidth" min="1" max="6" step="1" value="${w.containerBorderWidth || 1}">
                    <span class="cwc-slider-val" id="compChatContainerBorderWidthVal">${w.containerBorderWidth || 1}px</span>
                  </div>
                </div>
                <div class="cwc-row" id="compChatContainerBorderColorRow" style="display:${w.containerBorder ? 'flex' : 'none'};">
                  <span class="cwc-label">สีเส้นขอบกล่อง:</span>
                  <div class="cwc-color-wrap">
                    <input type="color" class="cwc-color-pick" id="compChatContainerBorderColor" value="${w.containerBorderColor || '#38bdf8'}">
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 4: ANIMATIONS & AUTO-HIDE -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">✨ แอนิเมชัน & ซ่อนข้อความ</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">แอนิเมชันขาเข้า (Anim In):</span>
                <select class="cwc-select" id="compChatAnimIn">
                  <option value="slide" ${(w.animation || w.animIn || 'slide') === 'slide' ? 'selected' : ''}>เลื่อนเข้า (Slide)</option>
                  <option value="fade" ${(w.animation || w.animIn) === 'fade' ? 'selected' : ''}>ค่อยๆ ปรากฏ (Fade)</option>
                  <option value="pop" ${(w.animation || w.animIn) === 'pop' ? 'selected' : ''}>เด้งขยาย (Pop)</option>
                  <option value="bounce" ${(w.animation || w.animIn) === 'bounce' ? 'selected' : ''}>กระเด้ง (Bounce)</option>
                  <option value="none" ${(w.animation || w.animIn) === 'none' ? 'selected' : ''}>ไม่มีแอนิเมชัน (None)</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">แอนิเมชันขาออก (Anim Out):</span>
                <select class="cwc-select" id="compChatAnimOut">
                  <option value="auto" ${(w.exitAnimation || w.animOut || 'auto') === 'auto' ? 'selected' : ''}>ตามขาเข้า (Auto)</option>
                  <option value="fade" ${(w.exitAnimation || w.animOut) === 'fade' ? 'selected' : ''}>ค่อยๆ จางหาย (Fade)</option>
                  <option value="slide-left" ${(w.exitAnimation || w.animOut) === 'slide-left' ? 'selected' : ''}>เลื่อนออกซ้าย (Slide Left)</option>
                  <option value="slide-right" ${(w.exitAnimation || w.animOut) === 'slide-right' ? 'selected' : ''}>เลื่อนออกขวา (Slide Right)</option>
                  <option value="slide-up" ${(w.exitAnimation || w.animOut) === 'slide-up' ? 'selected' : ''}>เลื่อนขึ้นบน (Slide Up)</option>
                  <option value="slide-down" ${(w.exitAnimation || w.animOut) === 'slide-down' ? 'selected' : ''}>เลื่อนลงล่าง (Slide Down)</option>
                  <option value="none" ${(w.exitAnimation || w.animOut) === 'none' ? 'selected' : ''}>หายทันที (None)</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ซ่อนข้อความอัตโนมัติ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compChatAutoHide" ${w.autoHide ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="compChatHideAfterRow" style="display:${w.autoHide ? 'flex' : 'none'};">
                <span class="cwc-label">ระยะเวลาก่อนซ่อนข้อความ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatHideAfter" min="2" max="60" step="1" value="${w.hideAfter || 8}">
                  <span class="cwc-slider-val" id="compChatHideAfterVal">${w.hideAfter || 8} วินาที</span>
                </div>
              </div>
            </div>
          </div>
        `;
      }

      if (mode === 'danmaku') {
        specificHtml = `
          <!-- DANMAKU CONTROLS -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">⚡ ตั้งค่ากระสุนดันมากุ</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ความเร็วการวิ่ง:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderDuration" min="3" max="15" step="0.5" value="${w.speed || 6}">
                  <span class="cwc-slider-val" id="cwcSliderDurationVal">${w.speed || 6}s</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความสูงแต่ละเลน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderLaneHeight" min="25" max="70" step="1" value="${w.laneHeight || 40}">
                  <span class="cwc-slider-val" id="cwcSliderLaneHeightVal">${w.laneHeight || 40}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ตำแหน่งการแสดงผล:</span>
                <select class="cwc-select" id="cwcSliderZone">
                  <option value="all" ${(w.slider_zone || 'middle') === 'all' ? 'selected' : ''}>เต็มหน้าจอ</option>
                  <option value="top" ${w.slider_zone === 'top' ? 'selected' : ''}>ครึ่งบน</option>
                  <option value="middle" ${(w.slider_zone || 'middle') === 'middle' ? 'selected' : ''}>ตรงกลาง</option>
                  <option value="bottom" ${w.slider_zone === 'bottom' ? 'selected' : ''}>ครึ่งล่าง</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดฟอนต์ดันมากุ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderFontSize" min="16" max="48" step="1" value="${w.fontSize || 24}">
                  <span class="cwc-slider-val" id="cwcSliderFontSizeVal">${w.fontSize || 24}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีตัวอักษรดันมากุ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcSliderTextColor" value="${w.fontColor || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เส้นขอบตัวอักษรดันมากุ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcSliderTextStroke" ${w.textStroke ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row" id="cwcSliderStrokeWidthRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">ความหนาเส้นขอบ:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcSliderStrokeWidth" min="1" max="6" step="1" value="${w.textStrokeWidth || 2}">
                  <span class="cwc-slider-val" id="cwcSliderStrokeWidthVal">${w.textStrokeWidth || 2}px</span>
                </div>
              </div>
              <div class="cwc-row" id="cwcSliderStrokeColorRow" style="display:${w.textStroke ? 'flex' : 'none'};">
                <span class="cwc-label">สีเส้นขอบ:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcSliderStrokeColor" value="${w.strokeColor || '#000000'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">เงาตัวอักษรดันมากุ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcSliderTextShadow" ${w.textShadow !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">แสดงโลโก้ข้างข้อความ:</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="cwcSliderShowLogo" ${w.showLogo !== false ? 'checked' : ''}>
                  <span class="cwc-switch-slider"></span>
                </label>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        specificHtml = `
          <!-- BALLOON CONTROLS -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">💬 ตั้งค่าบอลลูนคำพูด</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ความโปร่งใสบอลลูน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBalloonOpacity" min="10" max="100" step="5" value="${Math.round((w.balloonOpacity ?? 0.95) * 100)}">
                  <span class="cwc-slider-val" id="cwcBalloonOpacityVal">${Math.round((w.balloonOpacity ?? 0.95) * 100)}%</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดฟอนต์บอลลูน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBalloonFontSize" min="14" max="36" step="1" value="${w.fontSize || 15}">
                  <span class="cwc-slider-val" id="cwcBalloonFontSizeVal">${w.fontSize || 15}px</span>
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีตัวอักษรบอลลูน:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBalloonTextColor" value="${w.balloonTextColor || '#0f172a'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีพื้นหลังบอลลูน:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcBalloonBg" value="${w.balloonBg || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ความโค้งมนมุมบอลลูน:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcBalloonRadius" min="6" max="32" step="1" value="${w.balloonRadius ?? 14}">
                  <span class="cwc-slider-val" id="cwcBalloonRadiusVal">${w.balloonRadius ?? 14}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        specificHtml = `
          <!-- CHARACTER TALK CONTROLS -->
          <div class="cwc-section">
            <div class="cwc-section-header">
              <span class="cwc-section-title">🎭 ตั้งค่าตัวละครพูด</span>
              <span class="cwc-section-toggle">▼</span>
            </div>
            <div class="cwc-section-body">
              <div class="cwc-row">
                <span class="cwc-label">ชื่อตัวละคร:</span>
                <input type="text" class="cwc-input-text" id="cwcCharName" value="${w.characterName || 'Replie'}" style="flex:1; padding:6px 10px; font-size:12px; background:#111215; border:1px solid rgba(255,255,255,0.12); border-radius:6px; color:#ffffff;">
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ตำแหน่งตัวละคร:</span>
                <select class="cwc-select" id="cwcCharAlign">
                  <option value="left" ${(w.charAlign || 'left') === 'left' ? 'selected' : ''}>ตัวละครอยู่ฝั่งซ้าย</option>
                  <option value="right" ${(w.charAlign || 'left') === 'right' ? 'selected' : ''}>ตัวละครอยู่ฝั่งขวา</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">รูปภาพตัวละคร:</span>
                <select class="cwc-select" id="cwcCharAvatar">
                  <option value="./assets/dock_offline_character.png" ${(w.imageUrl || '').includes('dock_offline_character') ? 'selected' : ''}>Replie คลาสสิก</option>
                  <option value="./assets/character_cheer.png" ${(w.imageUrl || '').includes('character_cheer') ? 'selected' : ''}>Replie เชียร์สดใส</option>
                  <option value="./assets/character_game.png" ${(w.imageUrl || '').includes('character_game') ? 'selected' : ''}>Replie เล่นเกม</option>
                </select>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีพื้นหลังกล่องพูด:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcCharBubbleBg" value="${w.charBubbleBg || '#ffffff'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">สีตัวอักษร:</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="cwcCharTextColor" value="${w.charTextColor || '#0f172a'}">
                </div>
              </div>
              <div class="cwc-row">
                <span class="cwc-label">ขนาดตัวอักษร:</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="cwcCharFontSize" min="12" max="28" step="1" value="${w.charFontSize || 15}">
                  <span class="cwc-slider-val" id="cwcCharFontSizeVal">${w.charFontSize || 15}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else {
        // Mode: Default (Standard & Theme modes)
        const currentSubTab = state.chatSubTab || 'standard';
        specificHtml = `
          <div class="cwc-mode-segmented-bar">
            <button type="button" class="cwc-mode-tab-btn ${currentSubTab === 'standard' ? 'active' : ''}" id="tabSubStandard">⚙️ Default</button>
            <button type="button" class="cwc-mode-tab-btn ${currentSubTab === 'theme' ? 'active' : ''}" id="tabSubTheme">🎨 Theme</button>
          </div>
        `;

        if (currentSubTab === 'standard') {
          specificHtml += renderFullChatAccordionSections(w);
        } else {
          // 80 Themes Grid with Pagination
          const allThemes = window.CWC_ALL_THEMES || [];
          const pageNum = state.chatThemePage || 1;
          const pageSize = 8;
          const totalPages = Math.ceil(allThemes.length / pageSize) || 10;
          const startIdx = (pageNum - 1) * pageSize;
          const currentThemes = allThemes.slice(startIdx, startIdx + pageSize);

          let themeCardsHtml = '';
          currentThemes.forEach(t => {
            const themeId = t.id || t.key;
            const isSel = (w.chatTheme || 'default') === themeId;
            themeCardsHtml += `
              <div class="cwc-preset-card ${isSel ? 'active' : ''}" data-chat-theme="${themeId}" style="border:1.5px solid ${isSel ? '#38bdf8' : 'rgba(255,255,255,0.1)'}; border-radius:8px; padding:8px 10px; cursor:pointer; background:${isSel ? 'rgba(56,189,248,0.12)' : 'rgba(255,255,255,0.03)'}; transition:all 0.15s ease;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                  <span style="font-weight:700; font-size:12px; color:${isSel ? '#38bdf8' : '#ffffff'};">${t.name}</span>
                  <span style="font-size:10px; background:rgba(255,255,255,0.08); padding:1px 6px; border-radius:4px; color:#94a3b8;">${t.category || 'สไตล์'}</span>
                </div>
                <div style="font-size:11px; color:#cbd5e1; line-height:1.3; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${t.desc || ''}</div>
              </div>
            `;
          });

          specificHtml += `
            <div class="cwc-section">
              <div class="cwc-section-header">
                <span class="cwc-section-title">🎨 รูปแบบธีมสำเร็จรูป (80 ธีม)</span>
                <span class="cwc-section-toggle">▼</span>
              </div>
              <div class="cwc-section-body">
                <div class="cwc-presets-grid" id="cwcPresetsGrid" style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                  ${themeCardsHtml}
                </div>
                <div class="cwc-pagination" style="display:flex; justify-content:space-between; align-items:center; padding:8px 10px; background:rgba(0,0,0,0.3); border-radius:6px; margin-top:8px;">
                  <button type="button" class="cwc-page-btn" id="compBtnThemePrev" style="padding:5px 12px; font-size:12px; font-weight:600; background:#22252a; border:1px solid rgba(255,255,255,0.15); border-radius:4px; color:#ffffff; cursor:pointer;" ${pageNum <= 1 ? 'disabled style="opacity:0.4; cursor:not-allowed;"' : ''}>◀ ก่อนหน้า</button>
                  <span class="cwc-page-indicator" id="compThemePageIndicator" style="font-size:12px; font-weight:700; color:#38bdf8;">หน้า ${pageNum} / ${totalPages}</span>
                  <button type="button" class="cwc-page-btn" id="compBtnThemeNext" style="padding:5px 12px; font-size:12px; font-weight:600; background:#22252a; border:1px solid rgba(255,255,255,0.15); border-radius:4px; color:#ffffff; cursor:pointer;" ${pageNum >= totalPages ? 'disabled style="opacity:0.4; cursor:not-allowed;"' : ''}>ถัดไป ▶</button>
                </div>
              </div>
            </div>
          `;

          // Also include the full 4 accordion sections below theme grid so user can fine-tune!
          specificHtml += renderFullChatAccordionSections(w);
        }
      }
    }
    else if (w.type === 'clock') {
      const clockMode = w.clockMode || (w.clockStyle && w.clockStyle !== 'none' ? 'style' : 'theme');
      const curTheme = w.clockTheme || w.clock_theme || 'default';
      const curStyle = w.clockStyle || w.clock_style || 'dot1';
      const curFormat = w.clockFormat || w.clock_format || 'HH:MM';
      const themeOp = Math.round((w.themeOpacity ?? w.theme_opacity ?? 1.0) * 100);
      const styleOp = Math.round((w.styleOpacity ?? w.style_opacity ?? 1.0) * 100);

      const clockThemesList = [
        { id: 'default', name: 'Default (ขาวมาตรฐาน)' },
        { id: 'neon', name: 'Neon (นีออนฟ้า-น้ำเงิน)' },
        { id: 'cyberpunk', name: 'Cyberpunk (ชมพู-เขียว)' },
        { id: 'digital', name: 'Digital (เขียวเทอมินอล)' },
        { id: 'digital-red', name: 'Digital Red (แดงดิจิทัล)' },
        { id: 'digital-amber', name: 'Digital Amber (เหลืองดิจิทัล)' },
        { id: 'glass', name: 'Glass (กระจกฝ้า)' },
        { id: 'sakura', name: 'Sakura (ชมพูซากุระ)' },
        { id: 'gold', name: 'Gold (ทองหรูหรา)' },
        { id: 'retro', name: 'Retro (เรโทรคลาสสิก)' },
        { id: 'pipboy', name: 'Pip-Boy (เขียว Fallout)' },
        { id: 'minimal', name: 'Minimal (เรียบหรู)' },
        { id: 'outline', name: 'Outline (โปร่งใสขอบขาว)' },
        { id: 'shadow', name: 'Shadow (เงาดำเข้ม)' },
        { id: 'matrix', name: 'Matrix (เขียวเมทริกซ์)' },
        { id: 'vaporwave', name: 'Vaporwave (ชมพู-ฟ้า)' },
        { id: 'fire', name: 'Fire (ส้ม-แดงไฟ)' },
        { id: 'ice', name: 'Ice (ฟ้าเยือกแข็ง)' },
        { id: 'royal', name: 'Royal (ทอง-น้ำเงินเข้ม)' },
        { id: 'sunset', name: 'Sunset (ส้ม-ชมพู)' },
        { id: 'hologram', name: 'Hologram (ฟ้า-ชมพูโฮโลแกรม)' },
        { id: 'led', name: 'LED (แดง)' },
        { id: 'led-green', name: 'LED Green (เขียว)' },
        { id: 'led-blue', name: 'LED Blue (ฟ้า)' },
        { id: 'aqua', name: 'Aqua (ฟ้าน้ำทะเล)' },
        { id: 'coral', name: 'Coral (ส้มปะการัง)' },
        { id: 'mint', name: 'Mint (เขียวมิ้นต์)' },
        { id: 'lavender', name: 'Lavender (ม่วงลาเวนเดอร์)' },
        { id: 'bronze', name: 'Bronze (บรอนซ์)' },
        { id: 'platinum', name: 'Platinum (แพลตตินัม)' },
        { id: 'neon-purple', name: 'Neon Purple (ม่วงนีออน)' },
        { id: 'pixel-rpg', name: 'Pixel RPG (พิกเซลย้อนยุค)' }
      ];

      specificHtml = `
        <div class="cwc-mode-segmented-bar" style="margin-bottom:12px;">
          <button type="button" class="cwc-mode-tab-btn ${clockMode === 'theme' ? 'active' : ''}" id="tabClockTheme">🎨 Theme (32 ธีม)</button>
          <button type="button" class="cwc-mode-tab-btn ${clockMode === 'style' ? 'active' : ''}" id="tabClockStyle">⚙ Style (สไตล์พิเศษ)</button>
        </div>

        <!-- THEME SECTION -->
        <div id="compClockThemeSection" style="${clockMode === 'theme' ? 'display:block;' : 'display:none;'}">
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">🎨 รูปแบบธีมสำเร็จรูป (32 ธีม)</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">เลือกธีม</span>
                <select class="cwc-select" id="compClockTheme">
                  ${clockThemesList.map(t => `<option value="${t.id}" ${curTheme === t.id ? 'selected' : ''}>${t.name}</option>`).join('')}
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">รูปแบบเวลา</span>
                <select class="cwc-select" id="compClockFormat">
                  <option value="HH:MM" ${curFormat === 'HH:MM' ? 'selected' : ''}>HH:MM (เช่น 19:30)</option>
                  <option value="HH:MM:SS" ${curFormat === 'HH:MM:SS' ? 'selected' : ''}>HH:MM:SS (เช่น 19:30:45)</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาด Font เวลา</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockFontSize" min="14" max="96" value="${w.fontSize || 28}">
                  <span class="cwc-slider-val" id="compClockFontSizeVal">${w.fontSize || 28}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวเลขอักษรเวลา</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="compClockTimeColor" value="${w.timeColor || '#ffffff'}">
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งใส Opacity</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockThemeOpacity" min="10" max="100" value="${themeOp}">
                  <span class="cwc-slider-val" id="compClockThemeOpacityVal">${themeOp}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- DATE SETTINGS -->
          <div class="comp-card-section" style="margin-top:10px;">
            <div class="comp-card-header"><span class="comp-card-title">📅 การตั้งค่าวันที่</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">เปิดแสดงวันที่</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compClockShowDate" ${w.showDate ? 'checked' : ''}>
                  <span class="cwc-slider-round"></span>
                </label>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ภาษาแสดงวันที่</span>
                <select class="cwc-select" id="compClockDateLang">
                  <option value="th" ${(w.dateLang || 'th') === 'th' ? 'selected' : ''}>ภาษาไทย (3 ส.ค. 69)</option>
                  <option value="en" ${(w.dateLang || 'th') === 'en' ? 'selected' : ''}>English (3 Aug 2026)</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">รูปแบบวันที่</span>
                <select class="cwc-select" id="compClockDateFormat">
                  <option value="short" ${(w.dateFormat || 'short') === 'short' ? 'selected' : ''}>แบบสั้น (3 ส.ค. 69 / 3 Aug 26)</option>
                  <option value="long" ${(w.dateFormat || 'short') === 'long' ? 'selected' : ''}>แบบยาว (วันจันทร์ 3 สิงหาคม 2569)</option>
                  <option value="iso" ${(w.dateFormat || 'short') === 'iso' ? 'selected' : ''}>ISO (2026-08-03)</option>
                  <option value="weekday" ${(w.dateFormat || 'short') === 'weekday' ? 'selected' : ''}>วัน + วันที่ (จ. 3 ส.ค. 69)</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาด Font วันที่</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockDateFontSize" min="10" max="48" value="${w.dateFontSize || 14}">
                  <span class="cwc-slider-val" id="compClockDateFontSizeVal">${w.dateFontSize || 14}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษรวันที่</span>
                <div class="cwc-color-wrap">
                  <input type="color" class="cwc-color-pick" id="compClockDateColor" value="${w.dateColor || '#cccccc'}">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- STYLE SECTION -->
        <div id="compClockStyleSection" style="${clockMode === 'style' ? 'display:block;' : 'display:none;'}">
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">⚙ สไตล์พิเศษจาก Version 2</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">เลือก Style</span>
                <select class="cwc-select" id="compClockStyle">
                  <optgroup label="⏱ Dot Clock (ตัวเลข + จุดนับวินาที)">
                    <option value="dot1" ${curStyle === 'dot1' ? 'selected' : ''}>Dot 1 — HH:MM + ◯</option>
                    <option value="dot2" ${curStyle === 'dot2' ? 'selected' : ''}>Dot 2 — YYYY.MM.DD HH:MM + ◯</option>
                    <option value="dot3" ${curStyle === 'dot3' ? 'selected' : ''}>Dot 3 — DD.MM.YYYY HH:MM + ◎</option>
                  </optgroup>
                  <optgroup label="⭕ Circle Clock (วงแหวนเรืองแสงหมุนตามวินาที)">
                    <option value="cc1" ${curStyle === 'cc1' ? 'selected' : ''}>Circle Normal — ดำ/แดง</option>
                    <option value="cc2" ${curStyle === 'cc2' ? 'selected' : ''}>Circle Normal — ฟ้า/เหลือง</option>
                    <option value="cc3" ${curStyle === 'cc3' ? 'selected' : ''}>Circle Normal — เขียว</option>
                    <option value="cc4" ${curStyle === 'cc4' ? 'selected' : ''}>Circle Normal — ส้ม/ชมพู</option>
                    <option value="cc5" ${curStyle === 'cc5' ? 'selected' : ''}>Circle Normal — ม่วง/ฟ้า</option>
                    <option value="ccdate1" ${curStyle === 'ccdate1' ? 'selected' : ''}>Circle + Date — ดำ/แดง</option>
                    <option value="ccdate2" ${curStyle === 'ccdate2' ? 'selected' : ''}>Circle + Date — ฟ้า/เหลือง</option>
                    <option value="ccdate3" ${curStyle === 'ccdate3' ? 'selected' : ''}>Circle + Date — เขียว</option>
                    <option value="ccdate4" ${curStyle === 'ccdate4' ? 'selected' : ''}>Circle + Date — ส้ม/ชมพู</option>
                    <option value="ccdate5" ${curStyle === 'ccdate5' ? 'selected' : ''}>Circle + Date — ม่วง/ฟ้า</option>
                    <option value="cclive1" ${curStyle === 'cclive1' ? 'selected' : ''}>Circle + LIVE — ดำ/แดง</option>
                    <option value="cclive2" ${curStyle === 'cclive2' ? 'selected' : ''}>Circle + LIVE — ฟ้า/เหลือง</option>
                    <option value="cclive3" ${curStyle === 'cclive3' ? 'selected' : ''}>Circle + LIVE — เขียว</option>
                    <option value="cclive4" ${curStyle === 'cclive4' ? 'selected' : ''}>Circle + LIVE — ส้ม/ชมพู</option>
                    <option value="cclive5" ${curStyle === 'cclive5' ? 'selected' : ''}>Circle + LIVE — ม่วง/ฟ้า</option>
                    <option value="ccsec1" ${curStyle === 'ccsec1' ? 'selected' : ''}>Circle + Seconds — ดำ/แดง</option>
                    <option value="ccsec2" ${curStyle === 'ccsec2' ? 'selected' : ''}>Circle + Seconds — ฟ้า/เหลือง</option>
                    <option value="ccsec3" ${curStyle === 'ccsec3' ? 'selected' : ''}>Circle + Seconds — เขียว</option>
                    <option value="ccsec4" ${curStyle === 'ccsec4' ? 'selected' : ''}>Circle + Seconds — ส้ม/ชมพู</option>
                    <option value="ccsec5" ${curStyle === 'ccsec5' ? 'selected' : ''}>Circle + Seconds — ม่วง/ฟ้า</option>
                  </optgroup>
                  <optgroup label="⚡ Clock with Live Text">
                    <option value="lt1" ${curStyle === 'lt1' ? 'selected' : ''}>Live Text 1 — LIVE + เวลา + วันที่</option>
                    <option value="lt2" ${curStyle === 'lt2' ? 'selected' : ''}>Live Text 2 — เวลา + วันที่</option>
                    <option value="lt3" ${curStyle === 'lt3' ? 'selected' : ''}>Live Text 3 — เวลา (ตรงกลาง)</option>
                    <option value="lt4" ${curStyle === 'lt4' ? 'selected' : ''}>Live Text 4 — เวลา + วินาที</option>
                    <option value="lt5" ${curStyle === 'lt5' ? 'selected' : ''}>Live Text 5 — เวลา + LIVE สายฟ้า</option>
                  </optgroup>
                  <optgroup label="🎮 FPS Clock (กรอบเรขาคณิตเกมมิ่ง)">
                    <option value="fps2" ${curStyle === 'fps2' ? 'selected' : ''}>FPS 2 — หกเหลี่ยม Hexagon</option>
                    <option value="fps3" ${curStyle === 'fps3' ? 'selected' : ''}>FPS 3 — สี่เหลี่ยมตัดมุม</option>
                    <option value="fps4" ${curStyle === 'fps4' ? 'selected' : ''}>FPS 4 — แปดเหลี่ยม Octagon</option>
                  </optgroup>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งใส Opacity</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compClockStyleOpacity" min="10" max="100" value="${styleOp}">
                  <span class="cwc-slider-val" id="compClockStyleOpacityVal">${styleOp}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      const isTicker = (w.textMode || 'ticker') === 'ticker';
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ข้อความและรูปแบบ</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ข้อความประกาศ</span>
              <textarea class="cwc-input" id="compTextInput" rows="2" style="width:100%; resize:vertical;">${w.text || ''}</textarea>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดแสดงผล</span>
              <select class="cwc-select" id="compTextMode">
                <option value="ticker" ${w.textMode === 'ticker' ? 'selected' : ''}>ตัววิ่ง Marquee สด</option>
                <option value="static" ${w.textMode !== 'ticker' ? 'selected' : ''}>ข้อความนิ่ง</option>
              </select>
            </div>
            <div class="comp-field-row" id="compTextSpeedRow" style="display:${w.textMode === 'ticker' ? 'flex' : 'none'};">
              <span class="cwc-label">ความเร็วตัววิ่ง (วินาทีต่อรอบ):</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextSpeed" min="5" max="60" value="${w.marqueeSpeed || 15}">
                <span class="cwc-slider-val" id="compTextSpeedVal">${w.marqueeSpeed || 15} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="64" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compTextFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ตำแหน่งแนวตั้ง</span>
              <div style="display:flex; gap:6px;">
                <button type="button" class="composer-btn-sub ${w.vAlign === 'top' ? 'active' : ''}" id="btnTextVAlignTop">⬆️ บน</button>
                <button type="button" class="composer-btn-sub ${(!w.vAlign || w.vAlign === 'center') ? 'active' : ''}" id="btnTextVAlignMid">↕️ กลาง</button>
                <button type="button" class="composer-btn-sub ${w.vAlign === 'bottom' ? 'active' : ''}" id="btnTextVAlignBot">⬇️ ล่าง</button>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compTextFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <input type="color" class="cwc-color-pick" id="compTextBgColor" value="${w.bgColor || '#141923'}" ${w.bgEnabled === false ? 'disabled style="opacity:0.4;"' : ''}>
                <button type="button" class="composer-btn-sub ${w.bgEnabled === false ? 'active' : ''}" id="btnTextToggleBg">
                  ${w.bgEnabled === false ? '🚫 ไม่ใช้พื้นหลัง (ใส)' : '🎨 เปิดใช้พื้นหลัง'}
                </button>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาเส้นขอบ (Stroke)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextStrokeWidth" min="0" max="10" value="${w.textStrokeWidth ?? 0}">
                <span class="cwc-slider-val" id="compTextStrokeWidthVal">${w.textStrokeWidth ?? 0}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compTextStrokeColor" value="${w.strokeColor || '#000000'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดเงา (Shadow Blur)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextShadowBlur" min="0" max="20" value="${w.textShadowBlur ?? 0}">
                <span class="cwc-slider-val" id="compTextShadowBlurVal">${w.textShadowBlur ?? 0}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเงา</span>
              <input type="color" class="cwc-color-pick" id="compTextShadowColor" value="${w.textShadowColor || '#000000'}">
            </div>
          </div>
        </div>
        <!-- การ์ด 3: ฟอนต์และสี -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ฟอนต์และสี</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์ชื่อเพลง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpFontSize" min="8" max="40" value="${w.npFontSize || 14}">
                <span class="cwc-slider-val" id="compNpFontSizeVal">${w.npFontSize || 14}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์ชื่อศิลปิน</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpArtistFontSize" min="8" max="32" value="${w.npArtistFontSize || 12}">
                <span class="cwc-slider-val" id="compNpArtistFontSizeVal">${w.npArtistFontSize || 12}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์เวลา</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpTimeFontSize" min="6" max="24" value="${w.npTimeFontSize || 10}">
                <span class="cwc-slider-val" id="compNpTimeFontSizeVal">${w.npTimeFontSize || 10}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีข้อความ</span>
              <input type="color" class="cwc-color-pick" id="compNpTextColor" value="${w.npTextColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีแถบเวลา Progress</span>
              <input type="color" class="cwc-color-pick" id="compNpAccentColor" value="${w.npAccentColor || '#1db954'}">
            </div>
          </div>
        </div>

        <!-- การ์ด 4: ตัวเลือกการแสดงผล -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">⚙️ ตัวเลือกการแสดงผล</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงภาพปกอัลบั้ม</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpShowArt" ${w.npShowArt !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงแถบความคืบหน้า</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpShowProgress" ${w.npShowProgress !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เลื่อนชื่อเพลงยาว</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpScrollTitle" ${w.npScrollTitle !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมด Sync เวลา</span>
              <select class="cwc-select" id="compNpSyncMode">
                <option value="browser" ${(w.npSyncMode || 'browser') === 'browser' ? 'selected' : ''}>ประหยัดทรัพยากร</option>
                <option value="precise" ${w.npSyncMode === 'precise' ? 'selected' : ''}>แม่นยำสูง</option>
              </select>
            </div>
          </div>
        </div>

        <!-- การ์ด 5: กรอบและพื้นหลัง -->
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📦 กรอบและพื้นหลัง</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">พื้นหลังโปร่งใส</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpTransparent" ${w.npTransparent ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row" id="compNpBgColorRow" style="display:${w.npTransparent ? 'none' : 'flex'};">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <input type="color" class="cwc-color-pick" id="compNpBgColor" value="${w.npBgColor || '#1a1a2e'}">
            </div>
            <div class="comp-field-row" id="compNpBgOpacityRow" style="display:${w.npTransparent ? 'none' : 'flex'};">
              <span class="comp-field-label">ความโปร่งใสพื้นหลัง</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpBgOpacity" min="0" max="100" step="5" value="${Math.round((w.npBgOpacity ?? 0.85) * 100)}">
                <span class="cwc-slider-val" id="compNpBgOpacityVal">${Math.round((w.npBgOpacity ?? 0.85) * 100)}%</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมุมกรอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpRadius" min="0" max="24" step="1" value="${w.npRadius ?? 8}">
                <span class="cwc-slider-val" id="compNpRadiusVal">${w.npRadius ?? 8}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมุมปก</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpArtRadius" min="0" max="24" step="1" value="${w.npArtRadius ?? 6}">
                <span class="cwc-slider-val" id="compNpArtRadiusVal">${w.npArtRadius ?? 6}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดภาพปก</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compNpArtSize" min="24" max="120" step="4" value="${w.npArtSize ?? 48}">
                <span class="cwc-slider-val" id="compNpArtSizeVal">${w.npArtSize ?? 48}px</span>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ชื่อของรางวัล</span>
              <input type="text" class="cwc-input" id="compGiveawayPrize" value="${w.prizeTitle || 'รางวัลพิเศษประจำสตรีม'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;

    } else if (w.type === 'emote_party') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎉 ตั้งค่าปาร์ตี้อีโมทลอย</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบอนิเมชัน</span>
              <select class="cwc-select" id="compEpAnimation">
                <option value="float" ${(w.epAnimation || 'float') === 'float' ? 'selected' : ''}>ลอยขึ้นนุ่มนวล</option>
                <option value="bounce" ${w.epAnimation === 'bounce' ? 'selected' : ''}>เด้งกระดอน</option>
                <option value="fountain" ${w.epAnimation === 'fountain' ? 'selected' : ''}>พวยพุ่งน้ำพุ</option>
                <option value="dvd" ${w.epAnimation === 'dvd' ? 'selected' : ''}>เด้งชนผนัง</option>
                <option value="drop" ${w.epAnimation === 'drop' ? 'selected' : ''}>ตกกระทบพื้น</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ระยะเวลาแสดงผล</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpDuration" min="1" max="10" value="${w.epDuration || 4}">
                <span class="cwc-slider-val" id="compEpDurationVal">${w.epDuration || 4} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">จำนวนสูงสุดบนจอ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpMaxEmotes" min="5" max="50" value="${w.epMaxEmotes || 15}">
                <span class="cwc-slider-val" id="compEpMaxEmotesVal">${w.epMaxEmotes || 15} ตัว</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดอีโมท</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpEmoteSize" min="24" max="96" value="${w.epEmoteSize || 48}">
                <span class="cwc-slider-val" id="compEpEmoteSizeVal">${w.epEmoteSize || 48}px</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    bodyEl.innerHTML = demoHtml + specificHtml;

    // Bind Demo Action Buttons
    const btnDemoChatLoop = document.getElementById('btnDemoChatLoop');
    const btnDemoChatSingle = document.getElementById('btnDemoChatSingle');
    if (btnDemoChatLoop) btnDemoChatLoop.addEventListener('click', () => ComposerDemoManager.toggleChatLoop(w, btnDemoChatLoop));
    if (btnDemoChatSingle) btnDemoChatSingle.addEventListener('click', () => ComposerDemoManager.sendChatMsg(w));

    const btnDemoDanmakuLoop = document.getElementById('btnDemoDanmakuLoop');
    const btnDemoDanmakuSingle = document.getElementById('btnDemoDanmakuSingle');
    if (btnDemoDanmakuLoop) btnDemoDanmakuLoop.addEventListener('click', () => ComposerDemoManager.toggleDanmakuLoop(w, btnDemoDanmakuLoop));
    if (btnDemoDanmakuSingle) btnDemoDanmakuSingle.addEventListener('click', () => ComposerDemoManager.sendDanmakuMsg(w));

    const btnCompChatDemoSend = document.getElementById('btnCompChatDemoSend');
    const compChatDemoInput = document.getElementById('compChatDemoInput');
    if (btnCompChatDemoSend && compChatDemoInput) {
      const sendCustom = () => {
        const val = compChatDemoInput.value.trim();
        if (!val) return;
        if (w.chatMode === 'danmaku') {
          ComposerDemoManager.sendDanmakuMsg(w, val);
        } else {
          ComposerDemoManager.sendChatMsg(w, val);
        }
        compChatDemoInput.value = '';
      };
      btnCompChatDemoSend.addEventListener('click', sendCustom);
      compChatDemoInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendCustom();
      });
    }

    const btnDemoBalloonSingle = document.getElementById('btnDemoBalloonSingle');
    if (btnDemoBalloonSingle) btnDemoBalloonSingle.addEventListener('click', () => ComposerDemoManager.sendBalloonMsg(w));

    const btnDemoCharTalk = document.getElementById('btnDemoCharTalk');
    if (btnDemoCharTalk) btnDemoCharTalk.addEventListener('click', () => ComposerDemoManager.triggerCharacterTalk(w));

    const btnDemoClockToggle = document.getElementById('btnDemoClockToggle');
    if (btnDemoClockToggle) {
      btnDemoClockToggle.addEventListener('click', () => {
        w.clockFormat = w.clockFormat === '12' ? '24' : '12';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoClockSecs = document.getElementById('btnDemoClockSecs');
    if (btnDemoClockSecs) {
      btnDemoClockSecs.addEventListener('click', () => {
        w.showSeconds = w.showSeconds === false ? true : false;
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoTextTicker = document.getElementById('btnDemoTextTicker');
    if (btnDemoTextTicker) {
      btnDemoTextTicker.addEventListener('click', () => {
        w.textMode = w.textMode === 'ticker' ? 'static' : 'ticker';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoWebcamRec = document.getElementById('btnDemoWebcamRec');
    if (btnDemoWebcamRec) {
      btnDemoWebcamRec.addEventListener('click', () => {
        const dot = document.querySelector(`#widget-${w.id} .webcam-rec-dot`);
        if (dot) dot.style.display = dot.style.display === 'none' ? 'block' : 'none';
      });
    }

    const btnDemoWebcamAudio = document.getElementById('btnDemoWebcamAudio');
    if (btnDemoWebcamAudio) {
      btnDemoWebcamAudio.addEventListener('click', () => {
        const bars = document.querySelectorAll(`#widget-${w.id} .webcam-vu-bar`);
        bars.forEach(b => {
          b.style.height = (4 + Math.random() * 12) + 'px';
        });
      });
    }

    const btnDemoGoalPlus = document.getElementById('btnDemoGoalPlus');
    const btnDemoGoalReset = document.getElementById('btnDemoGoalReset');
    if (btnDemoGoalPlus) btnDemoGoalPlus.addEventListener('click', () => ComposerDemoManager.triggerGoalPlus(w));
    if (btnDemoGoalReset) btnDemoGoalReset.addEventListener('click', () => ComposerDemoManager.triggerGoalReset(w));

    const btnDemoViewerRandom = document.getElementById('btnDemoViewerRandom');
    const btnDemoViewerAdd = document.getElementById('btnDemoViewerAdd');
    const btnDemoViewerSub = document.getElementById('btnDemoViewerSub');
    if (btnDemoViewerRandom) btnDemoViewerRandom.addEventListener('click', () => ComposerDemoManager.triggerViewerRandom(w));
    if (btnDemoViewerAdd) btnDemoViewerAdd.addEventListener('click', () => ComposerDemoManager.triggerViewerAdd(w, 50));
    if (btnDemoViewerSub) btnDemoViewerSub.addEventListener('click', () => ComposerDemoManager.triggerViewerSub(w, 30));

    const btnDemoEmoteParty = document.getElementById('btnDemoEmoteParty');
    if (btnDemoEmoteParty) btnDemoEmoteParty.addEventListener('click', () => ComposerDemoManager.triggerEmoteParty(w));

    const btnDemoNowPlayingNext = document.getElementById('btnDemoNowPlayingNext');
    if (btnDemoNowPlayingNext) btnDemoNowPlayingNext.addEventListener('click', () => ComposerDemoManager.triggerNowPlayingNext(w));

    // Binders for specific widgets
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        bindField('cwcDanmakuColor', 'fontColor');
        bindField('cwcDanmakuSize', 'fontSize', 'number', 'px');
        bindField('cwcDanmakuSpeed', 'speed', 'number', ' วิ');
        bindField('cwcDanmakuOpacity', 'opacity', 'opacity');
        bindField('cwcDanmakuZone', 'slider_zone');
        bindField('cwcDanmakuStrokeColor', 'strokeColor');
        bindField('cwcDanmakuStrokeWidth', 'textStrokeWidth', 'number', 'px');
        bindField('cwcDanmakuShadowColor', 'textShadowColor');
        const chkDanmakuStroke = document.getElementById('cwcDanmakuStroke');
        if (chkDanmakuStroke) {
          chkDanmakuStroke.addEventListener('change', () => {
            w.textStroke = chkDanmakuStroke.checked;
            renderCanvasWidgets();
            saveState();
          });
        }
      } else if (mode === 'balloon') {
        bindField('cwcBalloonBg', 'balloonBg');
        bindField('cwcBalloonColor', 'balloonTextColor');
        bindField('cwcBalloonRadius', 'balloonRadius', 'number', 'px');
        bindField('cwcBalloonSize', 'fontSize', 'number', 'px');
        bindField('cwcBalloonOpacity', 'balloonOpacity', 'opacity');
      } else if (mode === 'character') {
        bindField('cwcCharName', 'characterName');
        bindField('cwcCharAlign', 'charAlign');
        bindField('cwcCharBubbleBg', 'charBubbleBg');
        bindField('cwcCharTextColor', 'charTextColor');
        bindField('cwcCharFontSize', 'charFontSize', 'number', 'px');
      } else {
        // Mode: Default / Theme
        const tabStd = document.getElementById('tabSubStandard');
        const tabThm = document.getElementById('tabSubTheme');
        if (tabStd) tabStd.addEventListener('click', () => { state.chatSubTab = 'standard'; renderWidgetCustomizerPanel(w.id); });
        if (tabThm) tabThm.addEventListener('click', () => { state.chatSubTab = 'theme'; renderWidgetCustomizerPanel(w.id); });

        document.querySelectorAll('#cwcPresetsGrid .cwc-preset-card').forEach(card => {
          card.addEventListener('click', (e) => {
            e.stopPropagation();
            const tid = card.dataset.chatTheme;
            w.chatTheme = tid;
            w.chat_theme = tid;
            w.chatSubTab = 'theme';
            w.chat_sub_tab = 'theme';
            state.chatSubTab = 'theme';
            renderCanvasWidgets();
            renderWidgetCustomizerPanel(w.id);
            saveState();
          });
        });

        const allThemes = window.CWC_ALL_THEMES || [];
        const totalPages = Math.ceil(allThemes.length / 8);
        const btnPrev = document.getElementById('compBtnThemePrev');
        const btnNext = document.getElementById('compBtnThemeNext');
        if (btnPrev) btnPrev.addEventListener('click', (e) => {
          e.stopPropagation();
          state.chatThemePage = Math.max(1, (state.chatThemePage || 1) - 1);
          renderWidgetCustomizerPanel(w.id);
        });
        if (btnNext) btnNext.addEventListener('click', (e) => {
          e.stopPropagation();
          state.chatThemePage = Math.min(totalPages, (state.chatThemePage || 1) + 1);
          renderWidgetCustomizerPanel(w.id);
        });

        // Section 1: Layout & Structure
        bindField('cwcLayout', 'layout');
        bindField('cwcDirection', 'direction');
        bindField('cwcAlign', 'align');
        bindField('cwcMsgSpacing', 'msgSpacing', 'number', 'px');
        bindField('cwcMaxMessages', 'maxMessages', 'number');

        // Section 2: Typography & Font
        bindField('cwcFontFamily', 'fontFamily');
        bindField('cwcFontSize', 'fontSize', 'number', 'px');
        bindField('cwcFontWeight', 'fontWeight');
        bindField('cwcUsernameColor', 'usernameColor');
        bindField('cwcMessageColor', 'fontColor');
        bindField('cwcTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
        bindField('cwcTextStrokeColor', 'strokeColor');
        bindField('cwcTextShadowBlur', 'textShadowBlur', 'number', 'px');
        bindField('cwcTextShadowColor', 'textShadowColor');

        const chkStroke = document.getElementById('cwcTextStroke');
        const strokeWRow = document.getElementById('cwcStrokeWidthRow');
        const strokeCRow = document.getElementById('cwcStrokeColorRow');
        if (chkStroke) {
          chkStroke.addEventListener('change', () => {
            w.textStroke = chkStroke.checked;
            if (strokeWRow) strokeWRow.style.display = chkStroke.checked ? 'flex' : 'none';
            if (strokeCRow) strokeCRow.style.display = chkStroke.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        const chkShadow = document.getElementById('cwcTextShadow');
        const shadowBRow = document.getElementById('cwcShadowBlurRow');
        const shadowCRow = document.getElementById('cwcShadowColorRow');
        if (chkShadow) {
          chkShadow.addEventListener('change', () => {
            w.textShadow = chkShadow.checked;
            if (shadowBRow) shadowBRow.style.display = chkShadow.checked ? 'flex' : 'none';
            if (shadowCRow) shadowCRow.style.display = chkShadow.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        // Section 3: Message Box & Bubble
        bindField('cwcBoxWidth', 'boxWidth');
        bindField('cwcBgColor', 'bgColor');
        bindField('cwcBgOpacity', 'bgOpacity', 'opacity');
        bindField('cwcBoxRadius', 'boxRadius', 'number', 'px');
        bindField('cwcBoxPadding', 'boxPadding', 'number', 'px');
        bindField('cwcBoxBorderWidth', 'boxBorderWidth', 'number', 'px');
        bindField('cwcBoxBorderColor', 'boxBorderColor');
        bindField('cwcBoxGlowColor', 'boxGlowColor');

        const chkBoxEnabled = document.getElementById('cwcBoxEnabled');
        if (chkBoxEnabled) chkBoxEnabled.addEventListener('change', () => { w.boxEnabled = chkBoxEnabled.checked; renderCanvasWidgets(); saveState(); });

        const chkBoxBorder = document.getElementById('cwcBoxBorder');
        const boxBorderWRow = document.getElementById('cwcBoxBorderWidthRow');
        const boxBorderCRow = document.getElementById('cwcBoxBorderColorRow');
        if (chkBoxBorder) {
          chkBoxBorder.addEventListener('change', () => {
            w.boxBorder = chkBoxBorder.checked;
            if (boxBorderWRow) boxBorderWRow.style.display = chkBoxBorder.checked ? 'flex' : 'none';
            if (boxBorderCRow) boxBorderCRow.style.display = chkBoxBorder.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        const chkBoxShadow = document.getElementById('cwcBoxShadow');
        if (chkBoxShadow) chkBoxShadow.addEventListener('change', () => { w.boxShadow = chkBoxShadow.checked; renderCanvasWidgets(); saveState(); });

        const chkBoxGlow = document.getElementById('cwcBoxGlow');
        const boxGlowCRow = document.getElementById('cwcBoxGlowColorRow');
        if (chkBoxGlow) {
          chkBoxGlow.addEventListener('change', () => {
            w.boxGlow = chkBoxGlow.checked;
            if (boxGlowCRow) boxGlowCRow.style.display = chkBoxGlow.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        // Section: Chat Container Background Box
        const chkContainerBg = document.getElementById('compChatContainerBgEnabled');
        const wrapContainerSettings = document.getElementById('compChatContainerSettingsWrap');
        if (chkContainerBg) {
          chkContainerBg.addEventListener('change', () => {
            w.containerBgEnabled = chkContainerBg.checked;
            w.container_bg_enabled = chkContainerBg.checked;
            if (wrapContainerSettings) wrapContainerSettings.style.display = chkContainerBg.checked ? 'block' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }
        bindField('compChatContainerBgColor', 'containerBgColor');
        bindField('compChatContainerBgOpacity', 'containerBgOpacity', 'opacity');
        bindField('compChatContainerRadius', 'containerRadius', 'number', 'px');

        const chkContainerBorder = document.getElementById('compChatContainerBorder');
        const containerBorderWRow = document.getElementById('compChatContainerBorderWidthRow');
        const containerBorderCRow = document.getElementById('compChatContainerBorderColorRow');
        if (chkContainerBorder) {
          chkContainerBorder.addEventListener('change', () => {
            w.containerBorder = chkContainerBorder.checked;
            w.container_border = chkContainerBorder.checked;
            if (containerBorderWRow) containerBorderWRow.style.display = chkContainerBorder.checked ? 'flex' : 'none';
            if (containerBorderCRow) containerBorderCRow.style.display = chkContainerBorder.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }
        bindField('compChatContainerBorderWidth', 'containerBorderWidth', 'number', 'px');
        bindField('compChatContainerBorderColor', 'containerBorderColor');

        // Section 4: Animations & Auto-Hide
        const selAnimIn = document.getElementById('compChatAnimIn');
        if (selAnimIn) {
          selAnimIn.addEventListener('change', () => {
            w.animation = selAnimIn.value;
            w.animIn = selAnimIn.value;
            w.anim_in = selAnimIn.value;
            saveState();
          });
        }

        const selAnimOut = document.getElementById('compChatAnimOut');
        if (selAnimOut) {
          selAnimOut.addEventListener('change', () => {
            w.exitAnimation = selAnimOut.value;
            w.animOut = selAnimOut.value;
            w.exit_animation = selAnimOut.value;
            w.anim_out = selAnimOut.value;
            saveState();
          });
        }

        const chkAutoHide = document.getElementById('compChatAutoHide');
        const hideAfterRow = document.getElementById('compChatHideAfterRow');
        if (chkAutoHide) {
          chkAutoHide.addEventListener('change', () => {
            w.autoHide = chkAutoHide.checked;
            w.auto_hide = chkAutoHide.checked;
            if (hideAfterRow) hideAfterRow.style.display = chkAutoHide.checked ? 'flex' : 'none';
            saveState();
          });
        }
        bindField('compChatHideAfter', 'hideAfter', 'number', ' วินาที');
      }
    }
    else if (w.type === 'clock') {
      const tabClkTheme = document.getElementById('tabClockTheme');
      const tabClkStyle = document.getElementById('tabClockStyle');
      if (tabClkTheme) {
        tabClkTheme.addEventListener('click', () => {
          w.clockMode = 'theme';
          w.clock_mode = 'theme';
          renderCanvasWidgets();
          renderWidgetCustomizerPanel(w.id);
          saveState();
        });
      }
      if (tabClkStyle) {
        tabClkStyle.addEventListener('click', () => {
          w.clockMode = 'style';
          w.clock_mode = 'style';
          if (!w.clockStyle || w.clockStyle === 'none') {
            w.clockStyle = 'dot1';
            w.clock_style = 'dot1';
          }
          renderCanvasWidgets();
          renderWidgetCustomizerPanel(w.id);
          saveState();
        });
      }

      bindField('compClockTheme', 'clockTheme');
      bindField('compClockFormat', 'clockFormat');
      bindField('compClockFontSize', 'fontSize', 'number', 'px');
      bindField('compClockTimeColor', 'timeColor');
      bindField('compClockThemeOpacity', 'themeOpacity', 'opacity');

      const chkShowDate = document.getElementById('compClockShowDate');
      if (chkShowDate) {
        chkShowDate.addEventListener('change', () => {
          w.showDate = chkShowDate.checked;
          w.show_date = chkShowDate.checked;
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compClockDateLang', 'dateLang');
      bindField('compClockDateFormat', 'dateFormat');
      bindField('compClockDateFontSize', 'dateFontSize', 'number', 'px');
      bindField('compClockDateColor', 'dateColor');

      bindField('compClockStyle', 'clockStyle');
      bindField('compClockStyleOpacity', 'styleOpacity', 'opacity');
    } else if (w.type === 'text') {
      bindField('compTextInput', 'text');
      const textModeEl = document.getElementById('compTextMode');
      const speedRow = document.getElementById('compTextSpeedRow');
      if (textModeEl) {
        textModeEl.addEventListener('change', () => {
          w.textMode = textModeEl.value;
          if (speedRow) speedRow.style.display = w.textMode === 'ticker' ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compTextSpeed', 'marqueeSpeed', 'number', ' วิ');
      bindField('compTextFontSize', 'fontSize', 'number', 'px');
      bindField('compTextFontColor', 'fontColor');
      bindField('compTextBgColor', 'bgColor');

      // Vertical alignment buttons
      const btnVTop = document.getElementById('btnTextVAlignTop');
      const btnVMid = document.getElementById('btnTextVAlignMid');
      const btnVBot = document.getElementById('btnTextVAlignBot');
      if (btnVTop && btnVMid && btnVBot) {
        const updateVAlign = (val) => {
          w.vAlign = val;
          btnVTop.classList.toggle('active', val === 'top');
          btnVMid.classList.toggle('active', val === 'center');
          btnVBot.classList.toggle('active', val === 'bottom');
          renderCanvasWidgets();
          saveState();
        };
        btnVTop.addEventListener('click', () => updateVAlign('top'));
        btnVMid.addEventListener('click', () => updateVAlign('center'));
        btnVBot.addEventListener('click', () => updateVAlign('bottom'));
      }

      // Background toggle
      const btnBgToggle = document.getElementById('btnTextToggleBg');
      const inpBgColor = document.getElementById('compTextBgColor');
      if (btnBgToggle) {
        btnBgToggle.addEventListener('click', () => {
          w.bgEnabled = (w.bgEnabled === false) ? true : false;
          btnBgToggle.textContent = w.bgEnabled ? '🎨 เปิดใช้พื้นหลัง' : '🚫 ไม่ใช้พื้นหลัง (ใส)';
          btnBgToggle.classList.toggle('active', !w.bgEnabled);
          if (inpBgColor) {
            inpBgColor.disabled = !w.bgEnabled;
            inpBgColor.style.opacity = w.bgEnabled ? '1' : '0.4';
          }
          renderCanvasWidgets();
          saveState();
        });
      }

      // Stroke controls (default 0)
      bindField('compTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
      bindField('compTextStrokeColor', 'strokeColor');

      // Shadow controls (default 0)
      bindField('compTextShadowBlur', 'textShadowBlur', 'number', 'px');
      bindField('compTextShadowColor', 'textShadowColor');
    } else if (w.type === 'webcam') {
      const ratioEl = document.getElementById('compWebcamRatio');
      if (ratioEl) {
        ratioEl.addEventListener('change', () => {
          const ratio = ratioEl.value;
          w.ratio = ratio;
          let newH = w.height;
          if (ratio === '16:9') newH = Math.round(w.width * 9 / 16);
          else if (ratio === '4:3') newH = Math.round(w.width * 3 / 4);
          else if (ratio === '1:1') newH = Math.round(w.width);
          else if (ratio === '9:16') newH = Math.round(w.width * 16 / 9);
          w.height = newH;
          updateTransformInspector();
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compWebcamTheme', 'webcamTheme');
      bindField('compWebcamBorderWidth', 'borderWidth', 'number', 'px');
      bindField('compWebcamBorderColor', 'borderColor');
    } else if (w.type === 'goal') {
      bindField('compGoalTitle', 'goalTitle');
      bindField('compGoalCurrent', 'goalCurrent', 'number');
      bindField('compGoalTarget', 'goalTarget', 'number');
      bindField('compGoalUnit', 'goalUnit');
    } else if (w.type === 'viewer') {
      bindField('compViewerTheme', 'viewerTheme');
      bindField('compViewerMode', 'viewerMode');
      bindField('compViewerDirection', 'viewerDirection');
      bindField('compViewerAlign', 'viewerAlign');
      bindField('compViewerShowIcon', 'showIcon', 'checkbox');
      bindField('compViewerIconSize', 'iconSize', 'number', 'px');
      bindField('compViewerFontSize', 'fontSize', 'number', 'px');
      bindField('compViewerFontColor', 'fontColor');

      const chkViewerStroke = document.getElementById('compViewerTextStroke');
      const strokeWRow = document.getElementById('compViewerTextStrokeRow');
      const strokeCRow = document.getElementById('compViewerTextStrokeColorRow');
      if (chkViewerStroke) {
        chkViewerStroke.addEventListener('change', () => {
          w.textStroke = chkViewerStroke.checked;
          if (strokeWRow) strokeWRow.style.display = chkViewerStroke.checked ? 'flex' : 'none';
          if (strokeCRow) strokeCRow.style.display = chkViewerStroke.checked ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compViewerTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
      bindField('compViewerTextStrokeColor', 'strokeColor');

      const platCbs = document.querySelectorAll('.comp-viewer-plat-cb');
      platCbs.forEach(cb => {
        cb.addEventListener('change', () => {
          const selected = [];
          document.querySelectorAll('.comp-viewer-plat-cb:checked').forEach(c => {
            selected.push(c.dataset.plat);
          });
          w.viewerPlatforms = selected.length > 0 ? selected : ['youtube'];
          renderCanvasWidgets();
          saveState();
        });
      });
    } else if (w.type === 'character') {
      bindField('compCharWidgetName', 'characterName');
    } else if (w.type === 'image') {
      bindField('compImageUrl', 'imageUrl');
      bindField('compImageFit', 'fitMode');
    } else if (w.type === 'video') {
      bindField('compVideoUrl', 'videoUrl');
      bindField('compVideoFit', 'fitMode');
    } else if (w.type === 'alert') {
      bindField('compAlertUrl', 'url');
      const btnRefresh = document.getElementById('btnRefreshAlert');
      if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
          renderCanvasWidgets();
          if (window.showToast) window.showToast('รีเฟรชหน้าเว็บเบราว์เซอร์สำเร็จ');
        });
      }
    } else if (w.type === 'now_playing') {
      // 1. Source
      const selNpSource = document.getElementById('compNpSource');
      if (selNpSource) {
        selNpSource.addEventListener('change', () => {
          w.npSource = selNpSource.value;
          w.np_source = selNpSource.value;
          renderCanvasWidgets();
          saveState();
        });
      }

      // 2. Theme Presets
      const selNpTheme = document.getElementById('compNpTheme');
      if (selNpTheme) {
        selNpTheme.addEventListener('change', () => {
          const theme = selNpTheme.value;
          w.npTheme = theme;
          w.np_theme = theme;
          const npPresets = {
            spotify:    { bg:'#1ed760', accent:'#000000', text:'#0a0a0a', opacity:95, radius:12, artRadius:6 },
            applemusic: { bg:'#fc2c55', accent:'#ffffff', text:'#ffffff', opacity:90, radius:16, artRadius:8 },
            ytmusic:    { bg:'#0f0f0f', accent:'#ff0000', text:'#ffffff', opacity:90, radius:4, artRadius:2 },
            neon:       { bg:'#1a0a2e', accent:'#bf00ff', text:'#e0b3ff', opacity:85, radius:8, artRadius:6 },
            glass:      { bg:'#2a2a3e', accent:'#64c8ff', text:'#ffffff', opacity:50, radius:16, artRadius:12 },
            dark:       { bg:'#000000', accent:'#333333', text:'#cccccc', opacity:90, radius:6, artRadius:4 },
            light:      { bg:'#ffffff', accent:'#0066cc', text:'#1a1a1a', opacity:95, radius:12, artRadius:8 },
            retro:      { bg:'#2a1a00', accent:'#ff8800', text:'#ffcc66', opacity:85, radius:4, artRadius:2 },
            ocean:      { bg:'#001a33', accent:'#00bfff', text:'#cce8ff', opacity:85, radius:12, artRadius:8 },
            sunset:     { bg:'#2a0a1a', accent:'#ff6b9d', text:'#ffd6e8', opacity:85, radius:12, artRadius:8 },
            cyberpunk:  { bg:'#0a0014', accent:'#00ffff', text:'#ff00ff', opacity:90, radius:2, artRadius:2 },
            aurora:     { bg:'#001a1a', accent:'#00ffaa', text:'#aaffee', opacity:80, radius:16, artRadius:12 },
            lava:       { bg:'#1a0500', accent:'#ff4400', text:'#ffaa88', opacity:90, radius:4, artRadius:2 },
            mint:       { bg:'#00220a', accent:'#00ff88', text:'#aaffcc', opacity:85, radius:12, artRadius:8 },
            lavender:   { bg:'#1a0a2a', accent:'#aa88ff', text:'#ddccff', opacity:85, radius:16, artRadius:12 },
            crimson:    { bg:'#1a0000', accent:'#ff0044', text:'#ff88aa', opacity:90, radius:6, artRadius:4 },
            gold:       { bg:'#1a1400', accent:'#ffcc00', text:'#ffeeaa', opacity:85, radius:8, artRadius:6 },
            deepocean:  { bg:'#000a1a', accent:'#0088ff', text:'#88ccff', opacity:85, radius:12, artRadius:8 },
            forest:     { bg:'#0a1a00', accent:'#44aa00', text:'#aacc88', opacity:85, radius:8, artRadius:6 },
            bubblegum:  { bg:'#2a0a1a', accent:'#ff44aa', text:'#ffaadd', opacity:85, radius:20, artRadius:16 },
          };
          if (theme !== 'custom' && npPresets[theme]) {
            const p = npPresets[theme];
            w.npBgColor = p.bg; w.np_bg_color = p.bg;
            w.npAccentColor = p.accent; w.np_accent_color = p.accent;
            w.npTextColor = p.text; w.np_text_color = p.text;
            w.npBgOpacity = p.opacity / 100; w.np_bg_opacity = p.opacity / 100;
            w.npRadius = p.radius; w.np_radius = p.radius;
            w.npArtRadius = p.artRadius; w.np_art_radius = p.artRadius;
            w.npTransparent = false;

            // Update UI elements in drawer
            const elBg = document.getElementById('compNpBgColor'); if (elBg) elBg.value = p.bg;
            const elAcc = document.getElementById('compNpAccentColor'); if (elAcc) elAcc.value = p.accent;
            const elTxt = document.getElementById('compNpTextColor'); if (elTxt) elTxt.value = p.text;
            const elOp = document.getElementById('compNpBgOpacity'); if (elOp) elOp.value = p.opacity;
            const elOpVal = document.getElementById('compNpBgOpacityVal'); if (elOpVal) elOpVal.textContent = p.opacity + '%';
            const elRad = document.getElementById('compNpRadius'); if (elRad) elRad.value = p.radius;
            const elRadVal = document.getElementById('compNpRadiusVal'); if (elRadVal) elRadVal.textContent = p.radius + 'px';
            const elArtRad = document.getElementById('compNpArtRadius'); if (elArtRad) elArtRad.value = p.artRadius;
            const elArtRadVal = document.getElementById('compNpArtRadiusVal'); if (elArtRadVal) elArtRadVal.textContent = p.artRadius + 'px';
            const chkTr = document.getElementById('compNpTransparent'); if (chkTr) chkTr.checked = false;
            const rowBg = document.getElementById('compNpBgColorRow'); if (rowBg) rowBg.style.display = 'flex';
            const rowOp = document.getElementById('compNpBgOpacityRow'); if (rowOp) rowOp.style.display = 'flex';
          }
          renderCanvasWidgets();
          saveState();
        });
      }

      // 3. Style Pattern
      const selNpStyle = document.getElementById('compNpStyle');
      if (selNpStyle) {
        selNpStyle.addEventListener('change', () => {
          w.npStyle = selNpStyle.value;
          w.np_style = selNpStyle.value;
          renderCanvasWidgets();
          saveState();
        });
      }

      // 4. Fonts and Colors
      bindField('compNpFontSize', 'npFontSize', 'number', 'px');
      bindField('compNpArtistFontSize', 'npArtistFontSize', 'number', 'px');
      bindField('compNpTimeFontSize', 'npTimeFontSize', 'number', 'px');
      bindField('compNpTextColor', 'npTextColor');
      bindField('compNpAccentColor', 'npAccentColor');

      // 5. Display Toggles
      bindField('compNpShowArt', 'npShowArt', 'checkbox');
      bindField('compNpShowProgress', 'npShowProgress', 'checkbox');
      bindField('compNpScrollTitle', 'npScrollTitle', 'checkbox');
      bindField('compNpSyncMode', 'npSyncMode');

      // 6. Box & Background
      const chkTrans = document.getElementById('compNpTransparent');
      const bgClrRow = document.getElementById('compNpBgColorRow');
      const bgOpRow = document.getElementById('compNpBgOpacityRow');
      if (chkTrans) {
        chkTrans.addEventListener('change', () => {
          w.npTransparent = chkTrans.checked;
          if (bgClrRow) bgClrRow.style.display = chkTrans.checked ? 'none' : 'flex';
          if (bgOpRow) bgOpRow.style.display = chkTrans.checked ? 'none' : 'flex';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compNpBgColor', 'npBgColor');
      bindField('compNpBgOpacity', 'npBgOpacity', 'opacity');
      bindField('compNpRadius', 'npRadius', 'number', 'px');
      bindField('compNpArtRadius', 'npArtRadius', 'number', 'px');
      bindField('compNpArtSize', 'npArtSize', 'number', 'px');
    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ชื่อของรางวัล</span>
              <input type="text" class="cwc-input" id="compGiveawayPrize" value="${w.prizeTitle || 'รางวัลพิเศษประจำสตรีม'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;

    } else if (w.type === 'emote_party') {
      bindField('compEpAnimation', 'epAnimation');
      bindField('compEpDuration', 'epDuration', 'number', ' วิ');
      bindField('compEpMaxEmotes', 'epMaxEmotes', 'number', ' ตัว');
      bindField('compEpEmoteSize', 'epEmoteSize', 'number', 'px');
    }
  }


  // Export Profile (JSON download)
  function exportProfile() {
    try {
      const data = {
        version: '3.0.0',
        exportedAt: new Date().toISOString(),
        pages: state.pages,
        activePageId: state.activePageId
      };
      const jsonStr = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `broadcast_playroom_profile_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      if (window.showToast) window.showToast('ส่งออกไฟล์ Profile สำเร็จ');
    } catch (e) {
      alert('ส่งออกไม่สำเร็จ: ' + e);
    }
  }

  // Import Profile (Parse JSON & Auto-Migrate)
  function importProfile(jsonStr) {
    try {
      const parsed = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
      if (parsed) {
        if (Array.isArray(parsed)) {
          if (parsed[0] && parsed[0].widgets) {
            state.pages = parsed.map(p => {
              p.widgets = (p.widgets || []).map(normalizeWidget);
              return p;
            });
          } else {
            state.pages = [{
              id: 'page-1',
              name: 'หน้า 1',
              widgets: parsed.map(normalizeWidget)
            }];
          }
        } else if (parsed.pages && Array.isArray(parsed.pages)) {
          state.pages = parsed.pages.map(p => {
            p.widgets = (p.widgets || []).map(normalizeWidget);
            return p;
          });
        } else if (parsed.widgets && Array.isArray(parsed.widgets)) {
          state.pages = [{
            id: 'page-1',
            name: 'หน้า 1',
            widgets: parsed.widgets.map(normalizeWidget)
          }];
        }
        state.activePageId = state.pages[0].id;
        renderPageTabs();
        renderCanvasWidgets();
        renderLayersList();
        saveState();
        if (window.showToast) window.showToast('นำเข้าและ Migrate เลย์เอาต์เรียบร้อยแล้ว');
      }
    } catch (e) {
      alert('นำเข้าไฟล์ไม่สำเร็จ: ' + e);
    }
  }

  // Toggle Clean Preview Mode
  function togglePreviewMode() {
    const modal = document.getElementById('win-composer') || document.getElementById('composerStudioModal') || document.querySelector('.composer-window');
    if (!modal) return;
    const isPreview = modal.classList.toggle('preview-clean-mode');
    const btn = document.getElementById('btnCompPreview');
    if (btn) {
      btn.innerHTML = isPreview ? '✏️ แก้ไข' : '👁️ พรีวิว';
      btn.classList.toggle('active', isPreview);
    }
    if (window.showToast) {
      window.showToast(isPreview ? 'เข้าสู่โหมดพรีวิว (ซ่อนเครื่องมือทั้งหมด)' : 'กลับสู่โหมดแก้ไข');
    }
  }

  // Setup Toolbar Events
  function setupToolbarEvents() {
    // Zoom buttons
    document.getElementById('btnCompZoomIn')?.addEventListener('click', () => setZoom(state.zoom + 0.1));
    document.getElementById('btnCompZoomOut')?.addEventListener('click', () => setZoom(state.zoom - 0.1));
    document.getElementById('btnCompZoomFit')?.addEventListener('click', autoFitCanvas);

    // Snap toggle
    const btnSnap = document.getElementById('btnCompSnap');
    if (btnSnap) {
      btnSnap.addEventListener('click', () => {
        state.snapGuides = !state.snapGuides;
        btnSnap.classList.toggle('active', state.snapGuides);
        if (window.showToast) {
          window.showToast(state.snapGuides ? 'เปิดระบบแม่เหล็กจัดแนวแล้ว' : 'ปิดระบบแม่เหล็กจัดแนวแล้ว');
        }
      });
    }

    // Background toggle
    document.querySelectorAll('.composer-bg-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.composer-bg-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.dataset.bg;
        const stage = document.getElementById('composerCanvasStage');
        if (stage) {
          stage.className = `composer-canvas-stage bg-${mode}`;
        }
      });
    });

    // Chat Context Dropdown Trigger
    const btnChatMenu = document.getElementById('btnCompAddChatMenu');
    const menuChat = document.getElementById('compChatDropdownMenu');
    if (btnChatMenu && menuChat) {
      btnChatMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = menuChat.style.display === 'block';
        menuChat.style.display = isOpen ? 'none' : 'block';
      });

      menuChat.querySelectorAll('.comp-chat-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
          e.stopPropagation();
          menuChat.style.display = 'none';
          const mode = item.dataset.chatMode || 'default';
          checkAndAddWidget('chat', mode);
        });
      });

      document.addEventListener('click', (e) => {
        if (!e.target.closest('#chatAddBtnWrapper')) {
          menuChat.style.display = 'none';
        }
      });
    }

    // Add Widget Buttons (Excluding the chat dropdown trigger)
    document.querySelectorAll('.btn-add-widget').forEach(btn => {
      if (btn.id === 'btnCompAddChatMenu') return;
      btn.addEventListener('click', () => {
        checkAndAddWidget(btn.dataset.widgetType);
      });
    });

    // Align Buttons
    document.querySelectorAll('.composer-btn-align').forEach(btn => {
      btn.addEventListener('click', () => {
        alignWidget(btn.dataset.align);
      });
    });

    // Transform Inspector inputs (clamped to canvas bounds)
    const bindProp = (id, key, minVal) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', () => {
        const widget = getSelectedWidget();
        if (!widget || widget.locked) return;
        const val = parseInt(el.value, 10);
        if (!isNaN(val)) {
          if (key === 'x') {
            widget.x = Math.max(0, Math.min(CANVAS_WIDTH - widget.width, val));
          } else if (key === 'y') {
            widget.y = Math.max(0, Math.min(CANVAS_HEIGHT - widget.height, val));
          } else if (key === 'width') {
            widget.width = Math.max(50, Math.min(CANVAS_WIDTH - widget.x, val));
          } else if (key === 'height') {
            widget.height = Math.max(30, Math.min(CANVAS_HEIGHT - widget.y, val));
          } else {
            widget[key] = Math.max(minVal, val);
          }
          renderCanvasWidgets();
          updateTransformInspector();
          saveState();
        }
      });
    };

    bindProp('compPropX', 'x', 0);
    bindProp('compPropY', 'y', 0);
    bindProp('compPropW', 'width', 50);
    bindProp('compPropH', 'height', 30);

    // Preview Mode Button
    document.getElementById('btnCompPreview')?.addEventListener('click', togglePreviewMode);

    // Export Profile Button
    document.getElementById('btnCompExport')?.addEventListener('click', exportProfile);

    // Import Profile Button & File Input
    const btnImport = document.getElementById('btnCompImport');
    const fileInput = document.getElementById('fileCompImportProfile');
    if (btnImport && fileInput) {
      btnImport.addEventListener('click', () => fileInput.click());
      fileInput.addEventListener('change', (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
          importProfile(evt.target.result);
          fileInput.value = '';
        };
        reader.readAsText(file);
      });
    }

    // Save Button
    document.getElementById('btnCompSave')?.addEventListener('click', saveState);

    // Copy OBS URL Button
    document.getElementById('btnCompCopyObs')?.addEventListener('click', copyComposerObsUrl);

    // Test in Browser Button
    document.getElementById('btnCompTestBrowser')?.addEventListener('click', openComposerTestInBrowser);
  }

  // Copy OBS URL
  function copyComposerObsUrl() {
    const host = (window.location.origin && window.location.origin.startsWith('http')) ? window.location.origin : 'http://127.0.0.1:8080';
    const activePage = getActivePage();
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/composer.html?p=${pageIndex}`;
    saveState(true);

    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        if (window.showToast) window.showToast(`📋 คัดลอกลิงก์ OBS สำหรับหน้า ${pageIndex} สำเร็จ (${url})`);
      }).catch(() => {
        prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
      });
    } else {
      prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
    }
  }

  // Open live test preview in browser
  function openComposerTestInBrowser() {
    const host = (window.location.origin && window.location.origin.startsWith('http')) ? window.location.origin : 'http://127.0.0.1:8080';
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/composer.html?p=${pageIndex}&test=1`;
    saveState(true);
    window.open(url, '_blank');
    if (window.showToast) {
      window.showToast(`🧪 เปิดหน้าต่างทดสอบ Overlay (หน้า ${pageIndex}) ในเบราว์เซอร์แล้ว`);
    }
  }

  // Expose Global Helper
  window.initComposerStudio = initComposerStudio;
  window.autoFitCanvas = autoFitCanvas;
  window.renderWidgetInnerHtml = renderWidgetInnerHtml;
  window.isFullscreenWidget = isFullscreenWidget;
  window.openComposerTestInBrowser = openComposerTestInBrowser;
  window.copyComposerObsUrl = copyComposerObsUrl;
  function bindComposerPopoutWindow(popWindow) {
    if (!popWindow || popWindow.closed) return;
    try {
      popWindow.addEventListener('resize', autoFitCanvas);
      popWindow.addEventListener('keydown', handleKeyDown);
      bindSpacebarPanning(popWindow);
      setTimeout(autoFitCanvas, 80);
    } catch (e) {
      console.warn('Could not bind composer popout window:', e);
    }
  }

  window.ComposerStudio = {
    init: initComposerStudio,
    autoFitCanvas: autoFitCanvas,
    bindWindow: bindComposerPopoutWindow,
    selectWidget: selectWidget,
    openWidgetSettings: openWidgetSettings,
    openWidgetCustomizer: openWidgetCustomizer,
    getState: () => state,
    getActivePage: getActivePage,
    state: state,
    addWidget: addWidget,
    checkAndAddWidget: checkAndAddWidget,
    deleteWidget: deleteWidget,
    duplicateWidget: duplicateWidget,
    renderCanvasWidgets: renderCanvasWidgets,
    renderLayersList: renderLayersList,
    updateTransformInspector: updateTransformInspector,
    alignWidget: alignWidget,
    demoManager: ComposerDemoManager,
    moveLayerByOne: moveLayerByOne,
    addNewPage: addNewPage,
    duplicateCurrentPage: duplicateCurrentPage,
    renameCurrentPage: renameCurrentPage,
    deletePage: deletePage,
    switchPage: switchPage,
    exportProfile: exportProfile,
    importProfile: importProfile,
    togglePreviewMode: togglePreviewMode,
    normalizeWidget: normalizeWidget,
    saveState: saveState,
    renderWidgetInnerHtml: renderWidgetInnerHtml,
    isFullscreenWidget: isFullscreenWidget,
    openTestInBrowser: openComposerTestInBrowser,
    copyObsUrl: copyComposerObsUrl
  };
  window.composerStudio = window.ComposerStudio;

  // Auto-init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComposerStudio);
  } else {
    initComposerStudio();
  }

})();


// ----------------------------------------------------
// ATTACH REAL-TIME BP3_BUS LISTENERS TO CANVAS STUDIO
// ----------------------------------------------------
function initStudioBusListener() {
  if (typeof window === 'undefined') return;
  const bus = window.BP3_BUS;
  if (!bus) {
    setTimeout(initStudioBusListener, 200);
    return;
  }

  
  bus.on('CHAT_MESSAGE', (msg) => {
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'chat') {
          const feed = document.getElementById(`widget-chat-feed-${w.id}`);
          if (feed) {
            const theme = w.chatTheme || 'default';
            const item = document.createElement('div');
            item.className = `cwc-msg-item msg chat-line theme-${theme} anim-in-${w.animIn || 'slide'}`;
            const boxStyle = w.boxEnabled !== false ? `background:rgba(30,31,34,0.85); border-radius:8px; padding:6px 12px;` : 'background:transparent;';
            item.style.cssText = boxStyle;
            item.innerHTML = `
              <div class="msg-bg"></div>
              <span class="author" style="color:${w.usernameColor || '#38bdf8'}; font-weight:700; margin-right:6px;">${msg.username}:</span>
              <span class="text" style="color:${w.fontColor || '#ffffff'}; font-size:${w.fontSize || 15}px;">${msg.text}</span>
            `;
            feed.appendChild(item);
            feed.scrollTop = feed.scrollHeight;

            if (w.autoHide) {
              const dur = (w.hideTimeout || 8) * 1000;
              setTimeout(() => {
                item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                item.style.opacity = '0';
                item.style.transform = 'translateY(-10px)';
                setTimeout(() => { item.remove(); }, 500);
              }, dur);
            }
          }
        }
      });
    }
  });

  let _csRandomizerTimer = null;
  bus.on('RANDOMIZER_SPIN', (data) => {
    if (!data) return;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[0];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'randomizer') {
          const card = document.getElementById(`compRandomizerCard_${w.id}`);
          const res = document.getElementById(`compRandomizerResult_${w.id}`);
          const hint = document.getElementById(`compRandomizerHint_${w.id}`);
          if (card && res) {
            card.style.display = 'block';
            card.style.animation = 'none';
            void card.offsetHeight;
            card.style.animation = 'randCardPopIn 0.35s cubic-bezier(0.16, 1, 0.3, 1)';

            const items = (data.items && data.items.length) ? data.items : ['1', '2'];
            let ticks = 0;
            const timer = setInterval(() => {
              ticks++;
              res.textContent = items[Math.floor(Math.random() * items.length)];
              res.style.color = '#fbbf24';
              if (ticks > 16) {
                clearInterval(timer);
                res.textContent = data.winner || items[0];
                res.style.color = '#38bdf8';
                if (hint) hint.textContent = 'สุ่มสำเร็จ 🎉';
                setTimeout(() => {
                  card.style.display = 'none';
                }, (data.duration || 5) * 1000);
              }
            }, 80);
          }
        }
      });
    }

    // On-Demand Dynamic Modal Overlay inside Composer Canvas
    const canvas = document.getElementById('composer-canvas') || document.body;
    const existing = document.getElementById('on-demand-randomizer-overlay-cs');
    if (existing) existing.remove();
    if (_csRandomizerTimer) {
      clearTimeout(_csRandomizerTimer);
      _csRandomizerTimer = null;
    }

    const items = (data.items && data.items.length) ? data.items : ['ตัวเลือก 1', 'ตัวเลือก 2'];
    const winner = data.winner || items[0];
    const title = data.title || '🎰 สุ่มกิจกรรม';
    const st = data.settings || {};
    const scale = (st.scale || 100) / 100;
    const ox = parseInt(st.offset_x, 10) || 0;
    const oy = parseInt(st.offset_y, 10) || 0;
    const holdDuration = (st.duration !== undefined ? parseFloat(st.duration) : (data.duration || 5)) * 1000;

    const overlay = document.createElement('div');
    overlay.id = 'on-demand-randomizer-overlay-cs';
    overlay.style.cssText = `
      position: absolute;
      top: 50%; left: 50%;
      z-index: 9999999;
      pointer-events: none;
      transform: translate(-50%, -50%) translate(${ox}px, ${oy}px) scale(${scale});
      transform-origin: center center;
      transition: opacity 0.4s ease-out, transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      opacity: 0;
      contain: layout style paint;
      isolation: isolate;
    `;
    overlay.innerHTML = `
      <div style="
        width: 460px;
        background: rgba(11, 17, 32, 0.96);
        border: 2px solid #3b82f6;
        border-radius: 18px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 25px rgba(59, 130, 246, 0.25);
        padding: 24px 26px 20px 26px;
        font-family: -apple-system, BlinkMacSystemFont, 'Prompt', 'Kanit', sans-serif;
        box-sizing: border-box;
        color: #ffffff;
        text-align: center;
        contain: layout style paint;
      ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 14px;">
          <span style="font-size: 20px;">🎰</span>
          <span style="font-size: 15px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase;">
            ${title}
          </span>
        </div>
        <div id="cs-roller-box" style="
          background: rgba(2, 6, 23, 0.95);
          border: 2px solid #1e293b;
          border-radius: 12px;
          height: 76px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0 16px;
          box-sizing: border-box;
          overflow: hidden;
          transition: border-color 0.3s, background-color 0.3s;
        ">
          <span id="cs-roller-text" style="
            font-size: 24px;
            font-weight: 800;
            color: #f1f5f9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
          ">...</span>
        </div>
        <div id="cs-footer-pill" style="
          margin-top: 14px;
          font-size: 12.5px;
          font-weight: 600;
          color: #94a3b8;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
        ">
          <span>⚡ กำลังสุ่ม...</span>
        </div>
      </div>
    `;
    canvas.appendChild(overlay);
    requestAnimationFrame(() => { overlay.style.opacity = '1'; });

    const rollerText = overlay.querySelector('#cs-roller-text');
    const rollerBox = overlay.querySelector('#cs-roller-box');
    const footerPill = overlay.querySelector('#cs-footer-pill');

    let ticks = 0;
    const maxTicks = 26;
    let delay = 50;

    function runCsTick() {
      ticks++;
      const cand = items[Math.floor(Math.random() * items.length)];
      if (rollerText) rollerText.textContent = cand;
      if (ticks < maxTicks) {
        if (ticks > maxTicks - 8) delay += 35;
        setTimeout(runCsTick, delay);
      } else {
        if (rollerText) rollerText.textContent = winner;
        if (rollerBox) {
          rollerBox.style.borderColor = '#f59e0b';
          rollerBox.style.backgroundColor = 'rgba(245, 158, 11, 0.12)';
          rollerText.style.color = '#fbbf24';
        }
        if (footerPill) {
          footerPill.innerHTML = '<span style="color: #fbbf24; font-weight: 700;">🎉 ผลการสุ่มเรียบร้อยแล้ว</span>';
        }
        _csRandomizerTimer = setTimeout(() => {
          overlay.style.opacity = '0';
          overlay.style.transform = `translate(-50%, -50%) translate(${ox}px, ${oy - 20}px) scale(${scale * 0.95})`;
          setTimeout(() => { overlay.remove(); }, 400);
        }, holdDuration);
      }
    }
    runCsTick();
  });

  bus.on('ASK_UPDATE', (data) => {
    window._liveAskState = data;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[0];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'ask') {
          const panel = document.getElementById(`compAskPanel_${w.id}`);
          const isAskActive = data && data.active === true && (data.phase === 'voting' || data.phase === 'ended');
          if (panel) {
            panel.style.display = isAskActive ? 'block' : 'none';
          }
          const qEl = document.getElementById(`compAskQ_${w.id}`);
          if (qEl) qEl.textContent = data.phase === 'ended' ? `🏆 สรุปผล: ${data.question}` : `📊 ${data.question}`;
          const timerEl = document.getElementById(`compAskTimer_${w.id}`);
          if (timerEl) {
            if (data.phase === 'ended') {
              timerEl.textContent = '🏆 สรุปผล';
              timerEl.style.color = '#fbbf24';
            } else if (data.phase === 'paused') {
              timerEl.textContent = '⏸ พักโหวต';
              timerEl.style.color = '#f59e0b';
            } else if (data.remainingSec != null) {
              timerEl.textContent = `⏱ ${data.remainingSec}s`;
              timerEl.style.color = data.remainingSec <= 10 ? '#f43f5e' : '#94a3b8';
            } else {
              timerEl.textContent = '🗳️ โหวตสด';
              timerEl.style.color = '#34d399';
            }
          }
          const listEl = document.getElementById(`compAskChoicesList_${w.id}`);
          if (listEl && data.choices) {
            const isEnded = (data.phase === 'ended');
            const choices = isEnded ? [...data.choices].sort((a,b) => (b.votes || 0) - (a.votes || 0)) : data.choices;
            listEl.innerHTML = choices.map((c, idx) => {
              const isWinner = isEnded && idx === 0 && (c.votes || 0) > 0;
              return `
              <div style="background:${isWinner ? 'rgba(251,191,36,0.15)' : 'rgba(255,255,255,0.05)'}; border:${isWinner ? '1.5px solid #fbbf24' : '1px solid rgba(255,255,255,0.06)'}; border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
                <div style="position:absolute; inset:0; width:${c.pct}%; background:${isWinner ? '#f59e0b' : (c.color || '#38bdf8')}; opacity:${isWinner ? '0.35' : '0.25'}; border-radius:6px; transition:width 0.4s ease;"></div>
                <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
                  <span>${isWinner ? '👑 ' : ''}${c.label}: ${c.text}</span>
                  <span style="color:${isWinner ? '#fbbf24' : (c.color || '#38bdf8')}; font-weight:700;">${c.pct}% (${c.votes || 0})</span>
                </div>
              </div>
            `;
            }).join('');
          }
        }
      });
    }
  });

  bus.on('GIVEAWAY_UPDATE', (data) => {
    window._liveGwState = data;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[0];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'giveaway') {
          const panel = document.getElementById(`compGwPanel_${w.id}`);
          const isGwActive = data && data.active === true && (data.phase === 'running' || data.phase === 'winner');
          if (panel) {
            panel.style.display = isGwActive ? 'block' : 'none';
          }
          const pEl = document.getElementById(`compGwPrize_${w.id}`);
          if (pEl) pEl.textContent = data.prize;
          const hEl = document.getElementById(`compGwHint_${w.id}`);
          if (hEl) hEl.innerHTML = `พิมพ์ <strong style="color:#fb7185;">${data.code}</strong> ในแชทเพื่อเข้าร่วมสุ่ม`;
          const cEl = document.getElementById(`compGwCount_${w.id}`);
          if (cEl) cEl.textContent = `ผู้เข้าร่วม: ${data.count} คน`;
          const winEl = document.getElementById(`compGwWinner_${w.id}`);
          const winNameEl = document.getElementById(`compGwWinnerName_${w.id}`);
          if (winEl && winNameEl) {
            if (data.winner) {
              winNameEl.textContent = data.winner;
              winEl.style.display = 'block';
            } else {
              winEl.style.display = 'none';
            }
          }
        }
      });
    }
  });

  bus.on('REPLIE_ACTION', (data) => {
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'character' || w.type === 'avatar' || w.type === 'replie') {
          const bubble = document.getElementById(`compCharBubble_${w.id}`);
          const bubbleText = document.getElementById(`compCharBubbleText_${w.id}`);
          const img = document.getElementById(`compCharImg_${w.id}`);
          if (bubble && bubbleText) {
            bubbleText.textContent = data.text || 'สวัสดีครับ!';
            bubble.style.display = 'block';
            bubble.style.opacity = '1';
            if (img) {
              img.style.transform = 'scale(1.15) translateY(-8px)';
              setTimeout(() => { img.style.transform = 'scale(1)'; }, 350);
            }
            setTimeout(() => {
              bubble.style.opacity = '0';
              setTimeout(() => { bubble.style.display = 'none'; }, 300);
            }, 5000);
          }
        }
      });
    }
  });

  bus.on('PLAYROOM_PLAY_CLIP', (data) => {
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'playroom') {
          const stage = document.getElementById(`compPlayroomStage_${w.id}`);
          const idle = document.getElementById(`compPlayroomIdle_${w.id}`);
          const title = document.getElementById(`compPlayroomTitle_${w.id}`);
          const tag = document.getElementById(`compPlayroomTag_${w.id}`);
          const bar = document.getElementById(`compPlayroomBar_${w.id}`);
          if (stage && idle && title && tag && bar) {
            title.textContent = data.name;
            tag.textContent = `คำสั่ง ${data.trigger}`;
            idle.style.display = 'none';
            stage.style.display = 'flex';
            bar.style.transition = 'none';
            bar.style.width = '100%';
            setTimeout(() => {
              bar.style.transition = `width ${data.duration || 5}s linear`;
              bar.style.width = '0%';
            }, 50);

            try {
              const audio = new Audio(data.url);
              audio.volume = (data.vol || 80) / 100;
              audio.play().catch(() => {});
            } catch (e) {}

            setTimeout(() => {
              stage.style.display = 'none';
              idle.style.display = 'flex';
            }, (data.duration || 5) * 1000);
          }
        }
      });
    }
  });
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', initStudioBusListener);
  setTimeout(initStudioBusListener, 500);
}
