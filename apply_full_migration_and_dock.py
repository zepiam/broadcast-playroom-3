import os, sys

base_dir = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"
src_dir = os.path.join(base_dir, "src")

# 1. Update composer_studio.css
css_path = os.path.join(src_dir, "composer_studio.css")
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

preview_css = """
/* ═══ Clean Preview Mode (Hide UI for True OBS View) ═══ */
.preview-clean-mode .composer-topbar,
.preview-clean-mode .composer-sidebar-left,
.preview-clean-mode .composer-sidebar-right,
.preview-clean-mode .composer-btn-expand-cust,
.preview-clean-mode .widget-badge,
.preview-clean-mode .btn-widget-gear,
.preview-clean-mode .handle-nw,
.preview-clean-mode .handle-n,
.preview-clean-mode .handle-ne,
.preview-clean-mode .handle-e,
.preview-clean-mode .handle-se,
.preview-clean-mode .handle-s,
.preview-clean-mode .handle-sw,
.preview-clean-mode .handle-w {
  display: none !important;
}
.preview-clean-mode .composer-widget {
  border: none !important;
  box-shadow: none !important;
}
.composer-btn-tool.active {
  background: #6366f1 !important;
  color: #ffffff !important;
}
"""

if "/* ═══ Clean Preview Mode (Hide UI for True OBS View) ═══ */" not in css:
    css += "\n" + preview_css + "\n"
    with open(css_path, "w", encoding="utf-8", newline="") as f:
        f.write(css)
    print("Updated composer_studio.css with Preview Mode styling")

# 2. Update index.html to add Export, Import, Preview buttons in toolbar
html_path = os.path.join(src_dir, "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

old_save_group = (
    '        <button type="button" class="composer-btn-tool primary" id="btnCompCopyObs" title="คัดลอกลิงก์ Overlay สำหรับ OBS">\n'
    '          🔗 ลิงก์ OBS\n'
    '        </button>\n'
    '        <button type="button" class="composer-btn-tool success" id="btnCompSave" title="บันทึกเลย์เอาต์หน้าจอ">\n'
    '          💾 บันทึก\n'
    '        </button>'
)
is_html_crlf = "\r\n" in html
if is_html_crlf:
    old_save_group = old_save_group.replace("\n", "\r\n")

eol = "\r\n" if is_html_crlf else "\n"

new_save_group = (
    '        <button type="button" class="composer-btn-tool" id="btnCompPreview" title="สลับโหมดพรีวิว (ซ่อนกรอบเครื่องมือทั้งหมด)">' + eol +
    '          👁️ พรีวิว' + eol +
    '        </button>' + eol +
    '        <button type="button" class="composer-btn-tool" id="btnCompExport" title="สำรองข้อมูลเลย์เอาต์ทั้งหมดเป็นไฟล์ JSON">' + eol +
    '          📁 ส่งออก' + eol +
    '        </button>' + eol +
    '        <button type="button" class="composer-btn-tool" id="btnCompImport" title="นำเข้าไฟล์เลย์เอาต์ JSON จากเวอร์ชั่นเก่าหรือเครื่องอื่น">' + eol +
    '          📥 นำเข้า' + eol +
    '        </button>' + eol +
    '        <input type="file" id="fileCompImportProfile" accept=".json" style="display:none;">' + eol +
    old_save_group
)

if old_save_group in html:
    html = html.replace(old_save_group, new_save_group, 1)
    with open(html_path, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print("Updated index.html with Preview, Export, Import buttons")
else:
    print("old_save_group not found in index.html (or already patched)")

# 3. Update composer_studio.js with normalizeWidget, exportProfile, importProfile, togglePreviewMode, and auto-migration
js_path = os.path.join(src_dir, "composer_studio.js")
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

is_js_crlf = "\r\n" in js
eol_js = "\r\n" if is_js_crlf else "\n"

# Add normalizeWidget function before loadSavedState
normalizer_code = (
    "  // ═══ V2/V3 Universal Schema Migration & Dual-Key Normalizer ═══" + eol_js +
    "  function normalizeWidget(w) {" + eol_js +
    "    if (!w || typeof w !== 'object') return w;" + eol_js +
    "    // Normalize type aliases" + eol_js +
    "    if (w.type === 'avatar' || w.type === 'replie') {" + eol_js +
    "      w.type = 'character';" + eol_js +
    "    } else if (w.type === 'donate_goal') {" + eol_js +
    "      w.type = 'goal';" + eol_js +
    "    }" + eol_js +
    eol_js +
    "    // Geometry" + eol_js +
    "    w.x = parseInt(w.x ?? 0, 10);" + eol_js +
    "    w.y = parseInt(w.y ?? 0, 10);" + eol_js +
    "    const widthVal = w.width ?? w.w ?? 300;" + eol_js +
    "    const heightVal = w.height ?? w.h ?? 180;" + eol_js +
    "    w.width = parseInt(widthVal, 10);" + eol_js +
    "    w.w = w.width;" + eol_js +
    "    w.height = parseInt(heightVal, 10);" + eol_js +
    "    w.h = w.height;" + eol_js +
    eol_js +
    "    // Typography & Styling (Dual-Key for V2/V3 compatibility)" + eol_js +
    "    w.fontSize = parseInt(w.fontSize ?? w.font_size ?? 16, 10);" + eol_js +
    "    w.font_size = w.fontSize;" + eol_js +
    "    w.fontColor = w.fontColor || w.font_color || '#ffffff';" + eol_js +
    "    w.font_color = w.fontColor;" + eol_js +
    "    w.fontWeight = w.fontWeight || w.font_weight || '600';" + eol_js +
    "    w.font_weight = w.fontWeight;" + eol_js +
    "    w.fontFamily = w.fontFamily || w.font_family || 'Kanit';" + eol_js +
    "    w.font_family = w.fontFamily;" + eol_js +
    eol_js +
    "    // Stroke & Shadow" + eol_js +
    "    w.textStroke = w.textStroke ?? w.text_stroke ?? false;" + eol_js +
    "    w.text_stroke = w.textStroke;" + eol_js +
    "    w.textStrokeWidth = parseInt(w.textStrokeWidth ?? w.text_stroke_width ?? 2, 10);" + eol_js +
    "    w.text_stroke_width = w.textStrokeWidth;" + eol_js +
    "    w.textStrokeColor = w.textStrokeColor || w.text_stroke_color || w.strokeColor || '#000000';" + eol_js +
    "    w.text_stroke_color = w.textStrokeColor;" + eol_js +
    "    w.strokeColor = w.textStrokeColor;" + eol_js +
    "    w.textShadow = w.textShadow ?? w.text_shadow ?? true;" + eol_js +
    "    w.text_shadow = w.textShadow;" + eol_js +
    "    w.textShadowBlur = parseInt(w.textShadowBlur ?? w.text_shadow_blur ?? 3, 10);" + eol_js +
    "    w.text_shadow_blur = w.textShadowBlur;" + eol_js +
    "    w.textShadowColor = w.textShadowColor || w.text_shadow_color || '#000000';" + eol_js +
    "    w.text_shadow_color = w.textShadowColor;" + eol_js +
    eol_js +
    "    // Background" + eol_js +
    "    w.bgColor = w.bgColor || w.bg_color || '#1e1f22';" + eol_js +
    "    w.bg_color = w.bgColor;" + eol_js +
    "    w.bgOpacity = parseFloat(w.bgOpacity ?? w.bg_opacity ?? 0.85);" + eol_js +
    "    w.bg_opacity = w.bgOpacity;" + eol_js +
    "    w.boxRadius = parseInt(w.boxRadius ?? w.box_radius ?? 8, 10);" + eol_js +
    "    w.box_radius = w.boxRadius;" + eol_js +
    eol_js +
    "    // Viewer Widget" + eol_js +
    "    w.viewerTheme = w.viewerTheme || w.viewer_theme || 'default';" + eol_js +
    "    w.viewer_theme = w.viewerTheme;" + eol_js +
    "    w.viewerMode = w.viewerMode || w.viewer_mode || 'both';" + eol_js +
    "    w.viewer_mode = w.viewerMode;" + eol_js +
    "    w.viewerDirection = w.viewerDirection || w.viewer_direction || 'horizontal';" + eol_js +
    "    w.viewer_direction = w.viewerDirection;" + eol_js +
    "    w.viewerAlign = w.viewerAlign || w.viewer_align || 'left';" + eol_js +
    "    w.viewer_align = w.viewerAlign;" + eol_js +
    "    w.iconSize = parseInt(w.iconSize ?? w.viewer_icon_size ?? 20, 10);" + eol_js +
    "    w.viewer_icon_size = w.iconSize;" + eol_js +
    "    w.viewerPlatforms = w.viewerPlatforms || w.viewer_platforms || ['youtube', 'twitch', 'tiktok', 'kick'];" + eol_js +
    "    w.viewer_platforms = w.viewerPlatforms;" + eol_js +
    eol_js +
    "    // Chat Widget" + eol_js +
    "    w.chatTheme = w.chatTheme || w.chat_theme || 'default';" + eol_js +
    "    w.chat_theme = w.chatTheme;" + eol_js +
    "    w.chatMode = w.chatMode || w.chat_mode || 'default';" + eol_js +
    "    w.chat_mode = w.chatMode;" + eol_js +
    eol_js +
    "    // Now Playing Widget" + eol_js +
    "    w.npTheme = w.npTheme || w.np_theme || 'custom';" + eol_js +
    "    w.np_theme = w.npTheme;" + eol_js +
    "    w.npStyle = w.npStyle || w.np_style || 'flat';" + eol_js +
    "    w.np_style = w.npStyle;" + eol_js +
    "    w.npSource = w.npSource || w.np_source || 'auto';" + eol_js +
    "    w.np_source = w.npSource;" + eol_js +
    "    w.npShowArt = w.npShowArt ?? w.np_show_art ?? true;" + eol_js +
    "    w.np_show_art = w.npShowArt;" + eol_js +
    "    w.npShowProgress = w.npShowProgress ?? w.np_show_progress ?? true;" + eol_js +
    "    w.np_show_progress = w.npShowProgress;" + eol_js +
    "    w.npScrollTitle = w.npScrollTitle ?? w.np_scroll_title ?? true;" + eol_js +
    "    w.np_scroll_title = w.npScrollTitle;" + eol_js +
    "    w.npBgColor = w.npBgColor || w.np_bg_color || '#1a1a2e';" + eol_js +
    "    w.np_bg_color = w.npBgColor;" + eol_js +
    "    w.npBgOpacity = parseFloat(w.npBgOpacity ?? w.np_bg_opacity ?? 0.85);" + eol_js +
    "    w.np_bg_opacity = w.npBgOpacity;" + eol_js +
    "    w.npRadius = parseInt(w.npRadius ?? w.np_radius ?? 8, 10);" + eol_js +
    "    w.np_radius = w.npRadius;" + eol_js +
    "    w.npArtRadius = parseInt(w.npArtRadius ?? w.np_art_radius ?? 6, 10);" + eol_js +
    "    w.np_art_radius = w.npArtRadius;" + eol_js +
    "    w.npArtSize = parseInt(w.npArtSize ?? w.np_art_size ?? 48, 10);" + eol_js +
    "    w.np_art_size = w.npArtSize;" + eol_js +
    "    w.npAccentColor = w.npAccentColor || w.np_accent_color || '#1db954';" + eol_js +
    "    w.np_accent_color = w.npAccentColor;" + eol_js +
    "    w.npTextColor = w.npTextColor || w.np_text_color || '#ffffff';" + eol_js +
    "    w.np_text_color = w.npTextColor;" + eol_js +
    "    w.npFontSize = parseInt(w.npFontSize ?? w.np_font_size ?? 14, 10);" + eol_js +
    "    w.np_font_size = w.npFontSize;" + eol_js +
    "    w.npArtistFontSize = parseInt(w.npArtistFontSize ?? w.np_artist_font_size ?? 12, 10);" + eol_js +
    "    w.np_artist_font_size = w.npArtistFontSize;" + eol_js +
    "    w.npTimeFontSize = parseInt(w.npTimeFontSize ?? w.np_time_font_size ?? 10, 10);" + eol_js +
    "    w.np_time_font_size = w.npTimeFontSize;" + eol_js +
    eol_js +
    "    // Webcam Widget" + eol_js +
    "    w.webcamRatio = w.webcamRatio || w.webcam_ratio || '16:9';" + eol_js +
    "    w.webcam_ratio = w.webcamRatio;" + eol_js +
    "    w.webcamTheme = w.webcamTheme || w.webcam_theme || 'border';" + eol_js +
    "    w.webcam_theme = w.webcamTheme;" + eol_js +
    "    w.borderWidth = parseInt(w.borderWidth ?? w.webcam_border_width ?? 3, 10);" + eol_js +
    "    w.webcam_border_width = w.borderWidth;" + eol_js +
    "    w.borderColor = w.borderColor || w.webcam_border_color || '#6366f1';" + eol_js +
    "    w.webcam_border_color = w.borderColor;" + eol_js +
    eol_js +
    "    // Clock Widget" + eol_js +
    "    w.clockTheme = w.clockTheme || w.clock_theme || 'default';" + eol_js +
    "    w.clock_theme = w.clockTheme;" + eol_js +
    "    w.clockStyle = w.clockStyle || w.clock_style || 'none';" + eol_js +
    "    w.clock_style = w.clockStyle;" + eol_js +
    "    w.clockFormat = w.clockFormat || w.clock_format || 'HH:MM';" + eol_js +
    "    w.clock_format = w.clockFormat;" + eol_js +
    eol_js +
    "    // Media & Browser Source" + eol_js +
    "    w.imageUrl = w.imageUrl || w.image_url || '';" + eol_js +
    "    w.image_url = w.imageUrl;" + eol_js +
    "    w.videoUrl = w.videoUrl || w.video_url || '';" + eol_js +
    "    w.video_url = w.videoUrl;" + eol_js +
    "    w.fitMode = w.fitMode || w.fit_mode || 'cover';" + eol_js +
    "    w.fit_mode = w.fitMode;" + eol_js +
    "    w.url = w.url || '';" + eol_js +
    eol_js +
    "    return w;" + eol_js +
    "  }" + eol_js +
    eol_js
)

old_load_saved = (
    "  // Load saved state from localStorage" + eol_js +
    "  function loadSavedState() {" + eol_js +
    "    try {" + eol_js +
    "      const saved = localStorage.getItem(STORAGE_KEY);" + eol_js +
    "      if (saved) {" + eol_js +
    "        const parsed = JSON.parse(saved);" + eol_js +
    "        if (Array.isArray(parsed) && parsed.length > 0) {" + eol_js +
    "          state.pages = parsed;" + eol_js +
    "          state.activePageId = parsed[0].id;" + eol_js +
    "        }" + eol_js +
    "      }" + eol_js +
    "    } catch (e) {" + eol_js +
    "      console.warn('Failed to load composer state from localStorage:', e);" + eol_js +
    "    }" + eol_js +
    "  }"
)

new_load_saved = (
    normalizer_code +
    "  // Load saved state from localStorage (with full V2 fallback & migration)" + eol_js +
    "  function loadSavedState() {" + eol_js +
    "    try {" + eol_js +
    "      let saved = localStorage.getItem(STORAGE_KEY);" + eol_js +
    "      if (!saved) {" + eol_js +
    "        saved = localStorage.getItem('composer_pages') || localStorage.getItem('composer_layout');" + eol_js +
    "      }" + eol_js +
    "      if (saved) {" + eol_js +
    "        const parsed = JSON.parse(saved);" + eol_js +
    "        if (Array.isArray(parsed) && parsed.length > 0) {" + eol_js +
    "          if (parsed[0].widgets) {" + eol_js +
    "            state.pages = parsed.map(p => {" + eol_js +
    "              p.widgets = (p.widgets || []).map(normalizeWidget);" + eol_js +
    "              return p;" + eol_js +
    "            });" + eol_js +
    "            state.activePageId = state.pages[0].id;" + eol_js +
    "          } else {" + eol_js +
    "            state.pages = [{" + eol_js +
    "              id: 'page-1'," + eol_js +
    "              name: 'หน้า 1'," + eol_js +
    "              widgets: parsed.map(normalizeWidget)" + eol_js +
    "            }];" + eol_js +
    "            state.activePageId = 'page-1';" + eol_js +
    "          }" + eol_js +
    "        }" + eol_js +
    "      }" + eol_js +
    "    } catch (e) {" + eol_js +
    "      console.warn('Failed to load composer state:', e);" + eol_js +
    "    }" + eol_js +
    "  }"
)

assert old_load_saved in js, "old_load_saved not found"
js = js.replace(old_load_saved, new_load_saved, 1)

# Add exportProfile, importProfile, togglePreviewMode functions before setupToolbarEvents
toolbar_helpers = (
    "  // Export Profile (JSON download)" + eol_js +
    "  function exportProfile() {" + eol_js +
    "    try {" + eol_js +
    "      const data = {" + eol_js +
    "        version: '3.0.0'," + eol_js +
    "        exportedAt: new Date().toISOString()," + eol_js +
    "        pages: state.pages," + eol_js +
    "        activePageId: state.activePageId" + eol_js +
    "      };" + eol_js +
    "      const jsonStr = JSON.stringify(data, null, 2);" + eol_js +
    "      const blob = new Blob([jsonStr], { type: 'application/json' });" + eol_js +
    "      const url = URL.createObjectURL(blob);" + eol_js +
    "      const a = document.createElement('a');" + eol_js +
    "      a.href = url;" + eol_js +
    "      a.download = `broadcast_playroom_profile_${Date.now()}.json`;" + eol_js +
    "      document.body.appendChild(a);" + eol_js +
    "      a.click();" + eol_js +
    "      document.body.removeChild(a);" + eol_js +
    "      URL.revokeObjectURL(url);" + eol_js +
    "      if (window.showToast) window.showToast('ส่งออกไฟล์ Profile สำเร็จ');" + eol_js +
    "    } catch (e) {" + eol_js +
    "      alert('ส่งออกไม่สำเร็จ: ' + e);" + eol_js +
    "    }" + eol_js +
    "  }" + eol_js +
    eol_js +
    "  // Import Profile (Parse JSON & Auto-Migrate)" + eol_js +
    "  function importProfile(jsonStr) {" + eol_js +
    "    try {" + eol_js +
    "      const parsed = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;" + eol_js +
    "      if (parsed) {" + eol_js +
    "        if (Array.isArray(parsed)) {" + eol_js +
    "          if (parsed[0] && parsed[0].widgets) {" + eol_js +
    "            state.pages = parsed.map(p => {" + eol_js +
    "              p.widgets = (p.widgets || []).map(normalizeWidget);" + eol_js +
    "              return p;" + eol_js +
    "            });" + eol_js +
    "          } else {" + eol_js +
    "            state.pages = [{" + eol_js +
    "              id: 'page-1'," + eol_js +
    "              name: 'หน้า 1'," + eol_js +
    "              widgets: parsed.map(normalizeWidget)" + eol_js +
    "            }];" + eol_js +
    "          }" + eol_js +
    "        } else if (parsed.pages && Array.isArray(parsed.pages)) {" + eol_js +
    "          state.pages = parsed.pages.map(p => {" + eol_js +
    "            p.widgets = (p.widgets || []).map(normalizeWidget);" + eol_js +
    "            return p;" + eol_js +
    "          });" + eol_js +
    "        } else if (parsed.widgets && Array.isArray(parsed.widgets)) {" + eol_js +
    "          state.pages = [{" + eol_js +
    "            id: 'page-1'," + eol_js +
    "            name: 'หน้า 1'," + eol_js +
    "            widgets: parsed.widgets.map(normalizeWidget)" + eol_js +
    "          }];" + eol_js +
    "        }" + eol_js +
    "        state.activePageId = state.pages[0].id;" + eol_js +
    "        renderPageTabs();" + eol_js +
    "        renderCanvasWidgets();" + eol_js +
    "        renderLayersList();" + eol_js +
    "        saveState();" + eol_js +
    "        if (window.showToast) window.showToast('นำเข้าและ Migrate เลย์เอาต์เรียบร้อยแล้ว');" + eol_js +
    "      }" + eol_js +
    "    } catch (e) {" + eol_js +
    "      alert('นำเข้าไฟล์ไม่สำเร็จ: ' + e);" + eol_js +
    "    }" + eol_js +
    "  }" + eol_js +
    eol_js +
    "  // Toggle Clean Preview Mode" + eol_js +
    "  function togglePreviewMode() {" + eol_js +
    "    const modal = document.getElementById('composerStudioModal');" + eol_js +
    "    if (!modal) return;" + eol_js +
    "    const isPreview = modal.classList.toggle('preview-clean-mode');" + eol_js +
    "    const btn = document.getElementById('btnCompPreview');" + eol_js +
    "    if (btn) {" + eol_js +
    "      btn.innerHTML = isPreview ? '✏️ แก้ไข' : '👁️ พรีวิว';" + eol_js +
    "      btn.classList.toggle('active', isPreview);" + eol_js +
    "    }" + eol_js +
    "    if (window.showToast) {" + eol_js +
    "      window.showToast(isPreview ? 'เข้าสู่โหมดพรีวิว (ซ่อนเครื่องมือทั้งหมด)' : 'กลับสู่โหมดแก้ไข');" + eol_js +
    "    }" + eol_js +
    "  }" + eol_js +
    eol_js
)

anchor_toolbar = "  // Setup Toolbar Events"
assert anchor_toolbar in js, "anchor_toolbar not found"
js = js.replace(anchor_toolbar, toolbar_helpers + anchor_toolbar, 1)

# Bind new buttons in setupToolbarEvents
old_tb_events = (
    "    // Save Button" + eol_js +
    "    document.getElementById('btnCompSave')?.addEventListener('click', saveState);" + eol_js +
    eol_js +
    "    // Copy OBS URL Button" + eol_js +
    "    document.getElementById('btnCompCopyObs')?.addEventListener('click', copyComposerObsUrl);"
)

new_tb_events = (
    "    // Preview Mode Button" + eol_js +
    "    document.getElementById('btnCompPreview')?.addEventListener('click', togglePreviewMode);" + eol_js +
    eol_js +
    "    // Export Profile Button" + eol_js +
    "    document.getElementById('btnCompExport')?.addEventListener('click', exportProfile);" + eol_js +
    eol_js +
    "    // Import Profile Button & File Input" + eol_js +
    "    const btnImport = document.getElementById('btnCompImport');" + eol_js +
    "    const fileInput = document.getElementById('fileCompImportProfile');" + eol_js +
    "    if (btnImport && fileInput) {" + eol_js +
    "      btnImport.addEventListener('click', () => fileInput.click());" + eol_js +
    "      fileInput.addEventListener('change', (e) => {" + eol_js +
    "        const file = e.target.files?.[0];" + eol_js +
    "        if (!file) return;" + eol_js +
    "        const reader = new FileReader();" + eol_js +
    "        reader.onload = (evt) => {" + eol_js +
    "          importProfile(evt.target.result);" + eol_js +
    "          fileInput.value = '';" + eol_js +
    "        };" + eol_js +
    "        reader.readAsText(file);" + eol_js +
    "      });" + eol_js +
    "    }" + eol_js +
    eol_js +
    old_tb_events
)

assert old_tb_events in js, "old_tb_events not found"
js = js.replace(old_tb_events, new_tb_events, 1)

# Expose new helpers on window.ComposerStudio
old_expose = "    switchPage: switchPage"
new_expose = (
    "    switchPage: switchPage," + eol_js +
    "    exportProfile: exportProfile," + eol_js +
    "    importProfile: importProfile," + eol_js +
    "    togglePreviewMode: togglePreviewMode," + eol_js +
    "    normalizeWidget: normalizeWidget"
)
assert old_expose in js, "old_expose not found"
js = js.replace(old_expose, new_expose, 1)

with open(js_path, "w", encoding="utf-8", newline="") as f:
    f.write(js)
print("Updated composer_studio.js with Schema Normalizer, Export, Import, and Preview Mode!")
