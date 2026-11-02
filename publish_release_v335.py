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

# 1. Confirm version 3.35
print("=== Step 1: Confirming Version 3.35 ===")
updater_file = root / "updater.py"
u_txt = updater_file.read_text(encoding='utf-8')
assert 'CURRENT_VERSION = "3.35"' in u_txt, "updater.py version mismatch"

pkg_file = root / "package.json"
p_txt = pkg_file.read_text(encoding='utf-8')
assert '"version": "3.35"' in p_txt, "package.json version mismatch"

html_file = root / "src" / "index.html"
h_txt = html_file.read_text(encoding='utf-8')
assert '<span class="desktop-titlebar-tag">v3.35</span>' in h_txt, "src/index.html version mismatch"
print("  [OK] Version 3.35 confirmed.")

# 2. Commit and push to git
print("\n=== Step 2: Git Commit & Push v3.35 ===")
subprocess.run(['git', '-C', str(root), 'add', '-A'], check=True)
subprocess.run(['git', '-C', str(root), 'commit', '-m', 'Release v3.35: Protected OAuth Credentials Encryption, Plugin Architecture Foundation & Auto-Cleanup of Legacy Dev Folders'], check=False)
subprocess.run(['git', '-C', str(root), 'push', 'origin', 'master'], check=True)

# 3. Package patch archives
print("\n=== Step 3: Packaging Patch Archives for v3.35 ===")
CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat',
    'avatar_cache_service.py', 'plugin_manager.py'
]

EXTRA_FOLDERS = [
    ('docs', 'docs'),
    ('plugins', 'plugins')
]

patches_dir = root / 'patches'
patches_dir.mkdir(exist_ok=True)

patch_lite = patches_dir / 'patch-v3.35-lite.zip'
patch_full = patches_dir / 'patch-v3.35-full.zip'
dist_src = root / 'dist'

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
        for f in CORE_PYTHON_FILES:
            sf = root / f
            if sf.exists():
                z.write(sf, f)
                z.write(sf, f'_internal/{f}')
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

changelog = """# Broadcast Playroom v3.35

### รายละเอียดการอัปเดตเวอร์ชัน 3.35:
- **ระบบความปลอดภัยข้อมูลลับ OAuth (Encrypted Credential Protection)**:
  - เข้ารหัสและซ่อนค่า Client Secret / Client ID ทั้งหมดในระดับไบนารี ป้องกันการเปิดอ่านเป็นข้อความดิบ
  - ลบโค้ดบันทึกค่า Secret ลง Windows Registry เพื่อความปลอดภัยสูงสุด
  - ระบบล้างโฟลเดอร์ทดสอบเก่าอัตโนมัติเมื่อกดอัปเดต ป้องกันการตกค้างของไฟล์สคริปต์เดิม
- **วางรากฐานระบบปลั๊กอิน (Plugin System Foundation)**:
  - เพิ่ม `plugin_manager.py` สถาปัตยกรรมรองรับปลั๊กอินภายนอกแบบ Non-Invasive (ไม่กระทบการทำงานเดิม 100%)
  - กำหนดพื้นที่ปลั๊กอินใน `data/plugins/` อย่างเป็นสัดส่วน อัปเดตโปรแกรมหลักไฟล์ปลั๊กอินไม่สูญหาย
  - เพิ่มระบบตรวจจับความปลอดภัย **Creator Attribution & Tamper Guard** ป้องกันปลั๊กอินแก้ไขหรือซ่อนหน้าต่างสนับสนุนผู้พัฒนา (`support_modal`, QR Code โดเนท)
  - เพิ่มคู่มือสำหรับนักพัฒนาและ AI: `docs/AI_PLUGIN_GUIDE.md`
  - เพิ่มโฟลเดอร์แม่แบบตัวอย่าง: `plugins/_starter_template/`
- **ระบบผสานคอนฟิกและฐานข้อมูลคนดู**:
  - คงระบบ Deep Merge และ User Manager บันทึกข้อมูลคนดูจริง ไม่หายเมื่ออัปเดต
"""

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.35",
    "latest_version": "3.35",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.35/patch-v3.35-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.35-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.35/patch-v3.35-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.35-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.35",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.35/patch-v3.35-lite.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.35-lite.zip"
            ],
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.35",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.35/patch-v3.35-full.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.35-full.zip"
            ],
            "patch_sha256": hash_full,
            "patch_size": patch_full.stat().st_size
        }
    }
}

manifest_file = root / 'version.json'
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Saved updated version.json manifest for v3.35.")

# Clean pending_update cache directory
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
        except OSError:
            pass

# 4. Publish to GitHub Releases v3.35
print("\n=== Step 4: Publishing to GitHub Releases v3.35 ===")
notes_file = root / "scratch" / "release_notes_v335.md"
notes_file.parent.mkdir(exist_ok=True)
notes_file.write_text(changelog, encoding='utf-8')

findupdate_bat = root / "FindUpdate.bat"
gh_cmd = [
    'gh', 'release', 'create', 'v3.35',
    str(patch_full),
    str(patch_lite),
    str(manifest_file),
    str(findupdate_bat),
    '--repo', 'zepiam/broadcast-playroom-3',
    '--title', 'Broadcast Playroom v3.35',
    '--notes-file', str(notes_file)
]
res = subprocess.run(gh_cmd, cwd=root, capture_output=True, text=True)
if res.returncode != 0:
    print(f"gh release create notice: {res.stderr.strip()}")
    subprocess.run(['gh', 'release', 'upload', 'v3.35', str(patch_full), str(patch_lite), str(manifest_file), str(findupdate_bat), '--repo', 'zepiam/broadcast-playroom-3', '--clobber'], cwd=root, check=True)
    subprocess.run(['gh', 'release', 'edit', 'v3.35', '--repo', 'zepiam/broadcast-playroom-3', '--notes-file', str(notes_file)], cwd=root, check=False)
else:
    print(f"  [OK] GitHub Release v3.35 created successfully: {res.stdout.strip()}")

# 5. Upload to HuggingFace repository (men9ch/broadcast-playroom-3)
print("\n=== Step 5: Uploading v3.35 Patches to Hugging Face ===")
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"

# Upload patch-v3.35-full.zip
api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo="patches/patch-v3.35-full.zip",
    repo_id=repo_id,
    commit_message="Release v3.35: patch-v3.35-full.zip"
)
print("  [OK] Uploaded patch-v3.35-full.zip to HuggingFace.")

# Upload patch-v3.35-lite.zip
api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo="patches/patch-v3.35-lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.35: patch-v3.35-lite.zip"
)
print("  [OK] Uploaded patch-v3.35-lite.zip to HuggingFace.")

# Upload version.json manifest
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="patches/version.json",
    repo_id=repo_id,
    commit_message="Release v3.35: patches/version.json manifest"
)
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="version.json",
    repo_id=repo_id,
    commit_message="Release v3.35: root version.json manifest"
)
print("  [OK] Uploaded version.json to HuggingFace.")

print("\n>>> ALL STEPS COMPLETED: RELEASE v3.35 LIVE ON GITHUB & HUGGINGFACE! <<<")
print("NOTE: As requested, local directory E:\\DOCS\\Documents\\BroadcastPlayroom3\\full was NOT modified.")
