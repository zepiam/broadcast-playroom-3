"""Thread-safe snapshots from the legacy Windows media watcher."""
import threading
from pathlib import Path
from now_playing import NowPlayingWatcher, CACHE_DIR

class NowPlayingService:
    def __init__(self, factory=NowPlayingWatcher):
        self.factory = factory
        self.lock = threading.RLock()
        self.watchers = {}
        self.states = {}

    def snapshot(self, source='auto'):
        source = source if source in ('auto', 'spotify', 'ytmusic', 'browser', 'desktop_player', 'any') else 'auto'
        with self.lock:
            if source not in self.watchers:
                self.states[source] = dict(title='', artist='', album='', thumbnail='', position=0, duration=0, is_playing=False)
                watcher = self.factory(on_change=lambda *args: self.change(source, *args), on_position=lambda *args: self.position(source, *args))
                watcher.set_source_filter(source)
                self.watchers[source] = watcher
                watcher.start()
            return dict(self.states[source])

    def change(self, source, title, artist, album, thumbnail, position, duration, is_playing):
        with self.lock:
            self.states[source] = dict(title=title, artist=artist, album=album, thumbnail=thumbnail, position=position, duration=duration, is_playing=is_playing)

    def position(self, source, position, duration, is_playing):
        with self.lock:
            self.states[source].update(position=position, duration=duration, is_playing=is_playing)

    def thumbnail(self, source):
        with self.lock:
            value = self.states.get(source, {}).get('thumbnail')
        if not value:
            return None
        target = Path(value).resolve()
        root = Path(CACHE_DIR).resolve()
        return target if root in target.parents and target.is_file() else None

    def stop(self):
        with self.lock:
            for watcher in self.watchers.values():
                watcher.stop()

now_playing_service = NowPlayingService()
