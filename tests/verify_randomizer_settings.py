import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
# Randomizer v2: single-page settings, shared renderer (randomizer_visual.js), live demo, announce and persistence.
with tempfile.TemporaryDirectory(prefix='bp3-rand-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 BASE=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1400,'height':950});page=ctx.new_page()
   errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   page.goto(BASE+'/index.html',wait_until='domcontentloaded'); page.wait_for_timeout(2000)
   page.evaluate("window._autoPopoutWindows=false;openToolWindow('randomizer')"); page.wait_for_timeout(600)
   obs=ctx.new_page()
   obs.goto(BASE+'/composer.html',wait_until='domcontentloaded'); obs.wait_for_timeout(1500)
   # pick style, theme, scale, anchor on the real page
   page.click('label.rz-opt:has(input[value="flip"])'); page.click('label.rz-opt:has(input[value="ocean"])'); page.click('label.rz-opt:has(input[value="top-right"])')
   page.click('label.rz-opt:has(input[name="randSpeed"][value="2"])')
   page.fill('#randScaleNum','60'); page.select_option('#randHold','3')
   page.fill('#randItemsText','Alpha\nBeta\nGamma')
   # demo on -> OBS shows idle overlay, resize applies without restart
   page.click('#btnRandDemo'); obs.wait_for_selector('#on-demand-randomizer-overlay',state='attached',timeout=5000)
   w1=obs.evaluate("document.getElementById('on-demand-randomizer-overlay').getBoundingClientRect().width")
   page.fill('#randScaleNum','120'); obs.wait_for_function("document.getElementById('on-demand-randomizer-overlay').getBoundingClientRect().width>700",timeout=5000)
   w2=obs.evaluate("document.getElementById('on-demand-randomizer-overlay').getBoundingClientRect().width")
   assert round(w1)==384 and round(w2)==768,(w1,w2)
   assert obs.locator('#on-demand-randomizer-overlay[data-randomizer-mode=flip]').count()==1
   # real spin: demo is replaced, result shown, overlay gone after hold
   page.click('#btnRandRun'); obs.wait_for_function("document.querySelector('.bp3rz-winner.show')",timeout=6000)
   winner=obs.inner_text('.bp3rz-winner-name'); assert winner in ('Alpha','Beta','Gamma'),winner
   assert page.get_attribute('#btnRandDemo','aria-pressed')=='false'
   page.wait_for_function("document.getElementById('randWinnerResult').textContent.includes('ผลการสุ่มล่าสุด')",timeout=6000)
   assert obs.evaluate("document.querySelector('.bp3rz-sr').textContent").endswith(winner)
   obs.wait_for_function("!document.querySelector('.bp3rz-root')",timeout=8000)
   assert obs.evaluate("document.getAnimations().length")==0
   # removed from list, settings persisted
   left=page.input_value('#randItemsText').split('\n'); assert len(left)==2 and winner not in left,left
   page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(1500)
   page.evaluate("window._autoPopoutWindows=false;openToolWindow('randomizer')"); page.wait_for_timeout(500)
   got=page.evaluate("[document.querySelector('input[name=randStyle]:checked').value,document.querySelector('input[name=randTheme]:checked').value,document.querySelector('input[name=randAnchorPos]:checked').value,document.getElementById('randScaleNum').value,document.getElementById('randHold').value]")
   assert got==['flip','ocean','top-right','120','3'],got
   # empty list is reported inline, nothing is sent
   page.fill('#randItemsText',''); page.click('#btnRandRun'); page.wait_for_timeout(300)
   assert 'ยังไม่มีตัวเลือก' in page.inner_text('#randItemsError')
   assert errs==[],errs

   print('PASS randomizer v2: settings, live demo resize, spin result, announce, persistence');browser.close()
 finally:server.shutdown();server.server_close()
