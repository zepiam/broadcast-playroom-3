import sys,threading,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();page=browser.new_page();state={'connected':False,'target':'example','status':'กำลังเชื่อมต่อแชท','channel_verified':None}
  page.route('**/api/status',lambda route:route.fulfill(json={'tiktok':state}))
  page.route('**/api/connect?**',lambda route:route.fulfill(json={'success':True,'connected':False,'target':'example'}))
  page.goto(base+'/index.html');page.evaluate("setPlatformChannel('tiktok','example')");page.locator('#btn-plat-tiktok').click()
  page.wait_for_function("document.querySelector('#status-tiktok').textContent.includes('กำลัง')")
  assert not page.locator('#card-tiktok').evaluate("e=>e.classList.contains('connected')")
  state.update(connected=True,status='✅ เชื่อมต่อ TikTok @example');page.evaluate('pollPlatformStatuses()');page.wait_for_function("document.querySelector('#card-tiktok').classList.contains('connected')")
  state.update(connected=False,status='ไม่พบ user');page.evaluate('pollPlatformStatuses()');page.wait_for_function("document.querySelector('#status-tiktok').textContent.includes('ไม่พบ')")
  assert not page.locator('#card-tiktok').evaluate("e=>e.classList.contains('connected')")
  print('PASS: UI pending → connected → failure; no false connected state');browser.close()
finally:server.shutdown();server.server_close()
