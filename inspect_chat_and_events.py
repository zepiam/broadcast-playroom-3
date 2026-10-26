import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('chat-header')
idx_end = c.find('</section>', idx)
print("=== CHAT HEADER ===")
print(c[idx-50:idx+1500])

idx_events = c.find('events-panel')
if idx_events == -1:
    idx_events = c.find('sidebar-events')
if idx_events == -1:
    idx_events = c.find('กิจกรรมสด')
print("=== EVENTS PANEL ===")
print(c[idx_events-100:idx_events+400])
