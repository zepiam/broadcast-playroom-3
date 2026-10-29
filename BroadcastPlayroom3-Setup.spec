# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\DOCS\\Documents\\AI TOOLS\\broadcast playroom 3\\installer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\DOCS\\Documents\\AI TOOLS\\broadcast playroom 3\\src\\assets', 'src/assets'), ('E:\\DOCS\\Documents\\AI TOOLS\\broadcast playroom 3\\assets\\icons', 'assets/icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torchaudio', 'torchvision', 'fairseq', 'scipy', 'matplotlib', 'playwright', 'IPython'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BroadcastPlayroom3-Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['E:\\DOCS\\Documents\\AI TOOLS\\broadcast playroom 3\\src\\assets\\icon.ico'],
)
