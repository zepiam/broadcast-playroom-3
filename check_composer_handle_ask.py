import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'function handleAskUpdate' in l:
        for j in range(i, min(i+40, len(lines))):
            print(f'{j+1}: {lines[j]}', end='')
        break
