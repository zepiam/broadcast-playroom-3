import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find("} else if (w.type === 'now_playing') {", 200000)
idx_end = text.find("} else if (w.type === 'ask') {", idx)
print("now_playing customizer block (len:", idx_end - idx, "):")
print(text[idx:idx+2000])
