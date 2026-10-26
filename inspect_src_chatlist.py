import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('id="chatList"')
idx_end = c.find('class="chat-panel-input"', idx)
print("=== chatList block in src/index.html ===")
print("idx:", idx, "idx_end:", idx_end)
print(c[idx:idx+300])
print("...")
print(c[idx_end-150:idx_end+50])
