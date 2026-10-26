import os

for root, dirs, files in os.walk('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src'):
    for file in files:
        if file.endswith(('.js', '.html')):
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f, 1):
                    if 'speakTextViaWebSpeech' in line:
                        print(f"{file}:{idx}: {line.strip()[:100]}")
