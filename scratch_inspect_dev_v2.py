import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'E:/DOCS/Documents/AI TOOLS/broadcast playroom dev/now_playing.py', 'r', encoding='utf-8') as f:
    text = f.read()

print(text[3500:])
