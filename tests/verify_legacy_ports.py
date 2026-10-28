import sys,json,threading,urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
import launch_dev
from legacy_compat import start_servers
servers=[];results=[]
try:
 main=launch_dev.start_server();threading.Thread(target=main.serve_forever,daemon=True).start();servers.append(main)
 aliases,statuses=start_servers(launch_dev.QuietHandler,launch_dev.PORT);servers.extend(aliases)
 assert len(aliases)==4,statuses
 for port,path,view in [(8801,'/?p=1','composer'),(8080,'/composer.html?p=1','composer'),(8765,'/','chat'),(8765,'/giveaway','giveaway'),(8766,'/','playroom'),(8790,'/','viewer')]:
  with urllib.request.urlopen(f'http://localhost:{port}{path}',timeout=5) as response:
   html=response.read().decode();assert response.status==200 and 'window.BP3LegacyView='+json.dumps(view) in html
  results.append({'url':f'http://localhost:{port}{path}','view':view,'status':'PASS'})
 with urllib.request.urlopen('http://localhost:8801/dock',timeout=5) as response:assert b'btnDockTts' in response.read()
 results.append({'url':'http://localhost:8801/dock','status':'PASS'})
finally:
 for server in servers:server.shutdown();server.server_close()
out=Path(sys.argv[1]) if len(sys.argv)>1 else root/'work'/'compat-audit'
out.mkdir(parents=True,exist_ok=True)
(out/'legacy-ports.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
