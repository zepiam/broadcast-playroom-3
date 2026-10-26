import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(15870, 16370):
    l = lines[i]
    if any(k in l for k in ['function startAskPoll', 'function togglePauseAsk', 'function endAskPoll', 'function closeAskOverlay', 'function resetAskPoll', 'function updateAskTimer', 'function updateAskUIState']):
        print(f'{i+1}: {l.strip()}')
