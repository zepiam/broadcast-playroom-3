import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('compNpTransparent')
spec_start = text.rfind("specificHtml = `", 0, idx)
print(text[spec_start-50:spec_start+400])
