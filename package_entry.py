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

    if '--splash-subprocess' in sys.argv:
        from splash import run_splash_subprocess
        raise SystemExit(run_splash_subprocess())

    if '--desktop-overlay' in sys.argv:
        sys.argv.remove('--desktop-overlay')
        import runpy
        runpy.run_module('desktop_overlay_qt', run_name='__main__')
    else:
        edition = 'lite' if 'lite' in Path(sys.executable).stem.lower() else 'full'
        os.environ['BP3_EDITION'] = edition

        # Unified root structure detection (<Root>/full or <Root>/lite -> shared <Root>/data)
        exe_dir = Path(sys.executable).parent
        parent_data = exe_dir.parent / 'data'
        local_data = exe_dir / 'data'
        portable_flag = exe_dir.parent / '.portable'
        
        if (exe_dir.parent / 'full').is_dir() or (exe_dir.parent / 'lite').is_dir() or parent_data.is_dir() or portable_flag.is_file():
            data_dir = parent_data
        elif local_data.is_dir() or (exe_dir / '.portable').is_file():
            data_dir = local_data
        else:
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
