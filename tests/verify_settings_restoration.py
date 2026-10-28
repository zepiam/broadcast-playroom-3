import sys,json,tempfile,threading,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
class Handler(launch_dev.QuietHandler):
 def do_GET(self):
  if self.path.startswith('/api/now-playing'):
   self.send_json({'title':'A very long actual fixture track title '*8,'artist':'Settings auditor','is_playing':True,'position':40,'duration':200,'thumbnail':''});return
  super().do_GET()
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-settings-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':kind,'type':kind,'x':i%3*560,'y':i//3*320,'width':440,'height':180} for i,kind in enumerate(['viewer','now_playing','text','avatar','donate_goal','video','image'])];widgets[3]['avatar_preset']='man'
 launch_dev.save_layout({'pages':[{'id':'settings','widgets':widgets}],'activePageId':'settings'})
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1920,'height':1080});context.route('https://**/*',lambda r:r.abort());context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))));app=context.new_page();app.set_default_timeout(8000);app.goto(base+'/index.html')
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.set_default_timeout(8000);composer.wait_for_load_state('domcontentloaded');remote=browser.new_context();overlay=remote.new_page();overlay.set_default_timeout(8000);overlay.on('pageerror',lambda e:errors.append(str(e)));overlay.goto(base+'/?p=1')
   def settings(kind):
    composer.locator('.composer-layer-item[data-id="'+kind+'"] .btn-layer-setting').click()
   composer.screenshot(path=str(out/'settings-composer-before.png'),timeout=8000);settings('viewer');check('Full Viewer controls restored',composer.locator('#compViewerTheme option').count()>=25 and composer.locator('#compViewerTextShadowColor,#compViewerFontFamily,#compViewerDirection,#compViewerMode').count()==4)
   select=composer.locator('#compViewerMode');select.focus();select.press('ArrowDown');check('Focused dropdown ArrowDown changes exactly one option',select.input_value()=='total');select.press('ArrowUp');check('ArrowUp returns one option without moving widget',select.input_value()=='both' and app.evaluate("ComposerStudio.getActivePage().widgets.find(w=>w.id==='viewer').x===0"))
   select.press('ArrowUp');check('Dropdown stops at first option',select.input_value()=='both')
   composer.locator('#compViewerTheme').select_option('neon');composer.locator('#compViewerDirection').select_option('vertical');composer.locator('#compViewerFontSize').fill('27');composer.locator('#compViewerFontSize').press('Tab');overlay.wait_for_function("document.querySelector('.widget.type-viewer .viewer-ticker')?.style.fontSize==='27px'");check('Viewer settings reach independent Overlay',overlay.locator('.viewer-theme-neon.viewer-direction-vertical').count()>0)
   composer.locator('#btnDemoViewerRandom').click();composer.wait_for_function("Number(document.querySelector('#widget-viewer .viewer-total .viewer-ticker')?.textContent.replace(/[^0-9]/g,''))>0");check('Viewer demo is isolated from real Overlay',overlay.locator('.viewer-total .viewer-ticker').inner_text()=='0')
   composer.locator('#btnViewerUseLive').click();composer.wait_for_function("document.querySelector('#widget-viewer .viewer-total .viewer-ticker')?.textContent==='0'");check('Explicit return-to-live button clears demo',True)
   composer.locator('#btnDemoViewerRandom').click();launch_dev.chat_bridge._on_status('twitch','connected');launch_dev.chat_bridge._on_viewer_count('twitch',321);composer.wait_for_function("document.querySelector('#widget-viewer .viewer-total .viewer-ticker')?.textContent==='321'");overlay.wait_for_function("document.querySelector('.viewer-total .viewer-ticker')?.textContent==='321'");check('Real provider update automatically replaces demo',True)
   saved=launch_dev.get_layout()['pages'][0]['widgets'][0];check('Demo count is not persisted as a fake live count',not saved.get('mockViewerCount'))
   settings('text');check('Text settings contain no music controls',composer.locator('#composerCustomizerBody [id^="compNp"]').count()==0 and composer.locator('#compTextInput').count()==1)
   settings('now_playing');check('All original Now Playing source/theme/style and display controls restored',composer.locator('#compNpTheme option').count()==21 and composer.locator('#compNpStyle option').count()==21 and composer.locator('#compNpSource option').count()==4 and composer.locator('#compNpShowArt,#compNpShowProgress,#compNpScrollTitle,#compNpSyncMode,#compNpArtRadius,#compNpTimeFontSize').count()==6)
   composer.locator('#compNpSource').focus();composer.locator('#compNpSource').press('ArrowDown');check('Now Playing source keyboard change persists',app.evaluate("ComposerStudio.getActivePage().widgets.find(w=>w.id==='now_playing').npSource==='spotify'"))
   composer.locator('#compNpTheme').select_option('ocean');composer.locator('#compNpStyle').select_option('metal');overlay.wait_for_function("document.querySelector('.np-style-metal')!==null");overlay.wait_for_function("document.querySelector('.np-title-text')?.style.animation.includes('bp3-np-scroll')");check('Music theme/style/long-title scroll actually render',overlay.locator('.widget-type-now-playing').evaluate("e=>getComputedStyle(e).backgroundColor.includes('0, 26, 51')"))
   composer.locator('#compNpScrollTitle').locator('..').click();overlay.wait_for_function("getComputedStyle(document.querySelector('.np-title-text')).animationName==='none'");composer.locator('#compNpShowArt').locator('..').click();composer.locator('#compNpShowProgress').locator('..').click();overlay.wait_for_function("!document.querySelector('.np-art') && !document.querySelector('.np-progress-row')");check('Music display toggles affect independent Overlay',True)
   composer.locator('#composerCustomizerBody').screenshot(path=str(out/'settings-now-playing.png'),timeout=8000)
   for kind in ['avatar','donate_goal','video','image']:
    settings(kind);check('Consistent settings cards and labelled fields: '+kind,composer.locator('#composerCustomizerBody .comp-card-body .comp-field-row').count()>0 and composer.locator('#composerCustomizerBody .comp-card-header .comp-card-title').count()>0)
    composer.locator('#composerCustomizerBody').screenshot(path=str(out/('settings-'+kind+'.png')),timeout=8000)
   composer.locator('#btnCompAddChatMenu').click();menu=composer.locator('#compChatDropdownMenu');check('Add Chat opens above clipping toolbar',menu.evaluate("e=>e.matches(':popover-open') && (()=>{const r=e.querySelector('.comp-chat-menu-item').getBoundingClientRect();return document.elementFromPoint(r.x+20,r.y+20)?.closest('.comp-chat-menu-item')!==null})()"));menu.locator('[data-chat-mode="balloon"]').click();check('Appearance choice creates the requested Chat widget',app.evaluate("ComposerStudio.getActivePage().widgets.some(w=>w.type==='chat' && w.chatMode==='balloon')"))
   composer.locator('#btnCompAddChatMenu').focus();composer.locator('#btnCompAddChatMenu').press('ArrowDown');composer.keyboard.press('ArrowDown');composer.keyboard.press('Enter');check('Chat appearance menu also supports keyboard selection',app.evaluate("ComposerStudio.getActivePage().widgets.some(w=>w.type==='chat' && w.chatMode==='danmaku')"))
   with app.expect_popup() as info:app.locator('#btnRailAsk').click()
   ask=info.value;ask.wait_for_load_state('domcontentloaded');duration=ask.locator('#askDurationSelect');before=duration.evaluate('e=>e.selectedIndex');count=duration.locator('option').count();duration.focus();duration.press('ArrowDown');check('Settings dropdown outside Composer supports one-step keyboard selection',duration.evaluate('e=>e.selectedIndex')==min(count-1,before+1));ask.close(run_before_unload=True)
   check('No JavaScript errors',not errors);browser.close()
 finally:
  launch_dev.avatar_mic_service.stop();launch_dev.donation_goal_service.stop();server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'settings-restoration.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
