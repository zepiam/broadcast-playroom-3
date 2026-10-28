import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from bot_runtime import BotRuntime
class Client:
 can_send=True;is_connected=True;_bot_username='bot'
 def __init__(self):self.sent=[]
 def send_message(self,text):self.sent.append(text);return True
clock=[100.0];client=Client();runtime=BotRuntime(lambda platform:client,clock=lambda:clock[0]);settings={'enabled':True,'platforms':['twitch'],'commands':[{'command':'!hello','response':'response','cooldown':5}],'timers':[{'id':'timer','text':'timer response','minutes':1,'minChat':2}]};runtime.configure(settings)
runtime.on_message('twitch','user','!hello');runtime.on_message('twitch','user','!hello');assert client.sent==['response'];runtime.on_message('twitch','bot','!hello');assert client.sent==['response'];clock[0]+=61;runtime.tick();assert client.sent==['response','timer response'];client.can_send=False;clock[0]+=6;runtime.on_message('twitch','user','!hello');assert len(client.sent)==2;runtime.configure({**settings,'enabled':False});client.can_send=True;runtime.on_message('twitch','user','!hello');assert len(client.sent)==2
print('PASS fake bot command, cooldown, own echo, timer, auth guard and disabled state')
