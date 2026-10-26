import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('DOMContentLoaded')
while idx != -1:
    print('Found DOMContentLoaded at:', idx)
    print(text[idx-50:idx+200])
    print('='*50)
    idx = text.find('DOMContentLoaded', idx+1)
