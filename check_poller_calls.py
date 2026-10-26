with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'initRealChatPoller' in line:
            print(f"{idx}: {line.strip()[:100]}")
