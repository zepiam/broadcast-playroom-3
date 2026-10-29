"""Actual legacy Qt windows managed by the new HTTP application."""
import atexit,json,os,subprocess,sys,tempfile,threading,uuid
from pathlib import Path
class DesktopOverlays:
 def __init__(self,get_layout,save_layout,publish):
  self.get_layout=get_layout;self.save_layout=save_layout;self.publish=publish;self.instances={};self.hotkeys={};self.lock=threading.RLock();atexit.register(self.stop)
 def snapshot(self):
  with self.lock:return {'instances':[{**{key:value for key,value in item.items() if key in ('id','kind','index','hwnd','ready','editing','click_through','error')},'demo_running':bool(item.get('demo_stop'))} for item in self.instances.values() if item['process'].poll() is None]}
 def command(self,item,cmd,**values):
  item['process'].stdin.write(json.dumps({'cmd':cmd,**values})+'\n');item['process'].stdin.flush()
 def _read(self,item):
  for line in item['process'].stdout:
   try:msg=json.loads(line)
   except Exception:continue
   with self.lock:
    command=msg.get('cmd')
    if command=='ready':item['hwnd']=msg.get('hwnd');item['ready']=True
    elif command=='position':
     layout=self.get_layout();settings=layout.setdefault('legacyTools',{})
     if item['kind'] in ('game','viewer'):
      for key,new in [('x','x'),('y','y'),('w','width'),('h','height')]:
       if key in msg:settings[('viewer_overlay_' if item['kind']=='viewer' else 'game_overlay_')+new]=msg[key]
     elif item['kind']=='overlay+':
      entries=settings.setdefault('more_overlays',[])
      if item['index']<len(entries):entries[item['index']].update({key:msg[key] for key in ('x','y','w','h') if key in msg})
     self.save_layout(layout);self.publish({'event':'DESKTOP_OVERLAY_STATE','payload':settings})
    elif command=='edit_state':item['editing']=bool(msg.get('editing'));item['click_through']=bool(msg.get('click_through'))
    elif command=='exit_edit':item['editing']=False
    elif command=='quit':self._close(item)
    elif command in ('open_settings','clear_messages','clear_msgs','toggle_demo','stop_demo'):
     if command in ('clear_messages','clear_msgs'):self.publish({'event':'DESKTOP_CHAT_CLEAR','payload':{'kind':item['kind']}})
     elif command in ('toggle_demo','stop_demo'):
      if item.get('demo_stop'):item['demo_stop'].set();item['demo_stop']=None;self.command(item,'demo_state',running=False)
      elif command=='toggle_demo':
       item['demo_stop']=threading.Event();self.command(item,'demo_state',running=True);threading.Thread(target=self._demo,args=(item,item['demo_stop']),daemon=True).start()
     elif command=='open_settings':self._bring_app_to_front();self.publish({'event':'DESKTOP_OVERLAY_SETTINGS','payload':{'kind':item['kind']}})
  with self.lock:
   if item['id'] in self.instances and item['process'].poll() is not None:self._close(item)
 def _bring_app_to_front(self):
  try:
   import ctypes
   u=ctypes.windll.user32
   def _cb(h,_):
    if u.IsWindowVisible(h):
     l=u.GetWindowTextLengthW(h)
     if l>0:
      b=ctypes.create_unicode_buffer(l+1)
      u.GetWindowTextW(h,b,l+1)
      if 'Broadcast Playroom' in b.value:
       u.ShowWindow(h,9);u.SetForegroundWindow(h)
    return True
   CMP=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_int,ctypes.c_int)
   u.EnumWindows(CMP(_cb),0)
  except Exception:pass
 def _demo(self,item,stop):
  while not stop.is_set() and item['process'].poll() is None:
   self.publish({'event':'DESKTOP_CHAT_MESSAGE','payload':{'kind':item['kind'],'message':{'username':'ทดสอบ Overlay','author':'ทดสอบ Overlay','text':'ข้อความทดสอบ Game Overlay','platform':'Twitch'}}})
   settings=(self.get_layout() or {}).get('legacyTools') or {}
   try: interval=max(1,min(60,float(settings.get('game_overlay_demo_interval',5))))
   except (TypeError,ValueError): interval=5
   stop.wait(interval)
 def _ensure_hotkeys(self,kind,base):
  if kind not in ('game','overlay+'):return
  settings=(self.get_layout() or {}).get('legacyTools') or {}
  prefix='game_overlay' if kind=='game' else 'more_overlay'
  defaults=('ctrl+shift+g','ctrl+shift+h') if kind=='game' else ('ctrl+shift+m','ctrl+shift+n')
  try:
   from desktop_hotkeys import DesktopHotkey
   for action,suffix,default in [('toggle','',defaults[0]),('edit','_edit',defaults[1])]:
    key=(kind,action)
    if key not in self.hotkeys:
     binding=settings.get(prefix+'_hotkey'+suffix) or default
     self.hotkeys[key]=DesktopHotkey(binding,lambda action=action,kind=kind:self.act(action,kind,base))
  except Exception:pass
 def rebind_game_hotkey(self,action,chord,base):
  if action not in ('toggle','edit'):raise ValueError('Invalid hotkey action')
  from desktop_hotkeys import DesktopHotkey
  key=('game',action);previous=self.hotkeys.get(key)
  if previous and getattr(previous,'chord',None)==chord:return
  replacement=DesktopHotkey(chord,lambda:self.act(action,'game',base))
  self.hotkeys[key]=replacement
  if previous:previous.close()
 def _start(self,kind,index,url,config):
  ident='bp3-'+uuid.uuid4().hex;folder=tempfile.TemporaryDirectory(prefix=ident+'-');log=open(Path(folder.name)/'stderr.log','w',encoding='utf-8')
  args=([sys.executable,'--desktop-overlay'] if getattr(sys,'frozen',False) else [sys.executable,str(Path(__file__).with_name('desktop_overlay_qt.py'))])+['--id',ident,'--mode',kind,'--url',url]
  for key,default in [('x',-1),('y',-1),('w',360),('h',500),('alpha',.85)]:args+=['--'+key,str(float(config.get(key,default)) if key=='alpha' else int(float(config.get(key,default))))]
  process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,text=True,encoding='utf-8',cwd=folder.name,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  item={'id':ident,'kind':kind,'index':index,'process':process,'folder':folder,'log':log,'ready':False,'editing':True,'hwnd':None}
  self.instances[ident]=item;threading.Thread(target=self._read,args=(item,),daemon=True).start();return item
 def act(self,action,kind,base):
  if kind not in ('game','overlay+','viewer'):raise ValueError('Unknown overlay')
  with self.lock:
   running=[item for item in self.instances.values() if item['kind']==kind and item['process'].poll() is None]
   if action=='edit':
    if kind=='game':running += [item for item in self.instances.values() if item['kind']=='viewer' and item['process'].poll() is None]
    for item in running:item['editing']=not item['editing'];self.command(item,'edit_on' if item['editing'] else 'edit_off')
   elif action=='demo' and kind=='game':
    if not running:raise ValueError('กรุณาเปิด Game Overlay ก่อนเริ่ม Demo')
    for item in running:
     if item.get('demo_stop'):
      item['demo_stop'].set();item['demo_stop']=None;self.command(item,'demo_state',running=False)
     else:
      item['demo_stop']=threading.Event();self.command(item,'demo_state',running=True);threading.Thread(target=self._demo,args=(item,item['demo_stop']),daemon=True).start()
   elif action=='stop' or (action=='toggle' and running):
    for item in running:self._close(item)
   elif action=='toggle':
    self._ensure_hotkeys(kind,base)
    settings=(self.get_layout() or {}).get('legacyTools') or {}
    if kind=='game':
     config={key:settings.get('game_overlay_'+old,default) for key,old,default in [('x','x',-1),('y','y',-1),('w','width',360),('h','height',500),('alpha','alpha',.85)]}
     self._start(kind,0,base+'/legacy-game-chat.html',config)
    elif kind=='viewer':
     config={key:settings.get('viewer_overlay_'+old,default) for key,old,default in [('x','x',-1),('y','y',-1),('w','width',400),('h','height',80),('alpha','alpha',1)]}
     self._start(kind,0,base+'/viewer_overlay.html',config)
    else:
     entries=[(index,entry) for index,entry in enumerate(settings.get('more_overlays',[])[:3]) if entry.get('enabled',True) and entry.get('url')]
     if not entries:raise ValueError('กรุณาตั้งค่า URL ของ Overlay+ ก่อน')
     from urllib.parse import urlparse
     for index,entry in entries:
      if urlparse(entry['url']).scheme not in ('http','https'):raise ValueError('Overlay URL ต้องเป็น http หรือ https')
     for index,entry in entries:self._start(kind,index,entry['url'],entry)
   else:raise ValueError('Unknown action')
   return self.snapshot()
 def _close(self,item):
  if item.get('demo_stop'):item['demo_stop'].set()
  process=item['process']
  if process.poll() is None:
   try:self.command(item,'quit');process.wait(timeout=5)
   except Exception:process.terminate();process.wait(timeout=3)
  try:process.stdin.close();item['log'].close();item['folder'].cleanup()
  except Exception:pass
  self.instances.pop(item['id'],None)
 def stop(self):
  with self.lock:
   for item in list(self.instances.values()):self._close(item)
   if self.hotkeys:
    for handle in self.hotkeys.values():
     try:handle.close()
     except Exception:pass
    self.hotkeys.clear()
