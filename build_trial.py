"""Build a new, local-only trial without replacing an existing output."""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('edition', choices=('lite', 'full'))
args = parser.parse_args()
output = root / 'build_trials' / ('trial-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
output.mkdir(parents=True, exist_ok=False)
subprocess.run(['npm.cmd', 'run', 'build'], cwd=root, check=True)
name = 'BroadcastPlayroom3-' + args.edition.capitalize()
command = [sys.executable, '-m', 'PyInstaller', '--onedir', '--name', name,
           '--distpath', str(output / 'dist'), '--workpath', str(output / 'work'),
           '--specpath', str(output), '--add-data', str(root / 'dist') + ';dist',
           '--add-data', str(root / 'src' / 'assets') + ';src/assets',
           '--icon', str(root / 'src' / 'assets' / ('icon_' + args.edition + '.ico')),
           '--collect-all', 'edge_tts']
for module in ('desktop_overlay_qt', 'edge_tts', 'chat_twitch', 'chat_kick', 'chat_soop',
               'chat_mylive', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebChannel'):
    command += ['--hidden-import', module]
for module in ('tensorflow', 'matplotlib', 'IPython'):
    command += ['--exclude-module', module]
if args.edition == 'lite':
    for module in ('torch', 'torchaudio', 'torchvision', 'rvc_python', 'fairseq'):
        command += ['--exclude-module', module]
else:
    command += ['--hidden-import', 'package_numba_cache']
    for module in ('rvc_python', 'fairseq'):
        command += ['--collect-all', module]
subprocess.run(command + [str(root / 'package_entry.py')], cwd=root, check=True)
icu = output / 'dist' / name / '_internal' / 'icuuc.dll'
if icu.exists():
    # This Python environment contributes an incompatible ICU with this name;
    # Qt uses the Windows system ICU when it is absent from the application root.
    icu.unlink()
# Timestamped shout imports are local media, not default product resources.
for folder in ('dist/assets', 'src/assets'):
    for imported in (output / 'dist' / name / '_internal' / folder).glob('shout_*'):
        if imported.is_file():
            imported.unlink()
print('LOCAL TRIAL ONLY:', output / 'dist' / name)
