import sys,json,tempfile,threading,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);results=[];errors=[]
def record(test,passed):
 print(test,passed,flush=True);results.append({'test':test,'status':'PASS' if passed else 'FAIL'});assert passed,test
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-webcam-') as directory:
 launch_dev.LAYOUT_FILE=str(Path(directory)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'webcam','pages':[{'id':'webcam','widgets':[{'id':'frame','type':'webcam','webcam_theme':'neon-blue','webcam_border_width':12,'webcam_ratio':'4:3','width':400,'height':300}]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1920,'height':1080});context.route('https://**/*',lambda route:route.abort());app=context.new_page();app.set_default_timeout(8000);app.on('pageerror',lambda error:errors.append(str(error)));app.goto(base+'/index.html');app.wait_for_timeout(700)
   remote=browser.new_context();overlay=remote.new_page();overlay.set_default_timeout(8000);overlay.on('pageerror',lambda error:errors.append(str(error)));overlay.goto(base+'/?p=1');frame=overlay.locator('.widget[data-id="frame"] .webcam-frame');frame.wait_for(state='attached')
   record('Legacy webcam theme and border width render directly on Overlay',frame.evaluate('frame=>getComputedStyle(frame).borderTopWidth==="12px" && getComputedStyle(frame).borderTopColor==="rgb(0, 212, 255)"'))
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.wait_for_load_state('domcontentloaded');composer.on('pageerror',lambda error:errors.append(str(error)));composer.locator('#widget-frame .btn-widget-gear').click();composer.locator('#compWebcamTheme').select_option('simple-black');composer.locator('#compWebcamBorderWidth').fill('7');composer.locator('#compWebcamBorderWidth').press('Tab')
   overlay.wait_for_function("(()=>{const frame=document.querySelector('.widget[data-id=\"frame\"] .webcam-frame');return getComputedStyle(frame).borderTopWidth==='7px' && getComputedStyle(frame).borderTopColor==='rgb(0, 0, 0)';})()")
   record('Actual theme and border controls update independent Overlay',True)
   composer.locator('#compWebcamRatio').select_option('9:16');overlay.wait_for_function("document.querySelector('.widget[data-id=\"frame\"]').style.height==='711px'");record('Webcam ratio control updates actual frame geometry',True)
   composer.locator('#compWebcamTheme').select_option('none');overlay.wait_for_function("getComputedStyle(document.querySelector('.widget[data-id=\"frame\"] .webcam-frame')).borderTopStyle==='none'");record('No-frame theme removes frame',True)
   saved=launch_dev.get_layout()['pages'][0]['widgets'][0];record('Webcam values persist in profile',saved['webcamTheme']=='none' and saved['borderWidth']==7 and saved['webcam_ratio']=='9:16')
   record('No fake camera capture controls or JavaScript errors',composer.locator('#btnDemoWebcamRec,#btnDemoWebcamAudio').count()==0 and not errors);browser.close()
 finally:
  server.shutdown();server.server_close();record('Production layout unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'webcam-widgets.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
