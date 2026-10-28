import sys,tempfile,threading,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
out=Path(sys.argv[1]);results=[];errors=[]
def check(name,ok):
 print(name,ok,flush=True);results.append({'test':name,'status':'PASS' if ok else 'FAIL'});assert ok,name
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-layers-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':'layer'+str(i),'type':'text','title':title,'text':'LAYER '+str(i),'width':350,'height':60,'z':i+1} for i,title in enumerate(['กิจกรรมแจกของรางวัล','โพลสำรวจความคิดเห็น','แชทลอยหน้าจอ ดันมากุ','แชทตัวละคร ปาร์ตี้ธีม','หลอด (Emote Party)','นาฬิกาดิจิทัล','Playroom Studio มินิเกม','แชทสด','สุ่มด่วน (Quick Randomizer)','เพลงที่กำลังเล่น','ข้อความยาวสำหรับทดสอบการตัดบรรทัดในชื่อเลเยอร์','รูปภาพ','ชื่อยาวมากๆที่ไม่มีช่องว่างระหว่างตัวอักษรเลยสำหรับทดสอบเลเยอร์'])]
 launch_dev.save_layout({'activePageId':'layers','pages':[{'id':'layers','widgets':widgets}]});server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1280,'height':900});context.route('https://**/*',lambda r:r.abort());context.on('page',lambda page:page.on('pageerror',lambda e:errors.append(str(e))));app=context.new_page();app.goto(base+'/index.html')
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   studio=info.value;studio.set_default_timeout(6000);studio.wait_for_load_state('domcontentloaded');studio.wait_for_selector('.composer-layer-item')
   for mode in ['normal','xlarge']:
    app.evaluate('(mode)=>BP3UiText.setMode(mode)',mode);studio.wait_for_timeout(100)
    valid=studio.locator('.composer-layer-item').evaluate_all('''items=>items.every(item=>{const main=item.querySelector('.composer-layer-main'),name=item.querySelector('.composer-layer-name'),actions=item.querySelector('.composer-layer-actions'),a=main.getBoundingClientRect(),b=name.getBoundingClientRect(),c=actions.getBoundingClientRect();return b.bottom<=a.bottom+1 && c.top>=a.bottom-1 && name.scrollWidth<=name.clientWidth+1 && name.scrollHeight<=name.clientHeight+1 && item.scrollWidth<=item.clientWidth+1 && item.scrollHeight<=item.clientHeight+1 && actions.querySelectorAll('button').length===6})''')
    check(mode+' long names fit above full-width action bar',valid);studio.locator('.composer-sidebar-right').screenshot(path=str(out/f'layer-cards-{mode}.png'))
   rows=studio.locator('.composer-layer-item');check('Top up and bottom down buttons disabled and faded',rows.first.locator('[data-action=move-up]').is_disabled() and rows.last.locator('[data-action=move-down]').is_disabled() and rows.first.locator('[data-action=move-up]').evaluate('(e)=>Number(getComputedStyle(e).opacity)<.5'))
   initial=rows.evaluate_all('(items)=>items.map(e=>e.dataset.id)');app.evaluate("window.layerKeptCanvas=document.getElementById('widget-layer0')")
   rows.nth(1).locator('[data-action=move-up]').click();check('Up arrow swaps exactly one visual layer',rows.evaluate_all('(items)=>items.slice(0,2).map(e=>e.dataset.id)')==[initial[1],initial[0]])
   check('New top button immediately disables',rows.first.locator('[data-action=move-up]').is_disabled())
   rows.first.locator('[data-action=move-down]').click();check('Down arrow restores previous order',rows.evaluate_all('(items)=>items.map(e=>e.dataset.id)')==initial)
   app.wait_for_function("async()=>{const data=await(await fetch('/api/composer/layout')).json();return data.pages[0].widgets.find(w=>w.id==='layer12').z===13}")
   check('Layer order persists without replacing unrelated canvas widget',app.evaluate("layerKeptCanvas===document.getElementById('widget-layer0')"))
   # Drag within visible rows; visual top goes below the third row.
   target_box=rows.nth(2).bounding_box();rows.nth(0).drag_to(rows.nth(2),source_position={'x':10,'y':10},target_position={'x':10,'y':target_box['height']-3});order=rows.evaluate_all('(items)=>items.map(e=>e.dataset.id)');check('Drag/drop and arrow order agree',order[:3]==[initial[1],initial[2],initial[0]])
   app.evaluate("ComposerStudio.getActivePage().widgets=[ComposerStudio.getActivePage().widgets[0]];ComposerStudio.renderLayersList()")
   check('Single layer disables both arrows',rows.locator('[data-action=move-up]').is_disabled() and rows.locator('[data-action=move-down]').is_disabled())
   check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'layer-cards.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
