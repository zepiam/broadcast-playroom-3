with open("src/index.html", "r", encoding="utf-8") as f:
    text = f.read()

def normalize(t):
    return t.replace("\r\n", "\n")

# 1. Update toolbar buttons
old_toolbar_btns = """        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="goal" title="เพิ่มเป้าหมายผู้ติดตาม">
          🎯 เป้าหมาย
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="image" title="เพิ่มกรอบรูปภาพ">
          🖼️ รูปภาพ
        </button>
      </div>"""

new_toolbar_btns = """        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="goal" title="เพิ่มเป้าหมายผู้ติดตาม">
          🎯 เป้าหมาย
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="viewer" title="เพิ่มตัวนับยอดผู้ชมสด">
          👥 ผู้ชม
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="image" title="เพิ่มกรอบรูปภาพ">
          🖼️ รูปภาพ
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="video" title="เพิ่มวิดีโอลูป">
          🎬 วิดีโอ
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="alert" title="เพิ่มเบราว์เซอร์ URL ภายนอก">
          🌐 เว็บ URL
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="now_playing" title="เพิ่มเพลงที่กำลังเล่น">
          🎵 กำลังเล่น
        </button>
        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="emote_party" title="เพิ่มปาร์ตี้อีโมทลอย">
          🎉 อีโมท
        </button>
      </div>"""

# 2. Insert left customizer panel before viewport
old_split_start = """    <!-- Main Workspace Split -->
    <div class="composer-main-split">
      <!-- Left / Center: Virtual 1920x1080 Viewport -->
      <div class="composer-viewport" id="composerViewport">"""

new_split_start = """    <!-- Main Workspace Split -->
    <div class="composer-main-split" style="position:relative;">
      <!-- Left Customizer Panel (Slides in when widget is clicked, collapsible) -->
      <div class="composer-sidebar-left collapsed" id="composerSidebarLeft">
        <div class="composer-side-header composer-customizer-header">
          <div style="display:flex; align-items:center; gap:8px; min-width:0;">
            <span id="compCustIcon" style="font-size:18px;">🎨</span>
            <div style="min-width:0;">
              <div id="compCustTitle" style="font-size:13.5px; font-weight:700; color:#f2f3f5; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">ปรับแต่งวิดเจ็ต</div>
              <div id="compCustType" style="font-size:11px; color:var(--dc-text-muted);">เลือกวิดเจ็ตเพื่อตั้งค่า</div>
            </div>
          </div>
          <button type="button" class="composer-btn-collapse" id="btnCollapseCustPanel" title="หุบแถบตั้งค่าเพื่อดูภาพรวมจอ">
            ◀ หุบแถบ
          </button>
        </div>

        <div class="composer-customizer-body" id="composerCustomizerBody">
          <!-- Populated dynamically when widget is selected -->
        </div>
      </div>

      <!-- Floating Expand Button (when left panel is collapsed) -->
      <button type="button" class="composer-btn-expand-left" id="btnExpandCustPanel" title="เปิดแถบปรับแต่งวิดเจ็ต">
        ⚙️ ปรับแต่งวิดเจ็ต ▶
      </button>

      <!-- Center: Virtual 1920x1080 Viewport -->
      <div class="composer-viewport" id="composerViewport">"""

# 3. Update right sidebar props
old_props = """        <div class="composer-props-body">
          <div class="composer-prop-row">
            <span class="composer-prop-label">พิกัด X:</span>
            <input type="number" class="composer-prop-input" id="compPropX" step="5">
            <span class="composer-prop-label">พิกัด Y:</span>
            <input type="number" class="composer-prop-input" id="compPropY" step="5">
          </div>
          <div class="composer-prop-row">
            <span class="composer-prop-label">กว้าง W:</span>
            <input type="number" class="composer-prop-input" id="compPropW" step="10">
            <span class="composer-prop-label">สูง H:</span>
            <input type="number" class="composer-prop-input" id="compPropH" step="10">
          </div>
          <div class="composer-prop-row">
            <span class="composer-prop-label">ความทึบ:</span>
            <input type="text" class="composer-prop-input" id="compPropOp" readonly>
          </div>
        </div>"""

new_props = """        <div class="composer-props-body">
          <div class="composer-props-grid">
            <div class="composer-prop-col">
              <span class="composer-prop-label">พิกัด X</span>
              <input type="number" class="composer-prop-input" id="compPropX" step="5">
            </div>
            <div class="composer-prop-col">
              <span class="composer-prop-label">พิกัด Y</span>
              <input type="number" class="composer-prop-input" id="compPropY" step="5">
            </div>
            <div class="composer-prop-col">
              <span class="composer-prop-label">ความกว้าง W</span>
              <input type="number" class="composer-prop-input" id="compPropW" step="10">
            </div>
            <div class="composer-prop-col">
              <span class="composer-prop-label">ความสูง H</span>
              <input type="number" class="composer-prop-input" id="compPropH" step="10">
            </div>
          </div>
          <div class="composer-prop-col" style="margin-top:6px;">
            <span class="composer-prop-label">ความทึบแสง</span>
            <input type="text" class="composer-prop-input" id="compPropOp" readonly>
          </div>
        </div>"""

text_norm = normalize(text)

if normalize(old_toolbar_btns) in text_norm:
    text_norm = text_norm.replace(normalize(old_toolbar_btns), normalize(new_toolbar_btns), 1)
    print("Updated toolbar buttons")
else:
    print("Could not find old_toolbar_btns")

if normalize(old_split_start) in text_norm:
    text_norm = text_norm.replace(normalize(old_split_start), normalize(new_split_start), 1)
    print("Inserted left customizer panel")
else:
    print("Could not find old_split_start")

if normalize(old_props) in text_norm:
    text_norm = text_norm.replace(normalize(old_props), normalize(new_props), 1)
    print("Updated right sidebar props layout")
else:
    print("Could not find old_props")

with open("src/index.html", "w", encoding="utf-8") as f:
    f.write(text_norm)

print("Updated src/index.html successfully!")
