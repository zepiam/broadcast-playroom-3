"""Native frame controls restricted to the application's isolated browser profile."""
import os
import sys
import json
import threading
import time
import ctypes
from pathlib import Path

_watching = set()
_shortcut_registered = False
_main_webview = None
_is_shutting_down = False
_main_hwnd = None
_is_maximized = False

def set_app_shutting_down(val=True):
    global _is_shutting_down
    _is_shutting_down = bool(val)

def is_app_shutting_down():
    global _is_shutting_down
    return _is_shutting_down

def set_webview_window(w):
    global _main_webview, _main_hwnd
    _main_webview = w
    if w and hasattr(w, 'native') and w.native:
        try:
            _main_hwnd = w.native.Handle.ToInt64() if hasattr(w.native, 'Handle') else int(w.native)
        except Exception:
            pass

def bring_main_window_to_front():
    """Restores and brings the main window of Broadcast Playroom to the foreground."""
    global _main_hwnd, _main_webview
    if _main_webview:
        try:
            _main_webview.restore()
        except Exception:
            pass
        try:
            _main_webview.show()
        except Exception:
            pass

    if os.name != 'nt':
        return False

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    hwnd = _main_hwnd
    if not hwnd or not user32.IsWindow(hwnd):
        # 1. Try finding window with title 'Broadcast Playroom'
        hwnd = user32.FindWindowW(None, 'Broadcast Playroom')
        if not hwnd:
            # 2. Enumerate visible windows looking for 'Broadcast Playroom' in title
            candidates = []
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            def enum_cb(h, _):
                if user32.IsWindowVisible(h):
                    length = user32.GetWindowTextLengthW(h)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(h, buff, length + 1)
                        if 'Broadcast Playroom' in buff.value:
                            candidates.append(h)
                return True
            try:
                user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
            except Exception:
                pass
            if candidates:
                hwnd = candidates[0]

    if hwnd and user32.IsWindow(hwnd):
        _main_hwnd = hwnd
        SW_RESTORE = 9
        SW_SHOW = 5
        cur_thread = kernel32.GetCurrentThreadId()
        fore_hwnd = user32.GetForegroundWindow()
        fore_thread = user32.GetWindowThreadProcessId(fore_hwnd, None)
        if fore_thread != cur_thread:
            user32.AttachThreadInput(cur_thread, fore_thread, True)

        try:
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, SW_RESTORE)
            else:
                user32.ShowWindow(hwnd, SW_SHOW)

            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
            user32.SetActiveWindow(hwnd)
        except Exception:
            pass

        if fore_thread != cur_thread:
            user32.AttachThreadInput(cur_thread, fore_thread, False)
        return True
    return False

def get_webview_window():
    global _main_webview
    return _main_webview

def find_app_icon_path():
    root = Path(__file__).resolve().parent
    ed = os.environ.get('BP3_EDITION', 'full')
    candidates = [
        root / 'assets' / 'icons' / f'bp-{ed}-icon.ico',
        root / 'assets' / 'icons' / 'bp-full-icon.ico',
        root / 'dist' / 'assets' / f'icon_{ed}.ico',
        root / 'dist' / 'assets' / 'icon.ico',
        root / 'src' / 'assets' / f'icon_{ed}.ico',
        root / 'src' / 'assets' / 'icon.ico',
        root / 'dist' / 'favicon.ico',
        root / 'public' / 'favicon.ico',
        Path(sys.executable).parent / 'dist' / 'assets' / 'icon.ico',
        Path(sys.executable).parent / 'src' / 'assets' / 'icon.ico',
    ]
    for c in candidates:
        if c.is_file():
            return str(c.resolve())
    return None

def _ensure_app_shortcut(app_id, ico_path):
    global _shortcut_registered
    if _shortcut_registered:
        return
    try:
        from win32com.propsys import propsys, pscon
        import pythoncom
        import win32com.client
        programs_dir = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Broadcast Playroom'
        programs_dir.mkdir(parents=True, exist_ok=True)
        target_lnk = programs_dir / 'Broadcast Playroom 3 (Full).lnk'
        if not target_lnk.exists():
            shell = win32com.client.Dispatch("WScript.Shell")
            sc = shell.CreateShortCut(str(target_lnk))
            sc.TargetPath = sys.executable
            sc.WorkingDirectory = str(Path(ico_path).parents[2])
            sc.IconLocation = f"{ico_path},0"
            sc.Description = "Broadcast Playroom"
            sc.Save()
        # Set AppUserModelID on shortcut
        st = propsys.SHGetPropertyStoreFromParsingName(str(target_lnk), None, 2, propsys.IID_IPropertyStore)
        cur_id = st.GetValue(pscon.PKEY_AppUserModel_ID).GetValue()
        if cur_id != app_id:
            st.SetValue(pscon.PKEY_AppUserModel_ID, propsys.PROPVARIANTType(app_id, pythoncom.VT_LPWSTR))
            st.SetValue(pscon.PKEY_AppUserModel_RelaunchIconResource, propsys.PROPVARIANTType(f'"{ico_path}",0', pythoncom.VT_LPWSTR))
            st.Commit()
        _shortcut_registered = True
    except Exception:
        pass

def setup_app_window_icon(hwnd):
    global _main_hwnd
    if hwnd:
        _main_hwnd = hwnd
    if os.name != 'nt' or not hwnd:
        return False
    try:
        import win32gui, win32con
        ico_path = find_app_icon_path()
        if not ico_path or not os.path.isfile(ico_path):
            return False
        user32 = ctypes.windll.user32

        # Small icon (16x16) for window title bar / caption
        hicon_sm = win32gui.LoadImage(0, ico_path, win32con.IMAGE_ICON, 16, 16, win32con.LR_LOADFROMFILE)
        # Big icon (32x32) for Windows Taskbar & Alt+Tab
        hicon_bg = win32gui.LoadImage(0, ico_path, win32con.IMAGE_ICON, 32, 32, win32con.LR_LOADFROMFILE)

        if hicon_sm:
            user32.SendMessageW(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon_sm)
            try:
                user32.SetClassLongPtrW(hwnd, -34, hicon_sm) # GCLP_HICONSM (-34)
            except Exception:
                try:
                    win32gui.SetClassLong(hwnd, win32con.GCL_HICONSM, hicon_sm)
                except Exception:
                    pass

        if hicon_bg:
            user32.SendMessageW(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon_bg)
            try:
                user32.SetClassLongPtrW(hwnd, -14, hicon_bg) # GCLP_HICON (-14)
            except Exception:
                try:
                    win32gui.SetClassLong(hwnd, win32con.GCL_HICON, hicon_bg)
                except Exception:
                    pass

        # Ensure Start Menu / Programs shortcut exists and has the AppUserModelID and icon linked
        app_id = "men9ch.BroadcastPlayroom3"
        try:
            _ensure_app_shortcut(app_id, ico_path)
        except Exception:
            pass

        # Set AppUserModelID on the HWND so Windows Taskbar pins/groups it with BP3 icon
        try:
            from win32com.propsys import propsys, pscon
            import pythoncom
            store = propsys.SHGetPropertyStoreForWindow(hwnd)
            store.SetValue(pscon.PKEY_AppUserModel_ID, propsys.PROPVARIANTType(app_id, pythoncom.VT_LPWSTR))
            store.SetValue(pscon.PKEY_AppUserModel_RelaunchIconResource, propsys.PROPVARIANTType(f'"{ico_path}",0', pythoncom.VT_LPWSTR))
            store.Commit()
        except Exception:
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ctypes.c_wchar_p(app_id))
            except Exception:
                pass
        
        return True
    except Exception:
        return False

def apply_icon_to_app_windows():
    if os.name != 'nt':
        return False
    try:
        import psutil, win32gui, win32process
        applied = False
        def collect(hwnd, _):
            nonlocal applied
            if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                return
            txt = win32gui.GetWindowText(hwnd)
            cls = win32gui.GetClassName(hwnd)
            if 'Broadcast Playroom' not in txt and cls != 'Chrome_WidgetWin_1':
                return
            try:
                pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                proc = psutil.Process(pid)
                pname = proc.name().lower()
                if pname not in ('chrome.exe', 'msedge.exe', 'broadcastplayroom3-full.exe', 'broadcastplayroom3-lite.exe', 'python.exe'):
                    return
                if 'Broadcast Playroom' in txt or any('index.html' in a or 'browser_profile' in a for a in proc.cmdline()):
                    if setup_app_window_icon(hwnd):
                        applied = True
            except Exception:
                pass
        win32gui.EnumWindows(collect, None)
        return applied
    except Exception:
        return False

def _remember_window(hwnd):
    import win32gui, win32con
    setup_app_window_icon(hwnd)
    path = Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'BroadcastPlayroom3' / 'main_window.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        rect = tuple(int(v) for v in data['rect'])
        if len(rect) == 4 and rect[2] - rect[0] >= 320 and rect[3] - rect[1] >= 240:
            import win32api
            if any(rect[0] < m[2][2] and rect[2] > m[2][0] and rect[1] < m[2][3] and rect[3] > m[2][1] for m in win32api.EnumDisplayMonitors()):
                placement = win32gui.GetWindowPlacement(hwnd)
                win32gui.SetWindowPlacement(hwnd, (placement[0], win32con.SW_SHOWMAXIMIZED if data.get('maximized') else win32con.SW_SHOWNORMAL, placement[2], placement[3], rect))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    def watch():
        previous = None
        while win32gui.IsWindow(hwnd):
            try:
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] not in (win32con.SW_SHOWMINIMIZED, win32con.SW_MINIMIZE):
                    data = {'rect': list(placement[4]), 'maximized': placement[1] == win32con.SW_SHOWMAXIMIZED}
                    if data != previous:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        temporary = path.with_suffix('.tmp')
                        temporary.write_text(json.dumps(data), encoding='utf-8')
                        os.replace(temporary, path)
                        previous = data
            except Exception:
                pass
            time.sleep(0.5)
        _watching.discard(hwnd)
    threading.Thread(target=watch, daemon=True).start()

class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]

def setup_discord_frame(hwnd):
    try:
        import win32gui, win32con
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MAXIMIZEBOX | win32con.WS_MINIMIZEBOX | win32con.WS_SYSMENU
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.SetWindowRgn(hwnd, 0, True)
        win32gui.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED
        )
    except Exception as e:
        print(f"[WARN] setup_discord_frame failed: {e}", flush=True)

HT_RESIZE_MAP = {
    'left': 10,
    'right': 11,
    'top': 12,
    'top-left': 13,
    'top-right': 14,
    'bottom': 15,
    'bottom-left': 16,
    'bottom-right': 17,
}

def _do_native_resize(dir_name, target_hwnd=None):
    try:
        code = HT_RESIZE_MAP.get(str(dir_name).lower())
        if not code:
            return
        h = target_hwnd or _main_hwnd
        if not h and _main_webview and hasattr(_main_webview, 'native') and _main_webview.native:
            try:
                h = _main_webview.native.Handle.ToInt64() if hasattr(_main_webview.native, 'Handle') else int(_main_webview.native)
            except Exception:
                pass
        if h:
            VK_LBUTTON = 0x01
            if not (ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000):
                return
            WM_NCLBUTTONDOWN = 0x00A1
            ctypes.windll.user32.ReleaseCapture()
            import win32gui
            win32gui.PostMessage(h, WM_NCLBUTTONDOWN, code, 0)
    except Exception as e:
        print(f"[WARN] _do_native_resize error: {e}", flush=True)

def _do_native_drag(target_hwnd=None):
    try:
        h = target_hwnd or _main_hwnd
        if not h and _main_webview and hasattr(_main_webview, 'native') and _main_webview.native:
            try:
                h = _main_webview.native.Handle.ToInt64() if hasattr(_main_webview.native, 'Handle') else int(_main_webview.native)
            except Exception:
                pass
        if h:
            VK_LBUTTON = 0x01
            if not (ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000):
                return
            WM_NCLBUTTONDOWN = 0x00A1
            HTCAPTION = 2
            ctypes.windll.user32.ReleaseCapture()
            import win32gui
            win32gui.PostMessage(h, WM_NCLBUTTONDOWN, HTCAPTION, 0)
    except Exception as e:
        print(f"[WARN] _do_native_drag error: {e}", flush=True)

def action(command, data=None):
    if data is None:
        data = {}
    elif isinstance(data, str):
        data = {'direction': data}
    if command not in ('init', 'restore-frame', 'drag', 'resize', 'set-bounds', 'minimize', 'maximize', 'close', 'set-icon', 'snap'):
        raise ValueError('Unknown window action')
    global _main_webview
    if _main_webview:
        try:
            if command == 'minimize':
                _main_webview.minimize()
                return {'ok': True}
            elif command == 'drag':
                if hasattr(_main_webview, 'native') and _main_webview.native:
                    try:
                        from System import Action
                        _main_webview.native.BeginInvoke(Action(_do_native_drag))
                        return {'ok': True}
                    except Exception as e:
                        print(f"[WARN] BeginInvoke drag error: {e}", flush=True)
                _do_native_drag()
                return {'ok': True}
            elif command == 'resize':
                dir_name = data.get('direction', 'right') if isinstance(data, dict) else str(data)
                if hasattr(_main_webview, 'native') and _main_webview.native:
                    try:
                        from System import Action
                        _main_webview.native.BeginInvoke(Action(lambda: _do_native_resize(dir_name)))
                        return {'ok': True}
                    except Exception as e:
                        print(f"[WARN] BeginInvoke resize error: {e}", flush=True)
                _do_native_resize(dir_name)
                return {'ok': True}
            elif command == 'maximize':
                global _is_maximized, _main_hwnd
                is_currently_max = False
                if _main_hwnd:
                    try:
                        is_currently_max = bool(ctypes.windll.user32.IsZoomed(_main_hwnd))
                    except Exception:
                        pass
                if not is_currently_max and hasattr(_main_webview, 'native') and _main_webview.native:
                    try:
                        ws = getattr(_main_webview.native, 'WindowState', None)
                        if ws is not None:
                            is_currently_max = (str(ws) == 'Maximized' or int(ws) == 2)
                    except Exception:
                        pass
                if not is_currently_max and _is_maximized:
                    is_currently_max = True

                if is_currently_max:
                    try:
                        _main_webview.restore()
                    except Exception:
                        pass
                    _is_maximized = False
                    if _main_hwnd:
                        try:
                            import win32gui, win32con
                            win32gui.ShowWindow(_main_hwnd, win32con.SW_RESTORE)
                        except Exception:
                            pass
                    return {'ok': True, 'maximized': False}
                else:
                    try:
                        _main_webview.maximize()
                    except Exception:
                        pass
                    _is_maximized = True
                    if _main_hwnd:
                        try:
                            import win32gui, win32con
                            win32gui.ShowWindow(_main_hwnd, win32con.SW_MAXIMIZE)
                        except Exception:
                            pass
                    return {'ok': True, 'maximized': True}
            elif command == 'snap':
                dir_name = data.get('direction', 'left') if isinstance(data, dict) else str(data)
                h = _main_hwnd
                if not h and hasattr(_main_webview, 'native') and _main_webview.native:
                    try:
                        h = _main_webview.native.Handle.ToInt64() if hasattr(_main_webview.native, 'Handle') else int(_main_webview.native)
                    except Exception:
                        pass
                if h:
                    try:
                        import win32api, win32gui, win32con
                        if dir_name == 'maximize':
                            try:
                                _main_webview.maximize()
                            except Exception:
                                pass
                            win32gui.ShowWindow(h, win32con.SW_MAXIMIZE)
                            return {'ok': True, 'maximized': True, 'snapped': False}
                        elif dir_name == 'restore':
                            try:
                                _main_webview.restore()
                            except Exception:
                                pass
                            win32gui.ShowWindow(h, win32con.SW_RESTORE)
                            return {'ok': True, 'maximized': False, 'snapped': False}
                        elif dir_name in ('left', 'right'):
                            try:
                                if ctypes.windll.user32.IsZoomed(h):
                                    win32gui.ShowWindow(h, win32con.SW_RESTORE)
                            except Exception:
                                pass
                            mon = win32api.MonitorFromWindow(h, win32con.MONITOR_DEFAULTTONEAREST)
                            info = win32api.GetMonitorInfo(mon)
                            work = info['Work']
                            w_total = work[2] - work[0]
                            h_total = work[3] - work[1]
                            half_w = w_total // 2
                            x = work[0] if dir_name == 'left' else (work[0] + half_w)
                            y = work[1]
                            w = half_w if dir_name == 'left' else (w_total - half_w)
                            win32gui.SetWindowPos(h, 0, x, y, w, h_total, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED)
                            try:
                                _main_webview.move(x, y)
                                _main_webview.resize(w, h_total)
                            except Exception:
                                pass
                            return {'ok': True, 'maximized': False, 'snapped': dir_name, 'x': x, 'y': y, 'w': w, 'h': h_total}
                    except Exception as e:
                        return {'ok': False, 'error': str(e)}
            elif command == 'close':
                set_app_shutting_down(True)
                _main_webview.destroy()
                return {'ok': True}
            elif command == 'set-icon':
                return {'ok': True}
            elif command == 'set-bounds':
                try:
                    w = int(data.get('w', 0))
                    h = int(data.get('h', 0))
                    x = int(data.get('x', 0))
                    y = int(data.get('y', 0))
                    if w >= 480 and h >= 360:
                        _main_webview.move(x, y)
                        _main_webview.resize(w, h)
                        return {'ok': True}
                except Exception:
                    pass
                return {'ok': True}
        except Exception:
            pass
    if os.name != 'nt':
        return {'ok': False}
    import psutil, win32gui, win32process, win32con
    windows = []
    def collect(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or 'Broadcast Playroom' not in win32gui.GetWindowText(hwnd):
            return
        try:
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            proc = psutil.Process(pid)
            if proc.name().lower() in ('chrome.exe', 'msedge.exe', 'broadcastplayroom3-full.exe', 'broadcastplayroom3-lite.exe', 'python.exe'):
                windows.append(hwnd)
        except psutil.Error:
            pass
    win32gui.EnumWindows(collect, None)
    if not windows:
        return {'ok': False}
    hwnd = windows[0]
    setup_app_window_icon(hwnd)
    if command in ('set-icon',):
        return {'ok': True}
    if command == 'restore-frame':
        win32gui.SetWindowRgn(hwnd, 0, True)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style | win32con.WS_CAPTION)
        win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
        if hwnd not in _watching:
            _watching.add(hwnd)
            _remember_window(hwnd)
        return {'ok': True}
    if command == 'init':
        win32gui.SetWindowRgn(hwnd, 0, True)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MAXIMIZEBOX | win32con.WS_MINIMIZEBOX | win32con.WS_SYSMENU
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
        return {'ok': True}
    elif command == 'drag':
        _do_native_drag(hwnd)
        return {'ok': True}
    elif command == 'resize':
        dir_name = data.get('direction', 'right') if isinstance(data, dict) else str(data)
        _do_native_resize(dir_name, hwnd)
        return {'ok': True}
    elif command == 'set-bounds':
        try:
            w = int(data.get('w', 0))
            h = int(data.get('h', 0))
            x = int(data.get('x', 0))
            y = int(data.get('y', 0))
            if w >= 480 and h >= 360:
                win32gui.SetWindowPos(hwnd, 0, x, y, w, h, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
                return {'ok': True}
        except Exception:
            pass
        return {'ok': False}
    elif command == 'minimize':
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    elif command == 'maximize':
        is_max = bool(ctypes.windll.user32.IsZoomed(hwnd)) if hasattr(ctypes.windll.user32, 'IsZoomed') else (win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMAXIMIZED)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE if is_max else win32con.SW_MAXIMIZE)
        return {'ok': True, 'maximized': not is_max}
    elif command == 'snap':
        dir_name = data.get('direction', 'left') if isinstance(data, dict) else str(data)
        try:
            import win32api, win32gui, win32con
            if dir_name == 'maximize':
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return {'ok': True, 'maximized': True, 'snapped': False}
            elif dir_name == 'restore':
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                return {'ok': True, 'maximized': False, 'snapped': False}
            elif dir_name in ('left', 'right'):
                try:
                    if ctypes.windll.user32.IsZoomed(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                except Exception:
                    pass
                mon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
                info = win32api.GetMonitorInfo(mon)
                work = info['Work']
                w_total = work[2] - work[0]
                h_total = work[3] - work[1]
                half_w = w_total // 2
                x = work[0] if dir_name == 'left' else (work[0] + half_w)
                y = work[1]
                w = half_w if dir_name == 'left' else (w_total - half_w)
                win32gui.SetWindowPos(hwnd, 0, x, y, w, h_total, win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED)
                return {'ok': True, 'maximized': False, 'snapped': dir_name, 'x': x, 'y': y, 'w': w, 'h': h_total}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    elif command == 'close':
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return {'ok': True}
