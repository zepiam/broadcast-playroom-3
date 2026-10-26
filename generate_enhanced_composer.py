# -*- coding: utf-8 -*-
import sys

# Script to build and apply the complete composer enhancements
patch_script = r"""# -*- coding: utf-8 -*-
import os

js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. New Top Code with ComposerDemoManager and enhanced renderWidgetInnerHtml
new_top_code = '''
  // ========================================================
  // COMPOSER LIVE DEMO SIMULATION MANAGER
  // ========================================================
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

    // Default Chat Simulation
    sendChatMsg(w) {
      const feed = document.getElementById(`widget-chat-feed-${w.id}`);
      if (!feed) return;
      const msg = this.chatMockPool[Math.floor(Math.random() * this.chatMockPool.length)];
      const item = document.createElement('div');
      item.className = 'widget-chat-item';
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const bgClr = w.bgColor || '#1e1f22';
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const border = w.boxBorder ? `border: 2px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};` : '';
      const shadow = w.boxShadow ? 'box-shadow: 0 4px 14px rgba(0,0,0,0.4);' : '';
      const isTheme = w.chatMode === 'theme';

      item.style.cssText = `font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}; animation:cwc-item-pop 0.25s ease-out; margin-bottom:6px;`;
      item.innerHTML = `
        <span style="color:${msg.color}; font-weight:700;">${msg.user}:</span>
        <span style="color:${fClr};">${msg.text}</span>
      `;
      feed.appendChild(item);
      feed.scrollTop = feed.scrollHeight;

      while (feed.children.length > 10) {
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
    sendDanmakuMsg(w) {
      const feed = document.getElementById(`widget-danmaku-feed-${w.id}`);
      if (!feed) return;
      const txt = this.danmakuPool[Math.floor(Math.random() * this.danmakuPool.length)];
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
      const stroke = w.textStroke !== false ? `-webkit-text-stroke: 1.5px ${w.strokeColor || '#000000'};` : '';
      const shadow = w.textShadow !== false ? 'filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8));' : '';
      const dur = w.speed || 6;

      bullet.style.cssText = `
        top: ${topPct}%;
        left: 0;
        font-size: ${fsz}px;
        color: ${clr};
        opacity: ${w.opacity ?? 1};
        ${stroke}
        ${shadow}
        animation: danmakuBulletRun ${dur}s linear forwards;
      `;
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
      const color = w.balloonTextColor || '#0f172a';
      const radius = w.balloonRadius ?? 14;
      const fsz = w.fontSize || 15;
      const op = w.balloonOpacity ?? 0.95;

      bubble.style.cssText = `
        background: ${bg};
        color: ${color};
        padding: 10px 16px;
        border-radius: ${radius}px;
        font-size: ${fsz}px;
        font-weight: 600;
        position: relative;
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        opacity: ${op};
        animation: cwc-balloon-pop 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
        margin-bottom: 14px;
        max-width: 90%;
      `;

      bubble.innerHTML = `
        <div style="font-weight:700; font-size:12px; color:${msg.color}; margin-bottom:3px;">${msg.user}:</div>
        <div>${msg.text}</div>
        <svg style="position:absolute; bottom:-11px; left:22px; width:18px; height:12px; fill:${bg};" viewBox="0 0 18 12">
          <path d="M0 0 L18 0 L6 12 Z"/>
        </svg>
      `;
      feed.appendChild(bubble);
      feed.scrollTop = feed.scrollHeight;

      while (feed.children.length > 5) {
        feed.removeChild(feed.children[0]);
      }
    },

    // Character Chat Simulation
    triggerCharacterTalk(w) {
      const txtEl = document.getElementById(`widget-char-text-${w.id}`);
      const avatarEl = document.getElementById(`widget-char-avatar-${w.id}`);
      if (txtEl) {
        const text = this.charMockPool[Math.floor(Math.random() * this.charMockPool.length)];
        txtEl.textContent = text;
        txtEl.parentElement.style.animation = 'none';
        void txtEl.parentElement.offsetWidth;
        txtEl.parentElement.style.animation = 'cwc-balloon-pop 0.3s ease-out';
      }
      if (avatarEl) {
        avatarEl.style.transform = 'scale(1.08)';
        avatarEl.style.filter = 'drop-shadow(0 0 12px #6366f1)';
        setTimeout(() => {
          avatarEl.style.transform = 'scale(1)';
          avatarEl.style.filter = 'none';
        }, 600);
      }
    },

    // Goal Simulation
    triggerGoalPlus(w) {
      w.goalCurrent = (w.goalCurrent || 0) + 50;
      if (w.goalTarget && w.goalCurrent > w.goalTarget) {
        w.goalCurrent = w.goalTarget;
      }
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
      if (window.showToast) window.showToast(`🎉 เป้าหมายยอดเพิ่มขึ้นเป็น ${w.goalCurrent} แล้ว!`);
    },

    triggerGoalReset(w) {
      w.goalCurrent = 0;
      renderCanvasWidgets();
      saveState();
      renderWidgetCustomizerPanel(w.id);
    },

    // Viewer Simulation
    triggerViewerPulse(w) {
      const randChange = (Math.floor(Math.random() * 30) - 10);
      w.mockViewerCount = Math.max(1, (w.mockViewerCount || 1250) + randChange);
      const countEl = document.getElementById(`widget-viewer-count-${w.id}`);
      if (countEl) {
        countEl.textContent = Number(w.mockViewerCount).toLocaleString();
        countEl.style.color = randChange >= 0 ? '#22c55e' : '#ef4444';
        setTimeout(() => countEl.style.color = '#ffffff', 800);
      }
    },

    // Emote Party Simulation
    triggerEmoteParty(w) {
      const container = document.getElementById(`widget-emote-party-${w.id}`);
      if (!container) return;
      const emotes = ['🔥', '🎉', '💖', '⭐', '🚀', '👑', '🎮', '✨', '👏', '🥳'];
      for (let i = 0; i < 20; i++) {
        setTimeout(() => {
          const em = document.createElement('div');
          const emo = emotes[Math.floor(Math.random() * emotes.length)];
          const left = Math.random() * 90;
          const dur = 1.5 + Math.random() * 1.5;
          const size = 24 + Math.random() * 24;
          em.style.cssText = `
            position: absolute;
            left: ${left}%;
            bottom: 0;
            font-size: ${size}px;
            pointer-events: none;
            user-select: none;
            animation: emoteFloatUp ${dur}s ease-out forwards;
          `;
          em.textContent = emo;
          container.appendChild(em);
          setTimeout(() => em.remove(), dur * 1000);
        }, i * 60);
      }
    }
  };

  // Render inner HTML for different widget types with live styling
  function renderWidgetInnerHtml(w) {
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      const theme = w.chatTheme || 'default';

      if (mode === 'danmaku') {
        const clr = w.fontColor || '#ffffff';
        const fsz = w.fontSize || 24;
        const dur = w.speed || 6;
        const op = w.opacity ?? 1;
        const stroke = w.textStroke !== false ? `-webkit-text-stroke: 1.5px ${w.strokeColor || '#000000'};` : '';
        const shadow = w.textShadow !== false ? 'filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8));' : '';
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
            <img id="widget-char-avatar-${w.id}" src="${charImg}" style="width:110px; height:110px; object-fit:contain; flex-shrink:0; transition:all 0.3s ease;" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
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

      // Default or Theme
      const fFam = w.fontFamily || 'Kanit';
      const fSz = w.fontSize || 15;
      const fClr = w.fontColor || '#ffffff';
      const bgClr = w.bgColor || '#1e1f22';
      const bgOp = w.bgOpacity ?? 0.85;
      const radius = w.boxRadius ?? 8;
      const border = w.boxBorder ? `border: 2px solid ${w.boxBorderColor || 'rgba(255,255,255,0.2)'};` : '';
      const shadow = w.boxShadow ? 'box-shadow: 0 4px 14px rgba(0,0,0,0.4);' : '';
      const isTheme = mode === 'theme';

      return `
        <div class="composer-widget-inner widget-type-chat theme-${theme}">
          <div id="widget-chat-feed-${w.id}" style="width:100%; height:100%; overflow-y:auto; overflow-x:hidden; display:flex; flex-direction:column; gap:6px;">
            <div class="widget-chat-item" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}">
              <span style="color:#ef4444; font-weight:700;">Gamer_Pro:</span>
              <span style="color:${fClr};">สวัสดีทุกคนในไลฟ์สตรีมครับ! 🎮</span>
            </div>
            <div class="widget-chat-item" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}">
              <span style="color:#a855f7; font-weight:700;">Zack_Live:</span>
              <span style="color:${fClr};">สตรีมภาพสวยคมชัด 60fps มากครับ 🔥</span>
            </div>
            <div class="widget-chat-item" style="font-family:'${fFam}',sans-serif; font-size:${fSz}px; background:${isTheme ? 'transparent' : bgClr}; opacity:${bgOp}; border-radius:${radius}px; ${border} ${shadow}">
              <span style="color:#22c55e; font-weight:700;">Mali_TH:</span>
              <span style="color:${fClr};">ยินดีต้อนรับเพื่อนๆ ทุกคนนะครับ 💖</span>
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
      const fsz = w.fontSize ? `font-size:${w.fontSize}px;` : 'font-size:18px;';
      const clr = w.fontColor ? `color:${w.fontColor};` : 'color:#ffffff;';
      const bg = w.bgColor ? `background:${w.bgColor};` : 'background:rgba(20,25,35,0.85);';
      const text = w.text || 'ข้อความประกาศบนหน้าจอไลฟ์สตรีม ยินดีต้อนรับทุกคนครับ!';

      if (isTicker) {
        return `
          <div class="composer-widget-inner widget-type-text widget-text-ticker" style="${fsz} ${clr} ${bg}">
            <span>${text}</span>
          </div>
        `;
      }

      return `
        <div class="composer-widget-inner widget-type-text" style="${fsz} ${clr} ${bg}">
          <span>${text}</span>
        </div>
      `;
    }

    if (w.type === 'character') {
      const charImg = w.imageUrl || './assets/dock_offline_character.png';
      const charName = w.characterName || 'Replie';
      return `
        <div class="composer-widget-inner widget-type-character">
          <img class="widget-character-img" src="${charImg}" alt="Character" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Replie1'">
          <div class="widget-character-name">${charName}</div>
        </div>
      `;
    }

    if (w.type === 'webcam') {
      const borderClr = w.borderColor || '#5865f2';
      const borderW = w.borderWidth ?? 4;
      const radius = w.borderRadius ?? 8;
      const glow = w.glow ? `box-shadow: 0 0 16px ${borderClr};` : '';
      const label = w.showStreamerName ? (w.streamerName || 'Streamer LIVE') : '';

      return `
        <div class="composer-widget-inner widget-type-webcam" style="border:${borderW}px solid ${borderClr}; border-radius:${radius}px; ${glow}">
          <div class="webcam-live-indicator">
            <div class="webcam-rec-dot"></div>
            <span>REC</span>
          </div>
          <div class="widget-webcam-label">📹 เว็บแคม (${w.ratio || '16:9'})</div>
          ${label ? `<div style="position:absolute; bottom:8px; left:50%; transform:translateX(-50%); background:rgba(0,0,0,0.75); color:#fff; font-size:12px; font-weight:700; padding:2px 10px; border-radius:4px; white-space:nowrap;">${label}</div>` : ''}
          <div class="webcam-audio-vu">
            <div class="webcam-vu-bar" style="height:6px;"></div>
            <div class="webcam-vu-bar" style="height:12px;"></div>
            <div class="webcam-vu-bar" style="height:9px;"></div>
            <div class="webcam-vu-bar" style="height:14px;"></div>
            <div class="webcam-vu-bar" style="height:7px;"></div>
          </div>
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
      const count = w.mockViewerCount || 1250;
      return `
        <div class="composer-widget-inner widget-type-viewer">
          <div class="widget-viewer-dot" style="width:8px; height:8px; background:#22c55e; border-radius:50%; box-shadow:0 0 8px #22c55e; animation:pulse 1.5s infinite;"></div>
          <span style="font-size:12px; color:var(--dc-text-muted);">ยอดผู้ชมสด:</span>
          <span id="widget-viewer-count-${w.id}" style="font-weight:700; font-size:15px; color:#ffffff;">${Number(count).toLocaleString()}</span>
        </div>
      `;
    }

    if (w.type === 'emote_party') {
      return `
        <div class="composer-widget-inner widget-type-emote-party" id="widget-emote-party-${w.id}" style="position:relative; overflow:hidden;">
          <span style="font-size:24px;">🎉</span>
          <span>ปาร์ตี้อีโมทลอยสด</span>
        </div>
      `;
    }

    if (w.type === 'image') {
      return `
        <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#1e1f22; border:1px dashed rgba(255,255,255,0.2);">
          <span style="font-size:32px;">🖼️</span>
          <span style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">กรอบรูปภาพ</span>
        </div>
      `;
    }

    if (w.type === 'video') {
      return `
        <div class="composer-widget-inner widget-type-video">
          <span style="font-size:28px;">🎬</span>
          <div style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">วิดีโอลูป</div>
        </div>
      `;
    }

    if (w.type === 'alert') {
      return `
        <div class="composer-widget-inner widget-type-alert">
          <span style="font-size:24px;">🌐</span>
          <div style="font-size:12px; color:var(--dc-text-muted); margin-top:4px;">เบราว์เซอร์ URL</div>
        </div>
      `;
    }

    if (w.type === 'now_playing') {
      return `
        <div class="composer-widget-inner widget-type-now-playing">
          <span style="font-size:20px;">🎵</span>
          <div style="min-width:0;">
            <div style="font-weight:700; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${w.songTitle || 'Never Gonna Give You Up'}</div>
            <div style="font-size:11px; color:var(--dc-text-muted);">${w.artist || 'Rick Astley'}</div>
          </div>
        </div>
      `;
    }

    return `
      <div class="composer-widget-inner" style="align-items:center; justify-content:center; background:#1e1f22; border:1px solid rgba(255,255,255,0.1);">
        <span>${w.title}</span>
      </div>
    `;
  }
'''

idx_get_icon = code.find('function getWidgetIcon(type) {')
code = new_top_code + "\n  " + code[idx_get_icon:]

# 2. Patch renderCanvasWidgets resize handles for Danmaku
old_handles_snippet = """      // 8 Resize Handles
      const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
      handles.forEach(h => {
        const handle = document.createElement('div');
        handle.className = `composer-resize-handle handle-${h}`;
        handle.dataset.handle = h;
        el.appendChild(handle);
      });"""

new_handles_snippet = """      // 8 Resize Handles - Exclude if noResize or Danmaku
      const isDanmaku = w.isDanmaku || w.chatMode === 'danmaku';
      if (!w.noResize && !isDanmaku) {
        const handles = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];
        handles.forEach(h => {
          const handle = document.createElement('div');
          handle.className = `composer-resize-handle handle-${h}`;
          handle.dataset.handle = h;
          el.appendChild(handle);
        });
      } else {
        el.classList.add('widget-danmaku-full');
      }"""

if old_handles_snippet in code:
    code = code.replace(old_handles_snippet, new_handles_snippet)
    print("Replaced resize handles logic in renderCanvasWidgets")
else:
    print("Could not find old_handles_snippet")

# 3. Patch startDrag and startResize
old_start_drag = """  function startDrag(e, widget) {
    if (widget.locked) {
      selectWidget(widget.id);
      return;
    }"""

new_start_drag = """  function startDrag(e, widget) {
    if (widget.locked || widget.noDrag || widget.isDanmaku || widget.chatMode === 'danmaku') {
      selectWidget(widget.id);
      return;
    }"""

old_start_resize = """  function startResize(e, widget, handle) {
    if (widget.locked) return;"""

new_start_resize = """  function startResize(e, widget, handle) {
    if (widget.locked || widget.noResize || widget.isDanmaku || widget.chatMode === 'danmaku') return;"""

if old_start_drag in code:
    code = code.replace(old_start_drag, new_start_drag)
    print("Patched startDrag")
if old_start_resize in code:
    code = code.replace(old_start_resize, new_start_resize)
    print("Patched startResize")

# 4. Patch updateTransformInspector
old_uti = """    if (inpX) inpX.value = widget.x;
    if (inpY) inpY.value = widget.y;
    if (inpW) inpW.value = widget.width;
    if (inpH) inpH.value = widget.height;
    if (inpOp) inpOp.value = `${Math.round((widget.opacity ?? 1) * 100)}%`;"""

new_uti = """    const isDanmaku = widget.isDanmaku || widget.chatMode === 'danmaku';
    if (inpX) { inpX.value = isDanmaku ? 0 : widget.x; inpX.disabled = isDanmaku; }
    if (inpY) { inpY.value = isDanmaku ? 0 : widget.y; inpY.disabled = isDanmaku; }
    if (inpW) { inpW.value = isDanmaku ? CANVAS_WIDTH : widget.width; inpW.disabled = isDanmaku; }
    if (inpH) { inpH.value = isDanmaku ? CANVAS_HEIGHT : widget.height; inpH.disabled = isDanmaku; }
    if (inpOp) inpOp.value = isDanmaku ? `${Math.round((widget.opacity ?? 1) * 100)}% (ล็อคเต็มจอ)` : `${Math.round((widget.opacity ?? 1) * 100)}%`;"""

if old_uti in code:
    code = code.replace(old_uti, new_uti)
    print("Patched updateTransformInspector")

# 5. Patch showComposerConfirmModal, checkAndAddWidget and addWidget
idx_add = code.find('function addWidget(type')
idx_del = code.find('function deleteSelectedWidget()')

new_add_block = """  // Show Duplicate Confirmation Modal (Zero GPU Lockup)
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
        boxRadius: 8
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
      now_playing: { title: 'เพลงที่กำลังเล่น', width: 340, height: 75, songTitle: 'Never Gonna Give You Up', artist: 'Rick Astley' },
      emote_party: { title: 'ปาร์ตี้อีโมทลอย', width: 300, height: 200 }
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

    const newWidget = {
      id: `w-${type}-${Date.now()}`,
      type: type,
      title: preset.title,
      x: (preset.isDanmaku ? 0 : Math.round(CANVAS_WIDTH / 2 - preset.width / 2)),
      y: (preset.isDanmaku ? 0 : Math.round(CANVAS_HEIGHT / 2 - preset.height / 2)),
      width: preset.width,
      height: preset.height,
      z: page.widgets.length + 1,
      opacity: 1,
      locked: false,
      hidden: false,
      text: preset.text || '',
      ...preset
    };

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
  
  """

if idx_add != -1 and idx_del != -1:
    code = code[:idx_add] + new_add_block + code[idx_del:]
    print("Replaced addWidget and added modal check successfully")
else:
    print("Could not find addWidget or deleteSelectedWidget")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved intermediate code")
"""

with open(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\patch_part1.py', 'w', encoding='utf-8') as f:
    f.write(patch_script)

print("Wrote patch_part1.py")
