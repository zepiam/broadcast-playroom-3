import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import chat_soop

class FakeSocket:
    def __init__(self): self.closed = False
    def settimeout(self, value): pass
    def connect(self, *args, **kwargs): pass
    def send(self, packet): pass
    def recv(self): return ''
    def close(self): self.closed = True

errors, statuses = [], []
client = chat_soop.SoopChat(lambda msg: None, statuses.append, errors.append)
client._bid, client._chatno, client._chdomain, client._chpt = 'test', '1', 'localhost', '1'
socket = FakeSocket()
with patch.object(chat_soop.websocket, 'WebSocket', return_value=socket):
    client._ws_loop()
assert any('ปิดลง' in error for error in errors), errors
assert statuses and not client.is_connected and socket.closed and client._ws is None
print('PASS SOOP closed socket reports disconnect and closes resources')
