import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
import chat_soop
for value,expected in [('@testuser',('testuser','')),('https://ch.sooplive.co.kr/testuser/vods/clip',('testuser','')),('bj.afreecatv.com/testuser',('testuser','')),('https://play.sooplive.co.kr/testuser/12345?foo=1',('testuser','12345')),('play.sooplive.com/testuser',('testuser','')),('https://www.sooplive.com/station/testuser',('testuser','')),('https://play.afreecatv.com/testuser/12345',('testuser','12345'))]:
 assert chat_soop.parse_soop_target(value)==expected
for value in ['https://fake-skoop.example/testuser','https://play.sooplive.com.evil.example/testuser','https://play.sooplive.com/testuser/notnumber','test user']:
 try:chat_soop.parse_soop_target(value);raise AssertionError('invalid URL accepted')
 except ValueError:pass
captured=[];original=chat_soop._resolve_channel
chat_soop._resolve_channel=lambda bid,bno='':(captured.append((bid,bno)) or {'chatno':'1','chdomain':'localhost','chpt':'443','title':''})
try:
 client=chat_soop.SoopChat(lambda m:None);client._ws_loop=lambda:None
 assert client.connect('https://play.sooplive.co.kr/testuser/12345')
 assert captured==[('testuser','12345')]
finally:chat_soop._resolve_channel=original
print('PASS SOOP usernames and official live/station URLs including broadcast number; reject invalid domains')
