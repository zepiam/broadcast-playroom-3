"""Smoke-test the frozen backend and actual Game Overlay settings UI in an isolated profile."""
import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
import psutil
from playwright.sync_api import sync_playwright

exe=Path(sys.argv[1]).resolve(); edition=sys.argv[2]
with tempfile.TemporaryDirectory(prefix='bp3-game-package-') as tmp:
 env=dict(os.environ,LOCALAPPDATA=tmp,USERPROFILE=tmp,HOME=tmp)
 out=Path(tmp)/'app.log'
 with out.open('w',encoding='utf-8') as log:
  process=subprocess.Popen([str(exe)],cwd=tmp,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  try:
   deadline=time.monotonic()+90
   while time.monotonic()<deadline:
    if process.poll() is not None:raise RuntimeError('Packaged app exited: '+out.read_text(encoding='utf-8',errors='replace')[-3000:])
    try:
     with urllib.request.urlopen('http://127.0.0.1:8801/api/app-instance',timeout=2) as response: state=json.load(response)
     if state.get('edition')==edition:break
    except (OSError,ValueError):pass
    time.sleep(.5)
   else:raise RuntimeError('Timed out starting packaged app')
   with sync_playwright() as p:
    browser=p.chromium.launch();ctx=browser.new_context();page=ctx.new_page();page.goto('http://127.0.0.1:8801/index.html')
    assert page.locator('.topbar').evaluate("e=>getComputedStyle(e).display")=='flex'
    styles=page.locator('link[rel="stylesheet"][href^="./assets/"]');assert styles.count()>=2
    assert all(styles.nth(i).evaluate('e=>!!e.sheet') for i in range(styles.count()))
    with ctx.expect_page() as opened:page.evaluate('openDesktopOverlaySettings()')
    pop=opened.value;pop.locator('#gameChatCustomizer .game-chat-mode').first.wait_for()
    pop.locator('.game-chat-mode').filter(has_text='Theme').click();pop.locator('#gameChatTheme').select_option('neon')
    page.wait_for_function("fetch('/game-chat-config').then(r=>r.json()).then(c=>c.theme==='neon')")
    pop.locator('.game-chat-mode').filter(has_text='Default').click()
    page.wait_for_function("fetch('/game-chat-config').then(r=>r.json()).then(c=>c.theme==='default')")
    with pop.expect_event('close'):pop.locator('.floating-footer button').filter(has_text='ปิดหน้าต่าง').click()
    browser.close()
   print('PASS packaged',edition,'Game Overlay popup and theme switching')
   if os.environ.get('BP3_NATIVE_TEST')=='1':
    base='http://127.0.0.1:8801'
    def post(kind,action):
     request=urllib.request.Request(base+'/api/desktop-overlays',data=json.dumps({'kind':kind,'action':action}).encode(),headers={'Content-Type':'application/json'},method='POST')
     with urllib.request.urlopen(request,timeout=8) as response:return json.load(response)
    def ready(kind):
     deadline=time.monotonic()+30
     while time.monotonic()<deadline:
      with urllib.request.urlopen(base+'/api/desktop-overlays',timeout=3) as response: data=json.load(response)
      if any(item['kind']==kind and item.get('ready') for item in data['instances']):return
      time.sleep(.2)
     raise RuntimeError('Packaged native '+kind+' window did not become ready')
    post('game','toggle');ready('game');post('game','demo');post('game','demo')
    post('viewer','toggle');ready('viewer');post('viewer','stop');post('game','stop')
    print('PASS packaged',edition,'native Qt Game/Viewer and demo start/stop')
  finally:
   try:
    owned=psutil.Process(process.pid);children=owned.children(recursive=True);owned.terminate()
    for child in children:
     try:child.terminate()
     except psutil.Error:pass
    psutil.wait_procs([owned,*children],timeout=8)
   except psutil.Error:pass
