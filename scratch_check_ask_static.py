import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('<!-- Live Preview Bar Graph -->')
idx_end = text.find('<!-- TAB 2: หน้าตา Overlay', idx)
print("Static preview block in ASK:")
print(text[idx:idx_end])
