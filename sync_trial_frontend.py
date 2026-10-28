"""Update trial index and its CSS as one coherent static frontend revision."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import os, shutil, tempfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'dist'
TARGETS = [ROOT / 'build_trials' / edition / name / '_internal' / 'dist' for edition, name in (
    ('lite', 'BroadcastPlayroom3-Lite'), ('full', 'BroadcastPlayroom3-Full'))]

class References(HTMLParser):
    def __init__(self):
        super().__init__(); self.styles = []; self.scripts = []
    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'link' and 'stylesheet' in attr.get('rel', '').split():
            self.styles.append(attr.get('href', ''))
        if tag == 'script' and attr.get('src'):
            self.scripts.append(attr['src'])

def local_path(url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path: return None
    relative = Path(unquote(parsed.path).lstrip('/'))
    if any(part == '..' for part in relative.parts): raise ValueError('Unsafe asset path')
    return relative

def main():
    html = (SOURCE / 'index.html').read_text(encoding='utf-8')
    parser = References(); parser.feed(html)
    styles = list(dict.fromkeys(path for value in parser.styles if (path := local_path(value)) is not None))
    scripts = list(dict.fromkeys(path for value in parser.scripts if (path := local_path(value)) is not None))
    if not styles: raise ValueError('No local stylesheets in index')
    for target in TARGETS:
        if not target.is_dir(): raise FileNotFoundError(f'Missing trial: {target}')
        for path in styles:
            if not (SOURCE / path).is_file(): raise FileNotFoundError(f'Missing source stylesheet: {path}')
        for path in scripts:
            if not (target / path).is_file(): raise FileNotFoundError(f'Missing trial script: {target / path}')
    for target in TARGETS:
        # Copy dependencies before publishing the new index, so it never points
        # to a not-yet-copied stylesheet during an update.
        for path in styles:
            (target / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / path, target / path)
        fd, temporary = tempfile.mkstemp(prefix='.index-', suffix='.tmp', dir=target)
        try:
            with os.fdopen(fd, 'wb') as stream: stream.write((SOURCE / 'index.html').read_bytes())
            os.replace(temporary, target / 'index.html')
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
        print(f'Updated {target}: {len(styles)} stylesheets, {len(scripts)} script references checked')

if __name__ == '__main__': main()
