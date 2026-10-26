import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/chat_twitch.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('CAP REQ')
print(c[idx-50:idx+400])
