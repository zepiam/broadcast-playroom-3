"""power_guard.py - keep Broadcast Playroom 3 running for hours while idle (v3.76).

What it does (Windows; every step is best-effort and never raises):
  1. Keep-awake: asks Windows not to enter system sleep while the program runs
     (SetThreadExecutionState ES_SYSTEM_REQUIRED; the display may still turn off).
  2. Opt out of Windows "Efficiency mode" (EcoQoS power throttling) for this process and for
     the app's browser processes, so background work is not slowed down.
  3. UI watchdog: the main page sends a heartbeat every ~10 s (/api/ui/heartbeat). If the browser
     process is still alive but heartbeats stop for HANG_SECONDS (page frozen / slept / grey),
     the app window is restarted (max 3 times per hour, minimised so it does not steal focus).
  4. Writes <data>/ui_health.log (page heap size every 5 min and every recovery) for diagnosis.

Opt-out: create <data>/power_settings.json  {"keep_awake": false, "watchdog": false, "no_efficiency_mode": false}
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

HANG_SECONDS = 180          # page silent this long (heartbeat is 10 s) => treat as hung
STARTUP_GRACE = 240         # seconds after (re)launch before the watchdog may act
MAX_RECOVERIES_PER_HOUR = 3
LOOP_SECONDS = 15

_lock = threading.Lock()
_state = {
    'last_beat': 0.0, 'beats': 0, 'heap_mb': None,
    'launched_at': 0.0, 'recoveries': [], 'started': False,
    'last_mem_log': 0.0,
}
_cfg = {'profile_dir': '', 'data_dir': '', 'relaunch': None}


def _data_dir() -> Path:
    return Path(_cfg['data_dir'] or os.environ.get('BP3_DATA_DIR') or '.')


def _log(message: str) -> None:
    try:
        base = _data_dir()
        base.mkdir(parents=True, exist_ok=True)
        log_file = base / 'ui_health.log'
        if log_file.is_file() and log_file.stat().st_size > 256 * 1024:
            log_file.replace(base / 'ui_health.old.log')
        with open(log_file, 'a', encoding='utf-8') as handle:
            handle.write('[%s] %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), message))
    except Exception:
        pass


def _settings() -> dict:
    values = {'keep_awake': True, 'watchdog': True, 'no_efficiency_mode': True}
    try:
        file = _data_dir() / 'power_settings.json'
        if file.is_file():
            values.update({k: bool(v) for k, v in json.loads(file.read_text(encoding='utf-8')).items() if k in values})
    except Exception:
        pass
    return values


def beat(heap_mb=None) -> None:
    """Called by the /api/ui/heartbeat endpoint."""
    with _lock:
        _state['last_beat'] = time.time()
        _state['beats'] += 1
        if heap_mb is not None and heap_mb >= 0:
            _state['heap_mb'] = heap_mb


def _keep_awake() -> None:
    if os.name != 'nt':
        return
    try:
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    except Exception:
        pass


def _release_awake() -> None:
    if os.name != 'nt':
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
    except Exception:
        pass


def _browser_processes():
    """Processes started with this app's --user-data-dir (browser main + children)."""
    result = []
    profile = (_cfg['profile_dir'] or '').lower()
    if not profile:
        return result
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmd = ' '.join(proc.info.get('cmdline') or []).lower()
                if profile in cmd:
                    result.append(proc)
            except Exception:
                continue
    except Exception:
        pass
    return result


def _main_browser_alive(procs) -> bool:
    for proc in procs:
        try:
            cmd = ' '.join(proc.info.get('cmdline') or [])
            if '--type=' not in cmd:
                return True
        except Exception:
            continue
    return False


def _disable_efficiency_mode(pids) -> None:
    if os.name != 'nt':
        return
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_POWER_THROTTLING_STATE(ctypes.Structure):
            _fields_ = [('Version', wintypes.ULONG), ('ControlMask', wintypes.ULONG), ('StateMask', wintypes.ULONG)]

        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.restype = wintypes.HANDLE
        state = PROCESS_POWER_THROTTLING_STATE(1, 0x1 | 0x4, 0)   # execution speed + timer resolution: force OFF
        for pid in pids:
            handle = kernel32.OpenProcess(0x0200, False, int(pid))   # PROCESS_SET_INFORMATION
            if not handle:
                continue
            try:
                kernel32.SetProcessInformation(handle, 4, ctypes.byref(state), ctypes.sizeof(state))  # ProcessPowerThrottling
            finally:
                kernel32.CloseHandle(handle)
    except Exception:
        pass


def _recover() -> None:
    now = time.time()
    with _lock:
        _state['recoveries'] = [t for t in _state['recoveries'] if now - t < 3600]
        if len(_state['recoveries']) >= MAX_RECOVERIES_PER_HOUR:
            return
        _state['recoveries'].append(now)
        heap = _state['heap_mb']
        silent = int(now - _state['last_beat'])
    _log('UI watchdog: no heartbeat for %ss while browser is alive (last page heap %s MB) -> restarting app window' % (silent, heap))
    try:
        for proc in _browser_processes():
            try:
                proc.kill()
            except Exception:
                pass
        time.sleep(2.0)
        relaunch = _cfg['relaunch']
        if callable(relaunch):
            relaunch()
        with _lock:
            _state['launched_at'] = time.time()
            _state['last_beat'] = 0.0
            _state['beats'] = 0
    except Exception as error:
        _log('UI watchdog: restart failed: %s' % error)


def _loop() -> None:
    last_throttle = 0.0
    while True:
        try:
            cfg = _settings()
            now = time.time()
            if cfg['keep_awake']:
                _keep_awake()
            else:
                _release_awake()
            procs = None
            if cfg['no_efficiency_mode'] and now - last_throttle > 60:
                last_throttle = now
                procs = _browser_processes()
                _disable_efficiency_mode([os.getpid()] + [p.pid for p in procs])
            with _lock:
                last_beat, beats, launched = _state['last_beat'], _state['beats'], _state['launched_at']
                heap = _state['heap_mb']
                last_mem = _state['last_mem_log']
            if beats and now - last_mem > 300:
                with _lock:
                    _state['last_mem_log'] = now
                _log('ok: page heap %s MB, heartbeats %s' % (heap, beats))
            if cfg['watchdog'] and beats and now - last_beat > HANG_SECONDS and now - launched > STARTUP_GRACE:
                if procs is None:
                    procs = _browser_processes()
                if _main_browser_alive(procs):
                    _recover()
                else:
                    # window was closed on purpose (or crashed): nothing to restart, wait for a new heartbeat
                    with _lock:
                        _state['beats'] = 0
                    _log('watchdog: browser process gone (window closed); watching stopped until the next heartbeat')
        except Exception:
            pass
        time.sleep(LOOP_SECONDS)


def start(profile_dir: str, data_dir: str = '', relaunch=None) -> None:
    """Idempotent. profile_dir = the app browser's --user-data-dir; relaunch() reopens the window."""
    _cfg['profile_dir'] = str(profile_dir or '')
    if data_dir:
        _cfg['data_dir'] = str(data_dir)
    if relaunch is not None:
        _cfg['relaunch'] = relaunch
    with _lock:
        _state['launched_at'] = time.time()
        if _state['started']:
            return
        _state['started'] = True
    threading.Thread(target=_loop, name='bp3-power-guard', daemon=True).start()
    _log('power_guard started (settings: %s)' % _settings())
