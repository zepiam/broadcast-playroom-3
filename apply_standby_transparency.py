import re

path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update randomizer widget render (hidden on standby)
old_rand_render = """    if (w.type === 'randomizer') {
      return `
        <div class="composer-widget-inner widget-type-randomizer" id="compInnerRandomizer_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; align-items:center; justify-content:center; pointer-events:none;">
          <div style="background:rgba(2, 6, 23, 0.95); border:2px solid #1e293b; border-radius:18px; padding:20px 32px; text-align:center; box-shadow:0 12px 40px rgba(0,0,0,0.8); pointer-events:auto; min-width:320px;">
            <div style="font-size:12px; color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">🎲 QUICK RANDOMIZER</div>
            <div id="compRandomizerResult_${w.id}" style="font-size:28px; font-weight:800; color:#38bdf8; text-shadow:0 0 16px rgba(56,189,248,0.5); margin-bottom:8px;">สุ่มพร้อมใช้งาน</div>
            <div style="font-size:11.5px; color:#cbd5e1; background:rgba(255,255,255,0.06); padding:4px 12px; border-radius:20px; display:inline-block;">คำสั่ง !spin หรือกดสุ่มจากแผงควบคุม</div>
          </div>
        </div>
      `;
    }"""

new_rand_render = """    if (w.type === 'randomizer') {
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
    }"""

if old_rand_render in code:
    code = code.replace(old_rand_render, new_rand_render, 1)
    print("Updated randomizer render to be transparent on standby")
else:
    print("Warning: old_rand_render not found")

# 2. Update ask widget render (hidden on standby)
old_ask_render = """    if (w.type === 'ask') {
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
    }"""

new_ask_render = """    if (w.type === 'ask') {
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
    }"""

if old_ask_render in code:
    code = code.replace(old_ask_render, new_ask_render, 1)
    print("Updated ask render to be transparent on standby")
else:
    print("Warning: old_ask_render not found")

# 3. Update giveaway widget render (hidden on standby)
old_gw_render = """    if (w.type === 'giveaway') {
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
    }"""

new_gw_render = """    if (w.type === 'giveaway') {
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
    }"""

if old_gw_render in code:
    code = code.replace(old_gw_render, new_gw_render, 1)
    print("Updated giveaway render to be transparent on standby")
else:
    print("Warning: old_gw_render not found")

# 4. Update playroom widget render (hide idle banner)
old_playroom_render = """    if (w.type === 'playroom') {
      return `
        <div class="composer-widget-inner widget-type-playroom" id="compInnerPlayroom_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; align-items:center; justify-content:center; pointer-events:none;">
          <!-- Active Playroom Media Stage -->
          <div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; align-items:center; justify-content:center;">
            <div class="playroom-clip-card" id="compPlayroomCard_${w.id}" style="background:rgba(15,23,42,0.95); border:2px solid #38bdf8; border-radius:18px; padding:24px 36px; text-align:center; box-shadow:0 12px 40px rgba(0,0,0,0.8); pointer-events:auto; min-width:340px;">
              <div style="font-size:36px; margin-bottom:4px;">🎮</div>
              <div class="playroom-clip-title" id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#38bdf8; margin-bottom:6px;">Playroom Action</div>
              <div id="compPlayroomTag_${w.id}" style="font-size:11px; color:#cbd5e1; background:rgba(255,255,255,0.08); padding:3px 10px; border-radius:12px; display:inline-block;">กำลังทำงาน...</div>
              <div style="margin-top:12px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;">
                <div id="compPlayroomBar_${w.id}" style="height:100%; width:100%; background:linear-gradient(90deg, #38bdf8, #818cf8);"></div>
              </div>
            </div>
          </div>
          <!-- Idle Waiting Banner -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="background:rgba(15,23,42,0.9); border:1.5px dashed rgba(255,255,255,0.2); border-radius:12px; padding:12px 20px; font-size:12px; font-weight:600; color:#94a3b8; display:flex; align-items:center; gap:8px;">
            <span>🎮</span> <span>รอคำสั่งจากสตรีมเมอร์ หรือแชท (!play / !sfx)</span>
          </div>
        </div>
      `;
    }"""

new_playroom_render = """    if (w.type === 'playroom') {
      return `
        <div class="composer-widget-inner widget-type-playroom" id="compInnerPlayroom_${w.id}" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; align-items:center; justify-content:center; pointer-events:none;">
          <!-- Active Playroom Media Stage (Only visible when playing) -->
          <div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; align-items:center; justify-content:center;">
            <div class="playroom-clip-card" id="compPlayroomCard_${w.id}" style="background:rgba(15,23,42,0.95); border:2px solid #38bdf8; border-radius:18px; padding:24px 36px; text-align:center; box-shadow:0 12px 40px rgba(0,0,0,0.8); pointer-events:auto; min-width:340px;">
              <div style="font-size:36px; margin-bottom:4px;">🎮</div>
              <div class="playroom-clip-title" id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#38bdf8; margin-bottom:6px;">Playroom Action</div>
              <div id="compPlayroomTag_${w.id}" style="font-size:11px; color:#cbd5e1; background:rgba(255,255,255,0.08); padding:3px 10px; border-radius:12px; display:inline-block;">กำลังทำงาน...</div>
              <div style="margin-top:12px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;">
                <div id="compPlayroomBar_${w.id}" style="height:100%; width:100%; background:linear-gradient(90deg, #38bdf8, #818cf8);"></div>
              </div>
            </div>
          </div>
          <!-- Standby: idle banner is completely hidden -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="display:none !important;"></div>
        </div>
      `;
    }"""

if old_playroom_render in code:
    code = code.replace(old_playroom_render, new_playroom_render, 1)
    print("Updated playroom render to be transparent on standby")
else:
    print("Warning: old_playroom_render not found")

# 5. Add RANDOMIZER_SPIN bus handler and update ASK_UPDATE & GIVEAWAY_UPDATE in initStudioBusListener
old_bus_listeners = """  bus.on('ASK_UPDATE', (data) => {
    window._liveAskState = data;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'ask') {
          const wrapperEl = document.getElementById(`compInnerAsk_${w.id}`);
          if (wrapperEl) {
            if (data.active === false || data.phase === 'idle') {
              wrapperEl.style.opacity = '0.35';
            } else {
              wrapperEl.style.opacity = '1';
            }
          }"""

new_bus_listeners = """  bus.on('RANDOMIZER_SPIN', (data) => {
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
          }"""

if old_bus_listeners in code:
    code = code.replace(old_bus_listeners, new_bus_listeners, 1)
    print("Added RANDOMIZER_SPIN and updated ASK_UPDATE")
else:
    print("Warning: old_bus_listeners not found")

# 6. Update GIVEAWAY_UPDATE to show/hide panel on active/idle
old_gw_listener = """  bus.on('GIVEAWAY_UPDATE', (data) => {
    window._liveGwState = data;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'giveaway') {"""

new_gw_listener = """  bus.on('GIVEAWAY_UPDATE', (data) => {
    window._liveGwState = data;
    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[0];
    if (curPage) {
      curPage.widgets.forEach(w => {
        if (w.type === 'giveaway') {
          const panel = document.getElementById(`compGwPanel_${w.id}`);
          const isGwActive = data && data.active === true && (data.phase === 'running' || data.phase === 'winner');
          if (panel) {
            panel.style.display = isGwActive ? 'block' : 'none';
          }"""

if old_gw_listener in code:
    code = code.replace(old_gw_listener, new_gw_listener, 1)
    print("Updated GIVEAWAY_UPDATE display logic")
else:
    print("Warning: old_gw_listener not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer_studio.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated composer_studio.js to src and dist!")
