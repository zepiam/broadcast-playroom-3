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

print("--- Step 1: Synchronize Frontend Dist to Compiled Trials ---")
trials = [
    ('Lite', 'trial-20261101-021316-344792', root / 'build_trials/lite/BroadcastPlayroom3-Lite'),
    ('Full', 'trial-20261101-021556-140248', Path(r'E:\DOCS\Documents\BroadcastPlayroom3\full'))
]

dist_dir = root / 'dist'
for edition, trial, baseline in trials:
    source = root / 'build_trials' / trial / 'dist' / ('BroadcastPlayroom3-' + edition)
    internal_dist = source / '_internal' / 'dist'
    internal_dist.mkdir(parents=True, exist_ok=True)
    
    # Copy all files from dist into internal_dist
    for item in dist_dir.rglob('*'):
        if item.is_file():
            rel = item.relative_to(dist_dir)
            target = internal_dist / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    print(f"Synced dist/ to {edition} trial source at {internal_dist}")

    # Also update version.json in trial source
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.6', 'build_type': edition.lower()}, indent=2).encode('utf-8')
    (source / 'version.json').write_bytes(ver_data)
    (source / '_internal' / 'version.json').write_bytes(ver_data)

print("\n--- Step 2: Build Patch ZIP Archives for v3.6 ---")
changelog = (
    "- Broadcast Playroom v3.6\n"
    "- แก้ไขปัญหาปุ่มควบคุมหัวหน้าต่างในหน้าต่างเครื่องมือแยก (Popout Tool Windows) ซ้อนกัน 2 ชั้น\n"
    "- แก้ไขการซ่อน/แสดงการ์ดแพลตฟอร์มบน Sidebar ในหน้าแรกให้ซิงค์แบบ Real-time ทันทีเมื่อตั้งค่าในหน้าต่างแยก\n"
    "- ปรับปรุงการกดปุ่ม Quick Pills ในหน้าตั้งค่าช่องทางสตรีมให้แม่นยำและเสถียรยิ่งขึ้น\n"
    "- รวมการอัปเกรดความเร็วเปิดโปรแกรม 13 เท่า และเฟรมหน้าต่าง Windows 11 Snap Assist จาก v3.5 ครบถ้วน"
)

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.6",
    "repo": "zepiam/broadcast-playroom-3",
    "changelog": changelog,
    "published_at": "2026-11-01"
}

patches = []
for edition, trial, baseline in trials:
    source = root / 'build_trials' / trial / 'dist' / ('BroadcastPlayroom3-' + edition)
    output = root / 'build_trials' / f'BroadcastPlayroom3-{edition}-Patch-3.6.zip'
    included = []

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
        for path in source.rglob('*'):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            name = relative.as_posix()
            if name == 'build_receipt.json':
                continue
            if name.startswith('data/') or path.name in ('composer_layout.json', 'replace_words.json', 'bot_accounts.dat'):
                raise ValueError('User data in source')
            old = baseline / relative
            if name.endswith('version.json') or not old.is_file() or path.stat().st_size != old.stat().st_size or digest(path) != digest(old):
                archive.write(path, name)
                included.append(name)
        if 'version.json' not in included:
            archive.write(source / 'version.json', 'version.json')
            included.append('version.json')
        if '_internal/version.json' not in included:
            archive.write(source / '_internal' / 'version.json', '_internal/version.json')
            included.append('_internal/version.json')

    # Verify archive integrity
    with zipfile.ZipFile(output) as check:
        assert check.testzip() is None
        assert json.loads(check.read('version.json'))['version'] == '3.6'
        assert json.loads(check.read('_internal/version.json'))['version'] == '3.6'

    size = output.stat().st_size
    d = digest(output)
    manifest[edition.lower()] = {
        'type': 'patch',
        'url': f'https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.6/{output.name}',
        'size': size,
        'sha256': d
    }
    patches.append(output)
    print(f"Created {edition} Patch-3.6: {size:,} bytes, {len(included)} modified files, SHA256: {d}", flush=True)

# Write version.json locally
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print("Updated local version.json")

print("\n--- Step 3: Publish GitHub Release v3.6 ---")
folder = root / 'build_trials/patch-publish-3.6'
folder.mkdir(parents=True, exist_ok=True)
staged = folder / 'version.json'
staged.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
notes = folder / 'notes.md'
notes.write_text(changelog, encoding='utf-8')

# Delete existing v3.6 release or tag if left over
try:
    gh('release', 'delete', 'v3.6', '--repo', 'zepiam/broadcast-playroom-3', '--yes')
    print("Deleted old v3.6 release")
except Exception:
    pass

print("Creating release v3.6...")
gh('release', 'create', 'v3.6', '--repo', 'zepiam/broadcast-playroom-3', '--draft', '--title', 'Broadcast Playroom v3.6', '--notes-file', str(notes))

for path in [*patches, staged]:
    print(f"Uploading {path.name}...")
    gh('release', 'upload', 'v3.6', str(path), '--repo', 'zepiam/broadcast-playroom-3')

print("Publishing and setting v3.6 as latest...")
gh('release', 'edit', 'v3.6', '--repo', 'zepiam/broadcast-playroom-3', '--draft=false', '--latest')

print("\n--- Step 4: Update version.json on master branch via GitHub API ---")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.6 - Fix popout header buttons and cross-window platform sync',
    'sha': current['sha'],
    'content': base64.b64encode(staged.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated version.json on master commit:', result['commit']['sha'])

print("\n--- Step 5: Verify Live Updater against GitHub ---")
import urllib.request
req = urllib.request.Request("https://api.github.com/repos/zepiam/broadcast-playroom-3/releases/latest", headers={"User-Agent": "BroadcastPlayroom-Updater/3.5"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("GitHub Latest Tag:", data['tag_name'])
    assert data['tag_name'] == 'v3.6', f"Expected v3.6, got {data['tag_name']}"

print("\nSUCCESS: v3.6 RELEASE IS FULLY PUBLISHED AND VERIFIED ON GITHUB!")
