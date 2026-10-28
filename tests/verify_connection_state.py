import sys
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.dont_write_bytecode=True
from chat_bridge import ChatBridge
class Fake:
 def __init__(self, **kwargs): self.callbacks=kwargs
 def connect(self, target): return True
 def disconnect(self): pass
b=ChatBridge()
with patch('chat_bridge.verify_twitch_channel',return_value=False):
 assert b.connect('twitch','missing')['success'] is False
with patch('chat_bridge.verify_twitch_channel',return_value=True),patch('chat_bridge.TwitchChat',Fake):
 result=b.connect('twitch','valid');assert result['success'] and not result['connected'] and result['channel_verified']
 b._clients['twitch'].callbacks['on_status']('✅ เชื่อมต่อ Twitch #valid');assert b.get_status()['twitch']['connected']
 b._clients['twitch'].callbacks['on_error']('การเชื่อมต่อ Twitch หลุด');assert not b.get_status()['twitch']['connected']
with patch('chat_bridge.YouTubeChat',Fake):
 result=b.connect('youtube','@name');assert result['success'] and not result['connected']
 b._clients['youtube'].callbacks['on_status']('⏳ YouTube: กำลังรอสตรีมถัดไป');assert not b.get_status()['youtube']['connected']
 b._clients['youtube'].callbacks['on_error']('ไม่พบ live chat');assert not b.get_status()['youtube']['connected'] and 'ไม่พบ' in b.get_status()['youtube']['status']
print('PASS: channel missing, pending, confirmed, disconnected and offline states')

import time
class RetryFake:
 calls = 0
 instances = []
 def __init__(self, **kwargs): self.callbacks=kwargs; self.__class__.instances.append(self)
 def connect(self, target):
  self.__class__.calls += 1
  self.callbacks['on_status']('✅ เชื่อมต่อ Twitch #valid')
  return True
 def disconnect(self): pass
b=ChatBridge();b._reconnect_interval=.05
with patch('chat_bridge.verify_twitch_channel',return_value=True),patch('chat_bridge.TwitchChat',RetryFake):
 assert b.connect('twitch','valid')['success']
 RetryFake.instances[-1].callbacks['on_error']('การเชื่อมต่อ Twitch หลุด')
 time.sleep(.3)
 assert RetryFake.calls == 2 and b.get_status()['twitch']['connected']
 RetryFake.instances[-1].callbacks['on_error']('การเชื่อมต่อ Twitch หลุด')
 b.disconnect('twitch');time.sleep(.2)
 assert RetryFake.calls == 2 and not b.get_status()['twitch']['connected']
print('PASS: reconnect after drop and manual disconnect cancels retry')

class FailRetry(RetryFake):
 calls=0
 instances=[]
 def connect(self,target):
  self.__class__.calls+=1
  if self.__class__.calls==1:
   self.callbacks['on_status']('✅ เชื่อมต่อ Twitch #valid');return True
  self.callbacks['on_error']('เชื่อมต่อไม่ได้');return False
b=ChatBridge();b._reconnect_interval=.03
with patch('chat_bridge.verify_twitch_channel',return_value=True),patch('chat_bridge.TwitchChat',FailRetry):
 assert b.connect('twitch','valid')['success']
 FailRetry.instances[-1].callbacks['on_error']('การเชื่อมต่อ Twitch หลุด')
 time.sleep(.5)
 assert FailRetry.calls == 6, FailRetry.calls
 assert '5 ครั้ง' in b.get_status()['twitch']['status']
print('PASS: stops after five reconnect attempts')

class SilentRetry(RetryFake):
 calls=0
 instances=[]
 def connect(self,target):
  self.__class__.calls+=1
  if self.__class__.calls==1:self.callbacks['on_status']('✅ เชื่อมต่อ Twitch #valid')
  return True
b=ChatBridge();b._reconnect_interval=.02;b._reconnect_timeout=.04
with patch('chat_bridge.verify_twitch_channel',return_value=True),patch('chat_bridge.TwitchChat',SilentRetry):
 b.connect('twitch','valid');old=SilentRetry.instances[-1];old.callbacks['on_error']('การเชื่อมต่อ Twitch หลุด');time.sleep(.18)
 assert SilentRetry.calls>=3
 b.disconnect('twitch');old.callbacks['on_status']('✅ เชื่อมต่อ Twitch #valid');time.sleep(.08)
 assert not b.get_status()['twitch']['connected']
print('PASS: stalled retries time out and stale callbacks are ignored')
