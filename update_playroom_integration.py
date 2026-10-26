import os
import re

index_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"
composer_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js"

with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add btnRailPlayroom to rail
if 'id="btnRailPlayroom"' not in html:
    rail_target = '<button class="rail-icon-btn sortable-item" id="btnRailChatWidget" data-item-id="chat-widget" draggable="true" title="🎨 Chat Widget Customizer" onclick="handleSortableClick(event, () => openToolWindow(\'chat-widget\'))">\n          🎨\n        </button>'
    if rail_target not in html:
        # try CRLF
        rail_target = rail_target.replace('\n', '\r\n')
    
    rail_replacement = rail_target + ('\r\n' if '\r\n' in html else '\n') + '''        <button class="rail-icon-btn sortable-item" id="btnRailPlayroom" data-item-id="playroom" draggable="true" title="🎮 Playroom มินิเกม & คลังคลิปแชท" onclick="handleSortableClick(event, () => openToolWindow('playroom'))">
          🎮
        </button>'''
    if '\r\n' in html:
        rail_replacement = rail_replacement.replace('\n', '\r\n')
    
    if rail_target in html:
        html = html.replace(rail_target, rail_replacement, 1)
        print("Successfully added btnRailPlayroom to rail!")
    else:
        print("WARNING: rail_target not found!")
else:
    print("btnRailPlayroom already exists.")

# 2. Add win-playroom window markup
if 'id="win-playroom"' not in html:
    playroom_window_html = '''  <!-- ========================================================
       WINDOW: PLAYROOM STUDIO (🎮 มินิเกม & คลังคลิปแชทอินเตอร์แอคทีฟ)
       ======================================================== -->
  <div class="floating-window" id="win-playroom" style="width: 860px; top: 75px; left: 320px;">
    <div class="floating-header" id="drag-playroom">
      <div class="floating-title-box">
        <span style="font-size: 18px;">🎮</span>
        <div>
          <div style="font-size: 14.5px; font-weight: 700; color: #f2f3f5;">Playroom Studio</div>
          <div style="font-size: 11px; color: var(--dc-text-muted);">จัดการคลิปมีม คำสั่งแชทอินเตอร์แอคทีฟ มินิเกม & ตัดฉากเขียว</div>
        </div>
      </div>
      <div class="floating-actions-right">
        <button class="btn-topbar-action" style="height: 26px; padding: 0 8px; font-size: 11px;" onclick="copyObsUrl()">🎴 ลิงก์ OBS</button>
        <button class="btn-win-action" title="ย่อหน้าต่าง" onclick="minimizeWindow('playroom')">—</button>
        <button class="btn-win-action close-red" title="ปิดหน้าต่าง" onclick="closeToolWindow('playroom')">✕</button>
      </div>
    </div>

    <!-- Main Mode Tabs -->
    <div style="padding: 10px 18px 0 18px; background-color: #232428;">
      <div class="win-tabs">
        <button class="win-tab-btn active" id="btnPlayroomTab1" onclick="switchPlayroomTab(1)">🎮 คำสั่ง & คลังคลิป</button>
        <button class="win-tab-btn" id="btnPlayroomTab2" onclick="switchPlayroomTab(2)">✨ ตัดฉากหลังเขียว</button>
        <button class="win-tab-btn" id="btnPlayroomTab3" onclick="switchPlayroomTab(3)">📺 ทดสอบ & จำลองแชท</button>
      </div>
    </div>

    <!-- Body Container -->
    <div class="floating-body" style="max-height: 520px; overflow-y: auto;">
      <!-- TAB 1: คำสั่ง & คลังคลิป -->
      <div id="panePlayroomTab1">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px; background-color: #1e1f22; padding: 10px 14px; border-radius: 6px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:12.5px; font-weight:600;">เปิดใช้งานระบบ Playroom</span>
            <input type="checkbox" id="chkPlayroomMasterEnabled" checked style="accent-color: var(--dc-green); transform: scale(1.1);" onchange="showToast(this.checked ? '🎮 เปิดใช้งานระบบ Playroom' : '⏸ พักระบบ Playroom ชั่วคราว')">
          </div>
          <button class="btn-topbar-action primary" onclick="addPlayroomTrigger()">
            ➕ เพิ่ม Trigger ใหม่
          </button>
        </div>

        <div class="section-card" style="margin-bottom: 14px;">
          <div class="section-card-title">
            <span>🎯 เลือกชุดคำสั่ง Trigger ที่ต้องการจัดการ</span>
            <span style="font-size:11px; color:#38bdf8;" id="lblPlayroomClipsCount">3 คลิปในชุดนี้</span>
          </div>
          <div class="modal-grid-2" style="margin-bottom: 8px;">
            <div class="modal-form-group">
              <label class="modal-form-label">คำสั่งแชท (Trigger Command)</label>
              <select class="voice-select-box" id="selPlayroomTrigger" style="margin:0; width:100%;" onchange="onPlayroomTriggerSelect(this.value)">
                <option value="!fortune">!fortune — เซียมซีและทำนายดวงประจำวัน</option>
                <option value="!scare">!scare — คลิปตกใจ Jumpscare หลอนๆ</option>
                <option value="!cheer">!cheer — เสียงและเอฟเฟกต์เชียร์สตรีมเมอร์</option>
                <option value="!gacha">!gacha — มินิเกมสุ่มเกลือ / รางวัลใหญ่</option>
              </select>
            </div>
            <div class="modal-form-group">
              <label class="modal-form-label">คูลดาวน์คำสั่ง (วินาที)</label>
              <div style="display:flex; gap:8px; align-items:center;">
                <input type="number" class="modal-input" id="numPlayroomCooldown" value="10" min="1" max="300" style="width:100px;">
                <span style="font-size:12px; color:#94a3b8;">วินาทีต่อครั้ง</span>
              </div>
            </div>
          </div>

          <div class="modal-grid-2">
            <div class="modal-form-group">
              <label class="modal-form-label">สิทธิ์ผู้ใช้งาน (Permission)</label>
              <select class="voice-select-box" id="selPlayroomPerm" style="margin:0;">
                <option value="all">ทุกคนในแชท (Everyone)</option>
                <option value="follower">ผู้ติดตาม (Follower ขึ้นไป)</option>
                <option value="sub">สมาชิก / ผู้สนับสนุน (Subscriber / VIP)</option>
                <option value="mod">ผู้ดูแลห้อง (Moderator เท่านั้น)</option>
              </select>
            </div>
            <div class="modal-form-group">
              <label class="modal-form-label">ระดับเสียงเริ่มต้นของชุดนี้</label>
              <div style="display:flex; gap:10px; align-items:center;">
                <input type="range" class="topbar-slider" id="rngPlayroomTriggerVol" min="0" max="100" value="85" style="flex:1;" oninput="document.getElementById('lblPlayroomTriggerVol').textContent = this.value + '%'">
                <span style="font-size:12px; color:#38bdf8; width:35px;" id="lblPlayroomTriggerVol">85%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-form-group" style="margin-bottom: 12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <label class="modal-form-label" style="font-weight:700;">🎬 คลังคลิปของคำสั่งที่เลือก</label>
            <div style="display:flex; gap:6px;">
              <button class="btn-topbar-action" style="height:26px; font-size:11.5px;" onclick="addPlayroomClipRow()">+ เพิ่มคลิป</button>
            </div>
          </div>

          <table class="tool-table" id="tblPlayroomClips">
            <thead>
              <tr>
                <th style="width: 35px;">#</th>
                <th>ชื่อคลิป / มีม</th>
                <th>ไฟล์หรือลิงก์มีเดีย</th>
                <th style="width: 80px;">น้ำหนักสุ่ม</th>
                <th style="width: 80px;">ระดับเสียง</th>
                <th style="width: 130px;">การทำงาน</th>
              </tr>
            </thead>
            <tbody id="tbodyPlayroomClips">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB 2: ตัดฉากหลังเขียว Chroma Key -->
      <div id="panePlayroomTab2" style="display:none;">
        <div class="section-card" style="margin-bottom:14px;">
          <div class="section-card-title">
            <span>✨ ปรับแต่งการตัดฉากหลังเขียว (Chroma Key Filter)</span>
          </div>
          <div class="clean-row" style="background:#1e1f22; padding: 10px 14px; border-radius: 6px; margin-bottom: 14px;">
            <div>
              <div style="font-weight: 600; font-size: 13px;">เปิดใช้งานระบบตัดสีพื้นหลังอัตโนมัติ</div>
              <div style="font-size: 11.5px; color: var(--dc-text-dim);">ตัดพื้นหลังสีเขียว/น้ำเงินของคลิปวิดีโอหรือภาพให้โปร่งใสบนจอ OBS ทันที</div>
            </div>
            <input type="checkbox" id="chkPlayroomChromaKey" checked style="accent-color: var(--dc-green); transform: scale(1.2);" onchange="onPlayroomChromaChange()">
          </div>

          <div class="modal-grid-2" style="margin-bottom: 14px;">
            <div class="modal-form-group">
              <label class="modal-form-label">สีหลักที่ต้องการเจาะโปร่งใส (Key Color)</label>
              <div style="display:flex; gap:10px; align-items:center;">
                <input type="color" class="cwc-color-pick" id="colPlayroomKey" value="#00ff00" onchange="onPlayroomChromaChange()">
                <select class="voice-select-box" id="selPlayroomPresetKey" style="margin:0; flex:1;" onchange="document.getElementById('colPlayroomKey').value = this.value; onPlayroomChromaChange();">
                  <option value="#00ff00">กรีนสกรีนสีเขียวมาตรฐาน (#00FF00)</option>
                  <option value="#0000ff">บลูสกรีนสีน้ำเงิน (#0000FF)</option>
                  <option value="#ff00ff">สีชมพูมาเจนต้า (#FF00FF)</option>
                </select>
              </div>
            </div>
            <div class="modal-form-group">
              <label class="modal-form-label">แอนิเมชั่นตอนคลิปปรากฏบนจอ</label>
              <select class="voice-select-box" id="selPlayroomAnim" style="margin:0;">
                <option value="pop">เด้งขยายตัว Pop & Bounce</option>
                <option value="fade">ค่อยๆ ปรากฏจางใส Smooth Fade</option>
                <option value="slide">เลื่อนขึ้นจากด้านล่าง Slide Up</option>
              </select>
            </div>
          </div>

          <div class="modal-grid-2" style="margin-bottom: 14px;">
            <div class="modal-form-group">
              <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <label class="modal-form-label">ความคล้ายคลึงของสี (Similarity)</label>
                <span style="font-size:12px; color:#38bdf8;" id="lblPlayroomSim">50%</span>
              </div>
              <input type="range" class="topbar-slider" id="rngPlayroomSim" min="1" max="100" value="50" oninput="document.getElementById('lblPlayroomSim').textContent = this.value + '%'; onPlayroomChromaChange();">
            </div>
            <div class="modal-form-group">
              <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <label class="modal-form-label">ความเนียนของขอบตัด (Smoothness)</label>
                <span style="font-size:12px; color:#38bdf8;" id="lblPlayroomSmooth">30%</span>
              </div>
              <input type="range" class="topbar-slider" id="rngPlayroomSmooth" min="1" max="100" value="30" oninput="document.getElementById('lblPlayroomSmooth').textContent = this.value + '%'; onPlayroomChromaChange();">
            </div>
          </div>

          <div class="modal-form-group">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
              <label class="modal-form-label">ระยะเวลาแสดงภาพนิ่ง (วินาที)</label>
              <span style="font-size:12px; color:#38bdf8;" id="lblPlayroomImgDur">5 วินาที</span>
            </div>
            <input type="range" class="topbar-slider" id="rngPlayroomImgDur" min="2" max="30" value="5" oninput="document.getElementById('lblPlayroomImgDur').textContent = this.value + ' วินาที'">
          </div>
        </div>
      </div>

      <!-- TAB 3: ทดสอบ & จำลองแชท -->
      <div id="panePlayroomTab3" style="display:none;">
        <div class="section-card" style="margin-bottom:14px;">
          <div class="section-card-title">
            <span>📺 เครื่องมือจำลองคำสั่งแชทสด & จอพรีวิว</span>
          </div>
          <div class="modal-form-group" style="margin-bottom:12px;">
            <label class="modal-form-label">พิมพ์คำสั่งจำลองเพื่อทดสอบการทำงาน</label>
            <div style="display:flex; gap:8px;">
              <input type="text" class="modal-input" id="txtPlayroomSimCmd" value="!fortune" placeholder="เช่น !fortune หรือ !scare">
              <button class="btn-topbar-action primary" onclick="runPlayroomSimulatedChat()">🚀 ยิงคำสั่งทดสอบ</button>
            </div>
          </div>

          <div style="background:#111214; border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:16px; text-align:center; min-height:160px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <div id="playroomMonitorContent" style="width:100%; display:flex; flex-direction:column; align-items:center; gap:8px;">
              <span style="font-size:28px;">🎮</span>
              <span style="color:#94a3b8; font-size:13px;" id="lblPlayroomMonitorStatus">รอคำสั่งจากแชทสด หรือกดปุ่ม "▶ ทดสอบยิงคลิป"</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="floating-footer">
      <div style="display:flex; align-items:center; gap:8px;">
        <span style="background:#10b981; width:8px; height:8px; border-radius:50%; display:inline-block;"></span>
        <span style="font-size:12px; color:#94a3b8;">ระบบเชื่อมต่อกับ Overlay Canvas แล้ว</span>
      </div>
      <div class="floating-footer-right">
        <button class="btn-topbar-action" onclick="closeToolWindow('playroom')">พับเก็บ</button>
        <button class="btn-topbar-action primary" onclick="playroomFireActiveClip()">
          ▶ ยิงคลิปล่าสุดขึ้นจอ
        </button>
      </div>
    </div>
  </div>\n'''
    if '\r\n' in html:
        playroom_window_html = playroom_window_html.replace('\n', '\r\n')

    settings_target = '<!-- ========================================================\n       WINDOW 5: SYSTEM SETTINGS'
    if settings_target not in html:
        settings_target = settings_target.replace('\n', '\r\n')
    
    if settings_target in html:
        html = html.replace(settings_target, playroom_window_html + '\n  ' + settings_target, 1)
        print("Successfully added #win-playroom markup!")
    else:
        print("WARNING: settings_target not found!")

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html markup done!")
