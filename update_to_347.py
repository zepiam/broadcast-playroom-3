import os
import sys
import json
import re

BASE_DIR = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"

# 1. Update updater.py
updater_path = os.path.join(BASE_DIR, "updater.py")
with open(updater_path, "r", encoding="utf-8") as f:
    u = f.read()

# Update version to 3.47
u = re.sub(r'CURRENT_VERSION\s*=\s*["\']3\.4[0-9]["\']', 'CURRENT_VERSION = "3.47"', u)

# Add mirror URLs
target_raw = 'RAW_MANIFEST_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/version.json"'
replacement_manifests = '''# 1. Hugging Face CDN (ความเร็วสูง ไม่ติดบล็อกเน็ตในไทย)
HF_MANIFEST_URL = "https://huggingface.co/men9ch/broadcast-playroom-3/raw/main/version.json"
# 2. jsDelivr Fastly CDN
JSDELIVR_MANIFEST_URL = f"https://cdn.jsdelivr.net/gh/{REPO_OWNER}/{REPO_NAME}@master/version.json"
# 3. Static raw manifest จาก master branch
RAW_MANIFEST_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/version.json"'''

assert target_raw in u, "target_raw not found"
u = u.replace(target_raw, replacement_manifests)

# Update urls in fetch_remote_manifest
pattern_urls = r'urls\s*=\s*\[\s*RELEASE_MANIFEST_URL[\s\S]*?RAW_MANIFEST_URL[\s\S]*?\]'
replacement_urls = '''urls = [
            HF_MANIFEST_URL + f"?t={int(time.time())}",
            JSDELIVR_MANIFEST_URL + f"?t={int(time.time())}",
            RELEASE_MANIFEST_URL,
            RAW_MANIFEST_URL + f"?t={int(time.time())}",
            HF_MANIFEST_URL,
            RAW_MANIFEST_URL,
        ]'''

u, count_urls = re.subn(pattern_urls, replacement_urls, u)
print(f"Replaced urls in fetch_remote_manifest: {count_urls}")
assert count_urls > 0, "Could not replace urls in fetch_remote_manifest"

# Update worker download logic to try mirrors (Hugging Face)
pattern_dl = r'ok\s*=\s*download_update_file\(\s*download_url[\s\S]*?expected_sha256=expected_sha,?\s*\)'
replacement_dl = '''# Candidate URLs prioritizing Hugging Face for Thailand/Asia
            urls_to_try = []
            mirrors = info.get("mirrors") or []
            for m in mirrors:
                if "huggingface" in m and m not in urls_to_try:
                    urls_to_try.append(m)
            if download_url and download_url not in urls_to_try:
                urls_to_try.append(download_url)
            for m in mirrors:
                if m not in urls_to_try:
                    urls_to_try.append(m)

            ok = False
            for cand_url in urls_to_try:
                ok = download_update_file(
                    cand_url,
                    str(target_zip),
                    on_progress=_on_prog,
                    expected_sha256=expected_sha,
                )
                if ok:
                    download_url = cand_url
                    break'''

u, count_dl = re.subn(pattern_dl, replacement_dl, u)
print(f"Replaced download_update_file call: {count_dl}")
assert count_dl > 0, "Could not replace download_update_file call"

with open(updater_path, "w", encoding="utf-8") as f:
    f.write(u)
print("updater.py updated successfully!")

# 2. Update patch_installer.py fallbacks
pi_path = os.path.join(BASE_DIR, "patch_installer.py")
with open(pi_path, "r", encoding="utf-8") as f:
    pi = f.read()

pi = re.sub(r"'latest_version',\s*'3\.4[0-9]'", "'latest_version', '3.47'", pi)
pi = re.sub(r"else\s*'3\.4[0-9]'", "else '3.47'", pi)
pi = re.sub(r"BP3-PatchInstaller/3\.4[0-9]", "BP3-PatchInstaller/3.47", pi)

with open(pi_path, "w", encoding="utf-8") as f:
    f.write(pi)
print("patch_installer.py updated successfully!")

# 3. Update package.json
pkg_path = os.path.join(BASE_DIR, "package.json")
with open(pkg_path, "r", encoding="utf-8") as f:
    pkg = json.load(f)
pkg["version"] = "3.47"
with open(pkg_path, "w", encoding="utf-8") as f:
    json.dump(pkg, f, indent=2)
print("package.json updated successfully!")

# 4. Update src/index.html & dist/index.html
for html_rel in ["src/index.html", "dist/index.html"]:
    html_path = os.path.join(BASE_DIR, html_rel)
    if os.path.isfile(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            h = f.read()

        # Fix spelling "วาร์ชันล่าสุด" -> "เวอร์ชันล่าสุด"
        h = h.replace("วาร์ชันล่าสุด", "เวอร์ชันล่าสุด")
        h = h.replace("วาร์ชัน", "เวอร์ชัน")

        # Fix hardcoded v3.6 and titlebar version
        h = h.replace('>v3.6<', '>v3.47<')
        h = re.sub(r'<span class="desktop-titlebar-tag">v3\.4[0-9]</span>', '<span class="desktop-titlebar-tag">v3.47</span>', h)
        
        # In checkAppUpdate catch block, fix stuck badge
        h = re.sub(r'if \(detail\) detail\.textContent = [\'"]ไม่สามารถตรวจสอบการอัปเดตได้[\'"];',
                   'if (badge) {\n          badge.textContent = "❌ ตรวจสอบไม่สำเร็จ";\n          badge.style.color = "#ef4444";\n          badge.style.background = "rgba(239,68,68,0.12)";\n          badge.style.borderColor = "rgba(239,68,68,0.25)";\n        }\n        if (detail) detail.textContent = "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์อัปเดตได้ กรุณาลองใหม่อีกครั้ง";',
                   h)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(h)
        print(f"{html_rel} updated successfully!")
