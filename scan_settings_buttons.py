import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('id="win-settings"')
idx_end = c.find('id="win-', idx + 20)
win_html = c[idx:idx_end]

import re
btns = re.findall(r'<button[^>]*>(.*?)</button>', win_html, re.DOTALL)
print(f"Total buttons in win-settings: {len(btns)}")
for i, b in enumerate(btns):
    clean = re.sub(r'<[^>]+>', '', b).strip()
    clean = ' '.join(clean.split())
    if clean:
        print(f"  [{i+1}] {clean}")
