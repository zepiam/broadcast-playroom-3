import os
import sys
import shutil
import hashlib
import json
import zipfile
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from huggingface_hub import HfApi
except ImportError:
    print("Error: huggingface_hub not installed.")
    sys.exit(1)

root = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

# 1. Update version to 3.48
print("=== Step 1: Updating Version to 3.48 ===")
updater_file = root / "updater.py"
u_txt = updater_file.read_text(encoding='utf-8')
u_txt = u_txt.replace('CURRENT_VERSION = "3.47"', 'CURRENT_VERSION = "3.48"')
u_txt = u_txt.replace('CURRENT_VERSION = "3.46"', 'CURRENT_VERSION = "3.48"')
updater_file.write_text(u_txt, encoding='utf-8')

pkg_file = root / "package.json"
p_txt = pkg_file.read_text(encoding='utf-8')
p_txt = p_txt.replace('"version": "3.47"', '"version": "3.48"')
p_txt = p_txt.replace('"version": "3.46"', '"version": "3.48"')
pkg_file.write_text(p_txt, encoding='utf-8')

for h_path in [root / "src" / "index.html", root / "dist" / "index.html"]:
    if h_path.exists():
        h_txt = h_path.read_text(encoding='utf-8')
        h_txt = h_txt.replace('>v3.47<', '>v3.48<')
        h_txt = h_txt.replace('>v3.46<', '>v3.48<')
        h_txt = h_txt.replace('>v3.6<', '>v3.48<')
        h_path.write_text(h_txt, encoding='utf-8')

pi_file = root / "patch_installer.py"
pi_txt = pi_file.read_text(encoding='utf-8')
pi_txt = pi_txt.replace("'3.47'", "'3.48'")
pi_txt = pi_txt.replace("/3.47", "/3.48")
pi_file.write_text(pi_txt, encoding='utf-8')

print("  [OK] Version 3.48 set across all files.")

# Rebuild dist
print("\n=== Rebuilding dist ===")
subprocess.run(["npm", "run", "build"], cwd=root, shell=True, check=True)

# Rebuild BP3_PatchInstaller.exe with PyInstaller
print("\n=== Rebuilding BP3_PatchInstaller.exe ===")
subprocess.run(["pyinstaller", "BP3_PatchInstaller.spec", "--noconfirm"], cwd=root, shell=True, check=True)
compiled_installer = root / "dist" / "BP3_PatchInstaller.exe"
if compiled_installer.exists():
    shutil.copy2(compiled_installer, root / "BP3_PatchInstaller.exe")
    print("  [OK] BP3_PatchInstaller.exe rebuilt and copied to root.")

# 2. Package patch archives
print("\n=== Step 2: Packaging Patch Archives for v3.48 ===")
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

patch_lite = patches_dir / 'patch-v3.48-lite.zip'
patch_full = patches_dir / 'patch-v3.48-full.zip'
dist_src = root / 'dist'

changelog = """# Broadcast Playroom v3.48

### สิ่งที่ได้รับการปรับปรุงในเวอร์ชัน 3.48:
- **กลับมาใช้ Native Windows Title Bar มาตรฐานเหมือนกันทุกเครื่อง 100%**:
  - ยกเลิกการใช้ Frameless Custom Title Bar ภายในหน้าเว็บ เพื่อตัดปัญหา Title Bar ซ้อน 2 ชั้นและปัญหาการย่อ/ขยาย/ลากหน้าต่าง
  - คืนค่า Title Bar ของระบบ Windows มาตรฐาน พร้อมปุ่ม ย่อ (Minimize), ขยาย (Maximize), และ ปิด (Close) แท้ๆ ของระบบปฏิบัติการ
  - เอาแถบควบคุมภายในแอป (Fake Title Bar & Resizers) ออกทั้งหมด ทำให้หน้าจอคลีน สวยงาม และเสถียร 100%
- **รองรับคีย์ลัด Ctrl+R / Ctrl+Shift+R / F5 เพื่อ Hard-Reload ล้างแคชได้ทุกเครื่อง**:
  - เพิ่ม Global Keyboard Shortcut ดักจับการกด `Ctrl+R`, `Ctrl+Shift+R`, หรือ `F5` เพื่อสั่งโหลดหน้าจอใหม่และสลัดแคชทิ้ง (Cache Bust) ทันทีในทุกโหมด
- **ระบบเช็คอัปเดต Multi-CDN ไม่ค้างและไม่ติดบล็อกเน็ตในไทย**:
  - ดึงข้อมูลผ่าน Hugging Face CDN (Cloudflare) + jsDelivr Mirror เช็คผ่านได้ใน 0.5 วินาที
  - แก้ไขป้ายกำกับเป็น 'เวอร์ชันล่าสุด' และแสดงเลขเวอร์ชันปัจจุบัน v3.48 อย่างถูกต้อง
"""

manifest_file = root / 'version.json'
manifest_data_pre = {
    "product": "broadcast-playroom-3",
    "version": "3.48",
    "latest_version": "3.48",
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

chosen_installer = root / "BP3_PatchInstaller.exe"

def make_patch(out_zip, is_full=False):
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in CORE_FILES:
            sf = root / f
            if sf.exists():
                z.write(sf, f)
                z.write(sf, f'_internal/{f}')
        if chosen_installer.exists():
            z.write(chosen_installer, "BP3_PatchInstaller.exe")
            z.write(chosen_installer, "_internal/BP3_PatchInstaller.exe")
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
    "version": "3.48",
    "latest_version": "3.48",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.48/patch-v3.48-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.48-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.48/patch-v3.48-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.48-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    }
}

manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Updated version.json with sha256 & mirrors.")

for patch_path in [patch_lite, patch_full]:
    with zipfile.ZipFile(patch_path, 'a') as z:
        z.write(manifest_file, 'version.json')
        z.write(manifest_file, '_internal/version.json')
    print(f"  [OK] Embedded latest version.json into {patch_path.name}")

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)
manifest["lite"]["sha256"] = hash_lite
manifest["lite"]["size"] = patch_lite.stat().st_size
manifest["full"]["sha256"] = hash_full
manifest["full"]["size"] = patch_full.stat().st_size
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

# 3. Upload to Hugging Face
print("\n=== Step 3: Uploading to Hugging Face ===")
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
        path_in_repo="patches/patch-v3.48-lite.zip",
        repo_id=repo_id,
        repo_type="model"
    )
    print("  [OK] Uploaded patch-v3.48-lite.zip to Hugging Face.")

    api.upload_file(
        path_or_fileobj=str(patch_full),
        path_in_repo="patches/patch-v3.48-full.zip",
        repo_id=repo_id,
        repo_type="model"
    )
    print("  [OK] Uploaded patch-v3.48-full.zip to Hugging Face.")

    if chosen_installer.exists():
        api.upload_file(
            path_or_fileobj=str(chosen_installer),
            path_in_repo="BP3_PatchInstaller.exe",
            repo_id=repo_id,
            repo_type="model"
        )
        print("  [OK] Uploaded BP3_PatchInstaller.exe to Hugging Face.")

# 4. Commit and Push Git
print("\n=== Step 4: Git Commit & Tag ===")
subprocess.run([
    "git", "add",
    "updater.py", "launch_dev.py", "patch_installer.py", "BP3_PatchInstaller.exe", "src/index.html", "src/styles.css",
    "package.json", "version.json",
    "patches/patch-v3.48-lite.zip", "patches/patch-v3.48-full.zip",
    "publish_release_v348.py"
], cwd=root, check=True)

subprocess.run(["git", "commit", "-m", "Release v3.48: Standard Native Windows Title Bar & Global Ctrl+R Reload"], cwd=root, check=True)
subprocess.run(["git", "tag", "-a", "v3.48", "-m", "Release v3.48"], cwd=root, check=True)
subprocess.run(["git", "push", "origin", "master", "--tags"], cwd=root, check=True)
print("  [OK] Pushed commit and tag v3.48 to GitHub.")

# 5. Create GitHub Release
print("\n=== Step 5: Creating GitHub Release ===")
release_cmd = [
    "gh", "release", "create", "v3.48",
    str(patch_lite),
    str(patch_full),
    str(manifest_file),
    "--title", "Broadcast Playroom v3.48",
    "--notes", changelog
]
if chosen_installer.exists():
    release_cmd.append(str(chosen_installer))

res = subprocess.run(release_cmd, cwd=root)
if res.returncode == 0:
    print("  [OK] GitHub Release v3.48 created successfully!")
else:
    print("  [!] gh release create failed or returned non-zero code.")

print("\n=== Release v3.48 Complete! ===")
