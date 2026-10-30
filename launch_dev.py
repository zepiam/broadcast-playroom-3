import webbrowser
_orig_webbrowser_open = webbrowser.open

def _safe_webbrowser_open(url, *args, **kwargs):
    if not url or str(url).startswith('about:'):
        return False
    return _orig_webbrowser_open(url, *args, **kwargs)

webbrowser.open = _safe_webbrowser_open
import os







import sys















if "--splash-subprocess" in sys.argv:







    from splash import run_splash_subprocess







    sys.exit(run_splash_subprocess())























# Ensure UTF-8 output on Windows consoles







if hasattr(sys.stdout, 'reconfigure'):







    sys.stdout.reconfigure(encoding='utf-8', errors='replace')







if hasattr(sys.stderr, 'reconfigure'):







    sys.stderr.reconfigure(encoding='utf-8', errors='replace')















import subprocess







import logging







import collections







import threading







import time















class _LogCapture:







    def __init__(self, max_entries=2000):







        self.buffer = collections.deque(maxlen=max_entries)







        self.lock = threading.Lock()







        self.stdout_orig = sys.stdout







        self.stderr_orig = sys.stderr















    def write(self, s):







        if s:







            with self.lock:







                self.buffer.append((time.time(), s))







        if self.stdout_orig:







            try:







                self.stdout_orig.write(s)







                self.stdout_orig.flush()







            except Exception:







                pass















    def flush(self):







        if self.stdout_orig:







            try:







                self.stdout_orig.flush()







            except Exception:







                pass















    def get_logs(self, since=0.0):







        with self.lock:







            return [{'time': t, 'text': msg} for t, msg in self.buffer if t > since]















    def clear(self):







        with self.lock:







            self.buffer.clear()















log_capture = _LogCapture()







sys.stdout = log_capture







sys.stderr = log_capture







import tempfile







from pathlib import Path







from http.server import SimpleHTTPRequestHandler, HTTPServer, ThreadingHTTPServer







import socket







import webbrowser







import json







import urllib.parse







import urllib.request







import hashlib







from overlay_events import overlay_events







from app_presence import app_presence







from layout_migration import normalize_layout







from legacy_media import find_media, serve_media







from rvc_service import rvc_service







from now_playing_service import now_playing_service







from donation_goal_service import donation_goal_service







from avatar_mic_service import avatar_mic_service







from playroom_media import playroom_media







from emote_service import EmoteService







emote_service=EmoteService()







from legacy_chat_config import build_chat_config, build_global_chat_config, build_game_chat_config







from legacy_compat import start_servers as start_legacy_servers







from chat_bridge import chat_bridge







from dictionary_manager import dict_manager







from tts_service import tts_service







from updater import check_for_update, get_current_version, get_build_type, perform_update_and_restart, get_update_runtime_status, start_background_download, apply_pending_update_on_startup, restart_and_apply_update







from defender_helper import DefenderExclusionManager















PORT = 8801







_GLOBAL_SPLASH_CTRL = None















def close_splash():







    global _GLOBAL_SPLASH_CTRL







    if _GLOBAL_SPLASH_CTRL:







        try:







            _GLOBAL_SPLASH_CTRL.finish()







        except Exception:







            pass







        _GLOBAL_SPLASH_CTRL = None







LEGACY_STATUS = []







LEGACY_FILTER_IMPORT_ENABLED = False







GAME_CHAT_LOCK = threading.RLock()







DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dist'))







SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))







_APP_ROOT = os.path.abspath(os.path.dirname(__file__))

ROOT_DIR = _APP_ROOT







_PARENT_DIR = os.path.dirname(_APP_ROOT)







_SHARED_DATA = os.path.join(_PARENT_DIR, 'data')







_LOCAL_DATA = os.path.join(_APP_ROOT, 'data')







_LOCAL_USERDATA = os.path.join(_APP_ROOT, 'userdata')







_PORTABLE_MARKER = os.path.join(_APP_ROOT, '.portable')







_PARENT_PORTABLE = os.path.join(_PARENT_DIR, '.portable')















# Resolution priority:







# 1. ../data/ (Shared data directory in root folder for full/ and lite/)







# 2. ./.portable or ./data/ or ./userdata/ (Direct portable mode)







# 3. %LOCALAPPDATA%\BroadcastPlayroom3 (Standard system user profile fallback)







if os.path.exists(_SHARED_DATA) or os.path.exists(_PARENT_PORTABLE):







    DATA_ROOT = Path(_SHARED_DATA)







    DATA_ROOT.mkdir(parents=True, exist_ok=True)







elif os.path.exists(_LOCAL_DATA):







    DATA_ROOT = Path(_LOCAL_DATA)







    DATA_ROOT.mkdir(parents=True, exist_ok=True)







elif os.path.exists(_LOCAL_USERDATA) or os.path.exists(_PORTABLE_MARKER) or os.environ.get('BP3_PORTABLE') == '1':







    DATA_ROOT = Path(_LOCAL_USERDATA)







    DATA_ROOT.mkdir(parents=True, exist_ok=True)







else:







    DATA_ROOT = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local') / 'BroadcastPlayroom3'















_cand_layout = DATA_ROOT / 'composer_layout.json'







if not _cand_layout.exists() and os.path.exists(os.path.join(_APP_ROOT, 'composer_layout.json')):







    LAYOUT_FILE = os.path.abspath(os.path.join(_APP_ROOT, 'composer_layout.json'))







else:







    LAYOUT_FILE = os.path.abspath(os.path.join(os.environ.get('BP3_DATA_DIR', str(DATA_ROOT)), 'composer_layout.json'))















from bot_auth import BotAccounts







bot_account_dir = DATA_ROOT







from dns_settings import DnsSettings







dns_settings=DnsSettings(bot_account_dir / 'dns_settings.json')







tts_service.dns_settings=dns_settings







bot_accounts = BotAccounts(bot_account_dir / 'bot_accounts.dat', apply_account=chat_bridge.apply_bot_account)







chat_bridge.accounts = bot_accounts















_LAYOUT_CACHE = None







_LAYOUT_MTIME = 0















def get_layout():







    global _LAYOUT_CACHE, _LAYOUT_MTIME







    if os.path.exists(LAYOUT_FILE):







        try:







            mtime = os.path.getmtime(LAYOUT_FILE)







            if _LAYOUT_CACHE is None or mtime > _LAYOUT_MTIME:







                with open(LAYOUT_FILE, 'r', encoding='utf-8') as f:







                    _LAYOUT_CACHE = normalize_layout(json.load(f))







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







    global _LAYOUT_CACHE, _LAYOUT_MTIME







    normalized = normalize_layout(data)







    # Replace atomically so OBS polling never reads half a JSON document.







    temporary = None







    try:







        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=os.path.dirname(LAYOUT_FILE), suffix='.json.tmp', delete=False) as stream:







            temporary = stream.name







            json.dump(normalized, stream, ensure_ascii=False, indent=2)







        os.replace(temporary, LAYOUT_FILE)







        _LAYOUT_CACHE = normalized







        _LAYOUT_MTIME = os.path.getmtime(LAYOUT_FILE)







    finally:







        if temporary and os.path.exists(temporary):







            os.remove(temporary)























from desktop_overlay_service import DesktopOverlays







desktop_overlays=DesktopOverlays(get_layout,save_layout,overlay_events.publish)















APP_PROJECT_ID=hashlib.sha256(os.path.normcase(os.path.realpath(os.path.dirname(__file__))).encode('utf-8')).hexdigest()







DOCK_STATE={}







from clip_markers import ClipMarkers







clip_markers = ClipMarkers(bot_account_dir / 'data')







from obs_connection import ObsConnection







obs_connection = ObsConnection(bot_account_dir / 'obs_connection.dat', clip_markers, source_ports=lambda: {PORT, *(item['port'] for item in LEGACY_STATUS if item.get('status')=='online')})







from clip_hotkey import ClipHotkey







clip_hotkey = ClipHotkey(bot_account_dir / 'clip_hotkey.json', clip_markers)







from legacy_secret_sounds import LegacySecretSounds







legacy_secret_sounds = LegacySecretSounds()















# In-memory LRU cache for TTS & RVC audio streams







_TTS_CACHE_LOCK = threading.Lock()







_TTS_AUDIO_CACHE = collections.OrderedDict()







_TTS_CACHE_MAX = 128















class QuietHandler(SimpleHTTPRequestHandler):







    legacy_view = 'composer'







    def __init__(self, *args, **kwargs):







        super().__init__(*args, directory=DIST_DIR, **kwargs)















    def handle(self):







        try:







            super().handle()







        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):







            # Browser navigation cancels in-flight polling/media requests normally.







            return















    def log_message(self, format, *args):







        pass















    def send_cors_headers(self):







        self.send_header('Access-Control-Allow-Origin', '*')







        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')







        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Cache-Control, X-Filename')















    def do_OPTIONS(self):







        self.send_response(200)







        self.send_cors_headers()







        self.end_headers()















    def do_GET(self):







        parsed = urllib.parse.urlparse(self.path)







        path = parsed.path















        if path == '/api/splash/close':







            close_splash()







            self.send_json({'ok': True})







            return







        if path in ('/favicon.ico', '/favicon.png', '/api/app-icon'):







            ed = getattr(rvc_service, 'edition', 'full')







            if path == '/favicon.png':







                cand = [







                    os.path.join(DIST_DIR, 'assets', 'icon.png'),







                    os.path.join(DIST_DIR, 'assets', f'bp-{ed}-icon.png'),







                    os.path.join(SRC_DIR, 'assets', 'icon.png'),







                    os.path.join(ROOT_DIR, 'assets', 'icons', f'bp-{ed}-icon.png'),







                ]







                content_type = 'image/png'







            else:







                icon_file = 'bp-full-icon.ico' if ed == 'full' else 'bp-lite-icon.ico'







                cand = [







                    os.path.join(DIST_DIR, 'assets', 'icon.ico'),







                    os.path.join(DIST_DIR, 'assets', f'icon_{ed}.ico'),







                    os.path.join(ROOT_DIR, 'assets', 'icons', icon_file),







                    os.path.join(SRC_DIR, 'assets', f'icon_{ed}.ico'),







                    os.path.join(SRC_DIR, 'assets', 'icon.ico'),







                ]







                content_type = 'image/x-icon'







            for c_path in cand:







                if os.path.isfile(c_path):







                    try:







                        with open(c_path, 'rb') as f_ico:







                            ico_data = f_ico.read()







                        self.send_response(200)







                        self.send_header('Content-Type', content_type)







                        self.send_header('Content-Length', str(len(ico_data)))







                        self.send_header('Cache-Control', 'public, max-age=86400')







                        self.end_headers()







                        self.wfile.write(ico_data)







                        return







                    except Exception:







                        pass















        if path in ('/manifest.json', '/manifest.webmanifest'):







            manifest_candidates = [







                os.path.join(DIST_DIR, 'manifest.json'),







                os.path.join(ROOT_DIR, 'public', 'manifest.json'),







                os.path.join(SRC_DIR, 'manifest.json'),







            ]







            for m_path in manifest_candidates:







                if os.path.isfile(m_path):







                    try:







                        with open(m_path, 'rb') as f_man:







                            man_data = f_man.read()







                        self.send_response(200)







                        self.send_header('Content-Type', 'application/manifest+json; charset=utf-8')







                        self.send_header('Content-Length', str(len(man_data)))







                        self.send_header('Cache-Control', 'public, max-age=86400')







                        self.end_headers()







                        self.wfile.write(man_data)







                        return







                    except Exception:







                        pass























        if path == '/api/chatbot/auth/status':







            origin = self.headers.get('Origin')







            if origin:







                parsed_origin = urllib.parse.urlparse(origin)







                if parsed_origin.scheme != 'http' or parsed_origin.hostname not in ('localhost', '127.0.0.1') or parsed_origin.port != self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403); return







            data = bot_accounts.public()







            with chat_bridge._lock:







                for platform, info in data.items():







                    client = chat_bridge._clients.get(platform)







                    info['ready'] = bool(client and getattr(client,'is_connected',False) and getattr(client,'can_send',False))







            self.send_json(data); return















        if path == '/api/legacy/secret-sounds':







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            self.send_json(legacy_secret_sounds.read() if LEGACY_FILTER_IMPORT_ENABLED else {'found':False,'entries':[]});return







        if path.startswith('/legacy-secret-sound/'):







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            ident=path.removeprefix('/legacy-secret-sound/')







            target=legacy_secret_sounds.find(ident)







            if target:serve_media(self,target)







            else:self.send_error(404)







            return















        if path == '/api/dns/settings':







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            self.send_json({**dns_settings.public(),'has_saved':dns_settings.path.exists()});return















        if path == '/api/legacy/user-filters':







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            if not LEGACY_FILTER_IMPORT_ENABLED:self.send_json({});return







            from legacy_user_filters import load







            self.send_json(load());return















        if path == '/api/stream-title':







            qs = urllib.parse.parse_qs(parsed.query)







            plat = qs.get('platform', [''])[0].lower()







            chan = qs.get('channel', [''])[0].strip()







            if not chan:







                with chat_bridge._lock:







                    chan = chat_bridge._statuses.get(plat, {}).get('target', '')







            title = chat_bridge.fetch_stream_title(plat, chan)







            with chat_bridge._lock:







                if plat in chat_bridge._statuses and title:







                    chat_bridge._statuses[plat]['title'] = title







            self.send_json({'ok': True, 'platform': plat, 'channel': chan, 'title': title})







            return















        if path == '/api/translate/mode':







            self.send_json({'ok': True, 'mode': chat_bridge.get_translate_mode()})







            return















        if path == '/api/clip-hotkey/status':







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            self.send_json({'active':False,'suspended':True});return















        if path == '/api/obs/status':







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            self.send_json(obs_connection.public()); return















        if path == '/api/supporters':







            from supporters_service import fetch







            self.send_json(fetch());return















        if path=='/api/app-instance':







            self.send_json({'application':'BroadcastPlayroom3','project':APP_PROJECT_ID,'edition':rvc_service.edition,'closing':app_presence.status()['closing']});return







        if path=='/api/app-presence':







            self.send_json(app_presence.status());return







        if path=='/api/app-presence/stream':







            close_splash()



            try:



                from app_window_frame import apply_icon_to_app_windows



                apply_icon_to_app_windows()



            except Exception:



                pass







            client=urllib.parse.parse_qs(parsed.query).get('client',[''])[0]







            if not client or len(client)>128:self.send_json({'error':'Invalid client'},400);return







            token=app_presence.open(client)







            if not token:self.send_json({'error':'Closed client'},410);return







            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Cache-Control','no-store');self.end_headers()







            self.connection.settimeout(3)







            try:







                while app_presence.touch(token):







                    self.wfile.write(b'data: ready\n\n');self.wfile.flush();time.sleep(1)







            except (OSError,TimeoutError):pass







            finally:app_presence.close(token)







            return















        if path=='/api/dock/status':







            layout=get_layout() or {};pages=layout.get('pages',[]);page=next((p for p in pages if p.get('id')==layout.get('activePageId')),pages[0] if pages else {})







            statuses=chat_bridge.get_status();counts={key:int(value.get('viewers') or 0) for key,value in statuses.items() if value.get('connected')}







            with overlay_events.lock:







                recent=[dict(item['payload'],id=item['payload'].get('id',item['id']),author=item['payload'].get('username',''),raw_author=item['payload'].get('username','')) for item in overlay_events.chat]







            state={**DOCK_STATE,'pages':[{'id':p.get('id'),'name':p.get('name',p.get('id'))} for p in pages],'active_page_id':page.get('id'),'active_widgets':[dict(w,enabled=not w.get('hidden',False),name=w.get('title',w['type'])) for w in page.get('widgets',[])],'viewers':{'total':sum(counts.values()),'platforms':counts},'recent_messages':recent,'widgets_installed':{kind:any(w.get('type')==kind for w in page.get('widgets',[])) for kind in ['chat','replie','ask','giveaway']}}







            from obs_scene_info import dock_scene







            obs_status=obs_connection.public();state['scene_overlay']=dock_scene(layout,obs_status['scene']);state['obs_stream']=obs_status['stream']







            self.send_json({'status':state});return







        if path=='/api/giveaway-settings':







            self.send_json(((get_layout() or {}).get('legacyTools') or {}).get('giveaway') or {});return







        if path=='/api/desktop-overlays':







            self.send_json({**desktop_overlays.snapshot(),'settings':{key:value for key,value in ((get_layout() or {}).get('legacyTools') or {}).items() if key=='more_overlays' or key.startswith('game_overlay_') or key.startswith('viewer_overlay_')}});return







        if path=='/api/game-chat-settings':







            from game_chat_settings import snapshot







            layout=get_layout() or {};settings={**(layout.get('legacyChat') or {}),**(layout.get('legacyTools') or {})}







            self.send_json(snapshot(settings));return







        if path=='/legacy-game-chat.html':







            self.serve_custom_file(os.path.join(DIST_DIR,'legacy_game_chat.html'),'text/html; charset=utf-8');return







        if path in ('/game-chat-config','/game-theme','/game-custom-css'):







            settings={**((get_layout() or {}).get('legacyChat') or {}),**((get_layout() or {}).get('legacyTools') or {})}







            config=build_game_chat_config(settings)







            if path=='/game-chat-config':self.send_json(config)







            else:







                data=config['theme_css' if path=='/game-theme' else 'custom_css'].encode('utf-8');self.send_response(200);self.send_header('Content-Type','text/css; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)







            return







        if path == '/legacy-chat.html':







            self.serve_custom_file(os.path.join(DIST_DIR,'legacy_chat.html'),'text/html; charset=utf-8')







            return







        if path in ('/chat-config','/config'):







            layout=get_layout() or {};settings=layout.get('legacyChat') or {};query=urllib.parse.parse_qs(parsed.query);wid=query.get('id',[''])[0]







            if path=='/config' or wid=='__global__':







                self.send_json(build_global_chat_config(settings));return







            else:







                pages=layout.get('pages',[]);page_value=query.get('p',[layout.get('activePageId','')])[0]







                selected=next((page for page in pages if str(page.get('id'))==page_value or str(page.get('name','')).lower()==str(page_value).lower()),None)







                if selected is None and str(page_value).isdigit() and 1<=int(page_value)<=len(pages):selected=pages[int(page_value)-1]







                candidates=selected.get('widgets',[]) if selected else [widget for page in pages for widget in page.get('widgets',[])]







                widget=next((widget for widget in candidates if str(widget.get('id'))==wid),{})







            self.send_json(build_chat_config(widget,settings))







            return







        if path.startswith(('/emote/','/game-emote/')):







            layout=get_layout() or {}







            if path.startswith('/game-emote/'):







                settings={**(layout.get('legacyChat') or {}),**(layout.get('legacyTools') or {})}







                animated=settings.get('game_overlay_animated_emotes',False)







            else:animated=(layout.get('legacyChat') or {}).get('overlay_animated_emotes',True)







            result=emote_service.read(urllib.parse.unquote(path.rsplit('/',1)[-1]),animated)







            if result is None:self.send_error(404)







            else:







                data,mime=result;self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_cors_headers();self.end_headers();self.wfile.write(data)







            return







        if path.startswith('/logo/'):















            platform=path.rsplit('/',1)[-1].lower()







            if platform in ('twitch','youtube','kick','tiktok','soop','mylive'):







                self.serve_custom_file(os.path.join(SRC_DIR,'assets',platform+'.png'),'image/png')







            else:self.send_error(404)







            return







        if path.startswith('/playroom-media/'):







            origin=self.headers.get('Origin')







            if origin:







                parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







            media=playroom_media.find(path)







            if media is None:self.send_error(404)







            else:serve_media(self,media)







            return







        if path == '/api/avatar/sync':







            avatar_mic_service.sync(get_layout())







            self.send_json({'ok':True})







            return







        if path == '/api/donation-goals':







            donation_goal_service.sync(get_layout())







            self.send_json(donation_goal_service.snapshot())







            return







        if path in ('/api/now-playing', '/api/now-playing/thumbnail'):







            source = urllib.parse.parse_qs(parsed.query).get('source', ['auto'])[0]







            if path.endswith('/thumbnail'):







                target = now_playing_service.thumbnail(source)







                if target:







                    serve_media(self, target)







                else:







                    self.send_error(404)







            else:







                state = now_playing_service.snapshot(source)







                state['thumbnail'] = ('/api/now-playing/thumbnail?source=' + urllib.parse.quote(source)) if state['thumbnail'] else ''







                self.send_json(state)







            return







        if path == '/api/viewer-overlay':







            from viewer_overlay_config import snapshot







            self.send_json(snapshot(get_layout(),chat_bridge.get_status()));return







        if path == '/api/capabilities':







            self.send_json(rvc_service.capabilities())







            return







        if path.startswith('/api/rvc/'):







            try:







                if path == '/api/rvc/models':self.send_json({'models':rvc_service.public_models(),'status':rvc_service.status()})







                elif path == '/api/rvc/catalog':self.send_json({'models':rvc_service.public_catalog()})







                elif path == '/api/rvc/status':self.send_json(rvc_service.status())







                else:self.send_json({'error':'Unknown RVC endpoint'},404)







            except PermissionError as error:self.send_json({'error':str(error)},403)







            except Exception as error:self.send_json({'error':str(error)},500)







            return















        if path.startswith(('/widget-image/' , '/widget-video/', '/clip/', '/character/', '/avatar-preset/')):







            media = find_media(path, get_layout())







            if media is None:







                self.send_error(404, 'Migrated media not found')







            else:







                serve_media(self, media)







            return















        if path == '/editor':







            self.send_response(302)







            suffix = ('&' + parsed.query) if parsed.query else ''







            self.send_header('Location', '/index.html?tool=composer' + suffix)







            self.end_headers()







            return







        views = {'/': self.legacy_view, '/composer': 'composer', '/composer.html': 'composer',







                 '/overlay.html': self.legacy_view, '/chat-widget': 'chat',







                 '/giveaway': 'giveaway', '/giveaway_overlay.html': 'giveaway',







                 '/playroom-widget': 'playroom', '/playroom.html': 'playroom',







                 '/viewer_overlay.html': 'viewer'}







        if path in views:







            if views[path]=='viewer':







                self.serve_custom_file(os.path.join(DIST_DIR,'legacy_viewer.html'),'text/html; charset=utf-8');return







            self.serve_overlay(views[path])







            return







        if path in ('/dock', '/dock-offline.html'):







            self.serve_custom_file(os.path.join(DIST_DIR, 'dock.html'), 'text/html; charset=utf-8')







            return







        if path == '/dock-sw.js':







            body = b"self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(self.registration.unregister()));"







            self.send_response(200)







            self.send_header('Content-Type', 'application/javascript')







            self.send_header('Content-Length', str(len(body)))







            self.send_header('Cache-Control', 'no-store')







            self.end_headers()







            self.wfile.write(body)







            return















        if path == '/api/overlay/events':







            qs = urllib.parse.parse_qs(parsed.query)







            try:







                after = int(qs['after'][0]) if 'after' in qs else None







                data = overlay_events.read(after, qs.get('epoch', [None])[0])







                self.send_json(data)







            except (ValueError, TypeError):







                self.send_json({'error': 'Invalid cursor'}, 400)







            return















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







                'version': get_current_version(),







                'obs_composer_url': f"http://localhost:{PORT}/",







                'legacy_listeners': LEGACY_STATUS,







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















        # Never reuse a cached application shell after a Dev restart.







        if clean_path in ('', 'index.html'):







            self.serve_custom_file(os.path.join(DIST_DIR, 'index.html'), 'text/html; charset=utf-8')







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















        if path == '/api/platform/settings':
            try:
                size = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(size).decode('utf-8'))
                settings_path = os.path.join(str(DATA_ROOT), 'platform_settings.json')
                existing = {}
                if os.path.exists(settings_path):
                    try:
                        with open(settings_path, 'r', encoding='utf-8') as sf:
                            existing = json.load(sf)
                    except Exception:
                        existing = {}
                if isinstance(data, dict):
                    existing.update(data)
                with open(settings_path, 'w', encoding='utf-8') as sf:
                    json.dump(existing, sf, ensure_ascii=False, indent=2)
                self.send_json({'success': True})
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)})
            return

        if path == '/api/messages/inject':







            try:







                size = int(self.headers.get('Content-Length', 0))







                data = json.loads(self.rfile.read(size).decode('utf-8'))







                from chat_twitch import ChatMessage







                plat = data.get('platform', 'twitch').lower()







                extra = data.get('extra', {})







                if 'gift_name' in data: extra['gift_name'] = data['gift_name']







                if 'count' in data: extra['count'] = data['count']







                if 'months' in data: extra['months'] = data['months']







                if 'viewers' in data: extra['viewers'] = data['viewers']







                msg = ChatMessage(







                    platform=plat,







                    author=data.get('author') or data.get('username') or 'Viewer',







                    text=data.get('text', ''),







                    event=data.get('event', 'message'),







                    amount=data.get('amount'),







                    extra=extra







                )







                chat_bridge._on_message(plat, msg)







                self.send_json({'success': True, 'id': chat_bridge._msg_id_counter})







            except Exception as e:







                self.send_json({'success': False, 'error': str(e)}, 400)







            return















        if path == '/api/dictionary/import':







            try:







                size = int(self.headers.get('Content-Length', 0))







                raw_body = self.rfile.read(size).decode('utf-8')







                data = json.loads(raw_body)







                res = dict_manager.import_dict(data)







                self.send_json(res)







            except Exception as e:







                self.send_json({'success': False, 'error': str(e)}, 400)







            return























        if path in ('/api/clip-hotkey','/api/clip-markers'):







            self.send_json({'ok':False,'error':'พักการใช้งานมาร์กคลิปชั่วคราว'},410);return















        if path=='/api/game-chat-settings':







            try:







                origin=self.headers.get('Origin')







                if origin:







                    parsed_origin=urllib.parse.urlparse(origin)







                    if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                        self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=32768:raise ValueError('Invalid request size')







                data=json.loads(self.rfile.read(size))







                from game_chat_settings import update, snapshot







                with GAME_CHAT_LOCK:







                    layout=get_layout(); old=dict(layout.get('legacyTools') or {})







                    for inherited_key,inherited_value in (layout.get('legacyChat') or {}).items():







                        if inherited_key.startswith(('game_overlay_','character_')) and inherited_key not in old:







                            old[inherited_key]=inherited_value







                    changed=update(old,data.get('mode'),data.get('key'),data.get('value'))







                    if data.get('key') in ('hotkey','hotkey_edit'):







                        desktop_overlays.rebind_game_hotkey('edit' if data['key']=='hotkey_edit' else 'toggle',data['value'],f'http://127.0.0.1:{self.server.server_port}')







                    layout['legacyTools']=changed;save_layout(layout)







                    merged={**(layout.get('legacyChat') or {}),**changed}







                    result=snapshot(merged)







                overlay_events.publish({'event':'DESKTOP_OVERLAY_STATE','payload':changed})







                self.send_json(result)







            except (ValueError,TypeError,OSError,AttributeError,RuntimeError) as error:self.send_json({'error':str(error)},400)







            return















        if path=='/api/viewer-overlay-settings':







            try:







                origin=self.headers.get('Origin')







                if origin:







                    parsed_origin=urllib.parse.urlparse(origin)







                    if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                        self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=4096:raise ValueError('Invalid request size')







                values=json.loads(self.rfile.read(size))







                if not isinstance(values,dict):raise ValueError('Invalid viewer settings')







                from viewer_overlay_config import configure







                with GAME_CHAT_LOCK:







                    layout=get_layout();settings=layout.setdefault('legacyTools',{});configure(settings,values);save_layout(layout)







                overlay_events.publish({'event':'DESKTOP_OVERLAY_STATE','payload':settings})







                for item in desktop_overlays.instances.values():







                    if item['kind']=='viewer' and item['process'].poll() is None:







                        if 'alpha' in values:desktop_overlays.command(item,'set_alpha',alpha=settings.get('viewer_overlay_alpha',1))







                        if 'width' in values or 'height' in values:desktop_overlays.command(item,'set_size',width=settings.get('viewer_overlay_width',400),height=settings.get('viewer_overlay_height',80))







                self.send_json({'ok':True})







            except (ValueError,TypeError,OSError,AttributeError) as error:self.send_json({'error':str(error)},400)







            return















        if path in ('/api/dns/settings','/api/dns/test','/api/dns/clear'):







            try:







                origin=urllib.parse.urlparse(self.headers.get('Origin',''))







                if origin.scheme!='http' or origin.hostname not in ('localhost','127.0.0.1') or origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=4096:raise ValueError('invalid')







                data=json.loads(self.rfile.read(size))







                if path=='/api/dns/settings':self.send_json(dns_settings.save(data))







                elif path=='/api/dns/clear':







                    from network_dns import clear_dns_cache







                    clear_dns_cache();self.send_json({'ok':True})







                else:







                    from network_dns import test_dns_connection







                    config=dns_settings._validate(data)







                    ok,latency,ip,_=test_dns_connection(config['service'],config['custom'])







                    self.send_json({'ok':bool(ok),'latency_ms':round(latency),'message':'เชื่อมต่อบริการเสียงสำเร็จ' if ok else 'ทดสอบการเชื่อมต่อไม่สำเร็จ'})







            except (ValueError,TypeError,AttributeError):self.send_json({'error':'ข้อมูล DNS ไม่ถูกต้อง'},400)







            except Exception:self.send_json({'error':'ไม่สามารถทำรายการ DNS ได้'},500)







            return















        if path == '/api/logs/clear':







            log_capture.clear()







            self.send_json({'ok': True}); return















        if path == '/api/open-external':







            try:







                origin = urllib.parse.urlparse(self.headers.get('Origin', ''))







                if origin.scheme != 'http' or origin.hostname not in ('localhost', '127.0.0.1') or origin.port != self.server.server_port:







                    self.send_json({'error': 'Invalid origin'}, 403); return







                size = int(self.headers.get('Content-Length', 0))







                if not 0 < size <= 4096: raise ValueError('invalid size')







                data = json.loads(self.rfile.read(size))







                url = str(data.get('url', '')).strip()







                if not (url.startswith('http://') or url.startswith('https://')):







                    self.send_json({'error': 'Invalid URL scheme'}, 400); return







                import webbrowser







                webbrowser.open(url)







                self.send_json({'ok': True})







            except Exception as e:







                self.send_json({'error': str(e)}, 500)







            return















        if path == '/api/apply-update':

            try:

                res = restart_and_apply_update()

                self.send_json(res)

            except Exception as e:

                self.send_json({'success': False, 'message': str(e)}, 500)

            return



        if path == '/api/shutdown':

            self.send_json({'ok': True, 'message': 'โปรแกรมกำลังปิดตัวลง...'})

            def _delayed_exit():

                time.sleep(0.4)

                try:

                    app_presence.begin_shutdown()

                except Exception:

                    pass

                os._exit(0)

            threading.Thread(target=_delayed_exit, daemon=True).start()

            return















        if path == '/api/defender/apply':







            try:







                success = DefenderExclusionManager.apply_one_click_exclusion()







                self.send_json({'success': success, 'info': DefenderExclusionManager.get_status_info()})







            except Exception as e:







                self.send_json({'success': False, 'message': str(e)}, 500)







            return















        if path == '/api/chatbot/blocklist':







            try:







                origin=urllib.parse.urlparse(self.headers.get('Origin',''))







                if origin.scheme!='http' or origin.hostname not in ('localhost','127.0.0.1') or origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=65536:raise ValueError('invalid')







                data=json.loads(self.rfile.read(size));names=data.get('names');words=data.get('banned_words',[])







                if not isinstance(names,list) or len(names)>2000 or any(not isinstance(name,str) or len(name)>200 for name in names):raise ValueError('invalid')







                if not isinstance(words,list) or len(words)>2000 or any(not isinstance(word,str) or len(word)>200 for word in words):raise ValueError('invalid')







                chat_bridge.set_bot_blocklist(names,words);self.send_json({'ok':True})







            except (ValueError,TypeError,AttributeError):self.send_json({'error':'Invalid request'},400)







            return















        if path == '/api/clip-hotkey':







            try:







                origin=urllib.parse.urlparse(self.headers.get('Origin',''))







                if origin.scheme!='http' or origin.hostname not in ('localhost','127.0.0.1') or origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=1024:raise ValueError('ข้อมูลไม่ถูกต้อง')







                data=json.loads(self.rfile.read(size));self.send_json(clip_hotkey.set(data.get('shortcut','')))







            except (ValueError,TypeError,AttributeError) as error:self.send_json({'error':str(error) or 'ข้อมูลไม่ถูกต้อง'},400)







            except Exception:self.send_json({'error':'บันทึกปุ่มลัดไม่สำเร็จ'},500)







            return















        if path == '/api/obs/config':







            try:







                origin=urllib.parse.urlparse(self.headers.get('Origin',''))







                if origin.scheme!='http' or origin.hostname not in ('localhost','127.0.0.1') or origin.port!=self.server.server_port:







                    self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=4096:raise ValueError('invalid')







                data=json.loads(self.rfile.read(size))







                self.send_json(obs_connection.save(data))







            except (ValueError,TypeError,AttributeError):self.send_json({'error':'ข้อมูล OBS ไม่ถูกต้อง'},400)







            except Exception:self.send_json({'error':'บันทึกการตั้งค่า OBS ไม่สำเร็จ'},500)







            return















        if path == '/api/obs/test':







            try:







                origin = urllib.parse.urlparse(self.headers.get('Origin', ''))







                if origin.scheme != 'http' or origin.hostname not in ('localhost', '127.0.0.1') or origin.port != self.server.server_port:







                    self.send_json({'ok': False, 'message': 'Invalid origin'}, 403); return







                size = int(self.headers.get('Content-Length', 0))







                if not 0 < size <= 4096: raise ValueError('Invalid request')







                data = json.loads(self.rfile.read(size))







                host = data.get('host', '').strip()







                port = int(data.get('port', 0))







                password = data.get('password', '')







                if not host or len(host) > 253 or any(c in host for c in '/\\@?#') or not 1 <= port <= 65535 or not isinstance(password, str): raise ValueError('Invalid request')







                if not password and not data.get('clear_password'): password = obs_connection.password_for(host, port)







                import obsws_python as obs







                client = None







                try:







                    client = obs.ReqClient(host=host, port=port, password=password, timeout=3)







                    version = client.get_version()







                    clip_markers.configure(host, port, password)







                    self.send_json({'ok': True, 'message': 'เชื่อมต่อ OBS สำเร็จ (OBS ' + str(getattr(version, 'obs_version', '')) + ')'})







                finally:







                    if client is not None:







                        try: client.base_client.ws.close()







                        except Exception: pass







            except (ValueError, TypeError, AttributeError, json.JSONDecodeError):







                self.send_json({'ok': False, 'message': 'ข้อมูลการเชื่อมต่อไม่ถูกต้อง'}, 400)







            except ImportError:







                self.send_json({'ok': False, 'message': 'ไม่พบส่วนเชื่อมต่อ OBS WebSocket ในโปรแกรม'}, 503)







            except Exception:







                self.send_json({'ok': False, 'message': 'เชื่อมต่อ OBS ไม่สำเร็จ ตรวจสอบ OBS, พอร์ต และรหัสผ่าน'}, 502)







            return















        if path == '/api/clip-markers':







            try:







                origin = urllib.parse.urlparse(self.headers.get('Origin', ''))







                if origin.scheme != 'http' or origin.hostname not in ('localhost', '127.0.0.1') or origin.port != self.server.server_port:







                    self.send_json({'ok': False, 'message': 'Invalid origin'}, 403); return







                size = int(self.headers.get('Content-Length', 0))







                if not 0 < size <= 1024: raise ValueError('Invalid request')







                data = json.loads(self.rfile.read(size))







                self.send_json(clip_markers.action(data.get('action')))







            except (ValueError, TypeError, AttributeError):







                self.send_json({'ok': False, 'message': 'คำสั่งไม่ถูกต้อง'}, 400)







            except OSError:







                self.send_json({'ok': False, 'message': 'เปิดหรือบันทึกไฟล์มาร์กคลิปไม่สำเร็จ'}, 500)







            return















        if path == '/api/supporters/action':







            try:







                origin=self.headers.get('Origin','');parsed_origin=urllib.parse.urlparse(origin)







                if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                    self.send_json({'ok':False,'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=8*1024*1024:raise ValueError('Invalid request')







                data=json.loads(self.rfile.read(size))







                if not isinstance(data,dict):raise ValueError('Invalid request')







                from supporters_service import action







                self.send_json(action(data))







            except (ValueError,TypeError,AttributeError):self.send_json({'ok':False,'error':'ข้อมูลไม่ถูกต้อง'},400)







            return















        if path == '/api/window/frame':







            origin=urllib.parse.urlparse(self.headers.get('Origin',''))







            if origin.scheme!='http' or origin.hostname not in ('localhost','127.0.0.1') or origin.port!=self.server.server_port:







                self.send_json({'ok':False},403);return







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<512:raise ValueError('Invalid request')







                data=json.loads(self.rfile.read(size))







                from app_window_frame import action







                self.send_json(action(data.get('action'), data))







            except Exception:self.send_json({'ok':False},400)







            return















        if path == '/api/window/owner':







            try:







                origin=self.headers.get('Origin')







                if origin:







                    parsed_origin=urllib.parse.urlparse(origin)







                    if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                        self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=1024:raise ValueError('Invalid request')







                data=json.loads(self.rfile.read(size))







                from app_window_ownership import set_tool_owner







                self.send_json(set_tool_owner(data.get('name','')))







            except (ValueError,TypeError,AttributeError):self.send_json({'error':'Invalid request'},400)







            return















        if path == '/api/chatbot/auth':







            try:







                origin = self.headers.get('Origin')







                if origin:







                    parsed_origin = urllib.parse.urlparse(origin)







                    if parsed_origin.scheme != 'http' or parsed_origin.hostname not in ('localhost', '127.0.0.1') or parsed_origin.port != self.server.server_port:







                        self.send_json({'error':'Invalid origin'},403); return







                size=int(self.headers.get('Content-Length',0))







                if not 0 < size <= 4096: raise ValueError('Invalid request')







                data=json.loads(self.rfile.read(size)); platform=data.get('platform');action=data.get('action')







                if platform not in ('twitch','kick') or action not in ('start','disconnect'):raise ValueError('Invalid request')







                if action == 'start':bot_accounts.start(platform)







                else:bot_accounts.disconnect(platform)







                self.send_json({'ok':True})







            except (ValueError, TypeError, AttributeError) as error:self.send_json({'error':str(error) or 'ไม่สามารถเริ่มเชื่อมต่อบัญชีได้'},400)







            return















        if path == '/api/chatbot/send':







            try:







                origin=self.headers.get('Origin')







                if origin:







                    parsed_origin=urllib.parse.urlparse(origin)







                    if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                        self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=8192: raise ValueError('Invalid request')







                data=json.loads(self.rfile.read(size));message=data.get('message');targets=data.get('targets')







                if not isinstance(message,str) or not message.strip() or len(message)>480 or any(c in message for c in '\r\n') or not isinstance(targets,list) or not targets or len(set(targets))!=len(targets) or any(p not in ('twitch','kick') for p in targets): raise ValueError('ข้อความหรือแพลตฟอร์มไม่ถูกต้อง')







                results={}







                for platform in targets:







                    with chat_bridge._lock: client=chat_bridge._clients.get(platform)







                    if not client or not client.is_connected or not client.can_send:







                        results[platform]={'ok':False,'error':'บัญชีหรือแชทยังไม่พร้อม'};continue







                    try: results[platform]={'ok':bool(client.send_message(message.strip()))}







                    except Exception: results[platform]={'ok':False,'error':'ส่งข้อความไม่สำเร็จ'}







                self.send_json({'results':results})







            except (ValueError,TypeError,AttributeError): self.send_json({'error':'ข้อความหรือแพลตฟอร์มไม่ถูกต้อง'},400)







            return















        if path == '/api/translate/mode':







            try:







                size = int(self.headers.get('Content-Length', 0))







                data = json.loads(self.rfile.read(size)) if size else {}







                mode = data.get('mode', 'translate')







                chat_bridge.set_translate_mode(mode)







                self.send_json({'ok': True, 'mode': mode})







            except Exception as e:







                self.send_json({'error': str(e)}, 400)







            return















        if path == '/api/translate/provider':







            try:







                size = int(self.headers.get('Content-Length', 0))







                data = json.loads(self.rfile.read(size)) if size else {}







                provider = data.get('provider', 'google')







                if getattr(chat_bridge, 'translator', None):







                    chat_bridge.translator.provider = provider







                self.send_json({'ok': True, 'provider': provider})







            except Exception as e:







                self.send_json({'error': str(e)}, 400)







            return















        if path == '/api/test/chat':







            try:







                size = int(self.headers.get('Content-Length', 0))







                data = json.loads(self.rfile.read(size)) if size else {}







                plat = data.get('platform', 'Twitch')







                author = data.get('author', 'Viewer')







                text = data.get('text', '')







                from chat_bridge import ChatMessage







                chat_bridge._on_message(plat, ChatMessage(plat.lower(), author, text))







                self.send_json({'ok': True})







            except Exception as e:







                self.send_json({'error': str(e)}, 400)







            return















        if path == '/api/chatbot/config':







            try:







                origin = self.headers.get('Origin')







                if origin:







                    parsed_origin = urllib.parse.urlparse(origin)







                    if parsed_origin.scheme != 'http' or parsed_origin.hostname not in ('localhost', '127.0.0.1') or parsed_origin.port != self.server.server_port:







                        self.send_json({'error': 'Invalid origin'}, 403); return







                size = int(self.headers.get('Content-Length', 0))







                if not 0 < size <= 65536: raise ValueError('Invalid configuration')







                data = json.loads(self.rfile.read(size))







                if not isinstance(data, dict): raise ValueError('Invalid configuration')







                chat_bridge.bot.configure(data)







                self.send_json({'ok': True})







            except (ValueError, TypeError, AttributeError): self.send_json({'error': 'Invalid configuration'}, 400)







            return















        if path=='/api/app-instance/reopen':







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=4096:raise ValueError()







                data=json.loads(self.rfile.read(size))







                if data.get('project')!=APP_PROJECT_ID:raise ValueError()







                if not app_presence.reserve_launch():self.send_json({'error':'Instance is closing'},503);return







                self.send_json({'ok':True})







            except (ValueError,TypeError,AttributeError):self.send_json({'error':'Invalid instance'},400)







            return















        if path=='/api/app-presence/leave':







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=4096:raise ValueError()







                data=json.loads(self.rfile.read(size));client=data.get('client')







                if not isinstance(client,str) or len(client)>128:raise ValueError()







                app_presence.leave(client);self.send_json({'ok':True})







            except (ValueError,TypeError,AttributeError):self.send_json({'error':'Invalid client'},400)







            return















        if path=='/api/chat/delete':







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=4096:raise ValueError()







                data=json.loads(self.rfile.read(size));target=str(data['id'])







                with chat_bridge._lock:chat_bridge._messages=[msg for msg in chat_bridge._messages if str(msg['id'])!=target]







                overlay_events.publish({'event':'CHAT_DELETE','payload':{'id':target}})







                self.send_json({'ok':True})







            except (ValueError,TypeError,KeyError):self.send_json({'error':'Invalid message'},400)







            return















        if path in ('/api/dock/action','/api/dock/state'):







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=1048576:raise ValueError()







                data=json.loads(self.rfile.read(size))







                if not isinstance(data,dict):raise ValueError()







                if path.endswith('/state'):DOCK_STATE.clear();DOCK_STATE.update(data)







                else:overlay_events.publish({'event':'DOCK_CONTROL','payload':data})







                self.send_json({'ok':True})







            except (ValueError,TypeError):self.send_json({'error':'Invalid Dock data'},400)







            return















        if path=='/api/chat-config/preview':







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=1048576:raise ValueError()







                widget=json.loads(self.rfile.read(size))







                if not isinstance(widget,dict):raise ValueError()







                self.send_json(build_chat_config(widget,(get_layout() or {}).get('legacyChat') or {}))







            except (ValueError,TypeError):self.send_json({'error':'Invalid chat settings'},400)







            return















        if path=='/api/giveaway-settings':







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=5*1024*1024:raise ValueError('Invalid settings size')







                data=json.loads(self.rfile.read(size))







                if not isinstance(data,dict) or not isinstance(data.get('code'),str) or len(data.get('code',''))>100:raise ValueError('Invalid settings')







                data={key:data[key] for key in ('code','duration','display','imageUrl') if key in data};layout=get_layout();layout.setdefault('legacyTools',{})['giveaway']=data;save_layout(layout);self.send_json({'saved':True})







            except (ValueError,OSError) as error:self.send_json({'error':str(error)},400)







            return







        if path=='/api/desktop-overlays':







            try:







                size=int(self.headers.get('Content-Length',0))







                if not 0<size<=65536:raise ValueError('Invalid request')







                data=json.loads(self.rfile.read(size))







                if data.get('action')=='configure':







                    entries=data.get('overlays')







                    if not isinstance(entries,list) or len(entries)>3:raise ValueError('Overlay+ รองรับสูงสุด 3 หน้าต่าง')







                    for entry in entries:







                        if not isinstance(entry,dict) or (entry.get('url') and urllib.parse.urlparse(entry['url']).scheme not in ('http','https')):raise ValueError('URL ไม่ถูกต้อง')







                    layout=get_layout();settings=layout.setdefault('legacyTools',{});settings['more_overlays']=entries







                    game=data.get('game') or {}







                    for key,low,high in [('game_overlay_width',120,3840),('game_overlay_height',80,2160),('game_overlay_font_size',8,120),('game_overlay_alpha',0,1)]:







                        if key in game:settings[key]=max(low,min(high,float(game[key]))) if key.endswith('alpha') else int(max(low,min(high,float(game[key]))))







                    if 'game_overlay_text_color' in game:







                        import re







                        if not re.fullmatch(r'#[0-9a-fA-F]{6}',str(game['game_overlay_text_color'])):raise ValueError('สีไม่ถูกต้อง')







                        settings['game_overlay_text_color']=game['game_overlay_text_color']







                    from viewer_overlay_config import configure







                    viewer=data.get('viewer') or {}







                    configure(settings,viewer)







                    save_layout(layout);overlay_events.publish({'event':'DESKTOP_OVERLAY_STATE','payload':settings})







                    for item in desktop_overlays.instances.values():







                        if game and item['kind']=='game' and item['process'].poll() is None:







                            desktop_overlays.command(item,'set_alpha',alpha=settings.get('game_overlay_alpha',.85))







                            desktop_overlays.command(item,'set_size',width=settings.get('game_overlay_width',360),height=settings.get('game_overlay_height',500))







                        elif viewer and item['kind']=='viewer' and item['process'].poll() is None:







                            desktop_overlays.command(item,'set_alpha',alpha=settings.get('viewer_overlay_alpha',1))







                            desktop_overlays.command(item,'set_size',width=settings.get('viewer_overlay_width',400),height=settings.get('viewer_overlay_height',80))







                    self.send_json({'saved':True})







                else:self.send_json(desktop_overlays.act(data.get('action'),data.get('kind'),f'http://127.0.0.1:{self.server.server_port}'))







            except (ValueError,OSError) as error:self.send_json({'error':str(error)},400)







            return







        if path == '/api/playroom/import':







            try:







                origin=self.headers.get('Origin')







                if origin:







                    parsed_origin=urllib.parse.urlparse(origin)







                    if parsed_origin.scheme!='http' or parsed_origin.hostname not in ('localhost','127.0.0.1') or parsed_origin.port!=self.server.server_port:







                        self.send_json({'error':'Invalid origin'},403);return







                size=int(self.headers.get('Content-Length',0))







                result=playroom_media.import_file(self.rfile,size,self.headers.get('X-Filename',''))







                self.send_json(result)







            except (ValueError,OSError) as error:self.send_json({'error':str(error)},400)







            return







        if path.startswith('/api/rvc/'):







            try:







                rvc_service.require_full()







                origin = self.headers.get('Origin')







                if origin and origin != 'null' and urllib.parse.urlparse(origin).hostname not in ('localhost','127.0.0.1','tauri.localhost'):







                    self.send_json({'error':'Forbidden origin'},403)







                    return







                if path == '/api/rvc/import':







                    original_name = urllib.parse.unquote(self.headers.get('X-Filename',''))







                    name = os.path.basename(original_name)







                    if name != original_name or not name.lower().endswith(('.pth','.index')):







                        raise ValueError('Choose a .pth or .index model file')







                    size = int(self.headers.get('Content-Length',0))







                    if not 0 < size <= 2147483648:raise ValueError('Invalid model size')







                    rvc_service.model_dir.mkdir(parents=True,exist_ok=True)







                    target=rvc_service.model_dir/name







                    if target.exists():raise ValueError('A file with this name already exists')







                    temporary=None







                    try:







                        with tempfile.NamedTemporaryFile(dir=rvc_service.model_dir,suffix='.partial',delete=False) as stream:







                            temporary=stream.name







                            remaining=size







                            while remaining:







                                chunk=self.rfile.read(min(1048576,remaining))







                                if not chunk:raise ValueError('Upload incomplete')







                                stream.write(chunk);remaining-=len(chunk)







                        os.replace(temporary,target)







                    finally:







                        if temporary and os.path.isfile(temporary):os.remove(temporary)







                    self.send_json({'ok':True,'models':rvc_service.public_models()})







                    return







                length=int(self.headers.get('Content-Length',0))







                if length>1048576:raise ValueError('Invalid request size')







                body=json.loads(self.rfile.read(length)) if length else {}







                if path == '/api/rvc/select':result=rvc_service.select(body.get('id'),body.get('enabled',True))







                elif path == '/api/rvc/download':result=rvc_service.download(body.get('id'))







                elif path == '/api/rvc/cancel':result=rvc_service.cancel()







                elif path == '/api/rvc/open-folder':







                    rvc_service.model_dir.mkdir(parents=True,exist_ok=True)







                    os.startfile(str(rvc_service.model_dir))







                    result={'ok':True}







                else:







                    self.send_json({'error':'Unknown RVC endpoint'},404)







                    return







                self.send_json(result)







            except PermissionError as error:self.send_json({'error':str(error)},403)







            except (ValueError,TypeError,OSError) as error:self.send_json({'error':str(error)},400)







            except Exception as error:self.send_json({'error':str(error)},500)







            return















        if path == '/api/composer/normalize':







            try:







                size = int(self.headers.get('Content-Length', 0))







                if not 0 < size <= 8388608:







                    raise ValueError('Invalid layout size')







                self.send_json(normalize_layout(json.loads(self.rfile.read(size))))







            except (ValueError, TypeError, KeyError):







                self.send_json({'error': 'Invalid Composer profile'}, 400)







            return















        if path == '/api/overlay/events':







            try:







                size = int(self.headers.get('Content-Length', 0))







                if not 0 < size <= 1048576:







                    self.send_json({'error': 'Invalid event size'}, 400)







                    return







                item = json.loads(self.rfile.read(size))







                sequence = overlay_events.publish(item)







                if item.get('event') == 'CHAT_CLEAR':







                    chat_bridge.clear_messages()







                self.send_json({'ok': True, 'cursor': sequence})







            except (ValueError, TypeError, AttributeError):







                self.send_json({'error': 'Invalid event'}, 400)







            return















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















    def serve_overlay(self, view='composer'):







        if view=='chat' and (get_layout() or {}).get('legacyChat'):







            self.serve_custom_file(os.path.join(DIST_DIR,'legacy_chat.html'),'text/html; charset=utf-8')







            return







        target = os.path.join(DIST_DIR, 'composer.html')







        if not os.path.isfile(target):







            target = os.path.join(SRC_DIR, 'composer.html')







        with open(target, 'r', encoding='utf-8') as stream:







            html = stream.read()







        html = html.replace('<head>', '<head><script>window.BP3LegacyView=' + json.dumps(view) + ';</script>', 1)







        body = html.encode('utf-8')







        self.send_response(200)







        self.send_header('Content-Type', 'text/html; charset=utf-8')







        self.send_header('Content-Length', str(len(body)))







        self.send_header('Cache-Control', 'no-store')







        self.send_cors_headers()







        self.end_headers()







        self.wfile.write(body)















    def send_json(self, data, status=200):







        body = json.dumps(data, ensure_ascii=False).encode('utf-8')







        self.send_response(status)







        self.send_header('Content-Type', 'application/json; charset=utf-8')







        self.send_header('Content-Length', str(len(body)))







        self.send_header('Cache-Control', 'no-store')







        self.send_cors_headers()







        self.end_headers()







        self.wfile.write(body)















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







        







        # 1. Handle TTS Audio streaming (with high-speed LRU memory cache)







        if path == '/api/tts':







            text = qs.get('text', [''])[0]







            gender = qs.get('gender', ['female'])[0]







            rate = qs.get('rate', ['+0%'])[0]







            pitch = qs.get('pitch', ['+0Hz'])[0]







            volume = qs.get('volume', ['+0%'])[0]







            







            try:







                preview = qs.get('preview', ['0'])[0] == '1'







                processed_text = text if preview else dict_manager.apply_replace(text)







                







                # Check RVC state for accurate caching







                rvc_enabled = bool(rvc_service and getattr(rvc_service, 'data', {}).get('enabled') and getattr(rvc_service, 'data', {}).get('loaded'))







                rvc_model = getattr(rvc_service, 'data', {}).get('selected') if rvc_enabled else None







                cache_key = (processed_text, gender, rate, pitch, volume, preview, rvc_enabled, rvc_model)















                cached_hit = None







                with _TTS_CACHE_LOCK:







                    if cache_key in _TTS_AUDIO_CACHE:







                        cached_hit = _TTS_AUDIO_CACHE[cache_key]







                        _TTS_AUDIO_CACHE.move_to_end(cache_key)















                if cached_hit:







                    audio_bytes, audio_mime = cached_hit







                else:







                    audio_bytes = tts_service.generate_audio_bytes(processed_text, gender, rate, pitch, volume)







                    if audio_bytes:







                        if preview:







                            audio_mime = 'audio/mpeg'







                        else:







                            try:







                                audio_bytes, audio_mime = rvc_service.convert(audio_bytes)







                            except Exception:







                                import logging







                                logging.getLogger('tts_service').exception('RVC conversion failed; returning original Edge-TTS audio')







                                audio_mime = 'audio/mpeg'







                        with _TTS_CACHE_LOCK:







                            _TTS_AUDIO_CACHE[cache_key] = (audio_bytes, audio_mime)







                            if len(_TTS_AUDIO_CACHE) > _TTS_CACHE_MAX:







                                _TTS_AUDIO_CACHE.popitem(last=False)















                if audio_bytes:







                    self.send_response(200)







                    self.send_header('Content-Type', audio_mime)







                    self.send_header('Content-Length', str(len(audio_bytes)))







                    self.send_cors_headers()







                    self.end_headers()







                    try:self.wfile.write(audio_bytes)







                    except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass







                    return







                else:







                    import logging







                    logging.getLogger('tts_service').warning('TTS synthesis returned no audio')







                    self.send_response(500)







                    self.send_cors_headers()







                    self.end_headers()







                    return







            except Exception:







                import logging







                logging.getLogger('tts_service').exception('TTS request failed')







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







        elif path == '/api/platform/settings':
            settings_path = os.path.join(str(DATA_ROOT), 'platform_settings.json')
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r', encoding='utf-8') as sf:
                        response_data = json.load(sf)
                except Exception:
                    response_data = {}
            else:
                response_data = {}

        elif path == '/api/version':







            response_data = {'version': get_current_version(), 'product': 'broadcast-playroom-3', 'build_type': get_build_type()}







        elif path == '/api/check-update':

            up_info = check_for_update()

            if up_info.get('has_update'):

                try:

                    start_background_download(up_info)

                except Exception as exc:

                    pass

            up_info['download_status'] = get_update_runtime_status()

            response_data = up_info



        elif path == '/api/update-status':

            response_data = get_update_runtime_status()



        elif path == '/api/apply-update':

            response_data = restart_and_apply_update()







        elif path == '/api/defender/status':







            response_data = DefenderExclusionManager.get_status_info()







        elif path == '/api/logs':







            query = urllib.parse.parse_qs(parsed.query)







            try:







                since = float(query.get('since', ['0'])[0])







            except (ValueError, TypeError):







                since = 0.0







            logs = log_capture.get_logs(since=since)







            latest_time = logs[-1]['time'] if logs else since







            response_data = {'logs': logs, 'latest_time': latest_time}







        elif path == '/api/open-external':







            query = urllib.parse.parse_qs(parsed.query)







            url = query.get('url', [''])[0].strip()







            if url.startswith('http://') or url.startswith('https://'):







                import webbrowser







                webbrowser.open(url)







                response_data = {'ok': True}







            else:







                response_data = {'error': 'Invalid URL scheme'}







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







    config_file = os.path.join(os.path.dirname(__file__), 'legacy_compat.json')







    if os.path.isfile(config_file):







        with open(config_file, 'r', encoding='utf-8') as stream:







            configured = json.load(stream)







        if 'composer' in configured:







            candidate = int(configured['composer'])







            if not 1 <= candidate <= 65535:







                raise ValueError('Invalid Composer port')







            PORT = candidate







    HTTPServer.allow_reuse_address = True







    if is_port_in_use(PORT):







        raise OSError(f'Composer port {PORT} is busy. Close the previous Broadcast Playroom instance; the OBS URL will not be silently changed.')







    







    from loopback_server import LoopbackServer







    server = LoopbackServer(('127.0.0.1', PORT), QuietHandler)







    return server















def find_browser():







    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"







    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"







    if os.path.exists(chrome_path):







        return chrome_path







    if os.path.exists(edge_path):







        return edge_path







    return None















def open_app_window(main_url):
    # 1. Prefer native frameless desktop window (removes browser titlebar completely)
    if '--browser' not in sys.argv:
        try:
            import webview
            storage_path = os.path.join(str(DATA_ROOT), 'webview_data')
            os.makedirs(storage_path, exist_ok=True)
            w = webview.create_window(
                title='Broadcast Playroom 3',
                url=main_url,
                width=1600,
                height=950,
                min_size=(760, 500),
                frameless=True,
                easy_drag=False
            )
            from app_window_frame import set_webview_window, setup_app_window_icon, is_app_shutting_down
            set_webview_window(w)

            def _on_closing():
                if is_app_shutting_down():
                    return True
                try:
                    w.evaluate_js("if (typeof requestAppExit === 'function') requestAppExit();")
                except Exception:
                    pass
                return False

            w.events.closing += _on_closing
            
            def _setup_icon():
                time.sleep(0.8)
                try:
                    if w and w.native:
                        h = w.native.Handle.ToInt64() if hasattr(w.native, 'Handle') else int(w.native)
                        setup_app_window_icon(h)
                except Exception:
                    pass
            threading.Thread(target=_setup_icon, daemon=True).start()
            
            try:
                close_splash()
            except Exception:
                pass

            print("[LAUNCH] Opening Native Frameless Desktop window (No browser bar)...", flush=True)
            webview.start(storage_path=storage_path)
            print("[INFO] Native Desktop window closed; stopping owned services.", flush=True)
            sys.exit(0)
        except Exception as e:
            print(f"[WARN] Native frameless window failed ({e}), falling back to Chrome/Edge app mode...", flush=True)

    browser_bin = find_browser()
    launched = False















    # Create dedicated, isolated application profile directory so that:







    # 1. It NEVER touches or shares the user's personal Chrome profile, history, or cookies.







    # 2. Chrome plugins/extensions (Bitwarden, LastPass, etc.) are 100% excluded and disabled.







    # 3. Autofill, password popups, and translate banners are strictly suppressed.







    app_profile_dir = os.path.join(str(DATA_ROOT), 'browser_profile')







    os.makedirs(app_profile_dir, exist_ok=True)















    if browser_bin:







        cmd = [







            browser_bin,







            f"--app={main_url}",







            f"--user-data-dir={app_profile_dir}",







            "--enable-features=WebAppWindowControlsOverlay",







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







        print(f"[LAUNCH] Opening Desktop App window...", flush=True)







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







        webbrowser.open(main_url)























class ExistingInstanceClosing(Exception):







    pass























def reuse_existing_server():







    base=f'http://127.0.0.1:{PORT}';verified=False







    try:







        with urllib.request.urlopen(base+'/api/app-instance',timeout=2) as response:







            data=json.load(response)







        if data.get('application')!='BroadcastPlayroom3' or data.get('project')!=APP_PROJECT_ID or data.get('edition')!=rvc_service.edition:return False







        verified=True







        if data.get('closing'):raise ExistingInstanceClosing()







        request=urllib.request.Request(base+'/api/app-instance/reopen',data=json.dumps({'project':APP_PROJECT_ID}).encode(),headers={'Content-Type':'application/json'},method='POST')







        with urllib.request.urlopen(request,timeout=2) as response:







            return json.load(response).get('ok') is True







    except OSError:







        if verified:raise ExistingInstanceClosing()







        return False







    except (ValueError,AttributeError):return False























def main():







    global LEGACY_STATUS, LEGACY_FILTER_IMPORT_ENABLED







    is_headless = '--headless' in sys.argv







    no_splash = is_headless or '--no-splash' in sys.argv







    splash_ctrl = None







    if not no_splash:







        try:







            from splash import create_splash







            splash_ctrl = create_splash()







            global _GLOBAL_SPLASH_CTRL







            _GLOBAL_SPLASH_CTRL = splash_ctrl







            splash_ctrl.set_progress(15, "กำลังตรวจสอบพอร์ตและเริ่มต้นระบบ...")



        except Exception:



            splash_ctrl = None



    try:

        if apply_pending_update_on_startup(splash_ctrl):

            print("[UPDATER] Successfully applied pending update on startup!", flush=True)

    except Exception as exc:

        print(f"[UPDATER] Startup update check failed: {exc}", flush=True)







    deadline=time.monotonic()+12







    while True:







        try:







            server = start_server()







            break







        except OSError as error:







            try:







                if reuse_existing_server():







                    print('[INFO] Broadcast Playroom is already running on port 8801. Re-opening app window...', flush=True)







                    print('[INFO] ตรวจพบว่าเซิร์ฟเวอร์ Broadcast Playroom 3 กำลังทำงานอยู่แล้วที่พอร์ต 8801 กำลังเปิดหน้าต่างโปรแกรมขึ้นมาให้ครับ', flush=True)







                    close_splash()







                    open_app_window(f'http://127.0.0.1:{PORT}/index.html')







                    return 0







            except ExistingInstanceClosing:







                if time.monotonic()<deadline:







                    time.sleep(.2)







                    continue







            print(f'[ERROR] {error}',flush=True)







            return 1







    donation_goal_service.sync(get_layout())







    avatar_mic_service.sync(get_layout())







    server_thread = threading.Thread(target=server.serve_forever, daemon=True)







    server_thread.start()







    legacy_servers, LEGACY_STATUS = start_legacy_servers(QuietHandler, PORT, os.path.join(os.path.dirname(__file__), 'legacy_compat.json'))







    LEGACY_FILTER_IMPORT_ENABLED = True







    try:







        from legacy_obs_settings import migrate as migrate_legacy_obs







        migrate_legacy_obs(obs_connection)







    except Exception:







        import logging







        logging.getLogger('obs_connection').warning('Could not import legacy OBS settings')







    obs_connection.start()







    # Clip Marker is temporarily suspended; do not register a global hotkey.















    desktop_overlays._ensure_hotkeys('game',f'http://127.0.0.1:{PORT}')







    desktop_overlays._ensure_hotkeys('overlay+',f'http://127.0.0.1:{PORT}')







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







    print("   * Close the last main app window or press Ctrl+C here to stop.", flush=True)







    print("============================================================\n", flush=True)















    try: overlay_events.prune_chat_log()







    except (OSError, UnicodeError): logging.getLogger(__name__).exception('Unable to prune chat log')















    if splash_ctrl:







        splash_ctrl.set_progress(90, "กำลังเปิดหน้าต่างหลัก...")







    if not is_headless:







        open_app_window(main_url)







    def _close_splash_delayed():







        time.sleep(0.5)







        close_splash()







    threading.Thread(target=_close_splash_delayed, daemon=True).start()















    # Closing the last main window releases owned servers after a short reopen grace.







    try:







        while True:







            if app_presence.should_exit():







                print('[INFO] Main app closed; stopping owned services and releasing ports.',flush=True)







                break







            if time.time() - overlay_events._last_log_cleanup >= 3600:







                try: overlay_events.prune_chat_log()







                except (OSError, UnicodeError): logging.getLogger(__name__).exception('Unable to prune chat log')







            time.sleep(.5)







    except KeyboardInterrupt:







        print("\n[INFO] Stopping Dev Server...")







    finally:







        clip_hotkey.stop()







        obs_connection.stop()







        app_presence.begin_shutdown()







        chat_bridge.bot.stop()







        desktop_overlays.stop()







        now_playing_service.stop()







        donation_goal_service.stop()







        avatar_mic_service.stop()







        for legacy_server in legacy_servers:







            legacy_server.shutdown()







            legacy_server.server_close()







        server.shutdown()







        server.server_close()







        sys.exit(0)















# Keep chat history beside the active profile, including isolated test profiles.







overlay_events.chat_log_path=lambda: Path(LAYOUT_FILE).resolve().parent / "log.txt"















if __name__ == '__main__':







    sys.exit(main() or 0)







