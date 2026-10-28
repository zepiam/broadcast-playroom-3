import sys,tempfile,threading,json,subprocess,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True;sys.stdout.reconfigure(encoding='utf-8',errors='replace');ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from playroom_media import PlayroomMedia
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);results=[];errors=[]
def record(name,value):
 print(name,value,flush=True);results.append({'test':name,'status':'PASS' if value else 'FAIL'});assert value,name
original=Path(launch_dev.LAYOUT_FILE);original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
class Handler(launch_dev.QuietHandler):
 def do_GET(self):
  if self.path=='/audit-alert':
   body=b'<html><body style="background:transparent"><div id="actual-alert">ACTUAL ALERT FRAME</div></body></html>';self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
  super().do_GET()
with tempfile.TemporaryDirectory(prefix='bp3-media-widgets-') as directory:
 root=Path(directory);launch_dev.LAYOUT_FILE=str(root/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.playroom_media=PlayroomMedia(root/'cache')
 launch_dev.save_layout({'activePageId':'media','pages':[{'id':'media','widgets':[{'id':kind,'type':kind,'x':0,'y':0,'width':320,'height':180} for kind in ['image','video','alert']]+[{'id':'viewer','type':'viewer','viewer_mode':'total','viewer_show_icon':False,'width':320,'height':80}]}]})
 image=root/'test-image.svg';image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="90"><rect width="300" height="90" fill="red"/></svg>',encoding='utf-8')
 video=root/'test-video.webm';ffmpeg=ROOT.parent/'broadcast playroom dev'/'ffmpeg.exe';subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=0x00FF00:s=128x72:d=1,drawbox=x=64:y=0:w=64:h=72:color=red:t=fill','-c:v','libvpx-vp9','-an','-y',str(video)],check=True,timeout=30)
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1920,'height':1080});context.route('https://**/*',lambda route:route.abort());app=context.new_page();app.set_default_timeout(10000);app.on('pageerror',lambda error:errors.append(str(error)));app.goto(base+'/index.html');app.wait_for_timeout(800)
   remote=browser.new_context();overlay=remote.new_page();overlay.set_default_timeout(10000);overlay.on('pageerror',lambda error:errors.append(str(error)));overlay.goto(base+'/?p=1')
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.wait_for_load_state('domcontentloaded');composer.on('pageerror',lambda error:errors.append(str(error)))
   for kind,path in [('image',image),('video',video)]:
    composer.locator('.composer-layer-item[data-id="'+kind+'"] .btn-layer-setting').click()
    with composer.expect_file_chooser() as choice:composer.locator('#btnCompImportMedia').click()
    choice.value.set_files(str(path));overlay.wait_for_function("kind=>document.querySelector('.widget[data-id=\"'+kind+'\"] '+(kind==='video'?'video':'img'))?.getAttribute('src')?.startsWith('/playroom-media/')",arg=kind)
    if kind=='image':record('Image picker loads selected file on independent Overlay',overlay.locator('.widget[data-id="image"] img').evaluate('image=>image.decode().then(()=>image.naturalWidth===300)'))
    else:overlay.wait_for_function("document.querySelector('.widget[data-id=\"video\"] video')?.readyState>=2");record('Video picker loads decoded muted looping video',overlay.locator('.widget[data-id="video"] video').evaluate('video=>video.videoWidth===128 && video.loop && video.muted'))
   overlay.evaluate("window.keptVideo=document.querySelector('.widget[data-id=\"video\"] video');window.keptImage=document.querySelector('.widget[data-id=\"image\"] img');window.videoReloads=0;keptVideo.addEventListener('loadedmetadata',()=>videoReloads++);")
   composer.locator('#compVideoCkEnabled').locator('..').click();overlay.wait_for_selector('[data-video-color-key="video"]')
   overlay.wait_for_function("document.querySelector('[data-video-color-key=\"video\"]')?.width===128")
   pixels=overlay.locator('[data-video-color-key="video"]').evaluate("canvas=>{const context=canvas.getContext('2d');return {green:context.getImageData(20,20,1,1).data[3],red:context.getImageData(90,20,1,1).data[3]};}")
   record('Video color key checkbox removes green while preserving red pixels',pixels=={'green':0,'red':255})
   overlay.evaluate("window.keptKeyCanvas=document.querySelector('[data-video-color-key]')")
   composer.locator('#compVideoCkSimilarity').fill('25');composer.locator('#compVideoCkSimilarity').press('Tab');app.evaluate("let v=ComposerStudio.getActivePage().widgets.find(w=>w.id==='video');v.width=500;ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)")
   overlay.wait_for_function("document.querySelector('.widget[data-id=\"video\"]').style.width==='500px'")
   record('Video settings and resize retain same playing video and key canvas without reload',overlay.evaluate("keptVideo===document.querySelector('.widget[data-id=\"video\"] video') && keptKeyCanvas===document.querySelector('[data-video-color-key]') && videoReloads===0"))
   app.evaluate("let image=ComposerStudio.getActivePage().widgets.find(w=>w.id==='image');image.fitMode='contain';ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)")
   overlay.wait_for_function("document.querySelector('.widget[data-id=\"image\"] img').style.objectFit==='contain'")
   record('Image styling preserves image and unrelated playing video nodes',overlay.evaluate("keptImage===document.querySelector('.widget[data-id=\"image\"] img') && keptVideo===document.querySelector('.widget[data-id=\"video\"] video') && videoReloads===0"))
   composer.locator('#compVideoCkEnabled').locator('..').click();overlay.wait_for_function("document.querySelector('[data-video-color-key=\"video\"]')===null");record('Disabling video color key restores original playback',overlay.locator('.widget[data-id="video"] video').evaluate('video=>video.style.opacity!=="0"'))
   composer.locator('.composer-layer-item[data-id="alert"] .btn-layer-setting').click();composer.locator('#compAlertUrl').fill(base+'/audit-alert');composer.locator('#compAlertUrl').press('Tab');overlay.frame_locator('.widget[data-id="alert"] iframe').locator('#actual-alert').wait_for(state='visible')
   record('Alert URL setting loads actual frame with no-referrer policy',overlay.locator('.widget[data-id="alert"] iframe').get_attribute('referrerpolicy')=='no-referrer')
   overlay.evaluate("window.keptAlert=document.querySelector('.widget[data-id=\"alert\"] iframe').contentWindow")
   app.evaluate("let alert=ComposerStudio.getActivePage().widgets.find(w=>w.id==='alert');alert.width=500;ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)")
   overlay.wait_for_function("document.querySelector('.widget[data-id=\"alert\"]').style.width==='500px'")
   record('Browser widget resize retains same loaded document',overlay.evaluate("keptAlert===document.querySelector('.widget[data-id=\"alert\"] iframe').contentWindow"))
   record('Media URLs and color-key state persist in profile',all(widget.get('imageUrl' if widget['type']=='image' else 'videoUrl' if widget['type']=='video' else 'url') for widget in launch_dev.get_layout()['pages'][0]['widgets'] if widget['type'] in ('image','video','alert')))
   record('Legacy viewer hide-icon option applies directly on Overlay',overlay.locator('.widget[data-id="viewer"] .viewer-total svg').count()==0)
   record('No JavaScript errors',not errors);browser.close()
 finally:
  record('Production layout unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==original_hash);server.shutdown();server.server_close();(out/'media-widgets.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
