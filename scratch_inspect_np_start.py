import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('bgOpacityPct')
start = text.rfind("} else if (w.type === 'now_playing') {", 0, idx)
print("now_playing specificHtml definition:")
print(text[start:start+800])
