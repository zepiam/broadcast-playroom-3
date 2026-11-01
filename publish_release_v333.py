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

# 1. Bump version numbers in source files
print("=== Step 1: Bumping Version to 3.33 ===")
updater_file = root / "updater.py"
u_txt = updater_file.read_text(encoding='utf-8')
u_txt = u_txt.replace('CURRENT_VERSION = "3.32"', 'CURRENT_VERSION = "3.33"', 1)
updater_file.write_text(u_txt, encoding='utf-8')

pkg_file = root / "package.json"
p_txt = pkg_file.read_text(encoding='utf-8')
p_txt = p_txt.replace('"version": "3.32"', '"version": "3.33"', 1)
pkg_file.write_text(p_txt, encoding='utf-8')

html_file = root / "src" / "index.html"
h_txt = html_file.read_text(encoding='utf-8')
h_txt = h_txt.replace('<span class="desktop-titlebar-tag">v3.32</span>', '<span class="desktop-titlebar-tag">v3.33</span>', 1)
html_file.write_text(h_txt, encoding='utf-8')
print("  [OK] Version bumped to 3.33 in updater.py, package.json, and src/index.html")

# 2. Build frontend dist
print("\n=== Step 2: Building Frontend Dist ===")
subprocess.run(['npm.cmd', '--prefix', str(root), 'run', 'build'], check=True)

# 3. Commit and push to git
print("\n=== Step 3: Git Commit & Push v3.33 ===")
subprocess.run(['git', '-C', str(root), 'add', '-A'], check=True)
subprocess.run(['git', '-C', str(root), 'commit', '-m', 'Release v3.33: Translate Mode Persistence Across Program Restarts'], check=False)
subprocess.run(['git', '-C', str(root), 'push', 'origin', 'master'], check=True)

# 4. Package patch archives
print("\n=== Step 4: Packaging Patch Archives for v3.33 ===")
CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat', 'avatar_cache_service.py'
]

patches_dir = root / 'patches'
patches_dir.mkdir(exist_ok=True)

patch_lite = patches_dir / 'patch-v3.33-lite.zip'
patch_full = patches_dir / 'patch-v3.33-full.zip'
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
    print(f"  [OK] Created {out_zip.name} ({out_zip.stat().st_size / (1024*1024):.2f} MB)")

make_patch(patch_lite, is_full=False)
make_patch(patch_full, is_full=True)

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

changelog = """# Broadcast Playroom v3.33

### รายละเอียดการอัปเดตเวอร์ชัน 3.33:
- **จดจำการตั้งค่าโหมดแปลภาษา (Translate Mode Persistence)**:
  - แก้ไขปุ่ม แปลภาษา / อ่านทุกภาษา ให้บันทึกการตั้งค่าลงเครื่องอย่างถาวร ปิดเปิดโปรแกรมใหม่ไม่คืนค่า
  - ซิงค์สถานะระหว่างหน้าเว็บหลักและระบบเซิร์ฟเวอร์แบบ Real-time ทันทีที่กดเปลี่ยนโหมด
  - กู้คืนสถานะโหมดล่าสุดทันทีที่เปิดโปรแกรมโดยไม่มีความหน่วง (Zero Delay UI Restore)
- **ฐานข้อมูลคนดูถาวร (User Manager Local Disk Persistence)**:
  - เชื่อมต่อการบันทึกรายชื่อคนดูลงฮาร์ดดิสก์จริง (`data/user_roster.json`) ผ่านระบบ API `/api/user-roster`
  - ข้อมูลคนดู (ชื่อ, แพลตฟอร์ม, รูปโปรไฟล์, จำนวนข้อความ, ประวัติแชท, สถานะ VIP/บล็อก) จะคงอยู่อย่างถาวรแม้ปิดหรือรีสตาร์ตโปรแกรม
  - รองรับการแสดงผลและนับจำนวนคนดูแบบเรียลไทม์ครบทุกแท็บ (ทั้งหมด, 🌟 ผู้สนับสนุน, 🛑 ถูกบล็อก, 🟢 ล่าสุด)
  - เพิ่มระบบสำรองและกู้คืนอัตโนมัติใน `updater.py` ทำให้เวลาอัปเดตเวอร์ชันใหม่ในอนาคต ข้อมูลรายชื่อคนดูจะไม่สูญหาย
  - วางระบบ Strict Isolation Gatekeeper บล็อกข้อความจากปุ่มทดสอบ, แชทจำลอง, และข้อความที่สตรีมเมอร์พิมพ์เอง ไม่ให้เข้าสู่ฐานข้อมูลคนดู บันทึกเฉพาะคนดูจริงจาก Live Stream เท่านั้น
- **ปรับแต่งแถบเมนูด้านบน (Topbar Cleanup)**:
  - นำตัวคั่น `|` ที่อยู่ขวามือถัดจากปุ่ม แปลภาษา, Overlay, Game Overlay ออกเพื่อความเรียบร้อยและสะอาดตา
- **เพิ่มแถบลิงก์ทางลัดด้านล่างขวา (Status Footer Quick Links)**:
  - เพิ่มลิงก์: `เว็บไซต์ | แจ้งบัค | สนับสนุนการพัฒนาโปรแกรม` พร้อมเส้นคั่นสีเทาบางๆ
  - ลิงก์ `เว็บไซต์` เปิด `https://www.men9ch.com`
  - ลิงก์ `แจ้งบัค` เปิด Discord Support `https://discord.gg/nj4KNs6b92`
  - ลิงก์ `สนับสนุนการพัฒนาโปรแกรม` เปิดหน้าต่างสนับสนุนในโปรแกรม
"""

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.33",
    "latest_version": "3.33",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.33/patch-v3.33-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.33-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.33/patch-v3.33-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.33-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.33",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.33/patch-v3.33-lite.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.33-lite.zip"
            ],
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.33",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.33/patch-v3.33-full.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.33-full.zip"
            ],
            "patch_sha256": hash_full,
            "patch_size": patch_full.stat().st_size
        }
    }
}

manifest_file = root / 'version.json'
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("  [OK] Saved updated version.json manifest for v3.33.")

# 5. Update local installed full directory
dst_full = Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full")
if dst_full.exists():
    for f in CORE_PYTHON_FILES:
        sf = root / f
        if sf.exists():
            shutil.copy2(sf, dst_full / f)
            if (dst_full / '_internal').exists():
                shutil.copy2(sf, dst_full / '_internal' / f)
    for p in dist_src.rglob('*'):
        if p.is_file():
            rel = p.relative_to(dist_src)
            out1 = dst_full / 'dist' / rel
            out1.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out1)
            if (dst_full / '_internal').exists():
                out2 = dst_full / '_internal' / 'dist' / rel
                out2.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out2)
    (dst_full / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    if (dst_full / '_internal').exists():
        (dst_full / '_internal' / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print("  [OK] Updated local full installation directory with v3.33 files.")

# Clean pending_update cache directory
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
        except OSError:
            pass

# 6. Publish to GitHub Releases v3.33
print("\n=== Step 5: Publishing to GitHub Releases v3.33 ===")
notes_file = root / "scratch" / "release_notes_v333.md"
notes_file.parent.mkdir(exist_ok=True)
notes_file.write_text(changelog, encoding='utf-8')

findupdate_bat = root / "FindUpdate.bat"
gh_cmd = [
    'gh', 'release', 'create', 'v3.33',
    str(patch_full),
    str(patch_lite),
    str(manifest_file),
    str(findupdate_bat),
    '--repo', 'zepiam/broadcast-playroom-3',
    '--title', 'Broadcast Playroom v3.33',
    '--notes-file', str(notes_file)
]
res = subprocess.run(gh_cmd, cwd=root, capture_output=True, text=True)
if res.returncode != 0:
    print(f"gh release create notice: {res.stderr.strip()}")
    # Upload with clobber if exists
    subprocess.run(['gh', 'release', 'upload', 'v3.33', str(patch_full), str(patch_lite), str(manifest_file), str(findupdate_bat), '--repo', 'zepiam/broadcast-playroom-3', '--clobber'], cwd=root, check=True)
    subprocess.run(['gh', 'release', 'edit', 'v3.33', '--repo', 'zepiam/broadcast-playroom-3', '--notes-file', str(notes_file)], cwd=root, check=False)
else:
    print(f"  [OK] GitHub Release v3.33 created successfully: {res.stdout.strip()}")

# 7. Upload to HuggingFace repository (men9ch/broadcast-playroom-3)
print("\n=== Step 6: Uploading v3.33 Patches to Hugging Face ===")
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"

# Upload patch-v3.33-full.zip
api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo="patches/patch-v3.33-full.zip",
    repo_id=repo_id,
    commit_message="Release v3.33: patch-v3.33-full.zip"
)
print("  [OK] Uploaded patch-v3.33-full.zip to HuggingFace.")

# Upload patch-v3.33-lite.zip
api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo="patches/patch-v3.33-lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.33: patch-v3.33-lite.zip"
)
print("  [OK] Uploaded patch-v3.33-lite.zip to HuggingFace.")

# Upload version.json manifest
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="patches/version.json",
    repo_id=repo_id,
    commit_message="Release v3.33: patches/version.json manifest"
)
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="version.json",
    repo_id=repo_id,
    commit_message="Release v3.33: root version.json manifest"
)
print("  [OK] Uploaded version.json to HuggingFace.")

print("\n>>> ALL STEPS COMPLETED: RELEASE v3.33 LIVE ON GITHUB & HUGGINGFACE! <<<")
