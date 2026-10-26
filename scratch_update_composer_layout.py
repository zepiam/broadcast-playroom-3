import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# ---------------------------------------------------------------------------
# 1. Update win-composer Header and Topbar Layout (Row 1, Row 2, Row 3)
# ---------------------------------------------------------------------------
comp_header_start = text.find('<!-- Window Header -->\n    <div class="floating-header" id="drag-composer"')
if comp_header_start == -1:
    comp_header_start = text.find('id="drag-composer"')
    # find enclosing <div
    comp_header_start = text.rfind('<div class="floating-header"', 0, comp_header_start)

comp_main_split = text.find('<div class="composer-main-split"', comp_header_start)

assert comp_header_start != -1 and comp_main_split != -1, "Composer header/main-split not found"

new_composer_toolbar_html = """<!-- Window Header (Row 1: Title & Main Action Buttons) -->
    <div class="floating-header" id="drag-composer" ondblclick="toggleMaximizeWindow('composer')">
      <div class="floating-title-box">
        <span style="font-size: 20px;">🎬</span>
        <div>
          <div style="font-size: 14.5px; font-weight: 700; color: #f2f3f5;">Overlay Composer Studio</div>
          <div style="font-size: 11px; color: var(--dc-text-muted);">จัดวางเลย์เอาต์หน้าจอและวิดเจ็ตสตรีมมิ่งสดโดยไม่ต้องเปิดเบราว์เซอร์</div>
        </div>
      </div>
      <div class="floating-actions-right" style="display:flex; align-items:center; gap:6px;">
        <button type="button" class="composer-btn-tool" id="btnCompPreview" title="สลับโหมดพรีวิว (ซ่อนกรอบเครื่องมือทั้งหมด)">
          👁️ พรีวิว
        </button>
        <button type="button" class="composer-btn-tool" id="btnCompExport" title="สำรองข้อมูลเลย์เอาต์ทั้งหมดเป็นไฟล์ JSON">
          📁 ส่งออก
        </button>
        <button type="button" class="composer-btn-tool" id="btnCompImport" title="นำเข้าไฟล์เลย์เอาต์ JSON จากเวอร์ชั่นเก่าหรือเครื่องอื่น">
          📥 นำเข้า
        </button>
        <input type="file" id="fileCompImportProfile" accept=".json" style="display:none;">
        <button type="button" class="composer-btn-tool primary" id="btnCompCopyObs" title="คัดลอกลิงก์ Overlay สำหรับ OBS">
          🔗 ลิงก์ OBS
        </button>
        <button type="button" class="composer-btn-tool success" id="btnCompSave" title="บันทึกเลย์เอาต์หน้าจอ">
          💾 บันทึก
        </button>
        <div style="width:1px; height:18px; background:rgba(255,255,255,0.12); margin:0 4px;"></div>
        <button class="btn-win-action" title="ย่อหน้าต่าง" onclick="minimizeWindow('composer')">−</button>
        <button class="btn-win-action" id="btnMaxComposer" title="ขยายเต็มจอ / ย่อขนาดเดิม" onclick="toggleMaximizeWindow('composer')">🗖</button>
        <button class="btn-win-action close-red" title="ปิดหน้าต่าง" onclick="closeToolWindow('composer')">✕</button>
      </div>
    </div>

    <!-- Row 2: Page Tabs & Canvas Controls -->
    <div class="composer-subbar-pages">
      <div style="display:flex; align-items:center; gap:8px; flex:1; overflow-x:auto;">
        <div class="composer-page-tabs" id="composerPageTabs" style="display:flex; align-items:center; gap:6px;">
          <!-- Populated by composer_studio.js -->
        </div>
      </div>
      <!-- View & Zoom Tools -->
      <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
        <button type="button" class="composer-btn-sub" id="btnCompZoomOut" title="ลดขนาด">
          −
        </button>
        <span id="composerZoomVal" style="font-family:'JetBrains Mono',monospace; font-size:11.5px; font-weight:700; color:var(--dc-text-muted); min-width:38px; text-align:center;">
          45%
        </span>
        <button type="button" class="composer-btn-sub" id="btnCompZoomIn" title="ขยายขนาด">
          +
        </button>
        <button type="button" class="composer-btn-sub" id="btnCompZoomFit" title="ย่อขยายให้พอดีกรอบหน้าต่าง">
          พอดีจอ
        </button>
        <button type="button" class="composer-btn-sub active" id="btnCompSnap" title="เปิด/ปิดการจัดแนวแบบแม่เหล็ก">
          🧲 แม่เหล็ก
        </button>
      </div>
    </div>

    <!-- Row 3: Pure Widgets List -->
    <div class="composer-subbar-widgets" id="compAddWidgetsGroup">
      <!-- Chat Widget Dropdown Trigger -->
      <div class="composer-add-btn-wrapper" id="chatAddBtnWrapper">
        <button type="button" class="composer-btn-tool btn-add-widget btn-add-chat-menu" id="btnCompAddChatMenu" title="คลิกเพื่อเลือกรูปแบบแชทและเพิ่มลงหน้าจอ">
          <span class="comp-widget-icon">💬</span>
          <span class="comp-widget-label">แชท ▾</span>
        </button>
        <!-- Chat Subtypes Context Dropdown Menu -->
        <div class="composer-chat-dropdown-menu" id="compChatDropdownMenu" style="display:none;">
          <div class="comp-chat-menu-item" data-chat-mode="default">
            <span class="comp-menu-icon">💬</span>
            <div class="comp-menu-text">
              <div class="comp-menu-title">กล่องแชทมาตรฐาน</div>
              <div class="comp-menu-desc">ปรับขนาดและเลื่อนอิสระ ปรับแต่งค่ามาตรฐานและ 80 ธีมสำเร็จรูป</div>
            </div>
          </div>
          <div class="comp-chat-menu-item" data-chat-mode="danmaku">
            <span class="comp-menu-icon">⚡</span>
            <div class="comp-menu-text">
              <div class="comp-menu-title">แชทลอยหน้าจอ ดันมากุ</div>
              <div class="comp-menu-desc">ข้อความวิ่งเต็มผืนผ้าใบหน้าจอ ล็อคขนาดเต็มจอ ปรับแต่งเฉพาะดันมากุ</div>
            </div>
          </div>
          <div class="comp-chat-menu-item" data-chat-mode="balloon">
            <span class="comp-menu-icon">🗯️</span>
            <div class="comp-menu-text">
              <div class="comp-menu-title">บอลลูนแชท</div>
              <div class="comp-menu-desc">กล่องคำพูดบอลลูนสไตล์การ์ตูน ย่อขยายได้อิสระ ปรับแต่งเฉพาะบอลลูน</div>
            </div>
          </div>
          <div class="comp-chat-menu-item" data-chat-mode="character">
            <span class="comp-menu-icon">🎭</span>
            <div class="comp-menu-text">
              <div class="comp-menu-title">แชทตัวละคร</div>
              <div class="comp-menu-desc">กล่องสนทนาพร้อมอวาตาร์ตัวละคร เปลี่ยนรูปภาพตัวละครและปรับแต่งอิสระ</div>
            </div>
          </div>
        </div>
      </div>

      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="clock" title="เพิ่มนาฬิกาสตรีม">
        <span class="comp-widget-icon">🕒</span>
        <span class="comp-widget-label">นาฬิกา</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="text" title="เพิ่มแถบข้อความประกาศ">
        <span class="comp-widget-icon">🔤</span>
        <span class="comp-widget-label">ข้อความ</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="character" title="เพิ่มตัวละคร Replie">
        <span class="comp-widget-icon">🎭</span>
        <span class="comp-widget-label">ตัวละคร</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="webcam" title="เพิ่มกรอบกล้องเว็บแคม">
        <span class="comp-widget-icon">📹</span>
        <span class="comp-widget-label">เว็บแคม</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="goal" title="เพิ่มเป้าหมายผู้ติดตาม">
        <span class="comp-widget-icon">🎯</span>
        <span class="comp-widget-label">เป้าหมาย</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="viewer" title="เพิ่มตัวนับยอดผู้ชมสด">
        <span class="comp-widget-icon">👥</span>
        <span class="comp-widget-label">ผู้ชม</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="image" title="เพิ่มกรอบรูปภาพ">
        <span class="comp-widget-icon">🖼️</span>
        <span class="comp-widget-label">รูปภาพ</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="video" title="เพิ่มวิดีโอลูป">
        <span class="comp-widget-icon">🎬</span>
        <span class="comp-widget-label">วิดีโอ</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="alert" title="เพิ่มเบราว์เซอร์ URL">
        <span class="comp-widget-icon">🌐</span>
        <span class="comp-widget-label">เว็บ URL</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="now_playing" title="เพิ่มเพลงที่กำลังเล่น">
        <span class="comp-widget-icon">🎵</span>
        <span class="comp-widget-label">กำลังเล่น</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="emote_party" title="เพิ่มปาร์ตี้อีโมทลอย">
        <span class="comp-widget-icon">🎉</span>
        <span class="comp-widget-label">อีโมท</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="ask" title="เพิ่มโพลสำรวจความคิดเห็น (ASK)">
        <span class="comp-widget-icon">📊</span>
        <span class="comp-widget-label">โพล ASK</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="giveaway" title="เพิ่มสุ่มแจกรางวัล (Giveaway)">
        <span class="comp-widget-icon">🎁</span>
        <span class="comp-widget-label">Giveaway</span>
      </button>
      <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="playroom" title="เพิ่ม Playroom Interactive Mini-game">
        <span class="comp-widget-icon">🎮</span>
        <span class="comp-widget-label">Playroom</span>
      </button>
    </div>

    """

text = text[:comp_header_start] + new_composer_toolbar_html + text[comp_main_split:]
print("Applied 3-Row Composer Toolbar layout.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved updated index.html successfully.")
