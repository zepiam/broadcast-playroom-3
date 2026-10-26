import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

old_actions_target = text.find('const actions = document.createElement(\'div\');')
assert old_actions_target != -1, "actions block not found"
old_actions_end = text.find('// Switch Active Page', old_actions_target)

new_actions_block = """const actions = document.createElement('div');
    actions.className = 'composer-page-actions';
    actions.innerHTML = `
      <button type="button" class="composer-btn-page-action" id="btnPageNew" title="สร้างหน้าเลย์เอาต์ใหม่">➕ เพิ่มหน้า</button>
      <button type="button" class="composer-btn-page-action" id="btnPageReorder" title="สลับเรียงลำดับหน้าใหม่">🔀 เรียงหน้าใหม่</button>
      <button type="button" class="composer-btn-page-action" id="btnPageDup" title="ทำสำเนาหน้านี้พร้อมวิดเจ็ตทั้งหมด">📋 สำเนา</button>
      <button type="button" class="composer-btn-page-action" id="btnPageRename" title="เปลี่ยนชื่อหน้านี้">✎ เปลี่ยนชื่อ</button>
      ${state.pages.length > 1 ? `<button type="button" class="composer-btn-page-action btn-danger" id="btnPageDel" title="ลบหน้านี้">🗑 ลบ</button>` : ''}
    `;

    const btnNew = actions.querySelector('#btnPageNew');
    if (btnNew) btnNew.addEventListener('click', addNewPage);
    const btnReorder = actions.querySelector('#btnPageReorder');
    if (btnReorder) btnReorder.addEventListener('click', reorderPages);
    const btnDup = actions.querySelector('#btnPageDup');
    if (btnDup) btnDup.addEventListener('click', duplicateCurrentPage);
    const btnRename = actions.querySelector('#btnPageRename');
    if (btnRename) btnRename.addEventListener('click', renameCurrentPage);
    const btnDel = actions.querySelector('#btnPageDel');
    if (btnDel) btnDel.addEventListener('click', () => deletePage(state.activePageId));

    pageBar.appendChild(actions);
    container.appendChild(pageBar);
  }

  function reorderPages() {
    if (state.pages.length <= 1) {
      if (window.showToast) window.showToast('ℹ️ มีหน้าเลย์เอาต์เพียง 1 หน้า กรุณากด "➕ เพิ่มหน้า" ก่อนครับ');
      return;
    }
    const curIdx = state.pages.findIndex(p => p.id === state.activePageId);
    if (curIdx !== -1) {
      const nextIdx = (curIdx + 1) % state.pages.length;
      const [moved] = state.pages.splice(curIdx, 1);
      state.pages.splice(nextIdx, 0, moved);
      renderPageTabs();
      saveState();
      if (window.showToast) window.showToast(`🔀 ย้ายหน้า "${moved.name}" ไปยังลำดับที่ ${nextIdx + 1} แล้ว`);
    }
  }

  """

text = text[:old_actions_target] + new_actions_block + text[old_actions_end:]

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated renderPageTabs with เรียงหน้าใหม่ button successfully.")
