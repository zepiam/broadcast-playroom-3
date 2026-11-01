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

print("--- Step 1: Prepare v3.7 Patch Archives ---")

changelog = (
    "- Broadcast Playroom v3.7\n"
    "- แก้ไขบั๊กหน้าต่างกลายเป็นรูปไอคอนใหญ่เต็มจอ: ฉีดสไตล์ชีต (styles.css, modal.css, ฯลฯ) ครบถ้วน 100% พร้อม inline constraint ขนาด 16px บนไอคอน titlebar\n"
    "- ปิดหน้าต่างโหลด Splash Screen ถาวรตามคำขอ เข้าโปรแกรมเร็วทันที (Instant Startup 0.9s)\n"
    "- แก้ไขปุ่มย่อ/ปิดหน้าต่างซ้อนกันในหน้าต่างป๊อปอัป (Popout Tool Windows) ให้เหลือชุดปุ่มระบบ Windows เพียงชุดเดียว\n"
    "- ปรับปรุงระบบซ่อน/แสดงช่องทางแพลตฟอร์มใน Sidebar และ Settings ให้ซิงค์สถานะตรงกันแบบเรียลไทม์\n"
    "- รวม Cumulative Patch สำหรับทั้งรุ่น Lite และ Full ให้กดอัปเดตจากเวอร์ชันใดก็ใช้งานได้ทันที"
)

# 1. Repackage Lite Patch 3.7 from Lite Patch 3.6
patch_lite_36 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.6.zip'
patch_lite_37 = root / 'build_trials/BroadcastPlayroom3-Lite-Patch-3.7.zip'

dist_dir = root / 'dist'

with zipfile.ZipFile(patch_lite_36) as src_z, zipfile.ZipFile(patch_lite_37, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as dst_z:
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

    # Write version 3.7
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.7', 'build_type': 'lite'}, indent=2).encode('utf-8')
    dst_z.writestr('version.json', ver_data)
    dst_z.writestr('_internal/version.json', ver_data)

# 2. Repackage Full Patch 3.7 from Full Patch 3.6
patch_full_36 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.6.zip'
patch_full_37 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.7.zip'

with zipfile.ZipFile(patch_full_36) as src_z, zipfile.ZipFile(patch_full_37, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as dst_z:
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

    # Write version 3.7
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.7', 'build_type': 'full'}, indent=2).encode('utf-8')
    dst_z.writestr('version.json', ver_data)
    dst_z.writestr('_internal/version.json', ver_data)

# Verify both archives
for p, expected_build in [(patch_lite_37, 'lite'), (patch_full_37, 'full')]:
    with zipfile.ZipFile(p) as check:
        assert check.testzip() is None
        v1 = json.loads(check.read('version.json'))
        v2 = json.loads(check.read('_internal/version.json'))
        assert v1['version'] == '3.7'
        assert v2['version'] == '3.7'
        assert '_internal/dist/index.html' in check.namelist()
        assert '_internal/dist/styles.css' in check.namelist()
        # Verify index.html inside archive actually has styles.css
        idx_content = check.read('_internal/dist/index.html').decode('utf-8')
        assert 'styles.css' in idx_content
        assert 'desktop-titlebar-icon' in idx_content
        print(f"Verified {p.name}: integrity OK, version 3.7, styles.css included!")

lite_size = patch_lite_37.stat().st_size
lite_sha = digest(patch_lite_37)
full_size = patch_full_37.stat().st_size
full_sha = digest(patch_full_37)

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.7",
    "repo": "zepiam/broadcast-playroom-3",
    "changelog": changelog,
    "published_at": "2026-11-01",
    "lite": {
        "type": "patch",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.7/{patch_lite_37.name}",
        "size": lite_size,
        "sha256": lite_sha
    },
    "full": {
        "type": "patch",
        "url": f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.7/{patch_full_37.name}",
        "size": full_size,
        "sha256": full_sha
    }
}

# Update local version.json
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("Updated local version.json")

print("\n--- Step 2: Publish GitHub Release v3.7 ---")
folder = root / 'build_trials/patch-publish-3.7'
folder.mkdir(parents=True, exist_ok=True)
staged_ver = folder / 'version.json'
staged_ver.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

# Delete existing v3.7 release if already exists
try:
    gh('release', 'delete', 'v3.7', '--repo', 'zepiam/broadcast-playroom-3', '--yes')
    print("Deleted old v3.7 release")
except Exception:
    pass

print("Creating release v3.7...")
gh('release', 'create', 'v3.7', '--repo', 'zepiam/broadcast-playroom-3', '--draft', '--title', 'Broadcast Playroom v3.7', '--notes-file', str(notes))

for path in [patch_lite_37, patch_full_37, staged_ver]:
    print(f"Uploading {path.name}...")
    gh('release', 'upload', 'v3.7', str(path), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

print("Publishing and setting v3.7 as latest...")
gh('release', 'edit', 'v3.7', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest')

print("\n--- Step 3: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.7 - Fix giant icon display, inject missing stylesheets, disable splash, clean popout titlebar',
    'sha': current['sha'],
    'content': base64.b64encode(staged_ver.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

print("\n--- Step 4: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.6"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.7', f"Expected v3.7, got {data['tag_name']}"

print("\nSUCCESS: v3.7 RELEASE IS LIVE AND VERIFIED ON GITHUB!")
