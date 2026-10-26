import os
import re

index_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"
composer_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js"

# -------------------------------------------------------------
# 1. Update src/index.html
# -------------------------------------------------------------
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Register win-playroom in initDraggableWindow
if "initDraggableWindow('win-playroom'" not in html:
    html = html.replace(
        "initDraggableWindow('win-chat-widget', 'drag-chat-widget');",
        "initDraggableWindow('win-chat-widget', 'drag-chat-widget');\n      initDraggableWindow('win-playroom', 'drag-playroom');"
    )

# Register playroom in openToolWindow and closeToolWindow
if "'playroom': 'btnRailPlayroom'" not in html:
    html = html.replace(
        "'chat-widget': 'btnRailChatWidget',",
        "'chat-widget': 'btnRailChatWidget',\n        'playroom': 'btnRailPlayroom',"
    )
    html = html.replace(
        "'chat-widget': 'Chat Widget Customizer'",
        "'chat-widget': 'Chat Widget Customizer',\n        'playroom': 'Playroom Studio มินิเกม & คลังคลิป'"
    )

# Wire up Replie DEMO buttons
replie_demo_old = """<button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="showToast('▶ แสดงภาพ !hi บนจอ OBS')">▶ DEMO</button>"""
replie_demo_new = """<button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="demoReplieAction('!hi', 'สวัสดีครับทุกคน! ยินดีต้อนรับสู่สตรีมครับ', 'happy')">▶ DEMO</button>"""
html = html.replace(replie_demo_old, replie_demo_new)

replie_demo_gg_old = """<button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="showToast('▶ แสดงภาพ !gg บนจอ OBS')">▶ DEMO</button>"""
replie_demo_gg_new = """<button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="demoReplieAction('!gg', 'GG WP ครับทุกคน! เก่งมากๆ เลย', 'cheer')">▶ DEMO</button>"""
html = html.replace(replie_demo_gg_old, replie_demo_gg_new)

replie_demo_bye_old = """<button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="showToast('▶ แสดงภาพ !bye บนจอ OBS')">▶ DEMO</button>"""
replie_demo_bye_new = """<button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="demoReplieAction('!bye', 'ขอบคุณที่รับชมนะครับ ไว้เจอกันใหม่ครับ บ๊ายบาย', 'sleepy')">▶ DEMO</button>"""
html = html.replace(replie_demo_bye_old, replie_demo_bye_new)

# Wire up Ask button
ask_send_old = """<button class="btn-topbar-action primary" onclick="showToast('🚀 ส่งโพลคำถามขึ้นจอ OBS เรียบร้อยแล้ว!')">
          🚀 ส่งโพลขึ้นจอ OBS
        </button>"""
ask_send_new = """<button class="btn-topbar-action primary" onclick="sendAskPollToObs()">
          🚀 ส่งโพลขึ้นจอ OBS
        </button>"""
html = html.replace(ask_send_old, ask_send_new)

# Insert the BP3_BUS and tool handlers script before </script>
bp3_script = """
    // ----------------------------------------------------
    // UNIFIED REAL-TIME EVENT BUS (BP3_BUS)
    // Synchronizes Management Tools & Overlay Widgets
    // ----------------------------------------------------
    window.BP3_BUS = {
      bc: ('BroadcastChannel' in window) ? new BroadcastChannel('bp3_system_channel') : null,
      listeners: {},
      on(event, cb) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(cb);
      },
      emit(event, payload) {
        if (this.listeners[event]) {
          this.listeners[event].forEach(cb => {
            try { cb(payload); } catch (e) { console.error('BP3_BUS local handler error:', e); }
          });
        }
        if (this.bc) {
          try {
            this.bc.postMessage({ event, payload, timestamp: Date.now() });
          } catch (e) {
            console.error('BP3_BUS broadcast error:', e);
          }
        }
      },
      init() {
        if (this.bc) {
          this.bc.onmessage = (msg) => {
            const { event, payload } = msg.data || {};
            if (event && this.listeners[event]) {
              this.listeners[event].forEach(cb => {
                try { cb(payload); } catch (e) { console.error('BP3_BUS remote handler error:', e); }
              });
            }
          };
        }
      }
    };
    window.BP3_BUS.init();

    // ----------------------------------------------------
    // PLAYROOM TOOL LOGIC & PRESETS
    // ----------------------------------------------------
    const PLAYROOM_PRESETS = {
      '!fortune': [
        { name: 'เซียมซี: ดวงมหาเฮง เฮงๆ รวยๆ', url: 'https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3', type: 'audio', weight: 35, vol: 90, desc: 'เซียมซีใบที่ 1 ดวงปังสุดๆ' },
        { name: 'เซียมซี: ราหูอมจันทร์ มีเกณฑ์เสียทรัพย์', url: 'https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3', type: 'audio', weight: 25, vol: 80, desc: 'เซียมซีใบที่ 7 ระวังของหาย' },
        { name: 'เซียมซี: มีเกณฑ์พบเนื้อคู่เร็วๆ นี้', url: 'https://assets.mixkit.co/active_storage/sfx/2018/2018-preview.mp3', type: 'audio', weight: 40, vol: 85, desc: 'เซียมซีใบที่ 9 ความรักสดใส' }
      ],
      '!scare': [
        { name: 'กรีดร้องสยองขวัญ Jumpscare', url: 'https://assets.mixkit.co/active_storage/sfx/2955/2955-preview.mp3', type: 'audio', weight: 50, vol: 95, desc: 'เสียงกรี๊ดตกใจ' },
        { name: 'หัวเราะหลอนกระตุกขวัญ', url: 'https://assets.mixkit.co/active_storage/sfx/2954/2954-preview.mp3', type: 'audio', weight: 50, vol: 90, desc: 'เสียงหัวเราะแม่มด' }
      ],
      '!cheer': [
        { name: 'เสียงปรบมือชื่นชมคนเก่ง', url: 'https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3', type: 'audio', weight: 60, vol: 85, desc: 'ปรบมือเกรียวกราว' },
        { name: 'เสียงเป่าแตรเฉลิมฉลองชัยชนะ', url: 'https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3', type: 'audio', weight: 40, vol: 90, desc: 'แตรฉลองชัย' }
      ],
      '!gacha': [
        { name: 'กาชา: เกลือล้วนๆ ไม่เจือปน (3 ดาว)', url: 'https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3', type: 'audio', weight: 70, vol: 85, desc: 'เกลือแกง 3 ดาว' },
        { name: 'กาชา: ได้ตัวละครลับระดับ UR สีทอง!', url: 'https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3', type: 'audio', weight: 30, vol: 95, desc: 'แสงรุ้งสีทองระดับ SSR' }
      ]
    };

    let _activePlayroomTrigger = '!fortune';
    let _activePlayroomClips = [...PLAYROOM_PRESETS['!fortune']];

    function switchPlayroomTab(tabNum) {
      document.getElementById('btnPlayroomTab1').classList.toggle('active', tabNum === 1);
      document.getElementById('btnPlayroomTab2').classList.toggle('active', tabNum === 2);
      document.getElementById('btnPlayroomTab3').classList.toggle('active', tabNum === 3);

      document.getElementById('panePlayroomTab1').style.display = tabNum === 1 ? 'block' : 'none';
      document.getElementById('panePlayroomTab2').style.display = tabNum === 2 ? 'block' : 'none';
      document.getElementById('panePlayroomTab3').style.display = tabNum === 3 ? 'block' : 'none';
    }

    function onPlayroomTriggerSelect(triggerKey) {
      _activePlayroomTrigger = triggerKey;
      _activePlayroomClips = PLAYROOM_PRESETS[triggerKey] || [];
      renderPlayroomClipsTable();
      const countLabel = document.getElementById('lblPlayroomClipsCount');
      if (countLabel) countLabel.textContent = `${_activePlayroomClips.length} คลิปในชุดนี้`;
      const txtSim = document.getElementById('txtPlayroomSimCmd');
      if (txtSim) txtSim.value = triggerKey;
    }

    function renderPlayroomClipsTable() {
      const tbody = document.getElementById('tbodyPlayroomClips');
      if (!tbody) return;
      tbody.innerHTML = '';

      _activePlayroomClips.forEach((clip, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${idx + 1}</td>
          <td><strong>${clip.name}</strong><br><span style="font-size:11px; color:#94a3b8;">${clip.desc || ''}</span></td>
          <td><span style="font-size:11px; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:4px; max-width:200px; display:inline-block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${clip.url}</span></td>
          <td>${clip.weight}%</td>
          <td>${clip.vol}%</td>
          <td>
            <button class="btn-topbar-action" style="height:22px; padding:0 6px; font-size:11px;" onclick="playroomTestClip(${idx})">▶ ทดสอบ</button>
            <button class="btn-win-action close-red" style="height:20px; display:inline-flex;" onclick="deletePlayroomClip(${idx})">✕</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function addPlayroomClipRow() {
      const name = prompt('กรุณาตั้งชื่อคลิป / มีมใหม่:', 'มีมใหม่');
      if (!name) return;
      _activePlayroomClips.push({
        name,
        url: 'https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3',
        type: 'audio',
        weight: 30,
        vol: 85,
        desc: 'คลิปที่เพิ่มใหม่'
      });
      renderPlayroomClipsTable();
      showToast(`➕ เพิ่มคลิป "${name}" สำเร็จ`);
    }

    function deletePlayroomClip(idx) {
      if (idx >= 0 && idx < _activePlayroomClips.length) {
        const removed = _activePlayroomClips.splice(idx, 1);
        renderPlayroomClipsTable();
        showToast(`🗑 ลบคลิป ${removed[0].name} แล้ว`);
      }
    }

    function playroomTestClip(idx) {
      const clip = _activePlayroomClips[idx];
      if (!clip) return;
      firePlayroomClipEvent(clip);
    }

    function playroomFireActiveClip() {
      if (_activePlayroomClips.length > 0) {
        firePlayroomClipEvent(_activePlayroomClips[0]);
      } else {
        showToast('⚠️ ยังไม่มีคลิปในชุดนี้ครับ');
      }
    }

    function runPlayroomSimulatedChat() {
      const cmd = (document.getElementById('txtPlayroomSimCmd')?.value || '!fortune').trim();
      const list = PLAYROOM_PRESETS[cmd] || _activePlayroomClips;
      if (!list || list.length === 0) {
        showToast(`⚠️ ไม่พบคลิปสำหรับคำสั่ง ${cmd}`);
        return;
      }
      const picked = list[Math.floor(Math.random() * list.length)];
      firePlayroomClipEvent(picked, cmd);
    }

    function firePlayroomClipEvent(clip, customCmd) {
      const trigger = customCmd || _activePlayroomTrigger;
      const ckEnabled = document.getElementById('chkPlayroomChromaKey')?.checked ?? true;
      const ckColor = document.getElementById('colPlayroomKey')?.value || '#00ff00';
      const duration = parseInt(document.getElementById('rngPlayroomImgDur')?.value) || 5;

      const payload = {
        trigger,
        name: clip.name,
        url: clip.url,
        type: clip.type || 'audio',
        vol: clip.vol || 85,
        ckEnabled,
        ckColor,
        duration
      };

      if (window.BP3_BUS) {
        window.BP3_BUS.emit('PLAYROOM_PLAY_CLIP', payload);
      }

      // Update monitor display in Tab 3
      const monStatus = document.getElementById('lblPlayroomMonitorStatus');
      if (monStatus) {
        monStatus.innerHTML = `<span style="color:#c084fc; font-weight:700;">▶ กำลังฉาย: ${clip.name} (${trigger})</span>`;
        setTimeout(() => {
          monStatus.innerHTML = 'รอคำสั่งจากแชทสด หรือกดปุ่ม "▶ ทดสอบยิงคลิป"';
        }, duration * 1000);
      }

      showToast(`🎬 ยิงคลิป "${clip.name}" ขึ้นจอเรียบร้อย!`);
    }

    function onPlayroomChromaChange() {
      const ckEnabled = document.getElementById('chkPlayroomChromaKey')?.checked;
      const ckColor = document.getElementById('colPlayroomKey')?.value;
      const sim = document.getElementById('rngPlayroomSim')?.value;
      const smooth = document.getElementById('rngPlayroomSmooth')?.value;

      if (window.BP3_BUS) {
        window.BP3_BUS.emit('PLAYROOM_CK_SETTINGS', { ckEnabled, ckColor, sim, smooth });
      }
    }

    function addPlayroomTrigger() {
      const newCmd = prompt('พิมพ์ชื่อคำสั่ง Trigger แชทใหม่ (ขึ้นต้นด้วย ! เช่น !jump):', '!');
      if (!newCmd || !newCmd.startsWith('!')) return;
      PLAYROOM_PRESETS[newCmd] = [
        { name: `${newCmd} เอฟเฟกต์ 1`, url: 'https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3', type: 'audio', weight: 50, vol: 85 }
      ];
      const sel = document.getElementById('selPlayroomTrigger');
      if (sel) {
        const opt = document.createElement('option');
        opt.value = newCmd;
        opt.textContent = `${newCmd} — คำสั่งแชทใหม่`;
        sel.appendChild(opt);
        sel.value = newCmd;
        onPlayroomTriggerSelect(newCmd);
      }
      showToast(`✨ สร้าง Trigger ${newCmd} เรียบร้อย!`);
    }

    // ----------------------------------------------------
    // REAL-TIME BRIDGE: ASK, GIVEAWAY, REPLIE
    // ----------------------------------------------------
    function emitAskState() {
      const q = document.getElementById('askQuestion')?.value || 'สตรีมวันนี้ เล่นเกมอะไรต่อดีครับ?';
      const rows = document.querySelectorAll('#askChoicesList .ask-choice-row');
      const choices = [];
      const colors = ['#38bdf8', '#34d399', '#fbbf24', '#f43f5e', '#a855f7', '#ec4899'];
      const defaultVotes = [83, 55, 28, 18, 12, 8];
      let totalVotes = 0;

      rows.forEach((row, i) => {
        const label = row.querySelector('.choice-tag')?.textContent || String.fromCharCode(65 + i);
        const text = row.querySelector('input')?.value || `ตัวเลือก ${label}`;
        const v = defaultVotes[i] || 10;
        totalVotes += v;
        choices.push({ label, text, votes: v, color: colors[i % colors.length] });
      });

      choices.forEach(c => {
        c.pct = totalVotes > 0 ? Math.round((c.votes / totalVotes) * 100) : 0;
      });

      window._liveAskState = { question: q, choices, totalVotes, isLive: true };
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('ASK_UPDATE', window._liveAskState);
      }
    }

    function sendAskPollToObs() {
      emitAskState();
      showToast('🚀 ส่งโพลคำถามสดขึ้นจอ OBS & Canvas เรียบร้อยแล้ว!');
    }

    function emitGwState(winner = null) {
      const prizeInput = document.querySelector('#gwStepView1 input[type="text"]');
      const prize = prizeInput?.value || 'ของรางวัลพิเศษประจำสตรีม';
      const code = document.getElementById('gwActiveCodeLabel')?.textContent || '#join';
      const count = parseInt(document.getElementById('gwParticipantCount')?.textContent) || 148;

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

    function demoReplieAction(cmd, text, emotion) {
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('REPLIE_ACTION', { cmd, text, emotion: emotion || 'happy' });
      }
      showToast(`▶ แสดงท่าทางและคำพูด ${cmd} บนจอ`);
    }

    // Init Playroom Tool Table on load
    window.addEventListener('DOMContentLoaded', () => {
      renderPlayroomClipsTable();
      const qInput = document.getElementById('askQuestion');
      if (qInput) qInput.addEventListener('input', emitAskState);
      const choiceContainer = document.getElementById('askChoicesList');
      if (choiceContainer) choiceContainer.addEventListener('input', emitAskState);
    });
"""

if 'window.BP3_BUS =' not in html:
    html = html.replace('</script>', bp3_script + '\n  </script>', 1)

# Hook rerollGwWinner to emitGwState
if 'rerollGwWinner()' in html:
    html = html.replace(
        "showToast(`🎉 ผู้โชคดีคือ: ${picked}`);",
        "showToast(`🎉 ผู้โชคดีคือ: ${picked}`);\n      emitGwState(picked);"
    )

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated src/index.html with full BP3_BUS and Playroom tool logic!")
