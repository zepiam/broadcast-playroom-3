import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('bgOpacityPct')
while idx != -1:
    print('Found bgOpacityPct at:', idx)
    print(text[idx-100:idx+200])
    print('='*50)
    idx = text.find('bgOpacityPct', idx+1)
