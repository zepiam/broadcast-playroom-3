import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('id="chatList"')
print(c[idx:idx+2500])
