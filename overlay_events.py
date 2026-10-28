import json
import threading
import time
import uuid
import logging
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque


class OverlayEvents:
    """Process-local event relay shared by the desktop app and OBS browser."""
    allowed = {'ASK_UPDATE', 'GIVEAWAY_UPDATE', 'CHAT_MESSAGE', 'CHAT_CLEAR', 'CHAT_DELETE',
               'RANDOMIZER_SPIN', 'REPLIE_ACTION', 'REPLIE_DISMISS',
               'DESKTOP_CHAT_MESSAGE','DESKTOP_CHAT_CLEAR','DESKTOP_OVERLAY_STATE','DESKTOP_OVERLAY_SETTINGS', 'PLAYROOM_PLAY_CLIP', 'AVATAR_STATE', 'VIEWERS_UPDATE', 'DOCK_CONTROL', 'CANVAS_LAYOUT_SAVED'}

    def __init__(self):
        self.chat_log_path = None
        self._last_log_cleanup = 0
        self.lock = threading.Lock()
        self.epoch = uuid.uuid4().hex
        self.sequence = 0
        self.events = deque(maxlen=1000)
        self.seen = deque(maxlen=1000)
        self.states = {}
        self.chat = deque(maxlen=100)

    def prune_chat_log(self, now=None):
        """Remove only dated chat entries older than seven days; preserve unknown lines."""
        now = time.time() if now is None else now
        with self.lock:
            self._last_log_cleanup = now
            if not self.chat_log_path:
                return 0
            path = Path(self.chat_log_path())
            if not path.is_file():
                return 0
            cutoff = datetime.fromtimestamp(now) - timedelta(days=7)
            temporary = None
            removed = 0
            try:
                with path.open('r', encoding='utf-8', newline='') as source, tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=path.parent, prefix='.chat-retention-', suffix='.tmp', delete=False) as target:
                    temporary = target.name
                    for line in source:
                        try:
                            stamp = datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S') if line.startswith('[') and line[20:21] == ']' else None
                        except ValueError:
                            stamp = None
                        if stamp is not None and stamp < cutoff:
                            removed += 1
                        else:
                            target.write(line)
                if removed:
                    os.replace(temporary, path)
                    temporary = None
                return removed
            finally:
                if temporary:
                    try: os.unlink(temporary)
                    except OSError: pass

    def publish(self, item):
        event = item.get('event')
        if event == 'CHAT_MESSAGE' and time.time() - self._last_log_cleanup >= 3600:
            try: self.prune_chat_log()
            except (OSError, UnicodeError): logging.getLogger(__name__).exception('Unable to prune chat log')
        if event not in self.allowed:
            raise ValueError('Unsupported overlay event')
        with self.lock:
            payload = item.get('payload')
            if not isinstance(payload, dict):
                raise ValueError('Event payload must be an object')
            event_id = ('chat:' + str(payload['id'])) if event == 'CHAT_MESSAGE' and isinstance(payload.get('id'), int) else str(item.get('id') or uuid.uuid4().hex)
            if event_id in self.seen:
                return self.sequence
            self.seen.append(event_id)
            self.sequence += 1
            entry = {'seq': self.sequence, 'id': event_id, 'event': event,
                     'payload': item.get('payload'), 'client': item.get('client'),
                     'time': time.time()}
            self.events.append(entry)
            if event == 'AVATAR_STATE':
                self.states[event+':'+str(payload.get('widget_id') or '*')] = entry
            elif event in ('ASK_UPDATE', 'GIVEAWAY_UPDATE', 'VIEWERS_UPDATE', 'AVATAR_STATE'):
                self.states[event] = entry
            elif event == 'CHAT_MESSAGE':
                self.chat.append(entry)
                if self.chat_log_path:
                    try:
                        path=Path(self.chat_log_path())
                        def plain(value):
                            return str(value or '').replace('\r','\\r').replace('\n','\\n')
                        line=f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{plain(payload.get('platform'))}] {plain(payload.get('username'))}: {plain(payload.get('raw_text') or payload.get('text'))}\n"
                        with path.open('a',encoding='utf-8') as stream:stream.write(line)
                    except OSError:
                        logging.getLogger(__name__).exception('Unable to append chat log')
            elif event == 'CHAT_DELETE':
                target=str(payload.get('id',''))
                self.chat=deque([row for row in self.chat if str(row['payload'].get('id',row['id']))!=target],maxlen=100)
            elif event == 'CHAT_CLEAR':
                self.chat.clear()
            elif event == 'REPLIE_DISMISS':
                self.states.pop('REPLIE_ACTION', None)
            elif event in ('REPLIE_ACTION', 'PLAYROOM_PLAY_CLIP'):
                self.states[event] = entry
            return self.sequence

    def read(self, after=None, epoch=None):
        with self.lock:
            reset = after is None or epoch != self.epoch or after > self.sequence or (self.events and after < self.events[0]['seq'] - 1)
            if reset:
                now = time.time()
                events = list(self.chat)
                for event, entry in self.states.items():
                    if event in ('REPLIE_ACTION', 'PLAYROOM_PLAY_CLIP'):
                        duration = float((entry['payload'] or {}).get('duration') or 5)
                        if not (entry['payload'] or {}).get('isLoop') and now - entry['time'] >= duration:
                            continue
                        entry = dict(entry, payload=dict(entry['payload'], duration=duration - (now-entry['time'])))
                    events.append(entry)
                events.sort(key=lambda e: e['seq'])
            else:
                events = [entry for entry in self.events if entry['seq'] > after]
            return {'epoch': self.epoch, 'cursor': self.sequence, 'events': events, 'reset': reset}


overlay_events = OverlayEvents()
