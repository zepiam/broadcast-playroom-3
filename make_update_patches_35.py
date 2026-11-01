import hashlib, json, zipfile
from pathlib import Path

root = Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

report = {}
trials = [
    ('Lite', 'trial-20261101-021316-344792', root / 'build_trials/lite/BroadcastPlayroom3-Lite'),
    ('Full', 'trial-20261101-021556-140248', Path(r'E:\DOCS\Documents\BroadcastPlayroom3\full'))
]

for edition, trial, baseline in trials:
    source = root / 'build_trials' / trial / 'dist' / ('BroadcastPlayroom3-' + edition)
    output = root / 'build_trials' / ('BroadcastPlayroom3-' + edition + '-Patch-3.5.zip')
    included = []
    
    # Ensure version.json is updated in source
    ver_data = json.dumps({'product': 'broadcast-playroom-3', 'version': '3.5', 'build_type': edition.lower()}, indent=2).encode('utf-8')
    (source / 'version.json').write_bytes(ver_data)
    (source / '_internal' / 'version.json').write_bytes(ver_data)
    
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
        # Ensure version.json entries are in zip
        if 'version.json' not in included:
            archive.write(source / 'version.json', 'version.json')
            included.append('version.json')
        if '_internal/version.json' not in included:
            archive.write(source / '_internal' / 'version.json', '_internal/version.json')
            included.append('_internal/version.json')

    # Verify archive integrity
    with zipfile.ZipFile(output) as check:
        assert check.testzip() is None
        assert json.loads(check.read('version.json'))['version'] == '3.5'
        assert json.loads(check.read('_internal/version.json'))['version'] == '3.5'

    size = output.stat().st_size
    d = digest(output)
    report[edition.lower()] = {
        'file': str(output),
        'size': size,
        'sha256': d,
        'entries': included,
        'baseline': str(baseline)
    }
    print(f"Created {edition} Patch-3.5: {size:,} bytes, {len(included)} modified files, SHA256: {d}", flush=True)

(root / 'build_trials/patch-report-3.5.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print("All patches created and verified successfully!", flush=True)
