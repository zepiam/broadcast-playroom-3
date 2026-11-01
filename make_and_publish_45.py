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

print("--- Step 1: Bump version numbers to 3.15 ---")

# 1. package.json
pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '3.15'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')
print("Updated package.json to 3.15")

# 2. updater.py
updater_path = root / 'updater.py'
upd_text = updater_path.read_text(encoding='utf-8')
upd_text = upd_text.replace('CURRENT_VERSION = "3.14"', 'CURRENT_VERSION = "3.15"')
updater_path.write_text(upd_text, encoding='utf-8')
print("Updated updater.py to 3.15")

# 3. src/index.html (titlebar tag)
idx_src = root / 'src/index.html'
idx_text = idx_src.read_text(encoding='utf-8')
idx_text = idx_text.replace('<span class="desktop-titlebar-tag">v3.14</span>', '<span class="desktop-titlebar-tag">v3.15</span>')
idx_src.write_text(idx_text, encoding='utf-8')
print("Updated src/index.html to v3.15")

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
    "- Broadcast Playroom v3.15\n"
    "- กู้คืนและแก้ไขปุ่ม Game Overlay และ Overlay+ ด้านบน ให้กลับมาใช้งานได้สมบูรณ์แบบ 100%\n"
    "- แก้ไขเมนูคลิกขวา Overlay & แปลภาษา: คลิก 'ตั้งค่าการแปลภาษา...' เปิดเข้าสู่หน้าตั้งค่าแท็บแปลภาษาโดยตรง และคลิก 'ตั้งค่า OBS WebSocket...' เปิดเข้าแท็บ OBS WebSocket โดยตรง\n"
    "- ปรับแต่งปุ่มแท็บสลับ Game Overlay / Viewer Overlay ในหน้าต่างตั้งค่า Game Overlay ให้เป็นดีไซน์ Dark Pill ที่สวยงาม ไม่เปลือย ไม่หลุดสไตล์\n"
    "- ปรับปุ่ม 'พับเก็บ' เป็น 'ปิดหน้าต่าง' และนำปุ่มบันทึกที่ซ้ำซ้อนออกในเครื่องมือ (Settings, Replie, ASK, QuickRandomizer, Playroom, User Manager) รองรับการสั่งปิดทั้งในโหมดปกติและ Popout Window\n"
    "- แก้ไขระบบ Auto-Save และ Backup & Restore ให้ผสานและจดจำข้อมูลช่องทางสตรีม (Channel Names) และสถานะเชื่อมต่ออัตโนมัติ (Auto-Connect) คงอยู่ถาวร 100% ไม่สูญหายเมื่ออัปเดตเวอร์ชันใหม่"
)

print("\n--- Step 3: Package Lite and Full Patch 3.15 ---")
patch_lite_44 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.14.zip'
patch_lite_45 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.15.zip'

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

        # Write version 3.15
        ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.15', 'build_type': build_type}, indent=2).encode('utf-8')
        dst_z.writestr('version.json', ver_data)
        dst_z.writestr('_internal/version.json', ver_data)

package_patch(patch_lite_44, patch_lite_45, 'lite')

patch_full_44 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.14.zip'
patch_full_45 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.15.zip'
package_patch(patch_full_44, patch_full_45, 'full')

# Verify both archives
for p, expected_build in [(patch_lite_45, 'lite'), (patch_full_45, 'full')]:
    with zipfile.ZipFile(p) as check:
        assert check.testzip() is None
        v1 = json.loads(check.read('version.json'))
        v2 = json.loads(check.read('_internal/version.json'))
        assert v1['version'] == '3.15'
        assert v2['version'] == '3.15'
        assert '_internal/dist/index.html' in check.namelist()
        assert '_internal/dist/styles.css' in check.namelist()
        assert '_internal/dist/desktop_overlay_controls.js' in check.namelist()

manifest = {
    "version": "3.15",
    "product": "broadcast-playroom-3",
    "release_date": "2026-11-01",
    "min_app_version": "3.0.0",
    "changelog": changelog,
    "packages": {
        "lite": {
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.15/BroadcastPlayroom3-Lite-Patch-3.15.zip",
            "patch_sha256": digest(patch_lite_45),
            "patch_size": patch_lite_45.stat().st_size
        },
        "full": {
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.15/BroadcastPlayroom3-Full-Patch-3.15.zip",
            "patch_sha256": digest(patch_full_45),
            "patch_size": patch_full_45.stat().st_size
        }
    }
}

print("\n--- Step 4: Publish GitHub Release v3.15 ---")
folder = root / 'build_trials/patch-publish-3.15'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

try:
    gh('release', 'delete', 'v3.15', '--repo', 'zepiam/broadcast-playroom-3', '--yes')
    print("Deleted old v3.15 release")
except Exception:
    pass

print("Creating release v3.15...")
gh('release', 'create', 'v3.15', '--repo', 'zepiam/broadcast-playroom-3', '--draft', '--title', 'Broadcast Playroom v3.15', '--notes-file', str(notes))

for path in [patch_lite_45, patch_full_45, staged_ver]:
    print(f"Uploading {path.name}...")
    gh('release', 'upload', 'v3.15', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Publishing and setting v3.15 as latest...")
gh('release', 'edit', 'v3.15', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest')

print("\n--- Step 5: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.15 - Game overlay fixes, popout navigation parity, and permanent settings persistence',
    'sha': current['sha'],
    'content': base64.b64encode(staged_ver.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

print("\n--- Step 6: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.14"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.15', f"Expected v3.15, got {data['tag_name']}"

print("\nSUCCESS: v3.15 RELEASE IS LIVE AND VERIFIED ON GITHUB!")
