import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Patch popout bridging
popout_start = -1
popout_end = -1
for i, l in enumerate(lines):
    if '// Forward all global helper functions and properties' in l:
        popout_start = i
    if popout_start != -1 and 'Could not mirror window functions to popup' in l:
        # Find closing brace of try/catch
        for j in range(i, i+10):
            if '}' in lines[j]:
                popout_end = j + 1
                break
        break

print(f"Popout mirror lines: {popout_start} to {popout_end}")

new_popout_code = """      // Forward all global helper functions, bus, and state objects from parent window to popup
      try {
        pop.opener = window;
        pop.parentWindow = window;
        pop.BP3_BUS = window.BP3_BUS;
        pop.composerStudio = window.composerStudio;
        pop.ComposerStudio = window.ComposerStudio;

        // Bridge state objects via getters/setters
        const bridgeKeys = [
          'BP3_BUS', '_askPollState', '_liveAskState', '_askVotes', '_askPollActive',
          '_liveGwState', '_gwState', '_randomizerState', 'ComposerStudio', 'composerStudio'
        ];
        bridgeKeys.forEach(k => {
          try {
            Object.defineProperty(pop, k, {
              get: () => window[k],
              set: (val) => { window[k] = val; },
              configurable: true,
              enumerable: true
            });
          } catch(e) {
            pop[k] = window[k];
          }
        });

        const copyProps = (src) => {
          for (const key of Object.getOwnPropertyNames(src)) {
            if (typeof src[key] === 'function' && !(key in pop)) {
              try { pop[key] = src[key].bind(window); } catch (e) { pop[key] = src[key]; }
            }
          }
        };
        copyProps(window);
        for (const key in window) {
          if (typeof window[key] === 'function' && !(key in pop)) {
            try { pop[key] = window[key].bind(window); } catch (e) { pop[key] = window[key]; }
          }
        }
      } catch (e) {
        console.warn('Could not mirror window functions to popup:', e);
      }
"""

if popout_start != -1 and popout_end != -1:
    lines[popout_start:popout_end] = [new_popout_code]
    print("Replaced popout mirroring section")

# 2. Patch ASK system
ask_start = -1
ask_end = -1
for i, l in enumerate(lines):
    if '// REAL ASK POLL SYSTEM' in l:
        ask_start = i
    if ask_start != -1 and 'function renderAskPreviewGraph' in l:
        # find end of renderAskPreviewGraph
        brace_count = 0
        started = False
        for j in range(i, min(i+120, len(lines))):
            if '{' in lines[j]:
                brace_count += lines[j].count('{')
                started = True
            if '}' in lines[j]:
                brace_count -= lines[j].count('}')
            if started and brace_count == 0:
                ask_end = j + 1
                break
        break

print(f"ASK system lines: {ask_start} to {ask_end}")

new_ask_code = """    // ----------------------------------------------------
    // REAL ASK POLL SYSTEM (FULL LIFECYCLE: IDLE -> VOTING -> PAUSED -> ENDED)
    // ----------------------------------------------------
    function getAskDoc() {
      if (window._popoutWindows && window._popoutWindows['ask'] && !window._popoutWindows['ask'].closed) {
        try {
          if (window._popoutWindows['ask'].document) return window._popoutWindows['ask'].document;
        } catch(e) {}
      }
      return document;
    }

    function getAskEl(id) {
      let el = null;
      if (window._popoutWindows && window._popoutWindows['ask'] && !window._popoutWindows['ask'].closed) {
        try {
          el = window._popoutWindows['ask'].document.getElementById(id);
        } catch(e) {}
      }
      if (!el) el = document.getElementById(id);
      return el;
    }

    function queryAskAll(selector) {
      let list = null;
      if (window._popoutWindows && window._popoutWindows['ask'] && !window._popoutWindows['ask'].closed) {
        try {
          list = window._popoutWindows['ask'].document.querySelectorAll(selector);
        } catch(e) {}
      }
      if (!list || list.length === 0) list = document.querySelectorAll(selector);
      return list;
    }

    window._askPollState = {
      phase: 'idle', // 'idle' | 'voting' | 'paused' | 'ended'
      question: '',
      choices: [],
      answerMode: 'letters',
      voters: {},
      durationSec: 30,
      remainingSec: 30,
      timerId: null,
      winner: null
    };

    function startAskPoll() {
      const qInput = getAskEl('askQuestion');
      const q = (qInput?.value || '').trim() || 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?';

      const rows = queryAskAll('#askChoicesList .ask-choice-row');
      if (!rows || rows.length < 2) {
        alert('กรุณามีตัวเลือกอย่างน้อย 2 ตัวเลือกครับ');
        return;
      }

      const modeSelect = getAskEl('askAnswerMode');
      const answerMode = modeSelect ? modeSelect.value : 'letters';

      const durSelect = getAskEl('askDurationSelect');
      const durVal = durSelect ? parseInt(durSelect.value) : 30;
      const durationSec = isNaN(durVal) || durVal <= 0 ? null : durVal;

      const colors = ['#38bdf8', '#34d399', '#fbbf24', '#f43f5e', '#a855f7', '#ec4899'];
      const choices = [];
      rows.forEach((row, i) => {
        const defaultTag = answerMode === 'numbers' ? String(i + 1) : String.fromCharCode(65 + i);
        const label = row.querySelector('.choice-tag')?.textContent || defaultTag;
        const text = (row.querySelector('input')?.value || '').trim() || `ตัวเลือก ${label}`;
        choices.push({
          label,
          text,
          key: (answerMode === 'numbers' ? String(i + 1) : String.fromCharCode(65 + i)).toUpperCase(),
          votes: 0,
          pct: 0,
          color: colors[i % colors.length]
        });
      });

      if (window._askPollState && window._askPollState.timerId) {
        clearInterval(window._askPollState.timerId);
      }

      window._askVotes = {};
      window._askPollState = {
        phase: 'voting',
        question: q,
        choices,
        answerMode,
        voters: {},
        durationSec,
        remainingSec: durationSec,
        timerId: null,
        winner: null
      };
      window._askPollActive = true;

      // Start countdown timer if duration specified
      if (durationSec) {
        window._askPollState.timerId = setInterval(() => {
          if (!window._askPollState || window._askPollState.phase !== 'voting') return;
          window._askPollState.remainingSec--;
          updateAskTimerDisplay();
          emitAskState();
          if (window._askPollState.remainingSec <= 0) {
            endAskPoll();
          }
        }, 1000);
      }

      // Update UI & Broadcast
      updateAskUIState('voting');
      emitAskState();

      // Announce in live chat
      const choiceHints = choices.map(c => `${c.label}=${c.text}`).join(' | ');
      appendAskChatSystemMessage(`🗳️ [เริ่มเปิดโหวตสด] "${q}" ➔ พิมพ์ ${choices.map(c => c.label).join('/')} ในแชทเพื่อโหวต (${choiceHints})`);
      playPlayroomSynthesizer('!poll_start', 0.8);
      if (window.showToast) window.showToast('🚀 เริ่มเปิดโหวตสดและส่งขึ้นจอ OBS เรียบร้อยแล้ว');
    }

    function togglePauseAskPoll() {
      if (!window._askPollState) return;
      if (window._askPollState.phase === 'voting') {
        window._askPollState.phase = 'paused';
        updateAskUIState('paused');
        emitAskState();
      } else if (window._askPollState.phase === 'paused') {
        window._askPollState.phase = 'voting';
        updateAskUIState('voting');
        emitAskState();
      }
    }

    function endAskPoll() {
      if (window._askPollState && window._askPollState.timerId) {
        clearInterval(window._askPollState.timerId);
        window._askPollState.timerId = null;
      }
      if (!window._askPollState) return;
      window._askPollState.phase = 'ended';
      window._askPollActive = false;

      // Determine winner
      const choices = window._askPollState.choices || [];
      let maxVotes = -1;
      let winner = null;
      choices.forEach(c => {
        if (c.votes > maxVotes) {
          maxVotes = c.votes;
          winner = c;
        }
      });
      window._askPollState.winner = winner;

      updateAskUIState('ended');
      emitAskState();

      // Announce in live chat
      const totalVoters = Object.keys(window._askPollState.voters || {}).length;
      if (winner && maxVotes > 0) {
        appendAskChatSystemMessage(`🏆 [สรุปผลโพล] "${window._askPollState.question}" ➔ อันดับ 1: ${winner.label}. ${winner.text} (${winner.votes} โหวต, ${winner.pct}%) | รวมคนโหวตทั้งหมด ${totalVoters} คน`);
      } else {
        appendAskChatSystemMessage(`📊 [สรุปผลโพล] "${window._askPollState.question}" ➔ จบการโหวตแล้ว (ยังไม่มีคะแนนโหวต)`);
      }
      playPlayroomSynthesizer('!gacha', 0.9);
      if (window.showToast) window.showToast('🏆 จบการโหวตและแสดงผลสรุปบนจอแล้ว');
    }

    function closeAskOverlay() {
      if (window._askPollState && window._askPollState.timerId) {
        clearInterval(window._askPollState.timerId);
        window._askPollState.timerId = null;
      }
      if (window._askPollState) {
        window._askPollState.phase = 'idle';
      }
      window._askPollActive = false;
      window._liveAskState = { active: false, phase: 'idle', isLive: false };

      // 1. Emit via BP3_BUS
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('ASK_UPDATE', window._liveAskState);
      }
      // 2. Direct BroadcastChannel failsafe to OBS
      if ('BroadcastChannel' in window) {
        try {
          const bc = new BroadcastChannel('bp3_system_channel');
          bc.postMessage({ event: 'ASK_UPDATE', payload: window._liveAskState });
        } catch(e) {}
      }

      updateAskUIState('idle');
      renderAskPreviewGraph(window._askPollState?.choices || [], 0);
      if (window.showToast) window.showToast('✕ ปิดผลโพลออกจากหน้าจอ Overlay เรียบร้อยแล้ว');
    }

    function resetAskPoll() {
      // 1. Immediately close and clear from overlay
      closeAskOverlay();

      // 2. Clear previous votes and reset choices
      if (window._askPollState) {
        window._askPollState.phase = 'idle';
        window._askPollState.winner = null;
        window._askPollState.voters = {};
        if (window._askPollState.choices) {
          window._askPollState.choices.forEach(c => {
            c.votes = 0;
            c.pct = 0;
          });
        }
      }
      window._askVotes = {};

      // 3. Make sure inputs are re-enabled
      const qInput = getAskEl('askQuestion');
      const modeSelect = getAskEl('askAnswerMode');
      const durSelect = getAskEl('askDurationSelect');
      if (qInput) qInput.disabled = false;
      if (modeSelect) modeSelect.disabled = false;
      if (durSelect) durSelect.disabled = false;

      updateAskUIState('idle');
      renderAskPreviewGraph(window._askPollState?.choices || [], 0);
      if (window.showToast) window.showToast('🔄 รีเซ็ตโพลเรียบร้อยแล้ว พร้อมเริ่มโพลใหม่ครับ');
    }

    function updateAskTimerDisplay() {
      const badge = getAskEl('askTimerBadge');
      if (badge && window._askPollState && window._askPollState.remainingSec != null) {
        badge.textContent = `⏱ ${window._askPollState.remainingSec}s`;
        badge.style.color = window._askPollState.remainingSec <= 10 ? '#f43f5e' : '#fbbf24';
      }
    }

    function updateAskUIState(phase) {
      const banner = getAskEl('askLiveStatusBanner');
      const dot = getAskEl('askStatusDot');
      const text = getAskEl('askStatusText');
      const meta = getAskEl('askStatusMeta');

      const footerIdle = getAskEl('askFooterIdle');
      const footerVoting = getAskEl('askFooterVoting');
      const footerEnded = getAskEl('askFooterEnded');
      const btnPause = getAskEl('btnAskPause');

      const qInput = getAskEl('askQuestion');
      const modeSelect = getAskEl('askAnswerMode');
      const durSelect = getAskEl('askDurationSelect');

      if (footerIdle) footerIdle.style.display = (phase === 'idle') ? 'flex' : 'none';
      if (footerVoting) footerVoting.style.display = (phase === 'voting' || phase === 'paused') ? 'flex' : 'none';
      if (footerEnded) footerEnded.style.display = (phase === 'ended') ? 'flex' : 'none';

      // Toggle inputs editable
      const isEditable = (phase === 'idle');
      if (qInput) qInput.disabled = !isEditable;
      if (modeSelect) modeSelect.disabled = !isEditable;
      if (durSelect) durSelect.disabled = !isEditable;

      if (phase === 'idle') {
        if (banner) {
          banner.style.background = '#162032';
          banner.style.borderColor = '#1e293b';
        }
        if (dot) dot.style.background = '#64748b';
        if (text) text.textContent = '⚪ สถานะ: พร้อมเริ่มโพลใหม่';
        if (meta) meta.innerHTML = '<span style="font-size:11.5px; color:#64748b;">กรอกคำถามและตัวเลือก แล้วกดปุ่ม "🚀 เริ่มเปิดโหวตขึ้นจอ OBS"</span>';
      } else if (phase === 'voting') {
        if (banner) {
          banner.style.background = 'rgba(16, 185, 129, 0.12)';
          banner.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        }
        if (dot) dot.style.background = '#10b981';
        if (text) text.textContent = '🟢 กำลังเปิดโหวตสด...';
        const timerTxt = window._askPollState?.remainingSec != null ? `⏱ ${window._askPollState.remainingSec}s` : '⏱ ไม่จำกัดเวลา';
        const totalVoters = Object.keys(window._askPollState?.voters || {}).length;
        if (meta) meta.innerHTML = `
          <span id="askTimerBadge" style="font-size:12px; font-weight:700; color:#fbbf24; background:rgba(251,191,36,0.15); padding:2px 8px; border-radius:4px;">${timerTxt}</span>
          <span id="askLiveVotersCount" style="font-size:12px; font-weight:600; color:#94a3b8;">👥 ${totalVoters} คน</span>
        `;
        if (btnPause) {
          btnPause.textContent = '⏸️ พักโหวต';
          btnPause.style.color = '#fbbf24';
        }
      } else if (phase === 'paused') {
        if (banner) {
          banner.style.background = 'rgba(245, 158, 11, 0.12)';
          banner.style.borderColor = 'rgba(245, 158, 11, 0.4)';
        }
        if (dot) dot.style.background = '#f59e0b';
        if (text) text.textContent = '⏸️ พักการรับโหวตชั่วคราว';
        if (meta) meta.innerHTML = '<span style="font-size:12px; color:#fbbf24; font-weight:600;">(เวลาและคะแนนถูกหยุดชั่วคราว)</span>';
        if (btnPause) {
          btnPause.textContent = '▶ รับโหวตต่อ';
          btnPause.style.color = '#34d399';
        }
      } else if (phase === 'ended') {
        if (banner) {
          banner.style.background = 'rgba(124, 58, 237, 0.15)';
          banner.style.borderColor = 'rgba(124, 58, 237, 0.4)';
        }
        if (dot) dot.style.background = '#a855f7';
        if (text) text.textContent = '🏆 จบการโหวตแล้ว — แสดงผลสรุปบนจอ OBS';
        const winner = window._askPollState?.winner;
        if (meta) {
          if (winner && winner.votes > 0) {
            meta.innerHTML = `<span style="font-size:12.5px; font-weight:700; color:#34d399;">อันดับ 1: 👑 ${winner.label}. ${winner.text} (${winner.votes} โหวต)</span>`;
          } else {
            meta.innerHTML = '<span style="font-size:12px; color:#94a3b8;">(ไม่มีคะแนนโหวต)</span>';
          }
        }
      }
    }

    function emitAskState() {
      const st = window._askPollState || {};
      const qInput = getAskEl('askQuestion');
      const q = st.question || qInput?.value || 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?';
      const choices = st.choices || [];
      let totalVotes = 0;
      choices.forEach(c => { totalVotes += (c.votes || 0); });
      choices.forEach(c => {
        c.pct = totalVotes > 0 ? Math.round((c.votes / totalVotes) * 100) : 0;
      });

      window._liveAskState = {
        active: st.phase !== 'idle',
        phase: st.phase || 'idle',
        question: q,
        choices,
        winner: st.winner,
        totalVotes,
        remainingSec: st.remainingSec,
        isLive: st.phase !== 'idle'
      };

      // Render live preview graph in win-ask
      renderAskPreviewGraph(choices, totalVotes);

      if (window.BP3_BUS) {
        window.BP3_BUS.emit('ASK_UPDATE', window._liveAskState);
      }
      if ('BroadcastChannel' in window) {
        try {
          const bc = new BroadcastChannel('bp3_system_channel');
          bc.postMessage({ event: 'ASK_UPDATE', payload: window._liveAskState });
        } catch(e) {}
      }
    }

    function renderAskPreviewGraph(choices, totalVotes) {
      const container = getAskEl('askLiveGraphContainer');
      const lblTotal = getAskEl('lblAskTotalVotes');
      if (lblTotal) lblTotal.textContent = `ยอดโหวตรวม: ${totalVotes} โหวต`;
      if (!container) return;

      const isEnded = window._askPollState && window._askPollState.phase === 'ended';
      const displayChoices = isEnded ? [...choices].sort((a,b) => (b.votes || 0) - (a.votes || 0)) : choices;

      if (totalVotes === 0) {
        container.innerHTML = displayChoices.map(c => `
          <div>
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
              <span><strong>${c.label}:</strong> ${c.text}</span><strong>0% (0 โหวต)</strong>
            </div>
            <div style="background:rgba(255,255,255,0.06); height:8px; border-radius:4px; overflow:hidden;">
              <div style="width:0%; height:100%; background:${c.color || '#38bdf8'}; transition:width 0.3s ease;"></div>
            </div>
          </div>
        `).join('');
      } else {
        container.innerHTML = displayChoices.map((c, idx) => {
          const isWinner = isEnded && idx === 0 && (c.votes || 0) > 0;
          return `
          <div>
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
              <span>${isWinner ? '👑 ' : ''}<strong>${c.label}:</strong> ${c.text}</span>
              <strong style="color:${isWinner ? '#fbbf24' : (c.color || '#38bdf8')};">${c.pct}% (${c.votes} โหวต)</strong>
            </div>
            <div style="background:rgba(255,255,255,0.06); height:8px; border-radius:4px; overflow:hidden;">
              <div style="width:${c.pct}%; height:100%; background:${isWinner ? 'linear-gradient(90deg, #f59e0b, #fbbf24)' : (c.color || '#38bdf8')}; transition:width 0.3s ease;"></div>
            </div>
          </div>
        `;
        }).join('');
      }
    }
"""

if ask_start != -1 and ask_end != -1:
    lines[ask_start:ask_end] = [new_ask_code]
    print("Replaced ASK system section")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Saved updated index.html to src and dist successfully!")
