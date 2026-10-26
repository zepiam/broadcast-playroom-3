import os

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update composer.html to include handleRandomizerSpin, handleAskUpdate, handleGwUpdate, handlePlayroomAction
old_bc = """    // BroadcastChannel real-time sync
    if ('BroadcastChannel' in window) {
      try {
        const bus = new BroadcastChannel('bp3_system_channel');
        bus.onmessage = (e) => {
          const { event, payload } = e.data || {};
          if (event === 'CANVAS_LAYOUT_SAVED') {
            updateLayout();
          }
        };
      } catch (e) {}
    }"""

new_bc = """    function handleRandomizerSpin(data) {
      document.querySelectorAll('.widget.type-randomizer').forEach(widgetEl => {
        const wid = widgetEl.dataset.id;
        const card = document.getElementById(`compRandomizerCard_${wid}`);
        const res = document.getElementById(`compRandomizerResult_${wid}`);
        const hint = document.getElementById(`compRandomizerHint_${wid}`);
        if (card && res) {
          card.style.display = 'block';
          const items = (data.items && data.items.length) ? data.items : ['1', '2'];
          let count = 0;
          const spinInt = setInterval(() => {
            count++;
            res.textContent = items[Math.floor(Math.random() * items.length)];
            res.style.color = '#fbbf24';
            if (count > 16) {
              clearInterval(spinInt);
              res.textContent = data.winner || items[0];
              res.style.color = '#38bdf8';
              if (hint) hint.textContent = 'สุ่มสำเร็จ 🎉';
              setTimeout(() => {
                card.style.display = 'none';
              }, (data.duration || 5) * 1000);
            }
          }, 80);
        }
      });
    }

    function handleAskUpdate(data) {
      document.querySelectorAll('.widget.type-ask').forEach(widgetEl => {
        const wid = widgetEl.dataset.id;
        const panel = document.getElementById(`compAskPanel_${wid}`);
        const isAskActive = data && data.active === true && (data.phase === 'voting' || data.phase === 'ended');
        if (panel) {
          panel.style.display = isAskActive ? 'block' : 'none';
        }
        if (isAskActive) {
          const qEl = document.getElementById(`compAskQ_${wid}`);
          if (qEl) qEl.textContent = data.phase === 'ended' ? `🏆 สรุปผล: ${data.question}` : `📊 ${data.question}`;
          const timerEl = document.getElementById(`compAskTimer_${wid}`);
          if (timerEl) {
            timerEl.textContent = data.phase === 'ended' ? '🏆 สรุปผล' : (data.remainingSec != null ? `⏱ ${data.remainingSec}s` : '🗳️ โหวตสด');
          }
          const listEl = document.getElementById(`compAskChoicesList_${wid}`);
          if (listEl && data.choices) {
            listEl.innerHTML = data.choices.map(c => `
              <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
                <div style="position:absolute; inset:0; width:${c.pct}%; background:${c.color || '#38bdf8'}; opacity:0.25; border-radius:6px;"></div>
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

    function handleGwUpdate(data) {
      document.querySelectorAll('.widget.type-giveaway').forEach(widgetEl => {
        const wid = widgetEl.dataset.id;
        const panel = document.getElementById(`compGwPanel_${wid}`);
        const isGwActive = data && data.active === true && (data.phase === 'running' || data.phase === 'winner');
        if (panel) {
          panel.style.display = isGwActive ? 'block' : 'none';
        }
        if (isGwActive) {
          const pEl = document.getElementById(`compGwPrize_${wid}`);
          if (pEl) pEl.textContent = data.prize;
          const hEl = document.getElementById(`compGwHint_${wid}`);
          if (hEl) hEl.innerHTML = `พิมพ์ <strong style="color:#fb7185;">${data.code}</strong> ในแชทเพื่อเข้าร่วมสุ่ม`;
          const cEl = document.getElementById(`compGwCount_${wid}`);
          if (cEl) cEl.textContent = `ผู้เข้าร่วม: ${data.count} คน`;
          const winEl = document.getElementById(`compGwWinner_${wid}`);
          const winNameEl = document.getElementById(`compGwWinnerName_${wid}`);
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

    function handlePlayroomAction(data) {
      document.querySelectorAll('.widget.type-playroom').forEach(widgetEl => {
        const wid = widgetEl.dataset.id;
        const stage = document.getElementById(`compPlayroomStage_${wid}`);
        const idle = document.getElementById(`compPlayroomIdle_${wid}`);
        const title = document.getElementById(`compPlayroomTitle_${wid}`);
        const tag = document.getElementById(`compPlayroomTag_${wid}`);
        const bar = document.getElementById(`compPlayroomBar_${wid}`);
        if (idle) idle.style.display = 'none';
        if (stage && title && tag && bar) {
          title.textContent = data.name;
          tag.textContent = `คำสั่ง ${data.trigger}`;
          stage.style.display = 'flex';
          bar.style.transition = 'none';
          bar.style.width = '100%';
          setTimeout(() => {
            bar.style.transition = `width ${data.duration || 5}s linear`;
            bar.style.width = '0%';
          }, 50);

          setTimeout(() => {
            stage.style.display = 'none';
            if (idle) idle.style.display = 'none';
          }, (data.duration || 5) * 1000);
        }
      });
    }

    // BroadcastChannel real-time sync
    if ('BroadcastChannel' in window) {
      try {
        const bus = new BroadcastChannel('bp3_system_channel');
        bus.onmessage = (e) => {
          const { event, payload } = e.data || {};
          if (event === 'CANVAS_LAYOUT_SAVED') {
            updateLayout();
          } else if (event === 'RANDOMIZER_SPIN') {
            handleRandomizerSpin(payload);
          } else if (event === 'ASK_UPDATE') {
            window._liveAskState = payload;
            handleAskUpdate(payload);
          } else if (event === 'GIVEAWAY_UPDATE') {
            window._liveGwState = payload;
            handleGwUpdate(payload);
          } else if (event === 'PLAYROOM_ACTION') {
            handlePlayroomAction(payload);
          }
        };
      } catch (e) {}
    }"""

if old_bc in html:
    html = html.replace(old_bc, new_bc, 1)
    print("Updated composer.html broadcast channel handling")
else:
    print("Warning: old_bc not found in composer.html")

files = [
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/overlay.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/overlay.html'
]

for p in files:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {p}")
