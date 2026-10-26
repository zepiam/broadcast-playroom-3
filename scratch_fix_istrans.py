import sys
sys.stdout.reconfigure(encoding='utf-8')
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("${isTrans ? 'checked' : ''}", "${w.npTransparent ? 'checked' : ''}")
text = text.replace("${isTrans ? 'none' : 'flex'}", "${w.npTransparent ? 'none' : 'flex'}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced isTrans with w.npTransparent.")
