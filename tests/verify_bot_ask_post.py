import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context();sent=[]
   def fake_send(route):sent.append(route.request.post_data_json);route.fulfill(json={'results':{'twitch':{'ok':True}}})
   ctx.route('**/api/chatbot/send',fake_send);page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as opened:page.locator('#btnRailSettings').click()
   settings=opened.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('platforms')")
   assert not settings.locator('#cfgTwitchBotEnabled').is_checked() and not settings.locator('#cfgTwitchBotAskPost').is_checked()
   settings.locator('#cfgTwitchBotEnabled').check();settings.locator('#cfgTwitchBotAskPost').check();settings.evaluate("switchSettingsSection('chatbot')")
   assert settings.locator('#cfgMasterBotEnabled').is_checked() and settings.locator('#cfgBotPlatTwitch').is_checked() and settings.locator('#cfgBotAskPostGlobal').is_checked()
   page.evaluate("window._botAuthStatuses={twitch:{ready:true}};window._askPollState={phase:'voting',question:'ทดสอบ',choices:[{key:'A',text:'One',votes:2},{key:'B',text:'Two',votes:1}],voters:{a:'A',b:'A',c:'B'}};endAskPoll();endAskPoll()")
   page.wait_for_timeout(250);assert len(sent)==1 and sent[0]['targets']==['twitch'] and '3 คนโหวต' in sent[0]['message']
   page.evaluate("window._askPollState={phase:'voting',question:'empty',choices:[],voters:{}};endAskPoll()")
   page.wait_for_timeout(250);assert len(sent)==1
   settings.locator('#cfgBotAskPostGlobal').uncheck();assert not settings.locator('#cfgTwitchBotAskPost').is_checked()
   page.evaluate("window._askPollState={phase:'voting',question:'off',choices:[{key:'A',text:'x',votes:1}],voters:{a:'A'}};endAskPoll()")
   page.wait_for_timeout(250);assert len(sent)==1
   print('PASS Twitch bot toggles synced and ASK result opt-in, once, only with voters (fake sender)');browser.close()
 finally:server.shutdown();server.server_close()
