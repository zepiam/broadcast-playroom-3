"""Entry point for experimental packaged editions."""
import multiprocessing
import os
import site
import sys
from pathlib import Path

if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    # Frozen Python skips site initialization; some RVC dependencies expect help.
    site.sethelper()
    multiprocessing.freeze_support()
    if '--desktop-overlay' in sys.argv:
        sys.argv.remove('--desktop-overlay')
        import runpy
        runpy.run_module('desktop_overlay_qt', run_name='__main__')
    else:
        edition = 'lite' if 'lite' in Path(sys.executable).stem.lower() else 'full'
        os.environ['BP3_EDITION'] = edition
        data_dir = Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'BroadcastPlayroom3' / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        os.environ['BP3_DATA_DIR'] = str(data_dir)
        cache_dir = data_dir / 'numba_cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault('NUMBA_CACHE_DIR', str(cache_dir))
        if edition == 'full':
            os.environ.setdefault('NUMBA_CACHE_LOCATOR_CLASSES', 'package_numba_cache.FrozenDataCacheLocator,UserWideCacheLocator')
        from launch_dev import main
        raise SystemExit(main())
