import sys,json,tempfile,threading,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from chat_twitch import ChatMessage
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[];layout_reports=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-readability-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'pages':[{'id':'readability','widgets':[{'id':'viewer','type':'viewer','title':'Viewer','x':100,'y':100,'width':450,'height':80,'viewerMode':'total','fontSize':18}]}],'activePageId':'readability'})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1280,'height':800});context.route('https://**/*',lambda r:r.abort());context.add_init_script("if(location.protocol==='http:')localStorage.setItem('bp3_master_tts','false')");context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e.stack))));app=context.new_page();app.set_default_timeout(8000);app.goto(base+'/index.html');normal=app.locator('#topbar-item-game-overlay').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')
   with app.expect_popup() as info:app.locator('#btnRailSettings').click()
   settings=info.value;settings.set_default_timeout(8000);settings.wait_for_load_state('domcontentloaded');settings.locator('#nav-sec-themes').click();control=settings.locator('#selUiTextSize');check('Normal/large/extra-large choices available in actual settings',control.locator('option').count()==3)
   control.select_option('large');app.wait_for_function("document.documentElement.dataset.uiTextSize==='large'");large=app.locator('#topbar-item-game-overlay').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)');check('Large mode increases application text',abs(large/normal-1.2)<.02)
   control.select_option('xlarge');extra=app.locator('#topbar-item-game-overlay').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)');check('Extra-large mode increases text once without double scaling',abs(extra/normal-1.4)<.02)
   check('Settings navigation rows grow without clipping or overlap',settings.locator('.settings-nav-item').evaluate_all('nodes=>nodes.every(e=>e.scrollHeight<=e.clientHeight+2)'))
   settings.screenshot(path=str(out/'readability-settings-xlarge.png'),timeout=8000)
   settings.close(run_before_unload=True)
   for width,height in [(900,700),(1280,800),(1920,1080)]:
    app.set_viewport_size({'width':width,'height':height});app.wait_for_timeout(150)
    report=app.evaluate("""()=>({width:innerWidth,rootWidth:document.documentElement.scrollWidth,topbarHeight:document.querySelector('.topbar').getBoundingClientRect().height,buttons:[...document.querySelectorAll('.topbar-single-btn,.btn-chat-header,.btn-plat-connect')].filter(e=>e.getBoundingClientRect().width>0 && e.getBoundingClientRect().height>0).map(e=>({text:e.textContent.trim(),width:e.clientWidth,scroll:e.scrollWidth,height:e.clientHeight,contentHeight:e.scrollHeight})).filter(e=>e.scroll>e.width+3 || e.contentHeight>e.height+3)})""");layout_reports.append(report);check('Large-mode controls do not clip text at '+str(width),report['rootWidth']<=width+1 and not report['buttons']);app.screenshot(path=str(out/f'readability-main-{width}.png'),timeout=8000)
   app.set_viewport_size({'width':1280,'height':800});launch_dev.chat_bridge._on_message('Twitch',ChatMessage(platform='twitch',author='Readable auditor',text='ข้อความยาวสำหรับตรวจการตัดบรรทัดและอ่านง่าย '+('LongMessageWithoutSpaces'*20)))
   app.wait_for_selector('#chatList .chat-body-msg');check('Large UI provides larger default chat text',app.locator('#chatList .chat-body-msg').last.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)===20'))
   app.evaluate('adjustFontSize(22-_chatFontSize)');increase=app.locator('[data-item-id="font-inc"]');values=[]
   for i in range(5):increase.click();values.append(app.evaluate('_chatFontSize'))
   check('Exactly five additional chat steps above old 22px limit',values==[23,24,25,26,27]);increase.click();check('Chat font clamps at new 27px maximum',app.evaluate('_chatFontSize===27'))
   app.screenshot(path=str(out/'readability-longchat.png'),timeout=8000);
   check('Long chat text wraps within available message width',app.locator('#chatList .chat-body-msg').last.evaluate('e=>e.scrollWidth<=e.clientWidth+2 && e.getBoundingClientRect().height>30'))
   launch_dev.chat_bridge._on_message('Twitch',ChatMessage(platform='twitch',author='Another readable viewer',text='New messages keep the selected chat size'));app.wait_for_function("[...document.querySelectorAll('#chatList .chat-body-msg')].some(e=>e.textContent.includes('New messages keep') && parseFloat(getComputedStyle(e).fontSize)===27)");check('New incoming messages retain enlarged chat font',True)
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.set_default_timeout(8000);composer.wait_for_load_state('domcontentloaded');composer.locator('.btn-layer-setting').click();check('New Composer window inherits large text preference',composer.evaluate("document.documentElement.dataset.uiTextSize==='xlarge'"));check('Canvas font remains exact despite large UI',composer.locator('#widget-viewer .viewer-total .viewer-ticker').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)===18'))
   check('Composer Chat add label stays on a readable single line',composer.locator('#btnCompAddChatMenu .comp-widget-label').evaluate('e=>e.getBoundingClientRect().height<=parseFloat(getComputedStyle(e).lineHeight)*1.4'))
   composer.wait_for_timeout(300)
   composer.screenshot(path=str(out/'readability-composer-xlarge.png'),timeout=8000)
   remote=browser.new_context();overlay=remote.new_page();overlay.goto(base+'/?p=1');check('OBS source never inherits application text mode',overlay.evaluate("!window.BP3UiText && !document.documentElement.hasAttribute('data-ui-text-size')") and overlay.locator('.viewer-total .viewer-ticker').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)===18'))
   composer.close(run_before_unload=True);app.reload();app.wait_for_function("document.documentElement.dataset.uiTextSize==='xlarge'");check('UI mode and chosen chat font persist after reload',app.evaluate("_chatFontSize===27 && localStorage.getItem('bp3_ui_text_size')==='xlarge'"))
   with app.expect_popup() as info:app.locator('#btnRailSettings').click()
   settings=info.value;settings.wait_for_load_state('domcontentloaded');settings.locator('#nav-sec-themes').click();settings.locator('#selUiTextSize').select_option('normal');check('Normal mode restores original UI font',app.locator('#topbar-item-game-overlay').evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')==normal);check('User-selected chat size survives UI mode changes',app.evaluate('_chatFontSize===27'));check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'readability.json').write_text(json.dumps({'results':results,'errors':errors,'layout':layout_reports},ensure_ascii=False,indent=2),encoding='utf-8')
