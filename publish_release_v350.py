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
SEVEN_ZIP = Path(r"C:\Program Files\7-Zip\7z.exe")

try:
    from huggingface_hub import HfApi, get_token
except ImportError:
    print("[ERROR] huggingface_hub not installed")
    sys.exit(1)

HF_REPO_ID = "men9ch/broadcast-playroom-3"
hf_token = get_token()
if not hf_token:
    print("[ERROR] No Hugging Face token found")
    sys.exit(1)
api = HfApi(token=hf_token)

VERSION = "3.50"

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
- **Disk-First Module Loader สำหรับตัวรัน (.exe)**:
  - แก้ไขปัญหาตัวรัน PyInstaller onedir (.exe) ไม่ยอมอ่านไฟล์ `.py` ที่อัปเดตจากแพตช์ โดยปรับให้ระบบค้นหาไฟล์บน Disk มาก่อน bytecode เก่าที่ฝังไว้
  - ทำให้ระบบเช็คอัปเดต (In-App Updater) ตรวจพบเวอร์ชั่นใหม่ผ่าน Hugging Face CDN อย่างแม่นยำทุกเครื่อง
- **แก้ไขหน้าต่าง Windows Defender (1-Click Exclusion) ค้างกำลังโหลด**:
  - เชื่อมโยงระบบตรวจจับโฟลเดอร์ปัจจุบันและสถานะการยกเว้นทันทีเมื่อคลิกแท็บ Windows Defender ในหน้าตั้งค่า
  - รองรับการตรวจจับโฟลเดอร์แม่ที่ Setup เพิ่มข้อยกเว้นไว้ ไม่ฟ้องว่าถูกย้ายโฟลเดอร์อีกต่อไป
  - เพิ่มการยกเว้น Process ของตัวรันโปรแกรมทั้ง Lite และ Full เพื่อป้องกัน Defender ล็อกไฟล์
- **แก้ไขปุ่ม Edit สตรีม และปุ่ม Refresh Title**:
  - เปลี่ยนปุ่มลิงก์เป็น Native Button หมดปัญหา URL ติด `#` หรือข้อความ `javascript:void(0)`
  - ใช้คำสั่งระบบ Windows (`os.startfile`) เพื่อเปิดหน้าจัดการสตรีมบน Default Browser ของผู้ใช้โดยตรงที่มีการล็อกอินบัญชีไว้อยู่แล้ว
  - ปรับปรุงให้กล่องแสดง Title และปุ่มควบคุมแสดงผลอย่างสมบูรณ์แบบ
"""

print(f"\n=== [STEP 2] Packaging {patch_lite.name} & {patch_full.name} ===")

# Build Lite patch
with zipfile.ZipFile(patch_lite, 'w', zipfile.ZIP_DEFLATED) as z:
    # Include new Lite .exe with disk-first loader
    lite_exe = ROOT / "build_trials" / "lite" / "BroadcastPlayroom3-Lite" / "BroadcastPlayroom3-Lite.exe"
    if lite_exe.exists():
        z.write(lite_exe, "BroadcastPlayroom3-Lite.exe")
        print("  [OK] Packed BroadcastPlayroom3-Lite.exe into patch")
    
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
    # Include new Full .exe with disk-first loader
    full_exe = ROOT / "build_trials" / "full" / "BroadcastPlayroom3-Full" / "BroadcastPlayroom3-Full.exe"
    if full_exe.exists():
        z.write(full_exe, "BroadcastPlayroom3-Full.exe")
        print("  [OK] Packed BroadcastPlayroom3-Full.exe into patch")
    
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
    "release_date": time.strftime("%Y-%m-%d"),
    "mandatory": False,
    "changelog": changelog,
    "patches": {
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
}

manifest_file = ROOT / "version.json"
with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print("  [OK] Updated version.json manifest with hashes.")

print(f"\n=== [STEP 3] Uploading Patches & version.json to Hugging Face ===")
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="version.json",
    repo_id=HF_REPO_ID,
    repo_type="model"
)
print("  [OK] Uploaded version.json to Hugging Face")

api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo=f"patches/{patch_lite.name}",
    repo_id=HF_REPO_ID,
    repo_type="model"
)
print(f"  [OK] Uploaded {patch_lite.name} to Hugging Face")

api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo=f"patches/{patch_full.name}",
    repo_id=HF_REPO_ID,
    repo_type="model"
)
print(f"  [OK] Uploaded {patch_full.name} to Hugging Face")

print(f"\n=== [STEP 4] Git Commit & Tag v{VERSION} ===")
files_to_commit = [
    "launch_dev.py", "updater.py", "chat_bridge.py", "app_window_frame.py",
    "src/index.html", "package.json", "version.json", "patch_installer.py",
    "defender_helper.py", "installer_gui.py", "package_entry.py", "BP3_PatchInstaller.exe",
    f"patches/patch-v{VERSION}-lite.zip", f"patches/patch-v{VERSION}-full.zip"
]
for fc in files_to_commit:
    subprocess.run(["git", "add", fc], cwd=ROOT, check=True)

subprocess.run(["git", "commit", "-m", f"Release v{VERSION}: Disk-First Module Loader, Windows Defender Fix, Stream Manager Links"], cwd=ROOT, check=True)
subprocess.run(["git", "tag", "-a", f"v{VERSION}", "-m", f"Release v{VERSION}"], cwd=ROOT, check=True)
subprocess.run(["git", "push", "origin", "master", "--tags"], cwd=ROOT, check=True)
print(f"  [OK] Pushed commit and tag v{VERSION} to GitHub.")

print(f"\n=== [STEP 5] Creating GitHub Release v{VERSION} ===")
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
    print(f"  [!] gh release create notice: {res.returncode}")

print("\n=== [STEP 6] Syncing Standalone Full/Lite Folders for Repackaging ===")
TARGETS = [
    ("lite", ROOT / "build_trials" / "lite" / "BroadcastPlayroom3-Lite", DIST_RELEASES / "BroadcastPlayroom3-Lite.zip"),
    ("full", ROOT / "build_trials" / "full" / "BroadcastPlayroom3-Full", DIST_RELEASES / "BroadcastPlayroom3-Full.zip"),
]

def clean_stale_caches(target_dir: Path):
    for r, dirs, files in os.walk(target_dir, topdown=False):
        for d in dirs:
            if d in ('__pycache__', 'browser_profile', 'webview_data', 'Cache', 'Code Cache', 'GPUCache', 'ShaderCache'):
                dp = Path(r) / d
                try:
                    shutil.rmtree(dp, ignore_errors=True)
                except Exception:
                    pass

def sync_edition_folder(edition: str, target_dir: Path):
    print(f">> Synchronizing {edition.upper()} edition directory: {target_dir}")
    clean_stale_caches(target_dir)

    for py_file in CORE_FILES:
        src_f = ROOT / py_file
        if src_f.is_file():
            shutil.copy2(src_f, target_dir / py_file)
            int_dir = target_dir / "_internal"
            if int_dir.is_dir():
                shutil.copy2(src_f, int_dir / py_file)

    for dst_base in [target_dir / "dist", target_dir / "_internal" / "dist"]:
        if dst_base.parent.is_dir():
            if dst_base.is_dir():
                shutil.rmtree(dst_base, ignore_errors=True)
            shutil.copytree(dist_src, dst_base, dirs_exist_ok=True)

    print(f"   [OK] {edition.upper()} synced with v{VERSION} files.")

for edition, target_dir, zip_path in TARGETS:
    if target_dir.is_dir():
        sync_edition_folder(edition, target_dir)

print("\n=== [STEP 7] Building BroadcastPlayroom3-Setup.exe ===")
subprocess.run([sys.executable, str(ROOT / "build_setup_installer.py")], cwd=ROOT, check=True)

print("\n=== [STEP 8] Compressing Standalone Zip Packages ===")
for edition, target_dir, zip_path in TARGETS:
    if not target_dir.is_dir():
        continue
    print(f">> Compressing {zip_path.name}...")
    if zip_path.exists():
        zip_path.unlink()
    
    parent_dir = target_dir.parent
    folder_name = target_dir.name
    cmd_7z = [
        str(SEVEN_ZIP),
        "a", "-tzip",
        str(zip_path),
        folder_name,
        "-mx=3",
        "-mmt=on"
    ]
    subprocess.run(cmd_7z, cwd=parent_dir, check=True)
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"   [OK] {zip_path.name} created ({size_mb:.2f} MB)")

print("\n=== [STEP 9] Uploading Standalone Setups & Zips to Hugging Face ===")
upload_files = [
    DIST_RELEASES / "BroadcastPlayroom3-Lite.zip",
    DIST_RELEASES / "BroadcastPlayroom3-Full.zip",
    DIST_RELEASES / "BroadcastPlayroom3-Setup.exe"
]

for uf in upload_files:
    if uf.exists():
        size_mb = uf.stat().st_size / (1024 * 1024)
        print(f">> Uploading {uf.name} ({size_mb:.2f} MB) to Hugging Face...")
        api.upload_file(
            path_or_fileobj=str(uf),
            path_in_repo=uf.name,
            repo_id=HF_REPO_ID,
            repo_type="model"
        )
        print(f"   [OK] Successfully uploaded {uf.name}")

# Purge jsDelivr CDN cache for version.json
try:
    import urllib.request
    purge_url = "https://purge.jsdelivr.net/gh/men9ch/broadcast-playroom-3@master/version.json"
    req = urllib.request.Request(purge_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        print("  [OK] Purged jsDelivr cache for version.json:", r.status)
except Exception as e:
    print("  [!] Notice: jsDelivr purge skipped:", e)

print(f"\n========================================================")
print(f"   Release v{VERSION} & Standalone Repackage Complete!   ")
print(f"========================================================")
