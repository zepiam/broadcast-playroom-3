/* Replie commands use the original ticker/image/combo payload and renderer. */
(() => {
  'use strict';
  window.editReplieCommand = function(previous) {
    const doc = getToolDocument('replie'),
          old = window._replieCommands[previous] || {},
          payload = structuredClone(old.legacyPayload || {});
    payload.ticker ||= { enabled: !!old.text, text: old.text || '', layout: 'bottom_ticker' };
    payload.image ||= { enabled: !!old.imageUrl, image_url: old.imageUrl || '', layout: 'card' };

    const dialog = doc.createElement('dialog');
    dialog.id = 'replieCommandEditor';
    dialog.style.cssText = `
      width: min(780px, 94vw);
      max-height: 88vh;
      overflow-y: auto;
      background: var(--dc-bg-card, #232428);
      color: var(--dc-text-primary, #f2f3f5);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 12px;
      padding: 0;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
      font-family: inherit;
    `;

    // Click outside backdrop to close
    dialog.addEventListener('click', (e) => {
      const rect = dialog.getBoundingClientRect();
      if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) {
        dialog.close();
      }
    });

    const form = doc.createElement('form');
    form.method = 'dialog';
    form.style.cssText = 'display: flex; flex-direction: column; margin: 0; padding: 0;';
    dialog.append(form);

    // Header with prominent close button
    const header = doc.createElement('div');
    header.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 20px;
      background: var(--dc-bg-rail, #1e1f22);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      position: sticky;
      top: 0;
      z-index: 10;
    `;
    const heading = doc.createElement('div');
    heading.style.cssText = 'display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; color: #38bdf8;';
    heading.innerHTML = `<span>🖼️</span><span>${previous ? 'แก้ไขคำสั่ง Replie (' + previous + ')' : 'สร้างคำสั่ง Replie ใหม่'}</span>`;
    
    const closeBtn = doc.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'btn-win-action close-red';
    closeBtn.style.cssText = 'width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; border-radius: 6px;';
    closeBtn.textContent = '✕';
    closeBtn.title = 'ปิดหน้าต่าง';
    closeBtn.onclick = () => dialog.close();
    header.append(heading, closeBtn);
    form.append(header);

    const body = doc.createElement('div');
    body.style.cssText = 'padding: 16px 20px; display: flex; flex-direction: column; gap: 14px;';
    form.append(body);

    const controls = {};
    function field(parent, path, label, type, value, options) {
      const row = doc.createElement('div');
      row.className = 'comp-field-row';
      row.style.cssText = 'display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin: 6px 0;';
      const title = doc.createElement('label');
      title.textContent = label;
      title.style.cssText = 'flex: 1 1 180px; font-size: 13px; font-weight: 500; color: #cbd5e1;';
      const input = doc.createElement(options ? 'select' : type === 'textarea' ? 'textarea' : 'input');
      input.id = 'replieEdit_' + path.replaceAll('.', '_');
      title.htmlFor = input.id;
      input.className = 'modal-input';
      input.style.cssText = 'flex: 2 1 260px; min-width: 0; padding: 6px 10px; border-radius: 6px; background: #1e1f22; border: 1px solid rgba(255,255,255,0.12); color: #fff; font-family: inherit;';
      if (options) {
        for (const option of options) {
          const node = doc.createElement('option');
          node.value = Array.isArray(option) ? option[0] : option;
          node.textContent = Array.isArray(option) ? option[1] : option;
          input.append(node);
        }
      } else if (type !== 'textarea') {
        input.type = type;
      }
      if (type === 'number') input.step = 'any';
      if (type === 'checkbox') {
        input.type = 'checkbox';
        input.checked = value;
        input.style.cssText = 'width: 18px; height: 18px; accent-color: var(--dc-green, #10b981); cursor: pointer;';
      } else {
        input.value = value ?? '';
      }
      row.append(title, input);
      parent.append(row);
      controls[path] = { input, type };
      return input;
    }

    // Section 1: Main Config Card
    const secMain = doc.createElement('div');
    secMain.style.cssText = 'background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 14px;';
    const secMainTitle = doc.createElement('div');
    secMainTitle.textContent = '⚙️ ตั้งค่าคำสั่งหลัก';
    secMainTitle.style.cssText = 'font-weight: 700; font-size: 13.5px; color: #fbbf24; margin-bottom: 10px;';
    secMain.append(secMainTitle);
    body.append(secMain);

    field(secMain, 'command', 'คำสั่งแชท (เช่น !hi หรือ !dance)', 'text', previous || '!hello');
    field(secMain, 'mode', 'รูปแบบการแสดงผล', 'text', payload.ticker.enabled && payload.image.enabled ? 'combo' : payload.image.enabled ? 'image' : 'ticker', [['ticker', 'ข้อความวิ่ง (Ticker)'], ['image', 'รูปภาพป๊อปอัป'], ['combo', 'ข้อความ + รูปภาพ (Combo)']]);
    field(secMain, 'duration_sec', 'ระยะเวลาแสดงบนจอ (วินาที)', 'number', payload.duration_sec || old.duration || 8);
    field(secMain, 'cooldown', 'คูลดาวน์กันสแปม (วินาที)', 'number', old.cooldown || 0);
    field(secMain, 'enabled', 'เปิดใช้งานคำสั่งนี้', 'checkbox', old.enabled !== false);
    field(secMain, 'is_loop', 'แสดงวนลูปต่อเนื่อง', 'checkbox', payload.is_loop || false);
    field(secMain, 'progress_style', 'แถบนับเวลาถอยหลัง', 'text', payload.progress_style || 'cyan', [['cyan', 'สีฟ้า Cyan'], ['gold', 'สีทอง Gold'], ['violet', 'สีม่วง Violet'], ['emerald', 'สีเขียว Emerald'], ['sunset', 'สีส้ม Sunset']]);

    // Section 2 & 3: Ticker and Image Cards
    for (const kind of ['ticker', 'image']) {
      const sec = doc.createElement('div');
      sec.style.cssText = 'background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 14px;';
      const secTitle = doc.createElement('div');
      secTitle.textContent = kind === 'ticker' ? '💬 ข้อความที่จะแสดง (Ticker)' : '🖼️ รูปภาพ (Image Popup)';
      secTitle.style.cssText = 'font-weight: 700; font-size: 13.5px; color: #38bdf8; margin-bottom: 10px;';
      sec.append(secTitle);
      body.append(sec);

      const data = payload[kind];
      const defaults = kind === 'ticker'
        ? { text: '', title: '', layout: 'bottom_ticker', ticker_font: 'Kanit', ticker_font_size: 28, ticker_color: '#ffffff', ticker_bold: true }
        : { image_url: '', top_text: '', bottom_text: '', layout: 'card' };
      const labels = {
        text: 'ข้อความตอบกลับ', title: 'หัวข้อ', image_url: 'URL รูปภาพ',
        top_text: 'ข้อความด้านบน', bottom_text: 'ข้อความด้านล่าง',
        ticker_font: 'ฟอนต์', ticker_font_size: 'ขนาดฟอนต์', ticker_color: 'สีข้อความ', ticker_bold: 'ตัวหนา'
      };

      for (const [key, value] of Object.entries(defaults)) {
        if (key === 'layout') {
          field(sec, kind + '.layout', 'รูปแบบจัดวาง', 'text', data.layout || value, kind === 'ticker' ? [['bottom_ticker', 'แถบยาวล่างจอ'], ['full_ticker', 'เต็มความกว้าง'], ['side_card', 'การ์ดด้านข้าง']] : [['card', 'การ์ดมาตรฐาน'], ['full', 'เต็มกรอบ'], ['frameless', 'ไม่มีกรอบ']]);
          continue;
        }
        const type = typeof value === 'boolean' ? 'checkbox' : typeof value === 'number' ? 'number' : key.endsWith('color') ? 'color' : key === 'text' ? 'textarea' : 'text';
        const input = field(sec, kind + '.' + key, labels[key] || key, type, data[key] ?? value);
        if (key === 'image_url') {
          const uploadRow = doc.createElement('div');
          uploadRow.style.cssText = 'display: flex; gap: 8px; align-items: center; margin: 4px 0 10px; padding-left: 190px;';
          const uploadBtn = doc.createElement('button');
          uploadBtn.type = 'button';
          uploadBtn.className = 'btn-topbar-action';
          uploadBtn.style.cssText = 'padding: 4px 10px; font-size: 12px; cursor: pointer;';
          uploadBtn.textContent = '📁 เลือกรูปภาพจากเครื่อง...';
          uploadRow.append(uploadBtn);
          sec.append(uploadRow);

          uploadBtn.onclick = () => {
            const picker = doc.createElement('input');
            picker.type = 'file';
            picker.accept = 'image/*';
            picker.style.display = 'none';
            doc.body.append(picker);
            picker.onchange = async () => {
              const file = picker.files?.[0];
              picker.remove();
              if (!file) return;
              try {
                uploadBtn.textContent = '⏳ กำลังอัปโหลด...';
                uploadBtn.disabled = true;
                const response = await fetch('/api/playroom/import', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/octet-stream', 'X-Filename': encodeURIComponent(file.name) },
                  body: file
                });
                const result = await response.json();
                if (response.ok && result.url) input.value = result.url;
              } catch (_) {
              } finally {
                uploadBtn.textContent = '📁 เลือกรูปภาพจากเครื่อง...';
                uploadBtn.disabled = false;
              }
            };
            picker.click();
          };
        }
      }

      for (const [key, label, type, value, options] of [
        ['pos_x', 'ตำแหน่ง X (%)', 'number', kind === 'ticker' ? 50 : 85],
        ['pos_y', 'ตำแหน่ง Y (%)', 'number', kind === 'ticker' ? 88 : 50],
        ['scale', 'สเกลขนาด', 'number', 1],
        ['opacity', 'ความทึบ (0.1–1)', 'number', 0.95],
        ['anim_in', 'แอนิเมชันเปิดตัว', 'text', kind === 'ticker' ? 'slide-up' : 'slide-left', [['none', 'ไม่มี'], ['fade', 'เลือนเข้า'], ['slide-up', 'เลื่อนขึ้น'], ['slide-down', 'เลื่อนลง'], ['slide-left', 'เลื่อนจากซ้าย'], ['slide-right', 'เลื่อนจากขวา'], ['zoom', 'ขยายเข้า'], ['bounce', 'เด้งกระดอน']]],
        ['anim_out', 'แอนิเมชันตอนออก', 'text', 'slide-down', [['none', 'ไม่มี'], ['fade', 'เลือนหาย'], ['slide-up', 'เลื่อนขึ้นหาย'], ['slide-down', 'เลื่อนลงหาย'], ['zoom', 'ย่อหาย']]]
      ]) {
        field(sec, kind + '.' + key, label, type, data[key] ?? value, options);
      }
    }

    // Actions Footer with Cancel and Save buttons
    const actions = doc.createElement('div');
    actions.style.cssText = `
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 12px;
      position: sticky;
      bottom: 0;
      background: var(--dc-bg-rail, #1e1f22);
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding: 12px 20px;
      z-index: 10;
    `;
    const cancel = doc.createElement('button');
    cancel.type = 'button';
    cancel.className = 'btn-topbar-action';
    cancel.style.cssText = 'padding: 6px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; color: #cbd5e1;';
    cancel.textContent = '✕ ยกเลิก';
    cancel.onclick = () => dialog.close();

    const save = doc.createElement('button');
    save.type = 'submit';
    save.className = 'btn-topbar-action primary';
    save.style.cssText = 'padding: 6px 20px; border-radius: 6px; font-size: 13px; font-weight: 700; cursor: pointer; background: var(--dc-blurple, #3b82f6); color: #fff;';
    save.textContent = '💾 บันทึกคำสั่ง';

    actions.append(cancel, save);
    form.append(actions);

    form.onsubmit = event => {
      event.preventDefault();
      const values = {};
      for (const [key, { input, type }] of Object.entries(controls)) {
        values[key] = type === 'checkbox' ? input.checked : type === 'number' ? Number(input.value) : input.value;
      }
      const name = String(values.command).trim();
      if (!name) return;
      for (const [key, value] of Object.entries(values)) {
        if (key.includes('.')) {
          const [group, fieldKey] = key.split('.');
          payload[group][fieldKey] = value;
        } else if (!['command', 'mode', 'cooldown', 'enabled'].includes(key)) {
          payload[key] = value;
        }
      }
      payload.ticker.enabled = values.mode !== 'image';
      payload.image.enabled = values.mode !== 'ticker';
      if (previous && previous !== name) delete window._replieCommands[previous];
      window._replieCommands[name] = {
        ...old,
        enabled: values.enabled,
        text: payload.ticker.enabled ? payload.ticker.text : '',
        imageUrl: payload.image.enabled ? payload.image.image_url : '',
        duration: Math.max(1, values.duration_sec),
        cooldown: Math.max(0, values.cooldown),
        legacyPayload: payload
      };
      localStorage.setItem('bp3_replie_commands', JSON.stringify(window._replieCommands));
      renderReplieCommands();
      dialog.close();
    };

    dialog.onclose = () => dialog.remove();
    doc.body.append(dialog);
    dialog.showModal();
  };
})();
