import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/chat_twitch.py', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = [m.start() for m in re.finditer(r'PRIVMSG', c)]
print('Matches indices:', matches)
for m in matches[2:]:
    print(c[m-50:m+200])
    print("=" * 40)
