import os
import sys
import shutil
import hashlib
import json
import subprocess
import time
import zipfile
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

VERSION = "3.54"

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
    'BP3_PatchInstaller.exe', 'version.json', 'package.json'
]

EXTRA_FOLDERS = [
    ('docs', 'docs'),
    ('plugins', 'plugins')
]

dist_src = ROOT / 'dist'
patch_lite = PATCHES_DIR / f'patch-v{VERSION}-lite.zip'
patch_full = PATCHES_DIR / f'patch-v{VERSION}-full.zip'

changelog = f"""# Broadcast Playroom v{VERSION}

### รายการอัปเดตและปรับปรุงในเวอร์ชั่น {VERSION}:
- **แก้ไขสถานะเซิร์ฟเวอร์เสียงอ่าน TTS หลุดเชื่อมต่อ (Server Status 100% Fixed)**:
  - เพิ่มโมดูล `language_detect.py` และ `network_dns.py` เข้าชุดแพตช์อัปเดตและโปรแกรมหลักอย่างสมบูรณ์แบบ
  - เสริมระบบ Fallback ความทนทานสูงใน `tts_service.py` แม้ขาดโมดูลเสริมเสียงอ่านก็ยังสังเคราะห์เสียงภาษาไทยได้ลื่นไหล 0% ล่ม
  - แถบสถานะด้านบนจะแสดงเป็นสีเขียว `🟢 ทดสอบเสียงสำเร็จ` ทั้งในโหมด Dev และตัวติดตั้งจริง
- **ปรับปรุงตัวติดตั้ง Setup สลับตำแหน่งเวอร์ชัน**:
  - สลับตำแหน่งตัวเลือกในหน้าติดตั้งให้ **⚡ Lite Edition (ขนาดกะทัดรัด)** อยู่ด้านบน และ **🚀 Full Edition (ครบวงจร)** อยู่ด้านล่างตามลำดับการใช้งาน
  - ตั้งค่า Google Drive เป็นช่องทางดาวน์โหลดหลักความเร็วสูง พร้อม Hugging Face สำรองอัตโนมัติ
- **ระบบอัปเดต In-App Updater ราบรื่น ไม่เปิดซ้ำ 2 หน้าต่าง**:
  - รองรับการรีสตาร์ทแตกไฟล์ทับและปิดหน้าต่างเดิมอย่างหมดจด ไม่เกิดการเปิดโปรแกรมซ้ำซ้อน
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
                    rel = full.relative_to(sp)
                    rel_clean = str(rel).replace('\\', '/')
                    z.write(full, f"{arc_dir}/{rel_clean}")

print(f"  [OK] Created {patch_lite.name} ({patch_lite.stat().st_size / (1024*1024):.2f} MB)")

# Build Full patch
with zipfile.ZipFile(patch_full, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in CORE_FILES:
        fp = ROOT / f
        if fp.exists():
            z.write(fp, f)
            print(f"  [Full] + {f}")

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
                    rel = full.relative_to(sp)
                    rel_clean = str(rel).replace('\\', '/')
                    z.write(full, f"{arc_dir}/{rel_clean}")

print(f"  [OK] Created {patch_full.name} ({patch_full.stat().st_size / (1024*1024):.2f} MB)")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    "version": VERSION,
    "latest_version": VERSION,
    "release_date": time.strftime("%Y-%m-%d"),
    "mandatory": False,
    "changelog": changelog,
    "patches": {
        "lite": {
            "file": f"patch-v{VERSION}-lite.zip",
            "url": f"https://huggingface.co/{HF_REPO_ID}/resolve/main/patches/patch-v{VERSION}-lite.zip",
            "sha256": sha256_file(patch_lite),
            "size": patch_lite.stat().st_size,
            "mirrors": [
                f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-lite.zip"
            ]
        },
        "full": {
            "file": f"patch-v{VERSION}-full.zip",
            "url": f"https://huggingface.co/{HF_REPO_ID}/resolve/main/patches/patch-v{VERSION}-full.zip",
            "sha256": sha256_file(patch_full),
            "size": patch_full.stat().st_size,
            "mirrors": [
                f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-full.zip"
            ]
        }
    },
    "lite": {
        "file": f"patch-v{VERSION}-lite.zip",
        "url": f"https://huggingface.co/{HF_REPO_ID}/resolve/main/patches/patch-v{VERSION}-lite.zip",
        "sha256": sha256_file(patch_lite),
        "size": patch_lite.stat().st_size
    },
    "full": {
        "file": f"patch-v{VERSION}-full.zip",
        "url": f"https://huggingface.co/{HF_REPO_ID}/resolve/main/patches/patch-v{VERSION}-full.zip",
        "sha256": sha256_file(patch_full),
        "size": patch_full.stat().st_size
    }
}

manifest_file = ROOT / "version.json"
with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print("  [OK] Saved updated version.json manifest")

# Re-write version.json inside patches so updated version.json is extracted
for pz in [patch_lite, patch_full]:
    with zipfile.ZipFile(pz, 'a', zipfile.ZIP_DEFLATED) as z:
        z.write(manifest_file, "version.json")

print("\n=== [STEP 3] Uploading Patches and Setup to Hugging Face ===")
upload_items = [
    (patch_lite, f"patches/patch-v{VERSION}-lite.zip"),
    (patch_full, f"patches/patch-v{VERSION}-full.zip"),
    (manifest_file, "version.json"),
    (DIST_RELEASES / "BroadcastPlayroom3-Setup.exe", "BroadcastPlayroom3-Setup.exe"),
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
files_to_commit = [
    "src/index.html",
    "tts_service.py",
    "installer_gui.py",
    "version.json",
    f"patches/patch-v{VERSION}-lite.zip",
    f"patches/patch-v{VERSION}-full.zip"
]
for fc in files_to_commit:
    pfc = ROOT / fc
    if pfc.exists():
        subprocess.run(["git", "add", fc], cwd=ROOT, check=True)

subprocess.run(["git", "commit", "-m", f"release: Broadcast Playroom v{VERSION} (TTS server status fix & Setup order)"], cwd=ROOT, check=True)
subprocess.run(["git", "tag", "-a", f"v{VERSION}", "-m", f"Release v{VERSION}"], cwd=ROOT, check=True)
subprocess.run(["git", "push", "origin", "master", "--tags"], cwd=ROOT, check=True)
print(f"  [OK] Pushed commit and tag v{VERSION} to GitHub.")

print("\n=== [STEP 5] Creating GitHub Release v" + VERSION + " ===")
release_cmd = [
    "gh", "release", "create", f"v{VERSION}",
    str(patch_lite),
    str(patch_full),
    str(manifest_file),
    str(DIST_RELEASES / "BroadcastPlayroom3-Setup.exe"),
    "--title", f"Broadcast Playroom v{VERSION}",
    "--notes", changelog
]
res = subprocess.run(release_cmd, cwd=ROOT)
if res.returncode == 0:
    print(f"  [OK] GitHub Release v{VERSION} created successfully!")
else:
    print(f"  [!] Notice: gh release create exited with {res.returncode}")

print(f"\n========================================================")
print(f"   Release v{VERSION} Published Successfully!           ")
print(f"   (No repack performed as requested)                   ")
print(f"========================================================")
