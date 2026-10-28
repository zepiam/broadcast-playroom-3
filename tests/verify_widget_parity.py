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
with tempfile.TemporaryDirectory(prefix='bp3-parity-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None
 widgets=[{'id':mode,'type':'chat','chatMode':mode,'width':600,'height':400,'x':0,'y':0,'fontSize':20,'autoHide':False} for mode in ['default','balloon','danmaku','character']]+[{'id':'viewer','type':'viewer','width':400,'height':180,'viewerDirection':'vertical','viewerAlign':'right'},{'id':'clock','type':'clock','width':300,'height':100,'clockTheme':'neon','clockFormat':'HH:MM:SS'},{'id':'replie','type':'replie','width':1920,'height':1080}]
 launch_dev.save_layout({'activePageId':'parity','pages':[{'id':'parity','widgets':widgets}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1280,'height':850});context.route('https://**/*',lambda r:r.abort());context.add_init_script("if(location.protocol==='http:')localStorage.setItem('bp3_master_tts','false')");context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e.stack))));app=context.new_page();app.set_default_timeout(10000);app.goto(base+'/index.html')
   with app.expect_popup() as info:app.locator('#btnRailComposer').click()
   composer=info.value;composer.set_default_timeout(8000);composer.wait_for_load_state('domcontentloaded');composer.wait_for_selector('#legacyChat_default');obs=browser.new_page();obs.on('pageerror',lambda e:errors.append(str(e.stack)));obs.on('framedetached',lambda f:print('OBS FRAME DETACHED',f.url,flush=True));obs.goto(base+'/?p=1');obs.wait_for_selector('#legacyChat_default')
   for p in [composer,obs]:
    for mode in ['default','balloon','danmaku','character']:p.frame_locator('#legacyChat_'+mode).locator('#chat').wait_for(state='attached')
   app.evaluate("sendSingleSimulatedChat('same-demo-hello')");app.wait_for_function("document.getElementById('chatList').textContent.includes('same-demo-hello')")
   for mode in ['default','balloon','danmaku','character']:
    for label,p in [('Composer',composer),('OBS',obs)]:
     p.frame_locator('#legacyChat_'+mode).locator('#chat').filter(has_text='same-demo-hello').wait_for(state='attached',timeout=10000)
     check(label+' '+mode+' receives same demo text',True)
   check('Default platform icon is an image',obs.frame_locator('#legacyChat_default').locator('img.platform-logo, img.logo').count()>0)
   app.evaluate("window.chatFrameBefore=document.getElementById('legacyChat_default').contentWindow;let w=ComposerStudio.getActivePage().widgets.find(w=>w.id==='viewer');w.viewerTheme='gold';ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)")
   app.wait_for_timeout(800);check('Editing Viewer preserves actual chat iframe and text',app.evaluate("chatFrameBefore===document.getElementById('legacyChat_default').contentWindow") and composer.frame_locator('#legacyChat_default').locator('#chat').inner_text().find('same-demo-hello')>=0)
   app.evaluate("let w=ComposerStudio.getActivePage().widgets.find(w=>w.id==='default');w.chatTheme='neon';w.chatMode='theme';w.fontSize=33;w.fontFamily='Tahoma';ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)")
   for label,p in [('Composer',composer),('OBS',obs)]:
    frame=p.frame_locator('#legacyChat_default');frame.locator('html').evaluate("e=>e.dataset.audit='yes'");p.wait_for_timeout(900)
    style=frame.locator('.text').first.evaluate("e=>({size:getComputedStyle(e).fontSize,font:getComputedStyle(e).fontFamily})")
    print(label,style,frame.locator('html').evaluate("e=>({root:getComputedStyle(e).getPropertyValue('--font-size'),body:getComputedStyle(document.body).fontFamily,config:config.font_size})"),flush=True)
    check(label+' theme edits retain text and update font',style['size']=='33px' and 'Tahoma' in style['font'])
   app.screenshot(path=str(out/'parity-main.png'));composer.screenshot(path=str(out/'parity-composer.png'),timeout=8000);obs.screenshot(path=str(out/'parity-obs.png'),timeout=8000)
   def settings(wid):
    close=composer.locator('#btnCompCloseSetting')
    if close.is_visible():close.click();composer.wait_for_timeout(200)
    composer.locator('.composer-layer-item[data-id="'+wid+'"] .btn-layer-setting').click()
   def frame(p,mode):return p.locator('#legacyChat_'+mode).element_handle().content_frame()
   def config(p,mode,key,value):
    try:frame(p,mode).wait_for_function('(pair)=>config[pair[0]]===pair[1]',arg=[key,value],timeout=5000)
    except Exception:
     print('CONFIG FAILURE',p.url,mode,key,value,p.locator('#obsCanvasStage').count(),p.locator('iframe').evaluate_all('(els)=>els.map(e=>({id:e.id,src:e.src}))'),flush=True);raise
   app.evaluate("window.keepNodes=[document.getElementById('widget-clock'),document.querySelector('#widget-clock .clock-time'),document.getElementById('widget-viewer'),document.getElementById('legacyChat_default').contentWindow]")
   obs.evaluate("window.keepChat=document.getElementById('legacyChat_default').contentWindow;window.keepClock=document.querySelector('.type-clock .clock-time')")
   settings('default');composer.locator('#cwcFontSize').focus();composer.locator('#cwcFontSize').press('ArrowRight');print('FONT CONTROL',composer.locator('#cwcFontSize').input_value(),app.evaluate("ComposerStudio.getActivePage().widgets.find(w=>w.id==='default').fontSize"),frame(composer,'default').evaluate('config.font_size'),flush=True);config(composer,'default','font_size',34);config(obs,'default','font_size',34);check('Actual Customizer font control updates existing text in both views',True)
   composer.locator('#cwcBoxRadius').focus();composer.locator('#cwcBoxRadius').press('ArrowRight');app.wait_for_timeout(500)
   expected=app.evaluate("ComposerStudio.getActivePage().widgets.find(w=>w.id==='default').boxRadius")
   config(composer,'default','box_radius',expected);check('Theme box radius control actually changes existing box',frame(composer,'default').locator('.msg').first.evaluate('(e)=>getComputedStyle(e).borderRadius')==str(expected)+'px')
   composer.locator('#cwcLayout').select_option('stacked');config(composer,'default','layout','stacked');check('Layout updates existing message structure',frame(composer,'default').locator('.msg .stack-header').first.evaluate('(e)=>getComputedStyle(e).display')=='block')
   composer.locator('#tabSubTheme').click();check('Chat Theme cards show English names only',composer.locator('#cwcPresetsGrid .cwc-preset-card').evaluate_all('(cards)=>cards.every(c=>!/[ก-๙]/.test(c.textContent))'))
   composer.locator('[data-chat-theme="neon"]').click();config(composer,'default','theme','neon');config(obs,'default','theme','neon')
   app.wait_for_timeout(300);backgrounds=[frame(p,'default').locator('.msg-bg').first.evaluate('(e)=>getComputedStyle(e).backgroundColor') for p in [composer,obs]]
   check('Theme picker applies identical actual theme background without losing messages',backgrounds[0]==backgrounds[1] and backgrounds[0]!='rgba(30, 31, 34, 0.85)' and '20, 10, 40' in backgrounds[0])
   composer.locator('#tabSubStandard').click();config(composer,'default','theme','default');config(obs,'default','theme','default');check('Chat returns to Default in both views',True)
   composer.locator('#tabSubTheme').click();config(composer,'default','theme','neon');config(obs,'default','theme','neon');check('Chat returns to saved Theme in both views',True)
   settings('clock');composer.locator('#tabClockStyle').click()
   for p in [composer,obs]:p.locator('.type-clock .dot-wait').wait_for(state='attached');check('Dot clock restores pixel triangle '+p.url,p.locator('.type-clock .dot-wait').inner_text()=='▼')
   composer.locator('#tabClockTheme').click();composer.locator('#compClockTheme').select_option('gold')
   for p in [composer,obs]:p.locator('.type-clock .clock-theme-gold').wait_for(state='attached');check('Clock switches back to selected Theme '+p.url,p.locator('.type-clock .dot-wait').count()==0)
   composer.locator('#compClockTheme').select_option('neon')
   settings('danmaku');composer.locator('#cwcSliderFontSize').focus();composer.locator('#cwcSliderFontSize').press('ArrowRight');config(composer,'danmaku','slider_font_size',21);config(obs,'danmaku','slider_font_size',21);check('Actual Danmaku size control updates both views',True)
   settings('balloon');composer.locator('#cwcBalloonFontSize').focus();composer.locator('#cwcBalloonFontSize').press('ArrowRight');config(composer,'balloon','balloon_font_size',21);config(obs,'balloon','balloon_font_size',21);check('Actual Balloon font control updates both views',True)
   settings('character');composer.locator('#cwcCharFontSize').focus();composer.locator('#cwcCharFontSize').press('ArrowRight');config(composer,'character','character_font_size',16);config(obs,'character','character_font_size',16);check('Actual Character font control updates both views',True)
   settings('viewer');check('Manual platform checkboxes removed',composer.locator('[id^="compViewerPlatform_"]').count()==0)
   launch_dev.chat_bridge._statuses['twitch'].update(connected=True,viewers=37);launch_dev.chat_bridge._statuses['mylive'].update(connected=True,viewers=0);launch_dev.chat_bridge._publish_viewers()
   for p in [composer,obs]:p.locator('.type-viewer .viewer-chip[data-platform="twitch"]').wait_for(state='visible');p.locator('.type-viewer .viewer-chip[data-platform="mylive"]').wait_for(state='visible')
   check('Viewer shows connected platforms including zero viewers, hides disconnected',composer.locator('.type-viewer .viewer-chip[data-platform="youtube"]').is_hidden() and obs.locator('.type-viewer .viewer-chip[data-platform="youtube"]').is_hidden())
   positions=[]
   for align in ['left','center','right']:
    composer.locator('#compViewerAlign').select_option(align);composer.wait_for_timeout(100);positions.append(composer.locator('.type-viewer .widget-type-viewer').evaluate('(e)=>{const a=e.querySelector(".viewer-total").getBoundingClientRect(),b=e.getBoundingClientRect();return a.x-b.x}'))
   check('Vertical Viewer left/center/right align across horizontal axis',positions[0]<positions[1]<positions[2])
   check('Unrelated clock and chat DOM identities remain unchanged',app.evaluate("keepNodes[0]===document.getElementById('widget-clock') && keepNodes[1]===document.querySelector('#widget-clock .clock-time') && keepNodes[2]===document.getElementById('widget-viewer') && keepNodes[3]===document.getElementById('legacyChat_default').contentWindow"))
   app.evaluate("let w=ComposerStudio.getActivePage().widgets.find(w=>w.id==='viewer');w.width+=80;ComposerStudio.renderCanvasWidgets();ComposerStudio.saveState(true)");app.wait_for_timeout(800)
   check('Resize preserves selected Viewer and independent OBS clock/chat nodes',app.evaluate("keepNodes[2]===document.getElementById('widget-viewer')") and obs.evaluate("keepClock===document.querySelector('.type-clock .clock-time') && keepChat===document.getElementById('legacyChat_default').contentWindow"))
   check('Clock decoration has one theme layer in Composer and OBS',composer.locator('#widget-clock .clock-theme-neon').count()==1 and obs.locator('.type-clock .clock-theme-neon').count()==1)
   check('Replie layer fixed fullscreen with no resize handles',composer.locator('#widget-replie').evaluate('(e)=>e.style.width==="1920px" && e.style.height==="1080px" && !e.querySelector(".composer-resize-handle")'))
   if composer.locator('#btnCompCloseSetting').is_visible():composer.locator('#btnCompCloseSetting').click()
   app.evaluate("()=>{for(let i=0;i<35;i++)injectIncomingChat({id:'scroll-'+i,demo:true,username:'[DEMO] Scroll',text:'scroll message '+i,platform:'Twitch',avatar:'',icon:''})}")
   app.locator('#chatList').evaluate('(e)=>e.scrollTop=100');top=app.locator('#chatList').evaluate('(e)=>e.scrollTop');app.evaluate("sendSingleSimulatedChat('while-reading')");app.wait_for_timeout(200)
   check('New chat does not force reader back to bottom',abs(app.locator('#chatList').evaluate('(e)=>e.scrollTop')-top)<3 and app.locator('#btnChatLatest').is_visible())
   app.locator('#btnChatLatest').click();check('Latest button resumes following bottom',app.locator('#chatList').evaluate('(e)=>e.scrollHeight-e.clientHeight-e.scrollTop<3'))
   with app.expect_popup() as replie_info:app.locator('#btnRailReplie').click()
   tool=replie_info.value;tool.wait_for_load_state('domcontentloaded');tool.locator('#paneReplieTab1 button.primary').click();tool.locator('#replieEdit_command').fill('!parity');tool.locator('#replieEdit_mode').select_option('combo');tool.locator('#replieEdit_ticker_text').fill('PARITY COMBO');tool.locator('#replieEdit_image_image_url').fill(base+'/assets/legacy_character.png');tool.locator('#replieEdit_duration_sec').fill('15');tool.locator('#replieCommandEditor button[type="submit"]').click();tool.locator('#replieCommandEditor').wait_for(state='detached')
   tool.locator('tr').filter(has_text='!parity').get_by_role('button',name='▶ DEMO',exact=True).click();obs.locator('.replie-wrapper').first.wait_for();composer.locator('.replie-wrapper').first.wait_for();check('Replie Combo command renders original text and image in both views',obs.locator('.replie-card-image').count()>0 and 'PARITY COMBO' in obs.locator('#obsCanvasStage').inner_text() and 'PARITY COMBO' in composer.locator('#composerCanvasStage').inner_text())
   dock=browser.new_page(viewport={'width':500,'height':1000});dock.on('pageerror',lambda e:errors.append(str(e.stack)));dock.goto(base+'/dock.html');dock.locator('#connText').filter(has_text='Online').wait_for();check('Original Dock modules restored and connected',dock.locator('#mod_tts_chat').count()==1 and dock.locator('#mod_replie').count()==1)
   dock.locator('#btnTtsToggle').click();app.wait_for_function('_masterTtsEnabled===true');check('Original Dock TTS button changes actual app state',True);dock.locator('#btnTtsToggle').click();app.wait_for_function('_masterTtsEnabled===false')
   app.evaluate("sendSingleSimulatedChat('dock-sync-message')");dock.locator('#liveChatMessages').filter(has_text='dock-sync-message').wait_for();check('Original Dock live chat follows shared messages',True)
   app.evaluate("injectIncomingChat({id:'emote-only',demo:true,username:'EmoteTest',platform:'Twitch',text:'Kappa',raw_text:'Kappa',twitch_emotes:[{start:0,end:4,url:'/assets/legacy_character.png',name:'Kappa'}],avatar:'',icon:''})")
   dock.locator('[data-msg-id="emote-only"] .live-chat-emote').wait_for();row=app.locator('[data-message-id="emote-only"]');check('Emote image renders in main chat and Dock without TTS badge',row.locator('.live-chat-emote').count()==1 and row.locator('.chat-tts-time').count()==0)
   check('Dock chat uses logo and separate message line',dock.locator('[data-msg-id="emote-only"] .chat-heading img').count()==1 and dock.locator('[data-msg-id="emote-only"] .chat-text img').count()==1)
   dock.locator('.replie-status-pill').first.wait_for();check('Dock Replie toggle has a label',bool(dock.locator('.replie-status-pill').first.inner_text().strip()))
   dock.screenshot(path=str(out/'parity-dock.png'),timeout=8000)
   saved=app.evaluate("async()=>{const w=ComposerStudio.getActivePage().widgets.find(w=>w.id==='default'),writes=[];for(const size of [29,30,31]){w.fontSize=size;ComposerStudio.renderCanvasWidgets();writes.push(ComposerStudio.saveState(true));}await Promise.all(writes);return (await (await fetch('/api/composer/layout')).json()).pages[0].widgets.find(w=>w.id==='default').fontSize}")
   check('Rapid setting saves retain latest value on server',saved==31)
   before_clock=obs.locator('.type-clock .clock-time').inner_text()
   app.evaluate("async()=>{const w=ComposerStudio.getActivePage().widgets.find(w=>w.id==='viewer');for(let i=0;i<7;i++){w.opacity=.9+i*.01;ComposerStudio.renderCanvasWidgets();await ComposerStudio.saveState(true);await new Promise(resolve=>setTimeout(resolve,200));}}")
   check('Clock keeps ticking during repeated edits to another widget',obs.locator('.type-clock .clock-time').inner_text()!=before_clock)
   app.evaluate("_replieCommands['!parity'].legacyPayload.is_loop=true;demoReplieAction('!parity')")
   dock.wait_for_function("async()=>{const data=await(await fetch('/api/dock/status')).json();return data.status.replie.loop_active===true}")
   check('Dock loop state reflects original Replie payload',True)
   check('No JavaScript errors',not errors);browser.close()
 finally:
  server.shutdown();server.server_close();check('Production layout unchanged',hashlib.sha256(original.read_bytes()).hexdigest()==digest);(out/'widget-parity.json').write_text(json.dumps({'results':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
