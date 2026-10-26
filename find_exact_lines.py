import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'Forward all global helper functions' in l:
        print(f"Match 1 at line {i+1}:")
        for j in range(i, min(i+25, len(lines))):
            print(f"  {repr(lines[j])}")
        break

for i, l in enumerate(lines):
    if 'REAL ASK POLL SYSTEM' in l:
        print(f"\nMatch 2 at line {i+1}:")
        for j in range(i, min(i+15, len(lines))):
            print(f"  {repr(lines[j])}")
        break
