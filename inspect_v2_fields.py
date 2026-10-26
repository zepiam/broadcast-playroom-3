with open(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom dev\composer.html", "r", encoding="utf-8") as f:
    text = f.read()

types_to_check = ['clock', 'viewer', 'webcam', 'text', 'image', 'video', 'now_playing', 'emote_party', 'avatar', 'donate_goal']

for t in types_to_check:
    needle = f"w.type === '{t}'"
    idx = text.find(needle)
    if idx != -1:
        print(f"=== WIDGET TYPE: {t} ===")
        print(text[idx:idx+1500])
        print("="*50)
