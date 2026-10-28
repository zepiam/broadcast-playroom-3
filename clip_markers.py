"""OBS clip markers; never create a marker unless OBS reports active output."""
import os
import threading
from datetime import datetime
from pathlib import Path

class ClipMarkers:
    def __init__(self, folder):
        self.folder = Path(folder)
        self._connection = None
        self._lock = threading.Lock()
        self._stream_active = False
        self._session_header_written = False
        self._session_type = None
        self._last_seconds = None

    def configure(self, host, port, password):
        with self._lock:
            self._connection = (host, port, password) if host else None

    def update_stream(self, active):
        # Do not clear a session on network disconnect: only confirmed OBS state
        # transitions count as a stopped live stream.
        with self._lock:
            if bool(active) != self._stream_active:
                self._stream_active = bool(active)
                if active or self._session_type == 'OBS Live':
                    self._session_header_written = False
                    self._session_type = 'OBS Live' if active else None
                    self._last_seconds = None

    def mark(self):
        with self._lock:
            connection = self._connection
        if not connection:
            return {'ok': False, 'message': 'กรุณาทดสอบการเชื่อมต่อ OBS ในการตั้งค่าก่อน'}
        import obsws_python as obs
        client = None
        try:
            client = obs.ReqClient(host=connection[0], port=connection[1], password=connection[2], timeout=3)
            stream = client.get_stream_status()
            is_live = bool(getattr(stream, 'output_active', False))
            output = stream if is_live else client.get_record_status()
            if not getattr(output, 'output_active', False):
                return {'ok': False, 'message': 'ยังไม่ได้เริ่ม Live หรือบันทึกใน OBS จึงมาร์กคลิปไม่ได้'}
            code = str(getattr(output, 'output_timecode', '')).split('.')[0]
            if not code or any(c not in '0123456789:' for c in code):
                return {'ok': False, 'message': 'OBS ไม่ได้ส่งเวลาสตรีมหรือบันทึก จึงมาร์กคลิปไม่ได้'}
            parts=code.split(':')
            seconds=sum(int(value)*60**index for index,value in enumerate(reversed(parts)))
            source='OBS Live' if is_live else 'OBS Record'
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with self._lock:
                self.folder.mkdir(parents=True, exist_ok=True)
                if self._session_type!=source or (self._last_seconds is not None and seconds+5<self._last_seconds):
                    self._session_type=source;self._session_header_written=False
                with (self.folder / 'clip_markers.txt').open('a', encoding='utf-8') as f:
                    if not self._session_header_written:
                        f.write('\n'+'='*55+'\n'+f'🔴 Live Session: {now} ({source})\n'+'='*55+'\n')
                        self._session_header_written=True
                    f.write(f'[{code}] ({now}) โดย Streamer\n')
                self._last_seconds=seconds
            return {'ok': True, 'message': f'มาร์กคลิปที่ {code} แล้ว', 'timecode': code}
        except Exception:
            return {'ok': False, 'message': 'ติดต่อ OBS ไม่สำเร็จ กรุณาตรวจสอบการเชื่อมต่อ'}
        finally:
            if client is not None:
                try: client.base_client.ws.close()
                except Exception: pass

    def action(self, action):
        if action == 'mark': return self.mark()
        if action == 'clear':
            with self._lock:
                path = self.folder / 'clip_markers.txt'
                if path.exists(): path.write_text('', encoding='utf-8')
                self._session_header_written=False
            return {'ok': True, 'message': 'ล้างประวัติมาร์กคลิปแล้ว'}
        if action in ('open', 'folder'):
            self.folder.mkdir(parents=True, exist_ok=True)
            path = self.folder / 'clip_markers.txt'
            if action == 'open': path.touch(exist_ok=True)
            os.startfile(str(path if action == 'open' else self.folder))
            return {'ok': True, 'message': 'เปิดไฟล์มาร์กคลิปแล้ว' if action == 'open' else 'เปิดโฟลเดอร์มาร์กคลิปแล้ว'}
        raise ValueError('Invalid action')
