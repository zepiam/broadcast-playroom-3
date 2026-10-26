import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update win-ask preview section to have dynamic container and clean labels
old_ask_preview = text.find('<!-- Live Preview Bar Graph -->')
old_ask_preview_end = text.find('</div>\n        </div>\n      </div>\n\n      <!-- TAB 2: หน้าตา Overlay', old_ask_preview)

if old_ask_preview != -1 and old_ask_preview_end != -1:
    new_ask_preview_html = """<!-- Live Preview Bar Graph -->
        <div class="section-card">
          <div class="section-card-title">
            <span>📊 ตัวอย่างแท่งคะแนนโหวตสด</span>
            <span style="font-size: 11px; color: #34d399;" id="lblAskTotalVotes">ยอดโหวตรวม: 0 โหวต</span>
          </div>
          <div id="askLiveGraphContainer" style="display:flex; flex-direction:column; gap:8px;">
            <div style="font-size:12px; color:#94a3b8; text-align:center; padding:12px;">กำลังรอผลโหวตจากคนดูในแชท (พิมพ์ A, B, C... หรือ 1, 2, 3...)</div>
          </div>
        </div>
      </div>"""
    text = text[:old_ask_preview] + new_ask_preview_html + text[old_ask_preview_end:]
    print("Replaced ask preview mockup with dynamic container.")

# 2. Clear mock rows from gwTableBody
gw_table_start = text.find('<tbody id="gwTableBody">')
gw_table_end = text.find('</tbody>', gw_table_start)
if gw_table_start != -1 and gw_table_end != -1:
    empty_gw_table = '<tbody id="gwTableBody">\n              <tr id="gwEmptyRow"><td colspan="5" style="text-align:center; color:#94a3b8; padding:14px;">ยังไม่มีผู้ร่วมสนุกพิมพ์โค้ด (เปิดรับโค้ดแล้วให้คนดูพิมพ์ #join ในแชทได้เลย)</td></tr>\n            </tbody>'
    text = text[:gw_table_start] + empty_gw_table + text[gw_table_end + 8:]
    print("Cleared mock rows from gwTableBody.")

# 3. Update gwParticipantCount to start from 0
text = text.replace('<span style="color:var(--dc-green); font-weight:bold;">148 คน</span>', '<span id="gwParticipantCount" style="color:var(--dc-green); font-weight:bold;">0 คน</span>')
text = text.replace('148 คน</span>', '0 คน</span>', 1)

# 4. Now update scripts: Playroom Audio & Visual + Real ASK + Real Giveaway + Real Replie + Real Randomizer
old_fire_idx = text.find('function firePlayroomClipEvent(clip, customCmd) {')
# find end of script block or emitAskState
old_emit_ask_idx = text.find('function emitAskState() {')
old_send_obs_idx = text.find('function sendAskPollToObs() {')
old_emit_gw_idx = text.find('function emitGwState(winner = null) {')

# Let's locate where firePlayroomClipEvent is
end_of_playroom_scripts = text.find('function onPlayroomChromaChange() {')

new_playroom_and_real_tools_code = """// ==============================================================================
    // PLAYROOM REAL AUDIO SYNTHESIS & ANIMATED VISUAL MONITOR
    // ==============================================================================
    let _playroomAudioCtx = null;
    function getPlayroomAudioCtx() {
      if (!_playroomAudioCtx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) _playroomAudioCtx = new AudioCtx();
      }
      if (_playroomAudioCtx && _playroomAudioCtx.state === 'suspended') {
        _playroomAudioCtx.resume();
      }
      return _playroomAudioCtx;
    }

    function playPlayroomSynthesizer(trigger, volume = 0.85) {
      try {
        const ctx = getPlayroomAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;
        const masterGain = ctx.createGain();
        masterGain.gain.setValueAtTime(volume, now);
        masterGain.connect(ctx.destination);

        if (trigger === '!scare') {
          // Jumpscare Screech + Bass Drop
          const osc = ctx.createOscillator();
          const g = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(95, now);
          osc.frequency.exponentialRampToValueAtTime(32, now + 1.2);
          g.gain.setValueAtTime(0.8, now);
          g.gain.exponentialRampToValueAtTime(0.01, now + 1.2);
          osc.connect(g);
          g.connect(masterGain);
          osc.start(now);
          osc.stop(now + 1.2);

          const screech = ctx.createOscillator();
          const sg = ctx.createGain();
          screech.type = 'triangle';
          screech.frequency.setValueAtTime(1600, now);
          screech.frequency.exponentialRampToValueAtTime(350, now + 0.9);
          sg.gain.setValueAtTime(0.5, now);
          sg.gain.exponentialRampToValueAtTime(0.01, now + 0.9);
          screech.connect(sg);
          sg.connect(masterGain);
          screech.start(now);
          screech.stop(now + 0.9);
        } else if (trigger === '!cheer') {
          // Triumph fanfare chord
          [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = 'triangle';
            o.frequency.setValueAtTime(freq, now + idx * 0.08);
            g.gain.setValueAtTime(0, now);
            g.gain.setValueAtTime(0.3, now + idx * 0.08);
            g.gain.exponentialRampToValueAtTime(0.001, now + 1.6);
            o.connect(g);
            g.connect(masterGain);
            o.start(now + idx * 0.08);
            o.stop(now + 1.6);
          });
        } else if (trigger === '!gacha') {
          // Roulette ticks + jackpot high bell
          for (let i = 0; i < 7; i++) {
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = 'sine';
            o.frequency.setValueAtTime(700 + i * 80, now + i * 0.08);
            g.gain.setValueAtTime(0.22, now + i * 0.08);
            g.gain.exponentialRampToValueAtTime(0.01, now + i * 0.08 + 0.06);
            o.connect(g);
            g.connect(masterGain);
            o.start(now + i * 0.08);
            o.stop(now + i * 0.08 + 0.06);
          }
          setTimeout(() => {
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = 'sine';
            o.frequency.setValueAtTime(1318.51, ctx.currentTime);
            g.gain.setValueAtTime(0.45, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.3);
            o.connect(g);
            g.connect(masterGain);
            o.start(ctx.currentTime);
            o.stop(ctx.currentTime + 1.3);
          }, 650);
        } else {
          // Mystical harp / fortune arpeggio (default / !fortune)
          [440, 554.37, 659.25, 880, 1108.73, 1318.51].forEach((freq, idx) => {
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = 'sine';
            o.frequency.setValueAtTime(freq, now + idx * 0.09);
            g.gain.setValueAtTime(0.32, now + idx * 0.09);
            g.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.95);
            o.connect(g);
            g.connect(masterGain);
            o.start(now + idx * 0.09);
            o.stop(now + idx * 0.09 + 0.95);
          });
        }
      } catch (err) {
        console.warn('Playroom audio synth error:', err);
      }
    }

    function firePlayroomClipEvent(clip, customCmd) {
      const trigger = customCmd || _activePlayroomTrigger || '!fortune';
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

      // 1. Play realistic Web Audio synthesis locally
      playPlayroomSynthesizer(trigger, (clip.vol || 85) / 100);

      // 2. Broadcast via BP3_BUS to OBS Overlay & Canvas
      if (window.BP3_BUS) {
        window.BP3_BUS.emit('PLAYROOM_PLAY_CLIP', payload);
      }

      // 3. Update monitor visual display in Tab 3 with live sound waves and countdown
      const monContent = document.getElementById('playroomMonitorContent');
      if (monContent) {
        const triggerIcons = { '!fortune': '🔮', '!scare': '👻', '!cheer': '🎉', '!gacha': '🎰' };
        const icon = triggerIcons[trigger] || '🎬';
        monContent.innerHTML = `
          <div style="display:flex; align-items:center; gap:12px; background:rgba(192, 132, 252, 0.15); border:1px solid #c084fc; border-radius:8px; padding:12px 18px; width:90%; box-sizing:border-box;">
            <span style="font-size:32px;">${icon}</span>
            <div style="flex:1; text-align:left;">
              <div style="color:#ffffff; font-weight:700; font-size:14px;">กำลังเล่น: ${clip.name}</div>
              <div style="color:#c084fc; font-size:11.5px; font-weight:600;">คำสั่ง: ${trigger} • น้ำหนักสุ่ม: ${clip.weight}% • เสียง: ${clip.vol}%</div>
              <div style="height:4px; background:rgba(255,255,255,0.2); border-radius:2px; margin-top:6px; overflow:hidden;">
                <div style="height:100%; width:100%; background:#c084fc; animation: playroomProg ${duration}s linear forwards;"></div>
              </div>
            </div>
            <span style="color:#34d399; font-size:12px; font-weight:700; white-space:nowrap;">● สด</span>
          </div>
        `;
        setTimeout(() => {
          monContent.innerHTML = `
            <span style="font-size:28px;">🎮</span>
            <span style="color:#94a3b8; font-size:13px;" id="lblPlayroomMonitorStatus">รอคำสั่งจากแชทสด หรือกดปุ่ม "▶ ทดสอบยิงคลิป"</span>
          `;
        }, duration * 1000);
      }

      showToast(`🎬 [เสียง & ภาพสด] ยิงคลิป "${clip.name}" (${trigger}) เรียบร้อย!`);
    }

    """

text = text[:old_fire_idx] + new_playroom_and_real_tools_code + text[end_of_playroom_scripts:]
print("Updated firePlayroomClipEvent with real audio synthesis and live visual monitor.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved index.html.")
