import os,sys,tempfile,threading,json,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));os.environ['BP3_EDITION']='lite'
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':m,'type':'chat','chatMode':m,'chatTheme':'neon' if m=='theme' else 'default','width':800,'height':600} for m in ['default','theme','danmaku','balloon','character']]
 launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':widgets}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   b=p.chromium.launch();ctx=b.new_context();page=ctx.new_page();page.goto(base+'/index.html');page.evaluate("localStorage.setItem('bp3_master_tts','false')")
   launch_dev.overlay_events.publish({'event':'CHAT_MESSAGE','payload':{'id':901,'username':'Fixture','text':'OLD_REPLAY_FIXTURE','platform':'twitch'}})
   for index,mode in enumerate(['default','theme','danmaku','balloon','character']):
    overlay=ctx.new_page();overlay.goto(base+'/legacy-chat.html?id='+mode+'&p=one');overlay.wait_for_function("typeof BP3LegacyChatReceive==='function'");overlay.wait_for_timeout(500)
    assert 'OLD_REPLAY_FIXTURE' not in overlay.locator('body').inner_text(),mode
    text='NEW_'+mode.upper()+'_FIXTURE'
    launch_dev.overlay_events.publish({'event':'CHAT_MESSAGE','payload':{'id':1000+index,'username':'Fixture','text':text,'platform':'twitch'}})
    overlay.wait_for_function('(t)=>document.body.innerText.includes(t)',arg=text)
    overlay.close()
   print('PASS no chat-history replay; new live messages render in all five modes')
   with page.expect_popup() as opened:page.locator('#btnRailComposer').click()
   studio=opened.value;studio.wait_for_function("window.ComposerStudio?.state?.pages?.length>0")
   assert studio.evaluate("async()=>{const s=ComposerStudio.state;s.pages[0].widgets[0].fontSize=37;s.pages[0].widgets[0].x=123;return await ComposerStudio.saveState(true)}")
   persisted=json.load(urllib.request.urlopen(base+'/api/composer/layout'))
   assert persisted['pages'][0]['widgets'][0]['fontSize']==37
   studio.close()
   with page.expect_popup() as opened:page.locator('#btnRailComposer').click()
   studio=opened.value;studio.wait_for_function("window.ComposerStudio?.state?.pages?.[0]?.widgets?.[0]?.fontSize===37")
   assert studio.evaluate('ComposerStudio.state.pages[0].widgets[0].x')==123
   print('PASS Composer saves settings and position and restores after reopen')
   b.close()
 finally:server.shutdown();server.server_close()
