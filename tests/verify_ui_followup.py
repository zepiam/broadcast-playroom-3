import sys,tempfile,threading,os
os.environ['BP3_EDITION']='lite'
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory(prefix='bp3-ui-') as temp:
 launch_dev.LAYOUT_FILE=str(Path(temp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});ctx.add_init_script("localStorage.setItem('bp3_master_tts','false')");page=ctx.new_page();page.goto(base+'/index.html')
   page.evaluate("injectIncomingChat({id:'emote-test',username:'Fixture',platform:'Kick',platform_key:'kick',avatar:'',text:'',segments:[{type:'emote',name:'Smile',url:'/assets/kick.png'}]})")
   icon=page.locator('[data-message-id="emote-test"] .plat-badge-mini img');icon.wait_for();page.wait_for_function("document.querySelector('[data-message-id=emote-test] .plat-badge-mini img').naturalWidth>0");assert icon.get_attribute('src')=='/logo/kick';print('PASS platform icon loaded')
   with page.expect_popup() as pop:page.evaluate("openAuthorModal('Fixture','Kick','','Fixture',false)")
   profile=pop.value;profile.wait_for_load_state();profile.wait_for_function("document.querySelector('#paneProfTab1')?.textContent.includes('Smile')");print('PASS history retains emote name')
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('replace')");settings.locator('button[onclick="toggleAddWordForm()"]').click();assert settings.locator('.dictionary-test-row button').count()==2
   settings.evaluate("document.getElementById('txtNewFindWord').value='original'; window.Audio=function(src){window.lastAudio=src;this.play=()=>Promise.resolve();this.pause=()=>{};}")
   page.evaluate("window.Audio=function(src){window.previewUrl=src;this.play=()=>Promise.resolve();this.pause=()=>{};}")
   settings.locator('button[onclick="previewDictionaryWord(\'txtNewFindWord\')"]').click();page.wait_for_function("window.previewUrl?.includes('preview=1') && window.previewUrl?.includes('original')");print('PASS original dictionary preview requests raw Edge TTS')
   settings.evaluate("document.getElementById('txtNewReplaceWord').value='replacement'");settings.locator('button[onclick="previewDictionaryWord(\'txtNewReplaceWord\')"]').click();page.wait_for_function("window.previewUrl?.includes('replacement')");print('PASS replacement preview')
   settings.evaluate("switchSettingsSection('ng')");assert settings.locator('#sec-ng textarea').evaluate('(e)=>e.getBoundingClientRect().height')>=180
   settings.evaluate("switchSettingsSection('secret')");assert settings.locator('#sec-secret textarea').evaluate('(e)=>e.getBoundingClientRect().height')>=180;print('PASS larger multiline fields')
   with page.expect_popup() as rand_pop:page.locator('#btnRailRandomizer').click()
   rand=rand_pop.value;rand.wait_for_load_state();assert rand.locator('#randItemsText').evaluate('(e)=>e.getBoundingClientRect().height')>=180;print('PASS larger Randomizer input')
   footer=profile.locator('.floating-footer');metrics=footer.evaluate('(e)=>{const r=e.getBoundingClientRect();return [...e.querySelectorAll("button")].every(b=>{const x=b.getBoundingClientRect();return x.top>=r.top && x.bottom<=r.bottom && x.left>=r.left && x.right<=r.right;})}');assert metrics;profile.evaluate("document.documentElement.dataset.uiTextSize='xlarge'");assert footer.evaluate('(e)=>{const r=e.getBoundingClientRect();return [...e.querySelectorAll("button")].every(b=>{const x=b.getBoundingClientRect();return x.top>=r.top && x.bottom<=r.bottom && x.left>=r.left && x.right<=r.right;})}');print('PASS footer buttons within bar at normal and larger text sizes')
   browser.close()
 finally:server.shutdown();server.server_close()
