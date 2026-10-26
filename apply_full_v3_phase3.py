# -*- coding: utf-8 -*-
import sys, io

file_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. NEW DEMO HTML BLOCKS FOR VIEWER, NOW PLAYING, EMOTE PARTY
old_demo_viewer = """    } else if (w.type === 'viewer') {
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
    }"""

new_demo_viewer = """    } else if (w.type === 'viewer') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">👥 ทดสอบตัวนับยอดผู้ชมสด</span>
            <span style="font-size:11px; color:#94a3b8;">อนิเมชันตัวเลขหมุนนุ่มนวล</span>
          </div>
          <div class="comp-demo-actions" style="display:flex; gap:6px;">
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerRandom" style="flex:1;">🎲 สุ่มยอดคนดู</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerAdd" style="flex:1;">📈 เพิ่ม +50 คน</button>
            <button type="button" class="btn-comp-demo-action" id="btnDemoViewerSub" style="flex:1;">📉 ลด -30 คน</button>
          </div>
        </div>
      `;
    } else if (w.type === 'emote_party') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎉 ทดสอบปาร์ตี้อีโมทสด</span>
            <span style="font-size:11px; color:#94a3b8;">พุ่งลอยบนจอสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoEmoteParty">🎉 ปล่อยอีโมททดสอบ</button>
          </div>
        </div>
      `;
    } else if (w.type === 'now_playing') {
      demoHtml = `
        <div class="comp-demo-section">
          <div class="comp-demo-header">
            <span class="comp-demo-title">🎵 ทดสอบเพลงที่กำลังเล่น</span>
            <span style="font-size:11px; color:#94a3b8;">เปลี่ยนเพลงสด</span>
          </div>
          <div class="comp-demo-actions">
            <button type="button" class="btn-comp-demo-action" id="btnDemoNowPlayingNext">🎵 จำลองเพลงถัดไป</button>
          </div>
        </div>
      `;
    }"""

if old_demo_viewer in code:
    code = code.replace(old_demo_viewer, new_demo_viewer)
    print("Replaced demoHtml blocks for viewer, emote_party, now_playing.")
else:
    print("WARNING: old_demo_viewer not exact match.")

# 2. NEW SPECIFIC HTML FOR TEXT, WEBCAM, VIEWER, IMAGE, VIDEO, ALERT, NOW_PLAYING, EMOTE_PARTY
old_specific_start = "    } else if (w.type === 'text') {\n      specificHtml = `"
s_sp_start = code.find(old_specific_start)
s_sp_end = code.find("    bodyEl.innerHTML = demoHtml + specificHtml;", s_sp_start)

new_specific_html = """    } else if (w.type === 'text') {
      const isTicker = (w.textMode || 'ticker') === 'ticker';
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
                <option value="ticker" ${isTicker ? 'selected' : ''}>ตัววิ่ง Marquee สด</option>
                <option value="static" ${!isTicker ? 'selected' : ''}>ข้อความนิ่ง</option>
              </select>
            </div>
            <div class="comp-field-row" id="compTextSpeedRow" style="display:${isTicker ? 'flex' : 'none'};">
              <span class="cwc-label">ความเร็วตัววิ่ง (วินาทีต่อรอบ):</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextSpeed" min="5" max="60" value="${w.marqueeSpeed || 15}">
                <span class="cwc-slider-val" id="compTextSpeedVal">${w.marqueeSpeed || 15} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดฟอนต์</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextFontSize" min="12" max="64" value="${w.fontSize || 18}">
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
            <div class="comp-field-row">
              <span class="comp-field-label">เส้นขอบตัวหนังสือ</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compTextStroke" ${w.textStroke ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row" id="compTextStrokeWidthRow" style="display:${w.textStroke ? 'flex' : 'none'};">
              <span class="comp-field-label">ความหนาเส้นขอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextStrokeWidth" min="1" max="8" value="${w.textStrokeWidth || 2}">
                <span class="cwc-slider-val" id="compTextStrokeWidthVal">${w.textStrokeWidth || 2}px</span>
              </div>
            </div>
            <div class="comp-field-row" id="compTextStrokeColorRow" style="display:${w.textStroke ? 'flex' : 'none'};">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compTextStrokeColor" value="${w.strokeColor || '#000000'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เงาตัวหนังสือ</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compTextShadow" ${w.textShadow ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row" id="compTextShadowBlurRow" style="display:${w.textShadow ? 'flex' : 'none'};">
              <span class="comp-field-label">ระยะเบลอเงา</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compTextShadowBlur" min="1" max="16" value="${w.textShadowBlur || 3}">
                <span class="cwc-slider-val" id="compTextShadowBlurVal">${w.textShadowBlur || 3}px</span>
              </div>
            </div>
            <div class="comp-field-row" id="compTextShadowColorRow" style="display:${w.textShadow ? 'flex' : 'none'};">
              <span class="comp-field-label">สีเงาตัวหนังสือ</span>
              <input type="color" class="cwc-color-pick" id="compTextShadowColor" value="${w.textShadowColor || '#000000'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'webcam') {
      const themes = [
        { group: '─ ธรรมดา ─', items: [
          { val: 'simple-white', label: 'ขาวเรียบมาตรฐาน' },
          { val: 'simple-black', label: 'ดำเรียบเท่' },
          { val: 'rounded', label: 'ขาวมุมโค้งมน' },
          { val: 'glass', label: 'กระจกฝ้าโปร่งแสง' },
          { val: 'neon-blue', label: 'นีออนฟ้าสดใส' },
          { val: 'neon-pink', label: 'นีออนชมพูหวาน' },
          { val: 'gold', label: 'ทองคำหรูหรา' },
          { val: 'cyberpunk', label: 'ไซเบอร์พังค์' },
          { val: 'pixel', label: 'พิกเซลเรโทร' },
          { val: 'none', label: 'ไม่มีเส้นขอบ' }
        ]},
        { group: '─ อนิเมชั่น ─', items: [
          { val: 'glow-pulse', label: 'เรืองแสงเต้นเป็นจังหวะ' },
          { val: 'rainbow-border', label: 'ขอบสีรุ้งหมุนวนรอบ' },
          { val: 'neon-flow', label: 'แสงนีออนไหลเวียน' },
          { val: 'game-shield', label: 'โล่เกมมิ่งป้องกัน' },
          { val: 'game-loading', label: 'หลอดโหลดสตรีมมิ่ง' },
          { val: 'rpg-aura', label: 'ออร่าพลังแฟนตาซี' },
          { val: 'tron-line', label: 'เส้นแสงทรอนไซเบอร์' },
          { val: 'pulse-ring', label: 'วงแหวนชีพจรกระพริบ' },
          { val: 'electric', label: 'ประกายสายฟ้าอาร์ค' },
          { val: 'gradient-shift', label: 'ไล่สีเกรเดียนท์นุ่มนวล' },
          { val: 'bounce-border', label: 'ขอบเด้งดึ๋งไดนามิก' },
          { val: 'fire-border', label: 'เปลวเพลิงเร่าร้อนลุกโชน' },
          { val: 'sparkle', label: 'ละอองประกายดาวระยิบระยับ' }
        ]}
      ];

      let themeOpts = '';
      themes.forEach(g => {
        themeOpts += `<optgroup label="${g.group}">`;
        g.items.forEach(it => {
          themeOpts += `<option value="${it.val}" ${(w.webcamTheme || 'simple-white') === it.val ? 'selected' : ''}>${it.label}</option>`;
        });
        themeOpts += `</optgroup>`;
      });

      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">📹 ตั้งค่ากรอบเว็บแคม</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">อัตราส่วนภาพ</span>
              <select class="cwc-select" id="compWebcamRatio">
                <option value="16:9" ${(w.ratio || '16:9') === '16:9' ? 'selected' : ''}>16:9 แนวนอนมาตรฐาน</option>
                <option value="4:3" ${(w.ratio || '16:9') === '4:3' ? 'selected' : ''}>4:3 คลาสสิก</option>
                <option value="1:1" ${(w.ratio || '16:9') === '1:1' ? 'selected' : ''}>1:1 จัตุรัส</option>
                <option value="9:16" ${(w.ratio || '16:9') === '9:16' ? 'selected' : ''}>9:16 แนวตั้งมือถือ</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ธีมกรอบเว็บแคม</span>
              <select class="cwc-select" id="compWebcamTheme">
                ${themeOpts}
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ความหนาเส้นขอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compWebcamBorderWidth" min="1" max="20" value="${w.borderWidth ?? 4}">
                <span class="cwc-slider-val" id="compWebcamBorderWidthVal">${w.borderWidth ?? 4}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compWebcamBorderColor" value="${w.borderColor || '#5865f2'}">
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
      const viewerThemes = [
        { val: 'default', label: 'มาตรฐานสีฟ้า' },
        { val: 'neon', label: 'นีออนไซเบอร์' },
        { val: 'glass', label: 'กระจกฝ้าโปร่งแสง' },
        { val: 'pill', label: 'แคปซูลไล่เฉด' },
        { val: 'dark', label: 'ดาร์กเรียบหรู' },
        { val: 'cyberpunk', label: 'ไซเบอร์พังค์เหลืองดำ' },
        { val: 'gold', label: 'ทองคำหรูหรา' },
        { val: 'retro', label: 'เรโทรพิกเซล' },
        { val: 'aqua', label: 'อควาน้ำทะเล' },
        { val: 'magma', label: 'แมกมาลาวาเพลิง' },
        { val: 'forest', label: 'ป่าไม้มรกต' },
        { val: 'sapphire', label: 'แซฟไฟร์น้ำเงินคราม' },
        { val: 'neon-purple', label: 'นีออนม่วงสด' },
        { val: 'sunset-orange', label: 'อาทิตย์อัสดงส้ม' },
        { val: 'mono', label: 'ขาวดำโมโนโครม' },
        { val: 'rainbow', label: 'สายรุ้งสีสันสดใส' },
        { val: 'carbon', label: 'คาร์บอนไฟเบอร์' },
        { val: 'vapor', label: 'เวเปอร์เวฟพาสเทล' },
        { val: 'ice', label: 'น้ำแข็งขั้วโลก' },
        { val: 'rose-gold', label: 'โรสโกลด์หวานหรู' },
        { val: 'emerald', label: 'เอเมอรัลด์ประกายเขียว' },
        { val: 'sakura', label: 'ซากุระชมพูหวาน' },
        { val: 'toxic', label: 'ท็อกซิกเขียวสว่าง' },
        { val: 'blood-moon', label: 'จันทราสีเลือด' },
        { val: 'chrome', label: 'โครเมียมเงางาม' },
        { val: 'coral', label: 'ปะการังชมพูส้ม' },
        { val: 'galaxy', label: 'กาแล็กซีห้วงอวกาศ' },
        { val: 'amber', label: 'อำพันประกายอบอุ่น' }
      ];

      const viewerThemeOpts = viewerThemes.map(it => `<option value="${it.val}" ${(w.viewerTheme || 'default') === it.val ? 'selected' : ''}>${it.label}</option>`).join('');

      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">👥 ตั้งค่ายอดผู้ชมสด</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ธีมวิดเจ็ตผู้ชม</span>
              <select class="cwc-select" id="compViewerTheme">
                ${viewerThemeOpts}
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">โหมดการแสดง</span>
              <select class="cwc-select" id="compViewerMode">
                <option value="both" ${(w.viewerMode || 'both') === 'both' ? 'selected' : ''}>แสดงรวม และ รายแพลตฟอร์ม</option>
                <option value="total" ${(w.viewerMode || 'both') === 'total' ? 'selected' : ''}>แสดงรวมอย่างเดียว</option>
                <option value="per_platform" ${(w.viewerMode || 'both') === 'per_platform' ? 'selected' : ''}>แสดงรายแพลตฟอร์มอย่างเดียว</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ทิศทางการเรียง</span>
              <select class="cwc-select" id="compViewerDirection">
                <option value="horizontal" ${(w.viewerDirection || 'horizontal') === 'horizontal' ? 'selected' : ''}>แนวนอนเรียงแถว</option>
                <option value="vertical" ${(w.viewerDirection || 'horizontal') === 'vertical' ? 'selected' : ''}>แนวตั้งเรียงหลัก</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การจัดตำแหน่ง</span>
              <select class="cwc-select" id="compViewerAlign">
                <option value="left" ${(w.viewerAlign || 'left') === 'left' ? 'selected' : ''}>ชิดซ้าย</option>
                <option value="center" ${(w.viewerAlign || 'left') === 'center' ? 'selected' : ''}>กึ่งกลาง</option>
                <option value="right" ${(w.viewerAlign || 'left') === 'right' ? 'selected' : ''}>ชิดขวา</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงไอคอน</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compViewerShowIcon" ${w.showIcon !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดไอคอน</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compViewerIconSize" min="14" max="48" value="${w.iconSize || 20}">
                <span class="cwc-slider-val" id="compViewerIconSizeVal">${w.iconSize || 20}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดตัวเลข</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compViewerFontSize" min="14" max="48" value="${w.fontSize || 18}">
                <span class="cwc-slider-val" id="compViewerFontSizeVal">${w.fontSize || 18}px</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวอักษร</span>
              <input type="color" class="cwc-color-pick" id="compViewerFontColor" value="${w.fontColor || '#ffffff'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">เส้นขอบตัวเลข</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compViewerTextStroke" ${w.textStroke ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row" id="compViewerTextStrokeRow" style="display:${w.textStroke ? 'flex' : 'none'};">
              <span class="comp-field-label">ความหนาขอบ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compViewerTextStrokeWidth" min="1" max="6" value="${w.textStrokeWidth || 2}">
                <span class="cwc-slider-val" id="compViewerTextStrokeWidthVal">${w.textStrokeWidth || 2}px</span>
              </div>
            </div>
            <div class="comp-field-row" id="compViewerTextStrokeColorRow" style="display:${w.textStroke ? 'flex' : 'none'};">
              <span class="comp-field-label">สีเส้นขอบ</span>
              <input type="color" class="cwc-color-pick" id="compViewerTextStrokeColor" value="${w.strokeColor || '#000000'}">
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
    } else if (w.type === 'image') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🖼️ ตั้งค่ากรอบรูปภาพ</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ลิงก์ URL รูปภาพ</span>
              <input type="text" class="cwc-input" id="compImageUrl" value="${w.imageUrl || ''}" placeholder="https://example.com/image.png" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การปรับพอดีภาพ</span>
              <select class="cwc-select" id="compImageFit">
                <option value="cover" ${(w.fitMode || 'cover') === 'cover' ? 'selected' : ''}>เต็มกรอบตัดขอบ</option>
                <option value="contain" ${(w.fitMode || 'cover') === 'contain' ? 'selected' : ''}>เห็นครบทั้งภาพ</option>
              </select>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'video') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎬 ตั้งค่าวิดีโอลูป</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ลิงก์ URL วิดีโอ</span>
              <input type="text" class="cwc-input" id="compVideoUrl" value="${w.videoUrl || ''}" placeholder="https://example.com/video.mp4" style="width:100%;">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">การปรับพอดีภาพ</span>
              <select class="cwc-select" id="compVideoFit">
                <option value="cover" ${(w.fitMode || 'cover') === 'cover' ? 'selected' : ''}>เต็มกรอบตัดขอบ</option>
                <option value="contain" ${(w.fitMode || 'cover') === 'contain' ? 'selected' : ''}>เห็นครบทั้งภาพ</option>
              </select>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'alert') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🌐 ตั้งค่าเบราว์เซอร์ URL</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row" style="flex-direction:column; align-items:flex-start;">
              <span class="comp-field-label" style="margin-bottom:4px;">ที่อยู่เว็บไซต์ URL</span>
              <input type="text" class="cwc-input" id="compAlertUrl" value="${w.url || ''}" placeholder="https://streamlabs.com/widgets/..." style="width:100%;">
            </div>
            <div class="comp-field-row" style="margin-top:8px;">
              <button type="button" class="btn-comp-demo-action" id="btnRefreshAlert" style="width:100%;">🔄 รีเฟรชหน้าเว็บ</button>
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'now_playing') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎵 ตั้งค่าเพลงที่กำลังเล่น</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">ชื่อเพลง</span>
              <input type="text" class="cwc-input" id="compNpTitle" value="${w.songTitle || 'Never Gonna Give You Up'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ศิลปิน</span>
              <input type="text" class="cwc-input" id="compNpArtist" value="${w.artist || 'Rick Astley'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">พื้นหลังโปร่งใส</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpTransparent" ${w.npTransparent !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row" id="compNpBgColorRow" style="display:${w.npTransparent !== false ? 'none' : 'flex'};">
              <span class="comp-field-label">สีพื้นหลัง</span>
              <input type="color" class="cwc-color-pick" id="compNpBgColor" value="${w.npBgColor || '#1a1a2e'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงภาพปก</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpShowArt" ${w.npShowArt !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">แสดงแถบเวลา</span>
              <label class="cwc-switch">
                <input type="checkbox" id="compNpShowProgress" ${w.npShowProgress !== false ? 'checked' : ''}>
                <span class="cwc-slider-round"></span>
              </label>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีแถบเวลา</span>
              <input type="color" class="cwc-color-pick" id="compNpAccentColor" value="${w.npAccentColor || '#10b981'}">
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">สีตัวหนังสือ</span>
              <input type="color" class="cwc-color-pick" id="compNpTextColor" value="${w.npTextColor || '#ffffff'}">
            </div>
          </div>
        </div>
      `;
    } else if (w.type === 'emote_party') {
      specificHtml = `
        <div class="comp-card-section">
          <div class="comp-card-header"><span class="comp-card-title">🎉 ตั้งค่าปาร์ตี้อีโมทลอย</span></div>
          <div class="comp-card-body">
            <div class="comp-field-row">
              <span class="comp-field-label">รูปแบบอนิเมชัน</span>
              <select class="cwc-select" id="compEpAnimation">
                <option value="float" ${(w.epAnimation || 'float') === 'float' ? 'selected' : ''}>ลอยขึ้นนุ่มนวล</option>
                <option value="bounce" ${w.epAnimation === 'bounce' ? 'selected' : ''}>เด้งกระดอน</option>
                <option value="fountain" ${w.epAnimation === 'fountain' ? 'selected' : ''}>พวยพุ่งน้ำพุ</option>
                <option value="dvd" ${w.epAnimation === 'dvd' ? 'selected' : ''}>เด้งชนผนัง</option>
                <option value="drop" ${w.epAnimation === 'drop' ? 'selected' : ''}>ตกกระทบพื้น</option>
              </select>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ระยะเวลาแสดงผล</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpDuration" min="1" max="10" value="${w.epDuration || 4}">
                <span class="cwc-slider-val" id="compEpDurationVal">${w.epDuration || 4} วิ</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">จำนวนสูงสุดบนจอ</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpMaxEmotes" min="5" max="50" value="${w.epMaxEmotes || 15}">
                <span class="cwc-slider-val" id="compEpMaxEmotesVal">${w.epMaxEmotes || 15} ตัว</span>
              </div>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">ขนาดอีโมท</span>
              <div class="cwc-slider-wrap">
                <input type="range" class="cwc-slider" id="compEpEmoteSize" min="24" max="96" value="${w.epEmoteSize || 48}">
                <span class="cwc-slider-val" id="compEpEmoteSizeVal">${w.epEmoteSize || 48}px</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }
"""

if s_sp_start != -1 and s_sp_end != -1:
    code = code[:s_sp_start] + new_specific_html + "\n" + code[s_sp_end:]
    print("Replaced specificHtml sections successfully.")
else:
    print("ERROR: specificHtml boundaries not found!")

# 3. NEW BINDERS & DEMO ACTIONS
old_binders_start = "    // Bind Demo Action Buttons"
s_bnd_start = code.find(old_binders_start)
s_bnd_end = code.find("  // Setup Toolbar Events\n  function setupToolbarEvents() {", s_bnd_start)

new_binders = """    // Bind Demo Action Buttons
    const btnDemoChatLoop = document.getElementById('btnDemoChatLoop');
    const btnDemoChatSingle = document.getElementById('btnDemoChatSingle');
    if (btnDemoChatLoop) btnDemoChatLoop.addEventListener('click', () => ComposerDemoManager.toggleChatLoop(w, btnDemoChatLoop));
    if (btnDemoChatSingle) btnDemoChatSingle.addEventListener('click', () => ComposerDemoManager.sendChatMsg(w));

    const btnDemoDanmakuLoop = document.getElementById('btnDemoDanmakuLoop');
    const btnDemoDanmakuSingle = document.getElementById('btnDemoDanmakuSingle');
    if (btnDemoDanmakuLoop) btnDemoDanmakuLoop.addEventListener('click', () => ComposerDemoManager.toggleDanmakuLoop(w, btnDemoDanmakuLoop));
    if (btnDemoDanmakuSingle) btnDemoDanmakuSingle.addEventListener('click', () => ComposerDemoManager.sendDanmakuMsg(w));

    const btnCompChatDemoSend = document.getElementById('btnCompChatDemoSend');
    const compChatDemoInput = document.getElementById('compChatDemoInput');
    if (btnCompChatDemoSend && compChatDemoInput) {
      const sendCustom = () => {
        const val = compChatDemoInput.value.trim();
        if (!val) return;
        if (w.chatMode === 'danmaku') {
          ComposerDemoManager.sendDanmakuMsg(w, val);
        } else {
          ComposerDemoManager.sendChatMsg(w, val);
        }
        compChatDemoInput.value = '';
      };
      btnCompChatDemoSend.addEventListener('click', sendCustom);
      compChatDemoInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendCustom();
      });
    }

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

    const btnDemoViewerRandom = document.getElementById('btnDemoViewerRandom');
    const btnDemoViewerAdd = document.getElementById('btnDemoViewerAdd');
    const btnDemoViewerSub = document.getElementById('btnDemoViewerSub');
    if (btnDemoViewerRandom) btnDemoViewerRandom.addEventListener('click', () => ComposerDemoManager.triggerViewerRandom(w));
    if (btnDemoViewerAdd) btnDemoViewerAdd.addEventListener('click', () => ComposerDemoManager.triggerViewerAdd(w, 50));
    if (btnDemoViewerSub) btnDemoViewerSub.addEventListener('click', () => ComposerDemoManager.triggerViewerSub(w, 30));

    const btnDemoEmoteParty = document.getElementById('btnDemoEmoteParty');
    if (btnDemoEmoteParty) btnDemoEmoteParty.addEventListener('click', () => ComposerDemoManager.triggerEmoteParty(w));

    const btnDemoNowPlayingNext = document.getElementById('btnDemoNowPlayingNext');
    if (btnDemoNowPlayingNext) btnDemoNowPlayingNext.addEventListener('click', () => ComposerDemoManager.triggerNowPlayingNext(w));

    // Binders for specific widgets
    if (w.type === 'chat') {
      const mode = w.chatMode || 'default';
      if (mode === 'danmaku') {
        bindField('cwcDanmakuColor', 'fontColor');
        bindField('cwcDanmakuSize', 'fontSize', 'number', 'px');
        bindField('cwcDanmakuSpeed', 'speed', 'number', ' วิ');
        bindField('cwcDanmakuOpacity', 'opacity', 'opacity');
        bindField('cwcDanmakuZone', 'slider_zone');
        bindField('cwcDanmakuStrokeColor', 'strokeColor');
        bindField('cwcDanmakuStrokeWidth', 'textStrokeWidth', 'number', 'px');
        bindField('cwcDanmakuShadowColor', 'textShadowColor');
        const chkDanmakuStroke = document.getElementById('cwcDanmakuStroke');
        if (chkDanmakuStroke) {
          chkDanmakuStroke.addEventListener('change', () => {
            w.textStroke = chkDanmakuStroke.checked;
            renderCanvasWidgets();
            saveState();
          });
        }
      } else if (mode === 'balloon') {
        bindField('cwcBalloonBg', 'balloonBg');
        bindField('cwcBalloonColor', 'balloonTextColor');
        bindField('cwcBalloonRadius', 'balloonRadius', 'number', 'px');
        bindField('cwcBalloonSize', 'fontSize', 'number', 'px');
        bindField('cwcBalloonOpacity', 'balloonOpacity', 'opacity');
      } else if (mode === 'character') {
        bindField('cwcCharName', 'characterName');
        bindField('cwcCharAlign', 'charAlign');
        bindField('cwcCharBubbleBg', 'charBubbleBg');
        bindField('cwcCharTextColor', 'charTextColor');
        bindField('cwcCharFontSize', 'charFontSize', 'number', 'px');
      } else {
        // Mode: Default / Theme
        const tabStd = document.getElementById('tabSubStandard');
        const tabThm = document.getElementById('tabSubTheme');
        if (tabStd) tabStd.addEventListener('click', () => { state.chatSubTab = 'standard'; renderWidgetCustomizerPanel(w.id); });
        if (tabThm) tabThm.addEventListener('click', () => { state.chatSubTab = 'theme'; renderWidgetCustomizerPanel(w.id); });

        document.querySelectorAll('#cwcPresetsGrid .cwc-preset-card').forEach(card => {
          card.addEventListener('click', () => {
            w.chatTheme = card.dataset.chatTheme;
            renderCanvasWidgets();
            renderWidgetCustomizerPanel(w.id);
            saveState();
          });
        });

        const allThemes = window.CWC_ALL_THEMES || [];
        const totalPages = Math.ceil(allThemes.length / 8);
        const btnPrev = document.getElementById('btnThemePrev');
        const btnNext = document.getElementById('btnThemeNext');
        if (btnPrev) btnPrev.addEventListener('click', () => {
          state.chatThemePage = Math.max(1, (state.chatThemePage || 1) - 1);
          renderWidgetCustomizerPanel(w.id);
        });
        if (btnNext) btnNext.addEventListener('click', () => {
          state.chatThemePage = Math.min(totalPages, (state.chatThemePage || 1) + 1);
          renderWidgetCustomizerPanel(w.id);
        });

        // Section 1: Layout & Structure
        bindField('cwcLayout', 'layout');
        bindField('cwcDirection', 'direction');
        bindField('cwcAlign', 'align');
        bindField('cwcMsgSpacing', 'msgSpacing', 'number', 'px');
        bindField('cwcMaxMessages', 'maxMessages', 'number');

        // Section 2: Typography & Font
        bindField('cwcFontFamily', 'fontFamily');
        bindField('cwcFontSize', 'fontSize', 'number', 'px');
        bindField('cwcFontWeight', 'fontWeight');
        bindField('cwcUsernameColor', 'usernameColor');
        bindField('cwcMessageColor', 'fontColor');
        bindField('cwcTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
        bindField('cwcTextStrokeColor', 'strokeColor');
        bindField('cwcTextShadowBlur', 'textShadowBlur', 'number', 'px');
        bindField('cwcTextShadowColor', 'textShadowColor');

        const chkTextStroke = document.getElementById('cwcTextStroke');
        const textStrokeWRow = document.getElementById('cwcTextStrokeWidthRow');
        const textStrokeCRow = document.getElementById('cwcTextStrokeColorRow');
        if (chkTextStroke) {
          chkTextStroke.addEventListener('change', () => {
            w.textStroke = chkTextStroke.checked;
            if (textStrokeWRow) textStrokeWRow.style.display = chkTextStroke.checked ? 'flex' : 'none';
            if (textStrokeCRow) textStrokeCRow.style.display = chkTextStroke.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        const chkTextShadow = document.getElementById('cwcTextShadow');
        const textShadowBRow = document.getElementById('cwcTextShadowBlurRow');
        const textShadowCRow = document.getElementById('cwcTextShadowColorRow');
        if (chkTextShadow) {
          chkTextShadow.addEventListener('change', () => {
            w.textShadow = chkTextShadow.checked;
            if (textShadowBRow) textShadowBRow.style.display = chkTextShadow.checked ? 'flex' : 'none';
            if (textShadowCRow) textShadowCRow.style.display = chkTextShadow.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        // Section 3: Message Box & Bubble
        bindField('cwcBoxWidth', 'boxWidth');
        bindField('cwcBgColor', 'bgColor');
        bindField('cwcBgOpacity', 'bgOpacity', 'opacity');
        bindField('cwcBoxRadius', 'boxRadius', 'number', 'px');
        bindField('cwcBoxPadding', 'boxPadding', 'number', 'px');
        bindField('cwcBoxBorderWidth', 'boxBorderWidth', 'number', 'px');
        bindField('cwcBoxBorderColor', 'boxBorderColor');
        bindField('cwcBoxGlowColor', 'boxGlowColor');

        const chkBoxEnabled = document.getElementById('cwcBoxEnabled');
        if (chkBoxEnabled) chkBoxEnabled.addEventListener('change', () => { w.boxEnabled = chkBoxEnabled.checked; renderCanvasWidgets(); saveState(); });

        const chkBoxBorder = document.getElementById('cwcBoxBorder');
        const boxBorderWRow = document.getElementById('cwcBoxBorderWidthRow');
        const boxBorderCRow = document.getElementById('cwcBoxBorderColorRow');
        if (chkBoxBorder) {
          chkBoxBorder.addEventListener('change', () => {
            w.boxBorder = chkBoxBorder.checked;
            if (boxBorderWRow) boxBorderWRow.style.display = chkBoxBorder.checked ? 'flex' : 'none';
            if (boxBorderCRow) boxBorderCRow.style.display = chkBoxBorder.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        const chkBoxShadow = document.getElementById('cwcBoxShadow');
        if (chkBoxShadow) chkBoxShadow.addEventListener('change', () => { w.boxShadow = chkBoxShadow.checked; renderCanvasWidgets(); saveState(); });

        const chkBoxGlow = document.getElementById('cwcBoxGlow');
        const boxGlowCRow = document.getElementById('cwcBoxGlowColorRow');
        if (chkBoxGlow) {
          chkBoxGlow.addEventListener('change', () => {
            w.boxGlow = chkBoxGlow.checked;
            if (boxGlowCRow) boxGlowCRow.style.display = chkBoxGlow.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }

        // Section 4: Animations & Auto-Hide
        bindField('cwcAnimation', 'animation');
        bindField('cwcHideAfter', 'hideAfter', 'number', ' วินาที');

        const chkAutoHide = document.getElementById('cwcAutoHide');
        const hideAfterRow = document.getElementById('cwcHideAfterRow');
        if (chkAutoHide) {
          chkAutoHide.addEventListener('change', () => {
            w.autoHide = chkAutoHide.checked;
            if (hideAfterRow) hideAfterRow.style.display = chkAutoHide.checked ? 'flex' : 'none';
            renderCanvasWidgets();
            saveState();
          });
        }
      }
    }
    else if (w.type === 'clock') {
      bindField('compClockTheme', 'clockTheme');
      bindField('compClockFormat', 'clockFormat');
      bindField('compClockShowSeconds', 'showSeconds', 'checkbox');
      bindField('compClockFontSize', 'fontSize', 'number', 'px');
      bindField('compClockFontColor', 'fontColor');
    } else if (w.type === 'text') {
      bindField('compTextInput', 'text');
      const textModeEl = document.getElementById('compTextMode');
      const speedRow = document.getElementById('compTextSpeedRow');
      if (textModeEl) {
        textModeEl.addEventListener('change', () => {
          w.textMode = textModeEl.value;
          if (speedRow) speedRow.style.display = w.textMode === 'ticker' ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compTextSpeed', 'marqueeSpeed', 'number', ' วิ');
      bindField('compTextFontSize', 'fontSize', 'number', 'px');
      bindField('compTextFontColor', 'fontColor');
      bindField('compTextBgColor', 'bgColor');

      const chkTextStroke = document.getElementById('compTextStroke');
      const strokeWRow = document.getElementById('compTextStrokeWidthRow');
      const strokeCRow = document.getElementById('compTextStrokeColorRow');
      if (chkTextStroke) {
        chkTextStroke.addEventListener('change', () => {
          w.textStroke = chkTextStroke.checked;
          if (strokeWRow) strokeWRow.style.display = chkTextStroke.checked ? 'flex' : 'none';
          if (strokeCRow) strokeCRow.style.display = chkTextStroke.checked ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
      bindField('compTextStrokeColor', 'strokeColor');

      const chkTextShadow = document.getElementById('compTextShadow');
      const shadowBRow = document.getElementById('compTextShadowBlurRow');
      const shadowCRow = document.getElementById('compTextShadowColorRow');
      if (chkTextShadow) {
        chkTextShadow.addEventListener('change', () => {
          w.textShadow = chkTextShadow.checked;
          if (shadowBRow) shadowBRow.style.display = chkTextShadow.checked ? 'flex' : 'none';
          if (shadowCRow) shadowCRow.style.display = chkTextShadow.checked ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compTextShadowBlur', 'textShadowBlur', 'number', 'px');
      bindField('compTextShadowColor', 'textShadowColor');
    } else if (w.type === 'webcam') {
      const ratioEl = document.getElementById('compWebcamRatio');
      if (ratioEl) {
        ratioEl.addEventListener('change', () => {
          const ratio = ratioEl.value;
          w.ratio = ratio;
          let newH = w.height;
          if (ratio === '16:9') newH = Math.round(w.width * 9 / 16);
          else if (ratio === '4:3') newH = Math.round(w.width * 3 / 4);
          else if (ratio === '1:1') newH = Math.round(w.width);
          else if (ratio === '9:16') newH = Math.round(w.width * 16 / 9);
          w.height = newH;
          updateTransformInspector();
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compWebcamTheme', 'webcamTheme');
      bindField('compWebcamBorderWidth', 'borderWidth', 'number', 'px');
      bindField('compWebcamBorderColor', 'borderColor');
    } else if (w.type === 'goal') {
      bindField('compGoalTitle', 'goalTitle');
      bindField('compGoalCurrent', 'goalCurrent', 'number');
      bindField('compGoalTarget', 'goalTarget', 'number');
      bindField('compGoalUnit', 'goalUnit');
    } else if (w.type === 'viewer') {
      bindField('compViewerTheme', 'viewerTheme');
      bindField('compViewerMode', 'viewerMode');
      bindField('compViewerDirection', 'viewerDirection');
      bindField('compViewerAlign', 'viewerAlign');
      bindField('compViewerShowIcon', 'showIcon', 'checkbox');
      bindField('compViewerIconSize', 'iconSize', 'number', 'px');
      bindField('compViewerFontSize', 'fontSize', 'number', 'px');
      bindField('compViewerFontColor', 'fontColor');

      const chkViewerStroke = document.getElementById('compViewerTextStroke');
      const strokeWRow = document.getElementById('compViewerTextStrokeRow');
      const strokeCRow = document.getElementById('compViewerTextStrokeColorRow');
      if (chkViewerStroke) {
        chkViewerStroke.addEventListener('change', () => {
          w.textStroke = chkViewerStroke.checked;
          if (strokeWRow) strokeWRow.style.display = chkViewerStroke.checked ? 'flex' : 'none';
          if (strokeCRow) strokeCRow.style.display = chkViewerStroke.checked ? 'flex' : 'none';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compViewerTextStrokeWidth', 'textStrokeWidth', 'number', 'px');
      bindField('compViewerTextStrokeColor', 'strokeColor');
    } else if (w.type === 'character') {
      bindField('compCharWidgetName', 'characterName');
    } else if (w.type === 'image') {
      bindField('compImageUrl', 'imageUrl');
      bindField('compImageFit', 'fitMode');
    } else if (w.type === 'video') {
      bindField('compVideoUrl', 'videoUrl');
      bindField('compVideoFit', 'fitMode');
    } else if (w.type === 'alert') {
      bindField('compAlertUrl', 'url');
      const btnRefresh = document.getElementById('btnRefreshAlert');
      if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
          renderCanvasWidgets();
          if (window.showToast) window.showToast('รีเฟรชหน้าเว็บเบราว์เซอร์สำเร็จ');
        });
      }
    } else if (w.type === 'now_playing') {
      bindField('compNpTitle', 'songTitle');
      bindField('compNpArtist', 'artist');
      const chkTrans = document.getElementById('compNpTransparent');
      const bgClrRow = document.getElementById('compNpBgColorRow');
      if (chkTrans) {
        chkTrans.addEventListener('change', () => {
          w.npTransparent = chkTrans.checked;
          if (bgClrRow) bgClrRow.style.display = chkTrans.checked ? 'none' : 'flex';
          renderCanvasWidgets();
          saveState();
        });
      }
      bindField('compNpBgColor', 'npBgColor');
      bindField('compNpShowArt', 'npShowArt', 'checkbox');
      bindField('compNpShowProgress', 'npShowProgress', 'checkbox');
      bindField('compNpAccentColor', 'npAccentColor');
      bindField('compNpTextColor', 'npTextColor');
    } else if (w.type === 'emote_party') {
      bindField('compEpAnimation', 'epAnimation');
      bindField('compEpDuration', 'epDuration', 'number', ' วิ');
      bindField('compEpMaxEmotes', 'epMaxEmotes', 'number', ' ตัว');
      bindField('compEpEmoteSize', 'epEmoteSize', 'number', 'px');
    }
  }
"""

if s_bnd_start != -1 and s_bnd_end != -1:
    code = code[:s_bnd_start] + new_binders + "\n\n" + code[s_bnd_end:]
    print("Replaced binders and demo actions successfully.")
else:
    print("ERROR: binders boundaries not found!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Part 3 written.")
