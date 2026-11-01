import json

# 1. Update updater.py
with open("updater.py", "r", encoding="utf-8") as f:
    up = f.read()
up = up.replace('CURRENT_VERSION = "3.6"', 'CURRENT_VERSION = "3.7"')
with open("updater.py", "w", encoding="utf-8") as f:
    f.write(up)
print("Updated updater.py to 3.7")

# 2. Update package.json
with open("package.json", "r", encoding="utf-8") as f:
    pkg = json.load(f)
pkg["version"] = "3.7"
with open("package.json", "w", encoding="utf-8") as f:
    json.dump(pkg, f, indent=2)
print("Updated package.json to 3.7")

# 3. Update src/index.html
with open("src/index.html", "r", encoding="utf-8") as f:
    html = f.read()
html = html.replace('<span class="desktop-titlebar-tag">v3.6</span>', '<span class="desktop-titlebar-tag">v3.7</span>')
with open("src/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Updated src/index.html to v3.7")
