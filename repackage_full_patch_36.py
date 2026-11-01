import base64
import hashlib
import json
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

print("--- Repackaging Full Patch 3.6 to be Fully Cumulative ---")
patch_35 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.5.zip'
patch_36 = root / 'build_trials/BroadcastPlayroom3-Full-Patch-3.6.zip'

# Read all entries from patch_35
with zipfile.ZipFile(patch_35) as p35, zipfile.ZipFile(patch_36, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as p36:
    for entry in p35.infolist():
        # Skip version.json and dist files that we will override from dist/
        if entry.filename in ('version.json', '_internal/version.json'):
            continue
        if entry.filename.startswith('_internal/dist/'):
            continue
        p36.writestr(entry, p35.read(entry))

    # Write all updated dist files
    dist_dir = root / 'dist'
    for item in dist_dir.rglob('*'):
        if item.is_file() and not item.name.startswith('shout_'):
            rel = item.relative_to(dist_dir).as_posix()
            p36.write(item, f'_internal/dist/{rel}')

    # Write version 3.6
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.6', 'build_type': 'full'}, indent=2).encode('utf-8')
    p36.writestr('version.json', ver_data)
    p36.writestr('_internal/version.json', ver_data)

# Validate archive
with zipfile.ZipFile(patch_36) as check:
    assert check.testzip() is None
    assert json.loads(check.read('version.json'))['version'] == '3.6'
    assert json.loads(check.read('_internal/version.json'))['version'] == '3.6'
    assert '_internal/dist/index.html' in check.namelist()
    assert 'BroadcastPlayroom3-Full.exe' in check.namelist()

size = patch_36.stat().st_size
d = digest(patch_36)
print(f"Created Cumulative Full Patch-3.6: {size:,} bytes, SHA256: {d}")

# Update version.json
manifest = json.loads((root / 'version.json').read_text(encoding='utf-8'))
manifest['full'] = {
    'type': 'patch',
    'url': f'https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.6/{patch_36.name}',
    'size': size,
    'sha256': d
}
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

# Upload to GitHub Release v3.6
print("Uploading updated Full Patch 3.6 to GitHub...")
gh('release', 'upload', 'v3.6', str(patch_36), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

# Upload updated version.json to release
staged = root / 'build_trials/patch-publish-3.6/version.json'
staged.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
gh('release', 'upload', 'v3.6', str(staged), '--clobber', '--repo', 'zepiam/broadcast-playroom-3')

# Update version.json on master branch
print("Updating version.json on master branch...")
current = json.loads(gh('api', 'repos/zepiam/broadcast-playroom-3/contents/version.json'))
payload = {
    'message': 'Release v3.6 - Cumulative Full Patch and UI fixes',
    'sha': current['sha'],
    'content': base64.b64encode(staged.read_bytes()).decode(),
    'branch': 'master'
}
result = json.loads(gh('api', '--method', 'PUT', 'repos/zepiam/broadcast-playroom-3/contents/version.json', '--input', '-', input=json.dumps(payload).encode()))
print('Updated master commit:', result['commit']['sha'])

print("Cumulative Full Patch 3.6 published successfully!")
