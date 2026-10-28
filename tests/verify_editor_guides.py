import sys,json,tempfile,threading,hashlib,io
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from PIL import Image
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-guides-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'pages':[{'id':'guides','widgets':[{'id':'idle','type':'playroom','title':'Standby','x':100,'y':400,'width':320,'height':90},{'id':'empty','type':'image','title':'Empty image','x':600,'y':400,'width':320,'height':90},{'id':'viewers','type':'viewer','title':'Viewer','x':50,'y':50,'width':500,'height':70,'viewerMode':'per_platform','viewerPlatforms':['mylive'],'showIcon':True}]}],'activePageId':'guides'})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1920,'height':1080});context.route('https://**/*',lambda r:r.abort());context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))));app=context.new_page();app.set_default_timeout(8000);app.goto(base+'/index.html')
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.set_default_timeout(8000);composer.wait_for_load_state('domcontentloaded');idle=composer.locator('#widget-idle');idle.wait_for(state='visible');check('Unselected standby widget has thin dashed editor guide',idle.evaluate("e=>getComputedStyle(e).outlineStyle==='dashed'"));check('Empty image placement is also visible in editor',composer.locator('#widget-empty').evaluate("e=>getComputedStyle(e).outlineStyle==='dashed'"))
   image=composer.locator('.plat-icon-mylive');composer.wait_for_function("document.querySelector('.plat-icon-mylive')?.naturalWidth>0");check('MyLive icon decodes in Composer',image.evaluate("e=>e.complete && getComputedStyle(e).display!=='none' && e.getAttribute('src').startsWith('data:image/png;base64,')"))
   idle.click();check('Selected widget retains its solid selection outline',idle.evaluate("e=>getComputedStyle(e).outlineStyle==='solid'"));composer.locator('#btnCompPreview').click();check('Clean preview hides all editor guides',composer.locator('#widget-empty').evaluate("e=>getComputedStyle(e).outlineStyle==='none'"));composer.locator('#btnCompPreview').click()
   remote=browser.new_context(viewport={'width':1920,'height':1080});overlay=remote.new_page();overlay.on('pageerror',lambda e:errors.append(str(e)));overlay.goto(base+'/?p=1');overlay.wait_for_function("document.querySelector('.plat-icon-mylive')?.naturalWidth>0");check('MyLive icon decodes on independent OBS source page',overlay.locator('.plat-icon-mylive').evaluate("e=>e.complete && e.naturalWidth>0 && getComputedStyle(e).display!=='none'"))
   check('OBS widget markup has no editor guide or outline',overlay.locator('.widget[data-id="idle"]').evaluate("e=>getComputedStyle(e).outlineStyle==='none'"))
   overlay.mouse.move(260,445);check('Hovering OBS source still cannot show editor outline',overlay.locator('.widget[data-id="idle"]').evaluate("e=>getComputedStyle(e).outlineStyle==='none'"))
   png=overlay.screenshot(omit_background=True,clip={'x':98,'y':398,'width':324,'height':94});image=Image.open(io.BytesIO(png)).convert('RGBA');check('OBS standby pixels remain completely transparent including border area',image.getchannel('A').getextrema()==(0,0));(out/'obs-standby-no-guides.png').write_bytes(png)
   composer.screenshot(path=str(out/'composer-editor-guides.png'),timeout=8000);check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'editor-guides.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
