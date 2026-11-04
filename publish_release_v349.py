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

VERSION = "3.49"

print(f"=== [STEP 1] Rebuilding Frontend Distribution for v{VERSION} ===")
subprocess.run(["npm.cmd", "run", "build"], cwd=ROOT, check=True)

# Copy BP3_PatchInstaller.exe to root if not already
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

### รายละเอียดการอัปเดตเวอร์ชัน {VERSION}:
- **มาตรฐานระบบหน้าต่างแบบ Native Chrome/Edge App Mode 100% เหมือนกันทุกเครื่อง**:
  - แก้ไขปัญหาความแตกต่างระหว่างเครื่อง Dev และเครื่องผู้ใช้งานทั่วไป โดยเปลี่ยนมาใช้ Chrome/Edge App Mode เป็นมาตรฐานหลักเดียวกันทั้งหมด
  - แสดงผล Windows Native Title Bar ด้านบนสุด พร้อมปุ่มย่อ ขยาย และปิดหน้าต่างมาตรฐานของ Windows อย่างสมบูรณ์แบบ
  - นำแถบ Title Bar ภายในโปรแกรมที่ซ้ำซ้อนออก เพื่อให้หน้าตาคลีนตาและมี Title Bar เพียงชั้นเดียว
- **เปิดหน้าต่างเครื่องมือย่อยแยกออกนอกจอโปรแกรมได้อิสระ (Multi-Monitor Floating Windows)**:
  - เพิ่มแฟล็ก `--disable-popup-blocking` ในคำสั่งรันเบราว์เซอร์ App Mode
  - ทำให้หน้าต่างแชท, การตั้งค่า, วงล้อสุ่ม, คำถาม และเครื่องมืออื่นๆ สามารถ Popout ออกเป็นหน้าต่างแยกอิสระ สามารถลากไปวางที่หน้าจอที่ 2 หรือ 3 ได้อย่างราบรื่น
- **แก้ไขปุ่มแก้ไขสตรีม (Edit Link) และกำจัด `javascript:void(0)`**:
  - เปลี่ยนลิงก์ Edit ของ Twitch/YouTube/Kick ให้ทำงานผ่าน handler ที่ถูกต้อง ไม่แสดง `javascript:void(0)` ที่มุมซ้ายล่างอีกต่อไป
  - เปิดหน้าแดชบอร์ดแก้ไขข้อมูลสตรีมบนเบราว์เซอร์หลักของผู้ใช้ได้ทันที
- **แก้ไขการดึงและรีเฟรชชื่อห้องสตรีม Twitch (SSL & Emojis Support)**:
  - เพิ่มระบบโหลดใบรับรอง SSL มาตรฐานของระบบ Windows ป้องกันปัญหาดึงชื่อห้องสตรีมไม่สำเร็จบนเครื่องที่ไม่มี Certificate Bundle
  - รองรับการถอดรหัสตัวอักษรพิเศษและอิโมจิในชื่อห้องสตรีมโดยไม่เกิดข้อผิดพลาด
"""

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

print(f"\n=== [STEP 2] Packaging Patches for v{VERSION} ===")

def make_patch(out_zip, is_full=False):
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in CORE_FILES:
            sf = ROOT / f
            if sf.exists():
                z.write(sf, f)
                z.write(sf, f'_internal/{f}')
        for p in dist_src.rglob('*'):
            if p.is_file():
                rel = p.relative_to(dist_src).as_posix()
                z.write(p, f'dist/{rel}')
                z.write(p, f'_internal/dist/{rel}')
        for src_folder, dst_folder in EXTRA_FOLDERS:
            folder_path = ROOT / src_folder
            if folder_path.is_dir():
                for p in folder_path.rglob('*'):
                    if p.is_file():
                        rel = p.relative_to(folder_path).as_posix()
                        z.write(p, f'{dst_folder}/{rel}')
                        z.write(p, f'_internal/{dst_folder}/{rel}')
        if not is_full:
            lite_exe = ROOT / 'build_trials' / 'lite' / 'BroadcastPlayroom3-Lite' / 'BroadcastPlayroom3-Lite.exe'
            if lite_exe.exists():
                z.write(lite_exe, 'BroadcastPlayroom3-Lite.exe')
                z.write(lite_exe, '_internal/BroadcastPlayroom3-Lite.exe')
        print(f"  [OK] Packaged {out_zip.name} ({out_zip.stat().st_size:,} bytes)")

make_patch(patch_lite, is_full=False)
make_patch(patch_full, is_full=True)

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

manifest_data = {
    "product": "broadcast-playroom-3",
    "version": VERSION,
    "latest_version": VERSION,
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-lite.zip",
        "mirrors": [
            f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-lite.zip",
            f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-lite.zip",
            f"https://cdn.jsdelivr.net/gh/zepiam/broadcast-playroom-3@v{VERSION}/patches/patch-v{VERSION}-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-full.zip",
        "mirrors": [
            f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-full.zip",
            f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-full.zip",
            f"https://cdn.jsdelivr.net/gh/zepiam/broadcast-playroom-3@v{VERSION}/patches/patch-v{VERSION}-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "patch_url": f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-lite.zip",
            "mirrors": [
                f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-lite.zip",
                f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-lite.zip",
                f"https://cdn.jsdelivr.net/gh/zepiam/broadcast-playroom-3@v{VERSION}/patches/patch-v{VERSION}-lite.zip"
            ],
            "sha256": hash_lite
        },
        "full": {
            "patch_url": f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-full.zip",
            "mirrors": [
                f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{VERSION}-full.zip",
                f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{VERSION}/patch-v{VERSION}-full.zip",
                f"https://cdn.jsdelivr.net/gh/zepiam/broadcast-playroom-3@v{VERSION}/patches/patch-v{VERSION}-full.zip"
            ],
            "sha256": hash_full
        }
    }
}

manifest_file = ROOT / 'version.json'
manifest_file.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Updated version.json with hashes and multi-CDN mirrors.")

print(f"\n=== [STEP 3] Uploading v{VERSION} Patches to Hugging Face ===")
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
    f"patches/patch-v{VERSION}-lite.zip", f"patches/patch-v{VERSION}-full.zip"
]
for fc in files_to_commit:
    subprocess.run(["git", "add", fc], cwd=ROOT, check=True)

subprocess.run(["git", "commit", "-m", f"Release v{VERSION}: Standardize Chrome/Edge App Mode, Native Title Bar & Popouts Parity, Twitch SSL Fix"], cwd=ROOT, check=True)
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

print(f"\n========================================================")
print(f"   Release v{VERSION} & Standalone Repackage Complete!   ")
print(f"========================================================")
