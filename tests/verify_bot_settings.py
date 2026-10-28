import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bot-settings-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as result:page.locator('#btnRailSettings').click()
   settings=result.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('chatbot')")
   settings.locator('button[onclick="addBotCommandPrompt()"]').click();settings.locator('#botCommandName').fill('!example');settings.locator('#botCommandResponse').fill('test reply');settings.locator('button[onclick="saveBotCommand()"]').click();assert settings.locator('#botCommandsList').inner_text().find('!example')>=0
   settings.locator('button[onclick="openBotTimerForm()"]').click();settings.locator('#botTimerText').fill('test timer');settings.locator('button[onclick="saveBotTimer()"]').click();assert 'test timer' in settings.locator('#botTimerList').inner_text()
   assert page.evaluate("JSON.parse(localStorage.getItem('bp3_bot_settings_v1')).commands[0].command==='!example'");assert page.evaluate("getSpeakableChatText('!example')==='' ");print('PASS create command/timer in settings and suppress command from TTS')
   settings.close();page.reload()
   with page.expect_popup() as result:page.locator('#btnRailSettings').click()
   settings=result.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('chatbot')");assert '!example' in settings.locator('#botCommandsList').inner_text() and 'test timer' in settings.locator('#botTimerList').inner_text();print('PASS command and timer persist across reload');browser.close()
 finally:server.shutdown();server.server_close()
