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

print("--- Step 1: Bump version numbers to 3.12 ---")

# 1. package.json
pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '3.12'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')
print("Updated package.json to 3.12")

# 2. updater.py
updater_path = root / 'updater.py'
upd_text = updater_path.read_text(encoding='utf-8')
upd_text = upd_text.replace('CURRENT_VERSION = "3.11"', 'CURRENT_VERSION = "3.12"')
updater_path.write_text(upd_text, encoding='utf-8')
print("Updated updater.py to 3.12")

# 3. src/index.html (titlebar tag)
idx_src = root / 'src/index.html'
idx_text = idx_src.read_text(encoding='utf-8')
idx_text = idx_text.replace('<span class="desktop-titlebar-tag">v3.11</span>', '<span class="desktop-titlebar-tag">v3.12</span>')
idx_src.write_text(idx_text, encoding='utf-8')
print("Updated src/index.html to v3.12")

print("\n--- Step 2: Build frontend distribution ---")
subprocess.check_call(['npm', 'run', 'build'], cwd=str(root), shell=True)

# Also sync to trial distributions
subprocess.check_call(['python', 'sync_trial_frontend.py'], cwd=str(root))

# Also sync to installed production folder if exists
installed_full = Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full")
if (installed_full / '_internal').exists():
    shutil.copytree(root / 'dist', installed_full / '_internal' / 'dist', dirs_exist_ok=True)
    for py in ['launch_dev.py', 'updater.py', 'game_chat_settings.py']:
        if (root / py).exists():
            shutil.copy2(root / py, installed_full / '_internal' / py)
    print("Synced to installed production app directory:", installed_full)

changelog = (
    "- Broadcast Playroom v3.12\n"
    "- นำแถบหัวข้อและคำอธิบายซ้ำซ้อนด้านบน (เช่น 'Overlay Composer Studio จัดวางเลย์เอาต์...', 'ตั้งค่า Game Overlay ปรับแต่งหน้าต่าง...') ออกจากทุกหน้าต่าง เพิ่มพื้นที่ทำงานให้กว้างขวาง สบายตา คลีน มินิมอล\n"
    "- ใน Composer Studio: ยุบหัวข้อซ้ำซ้อนและจัดแถบเครื่องมือ (พรีวิว, ส่งออก, นำเข้า, ลิงก์ OBS ฯลฯ) ชิดด้านบน ทำให้แคนวาสจัดฉากมีพื้นที่กว้างขึ้นเต็มตา\n"
    "- ใน Game Overlay: ปรับระบบเป็น Auto-save บันทึกอัตโนมัติทันทีที่มีการขยับสไลเดอร์ขนาด ความสูง หรือความทึบ พร้อมบันทึกก่อนปิดหน้าต่าง และนำปุ่ม '💾 บันทึกการตั้งค่า' ออก เหลือเพียงปุ่ม 'ปิดหน้าต่าง' เรียบหรู"
)

print("\n--- Step 3: Package Lite and Full Patch 3.12 ---")
patch_lite_41 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.11.zip'
patch_lite_42 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.12.zip'

dist_dir = root / 'dist'

def package_patch(src_patch, dst_patch, build_type):
    with zipfile.ZipFile(src_patch) as src_z, zipfile.ZipFile(dst_patch, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as dst_z:
        for entry in src_z.infolist():
            if entry.filename in ('version.json', '_internal/version.json'):
                continue
            if entry.filename.startswith('_internal/dist/'):
                continue
            if entry.filename in ('_internal/launch_dev.py', '_internal/updater.py', '_internal/game_chat_settings.py'):
                continue
            dst_z.writestr(entry, src_z.read(entry))

        # Add all fresh dist files
        for item in dist_dir.rglob('*'):
            if item.is_file() and not item.name.startswith('shout_'):
                rel = item.relative_to(dist_dir).as_posix()
                dst_z.write(item, f'_internal/dist/{rel}')

        # Add updated python files
        for py in ['launch_dev.py', 'updater.py', 'game_chat_settings.py']:
            py_path = root / py
            if py_path.exists():
                dst_z.write(py_path, f'_internal/{py}')

        # Write version 3.12
        ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.12', 'build_type': build_type}, indent=2).encode('utf-8')
        dst_z.writestr('version.json', ver_data)
        dst_z.writestr('_internal/version.json', ver_data)

package_patch(patch_lite_41, patch_lite_42, 'lite')

patch_full_41 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.11.zip'
patch_full_42 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.12.zip'
package_patch(patch_full_41, patch_full_42, 'full')

# Verify both archives
for p, expected_build in [(patch_lite_42, 'lite'), (patch_full_42, 'full')]:
    with zipfile.ZipFile(p) as check:
        assert check.testzip() is None
        v1 = json.loads(check.read('version.json'))
        v2 = json.loads(check.read('_internal/version.json'))
        assert v1['version'] == '3.12'
        assert v2['version'] == '3.12'
        assert '_internal/dist/index.html' in check.namelist()
        assert '_internal/dist/styles.css' in check.namelist()
        assert '_internal/dist/modal.css' in check.namelist()
        assert '_internal/dist/game_overlay_chat_controls.js' in check.namelist()
        print(f"Verified {p.name}: integrity OK, version 3.12 verified!")

lite_size = patch_lite_42.stat().st_size
lite_sha = digest(patch_lite_42)
full_size = patch_full_42.stat().st_size
full_sha = digest(patch_full_42)

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.12",
    "repo": "zepiam/broadcast-playroom-3",
    "changelog": changelog,
    "published_at": "2026-11-01",
    "lite": {
        "type": "patch",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.12/{patch_lite_42.name}",
        "size": lite_size,
        "sha256": lite_sha
    },
    "full": {
        "type": "patch",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.12/{patch_full_42.name}",
        "size": full_size,
        "sha256": full_sha
    }
}

# Update local version.json
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("Updated local version.json to v3.12")

# Update installed version.json if exists
if (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\version.json")).exists():
    (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\version.json")).write_text(
        json.dumps({'product': 'broadcast-playroom-3', 'version': '3.12', 'build_type': 'full'}, indent=2),
        encoding='utf-8'
    )
if (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\version.json")).exists():
    (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\version.json")).write_text(
        json.dumps({'product': 'broadcast-playroom-3', 'version': '3.12', 'build_type': 'full'}, indent=2),
        encoding='utf-8'
    )

print("\n--- Step 4: Publish GitHub Release v3.12 ---")
folder = root / 'build_trials/patch-publish-3.12'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

# Delete existing v3.12 release if already exists
try:
    gh('release', 'delete', 'v3.12', '--repo', 'zepiam/broadcast-playroom-3', '--yes')
    print("Deleted old v3.12 release")
except Exception:
    pass

print("Creating release v3.12...")
gh('release', 'create', 'v3.12', '--repo', 'zepiam/broadcast-playroom-3', '--draft', '--title', 'Broadcast Playroom v3.12', '--notes-file', str(notes))

for path in [patch_lite_42, patch_full_42, staged_ver]:
    print(f"Uploading {path.name}...")
    gh('release', 'upload', 'v3.12', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Publishing and setting v3.12 as latest...")
gh('release', 'edit', 'v3.12', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest')

print("\n--- Step 5: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.12 - Header Space Optimization and Game Overlay Auto-save',
    'sha': current['sha'],
    'content': base64.b64encode(staged_ver.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

print("\n--- Step 6: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.11"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.12', f"Expected v3.12, got {data['tag_name']}"

print("\nSUCCESS: v3.12 RELEASE IS LIVE AND VERIFIED ON GITHUB!")