import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace injectIncomingChat to hook up real chatters, real ask votes, real giveaway entries, and real replie commands
target_inject = text.find('function injectIncomingChat(msg) {')
assert target_inject != -1, "injectIncomingChat not found"
target_inject_end = text.find('function speakTextViaWebSpeech(', target_inject)

new_inject_and_tools = """// Real Global State for Interactive Live Tools
    window._activeChattersSet = new Set();
    window._askPollActive = true;
    window._askVotes = {}; // username -> choiceIndex
    window._gwParticipants = []; // array of { id, username, platform, time }
    window._isGwCodeBroadcasting = true;
    window._replieCommands = {
      '!hi': { text: 'สวัสดีครับทุกคน! ยินดีต้อนรับสู่สตรีมครับ ✨', emotion: 'happy' },
      '!gg': { text: 'GG WP ครับทุกคน! เก่งมากๆ สุดยอดเลย 🏆', emotion: 'cheer' },
      '!bye': { text: 'บ๊ายบายครับทุกคน แล้วพบกันใหม่รอบหน้านะครับ 👋', emotion: 'wave' },
      '!cheer': { text: 'สู้ๆ นะครับ ขอบคุณสำหรับกำลังใจครับผม! 🎉', emotion: 'cheer' }
    };

    function injectIncomingChat(msg) {
      const effectiveName = getEffectiveAuthorName(msg.username);
      registerUserToRoster(msg);
      
      // Track real active chatters
      window._activeChattersSet.add(effectiveName);

      const chatList = document.getElementById('chatList');
      if (chatList) {
        const row = document.createElement('div');
        row.className = 'chat-row';
        row.innerHTML = `
          <div class="chat-avatar" onclick="openAuthorModal('${msg.username}', '${msg.platform}', '${msg.avatar}', '${effectiveName}', ${msg.isVip})">
            <img class="avatar-img" src="${msg.avatar}" alt="Avatar">
            <div class="plat-badge-mini">
              <img src="${msg.icon}" alt="${msg.platform}">
            </div>
          </div>
          <div class="chat-text-area">
            <div class="chat-user-line">
              <span class="chat-username" data-original-user="${msg.username}" style="color: ${msg.color};" onclick="openAuthorModal('${msg.username}', '${msg.platform}', '${msg.avatar}', '${effectiveName}', ${msg.isVip})">${effectiveName}</span>
              ${msg.isVip ? '<span class="chat-badge-tag vip">🌟 VIP</span>' : ''}
              <span class="chat-timestamp">${msg.time}</span>
              <span class="chat-tts-time tts-done">✓ 0.2s</span>
            </div>
            <div class="chat-body-msg">${msg.text}</div>
          </div>
        `;
        chatList.appendChild(row);
        chatList.scrollTop = chatList.scrollHeight;
      }

      // Broadcast to Canvas Chat Widgets & OBS Overlay
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('CHAT_MESSAGE', msg);
      }

      // Check real ASK poll vote
      checkRealAskVote(msg);

      // Check real Giveaway entry
      checkRealGwEntry(msg, effectiveName);

      // Check real Replie command
      checkRealReplieCommand(msg, effectiveName);

      // Check if this message was recently sent by the host (IRC echo prevention)
      const msgNorm = (msg.text || '').trim().toLowerCase();
      const lastSentTime = (typeof _recentSentHostMessages !== 'undefined') ? _recentSentHostMessages.get(msgNorm) : null;
      const isHostEcho = lastSentTime && (Date.now() - lastSentTime < 10000);

      // Play Speech synthesis if Master TTS is ON and not a duplicate echo of host
      if (_masterTtsEnabled && !isHostEcho) {
        playChatMessageSpeech(msg.username, msg.text);
      }
    }

    // ----------------------------------------------------
    // REAL ASK POLL SYSTEM
    // ----------------------------------------------------
    function checkRealAskVote(msg) {
      if (!window._askPollActive) return;
      const text = (msg.text || '').trim();
      const rows = document.querySelectorAll('#askChoicesList .ask-choice-row');
      if (rows.length === 0) return;

      let matchedIdx = -1;
      const upper = text.toUpperCase();

      // Numeric vote: 1, 2, 3...
      const numVal = parseInt(text);
      if (!isNaN(numVal) && numVal >= 1 && numVal <= rows.length) {
        matchedIdx = numVal - 1;
      } else if (upper.length === 1 && upper >= 'A' && upper <= String.fromCharCode(64 + rows.length)) {
        // Single letter vote: A, B, C...
        matchedIdx = upper.charCodeAt(0) - 65;
      } else {
        // Choice text match
        rows.forEach((r, idx) => {
          const choiceText = (r.querySelector('input')?.value || '').trim().toLowerCase();
          if (choiceText && text.toLowerCase() === choiceText) {
            matchedIdx = idx;
          }
        });
      }

      if (matchedIdx !== -1) {
        window._askVotes[msg.username] = matchedIdx;
        emitAskState();
      }
    }

    function emitAskState() {
      const q = document.getElementById('askQuestion')?.value || 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?';
      const rows = document.querySelectorAll('#askChoicesList .ask-choice-row');
      const choices = [];
      const colors = ['#38bdf8', '#34d399', '#fbbf24', '#f43f5e', '#a855f7', '#ec4899'];
      const counts = new Array(rows.length).fill(0);
      let totalVotes = 0;

      // Count real votes
      Object.values(window._askVotes).forEach(idx => {
        if (idx >= 0 && idx < counts.length) {
          counts[idx]++;
          totalVotes++;
        }
      });

      rows.forEach((row, i) => {
        const label = row.querySelector('.choice-tag')?.textContent || String.fromCharCode(65 + i);
        const text = row.querySelector('input')?.value || `ตัวเลือก ${label}`;
        const v = counts[i];
        choices.push({ label, text, votes: v, color: colors[i % colors.length] });
      });

      choices.forEach(c => {
        c.pct = totalVotes > 0 ? Math.round((c.votes / totalVotes) * 100) : 0;
      });

      window._liveAskState = { question: q, choices, totalVotes, isLive: true };

      // Render live preview graph in win-ask
      renderAskPreviewGraph(choices, totalVotes);

      if (window.BP3_BUS) {
        window.BP3_BUS.emit('ASK_UPDATE', window._liveAskState);
      }
    }

    function renderAskPreviewGraph(choices, totalVotes) {
      const container = document.getElementById('askLiveGraphContainer');
      const lblTotal = document.getElementById('lblAskTotalVotes');
      if (lblTotal) lblTotal.textContent = `ยอดโหวตรวม: ${totalVotes} โหวต`;
      if (!container) return;

      if (totalVotes === 0) {
        container.innerHTML = choices.map(c => `
          <div>
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
              <span><strong>${c.label}:</strong> ${c.text}</span><strong>0% (0 โหวต)</strong>
            </div>
            <div style="height:8px; background:#111214; border-radius:4px; overflow:hidden;">
              <div style="width:0%; height:100%; background:${c.color}; transition: width 0.3s ease;"></div>
            </div>
          </div>
        `).join('');
        return;
      }

      container.innerHTML = choices.map(c => `
        <div>
          <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
            <span><strong>${c.label}:</strong> ${c.text}</span><strong>${c.pct}% (${c.votes} โหวต)</strong>
          </div>
          <div style="height:8px; background:#111214; border-radius:4px; overflow:hidden;">
            <div style="width:${c.pct}%; height:100%; background:${c.color}; transition: width 0.3s ease;"></div>
          </div>
        </div>
      `).join('');
    }

    function sendAskPollToObs() {
      emitAskState();
      showToast('🚀 ส่งโพลคำถามสดขึ้นจอ OBS & Canvas เรียบร้อยแล้ว!');
    }

    // ----------------------------------------------------
    // REAL GIVEAWAY PARTICIPANT & WINNER SYSTEM
    // ----------------------------------------------------
    function checkRealGwEntry(msg, effectiveName) {
      if (!window._isGwCodeBroadcasting) return;
      const code = (document.getElementById('gwActiveCodeLabel')?.textContent || '#join').trim().toLowerCase();
      const msgText = (msg.text || '').toLowerCase();
      if (msgText.includes(code)) {
        const exists = window._gwParticipants.find(p => p.username.toLowerCase() === effectiveName.toLowerCase());
        if (!exists) {
          const entrant = {
            id: window._gwParticipants.length + 1,
            username: effectiveName,
            platform: msg.platform || 'Twitch',
            time: msg.time || new Date().toLocaleTimeString('th-TH')
          };
          window._gwParticipants.push(entrant);
          renderGwTable();
          emitGwState();
        }
      }
    }

    function renderGwTable() {
      const tbody = document.getElementById('gwTableBody');
      const countEl = document.getElementById('gwParticipantCount');
      if (countEl) countEl.textContent = `${window._gwParticipants.length} คน`;
      if (!tbody) return;

      if (window._gwParticipants.length === 0) {
        tbody.innerHTML = '<tr id="gwEmptyRow"><td colspan="5" style="text-align:center; color:#94a3b8; padding:14px;">ยังไม่มีผู้ร่วมสนุกพิมพ์โค้ด (เปิดรับโค้ดแล้วให้คนดูพิมพ์ #join ในแชทได้เลย)</td></tr>';
        return;
      }

      tbody.innerHTML = window._gwParticipants.map(p => `
        <tr>
          <td>${p.id}</td>
          <td><strong>${p.username}</strong></td>
          <td><span>${p.platform}</span></td>
          <td>${p.time}</td>
          <td><button class="btn-win-action close-red" style="height:20px; display:inline-flex;" onclick="removeGwEntrant(${p.id})">✕</button></td>
        </tr>
      `).join('');
    }

    function removeGwEntrant(id) {
      window._gwParticipants = window._gwParticipants.filter(p => p.id !== id);
      renderGwTable();
      emitGwState();
    }

    function rerollGwWinner() {
      if (window._gwParticipants.length === 0) {
        showToast('⚠️ ยังไม่มีผู้เข้าร่วมพิมพ์โค้ดในแชทครับ');
        return;
      }

      const display = document.getElementById('gwWinnerDisplay');
      if (display) {
        display.innerHTML = `<span style="color:#fbbf24; animation: pulse 0.5s infinite;">🎲 กำลังหมุนสุ่มผู้โชคดี...</span>`;
      }

      let ticks = 0;
      const spinInterval = setInterval(() => {
        ticks++;
        const temp = window._gwParticipants[Math.floor(Math.random() * window._gwParticipants.length)];
        if (display) {
          display.innerHTML = `<span style="color:#38bdf8;">🌀 ${temp.username} (${temp.platform})</span>`;
        }
        if (ticks > 12) {
          clearInterval(spinInterval);
          const picked = window._gwParticipants[Math.floor(Math.random() * window._gwParticipants.length)];
          const winnerStr = `${picked.username} (${picked.platform})`;
          if (display) {
            display.innerHTML = `<span style="color:#fbbf24; font-size:18px; font-weight:800; animation: fadeIn 0.3s ease;">🏆 ${winnerStr}</span>`;
          }
          playPlayroomSynthesizer('!cheer', 0.9);
          showToast(`🎉 ผู้โชคดีคือ: ${winnerStr}`);
          emitGwState(winnerStr);
        }
      }, 100);
    }

    function emitGwState(winner = null) {
      const prizeInput = document.querySelector('#gwStepView1 input[type="text"]');
      const prize = prizeInput?.value || 'ของรางวัลพิเศษประจำสตรีม';
      const code = document.getElementById('gwActiveCodeLabel')?.textContent || '#join';
      const count = window._gwParticipants.length;

      window._liveGwState = {
        prize,
        code,
        count,
        winner,
        isBroadcasting: typeof _isGwCodeBroadcasting !== 'undefined' ? _isGwCodeBroadcasting : true
      };

      if (window.BP3_BUS) {
        window.BP3_BUS.emit('GIVEAWAY_UPDATE', window._liveGwState);
      }
    }

    // ----------------------------------------------------
    // REAL REPLIE REACTION SYSTEM
    // ----------------------------------------------------
    function checkRealReplieCommand(msg, effectiveName) {
      const firstWord = (msg.text || '').trim().split(' ')[0].toLowerCase();
      if (window._replieCommands && window._replieCommands[firstWord]) {
        const cmdData = window._replieCommands[firstWord];
        demoReplieAction(firstWord, `${effectiveName}: ${cmdData.text}`, cmdData.emotion);
      }
    }

    function demoReplieAction(cmd, text, emotion) {
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('REPLIE_ACTION', { cmd, text, emotion: emotion || 'happy' });
      }
      showToast(`▶ [คำสั่ง ${cmd}] ${text}`);
    }

    // ----------------------------------------------------
    // REAL QUICK RANDOMIZER SYSTEM
    // ----------------------------------------------------
    function pickChatViewerRandom() {
      const chatters = Array.from(window._activeChattersSet || []);
      const textEl = document.getElementById('randItemsText');
      if (chatters.length === 0) {
        showToast('⚠️ ยังไม่มีคนดูส่งข้อความในแชทสดครับ (ลองพิมพ์ข้อความในแชทก่อน)');
        return;
      }
      if (textEl) {
        textEl.value = chatters.join('\\n');
        showToast(`👥 ดึงรายชื่อคนดูสด ${chatters.length} คนเข้าสู่วงล้อสุ่มเรียบร้อย!`);
      }
    }

    function runSpinRandomizer() {
      const textEl = document.getElementById('randItemsText');
      if (!textEl) return;
      const lines = textEl.value.split('\\n').map(l => l.trim()).filter(Boolean);
      if (lines.length === 0) {
        showToast('⚠️ กรุณาพิมพ์ตัวเลือก หรือกดปุ่ม "👥 สุ่มชื่อคนดูในแชท"');
        return;
      }

      const resEl = document.getElementById('randWinnerResult');
      if (resEl) {
        resEl.innerHTML = `<span style="color:#fbbf24;">🌀 กำลังหมุนสุ่ม...</span>`;
      }

      let ticks = 0;
      const spinInt = setInterval(() => {
        ticks++;
        const temp = lines[Math.floor(Math.random() * lines.length)];
        if (resEl) resEl.innerHTML = `<span style="color:#38bdf8;">🎡 ${temp}</span>`;
        if (ticks > 14) {
          clearInterval(spinInt);
          const randIdx = Math.floor(Math.random() * lines.length);
          const chosen = lines[randIdx];

          if (resEl) {
            resEl.innerHTML = `<span style="color:#34d399; font-weight:800; font-size:17px;">🎯 ${chosen}</span>`;
          }

          const chkRemove = document.getElementById('chkRandRemove');
          if (chkRemove && chkRemove.checked) {
            lines.splice(randIdx, 1);
            textEl.value = lines.join('\\n');
          }

          playPlayroomSynthesizer('!gacha', 0.8);
          showToast(`🎡 ผลสุ่มวงล้อ: ${chosen}`);
        }
      }, 90);
    }

    """

text = text[:target_inject] + new_inject_and_tools + text[target_inject_end:]

# Also remove old duplicate declarations of emitAskState, rerollGwWinner, pickChatViewerRandom, runSpinRandomizer
# Let's inspect where old emitAskState was
old_emit_ask = text.find('function emitAskState() {', target_inject + len(new_inject_and_tools))
if old_emit_ask != -1:
    old_emit_ask_end = text.find('// Init Playroom Tool Table on load', old_emit_ask)
    text = text[:old_emit_ask] + text[old_emit_ask_end:]
    print("Cleaned up old duplicate emitAskState block.")

# Clean up old rerollGwWinner if exists
old_reroll = text.find('function rerollGwWinner() {', target_inject + len(new_inject_and_tools))
if old_reroll != -1:
    old_reroll_end = text.find('function addSimulatedParticipants() {', old_reroll)
    text = text[:old_reroll] + text[old_reroll_end:]
    print("Cleaned up old duplicate rerollGwWinner block.")

# Clean up old runSpinRandomizer if exists
old_spin = text.find('function runSpinRandomizer() {', target_inject + len(new_inject_and_tools))
if old_spin != -1:
    old_spin_end = text.find('function shuffleRandItems() {', old_spin)
    text = text[:old_spin] + text[old_spin_end:]
    print("Cleaned up old duplicate runSpinRandomizer block.")

# Clean up old pickChatViewerRandom if exists
old_pick = text.find('function pickChatViewerRandom() {', target_inject + len(new_inject_and_tools))
if old_pick != -1:
    old_pick_end = text.find('function ', old_pick + 20)
    text = text[:old_pick] + text[old_pick_end:]
    print("Cleaned up old duplicate pickChatViewerRandom block.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied real tools to index.html successfully.")
