# -*- coding: utf-8 -*-
import sys, io

file_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. NEW COMPOSER DEMO MANAGER
new_demo_manager = """  const ComposerDemoManager = {
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
      const ticker = document.querySelector(`#widget-${w.id} .viewer-ticker`);
      if (ticker) {
        updateNumberTicker(ticker, target);
      }
      renderLayersList();
    },

    triggerViewerAdd(w, delta = 50) {
      const current = w.mockViewerCount || 1250;
      const target = current + delta;
      w.mockViewerCount = target;
      const ticker = document.querySelector(`#widget-${w.id} .viewer-ticker`);
      if (ticker) {
        updateNumberTicker(ticker, target);
      }
      renderLayersList();
    },

    triggerViewerSub(w, delta = 30) {
      const current = w.mockViewerCount || 1250;
      const target = Math.max(0, current - delta);
      w.mockViewerCount = target;
      const ticker = document.querySelector(`#widget-${w.id} .viewer-ticker`);
      if (ticker) {
        updateNumberTicker(ticker, target);
      }
      renderLayersList();
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

    // Now Playing Simulation
    triggerNowPlayingNext(w) {
      const songs = [
        { title: 'Stay With Me', artist: 'Miki Matsubara' },
        { title: 'Blinding Lights', artist: 'The Weeknd' },
        { title: 'Cruel Summer', artist: 'Taylor Swift' },
        { title: 'Specialz', artist: 'King Gnu' },
        { title: 'アイドル (Idol)', artist: 'YOASOBI' }
      ];
      const nextSong = songs[Math.floor(Math.random() * songs.length)];
      w.songTitle = nextSong.title;
      w.artist = nextSong.artist;
      renderCanvasWidgets();
      renderWidgetCustomizerPanel(w.id);
      saveState();
    }
  };"""

# 2. NEW RENDER WIDGET INNER HTML
new_render_inner_html = """  // Render Inner HTML according to Widget Type
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
      const isTheme = mode === 'theme';
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
      const dir = w.direction === 'top' ? 'column' : 'column-reverse';
      const justify = w.direction === 'top' ? 'flex-start' : 'flex-end';
      const spacing = w.msgSpacing ?? 6;

      return `
        <div class="composer-widget-inner widget-type-chat theme-${theme}">
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
      let timeStr = '';
      if (w.clockFormat === '12') {
        let hrs = now.getHours();
        const ampm = hrs >= 12 ? 'PM' : 'AM';
        hrs = hrs % 12 || 12;
        const mins = String(now.getMinutes()).padStart(2, '0');
        const secs = String(now.getSeconds()).padStart(2, '0');
        timeStr = w.showSeconds === false ? `${hrs}:${mins} ${ampm}` : `${hrs}:${mins}:${secs} ${ampm}`;
      } else {
        const hrs = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        const secs = String(now.getSeconds()).padStart(2, '0');
        timeStr = w.showSeconds === false ? `${hrs}:${mins}` : `${hrs}:${mins}:${secs}`;
      }

      const clr = w.fontColor || '';
      const fsz = w.fontSize ? `${w.fontSize}px` : '';
      const themeClass = w.clockTheme ? `clock-theme-${w.clockTheme}` : 'clock-theme-cyberpunk';

      return `
        <div class="composer-widget-inner widget-type-clock ${themeClass}" style="${clr ? 'color:' + clr + ';' : ''} ${fsz ? 'font-size:' + fsz + ';' : ''}">
          <div class="widget-clock-time">${timeStr}</div>
        </div>
      `;
    }

    if (w.type === 'text') {
      const isTicker = w.textMode === 'ticker';
      const fsz = w.fontSize || 18;
      const clr = w.fontColor || '#ffffff';
      const bg = w.bgColor || 'transparent';
      const text = w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม ยินดีต้อนรับทุกคนครับ!';
      const strokeCss = w.textStroke ? `-webkit-text-stroke:${w.textStrokeWidth || 2}px ${w.strokeColor || '#000000'}; paint-order:stroke fill;` : '';
      const shadowCss = w.textShadow ? `text-shadow:0 1px ${w.textShadowBlur || 3}px ${w.textShadowColor || '#000000'};` : '';
      const fFam = w.fontFamily || 'Kanit';
      const dur = w.marqueeSpeed || 15;

      if (isTicker) {
        return `
          <div class="composer-widget-inner widget-type-text widget-text-ticker" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss}; --marquee-duration:${dur}s;">
            <span>${text}</span>
          </div>
        `;
      }

      return `
        <div class="composer-widget-inner widget-type-text" style="font-family:'${fFam}',sans-serif; font-size:${fsz}px; color:${clr}; background:${bg}; ${strokeCss} ${shadowCss};">
          <span>${text}</span>
        </div>
      `;
    }

    if (w.type === 'character') {
      const charImg = w.imageUrl || './assets/dock_offline_character.png';
      const charName = w.characterName || 'Replie';
      return `
        <div class="composer-widget-inner widget-type-character">
          <img class="widget-character-img" src="${charImg}" alt="Character" draggable="false" style="pointer-events:none; -webkit-user-drag:none;" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
          <div class="widget-character-name">${charName}</div>
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
        const mockPlats = [
          { name: 'youtube', icon: '🔴', count: Math.round(count * 0.6) },
          { name: 'twitch', icon: '🟣', count: Math.round(count * 0.4) }
        ];
        chipsHtml = mockPlats.map(p => `
          <span class="viewer-chip" data-platform="${p.name}" style="font-family:'${fFam}',sans-serif; font-size:${Math.round(fsz * 0.9)}px; color:${clr}; ${strokeCss} ${shadowCss}">
            ${showIcon ? `<span style="font-size:${iconSize}px;">${p.icon}</span>` : ''}
            <span>${p.count.toLocaleString()}</span>
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
      const isTrans = w.npTransparent !== false;
      const bgStyle = isTrans ? 'background:transparent;' : `background:${w.npBgColor || '#1a1a2e'}; opacity:${w.npBgOpacity ?? 0.95};`;
      const artRadius = w.npArtRadius ?? 6;
      const artSize = w.npArtSize ?? 44;
      const accent = w.npAccentColor || '#10b981';
      const textClr = w.npTextColor || '#ffffff';

      return `
        <div class="composer-widget-inner widget-type-now-playing" style="${bgStyle} border-radius:${w.npRadius ?? 8}px; padding:8px 12px; display:flex; align-items:center; gap:10px; width:100%; height:100%; box-sizing:border-box;">
          ${w.npShowArt !== false ? `<div style="width:${artSize}px; height:${artSize}px; border-radius:${artRadius}px; background:#334155; overflow:hidden; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:20px;">🎵</div>` : ''}
          <div style="flex:1; min-width:0;">
            <div style="font-weight:700; font-size:${w.npFontSize || 13}px; color:${textClr}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${w.songTitle || 'Never Gonna Give You Up'}</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.7);">${w.artist || 'Rick Astley'}</div>
            ${w.npShowProgress !== false ? `<div style="width:100%; height:3px; background:rgba(255,255,255,0.2); border-radius:2px; margin-top:4px;"><div style="width:45%; height:100%; background:${accent}; border-radius:2px;"></div></div>` : ''}
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:transparent; border:none;">
        <span>${w.title}</span>
      </div>
    `;
  }"""

# Replace ComposerDemoManager
s_dm = code.find('  const ComposerDemoManager = {')
e_dm = code.find('  // Load saved state from localStorage\n  function loadSavedState() {', s_dm)
if s_dm != -1 and e_dm != -1:
    code = code[:s_dm] + new_demo_manager + "\n\n" + code[e_dm:]
    print("Replaced ComposerDemoManager successfully.")
else:
    print("ERROR: ComposerDemoManager boundaries not found!")

# Replace renderWidgetInnerHtml
s_inner = code.find('  // Render Inner HTML according to Widget Type\n  function renderWidgetInnerHtml(w) {')
e_inner = code.find('  // Select Widget (Does NOT open or close drawer automatically)', s_inner)
if s_inner != -1 and e_inner != -1:
    code = code[:s_inner] + new_render_inner_html + "\n\n" + code[e_inner:]
    print("Replaced renderWidgetInnerHtml successfully.")
else:
    print("ERROR: renderWidgetInnerHtml boundaries not found!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Part 2 written.")
