import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('compNpTransparent')
idx_spec = text.rfind("} else if (w.type === 'now_playing') {", 0, idx)
print("specificHtml for now_playing starts at:", idx_spec)
print(text[idx_spec:idx_spec+800])
