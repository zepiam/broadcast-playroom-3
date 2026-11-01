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

print("--- Step 1: Bump version numbers to 3.8 ---")

# 1. package.json
pkg_path = root / 'package.json'
pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
pkg['version'] = '3.8'
pkg_path.write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf-8')
print("Updated package.json to 3.8")

# 2. updater.py
updater_path = root / 'updater.py'
upd_text = updater_path.read_text(encoding='utf-8')
upd_text = upd_text.replace('CURRENT_VERSION = "3.7"', 'CURRENT_VERSION = "3.8"')
updater_path.write_text(upd_text, encoding='utf-8')
print("Updated updater.py to 3.8")

# 3. src/index.html (titlebar tag)
idx_src = root / 'src/index.html'
idx_text = idx_src.read_text(encoding='utf-8')
idx_text = idx_text.replace('<span class="desktop-titlebar-tag">v3.7</span>', '<span class="desktop-titlebar-tag">v3.8</span>')
idx_src.write_text(idx_text, encoding='utf-8')
print("Updated src/index.html to v3.8")

print("\n--- Step 2: Build frontend distribution ---")
subprocess.check_call(['npm', 'run', 'build'], cwd=str(root), shell=True)

# Also sync to trial distributions
subprocess.check_call(['python', 'sync_trial_frontend.py'], cwd=str(root))

# Also sync to installed production folder if exists
installed_dist = Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\dist")
if installed_dist.exists():
    shutil.copytree(root / 'dist', installed_dist, dirs_exist_ok=True)
    print("Synced to installed production app directory:", installed_dist)

changelog = (
    "- Broadcast Playroom v3.8\n"
    "- กู้คืนหน้าต่าง Game Overlay Suite เต็มรูปแบบ: โหมด Themes (10 ธีมพร้อม Pagination), โหมด Balloon, โหมด Character Talk (นำเข้ารูปอวาตาร์ VTuber), บันทึก Global Hotkeys (Ctrl+Shift+G / Ctrl+Shift+H), แถบปรับขนาดและค่าความทึบแบบเรียลไทม์ (Live Sliders)\n"
    "- แยกหน้าต่างตั้งค่า Overlay+ (เบราว์เซอร์ลอย) ออกเป็นหน้าต่างเฉพาะ ไม่ปนกันและรองรับ URL ได้สูงสุด 3 หน้าต่าง\n"
    "- กู้คืนเมนูแถบซ้ายในหน้าต่างการตั้งค่า (Settings Sidebar): สามารถเลือกสลับหมวดหมู่ได้ครบทั้ง 16 หมวด (Platforms, Chatbot, TTS, Themes, Translate, OBS, Docks, Networking, NG, Replace, Block, Secret, Defender, About, Supporters, Log) ทั้งในหน้าต่างหลักและหน้าต่าง Popout\n"
    "- แก้ไขปัญหาลากขยับหน้าต่างหลักโปรแกรม (Custom Titlebar Dragging) ให้ลากขยับได้ลื่นไหล ไม่ติดขัด\n"
    "- ปรับปรุงการสลับหน้าต่างและคืน Node ไปยังหน้าต่างหลักอย่างไร้รอยต่อ ไม่มีปัญหา Event Handler หายหลังปิด Popout"
)

print("\n--- Step 3: Package Lite and Full Patch 3.8 ---")
patch_lite_37 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.7.zip'
patch_lite_38 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.8.zip'

dist_dir = root / 'dist'

with zipfile.ZipFile(patch_lite_37) as src_z, zipfile.ZipFile(patch_lite_38, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as dst_z:
    for entry in src_z.infolist():
        if entry.filename in ('version.json', '_internal/version.json'):
            continue
        if entry.filename.startswith('_internal/dist/'):
            continue
        dst_z.writestr(entry, src_z.read(entry))

    # Add all fresh dist files
    for item in dist_dir.rglob('*'):
        if item.is_file() and not item.name.startswith('shout_'):
            rel = item.relative_to(dist_dir).as_posix()
            dst_z.write(item, f'_internal/dist/{rel}')

    # Write version 3.8
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.8', 'build_type': 'lite'}, indent=2).encode('utf-8')
    dst_z.writestr('version.json', ver_data)
    dst_z.writestr('_internal/version.json', ver_data)

patch_full_37 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.7.zip'
patch_full_38 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.8.zip'

with zipfile.ZipFile(patch_full_37) as src_z, zipfile.ZipFile(patch_full_38, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as dst_z:
    for entry in src_z.infolist():
        if entry.filename in ('version.json', '_internal/version.json'):
            continue
        if entry.filename.startswith('_internal/dist/'):
            continue
        dst_z.writestr(entry, src_z.read(entry))

    # Add all fresh dist files
    for item in dist_dir.rglob('*'):
        if item.is_file() and not item.name.startswith('shout_'):
            rel = item.relative_to(dist_dir).as_posix()
            dst_z.write(item, f'_internal/dist/{rel}')

    # Write version 3.8
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.8', 'build_type': 'full'}, indent=2).encode('utf-8')
    dst_z.writestr('version.json', ver_data)
    dst_z.writestr('_internal/version.json', ver_data)

# Verify both archives
for p, expected_build in [(patch_lite_38, 'lite'), (patch_full_38, 'full')]:
    with zipfile.ZipFile(p) as check:
        assert check.testzip() is None
        v1 = json.loads(check.read('version.json'))
        v2 = json.loads(check.read('_internal/version.json'))
        assert v1['version'] == '3.8'
        assert v2['version'] == '3.8'
        assert '_internal/dist/index.html' in check.namelist()
        assert '_internal/dist/styles.css' in check.namelist()
        assert '_internal/dist/game_overlay_chat_controls.js' in check.namelist()
        print(f"Verified {p.name}: integrity OK, version 3.8, game_overlay_chat_controls.js included!")

lite_size = patch_lite_38.stat().st_size
lite_sha = digest(patch_lite_38)
full_size = patch_full_38.stat().st_size
full_sha = digest(patch_full_38)

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.8",
    "repo": "zepiam/broadcast-playroom-3",
    "changelog": changelog,
    "published_at": "2026-11-01",
    "lite": {
        "type": "patch",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.8/{patch_lite_38.name}",
        "size": lite_size,
        "sha256": lite_sha
    },
    "full": {
        "type": "patch",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.8/{patch_full_38.name}",
        "size": full_size,
        "sha256": full_sha
    }
}

# Update local version.json
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("Updated local version.json to v3.8")

# Update installed version.json if exists
if (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\version.json")).exists():
    (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\version.json")).write_text(
        json.dumps({'product': 'broadcast-playroom-3', 'version': '3.8', 'build_type': 'full'}, indent=2),
        encoding='utf-8'
    )
if (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\version.json")).exists():
    (Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\version.json")).write_text(
        json.dumps({'product': 'broadcast-playroom-3', 'version': '3.8', 'build_type': 'full'}, indent=2),
        encoding='utf-8'
    )

print("\n--- Step 4: Publish GitHub Release v3.8 ---")
folder = root / 'build_trials/patch-publish-3.8'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

# Delete existing v3.8 release if already exists
try:
    gh('release', 'delete', 'v3.8', '--repo', 'zepiam/broadcast-playroom-3', '--yes')
    print("Deleted old v3.8 release")
except Exception:
    pass

print("Creating release v3.8...")
gh('release', 'create', 'v3.8', '--repo', 'zepiam/broadcast-playroom-3', '--draft', '--title', 'Broadcast Playroom v3.8', '--notes-file', str(notes))

for path in [patch_lite_38, patch_full_38, staged_ver]:
    print(f"Uploading {path.name}...")
    gh('release', 'upload', 'v3.8', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Publishing and setting v3.8 as latest...")
gh('release', 'edit', 'v3.8', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest')

print("\n--- Step 5: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.8 - Full Game Overlay Suite, Settings Navigation, Window Dragging',
    'sha': current['sha'],
    'content': base64.b64encode(staged_ver.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

print("\n--- Step 6: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.7"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.8', f"Expected v3.8, got {data['tag_name']}"

print("\nSUCCESS: v3.8 RELEASE IS LIVE AND VERIFIED ON GITHUB!")
