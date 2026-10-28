import sys,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from chat_bridge import ChatBridge
from chat_twitch import ChatMessage
class FakeBot:
 def __init__(self):self.calls=[]
 def on_message(self,*args):self.calls.append(args)
bridge=ChatBridge.__new__(ChatBridge);bridge._lock=threading.Lock();bridge._messages=[];bridge._msg_id_counter=0;bridge._bot_blocked_names=set();bridge._bot_banned_words=();bridge.bot=FakeBot()
bridge.set_bot_blocklist([' FullUser ','NightBot'],['badword'])
bridge._on_message('twitch',ChatMessage(platform='twitch',author='FULLUSER',text='!test'))
bridge._on_message('twitch',ChatMessage(platform='twitch',author='NightBot',text='!test'))
bridge._on_message('twitch',ChatMessage(platform='twitch',author='Other',text='!test badword'))
bridge._on_message('twitch',ChatMessage(platform='twitch',author='Other',text='!test'))
assert len(bridge.bot.calls)==1 and bridge.bot.calls[0][1]=='Other'
assert len(bridge._messages)==4
bridge.set_bot_blocklist([]);bridge._on_message('twitch',ChatMessage(platform='twitch',author='FullUser',text='!test'));assert len(bridge.bot.calls)==2
print('PASS bot commands ignored for fully blocked users and default bot, unblock restores')
