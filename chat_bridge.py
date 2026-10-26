import sys
import os
import time
import threading
import json
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_twitch import TwitchChat, ChatMessage
from chat_youtube import YouTubeChat
from chat_kick import KickChat
from chat_tiktok import TikTokChat
from chat_soop import SoopChat

logger = logging.getLogger("chat_bridge")

class ChatBridge:
    def __init__(self):
        self._lock = threading.Lock()
        self._clients = {}
        self._statuses = {
            'twitch': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': ''},
            'youtube': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': ''},
            'kick': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': ''},
            'tiktok': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': ''},
            'soop': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': ''},
            'mylive': {'connected': False, 'viewers': 0, 'status': 'ยังไม่เชื่อมต่อ', 'target': ''},
        }
        self._messages = []
        self._msg_id_counter = 0

    def _on_message(self, platform_name: str, msg: ChatMessage):
        with self._lock:
            self._msg_id_counter += 1
            author = getattr(msg, 'author', '') or getattr(msg, 'username', 'ผู้ชม')
            text = getattr(msg, 'text', '')
            avatar = getattr(msg, 'avatar_url', '') or f"https://api.dicebear.com/7.x/bottts/svg?seed={author}"
            payload = {
                'id': self._msg_id_counter,
                'platform': platform_name.capitalize(),
                'platform_key': platform_name.lower(),
                'username': author,
                'text': text,
                'avatar': avatar,
                'color': getattr(msg, 'color', '#38bdf8'),
                'isVip': getattr(msg, 'is_vip', False) or getattr(msg, 'is_mod', False),
                'badges': getattr(msg, 'badges', []),
                'time': time.strftime('%H:%M', time.localtime())
            }
            self._messages.append(payload)
            if len(self._messages) > 1000:
                self._messages = self._messages[-1000:]
            print(f"[{platform_name}] {author}: {text}", flush=True)

    def _on_status(self, platform_name: str, status_text: str):
        with self._lock:
            if platform_name in self._statuses:
                self._statuses[platform_name]['status'] = status_text
                if 'connected' in status_text.lower() or 'เชื่อมต่อแล้ว' in status_text:
                    self._statuses[platform_name]['connected'] = True
                elif 'disconnected' in status_text.lower() or 'ตัดการเชื่อมต่อ' in status_text or 'หยุด' in status_text:
                    self._statuses[platform_name]['connected'] = False

    def _on_viewer_count(self, platform_name: str, count: int):
        with self._lock:
            if platform_name in self._statuses:
                self._statuses[platform_name]['viewers'] = count

    def connect(self, platform: str, target: str) -> dict:
        platform = platform.lower()
        target = target.strip()
        if not target:
            return {'success': False, 'error': f'กรุณาระบุชื่อแชนแนลหรือ URL สำหรับ {platform}'}

        self.disconnect(platform)

        try:
            client = None
            if platform == 'twitch':
                client = TwitchChat(
                    on_message=lambda m: self._on_message('Twitch', m),
                    on_status=lambda s: self._on_status('twitch', s),
                    on_viewer_count=lambda p, c: self._on_viewer_count('twitch', c)
                )
                success = client.connect(target)
            elif platform == 'youtube':
                client = YouTubeChat(
                    on_message=lambda m: self._on_message('YouTube', m),
                    on_status=lambda s: self._on_status('youtube', s),
                    on_viewer_count=lambda p, c: self._on_viewer_count('youtube', c)
                )
                success = client.connect(target)
            elif platform == 'kick':
                client = KickChat(
                    on_message=lambda m: self._on_message('KICK', m),
                    on_status=lambda s: self._on_status('kick', s),
                    on_viewer_count=lambda p, c: self._on_viewer_count('kick', c)
                )
                success = client.connect(target)
            elif platform == 'tiktok':
                client = TikTokChat(
                    on_message=lambda m: self._on_message('TikTok', m),
                    on_status=lambda s: self._on_status('tiktok', s),
                    on_viewer_count=lambda p, c: self._on_viewer_count('tiktok', c)
                )
                success = client.connect(target)
            elif platform == 'soop':
                client = SoopChat(
                    on_message=lambda m: self._on_message('SOOP', m),
                    on_status=lambda s: self._on_status('soop', s),
                    on_viewer_count=lambda p, c: self._on_viewer_count('soop', c)
                )
                success = client.connect(target)
            else:
                return {'success': False, 'error': f'ยังไม่รองรับแพลตฟอร์ม {platform}'}

            if success:
                with self._lock:
                    self._clients[platform] = client
                    self._statuses[platform]['connected'] = True
                    self._statuses[platform]['target'] = target
                    self._statuses[platform]['status'] = 'เชื่อมต่อแล้ว'
                return {'success': True, 'platform': platform, 'target': target}
            else:
                return {'success': False, 'error': f'เชื่อมต่อ {platform} ไม่สำเร็จ ตรวจสอบชื่อแชนแนลหรือสถานะ Live'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def disconnect(self, platform: str) -> dict:
        platform = platform.lower()
        with self._lock:
            client = self._clients.pop(platform, None)
            if platform in self._statuses:
                self._statuses[platform]['connected'] = False
                self._statuses[platform]['status'] = 'ยังไม่เชื่อมต่อ'

        if client and hasattr(client, 'disconnect'):
            try:
                client.disconnect()
            except Exception:
                pass
        return {'success': True, 'platform': platform}

    def get_status(self) -> dict:
        with self._lock:
            return dict(self._statuses)

    def get_messages(self, last_id: int = 0) -> list:
        with self._lock:
            if last_id == 0:
                return self._messages[-50:]
            return [m for m in self._messages if m['id'] > last_id]

# Global singleton
chat_bridge = ChatBridge()
