# -*- coding: utf-8 -*-
import os

js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

idx_cust_start = code.find('function renderWidgetCustomizerPanel(id) {')
old_toolbar_snippet = """    // Add Widget Buttons
    document.querySelectorAll('.btn-add-widget').forEach(btn => {
      btn.addEventListener('click', () => {
        addWidget(btn.dataset.widgetType);
      });
    });"""

idx_toolbar = code.find(old_toolbar_snippet)
print("idx_cust_start:", idx_cust_start)
print("idx_toolbar:", idx_toolbar)

new_customizer_and_toolbar = r"""function renderWidgetCustomizerPanel(id) {
    const page = getActivePage();
    if (!page) return;
    const w = page.widgets.find(x => x.id === id);
    if (!w) return;

    const iconEl = document.getElementById('compCustIcon');
    const titleEl = document.getElementById('compCustTitle');
    const typeEl = document.getElementById('compCustType');
    const bodyEl = document.getElementById('composerCustomizerBody');
    if (!bodyEl) return;

    // Determine customizer title based on type and chatMode
    let dispTitle = w.title;
    let dispType = 'การปรับแต่งวิดเจ็ต';
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        dispTitle = 'แชทลอยหน้าจอ ดันมากุ';
        dispType = 'วิดเจ็ตแชทลอยหน้าจอแบบ Danmaku';
      } else if (mode === 'balloon') {
        dispTitle = 'บอลลูนแชท';
        dispType = 'วิดเจ็ตแชทสไตล์บอลลูนคำพูด';
      } else if (mode === 'character') {
        dispTitle = 'แชทตัวละคร';
        dispType = 'วิดเจ็ตแชทพร้อมตัวละครสนทนา';
      } else {
        dispTitle = 'กล่องแชทมาตรฐาน';
        dispType = 'วิดเจ็ตกล่องแชทสด';
      }
    } else {
      const typeNames = {
        clock: 'วิดเจ็ตนาฬิกาสตรีม',
        text: 'วิดเจ็ตแถบข้อความประกาศ',
        webcam: 'วิดเจ็ตกรอบเว็บแคม',
        goal: 'วิดเจ็ตเป้าหมายยอดผู้ติดตาม',
        viewer: 'วิดเจ็ตตัวนับยอดผู้ชมสด',
        character: 'วิดเจ็ตตัวละครพูด Replie',
        image: 'วิดเจ็ตกรอบรูปภาพแบนเนอร์',
        video: 'วิดเจ็ตวิดีโอลูป',
        alert: 'วิดเจ็ตเบราว์เซอร์ URL ภายนอก',
        now_playing: 'วิดเจ็ตเพลงที่กำลังเล่น',
        emote_party: 'วิดเจ็ตปาร์ตี้อีโมทลอย'
      };
      dispType = typeNames[w.type] || 'การปรับแต่งวิดเจ็ต';
    }

    if (iconEl) iconEl.textContent = getWidgetIcon(w.type);
    if (titleEl) titleEl.textContent = dispTitle;
    if (typeEl) typeEl.textContent = dispType;

    // Helper binder for inputs
    const bindField = (elId, key, type = 'text', suffix = '') => {
      const el = document.getElementById(elId);
      if (!el) return;
      const handler = () => {
        if (type === 'checkbox') {
          w[key] = el.checked;
        } else if (type === 'number') {
          w[key] = parseFloat(el.value);
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + suffix;
        } else if (type === 'opacity') {
          w[key] = parseFloat(el.value) / 100;
          const lbl = document.getElementById(elId + 'Val');
          if (lbl) lbl.textContent = el.value + '%';
        } else {
          w[key] = el.value;
        }
        renderCanvasWidgets();
        renderLayersList();
        updateTransformInspector();
        saveState();
      };
      el.addEventListener('input', handler);
      el.addEventListener('change', handler);
    };

    // Build Demo Action Bar HTML
    let demoHtml = '';
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">⚡ ทดสอบกระสุนดันมากุ</span>
              <span style="font-size:11px; color:#94a3b8;">วิ่งบนจอตามโซน</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuLoop">▶ เล่นกระสุนดันมากุสด</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoDanmakuSingle">⚡ ปล่อย 1 ข้อความ</button>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">💬 ทดสอบบอลลูนคำพูด</span>
              <span style="font-size:11px; color:#94a3b8;">บอลลูนเด้งสด</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoBalloonSingle">💬 ส่งบอลลูน 1 ข้อความ</button>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">🎭 ทดสอบบทพูดตัวละคร</span>
              <span style="font-size:11px; color:#94a3b8;">ตัวละครขยับพร้อมคำพูด</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoCharTalk">▶ ทดสอบบทพูดตัวละครสด</button>
            </div>
          </div>
        `;
      } else {
        demoHtml = `
          <div class="comp-demo-section">
            <div class="comp-demo-header">
              <span class="comp-demo-title">🎮 ทดสอบเล่นเดโมสด</span>
              <span style="font-size:11px; color:#94a3b8;">จำลองแชทแบบสตรีมจริง</span>
            </div>
            <div class="comp-demo-actions">
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatLoop">▶ เล่นจำลองแชทสด</button>
              <button type="button" class="btn-comp-demo-action" id="btnDemoChatSingle">➕ ส่งแชท 1 ข้อความ</button>
            </div>
          </div>
        `;
      }
    } else if (w.type === 'clock') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🕒 ทดสอบสลับรูปแบบเวลา</span>
            <span style="font-size:11px; color:#94a3b8;">นาฬิกาเดินสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockToggle">🕒 สลับ 12 / 24 ชม.</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoClockSecs">⏱️ สลับแสดงวินาที</button>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🔤 ทดสอบตัววิ่ง Marquee</span>
            <span style="font-size:11px; color:#94a3b8;">ข้อความเลื่อนวิ่งสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoTextTicker">▶ สลับโหมดตัววิ่ง</button>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">📹 ทดสอบสถานะเว็บแคม</span>
            <span style="font-size:11px; color:#94a3b8;">ไฟกระพริบ REC และมิเตอร์เสียง</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoWebcamRec">🔴 สลับไฟสถานะ REC</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoWebcamAudio">🎙️ ทดสอบมิเตอร์เสียงสด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'goal') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎯 ทดสอบยอดเป้าหมาย</span>
            <span style="font-size:11px; color:#94a3b8;">หลอดเพิ่มแบบอนิเมชัน</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalPlus">🎉 จำลองผู้ติดตามใหม่ (+50)</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoGoalReset">🔄 รีเซ็ตยอด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'viewer') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">👥 ทดสอบยอดผู้ชมสด</span>
            <span style="font-size:11px; color:#94a3b8;">สุ่มความผันผวนยอดคนดู</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerPulse">👥 สุ่มยอดผู้ชมสด</button>
          </div>
        </div>
      `;
    } else if (w.type === 'emote_party') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎉 ทดสอบพลุปาร์ตี้อีโมท</span>
            <span style="font-size:11px; color:#94a3b8;">พุ่งกระจายเต็มจอ</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoEmoteParty">🎉 จุดพลุปาร์ตี้อีโมท</button>
          </div>
        </div>
      `;
    }

    let specificHtml = '';

    // ==========================================
    // 1. CHAT WIDGET
    // ==========================================
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';

      if (mode === 'danmaku') {
        specificHtml = `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">⚡ ตั้งค่าดันมากุวิ่งบนจอ</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">ความเร็วตัววิ่ง</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuSpeed" min="3" max="12" value="${w.speed || 6}">
                  <span class="cwc-slider-val" id="compChatDanmakuSpeedVal">${w.speed || 6} วินาที</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuFontSize" min="16" max="48" value="${w.fontSize || 24}">
                  <span class="cwc-slider-val" id="compChatDanmakuFontSizeVal">${w.fontSize || 24}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">พื้นที่แสดงผลบนจอ</span>
                <select class="cwc-select" id="compChatDanmakuZone">
                  <option value="middle" ${w.slider_zone === 'middle' ? 'selected' : ''}>แถบกลางหน้าจอ</option>
                  <option value="top" ${w.slider_zone === 'top' ? 'selected' : ''}>ครึ่งบนของหน้าจอ</option>
                  <option value="bottom" ${w.slider_zone === 'bottom' ? 'selected' : ''}>ครึ่งล่างของหน้าจอ</option>
                  <option value="full" ${w.slider_zone === 'full' ? 'selected' : ''}>ทั้งหน้าจอผืนผ้าใบ</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compChatDanmakuColor" value="${w.fontColor || '#ffffff'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">เส้นขอบตัวอักษร</span>
                <label class="cwc-switch">
                  <input type="checkbox" id="compChatDanmakuStroke" ${w.textStroke !== false ? 'checked' : ''}>
                  <span class="cwc-slider-round"></span>
                </label>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีเส้นขอบ</span>
                <input type="color" class="cwc-color-pick" id="compChatDanmakuStrokeColor" value="${w.strokeColor || '#000000'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโปร่งแสง</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatDanmakuOpacity" min="10" max="100" value="${Math.round((w.opacity ?? 1) * 100)}">
                  <span class="cwc-slider-val" id="compChatDanmakuOpacityVal">${Math.round((w.opacity ?? 1) * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'balloon') {
        specificHtml = `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">💬 ตั้งค่าบอลลูนคำพูด</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonFontSize" min="12" max="28" value="${w.fontSize || 15}">
                  <span class="cwc-slider-val" id="compChatBalloonFontSizeVal">${w.fontSize || 15}px</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compChatBalloonTextColor" value="${w.balloonTextColor || '#0f172a'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีพื้นหลังบอลลูน</span>
                <input type="color" class="cwc-color-pick" id="compChatBalloonBg" value="${w.balloonBg || '#ffffff'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความทึบแสงบอลลูน</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonOpacity" min="10" max="100" value="${Math.round((w.balloonOpacity ?? 0.95) * 100)}">
                  <span class="cwc-slider-val" id="compChatBalloonOpacityVal">${Math.round((w.balloonOpacity ?? 0.95) * 100)}%</span>
                </div>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ความโค้งมนมุม</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compChatBalloonRadius" min="0" max="32" value="${w.balloonRadius ?? 14}">
                  <span class="cwc-slider-val" id="compChatBalloonRadiusVal">${w.balloonRadius ?? 14}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else if (mode === 'character') {
        specificHtml = `
          <div class="comp-card-section">
            <div class="comp-card-header"><span class="comp-card-title">🎭 ตั้งค่าแชทตัวละคร</span></div>
            <div class="comp-card-body">
              <div class="comp-field-row" style="flex-direction:column; align-items:flex-start; gap:8px;">
                <span class="comp-field-label">รูปภาพตัวละคร</span>
                <div style="display:flex; gap:6px; width:100%;">
                  <button type="button" class="btn-comp-demo-action" id="btnCharPresetReplie">👧 Replie</button>
                  <button type="button" class="btn-comp-demo-action" id="btnCharPresetCat">🐱 แมว VTuber</button>
                  <button type="button" class="btn-comp-demo-action" id="btnCharPresetAnime">🌸 อนิเมะ</button>
                </div>
                <div style="display:flex; gap:6px; width:100%; margin-top:4px;">
                  <input type="file" id="compCharFileInput" accept="image/*" style="display:none;">
                  <button type="button" class="btn-comp-demo-action" id="btnUploadCharImg" style="width:100%; justify-content:center;">📁 อัปโหลดรูปจากเครื่อง</button>
                </div>
                <input type="text" class="cwc-input" id="compCharImgUrl" placeholder="หรือวางลิงก์รูป URL" value="${w.imageUrl || ''}" style="width:100%; margin-top:4px;">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ชื่อตัวละคร</span>
                <input type="text" class="cwc-input" id="compCharName" value="${w.characterName || 'Replie'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ตำแหน่งตัวละคร</span>
                <select class="cwc-select" id="compCharAlign">
                  <option value="left" ${w.charAlign !== 'right' ? 'selected' : ''}>ชิดซ้าย</option>
                  <option value="right" ${w.charAlign === 'right' ? 'selected' : ''}>ชิดขวา</option>
                </select>
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีกล่องคำพูด</span>
                <input type="color" class="cwc-color-pick" id="compCharBubbleBg" value="${w.charBubbleBg || '#ffffff'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">สีตัวอักษร</span>
                <input type="color" class="cwc-color-pick" id="compCharTextColor" value="${w.charTextColor || '#0f172a'}">
              </div>
              <div class="comp-field-row">
                <span class="comp-field-label">ขนาดตัวอักษร</span>
                <div class="cwc-slider-wrap">
                  <input type="range" class="cwc-slider" id="compCharFontSize" min="12" max="28" value="${w.charFontSize || 15}">
                  <span class="cwc-slider-val" id="compCharFontSizeVal">${w.charFontSize || 15}px</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else {
        // Default Chat - Shows ONLY 2 Tabs: ค่ามาตรฐาน & ธีมสำเร็จรูป
        const subTab = state.chatSubTab || 'standard';
        const theme = w.chatTheme || 'default';
        const allThemes = window.CWC_ALL_THEMES || [];
        const totalPages = Math.ceil(allThemes.length / 8);
        const curPage = Math.min(totalPages, Math.max(1, state.chatThemePage || 1));
        const pageThemes = allThemes.slice((curPage - 1) * 8, curPage * 8);

        let themeCardsHtml = '';
        pageThemes.forEach(t => {
          const isAct = t.id === theme;
          themeCardsHtml += `
            <div class="cwc-preset-card ${isAct ? 'active' : ''}" data-chat-theme="${t.id}">
              <div class="cwc-preset-badge" style="background:${t.id === 'cyberpunk' ? 'rgba(0,255,204,0.2)' : 'rgba(255,255,255,0.06)'};">
                ${t.badge || '🎨'}
              </div>
              <div class="cwc-preset-info">
                <div class="cwc-preset-name">${t.name}</div>
                <div class="cwc-preset-desc">${t.desc}</div>
              </div>
            </div>
          `;
        });

        specificHtml = `
          <!-- 2 Tabs: ค่ามาตรฐาน & ธีมสำเร็จรูป -->
          <div class="cwc-tabs-bar" style="border-radius:8px; margin-bottom:10px;">
            <button type="button" class="cwc-tab-btn ${subTab === 'standard' ? 'active' : ''}" id="tabSubStandard">
              ⚙️ ค่ามาตรฐาน
            </button>
            <button type="button" class="cwc-tab-btn ${subTab === 'theme' ? 'active' : ''}" id="tabSubTheme">
              🎨 ธีมสำเร็จรูป
            </button>
          </div>

          ${subTab === 'theme' ? `
            <div class="comp-card-section">
              <div class="comp-card-header">
                <span class="comp-card-title">🎨 คลัง 80 ธีมสำเร็จรูป</span>
              </div>
              <div class="comp-card-body">
                <div class="cwc-presets-grid" id="compChatThemesGrid">
                  ${themeCardsHtml}
                </div>
                <div class="cwc-pagination" style="margin-top:10px;">
                  <button type="button" class="cwc-page-btn" id="btnCompThemePrev" ${curPage <= 1 ? 'disabled' : ''}>◀ ก่อนหน้า</button>
                  <span class="cwc-page-indicator">หน้า ${curPage} / ${totalPages}</span>
                  <button type="button" class="cwc-page-btn" id="btnCompThemeNext" ${curPage >= totalPages ? 'disabled' : ''}>ถัดไป ▶</button>
                </div>
              </div>
            </div>
          ` : `
            <div class="comp-card-section">
              <div class="comp-card-header"><span class="comp-card-title">⚙️ ค่ามาตรฐานกล่องแชท</span></div>
              <div class="comp-card-body">
                <div class="comp-field-row">
                  <span class="comp-field-label">แบบอักษร</span>
                  <select class="cwc-select" id="compChatFontFamily">
                    <option value="Kanit" ${w.fontFamily === 'Kanit' ? 'selected' : ''}>Kanit</option>
                    <option value="Sarabun" ${w.fontFamily === 'Sarabun' ? 'selected' : ''}>Sarabun</option>
                    <option value="Prompt" ${w.fontFamily === 'Prompt' ? 'selected' : ''}>Prompt</option>
                    <option value="Chonburi" ${w.fontFamily === 'Chonburi' ? 'selected' : ''}>Chonburi</option>
                    <option value="JetBrains Mono" ${w.fontFamily === 'JetBrains Mono' ? 'selected' : ''}>JetBrains Mono</option>
                  </select>
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">ขนาดตัวอักษร</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatFontSize" min="12" max="32" value="${w.fontSize || 15}">
                    <span class="cwc-slider-val" id="compChatFontSizeVal">${w.fontSize || 15}px</span>
                  </div>
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">สีตัวอักษร</span>
                  <input type="color" class="cwc-color-pick" id="compChatFontColor" value="${w.fontColor || '#ffffff'}">
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">สีพื้นหลังกล่อง</span>
                  <input type="color" class="cwc-color-pick" id="compChatBgColor" value="${w.bgColor || '#1e1f22'}">
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">ความทึบแสงพื้นหลัง</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatBgOpacity" min="0" max="100" value="${Math.round((w.bgOpacity ?? 0.85) * 100)}">
                    <span class="cwc-slider-val" id="compChatBgOpacityVal">${Math.round((w.bgOpacity ?? 0.85) * 100)}%</span>
                  </div>
                </div>
                <div class="comp-field-row">
                  <span class="comp-field-label">ความโค้งมนมุม</span>
                  <div class="cwc-slider-wrap">
                    <input type="range" class="cwc-slider" id="compChatBoxRadius" min="0" max="32" value="${w.boxRadius ?? 8}">
                    <span class="cwc-slider-val" id="compChatBoxRadiusVal">${w.boxRadius ?? 8}px</span>
                  </div>
                </div>
              </div>
            </div>
          `}
        `;
      }
    } else if (w.type === 'clock') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🕒 ตั้งค่านาฬิกาสตรีม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ธีมนาฬิกา</span>
              <select class="cwc-select" id="compClockTheme">
                <option value="cyberpunk" ${w.clockTheme === 'cyberpunk' ? 'selected' : ''}>Cyberpunk</option>
                <option value="neon" ${w.clockTheme === 'neon' ? 'selected' : ''}>Neon Glow</option>
                <option value="flip" ${w.clockTheme === 'flip' ? 'selected' : ''}>Flip Clock</option>
                <option value="minimal" ${w.clockTheme === 'minimal' ? 'selected' : ''}>Minimal Clean</option>
                <option value="digital" ${w.clockTheme === 'digital' ? 'selected' : ''}>Digital Red</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบเวลา</span>
              <select class="cwc-select" id="compClockFormat">
                <option value="24" ${w.clockFormat === '24' ? 'selected' : ''}>24 ชั่วโมง</option>
                <option value="12" ${w.clockFormat === '12' ? 'selected' : ''}>12 ชั่วโมง พร้อม AM / PM</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงเข็มวินาที</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compClockShowSeconds" ${w.showSeconds !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดตัวอักษร</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compClockFontSize" min="16" max="64" value="${w.fontSize || 26}">
                <span class="cwc-slider-val" id="compClockFontSizeVal">${w.fontSize || 26}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compClockFontColor" value="${w.fontColor || '#38bdf8'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'text') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🔤 ตั้งค่าข้อความประกาศ</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ข้อความ</span>
              <textarea class="cwc-input" id="compTextInput" rows="2" style="width:100%; resize:vertical;">${w.text || ''}</textarea>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดแสดงผล</span>
              <select class="cwc-select" id="compTextMode">
                <option value="ticker" ${w.textMode === 'ticker' ? 'selected' : ''}>ตัววิ่ง Marquee สด</option>
                <option value="static" ${w.textMode === 'static' ? 'selected' : ''}>ข้อความนิ่ง</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="48" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compTextFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compTextFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <input type="color" class="cwc-color-pick" id="compTextBgColor" value="${w.bgColor || '#141923'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📹 ตั้งค่ากรอบเว็บแคม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">อัตราส่วนภาพ</span>
              <select class="cwc-select" id="compWebcamRatio">
                <option value="16:9" ${w.ratio === '16:9' ? 'selected' : ''}>16:9 แนวนอนมาตรฐาน</option>
                <option value="4:3" ${w.ratio === '4:3' ? 'selected' : ''}>4:3 คลาสสิก</option>
                <option value="1:1" ${w.ratio === '1:1' ? 'selected' : ''}>1:1 จัตุรัส</option>
                <option value="9:16" ${w.ratio === '9:16' ? 'selected' : ''}>9:16 แนวตั้งมือถือ</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาเส้นขอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamBorderWidth" min="0" max="12" value="${w.borderWidth ?? 4}">
                <span class="cwc-slider-val" id="compWebcamBorderWidthVal">${w.borderWidth ?? 4}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compWebcamBorderColor" value="${w.borderColor || '#5865f2'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความโค้งมนมุม</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamBorderRadius" min="0" max="32" value="${w.borderRadius ?? 8}">
                <span class="cwc-slider-val" id="compWebcamBorderRadiusVal">${w.borderRadius ?? 8}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสงเรืองรอบกรอบ</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compWebcamGlow" ${w.glow ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงป้ายชื่อสตรีมเมอร์</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compWebcamShowName" ${w.showStreamerName ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อสตรีมเมอร์</span>
              <input type="text" class="cwc-input" id="compWebcamName" value="${w.streamerName || 'Streamer LIVE'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'goal') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎯 ตั้งค่าเป้าหมายผู้ติดตาม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อเป้าหมาย</span>
              <input type="text" class="cwc-input" id="compGoalTitle" value="${w.goalTitle || 'เป้าหมายผู้ติดตาม'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ยอดปัจจุบัน</span>
              <input type="number" class="cwc-input" id="compGoalCurrent" value="${w.goalCurrent ?? 650}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ยอดเป้าหมาย</span>
              <input type="number" class="cwc-input" id="compGoalTarget" value="${w.goalTarget ?? 1000}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">หน่วยนับ</span>
              <input type="text" class="cwc-input" id="compGoalUnit" value="${w.goalUnit || 'คน'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'viewer') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">👥 ตั้งค่าตัวนับยอดผู้ชมสด</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">สไตล์ป้ายสถานะ</span>
              <select class="cwc-select" id="compViewerTheme">
                <option value="pill" ${w.viewerTheme === 'pill' ? 'selected' : ''}>Pill Badge</option>
                <option value="minimal" ${w.viewerTheme === 'minimal' ? 'selected' : ''}>Minimal Text</option>
              </select>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'character') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎭 ตั้งค่าตัวละคร Replie</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อตัวละคร</span>
              <input type="text" class="cwc-input" id="compCharWidgetName" value="${w.characterName || 'Replie'}">
            </div>
          </div>
        </div>
      `;
    }

    bodyEl.innerHTML = demoHtml + specificHtml;

    // Bind Demo Action Buttons
    const btnDemoChatLoop = document.getElementById('btnDemoChatLoop');
    const btnDemoChatSingle = document.getElementById('btnDemoChatSingle');
    if (btnDemoChatLoop) btnDemoChatLoop.addEventListener('click', () => ComposerDemoManager.toggleChatLoop(w, btnDemoChatLoop));
    if (btnDemoChatSingle) btnDemoChatSingle.addEventListener('click', () => ComposerDemoManager.sendChatMsg(w));

    const btnDemoDanmakuLoop = document.getElementById('btnDemoDanmakuLoop');
    const btnDemoDanmakuSingle = document.getElementById('btnDemoDanmakuSingle');
    if (btnDemoDanmakuLoop) btnDemoDanmakuLoop.addEventListener('click', () => ComposerDemoManager.toggleDanmakuLoop(w, btnDemoDanmakuLoop));
    if (btnDemoDanmakuSingle) btnDemoDanmakuSingle.addEventListener('click', () => ComposerDemoManager.sendDanmakuMsg(w));

    const btnDemoBalloonSingle = document.getElementById('btnDemoBalloonSingle');
    if (btnDemoBalloonSingle) btnDemoBalloonSingle.addEventListener('click', () => ComposerDemoManager.sendBalloonMsg(w));

    const btnDemoCharTalk = document.getElementById('btnDemoCharTalk');
    if (btnDemoCharTalk) btnDemoCharTalk.addEventListener('click', () => ComposerDemoManager.triggerCharacterTalk(w));

    const btnDemoClockToggle = document.getElementById('btnDemoClockToggle');
    if (btnDemoClockToggle) {
      btnDemoClockToggle.addEventListener('click', () => {
        w.clockFormat = w.clockFormat === '12' ? '24' : '12';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoClockSecs = document.getElementById('btnDemoClockSecs');
    if (btnDemoClockSecs) {
      btnDemoClockSecs.addEventListener('click', () => {
        w.showSeconds = w.showSeconds === false ? true : false;
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoTextTicker = document.getElementById('btnDemoTextTicker');
    if (btnDemoTextTicker) {
      btnDemoTextTicker.addEventListener('click', () => {
        w.textMode = w.textMode === 'ticker' ? 'static' : 'ticker';
        renderCanvasWidgets();
        renderWidgetCustomizerPanel(w.id);
        saveState();
      });
    }

    const btnDemoWebcamRec = document.getElementById('btnDemoWebcamRec');
    if (btnDemoWebcamRec) {
      btnDemoWebcamRec.addEventListener('click', () => {
        const dot = document.querySelector(`#widget-${w.id} .webcam-rec-dot`);
        if (dot) dot.style.display = dot.style.display === 'none' ? 'block' : 'none';
      });
    }

    const btnDemoWebcamAudio = document.getElementById('btnDemoWebcamAudio');
    if (btnDemoWebcamAudio) {
      btnDemoWebcamAudio.addEventListener('click', () => {
        const bars = document.querySelectorAll(`#widget-${w.id} .webcam-vu-bar`);
        bars.forEach(b => {
          b.style.height = (4 + Math.random() * 12) + 'px';
        });
      });
    }

    const btnDemoGoalPlus = document.getElementById('btnDemoGoalPlus');
    const btnDemoGoalReset = document.getElementById('btnDemoGoalReset');
    if (btnDemoGoalPlus) btnDemoGoalPlus.addEventListener('click', () => ComposerDemoManager.triggerGoalPlus(w));
    if (btnDemoGoalReset) btnDemoGoalReset.addEventListener('click', () => ComposerDemoManager.triggerGoalReset(w));

    const btnDemoViewerPulse = document.getElementById('btnDemoViewerPulse');
    if (btnDemoViewerPulse) btnDemoViewerPulse.addEventListener('click', () => ComposerDemoManager.triggerViewerPulse(w));

    const btnDemoEmoteParty = document.getElementById('btnDemoEmoteParty');
    if (btnDemoEmoteParty) btnDemoEmoteParty.addEventListener('click', () => ComposerDemoManager.triggerEmoteParty(w));

    // Bind Mode-Specific Inputs
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        bindField('compChatDanmakuSpeed', 'speed', 'number');
        bindField('compChatDanmakuFontSize', 'fontSize', 'number', 'px');
        bindField('compChatDanmakuZone', 'slider_zone');
        bindField('compChatDanmakuColor', 'fontColor');
        bindField('compChatDanmakuStroke', 'textStroke', 'checkbox');
        bindField('compChatDanmakuStrokeColor', 'strokeColor');
        bindField('compChatDanmakuOpacity', 'opacity', 'opacity');
      } else if (mode === 'balloon') {
        bindField('compChatBalloonFontSize', 'fontSize', 'number', 'px');
        bindField('compChatBalloonTextColor', 'balloonTextColor');
        bindField('compChatBalloonBg', 'balloonBg');
        bindField('compChatBalloonOpacity', 'balloonOpacity', 'opacity');
        bindField('compChatBalloonRadius', 'balloonRadius', 'number', 'px');
      } else if (mode === 'character') {
        bindField('compCharName', 'characterName');
        bindField('compCharAlign', 'charAlign');
        bindField('compCharBubbleBg', 'charBubbleBg');
        bindField('compCharTextColor', 'charTextColor');
        bindField('compCharFontSize', 'charFontSize', 'number', 'px');
        bindField('compCharImgUrl', 'imageUrl');

        // Presets & File Upload
        const btnReplie = document.getElementById('btnCharPresetReplie');
        const btnCat = document.getElementById('btnCharPresetCat');
        const btnAnime = document.getElementById('btnCharPresetAnime');
        if (btnReplie) btnReplie.addEventListener('click', () => { w.imageUrl = './assets/dock_offline_character.png'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });
        if (btnCat) btnCat.addEventListener('click', () => { w.imageUrl = 'https://api.dicebear.com/7.x/bottts/svg?seed=CatStreamer'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });
        if (btnAnime) btnAnime.addEventListener('click', () => { w.imageUrl = 'https://api.dicebear.com/7.x/bottts/svg?seed=AnimeHero'; renderCanvasWidgets(); renderWidgetCustomizerPanel(w.id); saveState(); });

        const uploadBtn = document.getElementById('btnUploadCharImg');
        const fileInp = document.getElementById('compCharFileInput');
        if (uploadBtn && fileInp) {
          uploadBtn.addEventListener('click', () => fileInp.click());
          fileInp.addEventListener('change', () => {
            const file = fileInp.files[0];
            if (file) {
              const reader = new FileReader();
              reader.onload = (ev) => {
                w.imageUrl = ev.target.result;
                renderCanvasWidgets();
                renderWidgetCustomizerPanel(w.id);
                saveState();
              };
              reader.readAsDataURL(file);
            }
          });
        }
      } else {
        // SubTabs
        const tabStd = document.getElementById('tabSubStandard');
        const tabThm = document.getElementById('tabSubTheme');
        if (tabStd) tabStd.addEventListener('click', () => { state.chatSubTab = 'standard'; renderWidgetCustomizerPanel(w.id); });
        if (tabThm) tabThm.addEventListener('click', () => { state.chatSubTab = 'theme'; renderWidgetCustomizerPanel(w.id); });

        // Themes Click & Pagination
        document.querySelectorAll('#compChatThemesGrid .cwc-preset-card').forEach(card => {
          card.addEventListener('click', () => {
            w.chatTheme = card.dataset.chatTheme;
            renderCanvasWidgets();
            renderWidgetCustomizerPanel(w.id);
            saveState();
          });
        });

        const allThemes = window.CWC_ALL_THEMES || [];
        const totalPages = Math.ceil(allThemes.length / 8);
        const btnPrev = document.getElementById('btnCompThemePrev');
        const btnNext = document.getElementById('btnCompThemeNext');
        if (btnPrev) btnPrev.addEventListener('click', () => {
          state.chatThemePage = Math.max(1, (state.chatThemePage || 1) - 1);
          renderWidgetCustomizerPanel(w.id);
        });
        if (btnNext) btnNext.addEventListener('click', () => {
          state.chatThemePage = Math.min(totalPages, (state.chatThemePage || 1) + 1);
          renderWidgetCustomizerPanel(w.id);
        });

        bindField('compChatFontFamily', 'fontFamily');
        bindField('compChatFontSize', 'fontSize', 'number', 'px');
        bindField('compChatFontColor', 'fontColor');
        bindField('compChatBgColor', 'bgColor');
        bindField('compChatBgOpacity', 'bgOpacity', 'opacity');
        bindField('compChatBoxRadius', 'boxRadius', 'number', 'px');
      }
    } else if (w.type === 'clock') {
      bindField('compClockTheme', 'clockTheme');
      bindField('compClockFormat', 'clockFormat');
      bindField('compClockShowSeconds', 'showSeconds', 'checkbox');
      bindField('compClockFontSize', 'fontSize', 'number', 'px');
      bindField('compClockFontColor', 'fontColor');
    } else if (w.type === 'text') {
      bindField('compTextInput', 'text');
      bindField('compTextMode', 'textMode');
      bindField('compTextFontSize', 'fontSize', 'number', 'px');
      bindField('compTextFontColor', 'fontColor');
      bindField('compTextBgColor', 'bgColor');
    } else if (w.type === 'webcam') {
      bindField('compWebcamRatio', 'ratio');
      bindField('compWebcamBorderWidth', 'borderWidth', 'number', 'px');
      bindField('compWebcamBorderColor', 'borderColor');
      bindField('compWebcamBorderRadius', 'borderRadius', 'number', 'px');
      bindField('compWebcamGlow', 'glow', 'checkbox');
      bindField('compWebcamShowName', 'showStreamerName', 'checkbox');
      bindField('compWebcamName', 'streamerName');
    } else if (w.type === 'goal') {
      bindField('compGoalTitle', 'goalTitle');
      bindField('compGoalCurrent', 'goalCurrent', 'number');
      bindField('compGoalTarget', 'goalTarget', 'number');
      bindField('compGoalUnit', 'goalUnit');
    } else if (w.type === 'viewer') {
      bindField('compViewerTheme', 'viewerTheme');
    } else if (w.type === 'character') {
      bindField('compCharWidgetName', 'characterName');
    }
  }

  // Bind Toolbar Buttons & Chat Dropdown Menu
  function initComposerToolbarEvents() {
    // Chat Context Dropdown Trigger
    const btnChatMenu = document.getElementById('btnCompAddChatMenu');
    const menuChat = document.getElementById('compChatDropdownMenu');
    if (btnChatMenu && menuChat) {
      btnChatMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = menuChat.style.display === 'block';
        menuChat.style.display = isOpen ? 'none' : 'block';
      });

      menuChat.querySelectorAll('.comp-chat-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
          e.stopPropagation();
          menuChat.style.display = 'none';
          const mode = item.dataset.chatMode || 'default';
          checkAndAddWidget('chat', mode);
        });
      });

      document.addEventListener('click', (e) => {
        if (!e.target.closest('#chatAddBtnWrapper')) {
          menuChat.style.display = 'none';
        }
      });
    }

    // Add Widget Buttons (Excluding the chat dropdown trigger)
    document.querySelectorAll('.btn-add-widget').forEach(btn => {
      if (btn.id === 'btnCompAddChatMenu') return;
      btn.addEventListener('click', () => {
        checkAndAddWidget(btn.dataset.widgetType);
      });
    });
  }
"""

if idx_cust_start != -1 and idx_toolbar != -1:
    end_snippet = idx_toolbar + len(old_toolbar_snippet)
    code = code[:idx_cust_start] + new_customizer_and_toolbar + "\n    initComposerToolbarEvents();\n\n" + code[end_snippet:]
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Replaced renderWidgetCustomizerPanel and toolbar bindings successfully!")
else:
    print("Could not find targets")
