import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="win-ask"')
idx2 = text.find('ตัวอย่างแท่งคะแนนโหวตสด', idx)
print(text[idx2-50:idx2+1500])
