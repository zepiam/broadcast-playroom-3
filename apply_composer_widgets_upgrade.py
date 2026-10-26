import os
import re

composer_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js"

with open(composer_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace character, ask, giveaway, playroom rendering
old_block_pattern = re.compile(
    r"if \(w\.type === 'character'\) \{.*?if \(w\.type === 'goal' \|\| w\.type === 'donate_goal'\) \{",
    re.DOTALL
)

new_block = """if (w.type === 'character') {
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
      const q = liveAsk.question || w.askQuestion || 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?';
      const choices = liveAsk.choices || [
        { label: 'A', text: (w.askChoices && w.askChoices[0]) || 'Valorant', pct: 65, votes: 130, color: '#38bdf8' },
        { label: 'B', text: (w.askChoices && w.askChoices[1]) || 'ROV / Garena', pct: 35, votes: 70, color: '#c084fc' }
      ];

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
        <div class="composer-widget-inner widget-type-ask" id="compInnerAsk_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center;">
          <div class="ask-panel" style="background:rgba(15, 23, 42, 0.92); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1.5px solid rgba(56, 189, 248, 0.35); border-radius:12px; padding:12px 16px; box-shadow:0 8px 30px rgba(0,0,0,0.5);">
            <div style="font-weight:700; font-size:14px; color:#38bdf8; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
              <span id="compAskQ_${w.id}">📊 ${q}</span>
              <span id="compAskTimer_${w.id}" style="font-size:11px; color:#94a3b8; background:rgba(255,255,255,0.08); padding:2px 8px; border-radius:4px;">⏱ 45s</span>
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
      const prize = liveGw.prize || w.prizeTitle || 'รางวัลพิเศษประจำสตรีม';
      const code = liveGw.code || '#join';
      const count = liveGw.count ?? 148;
      const winner = liveGw.winner;

      return `
        <div class="composer-widget-inner widget-type-giveaway" id="compInnerGw_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center;">
          <div style="background:rgba(15, 23, 42, 0.92); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1.5px solid rgba(244, 63, 94, 0.4); border-radius:14px; padding:14px 18px; text-align:center; box-shadow:0 8px 30px rgba(0,0,0,0.5);">
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
              <span style="color:#fb7185; font-weight:700;">นับถอยหลัง: 24s</span>
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'playroom') {
      return `
        <div class="composer-widget-inner widget-type-playroom" id="compInnerPlayroom_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; position:relative; display:flex; align-items:center; justify-content:center;">
          <!-- Active Playroom Media Stage -->
          <div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; position:absolute; inset:0; z-index:10; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div class="playroom-clip-card" id="compPlayroomCard_${w.id}" style="background:rgba(15,23,42,0.95); border:2px solid #a855f7; border-radius:16px; padding:16px 22px; box-shadow:0 12px 40px rgba(0,0,0,0.8); text-align:center; max-width:92%; transition:transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);">
              <div style="font-size:36px; margin-bottom:4px;">🎮</div>
              <div id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#c084fc; margin-bottom:4px;">เซียมซี: ดวงมหาเฮง</div>
              <div id="compPlayroomTag_${w.id}" style="font-size:11px; color:#cbd5e1; background:rgba(255,255,255,0.08); padding:3px 10px; border-radius:20px; display:inline-block;">คำสั่ง !fortune</div>
              <div style="margin-top:12px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;">
                <div id="compPlayroomBar_${w.id}" style="height:100%; width:100%; background:linear-gradient(90deg, #a855f7, #ec4899); transition:width linear;"></div>
              </div>
            </div>
          </div>
          <!-- Idle Waiting Banner -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="background:rgba(15,23,42,0.85); border:1.5px dashed rgba(168,85,247,0.45); border-radius:14px; padding:14px 20px; text-align:center; color:#c084fc;">
            <div style="font-size:24px; margin-bottom:4px;">🎮</div>
            <div style="font-size:13px; font-weight:700;">Playroom Interactive Overlay</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:2px;">รอคำสั่งจากแชทสด หรือยิงคลิปจากแผง Playroom Studio</div>
          </div>
        </div>
      `;
    }

    if (w.type === 'goal' || w.type === 'donate_goal') {"""

match = old_block_pattern.search(code)
if match:
    code = code[:match.start()] + new_block + code[match.end():]
    print("Replaced widget render blocks successfully!")
else:
    print("WARNING: old_block_pattern did not match!")

# Append initStudioBusListener if not already present
bus_listener_code = """
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

  bus.on('ASK_UPDATE', (data) => {
    window._liveAskState = data;
    const curPage = window.composerStudioState?.pages?.[window.composerStudioState.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'ask') {
          const qEl = document.getElementById(`compAskQ_${w.id}`);
          if (qEl) qEl.textContent = `📊 ${data.question}`;
          const listEl = document.getElementById(`compAskChoicesList_${w.id}`);
          if (listEl && data.choices) {
            listEl.innerHTML = data.choices.map(c => `
              <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
                <div style="position:absolute; inset:0; width:${c.pct}%; background:${c.color || '#38bdf8'}; opacity:0.25; border-radius:6px; transition:width 0.4s ease;"></div>
                <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
                  <span>${c.label}: ${c.text}</span>
                  <span style="color:${c.color || '#38bdf8'}; font-weight:700;">${c.pct}% (${c.votes || 0})</span>
                </div>
              </div>
            `).join('');
          }
        }
      });
    }
  });

  bus.on('GIVEAWAY_UPDATE', (data) => {
    window._liveGwState = data;
    const curPage = window.composerStudioState?.pages?.[window.composerStudioState.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'giveaway') {
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
    const curPage = window.composerStudioState?.pages?.[window.composerStudioState.activePageIndex];
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
    const curPage = window.composerStudioState?.pages?.[window.composerStudioState.activePageIndex];
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
"""

if "function initStudioBusListener()" not in code:
    code += "\n" + bus_listener_code
    print("Added initStudioBusListener to composer_studio.js!")

with open(composer_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated composer_studio.js successfully!")
