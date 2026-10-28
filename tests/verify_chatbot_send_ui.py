import os,sys,tempfile,threading,requests
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
class Client:
 is_connected=True
 can_send=True
 def __init__(self,ok=True):self.messages=[];self.ok=ok
 def send_message(self,msg):self.messages.append(msg);return self.ok
class Accounts:
 def public(self):return {'twitch':{'state':'saved','username':'testbot'},'kick':{'state':'saved','username':'kickbot'}}
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 launch_dev.bot_accounts=Accounts();tw=Client();kick=Client(False);launch_dev.chat_bridge._clients={'twitch':tw,'kick':kick}
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  base=f'http://127.0.0.1:{server.server_port}'
  assert requests.post(base+'/api/chatbot/send',headers={'Origin':'https://example.com'},json={'message':'blocked','targets':['twitch']}).status_code==403
  assert requests.post(base+'/api/chatbot/send',json={'message':'bad\nmessage','targets':['twitch']}).status_code==400
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.wait_for_function("window._botAuthStatuses?.twitch?.ready")
   assert page.locator('#chipSendTwitch').count()==0 and page.locator('#chipSendKick').count()==0
   page.locator('#txtChatInput').fill('hello test');page.locator('#btnChatSend').click();page.wait_for_function("document.getElementById('btnChatSend').disabled === false")
   assert tw.messages==['hello test'] and kick.messages==[]
   page.locator('#txtChatInput').fill('second');page.locator('#btnChatSend').click();page.wait_for_function("document.getElementById('btnChatSend').disabled === false")
   assert tw.messages==['hello test','second'] and kick.messages==[]
   with page.expect_popup() as opened:page.locator('#btnRailSettings').click()
   settings=opened.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('platforms')")
   assert settings.locator('#sec-chatbot #botAuthTwitchName').count()==0
   browser.close();print('PASS Twitch sending and hidden KICK with fake accounts; no external messages')
 finally:server.shutdown();server.server_close()

