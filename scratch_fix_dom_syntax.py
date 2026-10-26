import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("window.addEventListener('DOMContentLoaded', () =>emitAskState();\n       {", "window.addEventListener('DOMContentLoaded', () => {\n      emitAskState();")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed syntax error in DOMContentLoaded.")
