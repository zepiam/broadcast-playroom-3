import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom dev/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('ซิงค์คลังศัพท์ Replace อัตโนมัติ')
print(c[idx-50:idx+1500])
