import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(16510, min(16550, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
