# -*- coding: utf-8 -*-
import sys

js_file = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_file, 'r', encoding='utf-8') as f:
    code = f.read()

# ========================================================
# 1. COMPOSER DEMO MANAGER CODE
# ========================================================
demo_manager_code = """
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
"""

print("Defined ComposerDemoManager successfully")
