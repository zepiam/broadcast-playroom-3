import sys,json,tempfile,threading,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
from playroom_media import PlayroomMedia
out=Path(sys.argv[1]);results=[];errors=[]
def record(test,value):
 print(test,value,flush=True);results.append({'test':test,'status':'PASS' if value else 'FAIL'});assert value,test
original=Path(launch_dev.LAYOUT_FILE);digest=hashlib.sha256(original.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='bp3-widget-add-') as directory:
 launch_dev.playroom_media=PlayroomMedia(Path(directory)/'cache');launch_dev.LAYOUT_FILE=str(Path(directory)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'widgets','pages':[{'id':'widgets','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1920,'height':1080});context.route('https://**/*',lambda route:route.abort());app=context.new_page();app.set_default_timeout(10000);app.on('pageerror',lambda e:errors.append(str(e)));app.goto(base+'/index.html');app.wait_for_timeout(700)
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.wait_for_load_state('domcontentloaded');composer.on('pageerror',lambda e:errors.append(str(e)));composer.locator('[data-widget-type="donate_goal"]').click()
   goal=composer.locator('.composer-widget').first;composer.locator('.composer-layer-item .btn-layer-setting').last.click();composer.locator('#compLegacy_dg_goal_title').fill('My actual goal');composer.locator('#compLegacy_dg_goal_title').press('Tab');composer.locator('#compLegacy_dg_goal_amount').fill('2000');composer.locator('#compLegacy_dg_goal_amount').press('Tab');composer.locator('#compLegacy_dg_start_amount').fill('500');composer.locator('#compLegacy_dg_start_amount').press('Tab');composer.locator('#compLegacy_dg_theme').select_option('minimal')
   remote=browser.new_context();overlay=remote.new_page();overlay.set_default_timeout(10000);overlay.on('pageerror',lambda e:errors.append(str(e)));overlay.goto(base+'/?p=1');overlay.wait_for_function("document.querySelector('.dg-title')?.textContent==='My actual goal'")
   record('Add donation goal and edit title/amount/theme through actual controls',overlay.locator('.dg-bar-fill').evaluate("e=>e.style.width==='25%'") and overlay.locator('.dg-theme-minimal').count()==1)
   record('Composer goal preview matches independent Overlay',composer.locator('.dg-title').inner_text()=='My actual goal' and composer.locator('.dg-amount').inner_text()==overlay.locator('.dg-amount').inner_text())
   composer.locator('[data-widget-type="avatar"]').click();avatar=composer.locator('.composer-widget').last;composer.locator('.composer-layer-item .btn-layer-setting').first.click(timeout=4000);overlay.wait_for_function("document.querySelector('.av-idle')?.complete && document.querySelector('.av-idle')?.naturalWidth>0")
   record('Add PNG avatar with actual bundled preset image',True)
   composer.locator('#compLegacy_avatar_preset').select_option('girl');overlay.wait_for_function("document.querySelector('.av-idle')?.src.includes('/girl/')")
   composer.locator('#compLegacy_avatar_flip_h').locator('..').click();overlay.wait_for_function("document.querySelector('.avatar-flip-wrap')?.style.transform.includes('-1')")
   record('Preset and flip controls update independent Overlay',True)
   app.evaluate("BP3_BUS.emit('AVATAR_STATE',{talking:true})");overlay.wait_for_function("document.querySelector('.avatar-stage')?.classList.contains('avatar-anim-bounce')");app.evaluate("BP3_BUS.emit('AVATAR_STATE',{talking:false})");overlay.wait_for_function("!document.querySelector('.avatar-stage')?.classList.contains('avatar-anim-bounce')")
   record('Avatar speaking relay and return to idle',True)
   with composer.expect_file_chooser() as chooser:composer.locator('#compLegacyUpload_idle').click()
   chooser.value.set_files(str(root/'src/assets/legacy_character.png'));overlay.wait_for_function("document.querySelector('.av-idle')?.src.includes('/playroom-media/') && document.querySelector('.av-idle')?.naturalWidth>0")
   record('Actual avatar image picker imports and decodes selected file',True)
   saved=launch_dev.get_layout()['pages'][0]['widgets'];record('New widget settings persist',len(saved)==2 and saved[0]['dg_start_amount']==500 and saved[1]['avatar_preset']=='')
   record('No JavaScript errors',not errors);browser.close()
 finally:
  launch_dev.avatar_mic_service.stop();launch_dev.donation_goal_service.stop();server.shutdown();server.server_close();record('Production profile unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'widget-additions.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
