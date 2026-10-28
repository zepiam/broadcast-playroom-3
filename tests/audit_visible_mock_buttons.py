import os,sys,tempfile,threading,json
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
with tempfile.TemporaryDirectory() as tmp:
 launch_dev.LAYOUT_FILE=str(Path(tmp)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'a','pages':[{'id':'a','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context();ctx.add_init_script("localStorage.setItem('bp3_master_tts','false')");page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   found=[]
   for button in ['#btnRailSettings','#btnRailAsk','#btnRailGw','#btnRailRandomizer','#btnRailReplie','#btnRailPlayroom','#btnRailUserManager','#btnRailVoiceSettings']:
    with page.expect_popup() as opened:page.locator(button).click()
    popup=opened.value;popup.wait_for_load_state();popup.wait_for_timeout(150)
    if button=='#btnRailSettings':
     for section in ['platforms','tts','chatbot','replace','ng','block','networking','obs','docks','about']:
      popup.evaluate('(section)=>switchSettingsSection(section)',section)
      found.extend(popup.evaluate("section=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent && b.onclick && /^function onclick\\(event\\) \\{\\s*showToast\\(/.test(String(b.onclick))).map(b=>({section,label:b.innerText.trim()}))",section))
    else:found.extend(popup.evaluate("()=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent && b.onclick && /^function onclick\\(event\\) \\{\\s*showToast\\(/.test(String(b.onclick))).map(b=>({section:document.title,label:b.innerText.trim()}))"))
    popup.close()
   print('VISIBLE TOAST-ONLY BUTTON CANDIDATES:',json.dumps(found,ensure_ascii=False));browser.close()
 finally:server.shutdown();server.server_close()
