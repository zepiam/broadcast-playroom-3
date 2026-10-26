import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('compNpTransparent')
section_start = text.rfind('<div class="comp-card-section">', 0, idx)
section_end = text.find('</div>\n        </div>', idx)
print(text[section_start:section_end+400])
