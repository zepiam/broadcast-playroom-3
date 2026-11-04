import os
import re

BASE_DIR = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"

# 1. Update app_window_frame.py
awf_path = os.path.join(BASE_DIR, "app_window_frame.py")
with open(awf_path, "r", encoding="utf-8") as f:
    awf = f.read()

awf = awf.replace("'Broadcast Playroom 3'", "'Broadcast Playroom'")
awf = awf.replace('"Broadcast Playroom 3"', '"Broadcast Playroom"')

with open(awf_path, "w", encoding="utf-8") as f:
    f.write(awf)
print("app_window_frame.py updated successfully!")

# 2. Update launch_dev.py window title
ld_path = os.path.join(BASE_DIR, "launch_dev.py")
with open(ld_path, "r", encoding="utf-8") as f:
    ld = f.read()

ld = re.sub(r"title\s*=\s*['\"]Broadcast Playroom.*?['\"],", 'title=f"Broadcast Playroom v{CURRENT_VERSION}",', ld)

with open(ld_path, "w", encoding="utf-8") as f:
    f.write(ld)
print("launch_dev.py window title updated successfully!")

# 3. Update src/index.html & dist/index.html document title
for html_rel in ["src/index.html", "dist/index.html"]:
    html_path = os.path.join(BASE_DIR, html_rel)
    if os.path.isfile(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            h = f.read()

        h = re.sub(r"<title>Broadcast Playroom.*?</title>", "<title>Broadcast Playroom v3.48</title>", h)

        # In DOMContentLoaded version fetch, set document.title
        old_ver_fetch = "if(response.ok && info.version)document.querySelectorAll('.desktop-titlebar-tag, #appVersionBadge').forEach(node=>node.textContent='v'+info.version);"
        new_ver_fetch = "if(response.ok && info.version){document.title='Broadcast Playroom v'+info.version;document.querySelectorAll('.desktop-titlebar-tag, #appVersionBadge').forEach(node=>node.textContent='v'+info.version);}"
        if old_ver_fetch in h:
            h = h.replace(old_ver_fetch, new_ver_fetch)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(h)
        print(f"{html_rel} title updated successfully!")
