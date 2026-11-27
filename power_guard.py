"""power_guard.py - keep Broadcast Playroom 3 running for hours while idle (v3.77).

What it does (Windows; every step is best-effort and never raises):
  1. Keep-awake: asks Windows not to enter system sleep while the program runs
     (SetThreadExecutionState ES_SYSTEM_REQUIRED; the display may still turn off).
  2. Opt out of Windows "Efficiency mode" (EcoQoS power throttling) for this process and for
     the app's browser processes, so background work is not slowed down.
  3. UI watchdog: the main page sends a heartbeat every ~10 s (/api/ui/heartbeat). If the browser
     process is still alive but heartbeats stop for HANG_SECONDS (page frozen / slept / grey),
     the app window is restarted (max 3 times per hour, restored to normal view).
  4. Native Windows Process Management: handles process tree killing and tracking directly
     without requiring third-party libraries like psutil.
  5. Writes <data>/ui_health.log (page heap size every 5 min and every recovery) for diagnosis.

Opt-out: create <data>/power_settings.json
  {"keep_awake": false, "watchdog": false, "no_efficiency_mode": false, "disable_gpu": false}
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

HANG_SECONDS = 180          # page silent this long (heartbeat is 10 s) => treat as hung
STARTUP_GRACE = 240         # seconds after (re)launch before the watchdog may act
PAGE_LOST_SECONDS = 35      # page disconnected + browser alive this long (and no heartbeat 45 s) => restart sooner
MAX_RECOVERIES_PER_HOUR = 3
LOOP_SECONDS = 15

_lock = threading.Lock()
_state = {
    'last_beat': 0.0, 'beats': 0, 'heap_mb': None,
    'launched_at': 0.0, 'recoveries': [], 'started': False,
    'last_mem_log': 0.0,
}
_cfg = {'profile_dir': '', 'data_dir': '', 'relaunch': None}
_active_browser_proc = None


def register_browser_process(proc) -> None:
    """Register the active subprocess.Popen instance of the app browser."""
    global _active_browser_proc
    _active_browser_proc = proc


def terminate_browser() -> None:
    """Terminate registered browser process and any child processes cleanly."""
    global _active_browser_proc
    if _active_browser_proc is not None:
        try:
            _active_browser_proc.terminate()
            _active_browser_proc.wait(timeout=2)
        except Exception:
            try:
                _active_browser_proc.kill()
            except Exception:
                pass
        _active_browser_proc = None
    for p in _browser_processes():
        try:
            p.terminate()
        except Exception:
            pass


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
    values = {'keep_awake': True, 'watchdog': True, 'no_efficiency_mode': True, 'disable_gpu': False}
    try:
        file = _data_dir() / 'power_settings.json'
        if file.is_file():
            values.update({k: bool(v) for k, v in json.loads(file.read_text(encoding='utf-8')).items() if k in values})
    except Exception:
        pass
    return values


def beat(heap_mb=None, geometry=None, hidden=None) -> None:
    """Called by the /api/ui/heartbeat endpoint.
    geometry = (x, y, w, h) of the app window while it was visible; hidden = window minimized/hidden."""
    with _lock:
        _state['last_beat'] = time.time()
        _state['beats'] += 1
        _state['page_lost_at'] = 0.0
        if heap_mb is not None and heap_mb >= 0:
            _state['heap_mb'] = heap_mb
        if geometry:
            _state['window_geometry'] = tuple(int(v) for v in geometry)
        if hidden is not None:
            _state['window_hidden'] = bool(hidden)


def last_window():
    """(geometry or None, was_hidden) last reported by the app page: a watchdog restart reopens the
    window where the user had it (e.g. on a second monitor) and keeps it minimized if it was."""
    with _lock:
        return _state.get('window_geometry'), bool(_state.get('window_hidden'))


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


def _main_browser_alive(procs=None) -> bool:
    global _active_browser_proc
    if _active_browser_proc is not None:
        try:
            return _active_browser_proc.poll() is None
        except Exception:
            pass
    if procs:
        for proc in procs:
            try:
                cmd = ' '.join(proc.info.get('cmdline') or [])
                if '--type=' not in cmd:
                    return True
            except Exception:
                continue
    return False


def page_lost() -> None:
    """The app page dropped its connection while the browser is still running (grey/crashed page).
    Lets the watchdog restart the window after PAGE_LOST_SECONDS instead of the full HANG_SECONDS."""
    with _lock:
        if not _state.get('page_lost_at'):
            _state['page_lost_at'] = time.time()


def browser_alive() -> bool:
    """Public: the app window's browser main process is still running (or the watchdog is
    in the middle of restarting it, so the program must not quit during that gap)."""
    with _lock:
        if _state.get('recovering_until', 0) > time.time():
            return True
    return _main_browser_alive(None if _active_browser_proc is not None else _browser_processes())


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
        valid_pids = set(filter(None, pids))
        global _active_browser_proc
        if _active_browser_proc is not None and _active_browser_proc.poll() is None:
            valid_pids.add(_active_browser_proc.pid)
        for pid in valid_pids:
            try:
                handle = kernel32.OpenProcess(0x0200, False, int(pid))   # PROCESS_SET_INFORMATION
                if not handle:
                    continue
                try:
                    kernel32.SetProcessInformation(handle, 4, ctypes.byref(state), ctypes.sizeof(state))  # ProcessPowerThrottling
                finally:
                    kernel32.CloseHandle(handle)
            except Exception:
                pass
    except Exception:
        pass


def _recover() -> None:
    now = time.time()
    with _lock:
        _state['recoveries'] = [t for t in _state['recoveries'] if now - t < 3600]
        if len(_state['recoveries']) >= MAX_RECOVERIES_PER_HOUR:
            return
        _state['recoveries'].append(now)
        _state['recovering_until'] = now + 60
        heap = _state['heap_mb']
        silent = int(now - _state['last_beat'])
    _log('UI watchdog: no heartbeat for %ss while browser is alive (last page heap %s MB) -> restarting app window' % (silent, heap))
    try:
        global _active_browser_proc
        # 1. Native Windows tree-kill of the main browser process and all its sub-processes
        if _active_browser_proc is not None and _active_browser_proc.poll() is None:
            try:
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(_active_browser_proc.pid)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        # 2. Cleanup any lingering processes for this app profile via psutil if available
        for proc in _browser_processes():
            try:
                proc.kill()
            except Exception:
                pass

        time.sleep(1.5)
        relaunch = _cfg['relaunch']
        if callable(relaunch):
            relaunch()
        with _lock:
            _state['launched_at'] = time.time()
            _state['last_beat'] = 0.0
            _state['beats'] = 0
            _state['page_lost_at'] = 0.0
            _state['recovering_until'] = 0.0   # new window launched: normal close may exit again
    except Exception as error:
        with _lock:
            _state['recovering_until'] = 0.0
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
                pids = [os.getpid()] + [p.pid for p in procs]
                _disable_efficiency_mode(pids)
            with _lock:
                last_beat, beats, launched = _state['last_beat'], _state['beats'], _state['launched_at']
                heap = _state['heap_mb']
                last_mem = _state['last_mem_log']
                lost_at = _state.get('page_lost_at') or 0.0
            if beats and now - last_mem > 300:
                with _lock:
                    _state['last_mem_log'] = now
                _log('ok: page heap %s MB, heartbeats %s' % (heap, beats))
            hung = now - last_beat > HANG_SECONDS and now - launched > STARTUP_GRACE
            lost = bool(lost_at) and now - lost_at >= PAGE_LOST_SECONDS and now - last_beat >= 45
            if cfg['watchdog'] and beats and (hung or lost):
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
