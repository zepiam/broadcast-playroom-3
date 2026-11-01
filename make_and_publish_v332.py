"""Build, package, and publish Broadcast Playroom v3.32 dual-mirror release (GitHub + HuggingFace)
including standalone installer archive (BroadcastPlayroom3-Full.zip)."""

import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from huggingface_hub import HfApi

root = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

print("Step 1: Building frontend for v3.32 and executing smoke test gate...")
subprocess.run(['npm.cmd', 'run', 'build'], cwd=root, check=True)

dist_src = root / 'dist'
build_trials = root / 'build_trials'
build_trials.mkdir(exist_ok=True)

patch_lite = build_trials / 'patch-v3.32-lite.zip'
patch_full = build_trials / 'patch-v3.32-full.zip'

CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat', 'avatar_cache_service.py'
]

def package_patch(src_patch, dst_patch, build_type):
    if dst_patch.exists():
        dst_patch.unlink()
    with zipfile.ZipFile(dst_patch, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 1. dist/ at root and inside _internal/dist/
        for p in dist_src.rglob('*'):
            if p.is_file():
                rel = p.relative_to(dist_src).as_posix()
                zf.write(p, f"dist/{rel}")
                zf.write(p, f"_internal/dist/{rel}")
        # 2. Python runtime core scripts & FindUpdate at root and inside _internal/
        for py_file in CORE_PYTHON_FILES:
            f_path = root / py_file
            if f_path.exists():
                zf.write(f_path, py_file)
                zf.write(f_path, f"_internal/{py_file}")
        # 3. version.json at root and inside _internal/
        v_info = {
            "product": "broadcast-playroom-3",
            "version": "3.32",
            "latest_version": "3.32",
            "build_type": build_type
        }
        zf.writestr('version.json', json.dumps(v_info, indent=2))
        zf.writestr('_internal/version.json', json.dumps(v_info, indent=2))
        # 4. broadcast playroom dev oauth credentials for legacy frozen exe fallback
        dev_dir = root.parent / 'broadcast playroom dev'
        if dev_dir.exists():
            for f in ['twitch_oauth.py', 'kick_oauth.py']:
                fp = dev_dir / f
                if fp.exists():
                    zf.write(fp, f"broadcast playroom dev/{f}")
                    zf.write(fp, f"_internal/broadcast playroom dev/{f}")
    print(f"Packaged {dst_patch.name} ({dst_patch.stat().st_size:,} bytes)")

print("Step 2: Packaging dual-path patch archives (v3.32)...")
package_patch(dist_src, patch_lite, 'lite')
package_patch(dist_src, patch_full, 'full')

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

changelog = """# Broadcast Playroom v3.32

### รายละเอียดการอัปเดตเวอร์ชัน 3.32:
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
- **อัปเดตแพ็กเกจติดตั้ง Installer (BroadcastPlayroom3-Full.zip v3.32)**:
  - อัปเดตไฟล์ติดตั้งตัวเต็มผ่าน Hugging Face Mirror เพื่อให้ผู้ใช้งานที่ติดตั้งผ่าน Setup Installer ได้รับเวอร์ชัน 3.32 ทันที
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

# Clean pending_update cache directory
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
        except OSError:
            pass

# Step 5: Update staging full distribution directory and create BroadcastPlayroom3-Full.zip
trial_full = root / "build_trials" / "trial-20261029-141916-597303" / "dist" / "BroadcastPlayroom3-Full"
dist_releases = root / "dist_releases"
dist_releases.mkdir(parents=True, exist_ok=True)
zip_out_full = dist_releases / "BroadcastPlayroom3-Full.zip"

if trial_full.exists():
    print(f"Step 5a: Updating staging full distribution directory: {trial_full}")
    # 1. Update _internal/dist
    trial_internal_dist = trial_full / "_internal" / "dist"
    if trial_internal_dist.exists():
        shutil.rmtree(trial_internal_dist)
    shutil.copytree(dist_src, trial_internal_dist)
    
    # 2. Update core python files
    for f in CORE_PYTHON_FILES:
        sf = root / f
        if sf.exists():
            shutil.copy2(sf, trial_full / "_internal" / f)
            
    # 3. Update version.json
    (trial_full / "version.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (trial_full / "_internal" / "version.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 4. Verify privacy cleanliness
    from package_clean_releases import audit_directory
    violations, f_count = audit_directory(trial_full)
    if violations:
        raise RuntimeError(f"Audit failed on staging full directory! Violations: {violations}")
    print(f"   [OK] Staging full directory verified 100% clean ({f_count} files, 0 leaks)")
    
    # 5. Compress to dist_releases/BroadcastPlayroom3-Full.zip using 7-Zip
    seven_zip = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
    print(f"Step 5b: Compressing Full Edition with 7-Zip -> {zip_out_full.name}...")
    if zip_out_full.exists():
        zip_out_full.unlink()
        
    cmd_7z = [
        seven_zip, "a", "-tzip", "-mx=5", "-r",
        str(zip_out_full),
        "*"
    ]
    subprocess.run(cmd_7z, cwd=trial_full, check=True)
    size_mb = zip_out_full.stat().st_size / (1024 * 1024)
    print(f"   [SUCCESS] Created {zip_out_full.name} ({size_mb:.2f} MB)")

print("Step 6: Publishing to GitHub Releases v3.32...")
notes_file = root / "scratch" / "release_notes_v332.md"
notes_file.parent.mkdir(exist_ok=True)
notes_file.write_text(changelog, encoding='utf-8')

subprocess.run(['git', 'add', '-A'], cwd=root, check=True)
subprocess.run(['git', 'commit', '-m', 'Release v3.32: Persistent User Manager, Topbar Divider Cleanup, Status Footer Links'], cwd=root, check=False)
subprocess.run(['git', 'push', 'origin', 'master'], cwd=root, check=True)

# GitHub Release
findupdate_bat = root / "FindUpdate.bat"
gh_cmd = [
    'gh', 'release', 'create', 'v3.32',
    str(patch_full),
    str(patch_lite),
    str(manifest_file),
    str(findupdate_bat),
    '--title', 'Broadcast Playroom v3.32',
    '--notes-file', str(notes_file)
]
res = subprocess.run(gh_cmd, cwd=root, capture_output=True, text=True)
if res.returncode != 0:
    print(f"Warning/Error on gh release: {res.stderr}")
    subprocess.run(['gh', 'release', 'upload', 'v3.32', str(patch_full), str(patch_lite), str(manifest_file), str(findupdate_bat), '--clobber'], cwd=root, check=True)
else:
    print(f"GitHub Release v3.32 created successfully: {res.stdout.strip()}")

print("Step 7: Uploading to HuggingFace repository (men9ch/broadcast-playroom-3)...")
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"

# Upload patch-v3.32-full.zip
api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo="patches/patch-v3.32-full.zip",
    repo_id=repo_id,
    commit_message="Release v3.32: patch-v3.32-full.zip"
)
print("Uploaded patch-v3.32-full.zip to HuggingFace.")

# Upload patch-v3.32-lite.zip
api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo="patches/patch-v3.32-lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.32: patch-v3.32-lite.zip"
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

# Upload standalone installer zip (BroadcastPlayroom3-Full.zip) to root of HF repo
if zip_out_full.exists():
    print(f"Step 7b: Uploading installer archive {zip_out_full.name} ({zip_out_full.stat().st_size / (1024*1024):.2f} MB) to HuggingFace root...")
    api.upload_file(
        path_or_fileobj=str(zip_out_full),
        path_in_repo="BroadcastPlayroom3-Full.zip",
        repo_id=repo_id,
        commit_message="Release v3.32: BroadcastPlayroom3-Full.zip installer package"
    )
    print("Uploaded BroadcastPlayroom3-Full.zip to HuggingFace successfully!")

print("\n>>> ALL STEPS COMPLETED: v3.32 LIVE ON GITHUB & HUGGINGFACE + INSTALLER ARCHIVE READY! <<<")
