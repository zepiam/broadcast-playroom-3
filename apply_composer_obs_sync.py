import os

path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update saveState
old_save_state = '''  // Save current layout to localStorage
  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.pages));
      if (window.showToast) {
        window.showToast('บันทึกเลย์เอาต์หน้าจอเรียบร้อยแล้ว');
      }
    } catch (e) {
      console.error('Failed to save composer state:', e);
    }
  }'''

new_save_state = '''  // Save current layout to localStorage & sync to OBS Server
  function saveState(silent) {
    try {
      const payload = {
        pages: state.pages,
        activePageId: state.activePageId,
        updatedAt: Date.now()
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.pages));
      localStorage.setItem(STORAGE_KEY + '_full', JSON.stringify(payload));

      // Push to backend server API for OBS Studio Browser Source
      fetch('/api/composer/layout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(() => {});

      // Broadcast to any open windows
      try {
        if ('BroadcastChannel' in window) {
          const bus = new BroadcastChannel('bp3_system_channel');
          bus.postMessage({ event: 'CANVAS_LAYOUT_SAVED', payload });
        }
      } catch (e) {}

      if (!silent && window.showToast) {
        window.showToast('บันทึกเลย์เอาต์หน้าจอและส่งไปยัง OBS เรียบร้อยแล้ว');
      }
    } catch (e) {
      console.error('Failed to save composer state:', e);
    }
  }'''

if old_save_state in content:
    content = content.replace(old_save_state, new_save_state, 1)
    print("Replaced saveState")
else:
    print("Warning: old_save_state not found!")

# 2. Update setupToolbarEvents to bind btnCompTestBrowser
old_bind = '''    // Copy OBS URL Button
    document.getElementById('btnCompCopyObs')?.addEventListener('click', copyComposerObsUrl);
  }'''

new_bind = '''    // Copy OBS URL Button
    document.getElementById('btnCompCopyObs')?.addEventListener('click', copyComposerObsUrl);

    // Test in Browser Button
    document.getElementById('btnCompTestBrowser')?.addEventListener('click', openComposerTestInBrowser);
  }'''

if old_bind in content:
    content = content.replace(old_bind, new_bind, 1)
    print("Replaced toolbar events bind")
else:
    print("Warning: old_bind not found!")

# 3. Update copyComposerObsUrl and add openComposerTestInBrowser
old_copy = '''  // Copy OBS URL
  function copyComposerObsUrl() {
    const host = window.location.origin || 'http://127.0.0.1:8080';
    const activePage = getActivePage();
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/overlay.html?p=${pageIndex}`;

    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        if (window.showToast) window.showToast(`คัดลอกลิงก์ OBS สำหรับหน้า ${pageIndex} สำเร็จ`);
      }).catch(() => {
        prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
      });
    } else {
      prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
    }
  }'''

new_copy = '''  // Copy OBS URL
  function copyComposerObsUrl() {
    const host = (window.location.origin && window.location.origin.startsWith('http')) ? window.location.origin : 'http://127.0.0.1:8080';
    const activePage = getActivePage();
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/composer.html?p=${pageIndex}`;
    saveState(true);

    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        if (window.showToast) window.showToast(`📋 คัดลอกลิงก์ OBS สำหรับหน้า ${pageIndex} สำเร็จ (${url})`);
      }).catch(() => {
        prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
      });
    } else {
      prompt('คัดลอกลิงก์ OBS ของคุณ:', url);
    }
  }

  // Open live test preview in browser
  function openComposerTestInBrowser() {
    const host = (window.location.origin && window.location.origin.startsWith('http')) ? window.location.origin : 'http://127.0.0.1:8080';
    const pageIndex = state.pages.findIndex(p => p.id === state.activePageId) + 1;
    const url = `${host}/composer.html?p=${pageIndex}&test=1`;
    saveState(true);
    window.open(url, '_blank');
    if (window.showToast) {
      window.showToast(`🧪 เปิดหน้าต่างทดสอบ Overlay (หน้า ${pageIndex}) ในเบราว์เซอร์แล้ว`);
    }
  }'''

if old_copy in content:
    content = content.replace(old_copy, new_copy, 1)
    print("Replaced copyComposerObsUrl and added openComposerTestInBrowser")
else:
    print("Warning: old_copy not found!")

# 4. Expose functions to window
old_expose = '''  // Expose Global Helper
  window.initComposerStudio = initComposerStudio;
  window.autoFitCanvas = autoFitCanvas;'''

new_expose = '''  // Expose Global Helper
  window.initComposerStudio = initComposerStudio;
  window.autoFitCanvas = autoFitCanvas;
  window.renderWidgetInnerHtml = renderWidgetInnerHtml;
  window.isFullscreenWidget = isFullscreenWidget;
  window.openComposerTestInBrowser = openComposerTestInBrowser;
  window.copyComposerObsUrl = copyComposerObsUrl;'''

if old_expose in content:
    content = content.replace(old_expose, new_expose, 1)
    print("Exposed renderWidgetInnerHtml to window")
else:
    print("Warning: old_expose not found!")

# 5. Expose on ComposerStudio object
old_cs_obj = '''    togglePreviewMode: togglePreviewMode,
    normalizeWidget: normalizeWidget
  };'''

new_cs_obj = '''    togglePreviewMode: togglePreviewMode,
    normalizeWidget: normalizeWidget,
    saveState: saveState,
    renderWidgetInnerHtml: renderWidgetInnerHtml,
    isFullscreenWidget: isFullscreenWidget,
    openTestInBrowser: openComposerTestInBrowser,
    copyObsUrl: copyComposerObsUrl
  };'''

if old_cs_obj in content:
    content = content.replace(old_cs_obj, new_cs_obj, 1)
    print("Added exports to window.ComposerStudio")
else:
    print("Warning: old_cs_obj not found!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Also copy to dist/composer_studio.js
dist_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer_studio.js'
with open(dist_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated both src and dist composer_studio.js successfully!")
