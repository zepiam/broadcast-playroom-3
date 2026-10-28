import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from bot_auth import BotAccounts
class FakeOAuth:
 def __init__(self,name):self.name=name
 def start_oauth_flow(self):return {'access_token':'fake-private-token','refresh_token':'fake-refresh','username':self.name,'expires_in':3600}
with tempfile.TemporaryDirectory(prefix='bot-auth-ui-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 accounts=BotAccounts(Path(folder)/'accounts.dat',modules={'twitch':FakeOAuth('twbot'),'kick':FakeOAuth('kickbot')});launch_dev.bot_accounts=accounts;launch_dev.chat_bridge.accounts=accounts
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as opened:page.locator('#btnRailSettings').click()
   settings=opened.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('platforms')")
   for platform,label,username in [('twitch','Twitch','twbot')]:
    settings.locator('#'+platform+'BotConnect').click();settings.locator('#'+platform+'BotDisconnect').wait_for(state='visible',timeout=10000)
    settings.locator('#'+platform+'BotBadge').filter(has_text='รอเชื่อมแชท').wait_for(timeout=10000)
   assert not settings.locator('#kickBotConnect').is_visible()
   assert 'fake-private-token' not in str(page.evaluate("fetch('/api/chatbot/auth/status').then(r=>r.json())"));print('PASS OAuth buttons, saved-account status and no token exposure')
   settings.locator('#twitchBotDisconnect').click();settings.locator('#twitchBotDisconnect').wait_for(state='hidden',timeout=6000);assert accounts.get('twitch') is None;print('PASS logout in settings');browser.close()
 finally:server.shutdown();server.server_close()

