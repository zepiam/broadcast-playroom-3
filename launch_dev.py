import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import subprocess
import threading
import time
import tempfile
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket
import webbrowser
import json
import urllib.parse
from chat_bridge import chat_bridge
from dictionary_manager import dict_manager
from tts_service import tts_service

PORT = 8080
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dist'))
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
LAYOUT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'composer_layout.json'))

_LAYOUT_CACHE = None
_LAYOUT_MTIME = 0

def get_layout():
    global _LAYOUT_CACHE, _LAYOUT_MTIME
    if os.path.exists(LAYOUT_FILE):
        try:
            mtime = os.path.getmtime(LAYOUT_FILE)
            if _LAYOUT_CACHE is None or mtime > _LAYOUT_MTIME:
                with open(LAYOUT_FILE, 'r', encoding='utf-8') as f:
                    _LAYOUT_CACHE = json.load(f)
                    _LAYOUT_MTIME = mtime
                return _LAYOUT_CACHE
        except Exception:
            pass
    if _LAYOUT_CACHE is not None:
        return _LAYOUT_CACHE
    _LAYOUT_CACHE = {
        "pages": [
            {
                "id": "page-1",
                "name": "หน้า 1 (มาตรฐาน)",
                "widgets": [
                    {
                        "id": "w-chat-1",
                        "type": "chat",
                        "title": "แชทสด",
                        "x": 40,
                        "y": 500,
                        "width": 440,
                        "height": 520,
                        "z": 10,
                        "chatTheme": "glass-dark",
                        "chatMode": "default"
                    },
                    {
                        "id": "w-clock-1",
                        "type": "clock",
                        "title": "นาฬิกาดิจิทัล",
                        "x": 1640,
                        "y": 40,
                        "width": 240,
                        "height": 70,
                        "z": 11,
                        "clockTheme": "neon-glow",
                        "clockFormat": "HH:MM:SS"
                    }
                ]
            }
        ],
        "activePageId": "page-1",
        "updatedAt": time.time()
    }
    return _LAYOUT_CACHE

def save_layout(data):
    global _LAYOUT_CACHE
    _LAYOUT_CACHE = data
    try:
        with open(LAYOUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[COMPOSER] Saved overlay layout with {len(data.get('pages', []))} page(s)", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to save layout: {e}", flush=True)

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Cache-Control')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. API: Composer Layout Sync for OBS
        if path == '/api/composer/layout':
            layout_data = get_layout()
            payload = json.dumps(layout_data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(payload)
            return

        # 2. API: Server status & OBS URLs
        if path == '/api/server_status':
            status_data = {
                'status': 'online',
                'port': PORT,
                'version': '3.0.0',
                'obs_composer_url': f"http://127.0.0.1:{PORT}/composer.html",
                'obs_overlay_url': f"http://127.0.0.1:{PORT}/overlay.html",
                'obs_dock_url': f"http://127.0.0.1:{PORT}/dock.html"
            }
            payload = json.dumps(status_data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(payload)
            return

        # 3. Other APIs
        if path.startswith('/api/'):
            self.handle_api(parsed)
            return

        # 4. Fallback File Routing (Overlay / Composer / Dock from dist or src)
        clean_path = path.lstrip('/')
        if clean_path in ['composer.html', 'overlay.html']:
            # Prefer dist/composer.html, fallback to src/composer.html
            target = os.path.join(DIST_DIR, 'composer.html')
            if not os.path.exists(target):
                target = os.path.join(SRC_DIR, 'composer.html')
            if os.path.exists(target):
                self.serve_custom_file(target, 'text/html; charset=utf-8')
                return

        if clean_path == 'dock.html':
            target = os.path.join(DIST_DIR, 'dock.html')
            if not os.path.exists(target):
                target = os.path.join(SRC_DIR, 'dock.html')
            if os.path.exists(target):
                self.serve_custom_file(target, 'text/html; charset=utf-8')
                return

        # If file is not in dist, check if it's in src
        dist_candidate = os.path.join(DIST_DIR, clean_path)
        if not os.path.exists(dist_candidate) and clean_path:
            src_candidate = os.path.join(SRC_DIR, clean_path)
            if os.path.exists(src_candidate) and os.path.isfile(src_candidate):
                mime = 'text/plain'
                if clean_path.endswith('.js'): mime = 'application/javascript; charset=utf-8'
                elif clean_path.endswith('.css'): mime = 'text/css; charset=utf-8'
                elif clean_path.endswith('.png'): mime = 'image/png'
                elif clean_path.endswith('.jpg') or clean_path.endswith('.jpeg'): mime = 'image/jpeg'
                elif clean_path.endswith('.svg'): mime = 'image/svg+xml'
                self.serve_custom_file(src_candidate, mime)
                return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/composer/layout':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                save_layout(data)
                resp = {'status': 'ok', 'saved': True, 'timestamp': time.time()}
            except Exception as e:
                resp = {'status': 'error', 'message': str(e)}

            payload = json.dumps(resp, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.send_cors_headers()
        self.end_headers()

    def serve_custom_file(self, filepath, mime_type):
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()

    def handle_api(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        path = parsed.path
        
        # 1. Handle TTS Audio streaming
        if path == '/api/tts':
            text = qs.get('text', [''])[0]
            gender = qs.get('gender', ['female'])[0]
            rate = qs.get('rate', ['+0%'])[0]
            pitch = qs.get('pitch', ['+0Hz'])[0]
            volume = qs.get('volume', ['+0%'])[0]
            
            try:
                processed_text = dict_manager.apply_replace(text)
                audio_bytes = tts_service.generate_audio_bytes(processed_text, gender, rate, pitch, volume)
                if audio_bytes:
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/mpeg')
                    self.send_header('Content-Length', str(len(audio_bytes)))
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(audio_bytes)
                    return
                else:
                    self.send_response(500)
                    self.send_cors_headers()
                    self.end_headers()
                    return
            except Exception as e:
                self.send_response(500)
                self.send_cors_headers()
                self.end_headers()
                return

        response_data = {}
        if path == '/api/connect':
            platform = qs.get('platform', [''])[0]
            target = qs.get('target', [''])[0]
            response_data = chat_bridge.connect(platform, target)
        elif path == '/api/disconnect':
            platform = qs.get('platform', [''])[0]
            response_data = chat_bridge.disconnect(platform)
        elif path == '/api/status':
            response_data = chat_bridge.get_status()
        elif path == '/api/messages':
            last_id = int(qs.get('last_id', [0])[0])
            response_data = {'messages': chat_bridge.get_messages(last_id)}
        elif path == '/api/dictionary':
            response_data = dict_manager.get_all()
        elif path == '/api/dictionary/sync':
            response_data = dict_manager.sync_remote()
        elif path == '/api/dictionary/add':
            find_w = qs.get('find', [''])[0]
            rep_w = qs.get('replace', [''])[0]
            response_data = dict_manager.add_word(find_w, rep_w)
        elif path == '/api/dictionary/delete':
            word = qs.get('word', [''])[0]
            response_data = dict_manager.delete_word(word)
        else:
            response_data = {'error': 'Unknown endpoint'}

        payload = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    global PORT
    HTTPServer.allow_reuse_address = True
    while is_port_in_use(PORT):
        print(f"[INFO] Port {PORT} in use, trying {PORT + 1}...")
        PORT += 1
    
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    return server

def find_browser():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(chrome_path):
        return chrome_path
    if os.path.exists(edge_path):
        return edge_path
    return None

def main():
    server = start_server()
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    main_url = f"http://127.0.0.1:{PORT}/index.html"
    dock_url = f"http://127.0.0.1:{PORT}/dock.html"
    comp_url = f"http://127.0.0.1:{PORT}/composer.html"
    over_url = f"http://127.0.0.1:{PORT}/overlay.html"

    print("============================================================", flush=True)
    print("   Broadcast Playroom 3 (Live Dev & OBS Server)", flush=True)
    print("============================================================", flush=True)
    print(f"   [1] หน้าต่างหลักโปรแกรม:      {main_url}", flush=True)
    print(f"   [2] OBS Custom Dock:         {dock_url}", flush=True)
    print(f"   [3] OBS Live Overlay:        {comp_url}", flush=True)
    print(f"   [4] OBS Overlay (Alias):     {over_url}", flush=True)
    print("============================================================", flush=True)
    print("   * Server is running. Press Ctrl+C in this window to stop.", flush=True)
    print("============================================================\n", flush=True)

    browser_bin = find_browser()
    launched = False

    # Create dedicated, isolated application profile directory so that:
    # 1. It NEVER touches or shares the user's personal Chrome profile, history, or cookies.
    # 2. Chrome plugins/extensions (Bitwarden, LastPass, etc.) are 100% excluded and disabled.
    # 3. Autofill, password popups, and translate banners are strictly suppressed.
    app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    app_profile_dir = os.path.join(app_data, 'BroadcastPlayroom3', 'browser_profile')
    os.makedirs(app_profile_dir, exist_ok=True)

    if browser_bin:
        cmd = [
            browser_bin,
            f"--app={main_url}",
            f"--user-data-dir={app_profile_dir}",
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
        print(f"[LAUNCH] Opening Desktop App window...", flush=True)
        try:
            proc = subprocess.Popen(cmd)
            launched = True
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
        webbrowser.open(main_url)

    # Keep server alive until user exits
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Dev Server...")
    finally:
        server.shutdown()
        sys.exit(0)

if __name__ == '__main__':
    main()
