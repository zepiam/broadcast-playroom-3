import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

# 1. Update index.html
index_path = ROOT / "src" / "index.html"
index_html = index_path.read_text(encoding="utf-8")

# Bump version
index_html = index_html.replace("<title>Broadcast Playroom v3.56</title>", "<title>Broadcast Playroom v3.57</title>")
index_html = index_html.replace('<span class="desktop-titlebar-tag">v3.56</span>', '<span class="desktop-titlebar-tag">v3.57</span>')
index_html = index_html.replace('>v3.56</span>', '>v3.57</span>')

# Remove topbar-item-overlay button completely
# Match <button ... id="topbar-item-overlay" ... </button>
pattern_btn = re.compile(r'\s*<!-- 2\. Overlay [^\n]*-->\s*<button[^>]*id="topbar-item-overlay"[^>]*>.*?</button>', re.DOTALL)
m = pattern_btn.search(index_html)
if m:
    print(f"Found overlay button: {m.group(0)[:60]}...")
    index_html = pattern_btn.sub("", index_html)
    print("Removed overlay button from topbar HTML.")
else:
    print("[WARN] Could not find topbar-item-overlay button with pattern!")

# Remove 'overlay' entry from _topbarHideableMeta
pattern_meta = re.compile(r"\s*'overlay':\s*\{[^}]*actions:\s*\[[^\]]*\]\s*\},?", re.DOTALL)
m_meta = pattern_meta.search(index_html)
if m_meta:
    print(f"Found overlay in _topbarHideableMeta: {m_meta.group(0)[:60]}...")
    index_html = pattern_meta.sub("", index_html)
    print("Removed overlay from _topbarHideableMeta.")
else:
    print("[WARN] Could not find overlay in _topbarHideableMeta!")

index_path.write_text(index_html, encoding="utf-8")
print("[OK] src/index.html updated successfully.")

# 2. Update styles.css
styles_path = ROOT / "src" / "styles.css"
styles_css = styles_path.read_text(encoding="utf-8")
if "#topbar-item-overlay" not in styles_css:
    styles_css += "\n#topbar-item-overlay { display: none !important; }\n"
    styles_path.write_text(styles_css, encoding="utf-8")
    print("[OK] src/styles.css updated with display: none for #topbar-item-overlay.")

# 3. Update package.json
pkg_path = ROOT / "package.json"
pkg_json = pkg_path.read_text(encoding="utf-8")
pkg_json = pkg_json.replace('"version": "3.56"', '"version": "3.57"')
pkg_path.write_text(pkg_json, encoding="utf-8")
print("[OK] package.json updated to 3.57.")

# 4. Update updater.py
updater_path = ROOT / "updater.py"
updater_py = updater_path.read_text(encoding="utf-8")
updater_py = re.sub(r'CURRENT_VERSION\s*=\s*"[^"]+"', 'CURRENT_VERSION = "3.57"', updater_py)
updater_path.write_text(updater_py, encoding="utf-8")
print("[OK] updater.py CURRENT_VERSION updated to 3.57.")
