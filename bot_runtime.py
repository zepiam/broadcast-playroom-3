"""Chat bot command and timer engine; sends only via an authorized, connected client."""
import threading
import time
from collections import deque

class BotRuntime:
    def __init__(self, client_lookup, clock=time.monotonic):
        self.client_lookup = client_lookup
        self.clock = clock
        self.lock = threading.RLock()
        self.config = {'enabled': False, 'platforms': [], 'commands': [], 'timers': []}
        self.cooldowns = {}
        self.sent = deque()
        self.activity = {}
        self.next_due = {}
        self.stop_event = threading.Event()
        self.worker = None

    def configure(self, config):
        commands=[]
        for item in config.get('commands', []):
            name=str(item.get('command','')).strip().lower();reply=str(item.get('response','')).strip()
            if name.startswith('!') and ' ' not in name and reply:
                commands.append({'command':name,'response':reply,'cooldown':max(1,min(86400,int(item.get('cooldown') or 5)))})
        timers=[]
        for item in config.get('timers', []):
            text=str(item.get('text','')).strip();identifier=str(item.get('id',''))
            if text and identifier:timers.append({'id':identifier,'text':text,'minutes':max(1,min(1440,int(item.get('minutes') or 1))),'minChat':max(0,min(100000,int(item.get('minChat') or 0)))})
        with self.lock:
            self.config={'enabled':bool(config.get('enabled')), 'platforms':[p for p in config.get('platforms',[]) if p in ('twitch','kick')], 'commands':commands,'timers':timers}
            self.next_due={}
            now=self.clock()
            for platform in self.config['platforms']:
                for timer in timers:self.next_due[(platform,timer['id'])]=now+timer['minutes']*60

    def _send(self, platform, text):
        with self.lock:
            if not self.config['enabled'] or platform not in self.config['platforms']:return False
            now=self.clock()
            while self.sent and now-self.sent[0]>=30:self.sent.popleft()
            if len(self.sent)>=18:return False
            client=self.client_lookup(platform)
            if not client or not getattr(client,'can_send',False) or not getattr(client,'is_connected',False):return False
            self.sent.append(now)
        try:return bool(client.send_message(text))
        except Exception:return False

    def on_message(self, platform, author, text):
        platform=platform.lower();text=str(text or '').strip();now=self.clock()
        client=self.client_lookup(platform)
        if client and str(getattr(client,'bot_username',None) or getattr(client,'_bot_username','') or '').lower()==str(author or '').lower():return
        with self.lock:
            if not self.config['enabled'] or platform not in self.config['platforms']:return
            self.activity[platform]=self.activity.get(platform,0)+1
            command=text.split()[0].lower() if text else ''
            item=next((x for x in self.config['commands'] if x['command']==command),None)
            if not item:return
            key=(platform,command)
            if now-self.cooldowns.get(key,float('-inf'))<item['cooldown']:return
            self.cooldowns[key]=now
        self._send(platform,item['response'])

    def tick(self):
        sends=[];now=self.clock()
        with self.lock:
            if not self.config['enabled']:return
            for platform in self.config['platforms']:
                for timer in self.config['timers']:
                    key=(platform,timer['id']);due=self.next_due.setdefault(key,now+timer['minutes']*60)
                    if now>=due and self.activity.get(platform,0)>=timer['minChat']:
                        self.next_due[key]=now+timer['minutes']*60;self.activity[platform]=0;sends.append((platform,timer['text']))
        for platform,text in sends:self._send(platform,text)

    def start(self):
        if self.worker and self.worker.is_alive():return
        self.stop_event.clear()
        def run():
            while not self.stop_event.wait(5):self.tick()
        self.worker=threading.Thread(target=run,name='ChatBotTimers',daemon=True);self.worker.start()

    def stop(self):
        self.stop_event.set()
