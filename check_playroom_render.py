import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "if (w.type === 'playroom')" in l:
        print(f"Playroom found at line {i+1}")
        for j in range(i, min(i+25, len(lines))):
            print(f"{j+1}: {repr(lines[j])}")
        break
