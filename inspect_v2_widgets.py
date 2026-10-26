with open(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom dev\composer.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
labels = re.search(r'const WIDGET_LABELS\s*=\s*\{([^}]+)\}', text)
if labels:
    print("WIDGET_LABELS:\n", labels.group(0))

icons = re.search(r'const WIDGET_ICONS\s*=\s*\{([^}]+)\}', text)
if icons:
    print("WIDGET_ICONS:\n", icons.group(0))

types = set(re.findall(r'type\s*===\s*[\'"]([^\'"]+)[\'"]', text))
print("All types found:\n", sorted(list(types)))
