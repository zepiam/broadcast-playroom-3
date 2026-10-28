import sys,tempfile,time,threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from bot_auth import BotAccounts
from chat_bridge import ChatBridge
class OAuth:
 def start_oauth_flow(self):return {'access_token':'fixture-access','refresh_token':'fixture-refresh','username':'fixture-bot','expires_in':3600}
 def refresh_access_token(self,refresh):return {'access_token':'refreshed-access','refresh_token':'refreshed-refresh','expires_in':3600}
class Client:
 instances=[]
 def __init__(self,on_message,on_status,on_error,**kw):self.on_message=on_message;self.on_status=on_status;self.credentials=kw;self.is_connected=False;self.can_send=bool(kw.get('oauth_token'));self._bot_username=kw.get('bot_username','');self.sent=[];Client.instances.append(self)
 def connect(self,target):self.is_connected=True;self.on_status('✅ เชื่อมต่อ Twitch #fixture');return True
 def disconnect(self):self.is_connected=False
 def send_message(self,text):self.sent.append(text);return True
with tempfile.TemporaryDirectory(prefix='oauth-test-') as folder:
 path=Path(folder)/'accounts.dat';bridge=ChatBridge();accounts=BotAccounts(path,apply_account=bridge.apply_bot_account,modules={'twitch':OAuth()});bridge.accounts=accounts
 with patch('chat_bridge.verify_twitch_channel',return_value=True),patch('chat_bridge.TwitchChat',Client):
  assert bridge.connect('twitch','fixture')['success'];assert not Client.instances[-1].can_send
  accounts.start('twitch');deadline=time.time()+5
  while time.time()<deadline and not (accounts.public()['twitch']['state']=='saved' and Client.instances[-1].can_send):time.sleep(.02)
  client=Client.instances[-1];assert client.can_send and accounts.public()['twitch']['username']=='fixture-bot'
  assert b'fixture-access' not in path.read_bytes() and 'fixture-access' not in str(accounts.public())
  bridge.bot.configure({'enabled':True,'platforms':['twitch'],'commands':[{'command':'!hi','response':'fixture reply','cooldown':5}],'timers':[]})
  client.on_message(SimpleNamespace(author='viewer',text='!hi',extra={}));assert client.sent==['fixture reply']
  restored=BotAccounts(path,modules={'twitch':OAuth()});assert restored.get('twitch')['username']=='fixture-bot'
  restored.accounts['twitch']['expires_at']=time.time()-1;refreshed=restored.get('twitch');assert refreshed['access_token']=='refreshed-access' and refreshed['refresh_token']=='refreshed-refresh';assert b'refreshed-access' not in path.read_bytes()
  accounts.disconnect('twitch');assert not Client.instances[-1].can_send and accounts.get('twitch') is None
  bridge.disconnect('twitch');bridge.bot.stop()
print('PASS mock OAuth login, encrypted persistence, token refresh, connected bot response, reload and logout')

class DelayedOAuth:
 def __init__(self):self.wait=threading.Event()
 def start_oauth_flow(self):self.wait.wait(2);return {'access_token':'fake','username':'late-user'}
with tempfile.TemporaryDirectory(prefix='oauth-cancel-') as folder:
 provider=DelayedOAuth();a=BotAccounts(Path(folder)/'accounts.dat',modules={'kick':provider});a.start('kick');a.disconnect('kick');provider.wait.set();time.sleep(.2);assert a.get('kick') is None and a.public()['kick']['state']=='disconnected'
print('PASS logout while OAuth is pending ignores late callback')

with tempfile.TemporaryDirectory(prefix='kick-oauth-test-') as folder:
 bridge=ChatBridge();accounts=BotAccounts(Path(folder)/'accounts.dat',apply_account=bridge.apply_bot_account,modules={'kick':OAuth()});bridge.accounts=accounts
 with patch('chat_bridge.KickChat',Client):
  assert bridge.connect('kick','fixture')['success'];accounts.start('kick');deadline=time.time()+5
  while time.time()<deadline and not (accounts.public()['kick']['state']=='saved' and Client.instances[-1].can_send):time.sleep(.02)
  client=Client.instances[-1];assert client.can_send
  bridge.bot.configure({'enabled':True,'platforms':['kick'],'commands':[{'command':'!hi','response':'kick reply','cooldown':5}],'timers':[]})
  client.on_message(SimpleNamespace(author='viewer',text='!hi',extra={}));assert client.sent==['kick reply']
  accounts.disconnect('kick');bridge.disconnect('kick');bridge.bot.stop()
print('PASS mock Kick OAuth binds chat client and replies through fake sender')
