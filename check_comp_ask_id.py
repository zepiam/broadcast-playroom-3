with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1785, 1830):
    if 'compAsk' in lines[i] or 'ask-panel' in lines[i]:
        print(f'{i+1}: {lines[i].strip()}')
