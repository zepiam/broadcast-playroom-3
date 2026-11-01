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

print("--- Step 1: Bump version numbers to 3.16 ---")

# 1. package.json
pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '3.16'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')
print("Updated package.json to 3.16")

# 2. updater.py
updater_path = root / 'updater.py'
upd_text = updater_path.read_text(encoding='utf-8')
upd_text = upd_text.replace('CURRENT_VERSION = "3.15"', 'CURRENT_VERSION = "3.16"').replace('CURRENT_VERSION = "3.14"', 'CURRENT_VERSION = "3.16"')
updater_path.write_text(upd_text, encoding='utf-8')
print("Updated updater.py to 3.16")

# 3. src/index.html (titlebar tag)
idx_src = root / 'src/index.html'
idx_text = idx_src.read_text(encoding='utf-8')
idx_text = idx_text.replace('<span class="desktop-titlebar-tag">v3.15</span>', '<span class="desktop-titlebar-tag">v3.16</span>').replace('<span class="desktop-titlebar-tag">v3.14</span>', '<span class="desktop-titlebar-tag">v3.16</span>')
idx_src.write_text(idx_text, encoding='utf-8')
print("Updated src/index.html to v3.16")

print("\n--- Step 2: Build frontend distribution ---")
subprocess.check_call(['npm', 'run', 'build'], cwd=str(root), shell=True)

# Also sync to trial distributions
subprocess.check_call(['python', 'sync_trial_frontend.py'], cwd=str(root))

print("\n--- Step 3: Package differential update patches ---")
dist_src = root / 'dist'
build_trials = root / 'build_trials'
build_trials.mkdir(exist_ok=True)

patch_lite_46 = build_trials / 'patch-v3.16-lite.zip'
patch_full_46 = build_trials / 'patch-v3.16-full.zip'

def package_patch(src_patch, dst_patch, build_type):
    if dst_patch.exists(): dst_patch.unlink()
    with zipfile.ZipFile(dst_patch, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 1. dist/
        for p in dist_src.rglob('*'):
            if p.is_file():
                arcname = f"dist/{p.relative_to(dist_src).as_posix()}"
                zf.write(p, arcname)
        # 2. Python runtime core scripts
        for py_file in ['launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py']:
            f_path = root / py_file
            if f_path.exists():
                zf.write(f_path, py_file)
        # 3. version.json
        v_info = {
            "product": "broadcast-playroom-3",
            "version": "3.16",
            "build_type": build_type
        }
        zf.writestr('version.json', json.dumps(v_info, indent=2))
    print(f"Packaged {dst_patch.name} ({dst_patch.stat().st_size:,} bytes)")

package_patch(dist_src, patch_lite_46, 'lite')
package_patch(dist_src, patch_full_46, 'full')

hash_lite = digest(patch_lite_46)
hash_full = digest(patch_full_46)

changelog = """### Broadcast Playroom v3.16 Update Highlights

- **แถบเมนู Settings ตอบสนอง 100%**: แก้ไขปัญหาคลิกสลับหมวดหมู่ตั้งค่าด้านซ้ายแล้วหน้าจอไม่เปลี่ยนในโหมดหน้าต่างแยก
- **เปิดการตั้งค่า Overlay+ ให้อัตโนมัติ**: เมื่อกดปุ่ม Overlay+ หากยังไม่ได้ระบุ URL จะเปิดหน้าต่างตั้งค่าเบราว์เซอร์ลอยให้ทันที
- **หลอด Progress Bar ในกล่องอัปเดต**: เพิ่มแถบสถานะการดาวน์โหลดในเบื้องหลังแบบกราฟิกสีเขียวมรกตพร้อมตัวเลข % ละเอียด
- **จัดวางป้ายเวอร์ชันใหม่ (Inline Header)**: ดีไซน์ส่วนหัวหน้าต่างอัปเดตให้ป้ายเวอร์ชันวางเคียงคู่ชื่อโปรแกรมอย่างลงตัว ไม่อึดอัด
- **ความปลอดภัยและการตั้งค่าคงเดิม**: ข้อมูลบัญชีสตรีมและค่าทุกอย่างที่เคยกรอกไว้จะคงอยู่ครบถ้วนตลอดการอัปเดต
"""

manifest = {
    "latest_version": "3.16",
    "critical": False,
    "changelog": changelog.strip(),
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.16/patch-v3.16-lite.zip",
        "sha256": hash_lite,
        "size": patch_lite_46.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.16/patch-v3.16-full.zip",
        "sha256": hash_full,
        "size": patch_full_46.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.16",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.16/patch-v3.16-lite.zip",
            "patch_sha256": hash_lite,
            "patch_size": patch_lite_46.stat().st_size
        },
        "full": {
            "version": "3.16",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.16/patch-v3.16-full.zip",
            "patch_sha256": hash_full,
            "patch_size": patch_full_46.stat().st_size
        }
    }
}

print("\n--- Step 4: Publish GitHub Release v3.16 ---")
folder = root / 'build_trials/patch-publish-3.16'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

try:
    gh('release', 'delete', 'v3.16', '--repo', 'zepiam/broadcast-playroom-3', '--yes')
    print("Deleted old v3.16 release")
except Exception:
    pass

print("Creating release v3.16...")
gh('release', 'create', 'v3.16', '--repo', 'zepiam/broadcast-playroom-3', '--draft', '--title', 'Broadcast Playroom v3.16', '--notes-file', str(notes))

for path in [patch_lite_46, patch_full_46, staged_ver]:
    print(f"Uploading {path.name}...")
    gh('release', 'upload', 'v3.16', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Publishing and setting v3.16 as latest...")
gh('release', 'edit', 'v3.16', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest')

print("\n--- Step 5: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.16 - Settings nav restore, overlay+ auto-config, and progress bar polish',
    'sha': current['sha'],
    'content': base64.b64encode(staged_ver.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

# Also save version.json locally in root
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

print("\n--- Step 6: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.15"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.16', f"Expected v3.16, got {data['tag_name']}"

print("\nSUCCESS: v3.16 RELEASE IS LIVE AND VERIFIED ON GITHUB!")
