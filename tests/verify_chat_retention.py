import sys,tempfile,time
from datetime import datetime,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from overlay_events import OverlayEvents
now=time.time();base=datetime.fromtimestamp(now);stamp=lambda dt:dt.strftime('%Y-%m-%d %H:%M:%S')
with tempfile.TemporaryDirectory(prefix='chat-retention-') as folder:
 path=Path(folder)/'log.txt';old='['+stamp(base-timedelta(days=8))+'] [Twitch] Old: test\n';recent='['+stamp(base-timedelta(days=6))+'] [Kick] New: สวัสดี\n';unknown='unknown historical format\n';path.write_text(old+recent+unknown,encoding='utf-8')
 e=OverlayEvents();e.chat_log_path=lambda:path;assert e.prune_chat_log(now)==1
 assert path.read_text(encoding='utf-8')==recent+unknown
 e.publish({'event':'CHAT_MESSAGE','payload':{'platform':'Kick','username':'Tester','text':'fresh'}})
 result=path.read_text(encoding='utf-8');assert recent in result and 'Tester: fresh' in result and old not in result
 assert e.prune_chat_log(now)==0
 print('PASS old dated entries removed, recent/unknown preserved, new appended')
