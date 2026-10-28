import sys,json,tempfile,threading,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-cursor-skin-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'pages':[{'id':'cursor','widgets':[]}],'activePageId':'cursor'})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True,args=['--window-position=100,100']);context=browser.new_context(viewport={'width':1400,'height':850});context.route('https://**/*',lambda r:r.abort());context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))));app=context.new_page();app.set_default_timeout(8000);app.goto(base+'/index.html');app.evaluate('BP3CursorSkin.ready');app.bring_to_front()
   app.evaluate("""()=>{const area=document.createElement('div');area.id='cursorAuditArea';area.style.cssText='position:fixed;left:100px;top:150px;width:1000px;height:400px;z-index:999999;background:#222';for(const [id,cursor] of Object.entries({normal:'default',link:'pointer',vertical:'ns-resize',horizontal:'ew-resize',diagonal:'nwse-resize',otherDiagonal:'nesw-resize',text:'text',wait:'wait',grab:'grab'})){const e=document.createElement('div');e.id='cursorAudit_'+id;e.textContent=id;e.style.cssText='display:inline-block;width:100px;height:100px;cursor:'+cursor;area.append(e);}const input=document.createElement('input');input.id='cursorAudit_input';input.value='Windows text cursor';area.append(input);document.body.append(area);} """)
   check('Browser decodes all original CUR frames',app.evaluate("async()=>{const manifest=await BP3CursorSkin.ready;await Promise.all(Object.values(manifest).flatMap(x=>x.frames).map(frame=>new Promise((resolve,reject)=>{const image=new Image();image.onload=resolve;image.onerror=reject;image.src='/assets/cursors/ragnarok/'+frame.file;})));return true;}"))
   handles={}
   for role in ['normal','link','vertical','horizontal','diagonal']:
    item=app.locator('#cursorAudit_'+role);item.hover();app.wait_for_function("role=>document.querySelector('[data-bp3-cursor]')?.getAttribute('data-bp3-cursor')===role",arg=role);frames=set()
    for index in range(14):frames.add(item.evaluate('e=>getComputedStyle(e).cursor'));app.wait_for_timeout(70)
    check('Requested animated cursor frames: '+role,len(frames)>=2 and all('/assets/cursors/ragnarok/'+role+'-' in value for value in frames))
   for role,keyword in [('otherDiagonal','nesw-resize'),('text','text'),('wait','wait'),('grab','grab')]:
    item=app.locator('#cursorAudit_'+role);item.hover();app.wait_for_timeout(80);check('Unspecified '+keyword+' remains native',item.evaluate('e=>getComputedStyle(e).cursor')==keyword and app.locator('[data-bp3-cursor]').count()==0)
   app.locator('#cursorAudit_input').hover();app.wait_for_timeout(80);check('Text input retains Windows I-beam',app.locator('#cursorAudit_input').get_attribute('data-bp3-cursor') is None)
   app.evaluate("document.getElementById('cursorAuditArea').remove()")
   with app.expect_popup() as info:app.locator('#btnRailAsk').click()
   popup=info.value;popup.set_default_timeout(8000);popup.wait_for_load_state('domcontentloaded');popup.locator('#askFooterIdle button.primary').hover();popup.wait_for_function("document.querySelector('[data-bp3-cursor=link]')!==null");check('Actual detached tool button uses requested link skin',True)
   popup.locator('#askQuestion').hover();popup.wait_for_timeout(80);check('Detached tool text input stays native',popup.locator('#askQuestion').get_attribute('data-bp3-cursor') is None);popup.close(run_before_unload=True)
   overlay=context.new_page();overlay.goto(base+'/?p=1');check('OBS Overlay has no custom skin script or markers',overlay.evaluate("!window.BP3CursorSkin && !document.querySelector('[data-bp3-cursor]')"));check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'cursor-skin.json').write_text(json.dumps({'results':results,'errors':errors,'scope':'Chromium image decode and animated CSS mapping; no physical Windows cursor capture assertion.'},ensure_ascii=False,indent=2),encoding='utf-8')
