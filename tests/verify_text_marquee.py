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
with tempfile.TemporaryDirectory(prefix='bp3-marquee-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':name,'type':'text','title':name,'text':text,'textMode':'ticker','marqueeSpeed':5,'fontSize':28,'fontFamily':'Tahoma','width':320,'height':80,'y':i*100} for i,(name,text) in enumerate([('short','สวัสดีครับ'),('long','ข้อความยาวต้องเลื่อนออกให้ครบทั้งประโยคก่อนเริ่มรอบใหม่ '+('LONG MARQUEE MESSAGE '*6))])]
 launch_dev.save_layout({'activePageId':'marquee','pages':[{'id':'marquee','widgets':widgets}]});server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':850});context.route('https://**/*',lambda r:r.abort());context.on('page',lambda page:page.on('pageerror',lambda e:errors.append(str(e))));app=context.new_page();app.goto(base+'/index.html')
   with app.expect_popup() as opened:app.locator('#btnRailComposer').click()
   studio=opened.value;studio.wait_for_load_state('domcontentloaded');obs=browser.new_page();obs.on('pageerror',lambda e:errors.append(str(e)));obs.goto(base+'/?p=1');obs.wait_for_function("!document.documentElement.classList.contains('bp3-app-offline')");studio.wait_for_timeout(1200)
   script='''async el=>{const a=el.getAnimations().find(a=>a.animationName==='bp3MarqueeFullRun');if(!a)return {ok:false,error:'Missing shared marquee'};a.pause();const duration=Number(a.effect.getTiming().duration),box=el.parentElement.getBoundingClientRect(),width=el.getBoundingClientRect().width,head=box.width/(box.width+width);const positions=[];for(const phase of [0,head,head+(1-head)*.5,.99999,1.00001]){a.currentTime=duration*phase;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));const r=el.getBoundingClientRect();positions.push({left:r.left-box.left,right:r.right-box.left});}return {duration,width,viewport:box.width,positions,ok:Math.abs(positions[0].left-box.width)<2 && Math.abs(positions[1].left)<2 && positions[2].right>0 && positions[2].left<0 && Math.abs(positions[3].right)<2 && Math.abs(positions[4].left-box.width)<2};}'''
   for label,page in [('Composer',studio),('OBS',obs)]:
    for wid in ['short','long']:
     el=page.locator('.widget[data-id="'+wid+'"] .widget-text-ticker > span');el.wait_for(state='attached');report=el.evaluate(script);print(label,wid,json.dumps(report),flush=True);check(label+' '+wid+' exits full sentence before loop',report['ok'] and report['duration']==5000)
   check('Both views use same renderer without legacy replacement',obs.locator('.type-text .text-content').count()==0 and obs.locator('.widget-text-ticker').count()==2 and studio.locator('.widget-text-ticker').count()==2)
   obs.evaluate("window.keptSpan=document.querySelector('.widget[data-id=long] .widget-text-ticker > span');window.keptAnimation=keptSpan.getAnimations()[0]")
   app.evaluate("let w=ComposerStudio.getActivePage().widgets.find(w=>w.id==='long');w.width=500;w.fontSize=34;ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)")
   obs.wait_for_function("document.querySelector('.widget[data-id=long]').style.width==='500px'")
   check('Width/font update keeps same text and animation',obs.evaluate("keptSpan===document.querySelector('.widget[data-id=long] .widget-text-ticker > span') && keptAnimation===keptSpan.getAnimations()[0]"))
   report=obs.locator('.widget[data-id=long] .widget-text-ticker > span').evaluate(script);check('Updated text width still clears whole sentence',report['ok'])
   check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'text-marquee.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
