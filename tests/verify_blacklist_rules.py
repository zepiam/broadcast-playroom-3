import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from layout_migration import normalize_layout
assert normalize_layout({'pages':[{'id':'one','widgets':[]}],'blocked_users':[{'name':'OldUser','hide_overlay':False}],'tts_bot_blacklist':['oldbot'],'overlay_hide_bots':False,'twitch_bot_name':'OldBot'})['legacyTools']['blocked_users'][0]['hide_overlay'] is False
with tempfile.TemporaryDirectory(prefix='bp3-blacklist-') as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[{'id':'chat','type':'chat','chatMode':'default','width':600,'height':400}]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.set_default_timeout(10000);page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   dock=ctx.new_page();dock.goto(f'http://127.0.0.1:{server.server_port}/dock.html')
   game=ctx.new_page();game.goto(f'http://127.0.0.1:{server.server_port}/legacy-game-chat.html');game.locator('#chat').wait_for(state='attached')
   obs=ctx.new_page();obs.goto(f'http://127.0.0.1:{server.server_port}/composer.html');obs.frame_locator('#legacyChat_chat').locator('#chat').wait_for(state='attached')
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('block')")
   names=settings.locator('#botBlacklistNames').input_value().splitlines();assert names==['nightbot','streamelements','streamlabs','moobot','wizebot','fossabot','deepbot','phantombot','sery_bot','buttsbot','kapsulebot'];assert settings.locator('#botBlacklistHideOverlay').is_checked()
   page.evaluate("window.__tts=[];window.playChatMessageSpeech=(name,text)=>window.__tts.push([name,text]);window._masterTtsEnabled=true")
   page.evaluate("injectIncomingChat({username:'NightBot',platform:'Twitch',text:'bot hidden one',event:'message'})")
   page.locator('#chatList').filter(has_text='bot hidden one').wait_for();dock.locator('#liveChatMessages').filter(has_text='bot hidden one').wait_for();page.wait_for_timeout(500);assert page.evaluate('window.__tts.length')==0;assert 'bot hidden one' not in obs.frame_locator('#legacyChat_chat').locator('#chat').inner_text() and 'bot hidden one' not in game.locator('#chat').inner_text()
   settings.locator('#botBlacklistHideOverlay').uncheck();page.evaluate("injectIncomingChat({username:'NIGHTBOT',platform:'Twitch',text:'bot visible two',event:'message'})");obs.frame_locator('#legacyChat_chat').locator('#chat').filter(has_text='bot visible two').wait_for();game.locator('#chat').filter(has_text='bot visible two').wait_for();assert page.evaluate('window.__tts.length')==0
   settings.locator('#blockedViewerName').fill('UserOnlyTTS');settings.locator('button[onclick="blockViewerFromSettings()"]:visible').click();settings.get_by_label('บล็อก ทุกส่วน useronlytts').uncheck();settings.get_by_label('บล็อก TTS useronlytts').check()
   page.evaluate("injectIncomingChat({username:'UserOnlyTTS',platform:'Twitch',text:'tts only chat',event:'message'})");page.locator('#chatList').filter(has_text='tts only chat').wait_for();obs.frame_locator('#legacyChat_chat').locator('#chat').filter(has_text='tts only chat').wait_for();assert page.evaluate('window.__tts.length')==0
   settings.get_by_label('บล็อก ทุกส่วน useronlytts').check();page.wait_for_timeout(250);assert 'useronlytts' in launch_dev.chat_bridge._bot_blocked_names;page.evaluate("injectIncomingChat({username:'UserOnlyTTS',platform:'Twitch',text:'block all chat',event:'message'})");assert 'block all chat' not in page.locator('#chatList').inner_text()
   page.evaluate("injectIncomingChat({username:'UserOnlyTTS',platform:'Twitch',text:'blocked event',event:'sub'})");assert 'blocked event' not in page.locator('#chatList').inner_text()
   settings.get_by_label('บล็อก ทุกส่วน useronlytts').uncheck();page.wait_for_timeout(250);assert 'useronlytts' not in launch_dev.chat_bridge._bot_blocked_names;settings.get_by_label('บล็อก TTS useronlytts').uncheck();settings.get_by_label('บล็อก Overlay useronlytts').check();settings.get_by_label('บล็อก Replie useronlytts').check()
   page.evaluate("window.__replie=[];window.checkRealReplieCommand=(msg)=>window.__replie.push(msg.username);injectIncomingChat({username:'UserOnlyTTS',platform:'Twitch',text:'replie overlay hidden',event:'message'})")
   page.locator('#chatList').filter(has_text='replie overlay hidden').wait_for();page.wait_for_timeout(500);assert 'replie overlay hidden' not in obs.frame_locator('#legacyChat_chat').locator('#chat').inner_text();assert page.evaluate('window.__tts.length')==1 and page.evaluate('window.__replie.length')==0
   settings.get_by_label('บล็อก Overlay useronlytts').uncheck();settings.get_by_label('บล็อก Replie useronlytts').uncheck()
   page.evaluate("injectIncomingChat({username:'UserOnlyTTS',platform:'Twitch',text:'all allowed',event:'message'})");obs.frame_locator('#legacyChat_chat').locator('#chat').filter(has_text='all allowed').wait_for();assert page.evaluate('window.__tts.length')==2 and page.evaluate('window.__replie.length')==1
   page.evaluate("injectIncomingChat({username:'NormalUser',platform:'Twitch',text:'normal text',event:'message'})");assert page.evaluate('window.__tts.length')==3
   assert settings.get_by_label('บล็อก TTS nightbot').is_checked() and settings.get_by_label('บล็อก Replie nightbot').is_checked()
   settings.get_by_label('บล็อก TTS nightbot').uncheck();settings.get_by_label('บล็อก Replie nightbot').uncheck()
   page.evaluate("injectIncomingChat({username:'NightBot',platform:'Twitch',text:'bot allowed speech',event:'message'})");assert page.evaluate('window.__tts.length')==4 and page.evaluate('window.__replie.length')==3
   row=settings.locator('#blockedViewerList tr').filter(has_text='nightbot');row.get_by_text('คืนค่าเริ่มต้น').click();assert settings.get_by_label('บล็อก TTS nightbot').is_checked()
   page.evaluate("applyLegacyToolData({legacyTools:{blocked_users:[{name:'OldUser',hide_overlay:false}],tts_bot_blacklist:['oldbot'],overlay_hide_bots:true}})")
   assert page.evaluate("window._blockedUsers.olduser")=='tts';assert 'nightbot' in settings.locator('#botBlacklistNames').input_value()
   settings.evaluate("document.documentElement.dataset.uiTextSize='xlarge'");settings.evaluate("switchSettingsSection('block')")
   assert settings.locator('#blockedViewerList tr').first.evaluate("row=>{const outer=row.getBoundingClientRect();return [...row.querySelectorAll('input,button')].every(el=>{const r=el.getBoundingClientRect();return r.left>=outer.left && r.right<=outer.right && r.top>=outer.top && r.bottom<=outer.bottom;});}")
   settings.close();page.reload()
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('block')");assert not settings.locator('#botBlacklistHideOverlay').is_checked();assert settings.locator('#blockedViewerList').inner_text().lower().find('olduser')>=0
   print('PASS bot defaults, four independent block rules, overlay toggle, migration and persistence');browser.close()
 finally:server.shutdown();server.server_close()
