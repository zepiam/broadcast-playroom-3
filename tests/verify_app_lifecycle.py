import sys,json,tempfile,threading,subprocess,socket,time,urllib.request,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from app_presence import AppPresence
out=Path(sys.argv[1]);results=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=root/'composer_layout.json';digest=hashlib.sha256(original.read_bytes()).hexdigest()
def free_port():
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));return sock.getsockname()[1]
def get(base,path):
 with urllib.request.urlopen(base+path,timeout=2) as response:return json.load(response)
def leave(base,name):
 request=urllib.request.Request(base+'/api/app-presence/leave',data=json.dumps({'client':name}).encode(),headers={'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(request,timeout=2) as response:return json.load(response)
worker='''import sys,threading,json
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,sys.argv[1]);import launch_dev
from http.server import ThreadingHTTPServer
# Isolate OS-wide hooks and OBS from lifecycle tests.
launch_dev.clip_hotkey.start=lambda:None;launch_dev.clip_hotkey.stop=lambda:None
launch_dev.obs_connection.start=lambda:None;launch_dev.obs_connection.stop=lambda:None
folder=Path(sys.argv[2]);launch_dev.__file__=str(folder/'launch_dev.py');launch_dev.PORT=int(sys.argv[3]);launch_dev.LAYOUT_FILE=str(folder/'profile.json');launch_dev._LAYOUT_CACHE=None
if not Path(launch_dev.LAYOUT_FILE).exists():launch_dev.save_layout({'pages':[{'id':'lifecycle','widgets':[]}],'activePageId':'lifecycle'})
launch_dev.desktop_overlays._ensure_hotkeys=lambda *args:None
launch_dev.open_app_window=lambda url:print('OPEN_APP '+url,flush=True)
def legacy(*args):
 servers=[]
 for _ in range(2):
  server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();servers.append(server)
 print('OWNED_PORTS '+json.dumps([server.server_port for server in servers]),flush=True);return servers,[]
launch_dev.start_legacy_servers=legacy
sys.exit(launch_dev.main() or 0)
'''
with tempfile.TemporaryDirectory(prefix='bp3-lifecycle-') as folder:
 folder=Path(folder);script=folder/'worker.py';script.write_text(worker,encoding='utf-8');port=free_port();base=f'http://127.0.0.1:{port}';processes=[]
 def start(name):
  log=(folder/(name+'.log')).open('w',encoding='utf-8');proc=subprocess.Popen([sys.executable,'-u',str(script),str(root),str(folder),str(port)],stdout=log,stderr=subprocess.STDOUT);processes.append((proc,log));return proc,folder/(name+'.log')
 def ready(proc):
  deadline=time.monotonic()+10
  while time.monotonic()<deadline:
   try:return get(base,'/api/app-instance')
   except OSError:
    if proc.poll() is not None:raise AssertionError('Worker exited before ready')
    time.sleep(.1)
  raise AssertionError('Worker startup timeout')
 try:
  first,log_path=start('first');identity=ready(first);check('Actual launcher starts server with stable app identity',identity['application']=='BroadcastPlayroom3')
  stream=urllib.request.urlopen(base+'/api/app-presence/stream?client=first',timeout=3);stream.readline();check('Main-window stream marks app active',get(base,'/api/app-presence')['active'])
  duplicate,duplicate_log=start('duplicate');duplicate.wait(timeout=8);text=duplicate_log.read_text(encoding='utf-8');check('Duplicate launch reopens verified same-project server without crash',duplicate.returncode==0 and 'already running' in text and 'OPEN_APP ' in text and first.poll() is None and 'Traceback' not in text)
  second_stream=urllib.request.urlopen(base+'/api/app-presence/stream?client=second',timeout=3);second_stream.readline();stream.close();leave(base,'first');check('Another main window keeps server running',get(base,'/api/app-presence')['active'] and first.poll() is None)
  second_stream.close();leave(base,'second');first.wait(timeout=12);check('Last main-window close gracefully exits backend',first.returncode==0)
  log=log_path.read_text(encoding='utf-8');owned=json.loads(next(line.removeprefix('OWNED_PORTS ') for line in log.splitlines() if line.startswith('OWNED_PORTS ')))
  def released(number):
   with socket.socket() as sock:sock.settimeout(.2);return sock.connect_ex(('127.0.0.1',number))!=0
  check('Main and owned legacy listener ports all released',all(released(number) for number in [port,*owned]))
  restart,restart_log=start('restart');ready(restart);check('Restart binds same port successfully',restart.poll() is None)
  last=urllib.request.urlopen(base+'/api/app-presence/stream?client=restart',timeout=3);last.readline();last.close();leave(base,'restart');restart.wait(timeout=12);check('Restarted instance also closes cleanly',restart.returncode==0)
  class OtherHandler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    body=b'{"application":"OtherService"}';self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  other=ThreadingHTTPServer(('127.0.0.1',port),OtherHandler);threading.Thread(target=other.serve_forever,daemon=True).start()
  try:
   blocked,blocked_log=start('unrelated');blocked.wait(timeout=8);text=blocked_log.read_text(encoding='utf-8');check('Unrelated service is neither reused nor killed; friendly port error',blocked.returncode==1 and 'OPEN_APP ' not in text and 'Traceback' not in text and get(base,'/')['application']=='OtherService')
  finally:other.shutdown();other.server_close()
  presence=AppPresence();token=presence.open('closing');presence.close(token);check('Closing state rejects a late reopen race',presence.should_exit(grace=0) and not presence.reserve_launch() and presence.open('late') is None)
 finally:
  for proc,log in processes:
   if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
   log.close()
  check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'app-lifecycle.json').write_text(json.dumps({'results':results},ensure_ascii=False,indent=2),encoding='utf-8')
