# -*- coding: utf-8 -*-
"""
Generator script for updated composer_studio.css and composer_studio.js
"""
import os
import re

css_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.css'
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

# 1. Append or ensure essential CSS rules in composer_studio.css
css_additions = """
/* ── COMPOSER STUDIO ENHANCEMENTS: TICKER, WEBCAM & TRANSPARENT WIDGETS ── */

/* 1. Prevent native browser ghost dragging on images and media inside widgets */
.composer-widget img,
.composer-widget video,
.composer-widget svg,
.widget-character-img,
.composer-widget .widget-inner img {
  pointer-events: none !important;
  user-select: none !important;
  -webkit-user-drag: none !important;
  -webkit-touch-callout: none !important;
}

/* 2. Transparent widgets standby rules (Image, Video, Alert, Emote Party) */
.composer-widget.type-image,
.composer-widget.type-video,
.composer-widget.type-alert,
.composer-widget.type-emote_party,
.composer-widget.type-emote-party {
  background: transparent !important;
}

.composer-widget.type-image .composer-widget-inner,
.composer-widget.type-video .composer-widget-inner,
.composer-widget.type-alert .composer-widget-inner,
.composer-widget.type-emote_party .composer-widget-inner,
.composer-widget.type-emote-party .composer-widget-inner {
  background: transparent !important;
  border: none !important;
}

/* 3. Webcam Frame: completely transparent inside (no dark box, no obstruction in OBS) */
.composer-widget.type-webcam,
.composer-widget .widget-type-webcam,
.composer-widget .webcam-frame {
  background: transparent !important;
}
.composer-widget .widget-type-webcam {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}
.composer-widget .webcam-frame {
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
  box-sizing: border-box;
  pointer-events: none;
  border-width: var(--wc-border-width, 4px);
}

/* 4. Viewer Widget V2 & Rolling Number Ticker */
:is(.widget, .composer-widget).type-viewer :is(.widget-inner, .composer-widget-inner) {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent !important;
  border: none !important;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

:is(.widget, .composer-widget).viewer-align-left :is(.widget-inner, .composer-widget-inner) { justify-content: flex-start; }
:is(.widget, .composer-widget).viewer-align-center :is(.widget-inner, .composer-widget-inner) { justify-content: center; }
:is(.widget, .composer-widget).viewer-align-right :is(.widget-inner, .composer-widget-inner) { justify-content: flex-end; }
:is(.widget, .composer-widget).viewer-direction-horizontal :is(.widget-inner, .composer-widget-inner) { flex-direction: row; }
:is(.widget, .composer-widget).viewer-direction-vertical :is(.widget-inner, .composer-widget-inner) { flex-direction: column; }

:is(.widget, .composer-widget) .viewer-total {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
}
:is(.widget, .composer-widget) .viewer-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-variant-numeric: tabular-nums;
}

:is(.widget, .composer-widget) .vt-col {
  display: inline-block;
  position: relative;
  height: 1.15em;
  line-height: 1.15em;
  overflow: hidden;
  vertical-align: middle;
  min-width: 0.62em;
  text-align: center;
}
:is(.widget, .composer-widget) .vt-track {
  display: flex;
  flex-direction: column;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  will-change: transform;
}
:is(.widget, .composer-widget) .vt-track.animated {
  transition: transform 1200ms cubic-bezier(0.33, 1, 0.68, 1);
}
:is(.widget, .composer-widget) .vt-num {
  height: 1.15em;
  line-height: 1.15em;
  text-align: center;
  display: block;
  user-select: none;
}
:is(.widget, .composer-widget) .vt-char {
  display: inline-block;
  vertical-align: middle;
  line-height: 1.15em;
  min-width: 0.35em;
  text-align: center;
  opacity: 0.85;
}

/* 5. Text Marquee Animation Speed */
@keyframes compMarqueeRun {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}
.widget-text-ticker span {
  display: inline-block;
  white-space: nowrap;
  will-change: transform;
  animation: compMarqueeRun var(--marquee-duration, 15s) linear infinite;
}

/* 6. Gear button on widget badge */
.composer-widget-badge .btn-widget-gear {
  transition: transform 0.2s ease, opacity 0.2s ease;
  opacity: 0.8;
}
.composer-widget-badge .btn-widget-gear:hover {
  transform: rotate(45deg) scale(1.15);
  opacity: 1;
}
"""

if '/* ── COMPOSER STUDIO ENHANCEMENTS: TICKER, WEBCAM & TRANSPARENT WIDGETS ── */' not in css_content:
    css_content += "\n" + css_additions
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Updated composer_studio.css with animations, ticker, and transparent rules.")
else:
    print("composer_studio.css already contains enhancements.")
