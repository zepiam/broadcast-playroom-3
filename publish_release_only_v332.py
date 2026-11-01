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

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

print("Step 1: Building frontend dist...")
subprocess.run(['npm.cmd', '--prefix', str(root), 'run', 'build'], check=True)

CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat', 'avatar_cache_service.py'
]

patches_dir = root / 'patches'
patches_dir.mkdir(exist_ok=True)

patch_lite = patches_dir / 'patch-v3.32-lite.zip'
patch_full = patches_dir / 'patch-v3.32-full.zip'
dist_src = root / 'dist'

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
    print(f"Created {out_zip.name} ({out_zip.stat().st_size / (1024*1024):.2f} MB)")

print("Step 2: Packaging patch archives...")
make_patch(patch_lite, is_full=False)
make_patch(patch_full, is_full=True)

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

changelog = """# Broadcast Playroom v3.32

### รายละเอียดการอัปเดตเวอร์ชัน 3.32:
- **จดจำการตั้งค่าโหมดแปลภาษา (Translate Mode Persistence)**:
  - แก้ไขปุ่ม แปลภาษา / อ่านทุกภาษา ให้บันทึกการตั้งค่าลงเครื่องอย่างถาวร ปิดเปิดโปรแกรมใหม่ไม่คืนค่า
  - ซิงค์สถานะระหว่างหน้าเว็บหลักและระบบเซิร์ฟเวอร์แบบ Real-time ทันทีที่กดเปลี่ยนโหมด
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
    "version": "3.32",
    "latest_version": "3.32",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.32/patch-v3.32-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.32-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.32/patch-v3.32-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.32-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.32",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.32/patch-v3.32-lite.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.32-lite.zip"
            ],
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.32",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.32/patch-v3.32-full.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.32-full.zip"
            ],
            "patch_sha256": hash_full,
            "patch_size": patch_full.stat().st_size
        }
    }
}

manifest_file = root / 'version.json'
manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("Step 3: Saved updated version.json manifest.")

# Update installed full directory
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
    print("Step 4: Updated local full installation directory with v3.32 files.")

print("Step 5: Publishing to GitHub Releases v3.32...")
notes_file = root / "scratch" / "release_notes_v332.md"
notes_file.parent.mkdir(exist_ok=True)
notes_file.write_text(changelog, encoding='utf-8')

# GitHub Release upload
findupdate_bat = root / "FindUpdate.bat"
gh_cmd = [
    'gh', 'release', 'upload', 'v3.32',
    str(patch_full),
    str(patch_lite),
    str(manifest_file),
    str(findupdate_bat),
    '--repo', 'zepiam/broadcast-playroom-3',
    '--clobber'
]
res = subprocess.run(gh_cmd, cwd=root, capture_output=True, text=True)
if res.returncode != 0:
    print(f"Warning/Error on gh release upload: {res.stderr}")
else:
    print("GitHub Release v3.32 assets updated successfully.")

subprocess.run(['gh', 'release', 'edit', 'v3.32', '--repo', 'zepiam/broadcast-playroom-3', '--notes-file', str(notes_file)], cwd=root, check=False)

print("Step 6: Uploading patches to HuggingFace repository (men9ch/broadcast-playroom-3)...")
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"

# Upload patch-v3.32-full.zip
api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo="patches/patch-v3.32-full.zip",
    repo_id=repo_id,
    commit_message="Release v3.32: patch-v3.32-full.zip (translate mode persistence)"
)
print("Uploaded patch-v3.32-full.zip to HuggingFace.")

# Upload patch-v3.32-lite.zip
api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo="patches/patch-v3.32-lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.32: patch-v3.32-lite.zip (translate mode persistence)"
)
print("Uploaded patch-v3.32-lite.zip to HuggingFace.")

# Upload version.json manifest
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="patches/version.json",
    repo_id=repo_id,
    commit_message="Release v3.32: patches/version.json manifest"
)
api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="version.json",
    repo_id=repo_id,
    commit_message="Release v3.32: root version.json manifest"
)
print("Uploaded version.json to HuggingFace.")

print("\n>>> ALL STEPS COMPLETED: RELEASE v3.32 LIVE ON GITHUB & HUGGINGFACE! <<<")
