import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function popoutToolWindow(')
idx_end = text.find('function dockToolWindow(', idx)
print("popoutToolWindow implementation:")
print(text[idx:idx_end])
