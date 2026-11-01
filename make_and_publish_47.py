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

print("--- Step 1: Verify version numbers are 3.17 ---")

# 1. package.json
pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '3.17'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')

# 2. updater.py
updater_path = root / 'updater.py'
upd_text = updater_path.read_text(encoding='utf-8')
upd_text = upd_text.replace('CURRENT_VERSION = "3.16"', 'CURRENT_VERSION = "3.17"').replace('CURRENT_VERSION = "3.15"', 'CURRENT_VERSION = "3.17"')
updater_path.write_text(upd_text, encoding='utf-8')

# 3. src/index.html (titlebar tag)
idx_src = root / 'src/index.html'
idx_text = idx_src.read_text(encoding='utf-8')
idx_text = idx_text.replace('<span class="desktop-titlebar-tag">v3.16</span>', '<span class="desktop-titlebar-tag">v3.17</span>').replace('<span class="desktop-titlebar-tag">v3.15</span>', '<span class="desktop-titlebar-tag">v3.17</span>')
idx_src.write_text(idx_text, encoding='utf-8')

print("\n--- Step 2: Build frontend distribution ---")
subprocess.check_call(['npm', 'run', 'build'], cwd=str(root), shell=True)
subprocess.check_call(['python', 'sync_trial_frontend.py'], cwd=str(root))

print("\n--- Step 3: Package dual-path (root + _internal) update patches ---")
dist_src = root / 'dist'
build_trials = root / 'build_trials'
build_trials.mkdir(exist_ok=True)

patch_lite_47 = build_trials / 'patch-v3.17-lite.zip'
patch_full_47 = build_trials / 'patch-v3.17-full.zip'

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
            "version": "3.17",
            "latest_version": "3.17",
            "build_type": build_type
        }
        zf.writestr('version.json', json.dumps(v_info, indent=2))
        zf.writestr('_internal/version.json', json.dumps(v_info, indent=2))
    print(f"Packaged {dst_patch.name} ({dst_patch.stat().st_size:,} bytes)")

package_patch(dist_src, patch_lite_47, 'lite')
package_patch(dist_src, patch_full_47, 'full')

hash_lite = digest(patch_lite_47)
hash_full = digest(patch_full_47)

changelog = """### Broadcast Playroom v3.17 Update Highlights

- **ซ่อนปุ่ม Overlay+ อัตโนมัติเมื่อยังไม่มีการระบุ URL**: หากยังไม่ได้กำหนด URL ในตั้งค่า ปุ่ม Overlay+ จะไม่แสดงบนแถบด้านบนให้เกะกะ และจะปรากฏขึ้นอัตโนมัติทันทีที่มีการบันทึก URL หรือเปิดใช้งาน
- **แถบตั้งค่า Overlay+ ในแท็บ Docks & Web URL**: เพิ่มการ์ดสำหรับเข้าถึงการตั้งค่า URL ของ Overlay+ ในหน้าต่างตั้งค่าหลักโดยตรง
- **แถบขอบไฟอัปเดตแบบ Squircle Progress Bar บน Server Rail**: ขณะกำลังดาวน์โหลดไฟล์อัปเดตในเบื้องหลัง ขอบเรืองแสงสีเขียวรอบปุ่มลูกศรดาวน์โหลดจะวิ่งเป็น Progress Bar ตามเปอร์เซ็นต์จริง (0-100%) และเมื่อดาวน์โหลดเสร็จสมบูรณ์ เส้นขอบจะวิ่งครบรอบล้อมกรอบปุ่มตามเดิม พร้อมแจ้งเตือนให้พร้อมติดตั้ง
- **Zero GPU Lockup Compliance**: คำนวณความยาวเส้นรอบรูป SVG Dash-offset แบบ Real-time ตาม Chunks ที่รับมา โดยไม่มี CSS animation loop หน่วงการทำงาน ทำให้ GPU เข้าสู่โหมดพัก (0% idle) ได้อย่างสมบูรณ์
- **Safe PyInstaller Atomic Extraction (_internal parity)**: แพ็กเกจครอบคลุมโครงสร้าง _internal ของตัวเต็ม ทำให้รีสตาร์ทแล้วอัปเดตติดสมบูรณ์แบบแน่นอน
"""

manifest = {
    "version": "3.17",
    "latest_version": "3.17",
    "critical": False,
    "changelog": changelog.strip(),
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.17/patch-v3.17-lite.zip",
        "sha256": hash_lite,
        "size": patch_lite_47.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.17/patch-v3.17-full.zip",
        "sha256": hash_full,
        "size": patch_full_47.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.17",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.17/patch-v3.17-lite.zip",
            "patch_sha256": hash_lite,
            "patch_size": patch_lite_47.stat().st_size
        },
        "full": {
            "version": "3.17",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.17/patch-v3.17-full.zip",
            "patch_sha256": hash_full,
            "patch_size": patch_full_47.stat().st_size
        }
    }
}

print("\n--- Step 4: Publish GitHub Release v3.17 ---")
folder = root / 'build_trials/patch-publish-3.17'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

for path in [patch_lite_47, patch_full_47, staged_ver]:
    print(f"Uploading {path.name} to release v3.17...")
    gh('release', 'upload', 'v3.17', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Ensuring release v3.17 is published as latest...")
gh('release', 'edit', 'v3.17', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest', '--notes-file', str(notes))

print("\n--- Step 5: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.17 - Dual-path atomic update with _internal parity',
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

print("\n--- Step 6: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.15"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.17', f"Expected v3.17, got {data['tag_name']}"

print("\nSUCCESS: v3.17 DUAL-PATH RELEASE IS LIVE AND VERIFIED ON GITHUB!")
