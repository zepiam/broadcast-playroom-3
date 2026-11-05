import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")
index_path = ROOT / "src" / "index.html"
index_code = index_path.read_text(encoding="utf-8")

# Find the download button in updateCheckDetail
target_snippet = """<div style="display:flex; gap:8px;">"""
idx = index_code.find("data.download_url")
print("data.download_url at:", idx)

if idx != -1:
    # Find surrounding <div style="display:flex; gap:8px;"> ... </div>
    start_div = index_code.rfind('<div style="display:flex; gap:8px;">', 0, idx)
    end_div = index_code.find('</div>', idx) + 6
    print("Found block:")
    print(index_code[start_div:end_div])

    replacement_block = """<div style="display:flex; gap:8px; flex-wrap:wrap;">
                  <button class="btn btn-primary btn-sm" onclick="showFastUpdateModal()" style="font-size:12px; padding:7px 16px; background:#23a55a; border-color:#23a55a; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:5px;">
                    ⚡ อัปเดตในโปรแกรมทันที
                  </button>
                  <button class="btn btn-secondary btn-sm" onclick="openExternalUrl('https://github.com/zepiam/broadcast-playroom-3/releases')" style="font-size:12px; padding:7px 14px; cursor:pointer;">
                    🌐 ดูบันทึกการอัปเดต (Changelog)
                  </button>
                </div>"""

    index_code = index_code[:start_div] + replacement_block + index_code[end_div:]
    print("[OK] Replaced update button with in-app updater!")

# Also ensure auto-opening modal on manual check
manual_idx = index_code.find("if (manual) {")
print("manual_idx at:", manual_idx)
if manual_idx != -1:
    chunk = index_code[manual_idx:manual_idx+200]
    print("manual chunk:", repr(chunk))
    if "showFastUpdateModal();" not in chunk:
        index_code = index_code.replace(
            "if (manual) {",
            "if (manual) {\n            showFastUpdateModal();",
            1
        )
        print("[OK] Added showFastUpdateModal() on manual update check!")

index_path.write_text(index_code, encoding="utf-8")
print("[OK] File written successfully.")
