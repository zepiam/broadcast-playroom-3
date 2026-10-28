import sys

import os

import time

import threading

import json

import logging

import re

from urllib.parse import urlparse



# Ensure project root is in path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



from overlay_events import overlay_events

from chat_twitch import TwitchChat, ChatMessage

from chat_youtube import YouTubeChat

from chat_kick import KickChat

from chat_tiktok import TikTokChat

from chat_soop import SoopChat

from chat_mylive import MyLiveChat



logger = logging.getLogger("chat_bridge")



def verify_twitch_channel(channel):

    """Return True/False only for a definite lookup; None means unavailable."""

    try:

        import requests

        from chat_twitch import TWITCH_GQL_URL, TWITCH_GQL_CLIENT_ID

        response = requests.post(TWITCH_GQL_URL, json={'query': 'query { user(login: "%s") { id } }' % channel}, headers={'Client-ID': TWITCH_GQL_CLIENT_ID}, timeout=5)

        response.raise_for_status()

        data = response.json()

        if data.get('errors') or not isinstance(data.get('data'), dict) or 'user' not in data['data']:

            return None

        return data['data']['user'] is not None

    except Exception:

        return None





def fetch_stream_title(platform: str, channel: str) -> str:

    plat = (platform or '').lower()

    ch = (channel or '').strip()

    if not ch:

        return ''

    if plat == 'twitch':

        try:

            import urllib.request, json

            q = 'query { user(login: "%s") { broadcastSettings { title } stream { title } } }' % ch

            req = urllib.request.Request('https://gql.twitch.tv/gql', data=json.dumps({'query': q}).encode(), headers={'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})

            with urllib.request.urlopen(req, timeout=5) as res:

                data = json.loads(res.read())

                user = data.get('data', {}).get('user', {}) or {}

                stream = user.get('stream') or {}

                return stream.get('title') or (user.get('broadcastSettings') or {}).get('title') or ''

        except Exception:

            return ''

    elif plat == 'kick':

        try:

            import urllib.request, json

            req = urllib.request.Request(f'https://kick.com/api/v2/channels/{ch}', headers={'User-Agent': 'Mozilla/5.0'})

            with urllib.request.urlopen(req, timeout=5) as res:

                data = json.loads(res.read())

                return (data.get('livestream') or {}).get('session_title') or (data.get('user') or {}).get('bio') or ''

        except Exception:

            return ''

    elif plat == 'soop':

        try:

            from chat_soop import parse_soop_target, _resolve_channel

            bid, bno = parse_soop_target(ch)

            info = _resolve_channel(bid, bno, timeout=5.0)

            return info.get("title", "") or ""

        except Exception:

            return ''

    elif plat == 'mylive':

        try:

            import urllib.request, json, re

            raw = ch.strip()

            m = re.search(r"/streams/(\d+)", raw)

            stream_id = m.group(1) if m else (raw if raw.isdigit() else None)

            if not stream_id:

                clean = raw.rstrip("/").split("/")[-1].lstrip("@").strip()

                req = urllib.request.Request(f"https://mylive.in.th/a/users/{clean}", headers={"User-Agent": "Mozilla/5.0"})

                with urllib.request.urlopen(req, timeout=5) as res:

                    data = json.loads(res.read())

                    stream_id = data.get("live")

            if stream_id and str(stream_id) not in ("False", "false", "0"):

                req = urllib.request.Request(f"https://mylive.in.th/a/streams/{stream_id}", headers={"User-Agent": "Mozilla/5.0"})

                with urllib.request.urlopen(req, timeout=5) as res:

                    data = json.loads(res.read())

                    return data.get("title") or ""

        except Exception:

            return ''

    return ''



class ChatBridge:

    def __init__(self):

        self._lock = threading.Lock()

        self._clients = {}

        self._bot_blocked_names = set()

        self._bot_banned_words = ()

        self.accounts = None

        self._reconnect = {}

        self._reconnect_interval = 10.0

        self._reconnect_timeout = 60.0

        self._statuses = {

            'twitch': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': '', 'title': ''},

            'youtube': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': '', 'title': ''},

            'kick': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': '', 'title': ''},

            'tiktok': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': '', 'title': ''},

            'soop': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': '', 'title': ''},

            'mylive': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': '', 'title': ''},

        }

        self._messages = []

        self._msg_id_counter = 0

        self._last_viewer_state = None

        from bot_runtime import BotRuntime

        self.bot = BotRuntime(lambda platform: self._clients.get(platform))

        self.bot.start()

        try:

            from translator import Translator

            self.translator = Translator()

        except Exception:

            self.translator = None

        self.translate_mode = 'translate'

        self._stream_titles = {}



    def _on_message(self, platform_name: str, msg: ChatMessage):

        with self._lock:

            self._msg_id_counter += 1

            author = getattr(msg, 'author', '') or getattr(msg, 'username', 'ผู้ชม')

            text = getattr(msg, 'text', '')

            avatar = getattr(msg, 'avatar_url', '') or (getattr(msg, 'extra', {}) or {}).get('avatar_url', '') or f"https://api.dicebear.com/7.x/bottts/svg?seed={author}"

            extra = getattr(msg, 'extra', {}) or {}

            emotes=[]

            for original in extra.get('emotes',[]) or []:

                emote=dict(original)

                if not emote.get('url') and emote.get('id') is not None:

                    emote['url']='/emote/'+str(emote['id'])

                emotes.append(emote)

            payload = {

                'id': self._msg_id_counter,

                'event': getattr(msg, 'event', 'message') or 'message',

                'amount': getattr(msg, 'amount', None),

                'currency': getattr(msg, 'currency', ''),

                'event_details': getattr(msg, 'event_details', None) or extra.get('event_details'),

                'platform': platform_name.capitalize(),

                'platform_key': platform_name.lower(),

                'username': author,

                'own_message': bool(extra.get('_own_message')),

                'text': text,

                'avatar': avatar,

                'color': getattr(msg, 'color', None) or extra.get('color', '#38bdf8'),

                'isVip': getattr(msg, 'is_vip', False) or getattr(msg, 'is_mod', False),

                'badges': getattr(msg, 'badges', None) or extra.get('badges', []),

                'emotes': emotes,

                'twitch_emotes': emotes,

                'segments': extra.get('segments', []),

                'raw_text': extra.get('raw_text', text),

                'original_text': extra.get('original_text', ''),

                'is_translated': extra.get('is_translated', extra.get('translated',False)),

                'sticker_url': extra.get('sticker_url', ''),

                'system_text': getattr(msg, 'system_text', '') or '',

                'character_job': extra.get('character_job', extra.get('_job','')),

                'time': time.strftime('%H:%M', time.localtime())

            }

            self._messages.append(payload)

            if len(self._messages) > 1000:

                self._messages = self._messages[-1000:]

            print(f"[{platform_name}] {author}: {text}", flush=True)

        with self._lock: blocked_for_bot=author.strip().lower() in self._bot_blocked_names or any(word in text.lower() for word in self._bot_banned_words)

        if not blocked_for_bot:self.bot.on_message(platform_name.lower(), author, text)



    def set_bot_blocklist(self, names, banned_words=()):

        with self._lock:

            self._bot_blocked_names = {str(name).strip().lower() for name in names if str(name).strip()}

            self._bot_banned_words = tuple(str(word).strip().lower() for word in banned_words if str(word).strip())



    def _publish_viewers(self):

        with self._lock:

            counts = {name: int(status.get('viewers') or 0) if status.get('connected') else 0

                      for name, status in self._statuses.items()}

            connected=[name for name,status in self._statuses.items() if status.get('connected')]

            state=(counts,connected)

            if state == self._last_viewer_state:

                return

            self._last_viewer_state = state

        overlay_events.publish({'event': 'VIEWERS_UPDATE', 'payload': {'per_platform': counts, 'total': sum(counts.values()), 'connected': connected}})



    def _on_status(self, platform_name: str, status_text: str):

        with self._lock:

            if platform_name in self._statuses:

                self._statuses[platform_name]['status'] = status_text

                if 'disconnected' in status_text.lower() or 'ตัดการเชื่อมต่อ' in status_text or 'หยุด' in status_text:

                    self._statuses[platform_name]['connected'] = False

                elif 'connected' in status_text.lower() or 'เชื่อมต่อแล้ว' in status_text or status_text.startswith('✅ เชื่อมต่อ') or ('เชื่อมต่อ' in status_text and not any(k in status_text for k in ('กำลัง', 'ไม่ได้', 'ไม่สำเร็จ', 'ล้มเหลว', 'ยกเลิก'))):

                    self._statuses[platform_name]['connected'] = True

                    if platform_name in self._reconnect:

                        state = self._reconnect[platform_name]

                        if state.get('timer'): state['timer'].cancel(); state['timer'] = None

                        state.update(ever_connected=True, attempts=0)



        self._publish_viewers()



    def _on_error(self, platform_name: str, error: str):

        with self._lock:

            state = self._reconnect.get(platform_name)

            status = self._statuses.get(platform_name)

            if not status:

                return

            was_connected = status['connected']

            # Sending or bot errors do not imply the incoming chat disconnected.

            connection_error = any(word in str(error).lower() for word in ('หลุด', 'ปิดลง', 'ปิดจากเซิร์ฟเวอร์', 'ws หลุด', 'connection error', 'connect error', 'เชื่อมต่อไม่ได้', 'เข้าห้องแชทไม่ได้'))

            if was_connected and not connection_error:

                status['status'] = str(error)

                return

            status.update(connected=False, status=str(error))

            should_retry = bool(state and state.get('ever_connected') and connection_error)

        self._publish_viewers()

        if should_retry:

            self._schedule_reconnect(platform_name, str(error))



    def _schedule_reconnect(self, platform, error):

        with self._lock:

            state = self._reconnect.get(platform)

            if not state or state.get('timer'):

                return

            if state['attempts'] >= 5:

                self._statuses[platform]['status'] = 'หยุดเชื่อมต่ออัตโนมัติหลังลอง 5 ครั้ง: ' + error

                return

            token = state['token']

            self._statuses[platform]['status'] = f'🔄 แชทหลุด กำลังเชื่อมต่อใหม่ใน {int(self._reconnect_interval)} วินาที: {error}'

            timer = threading.Timer(self._reconnect_interval, self._retry_connection, args=(platform, token))

            timer.daemon = True

            state['timer'] = timer

        timer.start()



    def _retry_connection(self, platform, token):

        with self._lock:

            state = self._reconnect.get(platform)

            if not state or state['token'] != token:

                return

            state['timer'] = None

            state['attempts'] += 1

            target = state['target']

            self._statuses[platform]['status'] = f'🔄 กำลังเชื่อมต่อใหม่ ({state["attempts"]}/5)'

        result = self.connect(platform, target, _reconnect_token=token)

        with self._lock:

            active = self._reconnect.get(platform)

            valid = bool(active and active['token'] == token)

        if not valid:

            return

        if not result.get('success'):

            self._schedule_reconnect(platform, result.get('error', 'เชื่อมต่อไม่สำเร็จ'))

        elif not result.get('connected'):

            with self._lock:

                state = self._reconnect.get(platform)

                if state and state['token'] == token and not self._statuses[platform]['connected'] and not state.get('timer'):

                    timer = threading.Timer(self._reconnect_timeout, self._retry_timeout, args=(platform, token))

                    timer.daemon = True

                    state['timer'] = timer

                    timer.start()



    def _retry_timeout(self, platform, token):

        with self._lock:

            state = self._reconnect.get(platform)

            if not state or state['token'] != token or self._statuses[platform]['connected']:

                return

            state['timer'] = None

        self._schedule_reconnect(platform, 'หมดเวลารอการตอบรับจากแชท')



    def _on_viewer_count(self, platform_name: str, count: int):

        with self._lock:

            if platform_name in self._statuses:

                self._statuses[platform_name]['viewers'] = count



        self._publish_viewers()



    def connect(self, platform: str, target: str, _reconnect_token=None) -> dict:

        platform = platform.lower()

        target = target.strip()

        if not target:

            return {'success': False, 'error': f'กรุณาระบุชื่อแชนแนลหรือ URL สำหรับ {platform}'}



        verified = None

        if platform == 'twitch':

            value = target

            if value.lower().startswith(('twitch.tv/', 'www.twitch.tv/', 'm.twitch.tv/')):

                value = 'https://' + value

            if '://' in value:

                parsed = urlparse(value)

                if parsed.hostname not in ('twitch.tv', 'www.twitch.tv', 'm.twitch.tv'):

                    return {'success': False, 'error': 'ลิงก์นี้ไม่ใช่ช่อง Twitch'}

                value = parsed.path.strip('/')

            target = value.lstrip('#').lower()

            if not re.fullmatch(r'[a-z0-9_]+', target):

                return {'success': False, 'error': 'กรุณาระบุชื่อช่องหรือลิงก์ช่อง Twitch'}

            verified = verify_twitch_channel(target)

            if verified is False:

                return {'success': False, 'error': 'ไม่พบช่อง Twitch นี้ กรุณาตรวจสอบชื่อช่อง'}

        if _reconnect_token is None:

            self.disconnect(platform)

            with self._lock:

                self._reconnect[platform] = {'token': object(), 'target': target, 'attempts': 0, 'ever_connected': False, 'timer': None}

        else:

            with self._lock:

                active = self._reconnect.get(platform)

                if not active or active['token'] != _reconnect_token:

                    return {'success': False, 'error': 'ยกเลิกการเชื่อมต่อแล้ว'}

                old_client = self._clients.pop(platform, None)

            if old_client:

                try: old_client.disconnect()

                except Exception: pass

        attempt_token = object()

        with self._lock:

            active = self._reconnect.get(platform)

            if not active or (_reconnect_token is not None and active['token'] != _reconnect_token):

                return {'success': False, 'error': 'ยกเลิกการเชื่อมต่อแล้ว'}

            active['attempt_token'] = attempt_token

            if platform in self._statuses:

                self._statuses[platform].update(connected=False, target=target, status='กำลังเชื่อมต่อแชท', channel_verified=verified)



        def current():

            with self._lock:

                state = self._reconnect.get(platform)

                return bool(state and state.get('attempt_token') is attempt_token)



        try:

            client = None

            account = self.accounts.get(platform) if self.accounts and platform in ('twitch','kick') else None

            if platform == 'twitch':

                client = TwitchChat(

                    oauth_token=(account or {}).get('access_token') or '', bot_username=(account or {}).get('username') or '',

                    on_message=lambda m: self._on_message('Twitch', m) if current() else None,

                    on_status=lambda s: self._on_status('twitch', s) if current() else None,

                    on_error=lambda e: self._on_error('twitch', e) if current() else None,

                    on_viewer_count=lambda p, c: self._on_viewer_count('twitch', c)

                )

                if account:

                    client._refresh_token = account.get('refresh_token') or ''

                    client._on_token_refreshed = lambda access, refresh, *expiry: self.accounts.refresh_tokens('twitch', access, refresh, expiry[0] if expiry else 0)

                success = client.connect(target)

            elif platform == 'youtube':

                client = YouTubeChat(

                    on_message=lambda m: self._on_message('YouTube', m),

                    on_status=lambda s: self._on_status('youtube', s) if current() else None,

                    on_error=lambda e: self._on_error('youtube', e) if current() else None,

                    on_viewer_count=lambda p, c: self._on_viewer_count('youtube', c)

                )

                success = client.connect(target)

            elif platform == 'kick':

                client = KickChat(

                    oauth_token=(account or {}).get('access_token') or '', bot_username=(account or {}).get('username') or '',

                    on_message=lambda m: self._on_message('KICK', m) if current() else None,

                    on_status=lambda s: self._on_status('kick', s) if current() else None,

                    on_error=lambda e: self._on_error('kick', e) if current() else None,

                    on_viewer_count=lambda p, c: self._on_viewer_count('kick', c)

                )

                if account:

                    client._refresh_token = account.get('refresh_token') or ''

                    client._on_token_refreshed = lambda access, refresh, *expiry: self.accounts.refresh_tokens('kick', access, refresh, expiry[0] if expiry else 0)

                success = client.connect(target)

            elif platform == 'tiktok':

                client = TikTokChat(

                    on_message=lambda m: self._on_message('TikTok', m) if current() else None,

                    on_status=lambda s: self._on_status('tiktok', s) if current() else None,

                    on_error=lambda e: self._on_error('tiktok', e) if current() else None,

                    on_viewer_count=lambda p, c: self._on_viewer_count('tiktok', c)

                )

                success = client.connect(target)

            elif platform == 'soop':

                client = SoopChat(

                    on_message=lambda m: self._on_message('SOOP', m) if current() else None,

                    on_status=lambda s: self._on_status('soop', s) if current() else None,

                    on_error=lambda e: self._on_error('soop', e) if current() else None,

                    on_viewer_count=lambda p, c: self._on_viewer_count('soop', c)

                )

                success = client.connect(target)

            elif platform == 'mylive':

                client = MyLiveChat(

                    on_message=lambda m: self._on_message('MyLive', m) if current() else None,

                    on_status=lambda s: self._on_status('mylive', s) if current() else None,

                    on_error=lambda e: self._on_error('mylive', e) if current() else None,

                    on_viewer_count=lambda p, c: self._on_viewer_count('mylive', c)

                )

                success = client.connect(target)

            else:

                return {'success': False, 'error': f'ยังไม่รองรับแพลตฟอร์ม {platform}'}



            if success:

                with self._lock:

                    active = self._reconnect.get(platform)

                    cancelled = not active or active.get('attempt_token') is not attempt_token or (_reconnect_token is not None and active['token'] != _reconnect_token)

                    if not cancelled: self._clients[platform] = client

                    if not cancelled: self._statuses[platform]['target'] = target

                    connected = self._statuses[platform]['connected']

                if cancelled:

                    client.disconnect()

                    return {'success': False, 'error': 'ยกเลิกการเชื่อมต่อแล้ว'}

                def _fetch_title_bg(p, t):

                    try:

                        title = fetch_stream_title(p, t)

                        if title:

                            with self._lock:

                                if p in self._statuses:

                                    self._statuses[p]['title'] = title

                    except Exception:

                        pass

                threading.Thread(target=_fetch_title_bg, args=(platform, target), daemon=True).start()

                return {'success': True, 'platform': platform, 'target': target, 'connected': connected, 'channel_verified': verified}

            else:

                detail = self._statuses.get(platform, {}).get('status', '')

                return {'success': False, 'error': detail if detail and detail != 'กำลังเชื่อมต่อแชท' else f'เชื่อมต่อ {platform} ไม่สำเร็จ ตรวจสอบชื่อแชนแนลหรือสถานะ Live'}

        except Exception as e:

            return {'success': False, 'error': str(e)}



    def fetch_stream_title(self, platform: str, channel: str) -> str:

        return fetch_stream_title(platform, channel)



    def refresh_title(self, platform: str) -> str:

        with self._lock:

            target = self._statuses.get(platform, {}).get('target', '')

            client = self._clients.get(platform)

        if client and getattr(client, '_stream_title', ''):

            title = client._stream_title

            with self._lock:

                if platform in self._statuses:

                    self._statuses[platform]['title'] = title

            return title

        if not target:

            return ''

        title = fetch_stream_title(platform, target)

        if title:

            with self._lock:

                if platform in self._statuses:

                    self._statuses[platform]['title'] = title

        return title



    def apply_bot_account(self, platform, account):

        with self._lock:

            target = self._statuses.get(platform, {}).get('target', '')

            active = bool(self._clients.get(platform))

        if active and target:

            self.connect(platform, target)



    def disconnect(self, platform: str) -> dict:

        platform = platform.lower()

        with self._lock:

            client = self._clients.pop(platform, None)

            reconnect = self._reconnect.pop(platform, None)

            if reconnect and reconnect.get('timer'): reconnect['timer'].cancel()

            if platform in self._statuses:

                self._statuses[platform]['connected'] = False

                self._statuses[platform]['status'] = 'ยังไม่เชื่อมต่อ'



        if client and hasattr(client, 'disconnect'):

            try:

                client.disconnect()

            except Exception:

                pass

        self._publish_viewers()

        return {'success': True, 'platform': platform}



    def get_status(self) -> dict:

        with self._lock:

            return dict(self._statuses)



    def clear_messages(self):

        with self._lock:

            self._messages.clear()



    def get_messages(self, last_id: int = 0) -> list:

        with self._lock:

            if last_id == 0:

                return self._messages[-50:]

            return [m for m in self._messages if m['id'] > last_id]



# Global singleton

chat_bridge = ChatBridge()

