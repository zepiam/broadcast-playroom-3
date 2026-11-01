from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch();c=b.new_context();page=c.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8801/index.html');page.wait_for_timeout(2000)
 print('ERRORS',json.dumps(errors,ensure_ascii=True))
 print('functions',page.evaluate("Object.fromEntries(['closeToolWindow','showSettings','showContextMenu','hideContextMenu','openToolWindow'].map(n=>[n,typeof window[n]]))"))
 print('overlays',page.evaluate("[...document.querySelectorAll('[id*=modal]')].filter(e=>getComputedStyle(e).display!=='none').map(e=>({id:e.id,rect:e.getBoundingClientRect().toJSON()}))"))
 with c.expect_page() as opened:page.locator('#btnRailSettings').click()
 pop=opened.value;pop.on('pageerror',lambda e:errors.append(str(e)));pop.wait_for_load_state();pop.wait_for_timeout(500)
 print('POP FUNCTIONS',pop.evaluate("Object.fromEntries(['closeToolWindow','switchSettingsSection'].map(n=>[n,typeof window[n]]))"))
 print('POP ERRORS',json.dumps(errors,ensure_ascii=True))
 assert not errors,errors
 channel=pop.locator('#cfgTwitchChannel');channel.fill('persistence-fixture')
 page.evaluate("hidePlatform('kick')")
 page.wait_for_function("fetch('/api/platform/settings').then(r=>r.json()).then(s=>s.channel_twitch==='persistence-fixture' && s.hidden_platforms?.includes('kick'))")
 assert page.evaluate("typeof closeToolWindow==='function'")
 pop.evaluate("closeToolWindow('settings')")
 pop.wait_for_event('close') if not pop.is_closed() else None
 page.locator('#card-twitch').click(button='right')
 print('PASS Settings closed and platform right-click executed without script errors')
 fresh=b.new_context();reopened=fresh.new_page();reopened.goto('http://127.0.0.1:8801/index.html')
 reopened.wait_for_function("localStorage.getItem('bp3_channel_twitch')==='persistence-fixture'")
 reopened.wait_for_function("getComputedStyle(document.querySelector('#card-kick')).display==='none'")
 print('PASS channel and hidden platform restored in fresh browser context')
 b.close()
