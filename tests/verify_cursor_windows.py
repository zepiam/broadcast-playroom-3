import sys,json,tempfile,threading,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-cursor-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'pages':[{'id':'cursor','widgets':[]}],'activePageId':'cursor'})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1920,'height':1080});context.route('https://**/*',lambda r:r.abort());context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))));app=context.new_page();app.set_default_timeout(8000);app.goto(base+'/index.html')
   for rail in ['#btnRailAsk','#btnRailGw','#btnRailRandomizer','#btnRailPlayroom','#btnRailReplie','#btnRailSettings']:
    with app.expect_popup() as info:app.locator(rail).click()
    popup=info.value;popup.set_default_timeout(8000);popup.wait_for_load_state('domcontentloaded');popup.locator('.win-resize-handle').first.wait_for(state='attached')
    check('Detached tool hides embedded resize grip '+rail,popup.locator('.win-resize-handle').count()>0 and not popup.locator('.win-resize-handle').first.is_visible())
    popup.locator('.win-resize-handle').first.dispatch_event('pointerdown',{'button':0,'pointerId':1,'buttons':1});popup.mouse.up()
    check('Detached grip cannot lock parent cursor '+rail,app.evaluate("!document.body.classList.contains('win-is-resizing') && !document.body.style.cursor"))
    popup.close(run_before_unload=True)
   with app.expect_popup() as info:app.locator('#btnRailAsk').click()
   popup=info.value;popup.wait_for_load_state('domcontentloaded');popup.locator('.btn-popout-toggle').click();app.locator('#win-ask').wait_for(state='visible');handle=app.locator('#win-ask .win-resize-handle');check('Docking restores embedded resize grip',handle.is_visible())
   app.bring_to_front();app.wait_for_timeout(150);box=handle.bounding_box();before=app.locator('#win-ask').bounding_box();app.mouse.move(box['x']+8,box['y']+8);app.mouse.down();check('Resize cursor is active only while dragging',app.evaluate("document.body.classList.contains('win-is-resizing')"));app.mouse.move(box['x']+48,box['y']+38,steps=4);app.mouse.up();after=app.locator('#win-ask').bounding_box()
   check('Actual embedded resize works and releases cursor',after['width']>before['width'] and after['height']>before['height'] and app.evaluate("!document.body.classList.contains('win-is-resizing') && !document.querySelector('.floating-window.resizing')"))
   box=handle.bounding_box();app.mouse.move(box['x']+8,box['y']+8);app.mouse.down();app.evaluate("dispatchEvent(new Event('blur'))");app.mouse.up();check('Changing focus cancels resize and restores cursor',app.evaluate("!document.body.classList.contains('win-is-resizing')"))
   box=handle.bounding_box();app.mouse.move(box['x']+8,box['y']+8);app.mouse.down();app.evaluate("document.dispatchEvent(new PointerEvent('pointercancel',{pointerId:1}))");app.mouse.up();check('Cancelled pointer restores cursor',app.evaluate("!document.body.classList.contains('win-is-resizing')"))
   box=handle.bounding_box();app.mouse.move(box['x']+8,box['y']+8);app.mouse.down()
   with app.expect_popup() as info:app.evaluate("popoutToolWindow('ask')")
   popup=info.value;popup.wait_for_load_state('domcontentloaded');popup.mouse.up();check('Detaching during resize clears cursor and uses native border',app.evaluate("!document.body.classList.contains('win-is-resizing')") and not popup.locator('.win-resize-handle').is_visible());popup.close(run_before_unload=True)
   check('Window size persists and no JavaScript errors',app.evaluate("!!JSON.parse(localStorage.getItem('bp3_win_size_win-ask')).w") and not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'cursor-windows.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
