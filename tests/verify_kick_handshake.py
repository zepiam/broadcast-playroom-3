import json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
import chat_kick
class Socket:
 def __init__(self,frames):self.frames=list(frames)
 def settimeout(self,value):pass
 def connect(self,url):pass
 def send(self,value):pass
 def recv(self):return json.dumps(self.frames.pop(0))
 def close(self):pass
for frames in [[{'event':'pusher:error','data':{'code':4001}}],[{'event':'pusher:connection_established'},{'event':'pusher:subscription_error','data':'denied'}]]:
 errors=[];statuses=[];c=chat_kick.KickChat(on_message=lambda message:None,on_error=errors.append,on_status=statuses.append);c._chatroom_id=1;c._slug='fixture'
 with patch.object(chat_kick,'_realtime_pusher_url',return_value='wss://fixture'),patch.object(chat_kick.websocket,'WebSocket',return_value=Socket(frames)):c._ws_loop()
 assert errors and not c.is_connected and not any('✅' in s for s in statuses)
print('PASS: rejected socket and rejected subscription do not show connected')
