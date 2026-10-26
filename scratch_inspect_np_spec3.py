import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('compNpTransparent')
idx_spec = text.rfind("specificHtml", 0, idx)
print("specificHtml before compNpTransparent:", idx_spec)
print(text[idx_spec-50:idx_spec+400])
