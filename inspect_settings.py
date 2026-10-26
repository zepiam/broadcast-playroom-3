import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx_win = c.find('id="win-settings"')
idx_win_end = c.find('</aside>', idx_win)
if idx_win_end == -1:
    idx_win_end = c.find('</div>\n    </div>\n  </div>', idx_win)
win_html = c[idx_win:idx_win+15000]

import re
sections = re.findall(r'<div class="settings-section[^"]*" id="([^"]+)">', win_html)
print("Settings sections found:", sections)

# Find all buttons in settings
buttons = re.findall(r'<button[^>]*>.*?</button>', win_html, re.DOTALL)
print(f"Total buttons in win-settings: {len(buttons)}")
for b in buttons[:25]:
    clean_b = ' '.join(b.split())
    print(" -", clean_b[:120])
