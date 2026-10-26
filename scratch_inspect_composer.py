import sys
sys.stdout.reconfigure(encoding='utf-8')

html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="win-composer"')
if start == -1:
    start = text.find('win-composer')
end = text.find('composer-main-split', start)
print("=== WIN-COMPOSER HEADER & TOPBAR ===")
print(text[start:end])
