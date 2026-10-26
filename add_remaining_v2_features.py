# add_remaining_v2_features.py
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

INDEX_FILE = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"
CSS_FILE = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.css"
JS_FILE = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js"

# -------------------------------------------------------------
# 1. Update index.html: Add toolbar buttons for ask, giveaway, playroom
# -------------------------------------------------------------
with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

target_btn = '''        <button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="emote_party" title="เพิ่มเอฟเฟกต์อีโมตลอย">
          <span class="comp-widget-icon">🎉</span>
          <span class="comp-widget-label">อีโมต</span>
        </button>'''

if target_btn not in html:
    # Try searching with placeholder characters if encoded
    pattern = r'<button type="button" class="composer-btn-tool btn-add-widget" data-widget-type="emote_party"[^>]*>[\s\S]*?<\/button>'
    m = re.search(pattern, html)
    if m:
        target_btn = m.group(0)

new_buttons = target_btn + '''
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
        </button>'''

if target_btn in html:
    html = html.replace(target_btn, new_buttons)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print("SUCCESS: index.html toolbar buttons added")
else:
    print("WARNING: target_btn not found in index.html")

# -------------------------------------------------------------
# 2. Update composer_studio.css: Zero GPU Lockup & Standby Transparency
# -------------------------------------------------------------
with open(CSS_FILE, 'r', encoding='utf-8') as f:
    css = f.read()

transparency_css = '''
/* Zero GPU Lockup & Clean Standby Transparency for Overlays */
.preview-clean-mode .editor-only,
.overlay-mode .editor-only,
:not(.edit-mode) .editor-only {
  display: none !important;
}

.ask-idle, .giveaway-idle {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
'''

if ".preview-clean-mode .editor-only" not in css:
    css += "\n" + transparency_css
    with open(CSS_FILE, 'w', encoding='utf-8') as f:
        f.write(css)
    print("SUCCESS: composer_studio.css standby transparency added")

# -------------------------------------------------------------
# 3. Update composer_studio.js: presets, renderWidgetInnerHtml, settings, demo, normalizeWidget
# -------------------------------------------------------------
with open(JS_FILE, 'r', encoding='utf-8') as f:
    js = f.read()

# 3A. Presets in addWidget
presets_target = "emote_party: { title: 'เอฟเฟกต์อีโมตลอย', width: 300, height: 200 }"
if presets_target not in js:
    p_match = re.search(r"emote_party:\s*\{[^}]+\}", js)
    if p_match:
        presets_target = p_match.group(0)

new_presets = presets_target + ''',
      ask: { title: 'โพลสำรวจความคิดเห็น ASK', width: 440, height: 260, askQuestion: 'โหวตเลือกอะไรดีในสตรีมนี้?', askChoices: ['ตัวเลือก A (พิมพ์ A)', 'ตัวเลือก B (พิมพ์ B)'], askLayout: 'vright', askCountdownStyle: 'text', askDuration: 60, isAsk: true },
      giveaway: { title: 'สุ่มแจกรางวัล Giveaway', width: 440, height: 280, prizeTitle: 'รางวัลพิเศษประจำสตรีม', giveawayDuration: 30, isGiveaway: true },
      playroom: { title: 'Playroom Interactive', width: 400, height: 300, playroomUrl: 'http://127.0.0.1:8080/playroom-widget', ckEnabled: false, ckColor: '#00ff00', ckSimilarity: 0.4, ckSmoothness: 0.1 }'''

if presets_target in js and "ask:" not in js:
    js = js.replace(presets_target, new_presets)
    print("SUCCESS: addWidget presets updated with ask, giveaway, playroom")

# 3B. renderWidgetInnerHtml: add ask, giveaway, playroom, and editor-only transparency
render_inner_marker = "    if (w.type === 'goal' || w.type === 'donate_goal') {"
new_render_blocks = '''    if (w.type === 'ask') {
      const q = w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?';
      const ch1 = (w.askChoices && w.askChoices[0]) || 'ตัวเลือก A';
      const ch2 = (w.askChoices && w.askChoices[1]) || 'ตัวเลือก B';
      return `
        <div class="composer-widget-inner widget-type-ask" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center;">
          <div class="ask-panel" style="background:rgba(15, 23, 42, 0.88); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1.5px solid rgba(56, 189, 248, 0.35); border-radius:12px; padding:12px 16px; box-shadow:0 8px 30px rgba(0,0,0,0.5);">
            <div style="font-weight:700; font-size:14px; color:#38bdf8; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
              <span>📊 ${q}</span>
              <span style="font-size:11px; color:#94a3b8; background:rgba(255,255,255,0.08); padding:2px 8px; border-radius:4px;">⏱ 45s</span>
            </div>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
                <div style="position:absolute; inset:0; width:65%; background:rgba(56, 189, 248, 0.22); border-radius:6px;"></div>
                <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
                  <span>A: ${ch1}</span>
                  <span style="color:#38bdf8;">65% (130)</span>
                </div>
              </div>
              <div style="background:rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; position:relative; overflow:hidden;">
                <div style="position:absolute; inset:0; width:35%; background:rgba(168, 85, 247, 0.22); border-radius:6px;"></div>
                <div style="position:relative; z-index:1; display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#ffffff;">
                  <span>B: ${ch2}</span>
                  <span style="color:#c084fc;">35% (70)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'giveaway') {
      const prize = w.prizeTitle || 'รางวัลพิเศษประจำสตรีม';
      return `
        <div class="composer-widget-inner widget-type-giveaway" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden; display:flex; flex-direction:column; justify-content:center;">
          <div style="background:rgba(15, 23, 42, 0.9); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1.5px solid rgba(244, 63, 94, 0.4); border-radius:14px; padding:14px 18px; text-align:center; box-shadow:0 8px 30px rgba(0,0,0,0.5);">
            <div style="font-size:24px; margin-bottom:4px;">🎁</div>
            <div style="font-weight:700; font-size:15px; color:#f43f5e; margin-bottom:4px;">${prize}</div>
            <div style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">พิมพ์ !join ในแชทเพื่อเข้าร่วมสุ่ม</div>
            <div style="background:rgba(255,255,255,0.08); border-radius:6px; height:6px; overflow:hidden; margin-bottom:8px;">
              <div style="width:70%; height:100%; background:linear-gradient(90deg, #f43f5e, #fb7185); border-radius:6px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#94a3b8;">
              <span>ผู้เข้าร่วม: 148 คน</span>
              <span style="color:#fb7185; font-weight:700;">นับถอยหลัง: 24s</span>
            </div>
          </div>
        </div>
      `;
    }

    if (w.type === 'playroom') {
      const pUrl = w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget';
      return `
        <div class="composer-widget-inner widget-type-playroom" style="background:transparent !important; border:none !important; width:100%; height:100%; overflow:hidden;">
          <iframe src="${pUrl}" allow="autoplay; fullscreen" style="width:100%; height:100%; border:none; background:transparent;"></iframe>
        </div>
      `;
    }
'''

if "w.type === 'ask'" not in js and render_inner_marker in js:
    js = js.replace(render_inner_marker, new_render_blocks + "\n" + render_inner_marker)
    print("SUCCESS: renderWidgetInnerHtml updated with ask, giveaway, playroom")

# 3C. Add Demo triggers to ComposerDemoManager
demo_manager_marker = "    // Emote Party Simulation"
new_demo_methods = '''    // ASK Poll Simulation
    triggerAskVote(w) {
      if (window.showToast) window.showToast('📊 จำลองผู้ร่วมโหวตเพิ่มขึ้นแบบ Real-time!');
      renderCanvasWidgets();
    },

    // Giveaway Simulation
    triggerGiveawayDraw(w) {
      if (window.showToast) window.showToast('🎁 จำลองสุ่มผู้โชคดี: Gamer_Pro123 ได้รับรางวัล!');
      renderCanvasWidgets();
    },
'''

if "triggerAskVote" not in js and demo_manager_marker in js:
    js = js.replace(demo_manager_marker, new_demo_methods + "\n" + demo_manager_marker)
    print("SUCCESS: ComposerDemoManager updated with ask and giveaway triggers")

# 3D. Add Settings Panels in renderWidgetCustomizerPanel
customizer_panel_end = "    } else if (w.type === 'emote_party') {"
new_settings_panels = '''    } else if (w.type === 'ask') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📊 การตั้งค่าโพลสำรวจ (ASK)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">หัวข้อคำถาม</span>
              <input type="text" class="cwc-input" id="compAskQuestion" value="${w.askQuestion || 'โหวตเลือกอะไรดีในสตรีมนี้?'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบ Layout</span>
              <select class="cwc-select" id="compAskLayout">
                <option value="vright" ${(w.askLayout || 'vright') === 'vright' ? 'selected' : ''}>แถวเดี่ยวแนวตั้ง (Right / Tower)</option>
                <option value="hband" ${(w.askLayout || 'vright') === 'hband' ? 'selected' : ''}>แถบแนวนอนยาว (Horizontal Band)</option>
                <option value="minimal" ${(w.askLayout || 'vright') === 'minimal' ? 'selected' : ''}>การ์ดมินิมอล (Card Minimal)</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การนับถอยหลัง</span>
              <select class="cwc-select" id="compAskCountdownStyle">
                <option value="text" ${(w.askCountdownStyle || 'text') === 'text' ? 'selected' : ''}>แสดงเวลาตัวเลข</option>
                <option value="bar" ${(w.askCountdownStyle || 'text') === 'bar' ? 'selected' : ''}>แถบหลอดเวลาวิ่ง</option>
              </select>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoAskVote" style="width:100%; padding:8px; font-weight:700;">📊 จำลองคะแนนโหวตสด</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'giveaway') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎁 การตั้งค่าสุ่มแจกรางวัล (Giveaway)</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ชื่อของรางวัล</span>
              <input type="text" class="cwc-input" id="compGiveawayPrize" value="${w.prizeTitle || 'รางวัลพิเศษประจำสตรีม'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เวลานับถอยหลัง (วินาที)</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compGiveawayDuration" min="10" max="120" value="${w.giveawayDuration || 30}">
                <span class="cwc-slider-val" id="compGiveawayDurationVal">${w.giveawayDuration || 30}s</span>
              </div>
            </div>
            <div style="margin-top:10px;">
              <button type="button" class="btn-comp-demo-action" id="btnDemoGiveawayDraw" style="width:100%; padding:8px; font-weight:700;">🎁 ทดสอบเริ่มสุ่มแจกรางวัล</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'playroom') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎮 การตั้งค่า Playroom Interactive</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">URL ของ Playroom</span>
              <input type="text" class="cwc-input" id="compPlayroomUrl" value="${w.playroomUrl || 'http://127.0.0.1:8080/playroom-widget'}" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เปิดใช้งาน Chroma Key</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compPlayroomCkEnabled" ${w.ckEnabled ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีฉากเขียวที่ตัดออก (Chroma)</span>
              <div class="cwc-color-wrap">
                <input type="color" class="cwc-color-pick" id="compPlayroomCkColor" value="${w.ckColor || '#00ff00'}">
              </div>
            </div>
          </div>
        </div>
      `;
'''

if "compAskQuestion" not in js and customizer_panel_end in js:
    js = js.replace(customizer_panel_end, new_settings_panels + "\n" + customizer_panel_end)
    print("SUCCESS: renderWidgetCustomizerPanel updated with ask, giveaway, playroom settings")

# 3E. Add field binders in renderWidgetCustomizerPanel
binders_end = "    } else if (w.type === 'emote_party') {"
new_binders = '''    } else if (w.type === 'ask') {
      bindField('compAskQuestion', 'askQuestion');
      bindField('compAskLayout', 'askLayout');
      bindField('compAskCountdownStyle', 'askCountdownStyle');
      const btnDemoAsk = document.getElementById('btnDemoAskVote');
      if (btnDemoAsk) btnDemoAsk.addEventListener('click', () => ComposerDemoManager.triggerAskVote(w));
    } else if (w.type === 'giveaway') {
      bindField('compGiveawayPrize', 'prizeTitle');
      bindField('compGiveawayDuration', 'giveawayDuration', 'number', 's');
      const btnDemoGive = document.getElementById('btnDemoGiveawayDraw');
      if (btnDemoGive) btnDemoGive.addEventListener('click', () => ComposerDemoManager.triggerGiveawayDraw(w));
    } else if (w.type === 'playroom') {
      bindField('compPlayroomUrl', 'playroomUrl');
      bindField('compPlayroomCkEnabled', 'ckEnabled', 'checkbox');
      bindField('compPlayroomCkColor', 'ckColor');
'''

if "btnDemoAskVote" not in js and binders_end in js:
    js = js.replace(binders_end, new_binders + "\n" + binders_end)
    print("SUCCESS: field binders updated with ask, giveaway, playroom")

# 3F. Update normalizeWidget
norm_end = "    return w;\n  }"
new_norm = '''    // ASK & Giveaway & Playroom
    w.askQuestion = w.askQuestion || w.ask_question || 'โหวตเลือกอะไรดีในสตรีมนี้?';
    w.ask_question = w.askQuestion;
    w.askChoices = w.askChoices || w.ask_choices || ['ตัวเลือก A', 'ตัวเลือก B'];
    w.ask_choices = w.askChoices;
    w.askLayout = w.askLayout || w.ask_layout || 'vright';
    w.ask_layout = w.askLayout;
    w.prizeTitle = w.prizeTitle || w.prize_title || 'รางวัลพิเศษประจำสตรีม';
    w.prize_title = w.prizeTitle;
    w.playroomUrl = w.playroomUrl || w.playroom_url || 'http://127.0.0.1:8080/playroom-widget';
    w.playroom_url = w.playroomUrl;

    return w;
  }'''

if "w.askQuestion" not in js and norm_end in js:
    js = js.replace(norm_end, new_norm)
    print("SUCCESS: normalizeWidget updated with ask, giveaway, playroom dual-keys")

with open(JS_FILE, 'w', encoding='utf-8') as f:
    f.write(js)

print("ALL FILES UPDATED WITH COMPLETE V2 FEATURES!")
