css_rule = """
/* -----------------------------------------------------------
   STANDBY EVENT WIDGETS: ZERO STATIC CLUTTER (100% TRANSPARENT)
   ----------------------------------------------------------- */
.composer-widget.type-randomizer,
.composer-widget.type-ask,
.composer-widget.type-giveaway,
.composer-widget.type-playroom,
.composer-widget.type-emote_party {
  background: transparent !important;
  border: none !important;
}

body.overlay-mode .composer-widget.type-randomizer,
body.overlay-mode .composer-widget.type-ask,
body.overlay-mode .composer-widget.type-giveaway,
body.overlay-mode .composer-widget.type-playroom,
body.preview-clean-mode .composer-widget.type-randomizer,
body.preview-clean-mode .composer-widget.type-ask,
body.preview-clean-mode .composer-widget.type-giveaway,
body.preview-clean-mode .composer-widget.type-playroom {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
"""

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.css', 'a', encoding='utf-8') as f:
    f.write(css_rule)

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer_studio.css', 'a', encoding='utf-8') as f:
    f.write(css_rule)

print("Appended standby transparency CSS rules!")
