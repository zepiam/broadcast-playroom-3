with open(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="win-composer"' in l:
        print(f'Start win-composer: line {i+1}')
    if 'btnExpandCustPanel' in l:
        print(f'btnExpandCustPanel: line {i+1}')
    if '<!-- 12.' in l or '<!-- 11.' in l:
        print(f'{l.strip()}: line {i+1}')
