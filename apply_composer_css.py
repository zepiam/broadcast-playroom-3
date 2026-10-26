with open(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.css', 'r', encoding='utf-8') as f:
    css = f.read()

new_css_rules = """
/* ==============================================================================
   RESTRUCTURED COMPOSER STUDIO 3-ROW TOOLBAR & SLEEK LAYER CONTROLS
   ============================================================================== */

/* Row 2: Page & Canvas Controls */
.composer-subbar-pages {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 14px;
  background: #1e1f22;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
  box-sizing: border-box;
}

.composer-btn-sub {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 9px;
  font-size: 11.5px;
  font-weight: 600;
  color: #c4c9ce;
  background: #2b2d31;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.composer-btn-sub:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}
.composer-btn-sub.active {
  background: rgba(56, 189, 248, 0.2);
  border-color: #38bdf8;
  color: #38bdf8;
}

/* Row 3: Widget List Bar */
.composer-subbar-widgets {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #141517;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
  overflow-x: auto;
  scrollbar-width: thin;
  box-sizing: border-box;
}
.composer-subbar-widgets::-webkit-scrollbar {
  height: 4px;
}
.composer-subbar-widgets::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.18);
  border-radius: 2px;
}

/* Sleek Layer Actions & Drag Handle */
.composer-layer-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: grab;
  padding: 2px 4px;
  margin-right: 2px;
  transition: color 0.15s ease;
  flex-shrink: 0;
}
.composer-layer-handle:hover {
  color: #38bdf8;
}
.composer-layer-handle:active {
  cursor: grabbing;
}

.composer-btn-layer-action {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  color: #94a3b8;
  padding: 0;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}
.composer-btn-layer-action:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.25);
}
.composer-btn-layer-action.is-hidden {
  color: #ef4444 !important;
  background: rgba(239, 68, 68, 0.15) !important;
  border-color: rgba(239, 68, 68, 0.35) !important;
}
.composer-btn-layer-action.is-locked {
  color: #f59e0b !important;
  background: rgba(245, 158, 11, 0.15) !important;
  border-color: rgba(245, 158, 11, 0.35) !important;
}
.composer-btn-layer-action.close-red:hover {
  background: rgba(239, 68, 68, 0.25) !important;
  border-color: #ef4444 !important;
  color: #ef4444 !important;
}

/* Layer Drag and Drop Reordering */
.composer-layer-item {
  transition: transform 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
}
.composer-layer-item.dragging {
  opacity: 0.35 !important;
  transform: scale(0.98);
  border: 1px dashed #6366f1 !important;
  background: rgba(99, 102, 241, 0.12) !important;
}
.composer-layer-item.drag-over-top {
  border-top: 2px solid #38bdf8 !important;
  box-shadow: 0 -3px 8px rgba(56, 189, 248, 0.4);
  transform: translateY(2px);
}
.composer-layer-item.drag-over-bottom {
  border-bottom: 2px solid #38bdf8 !important;
  box-shadow: 0 3px 8px rgba(56, 189, 248, 0.4);
  transform: translateY(-2px);
}
"""

if "RESTRUCTURED COMPOSER STUDIO 3-ROW TOOLBAR" not in css:
    css += new_css_rules
    with open(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added new CSS rules to composer_studio.css")
else:
    print("CSS rules already present")
