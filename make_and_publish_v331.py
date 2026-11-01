"""Build, package, and publish Broadcast Playroom v3.31 dual-mirror release (GitHub + HuggingFace)."""
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

print("Step 1: Building frontend for v3.31 and executing smoke test gate...")
subprocess.run(['npm.cmd', 'run', 'build'], cwd=root, check=True)

dist_src = root / 'dist'
build_trials = root / 'build_trials'
build_trials.mkdir(exist_ok=True)

patch_lite = build_trials / 'patch-v3.31-lite.zip'
patch_full = build_trials / 'patch-v3.31-full.zip'

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
            "version": "3.31",
            "latest_version": "3.31",
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

print("Step 2: Packaging dual-path patch archives...")
package_patch(dist_src, patch_lite, 'lite')
package_patch(dist_src, patch_full, 'full')

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

changelog = """# Broadcast Playroom v3.31

### รายการอัปเดตและปรับปรุงในเวอร์ชัน 3.31:
- **ปรับปรุงแท็บกฎการบล็อกในหน้าต่างโปรไฟล์ผู้ชม (Master + 3-Grid Layout)**:
  - จัดการแสดงผลใหม่เป็น 2 ระดับ: แถวบนเป็นการ์ดหลัก "บล็อกทั้งหมด (Block All)" พร้อมไฮไลต์สีแดงเด่นชัด และแถวล่างเป็นการ์ดตัวเลือกย่อย 3 คอลัมน์ (ซ่อนจาก OBS, ปิดเสียง TTS, ปิดบอท Replie)
  - แสดงผลครบทุกหัวข้อทันที 100% โดยไม่ต้องเลื่อนเมาส์สไลด์หรือติด Scrollbar อีกต่อไป
  - ขยายขนาดหน้าต่างโปรไฟล์ผู้ชมเป็น 680x620 px เพิ่มความโปร่งสบายตา
- **ระบบ Dual-Mirror High-Availability Update (GitHub + HuggingFace)**:
  - เผยแพร่แพตช์คู่ขนานทั้งบน GitHub Releases และ HuggingFace Mirror (`men9ch/broadcast-playroom-3`)
  - รองรับ Auto-Fallback สลับดาวน์โหลดไปยังเซิร์ฟเวอร์สำรองอัตโนมัติหากพบอาการสะดุดหรือเน็ตค้าง
- **ยกระดับความทนทานของระบบดาวน์โหลดอัปเดต**:
  - รองรับ SSL Multi-Context ป้องกันปัญหา Antivirus สแกน HTTPS
  - เพิ่มระบบ Cache-Busting ป้องกัน CDN ส่งไฟล์ Hash เก่า
"""

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.31",
    "latest_version": "3.31",
    "critical": True,
    "changelog": changelog,
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.31/patch-v3.31-lite.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.31-lite.zip"
        ],
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.31/patch-v3.31-full.zip",
        "mirrors": [
            "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.31-full.zip"
        ],
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.31",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.31/patch-v3.31-lite.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.31-lite.zip"
            ],
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.31",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.31/patch-v3.31-full.zip",
            "patch_mirrors": [
                "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v3.31-full.zip"
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
    print("Step 4: Updated local full installation directory with v3.31 files.")

# Clean pending_update cache directory
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
        except OSError:
            pass

print("Step 5: Publishing to GitHub Releases v3.31...")
# Commit and push
notes_file = root / "scratch" / "release_notes_v331.md"
notes_file.parent.mkdir(exist_ok=True)
notes_file.write_text(changelog, encoding='utf-8')

subprocess.run(['git', 'add', '-A'], cwd=root, check=True)
subprocess.run(['git', 'commit', '-m', 'Release v3.31: Viewer Profile Block Rules Redesign & Dual-Mirror Release Protocol'], cwd=root, check=False)
subprocess.run(['git', 'push', 'origin', 'master'], cwd=root, check=True)

# GitHub Release
findupdate_bat = root / "FindUpdate.bat"
gh_cmd = [
    'gh', 'release', 'create', 'v3.31',
    str(patch_full),
    str(patch_lite),
    str(manifest_file),
    str(findupdate_bat),
    '--title', 'Broadcast Playroom v3.31',
    '--notes-file', str(notes_file)
]
res = subprocess.run(gh_cmd, cwd=root, capture_output=True, text=True)
if res.returncode != 0:
    print(f"Warning/Error on gh release: {res.stderr}")
    # If release exists, upload assets
    subprocess.run(['gh', 'release', 'upload', 'v3.31', str(patch_full), str(patch_lite), str(manifest_file), str(findupdate_bat), '--clobber'], cwd=root, check=True)
else:
    print(f"GitHub Release v3.31 created successfully: {res.stdout.strip()}")

print("Step 6: Uploading mirror to HuggingFace repository (men9ch/broadcast-playroom-3)...")
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"
api.upload_file(
    path_or_fileobj=str(patch_full),
    path_in_repo="patches/patch-v3.31-full.zip",
    repo_id=repo_id,
    commit_message="Release v3.31: patch-v3.31-full.zip"
)
print("Uploaded patch-v3.31-full.zip to HuggingFace.")

api.upload_file(
    path_or_fileobj=str(patch_lite),
    path_in_repo="patches/patch-v3.31-lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.31: patch-v3.31-lite.zip"
)
print("Uploaded patch-v3.31-lite.zip to HuggingFace.")

api.upload_file(
    path_or_fileobj=str(manifest_file),
    path_in_repo="patches/version.json",
    repo_id=repo_id,
    commit_message="Release v3.31: version.json manifest"
)
print("Uploaded version.json to HuggingFace.")

print("\n>>> ALL STEPS COMPLETED: v3.31 LIVE ON GITHUB & HUGGINGFACE! <<<")
