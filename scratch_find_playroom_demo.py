import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="win-playroom"')
end = text.find('id="win-composer"')
playroom_html = text[start:end]

for line in playroom_html.split('\n'):
    if 'สุ่ม' in line or 'demo' in line.lower() or 'เดโม' in line:
        print(line.strip())
