import os

path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add btnCompTestBrowser to Composer Studio toolbar
old_btn = '''        <button type="button" class="composer-btn-tool primary" id="btnCompCopyObs" title="คัดลอกลิงก์ Overlay สำหรับ OBS">

          🔗 ลิงก์ OBS

        </button>'''

new_btn = '''        <button type="button" class="composer-btn-tool primary" id="btnCompCopyObs" title="คัดลอกลิงก์ Overlay สำหรับ OBS">

          🔗 ลิงก์ OBS

        </button>

        <button type="button" class="composer-btn-tool" id="btnCompTestBrowser" title="เปิดหน้าต่างทดสอบหน้าจอ Overlay สดในเบราว์เซอร์ทันที">

          🧪 ทดสอบในเบราว์เซอร์

        </button>'''

if old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("Added btnCompTestBrowser")
else:
    print("Warning: old_btn not found")

# 2. Update Settings OBS section
old_settings = '''          <div class="section-card" style="margin-bottom: 12px;">

            <div class="section-card-title">1. แผงควบคุมสด</div>

            <div style="display:flex; gap:8px;">

              <input type="text" class="modal-input" value="http://127.0.0.1:8080/composer.html" style="flex:1;" readonly>

              <button class="btn-topbar-action" style="height:36px;" onclick="copyObsUrl()">คัดลอก</button>

            </div>

          </div>



          <div class="section-card">

            <div class="section-card-title">2. โอเวอร์เลย์รวมบนจอ</div>

            <div style="display:flex; gap:8px;">

              <input type="text" class="modal-input" value="http://127.0.0.1:8080/overlay.html" style="flex:1;" readonly>

              <button class="btn-topbar-action" style="height:36px;" onclick="navigator.clipboard.writeText('http://127.0.0.1:8080/overlay.html'); showToast('📋 คัดลอก Overlay URL แล้ว')">คัดลอก</button>

            </div>

          </div>'''

new_settings = '''          <div class="section-card" style="margin-bottom: 12px;">

            <div class="section-card-title">🖥️ 1. โอเวอร์เลย์รวมบนจอ (OBS Browser Source)</div>

            <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">ความละเอียด 1920×1080 พิกเซล พื้นหลังโปร่งใส ซิงค์ทุกวิดเจ็ตอัตโนมัติ</div>

            <div style="display:flex; gap:8px;">

              <input type="text" class="modal-input" id="inpSettingsObsOverlayUrl" value="http://127.0.0.1:8080/composer.html" style="flex:1;" readonly>

              <button class="btn-topbar-action" style="height:36px;" onclick="copyObsUrl()">📋 คัดลอก</button>

              <button class="btn-topbar-action" style="height:36px; background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.4);" onclick="window.open('http://127.0.0.1:8080/composer.html?test=1', '_blank')">🧪 เปิดทดสอบสด</button>

            </div>

          </div>



          <div class="section-card">

            <div class="section-card-title">🎛️ 2. แผงควบคุมสดใน OBS (OBS Custom Browser Dock)</div>

            <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">นำไปใส่ในเมนู Docks -> Custom Browser Docks ของ OBS Studio</div>

            <div style="display:flex; gap:8px;">

              <input type="text" class="modal-input" id="inpSettingsObsDockUrl" value="http://127.0.0.1:8080/dock.html" style="flex:1;" readonly>

              <button class="btn-topbar-action" style="height:36px;" onclick="navigator.clipboard.writeText('http://127.0.0.1:8080/dock.html'); showToast('📋 คัดลอก OBS Dock URL แล้ว')">📋 คัดลอก</button>

              <button class="btn-topbar-action" style="height:36px; background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.4);" onclick="window.open('http://127.0.0.1:8080/dock.html', '_blank')">🧪 เปิดทดสอบ</button>

            </div>

          </div>'''

if old_settings in content:
    content = content.replace(old_settings, new_settings, 1)
    print("Updated settings OBS cards")
else:
    print("Warning: old_settings not found")

# 3. Update topbar context menu for overlay
old_ctx = '''          { text: '📋 คัดลอก Overlay URL (สำหรับ OBS)', run: () => copyObsUrl() },

          { text: '🖥️ เปิด Composer Canvas Studio', run: () => showToast('🎛️ เปิด Composer Canvas Studio ในเบราว์เซอร์') }'''

new_ctx = '''          { text: '📋 คัดลอก Overlay URL (สำหรับ OBS)', run: () => copyObsUrl() },

          { text: '🧪 เปิดทดสอบสดในเบราว์เซอร์', run: () => window.open('http://127.0.0.1:8080/composer.html?test=1', '_blank') },

          { text: '🖥️ เปิด Composer Canvas Studio', run: () => openToolWindow('composer') }'''

if old_ctx in content:
    content = content.replace(old_ctx, new_ctx, 1)
    print("Updated topbar context menu")
else:
    print("Warning: old_ctx not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Copy to dist/index.html
dist_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html'
with open(dist_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated src/index.html and dist/index.html successfully!")
