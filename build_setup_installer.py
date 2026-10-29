import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
icon_path = root / 'src' / 'assets' / 'icon.ico'
icon_png = root / 'src' / 'assets' / 'icon.png'
dist_dir = root / 'dist_releases'
dist_dir.mkdir(parents=True, exist_ok=True)

cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--name', 'BroadcastPlayroom3-Setup',
    '--distpath', str(dist_dir),
    '--icon', str(icon_path),
    '--add-data', f'{root / "src" / "assets"};src/assets',
    '--add-data', f'{root / "assets" / "icons"};assets/icons',
    '--exclude-module', 'torch',
    '--exclude-module', 'torchaudio',
    '--exclude-module', 'torchvision',
    '--exclude-module', 'fairseq',
    '--exclude-module', 'scipy',
    '--exclude-module', 'matplotlib',
    '--exclude-module', 'playwright',
    '--exclude-module', 'IPython',
    str(root / 'installer_gui.py')
]

print("Building BroadcastPlayroom3-Setup.exe...")
subprocess.run(cmd, cwd=root, check=True)
print("Setup installer built successfully into dist_releases/BroadcastPlayroom3-Setup.exe!")
