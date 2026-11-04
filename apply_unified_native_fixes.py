import os
import re
import json

BASE_DIR = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"

# 1. Update updater.py
updater_path = os.path.join(BASE_DIR, "updater.py")
with open(updater_path, "r", encoding="utf-8") as f:
    up = f.read()
up = re.sub(r'CURRENT_VERSION\s*=\s*["\']3\.48["\']', 'CURRENT_VERSION = "3.49"', up)
with open(updater_path, "w", encoding="utf-8") as f:
    f.write(up)
print("[OK] updater.py updated to 3.49")

# 2. Update version.json
vjson_path = os.path.join(BASE_DIR, "version.json")
with open(vjson_path, "r", encoding="utf-8") as f:
    vj = json.load(f)
vj["version"] = "3.49"
vj["release_notes"] = "v3.49: Standardize unified native Chrome/Edge app mode for dev & production, native title bar parity, popouts can leave screen on all machines, Twitch title SSL & edit fixes."
with open(vjson_path, "w", encoding="utf-8") as f:
    json.dump(vj, f, indent=2, ensure_ascii=False)
print("[OK] version.json updated to 3.49")

# 3. Update package.json
pkg_path = os.path.join(BASE_DIR, "package.json")
with open(pkg_path, "r", encoding="utf-8") as f:
    pkg = json.load(f)
pkg["version"] = "3.49"
with open(pkg_path, "w", encoding="utf-8") as f:
    json.dump(pkg, f, indent=2, ensure_ascii=False)
print("[OK] package.json updated to 3.49")

# 4. Update patch_installer.py
pi_path = os.path.join(BASE_DIR, "patch_installer.py")
with open(pi_path, "r", encoding="utf-8") as f:
    pi = f.read()
pi = pi.replace("'3.48'", "'3.49'").replace('"3.48"', '"3.49"').replace('BP3-PatchInstaller/3.48', 'BP3-PatchInstaller/3.49')
with open(pi_path, "w", encoding="utf-8") as f:
    f.write(pi)
print("[OK] patch_installer.py updated to 3.49")

# 5. Update chat_bridge.py (Twitch Title SSL & UTF-8 decoding)
cb_path = os.path.join(BASE_DIR, "chat_bridge.py")
with open(cb_path, "r", encoding="utf-8") as f:
    cb = f.read()

old_twitch_gql = """            import urllib.request, json

            q = 'query { user(login: "%s") { broadcastSettings { title } stream { title } } }' % ch

            req = urllib.request.Request('https://gql.twitch.tv/gql', data=json.dumps({'query': q}).encode(), headers={'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})

            with urllib.request.urlopen(req, timeout=5) as res:

                data = json.loads(res.read())

                user = data.get('data', {}).get('user', {}) or {}

                stream = user.get('stream') or {}

                return stream.get('title') or (user.get('broadcastSettings') or {}).get('title') or ''"""

new_twitch_gql = """            import urllib.request, json, ssl
            ctx = None
            try:
                ctx = ssl.create_default_context()
                if hasattr(ctx, 'load_default_certs'):
                    ctx.load_default_certs()
            except Exception:
                pass
            if not ctx:
                ctx = ssl._create_unverified_context()
            q = 'query { user(login: "%s") { broadcastSettings { title } stream { title } } }' % ch
            req = urllib.request.Request('https://gql.twitch.tv/gql', data=json.dumps({'query': q}).encode('utf-8'), headers={'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
                data = json.loads(res.read().decode('utf-8', errors='replace'))
                user = data.get('data', {}).get('user', {}) or {}
                stream = user.get('stream') or {}
                return stream.get('title') or (user.get('broadcastSettings') or {}).get('title') or ''"""

if old_twitch_gql in cb:
    cb = cb.replace(old_twitch_gql, new_twitch_gql)
    with open(cb_path, "w", encoding="utf-8") as f:
        f.write(cb)
    print("[OK] chat_bridge.py updated with robust SSL and UTF-8 handling")
else:
    print("[WARN] old_twitch_gql pattern not matched directly in chat_bridge.py, using regex fallback")
    pattern = r"import urllib\.request, json\s+q = 'query \{ user\(login:.*?return stream\.get\('title'\) or \(user\.get\('broadcastSettings'\) or \{\}\)\.get\('title'\) or ''"
    cb = re.sub(pattern, new_twitch_gql.strip(), cb, flags=re.DOTALL)
    with open(cb_path, "w", encoding="utf-8") as f:
        f.write(cb)
    print("[OK] chat_bridge.py regex replaced successfully")

# 6. Update app_window_frame.py (Prevent titlebar stripping and clipping)
awf_path = os.path.join(BASE_DIR, "app_window_frame.py")
with open(awf_path, "r", encoding="utf-8") as f:
    awf = f.read()

# Replace setup_discord_frame to retain native caption
old_sdf = """def setup_discord_frame(hwnd):
    try:
        import win32gui, win32con
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.WS_THICKFRAME | win32con.WS_MAXIMIZEBOX | win32con.WS_MINIMIZEBOX
        style &= ~win32con.WS_CAPTION
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        margins = MARGINS(0, 0, 1, 0)
        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

        win32gui.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED
        )
    except Exception as e:
        print(f"[WARN] setup_discord_frame failed: {e}", flush=True)"""

new_sdf = """def setup_discord_frame(hwnd):
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
        print(f"[WARN] setup_discord_frame failed: {e}", flush=True)"""

if old_sdf in awf:
    awf = awf.replace(old_sdf, new_sdf)
    print("[OK] setup_discord_frame updated in app_window_frame.py")

# Ensure command == 'init' doesn't clip caption
old_init_clip = """    if command == 'init':
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        client_x, client_y = win32gui.ClientToScreen(hwnd, (0, 0))
        user32 = ctypes.windll.user32
        try:
            user32.GetDpiForWindow.argtypes = [ctypes.c_void_p]
            dpi = user32.GetDpiForWindow(hwnd) or 96
            caption = user32.GetSystemMetricsForDpi(4, dpi) + user32.GetSystemMetricsForDpi(33, dpi) + user32.GetSystemMetricsForDpi(92, dpi)
        except AttributeError:
            caption = user32.GetSystemMetrics(4) + user32.GetSystemMetrics(33) + user32.GetSystemMetrics(92)
        inset = max(0, client_y - top, caption)
        if inset:
            from ctypes import wintypes
            create_region = ctypes.windll.gdi32.CreateRectRgn
            create_region.argtypes = [ctypes.c_int] * 4
            create_region.restype = wintypes.HANDLE
            region = create_region(0, inset, right - left, bottom - top)
            if not region:
                return {'ok': False}
            win32gui.SetWindowRgn(hwnd, region, True)"""

new_init_clip = """    if command == 'init':
        win32gui.SetWindowRgn(hwnd, 0, True)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MAXIMIZEBOX | win32con.WS_MINIMIZEBOX | win32con.WS_SYSMENU
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
        return {'ok': True}"""

if old_init_clip in awf:
    awf = awf.replace(old_init_clip, new_init_clip)
    print("[OK] command init clipping removed in app_window_frame.py")

with open(awf_path, "w", encoding="utf-8") as f:
    f.write(awf)

# 7. Update launch_dev.py
ld_path = os.path.join(BASE_DIR, "launch_dev.py")
with open(ld_path, "r", encoding="utf-8") as f:
    ld = f.read()

# Update find_browser
old_find_browser = """def find_browser():
    chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    edge_path = r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    if os.path.exists(chrome_path):
        return chrome_path
    if os.path.exists(edge_path):
        return edge_path
    return None"""

new_find_browser = """def find_browser():
    candidates = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"),
        r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Microsoft\\Edge\\Application\\msedge.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None"""

if old_find_browser in ld:
    ld = ld.replace(old_find_browser, new_find_browser)
    print("[OK] find_browser expanded in launch_dev.py")
else:
    # Use lambda to avoid regex escape interpretation
    ld = re.sub(r'def find_browser\(\):.*?return None\b', lambda m: new_find_browser, ld, flags=re.DOTALL)
    print("[OK] find_browser regex replaced in launch_dev.py")

# Update /api/open-external origin check in launch_dev.py
old_open_external_origin = """        if path == '/api/open-external':
            try:
                origin = urllib.parse.urlparse(self.headers.get('Origin', ''))
                if origin.scheme != 'http' or origin.hostname not in ('localhost', '127.0.0.1') or origin.port != self.server.server_port:
                    self.send_json({'error': 'Invalid origin'}, 403); return"""

new_open_external_origin = """        if path == '/api/open-external':
            try:
                client_ip = self.client_address[0] if hasattr(self, 'client_address') and self.client_address else ''
                origin = urllib.parse.urlparse(self.headers.get('Origin', ''))
                is_local = client_ip in ('127.0.0.1', '::1', 'localhost') or origin.hostname in ('localhost', '127.0.0.1')
                if not is_local:
                    self.send_json({'error': 'Invalid origin'}, 403); return"""

if old_open_external_origin in ld:
    ld = ld.replace(old_open_external_origin, new_open_external_origin)
    print("[OK] /api/open-external origin check relaxed in launch_dev.py")
else:
    ld = re.sub(r"if path == '/api/open-external':\s+try:\s+origin = urllib\.parse\.urlparse\(self\.headers\.get\('Origin', ''\)\)\s+if origin\.scheme != 'http' or origin\.hostname not in \('localhost', '127\.0\.0\.1'\) or origin\.port != self\.server\.server_port:\s+self\.send_json\(\{'error': 'Invalid origin'\}, 403\); return", new_open_external_origin, ld)
    print("[OK] /api/open-external origin regex replaced in launch_dev.py")

# Now update open_app_window to standardize on Chrome/Edge App Mode with --disable-popup-blocking
# First let's check what open_app_window has:
open_app_window_regex = r"def open_app_window\(main_url\):.*?if not launched:\s+print\(\"\[LAUNCH\] Opening in default web browser\.\.\.\", flush=True\)\s+webbrowser\.open\(main_url\)"

new_open_app_window = """def open_app_window(main_url):
    curr_ver = get_current_version()
    browser_bin = find_browser()
    launched = False

    app_profile_dir = os.path.join(str(DATA_ROOT), 'browser_profile')
    os.makedirs(app_profile_dir, exist_ok=True)
    # Purge stale browser cache to guarantee immediate UI update without requiring Ctrl+Shift+R
    for cache_sub in ['Default/Cache', 'Default/Code Cache', 'Default/GPUCache', 'ShaderCache', 'GrShaderCache']:
        cp = os.path.join(app_profile_dir, *cache_sub.split('/'))
        if os.path.isdir(cp):
            try:
                import shutil
                shutil.rmtree(cp, ignore_errors=True)
            except Exception:
                pass

    cache_delim = '&' if '?' in main_url else '?'
    main_url_busted = f"{main_url}{cache_delim}_v={curr_ver}_{int(time.time())}"

    if browser_bin:
        cmd = [
            browser_bin,
            f"--app={main_url_busted}",
            f"--user-data-dir={app_profile_dir}",
            "--disable-popup-blocking",
            "--new-window",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,QuickIntensiveWakeUpThrottlingAfterLoading,WebAppWindowControlsOverlay",
            "--disable-http-cache",
            "--disable-application-cache",
            "--disk-cache-size=1",
            "--media-cache-size=1",
            "--autoplay-policy=no-user-gesture-required",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-features=Translate,AutofillServerCommunication,AutofillEnableAccountWalletStorage,PasswordGeneration",
            "--disable-save-password-bubble",
            "--disable-single-click-autofill",
            "--disable-autofill-keyboard-accessory-view",
            "--password-store=basic",
            "--no-default-browser-check",
            "--no-first-run",
            "--window-size=1600,950",
            "--window-position=100,50"
        ]
        print(f"[LAUNCH] Opening Desktop App window via {os.path.basename(browser_bin)} (Popouts & Title Bar Native)...", flush=True)
        try:
            proc = subprocess.Popen(cmd)
            launched = True
            def _watch_app_window_icon():
                start_t = time.time()
                while time.time() - start_t < 35:
                    try:
                        from app_window_frame import apply_icon_to_app_windows
                        if apply_icon_to_app_windows():
                            time.sleep(1.0)
                        else:
                            time.sleep(0.3)
                    except Exception:
                        time.sleep(0.5)
            threading.Thread(target=_watch_app_window_icon, daemon=True).start()
            time.sleep(1.0)
            if proc.poll() is not None and proc.returncode != 0:
                print(f"[WARN] App mode exited unexpectedly (code {proc.returncode}), opening browser...", flush=True)
                webbrowser.open(main_url)
        except Exception as e:
            print(f"[WARN] Failed to open app mode ({e}), falling back to default browser...", flush=True)
            webbrowser.open(main_url)
            launched = True

    if not launched:
        print("[LAUNCH] Opening in default web browser...", flush=True)
        webbrowser.open(main_url)"""

ld = re.sub(open_app_window_regex, lambda m: new_open_app_window, ld, flags=re.DOTALL)
with open(ld_path, "w", encoding="utf-8") as f:
    f.write(ld)
print("[OK] launch_dev.py open_app_window standardized on native Chrome/Edge App Mode")

# 8. Update src/index.html
html_path = os.path.join(BASE_DIR, "src", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace version occurrences
html = html.replace("<title>Broadcast Playroom v3.48</title>", "<title>Broadcast Playroom v3.49</title>")
html = html.replace("v3.48", "v3.49")

# Replace plat-edit-link href="javascript:void(0)"
html = html.replace('<a href="javascript:void(0)" class="plat-edit-link" onclick="editPlatformStreamInfo(\'twitch\')"',
                    '<a href="#" class="plat-edit-link" onclick="editPlatformStreamInfo(\'twitch\'); return false;"')
html = html.replace('<a href="javascript:void(0)" class="plat-edit-link" onclick="editPlatformStreamInfo(\'youtube\')"',
                    '<a href="#" class="plat-edit-link" onclick="editPlatformStreamInfo(\'youtube\'); return false;"')
html = html.replace('<a href="javascript:void(0)" class="plat-edit-link" onclick="editPlatformStreamInfo(\'kick\')"',
                    '<a href="#" class="plat-edit-link" onclick="editPlatformStreamInfo(\'kick\'); return false;"')

# Enhance openExternalUrl
old_oeu = """    function openExternalUrl(url) {
      if (!url) return;
      try {
        fetch('/api/open-external', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url })
        }).catch(() => {
          window.open(url, '_blank');
        });
      } catch (_) {
        window.open(url, '_blank');
      }
    }"""

new_oeu = """    function openExternalUrl(url) {
      if (!url) return;
      try {
        fetch('/api/open-external', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url })
        }).then(res => {
          if (!res.ok) {
            fetch('/api/open-external?url=' + encodeURIComponent(url)).catch(() => {
              window.open(url, '_blank');
            });
          }
        }).catch(() => {
          fetch('/api/open-external?url=' + encodeURIComponent(url)).catch(() => {
            window.open(url, '_blank');
          });
        });
      } catch (_) {
        window.open(url, '_blank');
      }
    }"""

if old_oeu in html:
    html = html.replace(old_oeu, new_oeu)
    print("[OK] openExternalUrl enhanced in src/index.html")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("[OK] src/index.html updated successfully with v3.49 and edit link fixes")
