"""Smoke-check a packaged build in an isolated temporary profile; no live chat."""
import json, os, shutil, subprocess, sys, tempfile, time, urllib.error, urllib.request
from pathlib import Path
import psutil
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

class StyleLinks(HTMLParser):
    def __init__(self): super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'link' and 'stylesheet' in attr.get('rel', '').split(): self.links.append(attr.get('href', ''))

exe = Path(sys.argv[1]).resolve()
edition = sys.argv[2]
with tempfile.TemporaryDirectory(prefix='bp3-package-') as directory:
    env = dict(os.environ, LOCALAPPDATA=directory, USERPROFILE=directory, HOME=directory)
    if os.environ.get('BP3_TEST_LOCATOR') == '1':
        cache_dir = Path(directory) / 'numba_cache'
        cache_dir.mkdir()
        env['NUMBA_CACHE_DIR'] = str(cache_dir)
    else:
        env.pop('NUMBA_CACHE_DIR', None)
        env.pop('NUMBA_CACHE_LOCATOR_CLASSES', None)
    if os.environ.get('BP3_TEST_DISABLE_JIT') == '1': env['NUMBA_DISABLE_JIT'] = '1'
    if os.environ.get('BP3_TEST_LOCATOR') == '1': env['NUMBA_CACHE_LOCATOR_CLASSES'] = 'package_numba_cache.FrozenDataCacheLocator,UserWideCacheLocator'
    if len(sys.argv) > 3 and sys.argv[3] != '--overlay':
        model_dir = Path(directory) / 'BroadcastPlayroom3' / 'data' / 'rvc_models'
        model_dir.mkdir(parents=True)
        shutil.copyfile(sys.argv[3], model_dir / 'test-model.pth')
    output = Path(directory) / 'output.log'
    with output.open('w', encoding='utf-8') as log:
        process = subprocess.Popen([str(exe)], env=env, cwd=directory, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        try:
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('Application exited during startup: ' + output.read_text(encoding='utf-8', errors='replace')[-4000:])
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8801/api/app-instance', timeout=2) as response:
                        result = json.load(response)
                    if result.get('edition') == edition:
                        break
                except (OSError, ValueError):
                    pass
                time.sleep(.5)
            else: raise RuntimeError('Server did not start')
            with urllib.request.urlopen('http://127.0.0.1:8801/index.html', timeout=5) as response:
                html = response.read().decode('utf-8')
                assert 'Broadcast Playroom' in html
            links = StyleLinks(); links.feed(html)
            local_styles = [link for link in links.links if not urlsplit(link).netloc and not urlsplit(link).scheme]
            assert local_styles, 'No local stylesheets'
            for link in local_styles:
                with urllib.request.urlopen(urljoin('http://127.0.0.1:8801/index.html', link), timeout=5) as response:
                    assert response.status == 200 and response.headers.get_content_type() == 'text/css' and response.read(), link
            with urllib.request.urlopen('http://127.0.0.1:8801/api/capabilities', timeout=5) as response:
                capabilities = json.load(response)
            assert capabilities['edition'] == edition and capabilities['rvc'] == (edition == 'full')
            if edition == 'lite':
                try: urllib.request.urlopen('http://127.0.0.1:8801/api/rvc/models', timeout=5)
                except urllib.error.HTTPError as error: assert error.code == 403
                else: raise AssertionError('Lite accepted RVC models request')
                if len(sys.argv) > 3 and sys.argv[3] == '--overlay':
                    request = urllib.request.Request('http://127.0.0.1:8801/api/desktop-overlays',
                        data=json.dumps({'action': 'toggle', 'kind': 'viewer'}).encode(),
                        headers={'Content-Type': 'application/json'}, method='POST')
                    with urllib.request.urlopen(request, timeout=10) as response: json.load(response)
                    deadline = time.monotonic() + 90
                    while time.monotonic() < deadline:
                        with urllib.request.urlopen('http://127.0.0.1:8801/api/desktop-overlays', timeout=5) as response:
                            instances = json.load(response)['instances']
                        if instances and instances[0].get('ready'): break
                        time.sleep(.5)
                    else: raise RuntimeError('Desktop overlay did not become ready')
                    print('Packaged desktop viewer overlay startup: PASS')
            elif len(sys.argv) > 3:
                with urllib.request.urlopen('http://127.0.0.1:8801/api/rvc/models', timeout=5) as response:
                    models = json.load(response)['models']
                assert len(models) == 1
                request = urllib.request.Request('http://127.0.0.1:8801/api/rvc/select',
                    data=json.dumps({'id': models[0]['id'], 'enabled': True}).encode(),
                    headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(request, timeout=10) as response: json.load(response)
                deadline = time.monotonic() + 180
                while time.monotonic() < deadline:
                    with urllib.request.urlopen('http://127.0.0.1:8801/api/rvc/status', timeout=5) as response:
                        status = json.load(response)
                    if status.get('loaded'): break
                    if status.get('state') == 'error':
                        raise RuntimeError('RVC load failed: ' + str(status.get('error')) + '\n' + output.read_text(encoding='utf-8', errors='replace')[-6000:])
                    time.sleep(1)
                else: raise RuntimeError('RVC load timed out')
                print('Packaged real model load: PASS')
                if len(sys.argv) > 4 and sys.argv[4] == '--voice':
                    with urllib.request.urlopen('http://127.0.0.1:8801/api/tts?text=hello', timeout=120) as response:
                        audio = response.read()
                        if response.headers.get_content_type() != 'audio/wav':
                            raise RuntimeError('RVC conversion returned fallback audio\n' + output.read_text(encoding='utf-8', errors='replace')[-6000:])
                    assert audio.startswith(b'RIFF') and len(audio) > 44
                    print('Packaged Edge TTS + real RVC conversion: PASS')
            print('Packaged startup and main page:', edition, 'PASS')
        finally:
            try:
                owned = psutil.Process(process.pid)
                children = owned.children(recursive=True)
                owned.terminate()
                for child in children:
                    try: child.terminate()
                    except psutil.Error: pass
                psutil.wait_procs([owned, *children], timeout=8)
            except psutil.Error: pass
