import sys,json,tempfile,threading,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from layout_migration import normalize_layout
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-viewer-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None
 launch_dev.save_layout({'pages':[{'id':'empty','widgets':[]}],'activePageId':'empty','viewer_overlay_font_size':31,'viewer_overlay_mode':'total','viewer_overlay_width':440,'viewer_overlay_height':90,'viewer_overlay_x':100,'viewer_overlay_y':100})
 check('Old flat viewer settings migrate without Composer widget',launch_dev.get_layout()['legacyTools']['viewer_overlay_font_size']==31)
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);app=browser.new_page(viewport={"width":1920,"height":1080});app.set_default_timeout(10000);app.on('pageerror',lambda e:errors.append(str(e)));app.goto(base+'/index.html');overlay=browser.new_page();overlay.set_default_timeout(10000);overlay.on('pageerror',lambda e:errors.append(str(e)));overlay.goto(base+'/viewer_overlay.html');launch_dev.chat_bridge._on_status('twitch','connected');launch_dev.chat_bridge._on_viewer_count('twitch',123);overlay.wait_for_function("document.querySelector('.v-count')?.textContent==='123'")
   check('Original standalone viewer renders provider callback and old font',overlay.locator('.v-count').evaluate("e=>getComputedStyle(e).fontSize==='31px'"))
   app.locator('#topbar-item-game-overlay').click(button='right');app.locator('#topbarContextMenu button').filter(has_text='Viewer Overlay').click();until=time.monotonic()+30
   while time.monotonic()<until and not any(x.get('ready') for x in launch_dev.desktop_overlays.snapshot()['instances']):app.wait_for_timeout(100)
   check('Actual context-menu click starts native Qt viewer window',any(x['kind']=='viewer' and x['ready'] for x in launch_dev.desktop_overlays.snapshot()['instances']))
   app.locator('#topbar-item-game-overlay').click(button='right');app.locator('#topbarContextMenu button').filter(has_text='ซ่อน/แสดงกรอบปรับแต่ง').click();app.wait_for_timeout(400);check('Existing edit menu controls actual native viewer too',all(not x['editing'] for x in launch_dev.desktop_overlays.snapshot()['instances']))
   with app.expect_popup() as info:app.evaluate('openDesktopOverlaySettings()')
   settings=info.value;settings.wait_for_load_state('domcontentloaded');settings.locator('#desktop-viewer_mode').select_option('per_platform');settings.locator('#desktop-viewer_font_size').fill('26');settings.locator('#desktop-viewer_font_color').fill('#00ff00');settings.locator('#desktop-viewer_text_stroke').uncheck();settings.locator('#btnSaveDesktopOverlays').click();overlay.wait_for_function("document.querySelector('.v-icon') && getComputedStyle(document.querySelector('.v-count')).fontSize==='26px'")
   check('Actual settings change original standalone renderer live',overlay.locator('.v-count').first.evaluate("e=>getComputedStyle(e).color==='rgb(0, 255, 0)' && getComputedStyle(e).webkitTextStrokeWidth==='0px'"))
   settings.locator('#desktop-viewer_mode').select_option('off');settings.locator('#btnSaveDesktopOverlays').click();overlay.wait_for_function("document.getElementById('viewer').childElementCount===0");check('Off mode restores transparent empty viewer',True)
   settings.locator('#desktop-viewer_mode').select_option('total');settings.locator('#btnSaveDesktopOverlays').click();launch_dev.chat_bridge._on_status('twitch','disconnected');overlay.wait_for_function("document.querySelector('.v-count')?.textContent==='0'");check('Disconnect removes stale count',True)
   app.locator('#topbar-item-game-overlay').click(button='right');app.locator('#topbarContextMenu button').filter(has_text='Viewer Overlay').click();app.wait_for_timeout(500);check('Same menu closes only viewer window',not launch_dev.desktop_overlays.snapshot()['instances'])
   saved=launch_dev.get_layout()['legacyTools'];check('Viewer settings persist and no JavaScript errors',saved['viewer_overlay_font_size']==26 and saved['viewer_overlay_mode']=='total' and not errors);browser.close()
 finally:
  launch_dev.desktop_overlays.stop();server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'viewer-standalone.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
