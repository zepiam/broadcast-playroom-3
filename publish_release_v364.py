import os
import sys
import shutil
import hashlib
import json
import subprocess
import time
import zipfile
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")
DIST_RELEASES = ROOT / "dist_releases"
DIST_RELEASES.mkdir(parents=True, exist_ok=True)
PATCHES_DIR = ROOT / "patches"
PATCHES_DIR.mkdir(parents=True, exist_ok=True)

try:
    from huggingface_hub import HfApi, get_token
except ImportError:
    print("[ERROR] huggingface_hub not installed")
    sys.exit(1)

HF_REPO_ID = "men9ch/broadcast-playroom-3"
hf_token = get_token()
if not hf_token:
    token_path = Path.home() / ".cache" / "huggingface" / "token"
    if token_path.exists():
        hf_token = token_path.read_text().strip()

if not hf_token:
    print("[ERROR] No Hugging Face token found")
    sys.exit(1)

api = HfApi(token=hf_token)

VERSION = "3.64"

print(f"=== [STEP 1] Rebuilding Frontend Distribution for v{VERSION} ===")
subprocess.run(["npm.cmd", "run", "build"], cwd=ROOT, check=True)

bp3_pi_src = ROOT / "dist" / "BP3_PatchInstaller.exe"
if bp3_pi_src.exists():
    shutil.copy2(bp3_pi_src, ROOT / "BP3_PatchInstaller.exe")
    print("  [OK] Copied BP3_PatchInstaller.exe to root")

CORE_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_tiktok.py', 'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'language_detect.py', 'network_dns.py', 'translator.py', 'dictionary_manager.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat',
    'avatar_cache_service.py', 'plugin_manager.py', 'app_window_frame.py', 'defender_helper.py',
    'app_presence.py', 'BP3_PatchInstaller.exe', 'version.json', 'package.json'
]

EXTRA_FOLDERS = [
    ('docs', 'docs'),
    ('plugins', 'plugins')
]

dist_src = ROOT / 'dist'
patch_lite = PATCHES_DIR / f'patch-v{VERSION}-lite.zip'
patch_full = PATCHES_DIR / f'patch-v{VERSION}-full.zip'

changelog = f"""# Broadcast Playroom v{VERSION}

### การเปลี่ยนแปลงในเวอร์ชัน {VERSION}:
- **แก้หน้า ตั้งค่า > เสียง TTS ค่าไม่เซฟ**: ระดับเสียง ความเร็ว (และพิตช์ในรุ่น Full) สวิตช์สุ่มเพศเสียง จำกัดตัวอักษร สวิตช์/ระดับเสียงแจ้งเตือนเมื่อเกินลิมิต และข้อความทดสอบ จะจำค่าที่ปรับไว้หลังปิด/เปิดหน้าตั้งค่าหรือเปิดโปรแกรมใหม่ (เดิมบันทึกแล้วแต่ไม่เคยอ่านกลับมา) และหน้าต่างหลักรับค่าที่เปลี่ยนจากหน้าตั้งค่าแบบ popout ด้วย
"""

print(f"\n=== [STEP 2] Packaging {patch_lite.name} & {patch_full.name} ===")

# Build Lite patch
with zipfile.ZipFile(patch_lite, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in CORE_FILES:
        fp = ROOT / f
        if fp.exists():
            z.write(fp, f)
            print(f"  [Lite] + {f}")

    for root, _, files in os.walk(dist_src):
        for file in files:
            full = Path(root) / file
            rel = full.relative_to(ROOT)
            z.write(full, str(rel).replace('\\', '/'))

    for src_dir, arc_dir in EXTRA_FOLDERS:
        sp = ROOT / src_dir
        if sp.exists():
            for root, _, files in os.walk(sp):
                for file in files:
                    full = Path(root) / file
                    rel = full.relative_to(ROOT)
                    z.write(full, str(rel).replace('\\', '/'))

print(f"  [Lite] Built {patch_lite.name} ({patch_lite.stat().st_size:,} bytes)")

# Build Full patch
shutil.copy2(patch_lite, patch_full)
print(f"  [Full] Built {patch_full.name} ({patch_full.stat().st_size:,} bytes)")

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

# Prepare manifest draft
manifest = {
    "version": VERSION,
    "latest_version": VERSION,
    "release_date": "2026-11-09",
    "mandatory": False,
    "changelog": changelog,
    "patches": {
        "lite": {
            "file": f"patch-v{VERSION}-lite.zip",
            "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-lite.zip",
            "sha256": "",
            "size": patch_lite.stat().st_size,
            "mirrors": [
                f"https://huggingface.co/{HF_REPO_ID}/resolve/main/patches/patch-v{VERSION}-lite.zip"
            ]
        },
        "full": {
            "file": f"patch-v{VERSION}-full.zip",
            "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-full.zip",
            "sha256": "",
            "size": patch_full.stat().st_size,
            "mirrors": [
                f"https://huggingface.co/{HF_REPO_ID}/resolve/main/patches/patch-v{VERSION}-full.zip"
            ]
        }
    },
    "lite": {
        "file": f"patch-v{VERSION}-lite.zip",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-lite.zip",
        "sha256": "",
        "size": patch_lite.stat().st_size
    },
    "full": {
        "file": f"patch-v{VERSION}-full.zip",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-full.zip",
        "sha256": "",
        "size": patch_full.stat().st_size
    }
}

manifest_file = ROOT / "version.json"
with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

# Write version.json into patches BEFORE final hashing
for pz in [patch_lite, patch_full]:
    with zipfile.ZipFile(pz, 'a', zipfile.ZIP_DEFLATED) as z:
        z.write(manifest_file, "version.json")

# RE-CALCULATE EXACT SHA256 & SIZE ON FINALIZED ZIP FILES
lite_final_sha = sha256_file(patch_lite)
full_final_sha = sha256_file(patch_full)
manifest["patches"]["lite"]["sha256"] = lite_final_sha
manifest["patches"]["lite"]["size"] = patch_lite.stat().st_size
manifest["patches"]["full"]["sha256"] = full_final_sha
manifest["patches"]["full"]["size"] = patch_full.stat().st_size
manifest["lite"]["sha256"] = lite_final_sha
manifest["lite"]["size"] = patch_lite.stat().st_size
manifest["full"]["sha256"] = full_final_sha
manifest["full"]["size"] = patch_full.stat().st_size

with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

# STRICT INTEGRITY GATE: Guarantee zero SHA256 mismatch before any upload
assert sha256_file(patch_lite) == manifest["patches"]["lite"]["sha256"], "LITE SHA256 GATE FAILED"
assert sha256_file(patch_full) == manifest["patches"]["full"]["sha256"], "FULL SHA256 GATE FAILED"
print("  [OK] Strict SHA256 gate passed! Hashes 100% matched finalized zips.")

print("\n=== [STEP 3] Uploading Patches and Manifest to Hugging Face ===")
upload_items = [
    (patch_lite, f"patches/patch-v{VERSION}-lite.zip"),
    (patch_full, f"patches/patch-v{VERSION}-full.zip"),
    (manifest_file, "version.json"),
]

for local_p, repo_p in upload_items:
    if local_p.exists():
        print(f"Uploading {local_p.name} -> {repo_p}...")
        api.upload_file(
            path_or_fileobj=str(local_p),
            path_in_repo=repo_p,
            repo_id=HF_REPO_ID,
            repo_type="model"
        )
        print(f"  [OK] Uploaded {local_p.name} successfully!")

print("\n=== [STEP 4] Git Commit & Tag v" + VERSION + " ===")
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
subprocess.run(["git", "reset", "-q", "--", "composer_layout.json"], cwd=ROOT, check=False)  # keep user layout out of the release commit
print("  [OK] composer_layout.json excluded from release commit")
subprocess.run(["git", "commit", "-m", f"release: Broadcast Playroom v{VERSION} (persist TTS settings: volume, speed, pitch, limit, test message)"], cwd=ROOT, check=True)
subprocess.run(["git", "tag", "-a", f"v{VERSION}", "-m", f"Release v{VERSION}"], cwd=ROOT, check=True)
subprocess.run(["git", "push", "origin", "master", "--tags"], cwd=ROOT, check=True)
print(f"  [OK] Pushed commit and tag v{VERSION} to GitHub.")

print("\n=== [STEP 5] Creating GitHub Release v" + VERSION + " ===")
release_cmd = [
    "gh", "release", "create", f"v{VERSION}",
    str(patch_lite),
    str(patch_full),
    str(manifest_file),
    "--title", f"Broadcast Playroom v{VERSION}",
    "--notes", changelog
]
res = subprocess.run(release_cmd, cwd=ROOT)
if res.returncode == 0:
    print(f"  [OK] GitHub Release v{VERSION} created successfully!")
else:
    print(f"  [!] Notice: gh release create exited with {res.returncode}")

print("\n=== [STEP 6] Purging jsDelivr Cache ===")
purge_urls = [
    f"https://purge.jsdelivr.net/gh/zepiam/broadcast-playroom-3@master/version.json",
    f"https://purge.jsdelivr.net/gh/zepiam/broadcast-playroom-3@v{VERSION}/version.json"
]
for p_url in purge_urls:
    try:
        req = urllib.request.Request(p_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"  [OK] Purged {p_url} (HTTP {r.status})")
    except Exception as ex:
        print(f"  [INFO] Purge notice for {p_url}: {ex}")

print(f"\n========================================================")
print(f"   Release v{VERSION} Published Successfully!           ")
print(f"========================================================")
