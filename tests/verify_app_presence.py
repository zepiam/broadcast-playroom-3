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
with tempfile.TemporaryDirectory(prefix='bp3-presence-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'presence','pages':[{'id':'presence','widgets':[{'id':'text','type':'text','text':'PRESENCE CONTENT','textMode':'static','bgEnabled':True,'width':400,'height':100}]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();overlay_context=browser.new_context(viewport={'width':500,'height':200});source=overlay_context.new_page();source.set_default_timeout(8000);source.on('pageerror',lambda e:errors.append(str(e)));source.goto(base+'/?p=1');source.wait_for_selector('.widget',state='attached')
   check('Source is hidden before main app starts',source.locator('html').evaluate("e=>e.classList.contains('bp3-app-offline')"))
   context=browser.new_context();context.route('https://**/*',lambda r:r.abort());context.add_init_script("if(location.protocol==='http:')localStorage.setItem('bp3_master_tts','false')");app=context.new_page();app.on('pageerror',lambda e:errors.append(str(e)));app.goto(base+'/index.html');source.wait_for_function("!document.documentElement.classList.contains('bp3-app-offline')")
   check('Opening main app shows retained source',source.locator('.widget').is_visible())
   source.evaluate("window.keptWidget=document.querySelector('.widget');window.keptText=document.querySelector('.type-text span')")
   app.close();source.wait_for_function("document.documentElement.classList.contains('bp3-app-offline')")
   check('Closing main window hides source even with backend still running',source.request.get(base+'/api/app-presence').json()['active'] is False)
   data=source.screenshot(omit_background=True);(out/'presence-offline.png').write_bytes(data);alpha=Image.open(io.BytesIO(data)).convert('RGBA').getchannel('A');check('Hidden source pixels fully transparent',alpha.getextrema()==(0,0))
   app=context.new_page();app.goto(base+'/index.html');source.wait_for_function("!document.documentElement.classList.contains('bp3-app-offline')")
   check('Reopening app restores existing DOM without reloading',source.evaluate("keptWidget===document.querySelector('.widget') && keptText===document.querySelector('.type-text span')"))
   overlay_context.route('**/api/app-presence',lambda r:r.abort());source.wait_for_function("document.documentElement.classList.contains('bp3-app-offline')")
   check('Network/server interruption hides source',True)
   overlay_context.unroute('**/api/app-presence');source.wait_for_function("!document.documentElement.classList.contains('bp3-app-offline')")
   check('Connection recovery restores same source',source.evaluate("keptWidget===document.querySelector('.widget')"))
   second=context.new_page();second.goto(base+'/index.html');second.wait_for_function("document.readyState==='complete'");app.close();source.wait_for_timeout(1200)
   check('Closing one of two main windows keeps source visible',source.locator('html').evaluate("e=>!e.classList.contains('bp3-app-offline')"))
   second.close();source.wait_for_function("document.documentElement.classList.contains('bp3-app-offline')");check('Closing final main window hides source',True)
   check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production layout unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'app-presence.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
