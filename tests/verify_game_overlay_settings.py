import json, os, sys, tempfile, threading, time, urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root));sys.dont_write_bytecode=True
os.environ['BP3_EDITION']='lite'
import launch_dev
from game_chat_settings import snapshot, update
from viewer_overlay_config import configure
from desktop_overlay_service import DesktopOverlays
import io

class FakeProcess:
 def __init__(self):self.stdin=io.StringIO()
 def poll(self):return None
service=DesktopOverlays(lambda:{'legacyTools':{}},lambda value:None,lambda value:None)
item={'id':'fake','kind':'game','index':0,'process':FakeProcess()}
service.instances['fake']=item
service._demo=lambda item,stop:stop.wait(2)
service.act('demo','game','http://127.0.0.1:8801');assert item.get('demo_stop') and service.snapshot()['instances'][0]['demo_running']
service.act('demo','game','http://127.0.0.1:8801');assert item.get('demo_stop') is None and not service.snapshot()['instances'][0]['demo_running']
service.instances.clear();service.stop()

original={'game_overlay_mode_configs':{'default':{'font_size':20},'theme':{'theme':'neon','font_size':25}},'more_overlays':[{'url':'https://example.com','enabled':True,'x':123,'y':90}]}
data=update(original,'theme','font_size',32)
assert data['game_overlay_mode_configs']['default']['font_size']==20
assert data['game_overlay_mode_configs']['theme']['font_size']==32
assert original['game_overlay_mode_configs']['theme']['font_size']==25
assert snapshot(data)['values']['font_size']==20  # default mode remains independent
fresh=update({'game_overlay_font_size':14},'theme','mode','theme')
fresh=update(fresh,'theme','font_size',32)
fresh=update(fresh,'default','mode','default')
assert snapshot(fresh)['values']['font_size']==14
viewer={};configure(viewer,{'viewer_overlay_mode':'per_platform','viewer_overlay_font_size':22})
assert viewer['viewer_overlay_mode']=='per_platform' and viewer['viewer_overlay_font_size']==22

with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.playroom_media.root=Path(tmp)/'uploads'
 hotkey_changes=[];launch_dev.desktop_overlays.rebind_game_hotkey=lambda action,chord,base:hotkey_changes.append((action,chord))
 launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','name':'test','widgets':[{'id':'text-one','type':'text','title':'Keep'}]}], 'legacyTools':original,'legacyChat':{'separate':'unchanged','overlay_animated_emotes':True}})
 emote_calls=[];launch_dev.emote_service.read=lambda eid,animated:(emote_calls.append((eid,animated)) or (b'fake','image/png'))
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  urllib.request.urlopen(base+'/game-emote/123').read();urllib.request.urlopen(base+'/emote/123').read()
  assert emote_calls==[('123',False),('123',True)]
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context();page=ctx.new_page();page.goto(base+'/index.html')
   overlay=ctx.new_page();overlay.goto(base+'/legacy-game-chat.html');overlay.wait_for_function("typeof window.BP3LegacyChatReceive === 'function'")
   with ctx.expect_page() as opened:page.evaluate('openDesktopOverlaySettings()')
   pop=opened.value;pop.wait_for_load_state();pop.locator('#gameChatCustomizer .game-chat-mode').first.wait_for()
   assert pop.locator('#paneGoGame input[type=number]:visible').count()==0
   width=pop.locator('#goGameWidth');assert width.get_attribute('type')=='range'
   width.evaluate("e=>{e.value='420';e.dispatchEvent(new Event('input',{bubbles:true}))}")
   assert pop.locator('#goGameWidthValue').inner_text()=='420px'
   if os.environ.get('BP3_SCREENSHOT'):pop.screenshot(path=os.environ['BP3_SCREENSHOT'])
   footer=pop.locator('#win-game-overlay > .floating-footer')
   assert abs(footer.bounding_box()['y']+footer.bounding_box()['height']-pop.viewport_size['height']) < 3
   assert pop.locator('#tabGoMore').count()==0
   assert pop.locator('#paneGoMore').is_hidden()
   hotkeys=pop.locator('#gameOverlayHotkeys')
   assert hotkeys.bounding_box()['y'] < pop.locator('#gameChatCustomizer').bounding_box()['y']
   hotkey=hotkeys.locator('button').first;hotkey.click();hotkey.press('Escape')
   assert pop.locator('#win-game-overlay').is_visible() and hotkey.inner_text()=='ctrl+shift+g'
   hotkey.click();hotkey.press('Control+Shift+J')
   page.wait_for_function("fetch('/api/game-chat-settings').then(r=>r.json()).then(c=>c.values.hotkey==='ctrl+shift+j')")
   assert hotkey_changes==[('toggle','ctrl+shift+j')]
   pop.locator('.game-chat-mode').filter(has_text='Theme').click()
   theme_grid=pop.locator('#gameChatThemeGrid');theme_grid.wait_for()
   assert theme_grid.locator('.game-chat-theme-card').count()==10
   retained_font=pop.locator('details').filter(has_text='เนื้อหาและการจัดวาง').locator('input[data-game-chat-key=font_size]')
   retained_font.evaluate("e=>window.gameOverlayFontControl=e")
   pop.locator('#gameChatThemeNext').click()
   assert pop.locator('#gameChatThemePage').inner_text().startswith('หน้า 2 / ')
   assert retained_font.evaluate("e=>e===window.gameOverlayFontControl")
   pop.locator('#gameChatThemePrev').click()
   pop.locator('#gameChatThemeGrid [data-theme=neon]').click()
   page.wait_for_function("fetch('/game-chat-config').then(r=>r.json()).then(c=>c.theme==='neon')")
   overlay.wait_for_function("document.querySelector('#theme-css')?.textContent.includes('--box-bg')")
   font=pop.locator('details').filter(has_text='เนื้อหาและการจัดวาง').locator('input[data-game-chat-key=font_size]')
   assert font.get_attribute('type')=='range'
   font.evaluate("e=>{e.value='31';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
   assert font.locator('xpath=..').locator('output').inner_text()=='31'
   page.wait_for_function("fetch('/game-chat-config').then(r=>r.json()).then(c=>c.font_size===31)")
   overlay.wait_for_function("getComputedStyle(document.documentElement).getPropertyValue('--font-size').trim()==='31px'")
   pop.locator('.game-chat-mode').filter(has_text='Default').click()
   page.wait_for_function("fetch('/game-chat-config').then(r=>r.json()).then(c=>c.theme==='default' && c.font_size===20)")
   overlay.wait_for_function("document.querySelector('#theme-css')?.textContent.trim()===''")
   overlay.evaluate('''() => {
    addMessage({author:'Alice',text:'abcdefghij',platform:'twitch',timestamp:'12:34',segments:[{type:'emote',url:'/logo/twitch'}]});
    window.testMessage=document.querySelector('.msg:not(.exiting)');
    applyConfig({layout:'stacked',show_logo:true,show_timestamp:true,emote_size:42,msg_spacing:0});
   }''')
   assert overlay.evaluate("document.querySelector('.msg:not(.exiting)') === window.testMessage")
   assert overlay.locator('.msg:not(.exiting).layout-stacked').count()==1
   assert overlay.locator('.msg:not(.exiting) img.emote').first.evaluate("e => e.style.width")=='42px'
   assert overlay.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--msg-gap').trim()")=='0px'
   overlay.evaluate("applyConfig({layout:'message_only',show_logo:false,show_timestamp:false,emote_size:24})")
   assert overlay.locator('.msg:not(.exiting) .author').count()==0
   assert overlay.locator('.msg:not(.exiting) img.emote').first.evaluate("e => e.style.width")=='24px'
   pop.locator('.game-chat-mode').filter(has_text='Character Talk').click()
   image=pop.locator('#gameChatCustomizer input[type=file]');image.wait_for()
   image.set_input_files({'name':'test.png','mimeType':'image/png','buffer':bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000b49444154789c636000020000050001a5f645400000000049454e44ae426082')})
   page.wait_for_function("fetch('/game-chat-config').then(r=>r.json()).then(c=>c.character_mode && c.game_character_image_url.startsWith('/playroom-media/'))")
   overlay.wait_for_function("config.character_mode === true && !!config.game_character_image_url")
   overlay.evaluate("window.BP3LegacyChatReceive({event:'DESKTOP_CHAT_MESSAGE',payload:{kind:'game',message:{username:'test',text:'hello'}}})")
   overlay.wait_for_function("document.querySelector('.char-img')?.getAttribute('src')?.startsWith('/playroom-media/')")
   pop.locator('#tabGoViewer').click();pop.locator('#goViewerMode').select_option('per_platform')
   assert pop.locator('#paneGoViewer input[type=number]:visible').count()==0
   viewer_font=pop.locator('#goViewerFontSize');assert viewer_font.get_attribute('type')=='range'
   viewer_font.evaluate("e=>{e.value='22';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
   assert pop.locator('#goViewerFontSizeValue').inner_text()=='22px'
   alpha=pop.locator('#goViewerAlpha');alpha.evaluate("e=>{e.value='0';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))}")
   assert pop.locator('#goViewerAlphaValue').inner_text()=='0%'
   page.wait_for_function("fetch('/api/viewer-overlay').then(r=>r.json()).then(v=>v.config.mode==='per_platform' && v.config.font_size===22)")
   pop.locator('#btnSaveGameOverlaySettings').click();pop.wait_for_event('close')
   state=json.loads(Path(launch_dev.LAYOUT_FILE).read_text(encoding='utf-8'))
   assert state['legacyTools']['more_overlays']==original['more_overlays']
   assert state['legacyTools']['viewer_overlay_mode']=='per_platform' and state['legacyTools']['viewer_overlay_font_size']==22 and state['legacyTools']['viewer_overlay_alpha']==0
   assert state['legacyTools']['game_overlay_width']==420
   assert state['pages'][0]['widgets'][0]['title']=='Keep' and state['legacyChat']=={'separate':'unchanged','overlay_animated_emotes':True}
   with ctx.expect_page() as opened:page.evaluate('openDesktopOverlaySettings()')
   pop=opened.value;pop.locator('#gameChatCustomizer .game-chat-mode').first.wait_for()
   with pop.expect_event('close'):pop.locator('.floating-footer button').filter(has_text='ปิดหน้าต่าง').click()
   page.evaluate("document.getElementById('win-game-overlay').classList.add('active')")
   embedded=page.locator('#win-game-overlay');embedded.wait_for(state='visible')
   before=embedded.bounding_box();handle=page.locator('#drag-game-overlay').bounding_box()
   page.mouse.move(handle['x']+35,handle['y']+18);page.mouse.down();page.mouse.move(handle['x']+95,handle['y']+58,steps=5);page.mouse.up()
   after=embedded.bounding_box();assert abs(after['x']-before['x'])>10
   embedded.locator('.floating-footer button').filter(has_text='ปิดหน้าต่าง').click()
   assert not embedded.is_visible(), embedded.evaluate("e=>({className:e.className,style:e.getAttribute('style'),display:getComputedStyle(e).display})")
   with ctx.expect_page() as opened:page.evaluate('openOverlayPlusSettings()')
   plus=opened.value;plus.locator('#opUrl0').wait_for();plus.wait_for_function("document.querySelector('#opUrl0').value==='https://example.com'")
   plus.locator('#opUrl0').fill('https://example.org')
   with plus.expect_event('close'):plus.locator('.floating-footer button').filter(has_text='บันทึก').click()
   state=json.loads(Path(launch_dev.LAYOUT_FILE).read_text(encoding='utf-8'))
   assert state['legacyTools']['more_overlays'][0]['url']=='https://example.org' and state['legacyTools']['more_overlays'][0]['x']==123
   assert state['legacyTools']['game_overlay_mode_configs']['theme']['font_size']==31
   browser.close();print('PASS separate Game Overlay themes, live rendering, viewer save, retained other settings and popup close')
 finally:server.shutdown();server.server_close()

