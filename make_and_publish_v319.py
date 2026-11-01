import base64
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

root = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def gh(*args, **kwargs):
    return subprocess.check_output(['gh', *args], **kwargs).decode('utf-8')

print("--- Step 1: Bump version numbers to 3.19 ---")

# 1. package.json
pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '3.19'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')

# 2. updater.py
updater_path = root / 'updater.py'
upd_text = updater_path.read_text(encoding='utf-8')
upd_text = upd_text.replace('CURRENT_VERSION = "3.18"', 'CURRENT_VERSION = "3.19"')
updater_path.write_text(upd_text, encoding='utf-8')

# 3. src/index.html (titlebar tag)
idx_src = root / 'src/index.html'
idx_text = idx_src.read_text(encoding='utf-8')
idx_text = idx_text.replace('<span class="desktop-titlebar-tag">v3.18</span>', '<span class="desktop-titlebar-tag">v3.19</span>')
idx_src.write_text(idx_text, encoding='utf-8')

print("\n--- Step 2: Build frontend distribution ---")
subprocess.check_call(['npm', 'run', 'build'], cwd=str(root), shell=True)
if (root / 'sync_trial_frontend.py').exists():
    try:
        subprocess.check_call(['python', 'sync_trial_frontend.py'], cwd=str(root))
    except Exception as e:
        print("sync_trial_frontend warning:", e)

# Also sync to installed full directory
full_inst = Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full")
if (full_inst / "dist").exists():
    shutil.copytree(root / "dist", full_inst / "dist", dirs_exist_ok=True)
if (full_inst / "_internal" / "dist").exists():
    shutil.copytree(root / "dist", full_inst / "_internal" / "dist", dirs_exist_ok=True)
if (full_inst / "launch_dev.py").exists():
    shutil.copy2(root / "launch_dev.py", full_inst / "launch_dev.py")
if (full_inst / "_internal" / "launch_dev.py").exists():
    shutil.copy2(root / "launch_dev.py", full_inst / "_internal" / "launch_dev.py")
print("Synchronized dist and launch_dev.py to installed Full application directories.")

print("\n--- Step 3: Package dual-path (root + _internal) update patches ---")
dist_src = root / 'dist'
build_trials = root / 'build_trials'
build_trials.mkdir(exist_ok=True)

patch_lite = build_trials / 'patch-v3.19-lite.zip'
patch_full = build_trials / 'patch-v3.19-full.zip'

def package_patch(src_patch, dst_patch, build_type):
    if dst_patch.exists(): dst_patch.unlink()
    with zipfile.ZipFile(dst_patch, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 1. dist/ at root and inside _internal/dist/ for PyInstaller parity
        for p in dist_src.rglob('*'):
            if p.is_file():
                rel = p.relative_to(dist_src).as_posix()
                zf.write(p, f"dist/{rel}")
                zf.write(p, f"_internal/dist/{rel}")
        # 2. Python runtime core scripts at root and inside _internal/
        for py_file in ['launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py']:
            f_path = root / py_file
            if f_path.exists():
                zf.write(f_path, py_file)
                zf.write(f_path, f"_internal/{py_file}")
        # 3. version.json at root and inside _internal/
        v_info = {
            "product": "broadcast-playroom-3",
            "version": "3.19",
            "latest_version": "3.19",
            "build_type": build_type
        }
        zf.writestr('version.json', json.dumps(v_info, indent=2))
        zf.writestr('_internal/version.json', json.dumps(v_info, indent=2))
    print(f"Packaged {dst_patch.name} ({dst_patch.stat().st_size:,} bytes)")

package_patch(dist_src, patch_lite, 'lite')
package_patch(dist_src, patch_full, 'full')

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

changelog = """### Broadcast Playroom v3.19 Update Highlights

- **แก้ไขปุ่ม "ปิดหน้าต่าง" ให้กดปิดได้ 100% ทุกหน้าต่างแยก (Robust Window Close & Anti-Deadlock)**:
  - แก้ไขปัญหาปุ่ม "ปิดหน้าต่าง" ของหน้าต่างตั้งค่าระบบ, ตั้งค่าเสียงอ่าน, Replie Tools, ASK Tool, Quick Randomizer และ User Manager ที่เคยกดปิดไม่ลงหรือปิดติดๆ ดับๆ
  - ขจัดปัญหา Deadlock ระหว่างการเรียก fetch ปิดหน้าต่างกับการทำลายหน้าต่าง WebView2 โดยตอบกลับ HTTP ทันทีและทำลายหน้าต่างแบบ Asynchronous บน Thread แยก
  - ป้องกัน Cross-Thread Conflict ด้วย Safe Window Lock และส่ง Instance หน้าต่างตรงเข้า JS API Bridge
  - เพิ่ม Global Capture Click Interceptor ที่ระดับ Document ปิดหน้าต่างทันทีเมื่อกดปุ่มปิด
- **คลิกขวาปุ่มด้านบนแล้วเลือกตั้งค่า ไปยังแท็บที่เกี่ยวข้องทันที (Direct Section Deep-Linking)**:
  - เมื่อคลิกขวาที่ปุ่มด้านบน เช่น ปุ่ม "อ่านทุกภาษา / แปลภาษา" แล้วกด "⚙️ ตั้งค่าการแปลภาษา..." หน้าต่างตั้งค่าจะเปิดและสลับไปยังแท็บ "แปลภาษาแชทสด" โดยตรง ไม่ค้างอยู่ที่ "ช่องทางสตรีม"
  - รองรับการเปิดไปยังแท็บ OBS WebSocket, ผู้สนับสนุน และแท็บอื่นๆ จากทุกเมนูคลิกขวาอย่างแม่นยำ
- **Dual-Path Packaging & Version Manifest Parity**:
  - รองรับการอัปเดตแบบคู่ขนานทั้ง root และ `_internal/` ป้องกันการ rollback กลับเวอร์ชันเดิม
"""

manifest = {
    "version": "3.19",
    "latest_version": "3.19",
    "critical": False,
    "changelog": changelog.strip(),
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.19/patch-v3.19-lite.zip",
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.19/patch-v3.19-full.zip",
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.19",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.19/patch-v3.19-lite.zip",
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.19",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.19/patch-v3.19-full.zip",
            "patch_sha256": hash_full,
            "patch_size": patch_full.stat().st_size
        }
    }
}

print("\n--- Step 4: Publish GitHub Release v3.19 ---")
folder = root / 'build_trials/patch-publish-3.19'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

# Check if release v3.19 exists or create it
try:
    gh('release', 'view', 'v3.19', '--repo', 'zepiam/broadcast-playroom-3')
    print("Release v3.19 already exists, uploading assets...")
except Exception:
    print("Creating new GitHub Release v3.19...")
    gh('release', 'create', 'v3.19', '--title', 'Broadcast Playroom v3.19', '--notes-file', str(notes), '--repo', 'zepiam/broadcast-playroom-3')

for path in [patch_lite, patch_full, staged_ver]:
    print(f"Uploading {path.name} to release v3.19...")
    gh('release', 'upload', 'v3.19', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Ensuring release v3.19 is marked as latest...")
gh('release', 'edit', 'v3.19', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest', '--notes-file', str(notes))

print("\n--- Step 5: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.19 - Fix popout window close reliability and direct section deep-linking',
    'sha': current['sha'],
    'content': base64.b64encode(staged_ver.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

# Also save version.json locally in root
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

# Clean out any old pending_update on this machine so fresh new zip is downloaded
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
            print(f"Cleaned stale pending file: {f.name}")
        except Exception as e:
            print(f"Could not delete {f.name}: {e}")

# Rebase local git before pushing
print("\n--- Step 6: Pull rebase and push git changes ---")
subprocess.run(['git', 'add', '-A'], cwd=str(root), check=True)
subprocess.run(['git', 'commit', '-m', 'chore: release v3.19 with popout close reliability and settings deep-linking'], cwd=str(root))
subprocess.run(['git', 'pull', '--rebase', 'origin', 'master'], cwd=str(root), check=True)
subprocess.run(['git', 'push', 'origin', 'master'], cwd=str(root), check=True)

print("\n--- Step 7: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.18"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.19', f"Expected v3.19, got {data['tag_name']}"

print("\nSUCCESS: v3.19 DUAL-PATH RELEASE IS LIVE AND VERIFIED ON GITHUB!")
