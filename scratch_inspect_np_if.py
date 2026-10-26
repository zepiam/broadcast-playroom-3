import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('bgOpacityPct')
start = text.rfind("if (w.type === 'now_playing')", 0, idx)
if start == -1:
    start = text.rfind("w.type === 'now_playing'", 0, idx)
print("Start at:", start)
print(text[start:start+800])
