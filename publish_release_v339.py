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

# 1. Confirm version 3.39
print("=== Step 1: Confirming Version 3.39 ===")
updater_file = root / "updater.py"
u_txt = updater_file.read_text(encoding='utf-8')
assert 'CURRENT_VERSION = "3.39"' in u_txt, "updater.py version mismatch"

pkg_file = root / "package.json"
p_txt = pkg_file.read_text(encoding='utf-8')
assert '"version": "3.39"' in p_txt, "package.json version mismatch"

html_file = root / "src" / "index.html"
h_txt = html_file.read_text(encoding='utf-8')
assert '<span class="desktop-titlebar-tag">v3.39</span>' in h_txt, "src/index.html version mismatch"
print("  [OK] Version 3.39 confirmed across all files.")

# 2. Package patch archives
print("\n=== Step 2: Packaging Patch Archives for v3.39 ===")
CORE_FILES = [
    'version.json',
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

patch_lite = patches_dir / 'patch-v3.39-lite.zip'
patch_full = patches_dir / 'patch-v3.39-full.zip'
dist_src = root / 'dist'

changelog = """# Broadcast Playroom v3.39

### รายละเอียดการอัปเดตเวอร์ชัน 3.39:
- **แก้ไขและเพิ่มระบบ Self-Healing Version Tag & Sync**:
  - บรรจุ `version.json` และ `_internal/version.json` เข้าในไฟล์แพตช์อย่างเป็นทางการ เพื่อให้อัปเดตและแสดงเวอร์ชันถูกต้องทันทีหลังแตกไฟล์
  - เพิ่มระบบตรวจจับและซิงค์เวอร์ชันอัตโนมัติ (Self-Healing) ใน `updater.py` หากพบว่าตัวเลขในไฟล์บนเครื่องเก่ากว่าโค้ดที่รันจริง ระบบจะอัปเดตไฟล์ให้ตรงกับเวอร์ชันปัจจุบันทันที ไม่ค้างอยู่ที่เลขเวอร์ชันเดิม
- **ปรับปรุงหน้าต่างโปรไฟล์คนดู (Spacious Viewer Profile Modal Layout)**:
  - ขยายขนาดหน้าต่างเริ่มต้นเป็น 780x800 พิกเซล ทั้งโหมดหน้าต่างลอยและ Popout อิสระ
  - กฎการบล็อก (Block Rules) ทั้งหมดแสดงผลครบถ้วน ชัดเจน 100% ไม่ถูกตัดขอบหรือบีบแคบ
  - พื้นที่ประวัติแชท ประวัติกิจกรรม และโน้ตความจำ กว้างขวางอ่านง่ายตั้งแต่แรกเปิด ไม่ต้องลากขยายหน้าต่างเอง
- **ปรับปรุงระบบ TTS Idle และข้อความแจ้งเตือนเสียงสำรอง**:
  - ลบ TCP socket probe เพื่อป้องกัน Microsoft Bing WAF ตัดการเชื่อมต่อเมื่อเปิดทิ้งไว้นาน
  - อัปเดตข้อความ Tooltip เป็น *"ใช้เสียงสำรองของระบบ (TTS ออนไลน์ไม่ตอบสนองชั่วคราว)"*
"""

manifest_file = root / 'version.json'
manifest_data_pre = {
    "product": "broadcast-playroom-3",
    "version": "3.39",
    "latest_version": "3.39",
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
    "version": "3.39",
    "latest_version": "3.39",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.39/patch-v3.39-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.39-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.39/patch-v3.39-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.39-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.39",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.39/patch-v3.39-lite.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.39-lite.zip"
            ],
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.39",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.39/patch-v3.39-full.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.39-full.zip"
            ],
            "patch_sha256": hash_full,
            "patch_size": patch_full.stat().st_size
        }
    }
}

manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Saved final version.json manifest for v3.39.")

# Repack patch archives to include the final version.json!
make_patch(patch_lite, is_full=False)
make_patch(patch_full, is_full=True)
manifest["lite"]["sha256"] = digest(patch_lite)
manifest["lite"]["size"] = patch_lite.stat().st_size
manifest["full"]["sha256"] = digest(patch_full)
manifest["full"]["size"] = patch_full.stat().st_size
manifest["packages"]["lite"]["patch_sha256"] = manifest["lite"]["sha256"]
manifest["packages"]["lite"]["patch_size"] = manifest["lite"]["size"]
manifest["packages"]["full"]["patch_sha256"] = manifest["full"]["sha256"]
manifest["packages"]["full"]["patch_size"] = manifest["full"]["size"]
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Re-verified hashes with version.json inside.")

# Clean pending_update cache directory
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
        except OSError:
            pass

# 3. Commit and push to git
print("\n=== Step 3: Git Commit & Push v3.39 ===")
subprocess.run(['git', '-C', str(root), 'add', '-A'], check=True)
subprocess.run(['git', '-C', str(root), 'commit', '-m', 'Release v3.39: Self-Healing Version Tag Sync & Packaging Fix'], check=False)
subprocess.run(['git', '-C', str(root), 'push', 'origin', 'master'], check=True)

# 4. Publish to GitHub Releases v3.39
print("\n=== Step 4: Publishing to GitHub Releases v3.39 ===")
notes_file = root / "scratch" / "release_notes_v339.md"
notes_file.parent.mkdir(exist_ok=True)
notes_file.write_text(changelog, encoding='utf-8')

findupdate_bat = root / "FindUpdate.bat"
gh_cmd = [
    'gh', 'release', 'create', 'v3.39',
    str(patch_full),
    str(patch_lite),
    str(manifest_file),
    str(findupdate_bat),
    '--repo', 'zepiam/broadcast-playroom-3',
    '--title', 'Broadcast Playroom v3.39',
    '--notes-file', str(notes_file)
]
res = subprocess.run(gh_cmd, cwd=root, capture_output=True, text=True)
if res.returncode != 0:
    print(f"gh release create notice: {res.stderr.strip()}")
    subprocess.run(['gh', 'release', 'upload', 'v3.39', str(patch_full), str(patch_lite), str(manifest_file), str(findupdate_bat), '--repo', 'zepiam/broadcast-playroom-3', '--clobber'], cwd=root, check=True)
    subprocess.run(['gh', 'release', 'edit', 'v3.39', '--repo', 'zepiam/broadcast-playroom-3', '--notes-file', str(notes_file)], cwd=root, check=False)
else:
    print(f"  [OK] GitHub Release v3.39 created successfully: {res.stdout.strip()}")

# 5. Upload to HuggingFace repository (men9ch/broadcast-playroom-3)
print("\n=== Step 5: Uploading v3.39 Patches to Hugging Face ===")
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"

# Upload patch-v3.39-full.zip
api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo="patches/patch-v3.39-full.zip",
    repo_id=repo_id,
    commit_message="Release v3.39: patch-v3.39-full.zip"
)
print("  [OK] Uploaded patch-v3.39-full.zip to HuggingFace.")

# Upload patch-v3.39-lite.zip
api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo="patches/patch-v3.39-lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.39: patch-v3.39-lite.zip"
)
print("  [OK] Uploaded patch-v3.39-lite.zip to HuggingFace.")

# Upload version.json manifest
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="patches/version.json",
    repo_id=repo_id,
    commit_message="Release v3.39: patches/version.json manifest"
)
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="version.json",
    repo_id=repo_id,
    commit_message="Release v3.39: root version.json manifest"
)
print("  [OK] Uploaded version.json to HuggingFace.")

print("\n>>> ALL STEPS COMPLETED: RELEASE v3.39 LIVE ON GITHUB & HUGGINGFACE! <<<")
