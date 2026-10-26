import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('<header')
idx_end = c.find('</header>')
if idx != -1 and idx_end != -1:
    print("=== TOPBAR HEADER ===")
    print(c[idx:idx_end+9])
