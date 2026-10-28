import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
class Client:
 is_connected=True;can_send=True
 def __init__(self):self.messages=[]
 def send_message(self,msg):self.messages.append(msg);return True
class Accounts:
 def __init__(self):self.connected=False
 def public(self):return {'twitch':({'state':'saved','username':'streamer'} if self.connected else {'state':'disconnected'}),'kick':{'state':'saved','username':'kickbot'}}
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 accounts=Accounts();launch_dev.bot_accounts=accounts;tw=Client();launch_dev.chat_bridge._clients={'kick':Client()}
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context();ctx.add_init_script("localStorage.setItem('bp3_tts_random_gender','false');localStorage.setItem('bp3_voice_gender','male');window.__audio=[];window.Audio=class extends EventTarget {constructor(url){super();this.url=url;window.__audio.push(url)} play(){setTimeout(()=>{this.dispatchEvent(new Event('playing'));this.onended?.()},40);return Promise.resolve()} pause(){}};")
   page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.wait_for_function("window._botAuthStatuses?.twitch?.state==='disconnected'");assert not page.locator('#txtChatInput').is_visible() and page.locator('#chatInputUnavailable').is_visible();accounts.connected=True;launch_dev.chat_bridge._clients['twitch']=tw;page.evaluate('window.refreshBotAuthStatus()');page.wait_for_function("window._botAuthStatuses?.twitch?.ready")
   assert page.locator('#chipSendTwitch').count()==0 and page.locator('#chipSendKick').count()==0
   for key in ('twitch','kick','youtube','soop','mylive','tiktok'):launch_dev.chat_bridge._statuses[key].update(connected=True,target='test')
   page.evaluate('pollPlatformStatuses()');page.wait_for_function("['twitch','kick','youtube','soop','mylive','tiktok'].every(p=>document.getElementById('btn-plat-'+p).classList.contains('connected'))")
   assert not page.locator('#btnSimulateChat').count()
   page.locator('#txtChatInput').fill('hello from program');page.locator('#btnChatSend').click();page.locator('#chatList').get_by_text('hello from program').wait_for()
   page.wait_for_function("window.__audio.some(url=>url.includes('gender=male'))")
   row=page.locator('#chatList .chat-row').filter(has_text='hello from program');row.locator('.tts-done').wait_for(timeout=5000);assert '135ms' not in page.locator('#chatTtsLatencyBadge').inner_text();assert tw.messages==['hello from program']
   page.evaluate("injectIncomingChat({username:'streamer',platform:'Twitch',platform_key:'twitch',text:'website message',event:'message'})")
   own=page.locator('#chatList .chat-row').filter(has_text='website message');own.locator('.tts-done').wait_for(timeout=10000);assert 'บล็อก TTS' not in own.inner_text()
   with page.expect_popup() as opened:page.locator('#btnRailUserManager').click()
   manager=opened.value;manager.wait_for_load_state();manager.locator('#userRosterBody').get_by_text('streamer',exact=True).first.wait_for(timeout=10000)
   manager.wait_for_timeout(300);manager.locator('#btnFilterBlocked').click();assert manager.locator('#userRosterBody tr').count()==0
   manager.locator('#btnFilterAll').click();assert manager.locator('#userRosterBody tr').count()==1
   with page.expect_popup() as opened:manager.locator('#userRosterBody button').first.click()
   profile=opened.value;profile.wait_for_load_state();profile.locator('[onclick="blockUserFromProfile()"]').click();profile.locator('[data-block-rule="overlay"]').check();profile.locator('#profileBlockRules button').click();assert page.evaluate("window._blockedUsers.streamer.overlay") is True
   profile.locator('#btnProfTab3').click();profile.locator('#paneProfTab3 textarea').fill('memo');profile.locator('#btnSaveUserNotes').click();assert profile.is_closed();assert page.evaluate("JSON.parse(localStorage.getItem('bp3_user_notes')).streamer")=='memo'
   with page.expect_popup() as opened:page.locator('#btnRailSettings').click()
   settings=opened.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('platforms')");assert not settings.locator('#kickBotConnect').is_visible();settings.locator('#win-settings .floating-footer button.primary').click();assert settings.is_closed()
   with page.expect_popup() as opened:page.locator('#btnChatSettings').click()
   chatsettings=opened.value;chatsettings.wait_for_load_state();chatsettings.locator('#chkChatAvatar').uncheck();chatsettings.locator('#win-chat-settings .floating-footer button.primary').click();assert chatsettings.is_closed();assert page.evaluate("JSON.parse(localStorage.getItem('bp3_chat_display_config')).showAvatar") is False
   print('PASS own Twitch messages, selected voice, real TTS timing, KICK hidden, user manager and profile block rules (fake clients/audio)');browser.close()
 finally:server.shutdown();server.server_close()


