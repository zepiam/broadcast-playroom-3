with open(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom dev\composer.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("function _openSettingsModalInner")
end_idx = text.find("function closeSettingsModal", idx)
if end_idx == -1: end_idx = idx + 25000

print(f"Modal code length: {end_idx - idx}")

# Let's inspect sections in modal
import re
sections = re.findall(r'if\s*\(\s*w\.type\s*===\s*[\'"]([^\'"]+)[\'"]', text[idx:end_idx])
print("Widget types with specific settings:", sections)
