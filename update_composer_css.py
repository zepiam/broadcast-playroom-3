with open("src/composer_studio.css", "r", encoding="utf-8") as f:
    css = f.read()

def normalize(t):
    return t.replace("\r\n", "\n")

# Update right sidebar to 320px and overflow-x hidden
old_sb_right = """.composer-sidebar-right {
  width: 300px;
  background: #1e1f22;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}"""

new_sb_right = """.composer-sidebar-right {
  width: 320px;
  background: #1e1f22;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

.composer-layers-list {
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  gap: 4px;
  max-height: 240px;
  overflow-y: auto;
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
}

.composer-layer-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  background: #2b2d31;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.composer-props-body {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

.composer-props-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  width: 100%;
  box-sizing: border-box;
}

.composer-prop-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.composer-prop-col .composer-prop-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--dc-text-muted);
}

.composer-prop-col .composer-prop-input {
  width: 100%;
  height: 28px;
  background: #141517;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: #f2f3f5;
  padding: 2px 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  box-sizing: border-box;
}

.composer-prop-col .composer-prop-input:focus {
  outline: none;
  border-color: var(--dc-blurple);
}"""

left_panel_css = """

/* ────────────────────────────────────────────────────────
   LEFT CUSTOMIZATION DRAWER PANEL
   Slides in when widget is selected, collapsible
   ──────────────────────────────────────────────────────── */
.composer-sidebar-left {
  width: 440px;
  max-width: 50vw;
  background: #232428;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
  transition: width 0.22s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
  box-sizing: border-box;
  z-index: 25;
}

.composer-sidebar-left.collapsed {
  width: 0 !important;
  border-right: none;
  opacity: 0;
  pointer-events: none;
}

.composer-customizer-header {
  padding: 10px 14px;
  background: #1e1f22;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.composer-btn-collapse {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--dc-text-muted);
  border-radius: 5px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.composer-btn-collapse:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.composer-btn-expand-left {
  position: absolute;
  top: 14px;
  left: 14px;
  z-index: 30;
  padding: 6px 12px;
  background: #1e1f22;
  border: 1px solid var(--dc-blurple);
  color: #ffffff;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
  display: none;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.composer-btn-expand-left:hover {
  background: var(--dc-blurple);
  transform: translateY(-1px);
}

.composer-btn-expand-left.visible {
  display: inline-flex !important;
}

.composer-customizer-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-sizing: border-box;
}

.composer-customizer-body::-webkit-scrollbar {
  width: 6px;
}
.composer-customizer-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

/* Customizer Sections & Controls */
.comp-card-section {
  background: #2b2d31;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.comp-card-header {
  padding: 9px 12px;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.comp-card-title {
  font-size: 12.5px;
  font-weight: 700;
  color: #f2f3f5;
  display: flex;
  align-items: center;
  gap: 6px;
}

.comp-card-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comp-field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
}

.comp-field-label {
  color: #dbdee1;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Canvas widget enhancements */
.widget-type-clock {
  padding: 8px 16px;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  border-radius: 8px;
  box-sizing: border-box;
  background: rgba(18, 19, 22, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #38bdf8;
  font-size: 26px;
  letter-spacing: 1px;
}

.widget-type-clock.clock-theme-cyberpunk {
  color: #00ffcc;
  background: rgba(10, 15, 25, 0.9);
  border: 2px solid #00ffcc;
  box-shadow: 0 0 15px rgba(0, 255, 204, 0.4), inset 0 0 10px rgba(0, 255, 204, 0.2);
}

.widget-type-clock.clock-theme-neon {
  color: #f43f5e;
  border: 2px solid #f43f5e;
  box-shadow: 0 0 16px rgba(244, 63, 94, 0.5);
  background: rgba(20, 10, 15, 0.85);
}

.widget-type-clock.clock-theme-flip {
  color: #ffffff;
  background: #18181b;
  border: 1px solid #3f3f46;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.5);
  border-radius: 6px;
}

.widget-type-clock.clock-theme-minimal {
  background: transparent;
  border: none;
  box-shadow: none;
  color: #ffffff;
}

.widget-type-clock.clock-theme-digital {
  font-family: 'Courier New', monospace;
  color: #22c55e;
  background: #022c22;
  border: 1px solid #15803d;
}

/* Ticker text marquee */
.widget-text-ticker {
  overflow: hidden;
  white-space: nowrap;
  width: 100%;
}
.widget-text-ticker span {
  display: inline-block;
  padding-left: 100%;
  animation: comp-ticker-move 12s linear infinite;
}
@keyframes comp-ticker-move {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-100%, 0, 0); }
}

/* Viewer Count Widget */
.widget-type-viewer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(18, 19, 22, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #ffffff;
  font-weight: 700;
  font-size: 15px;
}

/* Video Widget */
.widget-type-video {
  align-items: center;
  justify-content: center;
  background: #090a0c;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 600;
}

/* Alert / Browser Widget */
.widget-type-alert {
  align-items: center;
  justify-content: center;
  background: rgba(20, 25, 40, 0.75);
  border: 2px dashed #38bdf8;
  border-radius: 8px;
  color: #38bdf8;
  font-size: 13px;
  font-weight: 600;
  padding: 10px;
  text-align: center;
}

/* Now Playing Widget */
.widget-type-now-playing {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: rgba(24, 24, 27, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
}

/* Emote Party Widget */
.widget-type-emote-party {
  align-items: center;
  justify-content: center;
  background: rgba(88, 101, 242, 0.1);
  border: 2px dashed var(--dc-blurple);
  border-radius: 8px;
  color: #f2f3f5;
  font-size: 13px;
  font-weight: 600;
}
"""

css_norm = normalize(css)

if normalize(old_sb_right) in css_norm:
    css_norm = css_norm.replace(normalize(old_sb_right), normalize(new_sb_right), 1)
    print("Replaced old_sb_right styles")
else:
    print("Could not find old_sb_right")

if ".composer-sidebar-left" not in css_norm:
    css_norm += left_panel_css
    print("Appended left customizer panel styles")
else:
    print("composer-sidebar-left already in css")

with open("src/composer_studio.css", "w", encoding="utf-8") as f:
    f.write(css_norm)

print("Updated src/composer_studio.css successfully!")
