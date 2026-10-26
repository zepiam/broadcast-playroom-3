import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('runPlayroomSimulatedChat')
print("runPlayroomSimulatedChat occurrences:")
while idx != -1:
    print(text[idx-100:idx+300])
    print('='*50)
    idx = text.find('runPlayroomSimulatedChat', idx+1)
