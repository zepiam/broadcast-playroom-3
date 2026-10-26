import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

targets = ["if (w.type === 'randomizer')", "if (w.type === 'ask')", "if (w.type === 'giveaway')", "if (w.type === 'emote_party')", "if (w.type === 'playroom')"]
for i, l in enumerate(lines):
    for t in targets:
        if t in l:
            print(f'Line {i+1}: {l.strip()}')
            for j in range(i, min(i+30, len(lines))):
                print(f'   {j+1}: {lines[j].strip()[:100]}')
