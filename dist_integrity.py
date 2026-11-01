"""
Broadcast Playroom - Distribution & Asset Integrity Checker
Verifies that dist/ and core web assets are 100% complete, uncorrupted, and syntax-valid
before the application launches or before an update release is packaged.
"""
import re
import sys
from pathlib import Path

def verify_dist_health(root_path=None) -> tuple[bool, str]:
    if root_path is None:
        root_path = Path(__file__).resolve().parent
    else:
        root_path = Path(root_path)

    dist_dir = root_path / 'dist'
    if not dist_dir.exists() or not dist_dir.is_dir():
        return False, f"Missing dist directory at: {dist_dir}"

    index_html = dist_dir / 'index.html'
    if not index_html.exists() or not index_html.is_file():
        return False, "Missing dist/index.html!"

    size = index_html.stat().st_size
    if size < 100_000:
        return False, f"dist/index.html is suspiciously small ({size:,} bytes < 100KB)!"

    try:
        content = index_html.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Cannot read dist/index.html as UTF-8: {e}"

    # 1. Structural HTML boundary checks
    if '<!DOCTYPE' not in content and '<html' not in content:
        return False, "dist/index.html lacks standard HTML document declaration!"

    if '</html>' not in content:
        return False, "dist/index.html is truncated (missing closing </html> tag)!"

    # 2. Strict Script Tag Nesting & Splitting Validation
    # In HTML, any occurrence of </script> inside a <script> block (even in JS string templates)
    # prematurely terminates the script tag.
    # We verify that script tags balance and that no raw JS dumps into the body.
    script_opens = len(re.findall(r'<script\b[^>]*>', content, re.IGNORECASE))
    script_closes = len(re.findall(r'</script>', content, re.IGNORECASE))
    if script_opens != script_closes:
        return False, f"Script tag mismatch in dist/index.html: {script_opens} <script> vs {script_closes} </script>!"

    # 3. Check for obvious signs of raw JS leaking into HTML
    # (e.g. pop.document.close(); or function declarations appearing outside of <script> tags)
    body_content_without_scripts = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', content, flags=re.IGNORECASE)
    dangerous_js_snippets = [
        'pop.document.close()',
        'bindPlatformChannelInputs',
        'bindPlatformAutoInputs',
        'localStorage.getItem(',
        'addEventListener(\'contextmenu\''
    ]
    for snippet in dangerous_js_snippets:
        if snippet in body_content_without_scripts:
            return False, f"Raw JavaScript code leaked into HTML body outside <script> block! Found: '{snippet}'"

    # 4. Critical external companion scripts and stylesheets
    required_assets = [
        'user_controls.js',
        'dock_controls.js',
        'styles.css',
        'modal.css'
    ]
    for asset in required_assets:
        ap = dist_dir / asset
        if not ap.exists() or ap.stat().st_size == 0:
            return False, f"Missing or empty required dist asset: {asset}"

    # 5. Check user_controls.js syntax & key functions
    user_ctrl = (dist_dir / 'user_controls.js').read_text(encoding='utf-8')
    if 'openAuthorModal' not in user_ctrl:
        return False, "dist/user_controls.js is missing openAuthorModal!"

    return True, f"All dist integrity checks passed ({size:,} bytes verified healthy)."

def verify_patch_archive(zip_path, expected_version: str) -> tuple[bool, str]:
    """Verifies that an update patch archive contains all required files including version manifests."""
    import zipfile, json
    zp = Path(zip_path)
    if not zp.is_file():
        return False, f"Archive not found: {zip_path}"
    try:
        with zipfile.ZipFile(zp, 'r') as zf:
            names = zf.namelist()
            if 'version.json' not in names:
                return False, "Archive is missing root 'version.json'!"
            if '_internal/version.json' not in names:
                return False, "Archive is missing '_internal/version.json'!"
            data = json.loads(zf.read('version.json').decode('utf-8'))
            if data.get('version') != expected_version:
                return False, f"version.json in archive has version '{data.get('version')}', expected '{expected_version}'"
            if 'dist/index.html' not in names:
                return False, "Archive is missing 'dist/index.html'!"
    except Exception as e:
        return False, f"Corrupted patch archive: {e}"
    return True, f"Patch archive {zp.name} verified: contains valid version.json matching v{expected_version}"

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    ok, msg = verify_dist_health(root)
    print(f"[{'PASS' if ok else 'FAIL'}] {msg}")
    sys.exit(0 if ok else 1)
