import sys, re
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom dev/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

matches = [m.start() for m in re.finditer(r'คลัง', c)]
print('Matches for คลัง in app.py:', len(matches))
for m in matches[:15]:
    print(c[m-20:m+80].replace('\n', ' '))
