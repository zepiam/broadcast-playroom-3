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
               'chat_mylive', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebChannel',
               'app_window_frame', 'win32crypt', 'psutil', 'win32gui', 'win32process', 'win32con'):
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

# Patch PE subsystem to Windows GUI (2)
def patch_pe_subsystem_to_gui(exe_path):
    import struct
    try:
        with open(exe_path, "r+b") as f:
            f.seek(0x3C)
            pe_offset = struct.unpack("<I", f.read(4))[0]
            sub_offset = pe_offset + 0x5C
            f.seek(sub_offset)
            current_sub = struct.unpack("<H", f.read(2))[0]
            if current_sub == 3:
                f.seek(sub_offset)
                f.write(struct.pack("<H", 2))
                print(f"Patched {exe_path.name} to Windows GUI (no console) successfully!")
    except Exception as e:
        print(f"Error patching PE subsystem: {e}")

exe_file = output / 'dist' / name / (name + '.exe')
if exe_file.exists():
    patch_pe_subsystem_to_gui(exe_file)

print('LOCAL TRIAL ONLY:', output / 'dist' / name)
