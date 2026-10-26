import re

# 1. Update src/composer_studio.css
css_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace first .composer-layers-list block
css_target1 = """.composer-layers-list {
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  gap: 4px;
  max-height: 240px;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
}"""

css_repl1 = """.composer-layers-list {
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  gap: 4px;
  max-height: min(560px, calc(100vh - 350px));
  min-height: 180px;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
  transition: max-height 0.2s ease;
}

.composer-layers-list.expanded {
  max-height: none !important;
  height: auto !important;
}"""

if css_target1 in css:
    css = css.replace(css_target1, css_repl1, 1)
    print("1. Replaced first .composer-layers-list block in CSS")
else:
    print("WARNING: css_target1 not found in composer_studio.css")

# Replace second .composer-layers-list block
css_target2 = """/* Layers List */
.composer-layers-list {
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  gap: 4px;
  max-height: 240px;
  overflow-y: auto;
}"""

css_repl2 = """/* Layers List */
.composer-layers-list {
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  gap: 4px;
  overflow-y: auto;
}"""

if css_target2 in css:
    css = css.replace(css_target2, css_repl2, 1)
    print("2. Replaced second .composer-layers-list block in CSS")
else:
    print("WARNING: css_target2 not found in composer_studio.css")

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Update src/index.html for expand button & layer count
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

html_target = """        <div class="composer-side-header">
          <span>เลเยอร์วิดเจ็ตในหน้านี้</span>
          <span style="font-size: 11px; color: var(--dc-text-muted);">ลำดับชั้น</span>
        </div>"""

html_repl = """        <div class="composer-side-header" style="display:flex; justify-content:space-between; align-items:center;">
          <span>เลเยอร์วิดเจ็ตในหน้านี้</span>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size: 11px; color: var(--dc-text-muted);" id="composerLayerCount">ลำดับชั้น</span>
            <button type="button" class="btn-expand-layers" id="btnToggleLayersExpand" title="สลับขยายดูเลเยอร์ทั้งหมด / ย่อขนาด" style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.15); border-radius:4px; color:#cbd5e1; font-size:11px; padding:2px 7px; cursor:pointer; transition:all 0.15s ease;">⛶ ขยายดูทั้งหมด</button>
          </div>
        </div>"""

if html_target in html:
    html = html.replace(html_target, html_repl, 1)
    print("3. Updated index.html header with expand button and layer count ID")
else:
    print("WARNING: html_target not found in index.html, attempting regex match...")
    pattern_side_header = r"""(<div class="composer-side-header">[\s\S]*?id="composerLayersList")"""
    match = re.search(r"""<div class="composer-sidebar-right">\s*<div class="composer-side-header">[\s\S]*?<\/div>""", html)
    if match:
        html = html[:match.start()] + """<div class="composer-sidebar-right">\n""" + html_repl + html[match.end():]
        print("3. Updated index.html header using regex match")
    else:
        print("WARNING: index.html regex failed")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 3. Update src/composer_studio.js for layer count display and button toggle listener
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Update renderLayersList to update composerLayerCount text
target_rl = "list.innerHTML = '';\n    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));"
repl_rl = """list.innerHTML = '';
    const sorted = [...page.widgets].sort((a, b) => (b.z || 0) - (a.z || 0));
    const countEl = document.getElementById('composerLayerCount');
    if (countEl) countEl.textContent = `${sorted.length} เลเยอร์`;"""

if target_rl in js:
    js = js.replace(target_rl, repl_rl, 1)
    print("4. Updated renderLayersList to display layer count")
else:
    print("WARNING: target_rl not found in composer_studio.js")

# In initComposerStudio, add listener for btnToggleLayersExpand
target_init = "// Left Drawer Expand Button Listener"
repl_init = """// Layers List Expand/Collapse Button Listener
    const btnToggleLayers = document.getElementById('btnToggleLayersExpand');
    const layersList = document.getElementById('composerLayersList');
    if (btnToggleLayers && layersList) {
      btnToggleLayers.addEventListener('click', () => {
        const isExpanded = layersList.classList.toggle('expanded');
        btnToggleLayers.textContent = isExpanded ? '🗗 ย่อขนาด' : '⛶ ขยายดูทั้งหมด';
        btnToggleLayers.style.background = isExpanded ? 'rgba(88, 101, 242, 0.25)' : 'rgba(255,255,255,0.06)';
        btnToggleLayers.style.borderColor = isExpanded ? 'var(--dc-blurple)' : 'rgba(255,255,255,0.15)';
        btnToggleLayers.style.color = isExpanded ? '#ffffff' : '#cbd5e1';
      });
    }

    // Left Drawer Expand Button Listener"""

if target_init in js:
    js = js.replace(target_init, repl_init, 1)
    print("5. Added btnToggleLayersExpand listener in initComposerStudio")
else:
    print("WARNING: target_init not found in composer_studio.js")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("All updates applied successfully!")
