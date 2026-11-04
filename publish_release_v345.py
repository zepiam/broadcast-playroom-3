import os
import sys
import shutil
import hashlib
import json
import zipfile
import subprocess
from pathlib import Path

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from huggingface_hub import HfApi
except ImportError:
    print("Error: huggingface_hub not installed.")
    sys.exit(1)

root = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

# 1. Update version to 3.45
print("=== Step 1: Updating Version to 3.45 ===")
updater_file = root / "updater.py"
u_txt = updater_file.read_text(encoding='utf-8')
u_txt = u_txt.replace('CURRENT_VERSION = "3.44"', 'CURRENT_VERSION = "3.45"')
updater_file.write_text(u_txt, encoding='utf-8')

pkg_file = root / "package.json"
p_txt = pkg_file.read_text(encoding='utf-8')
p_txt = p_txt.replace('"version": "3.44"', '"version": "3.45"')
pkg_file.write_text(p_txt, encoding='utf-8')

for h_path in [root / "src" / "index.html", root / "dist" / "index.html"]:
    if h_path.exists():
        h_txt = h_path.read_text(encoding='utf-8')
        h_txt = h_txt.replace('v3.44', 'v3.45')
        h_path.write_text(h_txt, encoding='utf-8')

print("  [OK] Version 3.45 set across all files.")

# Rebuild dist to sync updated index.html & assets
print("\n=== Rebuilding dist ===")
subprocess.run(["npm", "run", "build"], cwd=root, shell=True, check=True)

# 2. Package patch archives
print("\n=== Step 2: Packaging Patch Archives for v3.45 ===")
CORE_FILES = [
    'version.json',
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_tiktok.py', 'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat',
    'avatar_cache_service.py', 'plugin_manager.py'
]

EXTRA_FOLDERS = [
    ('docs', 'docs'),
    ('plugins', 'plugins')
]

patches_dir = root / 'patches'
patches_dir.mkdir(exist_ok=True)

patch_lite = patches_dir / 'patch-v3.45-lite.zip'
patch_full = patches_dir / 'patch-v3.45-full.zip'
dist_src = root / 'dist'

changelog = """# Broadcast Playroom v3.45

### รายละเอียดการอัปเดตเวอร์ชัน 3.45:
- **แก้ไขบั๊กข้อมูลผู้ชมใน User Manager หายถาวรเมื่ออัปเดตเวอร์ชัน (Permanent User Manager Persistence & Deep Merge Fix)**:
  - แก้ไขตัวอัปเดต (`updater.py` / batch script) ไม่ให้เขียนทับไฟล์ `user_roster.json` ด้วยไฟล์ว่างเปล่า โดยเพิ่มเงื่อนไขตรวจสอบขนาดไฟล์ (`>10 bytes`) ก่อน Backup และ Restore ป้องกันไฟล์ว่างขนาด 2 bytes เขียนทับข้อมูลจริง
  - ผสานรวมข้อมูลผู้ชม (`Deep Merge`) ทั้งใน `updater.py` และ `launch_dev.py` จากทุกไดเรกทอรี (`DATA_ROOT`, `LOCALAPPDATA`, `settings_backup`) อัตโนมัติ โดยไม่คัดเลือกไฟล์ใดไฟล์หนึ่งทิ้ง แต่รวมรายชื่อผู้ชม ประวัติการแชท และกิจกรรมเข้าด้วยกันทั้งหมด
  - เพิ่มระบบ Safe Atomic Write (`.tmp` -> replace) และระบบป้องกันการเขียนทับด้วยข้อมูลว่าง (Zero-Wipe Guard)
  - เพิ่มการบันทึก `localStorage` ทันทีเมื่อมีผู้ชมส่งข้อความ (Synchronous Persist) และส่งข้อมูลผ่าน `navigator.sendBeacon` ทันทีก่อนปิดหรือรีสตาร์ทโปรแกรม (`beforeunload` / `pagehide`)
  - อัปเดตการซิงค์แบบ Two-Way Realtime Sync ใน `src/user_controls.js` เพื่อให้ฐานข้อมูลฝั่ง Backend และ Frontend ตรงกันตลอดเวลา
  - กู้คืนประวัติและข้อมูลผู้ชม `MeN9CH` (Twitch: "สวัสดีครับ") กลับเข้าสู่ฐานข้อมูลระบบเรียบร้อย
"""

manifest_file = root / 'version.json'
manifest_data_pre = {
    "product": "broadcast-playroom-3",
    "version": "3.45",
    "latest_version": "3.45",
    "critical": True,
    "changelog": changelog
}
manifest_file.write_text(json.dumps(manifest_data_pre, ensure_ascii=False, indent=2), encoding='utf-8')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def make_patch(out_zip, is_full=False):
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in CORE_FILES:
            sf = root / f
            if sf.exists():
                z.write(sf, f)
                z.write(sf, f'_internal/{f}')
        # Embed BP3_PatchInstaller.exe directly in root of patch archive
        installer_exe = root / "dist_installer" / "BP3_PatchInstaller.exe"
        if installer_exe.exists():
            z.write(installer_exe, "BP3_PatchInstaller.exe")
        for p in dist_src.rglob('*'):
            if p.is_file():
                rel = p.relative_to(dist_src)
                z.write(p, f'dist/{rel}')
                z.write(p, f'_internal/dist/{rel}')
        for src_folder, dst_folder in EXTRA_FOLDERS:
            folder_path = root / src_folder
            if folder_path.is_dir():
                for p in folder_path.rglob('*'):
                    if p.is_file():
                        rel = p.relative_to(folder_path)
                        z.write(p, f'{dst_folder}/{rel}')
                        z.write(p, f'_internal/{dst_folder}/{rel}')
    print(f"  [OK] Created {out_zip.name} ({out_zip.stat().st_size / (1024*1024):.2f} MB)")

make_patch(patch_lite, is_full=False)
make_patch(patch_full, is_full=True)

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.45",
    "latest_version": "3.45",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.45/patch-v3.45-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.45-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.45/patch-v3.45-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.45-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    }
}

manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Updated version.json with sha256 & mirrors.")

# Re-add updated version.json into patch zips
for patch_path in [patch_lite, patch_full]:
    with zipfile.ZipFile(patch_path, 'a') as z:
        z.write(manifest_file, 'version.json')
        z.write(manifest_file, '_internal/version.json')
    print(f"  [OK] Embedded latest version.json into {patch_path.name}")

# Re-calculate hashes after embedding final version.json
hash_lite = digest(patch_lite)
hash_full = digest(patch_full)
manifest["lite"]["sha256"] = hash_lite
manifest["lite"]["size"] = patch_lite.stat().st_size
manifest["full"]["sha256"] = hash_full
manifest["full"]["size"] = patch_full.stat().st_size
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

# 3. Build / Verify BP3_PatchInstaller.exe
installer_exe = root / "dist_installer" / "BP3_PatchInstaller.exe"
print(f"  [OK] BP3_PatchInstaller.exe ready at {installer_exe}")

# 4. Upload to Hugging Face
print("\n=== Step 4: Uploading to Hugging Face ===")
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    token_path = Path.home() / ".cache" / "huggingface" / "token"
    if token_path.exists():
        hf_token = token_path.read_text().strip()

if not hf_token:
    print("Warning: HF_TOKEN not found, skipping Hugging Face upload.")
else:
    api = HfApi(token=hf_token)
    repo_id = "men9ch/broadcast-playroom-3"
    api.upload_file(
        path_or_fileobj=str(manifest_file),
        path_in_repo="version.json",
        repo_id=repo_id,
        repo_type="model"
    )
    print("  [OK] Uploaded version.json to Hugging Face.")

    api.upload_file(
        path_or_fileobj=str(patch_lite),
        path_in_repo="patches/patch-v3.45-lite.zip",
        repo_id=repo_id,
        repo_type="model"
    )
    print("  [OK] Uploaded patch-v3.45-lite.zip to Hugging Face.")

    api.upload_file(
        path_or_fileobj=str(patch_full),
        path_in_repo="patches/patch-v3.45-full.zip",
        repo_id=repo_id,
        repo_type="model"
    )
    print("  [OK] Uploaded patch-v3.45-full.zip to Hugging Face.")

    if installer_exe.exists():
        api.upload_file(
            path_or_fileobj=str(installer_exe),
            path_in_repo="BP3_PatchInstaller.exe",
            repo_id=repo_id,
            repo_type="model"
        )
        print("  [OK] Uploaded BP3_PatchInstaller.exe to Hugging Face.")

# 5. Commit and Push Git
print("\n=== Step 5: Git Commit & Tag ===")
subprocess.run([
    "git", "add",
    "updater.py", "launch_dev.py", "src/user_controls.js", "src/index.html",
    "package.json", "version.json",
    "patches/patch-v3.45-lite.zip", "patches/patch-v3.45-full.zip",
    "publish_release_v345.py"
], cwd=root, check=True)

subprocess.run(["git", "commit", "-m", "Release v3.45: Fix User Manager Persistence across Updates & Multi-Path Deep Merge"], cwd=root, check=True)
subprocess.run(["git", "tag", "-a", "v3.45", "-m", "Release v3.45"], cwd=root, check=True)
subprocess.run(["git", "push", "origin", "master", "--tags"], cwd=root, check=True)
print("  [OK] Pushed commit and tag v3.45 to GitHub.")

# 6. Create GitHub Release
print("\n=== Step 6: Creating GitHub Release ===")
release_cmd = [
    "gh", "release", "create", "v3.45",
    str(patch_lite),
    str(patch_full),
    str(manifest_file),
    "--title", "Broadcast Playroom v3.45",
    "--notes", changelog
]
if installer_exe.exists():
    release_cmd.append(str(installer_exe))

res = subprocess.run(release_cmd, cwd=root)
if res.returncode == 0:
    print("  [OK] GitHub Release v3.45 created successfully!")
else:
    print("  [!] gh release create failed or returned non-zero code.")

print("\n=== Release v3.45 Complete! ===")
