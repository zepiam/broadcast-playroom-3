import sys
sys.stdout.reconfigure(encoding='utf-8')
with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if '_currentVoiceGender' in line or 'selectVoiceGender' in line:
            print(f"{idx}: {line.strip()[:100]}")
