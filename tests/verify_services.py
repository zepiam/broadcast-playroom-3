import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import functools,json,threading,tempfile,urllib.request,io
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import chat_bridge as chat_module
from now_playing_service import NowPlayingService
import launch_dev
import easydonate_api
from donation_goal_service import DonationGoalService
from avatar_mic_service import AvatarMicService

class Client:
    def __init__(self,**callbacks):self.callbacks=callbacks
    def connect(self,target):self.target=target;return True
    def disconnect(self):pass
bridge=chat_module.ChatBridge()
for platform,name in [('twitch','TwitchChat'),('youtube','YouTubeChat'),('kick','KickChat'),('tiktok','TikTokChat'),('soop','SoopChat'),('mylive','MyLiveChat')]:
    original=getattr(chat_module,name)
    setattr(chat_module,name,Client)
    try:
        assert bridge.connect(platform,'https://www.twitch.tv/audit_target' if platform=='twitch' else 'audit_target')['success'],platform
        client=bridge._clients[platform]
        client.callbacks['on_viewer_count'](platform,23)
        assert bridge.get_status()[platform]['viewers']==23
        bridge.disconnect(platform)
    finally:setattr(chat_module,name,original)
print('PASS six platform button-to-client contracts (network fixtures)')
class Watcher:
    def __init__(self,**callbacks):self.callbacks=callbacks
    def set_source_filter(self,source):self.source=source
    def start(self):pass
    def stop(self):pass
service=NowPlayingService(Watcher)
launch_dev.now_playing_service=service
launch_dev.donation_goal_service=DonationGoalService()
class Mic:
    def __init__(self,on_level,**kwargs):self.on_level=on_level;self.stopped=False
    def start(self):self.on_level(-60);return True
    def stop(self):self.stopped=True
launch_dev.avatar_mic_service=AvatarMicService(factory=Mic)
donation_total=500
donation_count=1
class Handler(launch_dev.QuietHandler):
    def do_GET(self):
        if self.path.startswith('/audit-easy/'):
            assert self.headers.get('Authorization')=='Bearer fixture-key'
            path=self.path.split('?')[0]
            if path.endswith('/me'):data={'id':'fixture-account'}
            elif path.endswith('/breakdown'):data={'totalAmount':donation_total,'totalCount':donation_count}
            else:data={'histories':[{'donatorName':'<literal donor>','amount':250}]}
            self.send_json({'statusCode':200,'data':data});return
        super().do_GET()
with tempfile.TemporaryDirectory() as directory:
    from emote_service import EmoteService
    import base64
    cache=Path(directory)/'emotes';cache.mkdir()
    (cache/'25_1.0.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a3ioAAAAASUVORK5CYII='))
    launch_dev.emote_service=EmoteService(cache)
    launch_dev.LAYOUT_FILE=str(Path(directory)/'layout.json')
    launch_dev._LAYOUT_CACHE=None
    launch_dev.save_layout({'version':3,'activePageId':'music','pages':[{'id':'music','name':'Music','widgets':[{'id':'song','type':'now_playing','width':400,'height':100,'npSource':'spotify'},{'id':'clip','type':'playroom','width':400,'height':200},{'id':'clip-other','type':'playroom','width':400,'height':200}]+[dict(id=mode,type='chat',chatMode=mode,width=600,height=200,maxMessages=2,hideTimeout=1,speed=1) for mode in ['default','balloon','character','danmaku']]+[dict(id='emotes',type='emote_party',width=600,height=200,epDuration=1)]+[dict(id='text-'+mode,type='text',text_mode=mode,text_content='First legacy line\nSecond legacy line' if mode=='schedule' else '<literal legacy text>',text_interval=1,width=400,height=80) for mode in ['static','scroll','schedule']]+[dict(id='pngtuber',type='avatar',avatar_preset='man',avatar_mode='tts',avatar_breathing=False,avatar_sway=False,avatar_blink_rate=100,width=300,height=300)]+[dict(id='donation',type='donate_goal',dg_api_key='fixture-key',dg_start_amount=100,dg_goal_amount=1000,dg_goal_title='Actual donation goal',width=500,height=130)]+[dict(id='mic-tuber',type='avatar',avatar_preset='girl',avatar_mode='mic',avatar_breathing=False,avatar_sway=False,avatar_mic_threshold=-35,avatar_blink_rate=100,width=300,height=300)]+[dict(id='clock-'+style,type='clock',clockStyle=style,clockFormat='12',showSeconds=False,showDate=True,width=400,height=200) for style in ['none','dot2','fps1','ccsec1']]}]})
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    easydonate_api.BASE_URL=base+'/audit-easy';easydonate_api.POLL_INTERVAL=.1
    try:
        with sync_playwright() as play:
            browser=play.chromium.launch(headless=True)
            page=browser.new_page()
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(base+'/?p=1')
            page.wait_for_selector('.widget-type-now-playing',state='attached')
            assert not page.locator('.widget-type-now-playing').is_visible()
            service.snapshot('spotify')
            service.change('spotify','Actual session title','Actual artist','Album','',84,212,True)
            page.evaluate('BP3Live.refreshNowPlaying()')
            page.wait_for_function("document.querySelector('.np-title-text')?.textContent==='Actual session title'")
            assert page.locator('.widget-type-now-playing').is_visible()
            assert page.locator('[data-np-position]').inner_text()=='1:24'
            assert page.locator('[data-np-duration]').inner_text()=='3:32'
            service.position('spotify',100,212,False)
            page.evaluate('BP3Live.refreshNowPlaying()')
            assert not page.locator('.widget-type-now-playing').is_visible()
            service.change('spotify','<script>literal title</script>','Artist','','',0,60,True)
            page.evaluate('BP3Live.refreshNowPlaying()')
            assert page.locator('.np-title-text').inner_text()=='<script>literal title</script>'
            assert not errors,errors
            page.evaluate("BP3Live.receive({event:'PLAYROOM_PLAY_CLIP',payload:{type:'image',url:'data:image/svg+xml,'+encodeURIComponent('<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"2\" height=\"1\"><path fill=\"#00ff00\" d=\"M0 0h1v1H0z\"/><path fill=\"red\" d=\"M1 0h1v1H1z\"/></svg>'),ckEnabled:true,ckColor:'#00ff00',duration:.5}})")
            page.wait_for_function("document.querySelector('canvas[data-live-media]')?.width===2")
            pixels=page.evaluate("Array.from(document.querySelector('canvas[data-live-media]').getContext('2d').getImageData(0,0,2,1).data)")
            assert pixels[3]==0 and pixels[7]==255,pixels
            page.wait_for_timeout(800)
            assert page.locator('[data-live-media]').count()==0
            page.evaluate("""()=>{const url=color=>'data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" fill="'+color+'"/></svg>');for(const [color,target] of [['red','clip'],['blue','clip'],['lime','clip-other']])BP3Live.receive({event:'PLAYROOM_PLAY_CLIP',payload:{type:'image',url:url(color),duration:.4,targetWidgetIds:[target]}});}""")
            assert 'red' in page.locator('#compPlayroomStage_clip img[data-live-media]').get_attribute('src')
            assert 'lime' in page.locator('#compPlayroomStage_clip-other img[data-live-media]').get_attribute('src')
            page.wait_for_function("document.querySelector('#compPlayroomStage_clip img[data-live-media]')?.src.includes('blue')")
            page.wait_for_timeout(600)
            assert page.locator('[data-live-media]').count()==0
            import wave,base64
            audio=io.BytesIO()
            with wave.open(audio,'wb') as file:file.setnchannels(1);file.setsampwidth(2);file.setframerate(8000);file.writeframes(b'\0\0'*9600)
            audio_url='data:audio/wav;base64,'+base64.b64encode(audio.getvalue()).decode()
            page.evaluate("url=>BP3Live.receive({event:'PLAYROOM_PLAY_CLIP',payload:{type:'audio',url,duration:.1,vol:0,targetWidgetIds:['clip']}})",audio_url)
            page.wait_for_timeout(350)
            assert page.locator('audio[data-live-media]').count()==1
            assert page.locator('audio[data-live-media]').evaluate('(audio)=>audio.volume===0 && audio.currentTime>0')
            page.wait_for_timeout(1300)
            assert page.locator('[data-live-media]').count()==0
            print('PASS Playroom per-widget targets, independent ordered queues and actual audio end instead of image timeout')
            print('PASS Playroom chroma removes selected color, keeps red and cleans idle media')
            page.evaluate("""()=>{const widget=_overlayWidgets.find(widget=>widget.id==='clip');widget.ckEnabled=true;widget.ck_enabled=false;widget.ckColor='#00ff00';BP3Live.receive({event:'PLAYROOM_PLAY_CLIP',payload:{type:'image',url:'data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="2" height="1"><path fill="lime" d="M0 0h1v1H0z"/><path fill="red" d="M1 0h1v1H1z"/></svg>'),ckEnabled:false,duration:.5,targetWidgetIds:['clip']}});}""")
            page.wait_for_function("document.querySelector('canvas[data-live-media]')?.width===2")
            assert page.locator('canvas[data-live-media]').evaluate('canvas=>canvas.getContext("2d").getImageData(0,0,1,1).data[3]')==0
            page.wait_for_timeout(800)
            page.evaluate("()=>{const widget=_overlayWidgets.find(widget=>widget.id==='clip');delete widget.ckEnabled;delete widget.ck_enabled;delete widget.ckColor;}")
            print('PASS edited Playroom camel-case chroma setting overrides stale imported raw value')

            for mode in ['default','balloon','character','danmaku']:
                assert 'ยินดีต้อนรับ' not in page.locator(f'.widget[data-id="{mode}"]').inner_text()
            def relay(text):
                bridge._on_message('Twitch',chat_module.ChatMessage(platform='twitch',author='Actual viewer',text=text))
                launch_dev.overlay_events.publish({'event':'CHAT_MESSAGE','payload':bridge.get_messages()[-1]})
            relay('Actual chat 😀')
            page.wait_for_function("document.querySelector('#widget-balloon-feed-balloon')?.textContent.includes('Actual chat')")
            for selector in ['#widget-chat-feed-default','#widget-balloon-feed-balloon','#widget-character-feed-character','#widget-danmaku-feed-danmaku']:
                assert 'Actual chat' in page.locator(selector).inner_text(),selector
            assert page.locator('[data-live-emote]').count()==1
            page.wait_for_timeout(1300)
            assert page.locator('#widget-danmaku-feed-danmaku').inner_text()==''
            assert not page.locator('#widget-character-feed-character').is_visible()
            assert page.locator('[data-live-emote]').count()==0
            for i in range(3):relay(f'Message {i}')
            page.wait_for_function("document.querySelector('#widget-chat-feed-default')?.textContent.includes('Message 2')")
            assert page.locator('#widget-chat-feed-default > .chat-line').count()==2
            assert 'Message 0' not in page.locator('#widget-chat-feed-default').inner_text()
            launch_dev.overlay_events.publish({'event':'CHAT_CLEAR','payload':{}})
            page.wait_for_function("document.querySelector('#widget-chat-feed-default')?.children.length===0")
            assert page.locator('#widget-balloon-feed-balloon').inner_text()==''
            print('PASS actual provider message through relay into all four chat modes, emotes, caps and clear')
            assert page.locator('.widget[data-id="text-static"] .text-content').inner_text()=='<literal legacy text>'
            assert page.locator('.widget[data-id="text-scroll"] .text-content').text_content()=='<literal legacy text>'
            page.wait_for_function("document.querySelector('.widget[data-id=\"text-schedule\"] .text-line.active')?.textContent==='Second legacy line'")
            assert not errors,errors
            print('PASS legacy text static literal content, scrolling renderer and scheduled line rotation')
            page.wait_for_selector('.widget[data-id="pngtuber"] .avatar-stage .av-idle',state='visible')
            assert page.locator('.widget[data-id="pngtuber"] .avatar-stage .av-idle').evaluate('(image)=>image.complete && image.naturalWidth>0')
            launch_dev.overlay_events.publish({'event':'AVATAR_STATE','payload':{'talking':True}})
            page.wait_for_function("document.querySelector('.widget[data-id=\"pngtuber\"] .avatar-stage')?.classList.contains('avatar-anim-bounce')")
            launch_dev.overlay_events.publish({'event':'AVATAR_STATE','payload':{'talking':False}})
            page.wait_for_function("!document.querySelector('.widget[data-id=\"pngtuber\"] .avatar-stage')?.classList.contains('avatar-anim-bounce')")
            assert page.locator('.widget[data-id="pngtuber"] .avatar-stage .av-idle').is_visible()
            mic=launch_dev.avatar_mic_service.instances['mic-tuber']['watcher']
            mic.on_level(-20);mic.on_level(-20)
            page.wait_for_function("document.querySelector('.widget[data-id=\"mic-tuber\"] .avatar-stage')?.classList.contains('avatar-anim-bounce')")
            for _ in range(5):mic.on_level(-60)
            page.wait_for_function("!document.querySelector('.widget[data-id=\"mic-tuber\"] .avatar-stage')?.classList.contains('avatar-anim-bounce')")
            snapshot=launch_dev.overlay_events.read()
            avatar_ids={item['payload'].get('widget_id') for item in snapshot['events'] if item['event']=='AVATAR_STATE'}
            assert 'mic-tuber' in avatar_ids
            print('PASS configured microphone adapter loud/silent hysteresis and per-widget state snapshots (no physical microphone opened)')
            page.evaluate('BP3LegacyAvatar.dispose()')
            assert not errors,errors
            print('PASS actual bundled avatar image, speaking relay, return to idle and cleanup')
            import time
            until=time.monotonic()+5
            while time.monotonic()<until and launch_dev.donation_goal_service.snapshot().get('donation',{}).get('status')!='ready':page.wait_for_timeout(100)
            assert launch_dev.donation_goal_service.snapshot()['donation']['current']==0
            donation_total=750;donation_count=2
            page.wait_for_timeout(400)
            page.evaluate('BP3LegacyGoals.refresh()')
            page.wait_for_function("document.querySelector('.dg-amount')?.textContent.includes('350')")
            assert page.locator('.dg-title').inner_text()=='Actual donation goal'
            assert '<literal donor>' in page.locator('.dg-donor').inner_text()
            assert page.locator('.dg-bar-fill').evaluate('(node)=>node.style.width')=='35%'
            assert not errors,errors
            print('PASS legacy EasyDonate authenticated local API, baseline delta, initial amount, donor literal and progress')
            clock=page.evaluate("""()=>{const now=new Date(2026,9,26,15,4,5);for(const widget of _overlayWidgets.filter(w=>w.type==='clock'))BP3UpdateClock(document.querySelector('.widget[data-id="'+widget.id+'"]'),widget,now);return {normal:document.querySelector('[data-id="clock-none"] .clock-time').textContent,dot:document.querySelector('[data-id="clock-dot2"] .dot-time').textContent,fps:document.querySelector('[data-id="clock-fps1"] .fps-time').textContent,circle:document.querySelector('[data-id="clock-ccsec1"] .cc-t2').textContent,date:document.querySelector('[data-id="clock-none"] .clock-date').textContent};}""")
            assert clock['normal']=='3:04 PM' and clock['dot']=='2026.10.26 15:04' and clock['fps']=='15:04:05' and clock['circle']=='05' and clock['date'],clock
            print('PASS shared live clock updater for 12-hour/date, dated dots, FPS and circle seconds')
            for animation in ['float','dvd','drop','shake']:
                values=page.evaluate("""animation=>{const widget=_overlayWidgets.find(widget=>widget.id==='emotes');widget.epAnimation=animation;widget.epMaxEmotes=2;widget.epEmoteSize=62;widget.epDuration=.5;BP3LegacyEmotes.show(widget,[{text:'🔥'},{text:'⭐'},{text:'🎉'}]);return [...document.querySelectorAll('[data-live-emote]')].map(node=>({animation:node.dataset.emoteAnimation,width:node.style.width,transform:node.style.transform}));}""",animation)
                assert len(values)==2 and all(value['animation']==animation and value['width']=='62px' and value['transform'] for value in values),values
                page.wait_for_timeout(700)
                assert page.evaluate('BP3LegacyEmotes.stats()')=={'active':0,'running':False}
            page.evaluate("""()=>{const widget=_overlayWidgets.find(widget=>widget.id==='emotes');widget.epEmojiEnabled=false;BP3LegacyEmotes.show(widget,[{text:'🔥'}]);}""")
            assert page.locator('[data-live-emote]').count()==0
            bridge._on_message('Twitch',chat_module.ChatMessage(platform='twitch',author='Emote viewer',text='',extra={'emotes':[{'id':'25','name':'Kappa','start':0,'end':4}],'raw_text':'Kappa'}))
            launch_dev.overlay_events.publish({'event':'CHAT_MESSAGE','payload':bridge.get_messages()[-1]})
            page.wait_for_selector('[data-live-emote] img')
            assert page.locator('[data-live-emote] img').evaluate('image=>image.decode().then(()=>image.naturalWidth>0)')
            page.evaluate('BP3LegacyEmotes.clear()')
            assert page.evaluate('BP3LegacyEmotes.stats()')=={'active':0,'running':False}
            print('PASS original Emote Party float/DVD/drop/shake physics, max count, size, expiry/idle stop, emoji switch and actual Twitch ID image decoding from legacy cache')
            launch_dev.overlay_events.publish({'event':'CHAT_CLEAR','payload':{}})
            migrated=[dict(id='old-'+mode,type='chat',appearance_mode=mode,theme='neon' if mode=='theme' else 'default',font_size=31,font_color='#aabbcc',width=600,height=300) for mode in ['default','theme','balloon','slider','character']]
            layout=launch_dev.get_layout();layout['pages'][0]['widgets']=migrated
            launch_dev.save_layout(layout)
            legacy_page=browser.new_page();legacy_page.on('pageerror',lambda error:errors.append(str(error)))
            legacy_page.goto(base+'/?p=1')
            legacy_page.wait_for_selector('iframe[data-legacy-chat]',state='attached')
            assert legacy_page.locator('iframe[data-legacy-chat]').count()==5
            for widget in migrated:
                frame=legacy_page.frame_locator('#legacyChat_'+widget['id'])
                frame.locator('#chat').wait_for(state='attached')
                frame.locator('body').evaluate("()=>loadConfig()")
                assert frame.locator('body').evaluate("()=>config.font_size") ==31
            relay('<literal migrated chat>')
            for widget in migrated:
                frame=legacy_page.frame_locator('#legacyChat_'+widget['id'])
                frame.locator('#chat').filter(has_text='<literal migrated chat>').wait_for(state='visible')
                assert frame.locator('#chat script').count()==0
            assert legacy_page.frame_locator('#legacyChat_old-theme').locator('body').evaluate("()=>config.theme_css.length>0")
            image=legacy_page.frame_locator('#legacyChat_old-character').locator('.char-slot img.char-img')
            image.evaluate("image=>image.decode()")
            assert image.evaluate("image=>image.naturalWidth>0")
            assert legacy_page.frame_locator('#legacyChat_old-character').locator('.char-slot').count()==1
            launch_dev.overlay_events.publish({'event':'CHAT_CLEAR','payload':{}})
            for widget in migrated:
                frame=legacy_page.frame_locator('#legacyChat_'+widget['id'])
                frame.locator('body').evaluate("()=>new Promise(resolve=>{const timer=setInterval(()=>{if(!document.querySelector('#chat').children.length){clearInterval(timer);resolve();}},50);})")
            assert not errors,errors
            layout['legacyChat']={'overlay_balloon_mode':True,'overlay_font_size':29,'overlay_box_bg_opacity':0.4,'overlay_mode_configs':{'default':{'font_size':35}},'overlay_theme':'neon'}
            launch_dev.save_layout(layout)
            legacy_page.goto(base+'/legacy-chat.html')
            legacy_page.wait_for_function('typeof config!=="undefined" && config.balloon_mode')
            assert legacy_page.evaluate('config.font_size===35 && config.box_bg_opacity===0.4 && config.theme_css.length>0')
            relay('Global legacy settings')
            legacy_page.locator('#chat').filter(has_text='Global legacy settings').wait_for(state='visible')
            assert not errors,errors
            legacy_page.close()
            print('PASS migrated legacy chat uses original renderer for default/theme/balloon/slider/character, preserves font, literal text and clears all modes')
            browser.close()
        print('PASS Now Playing real API/render contract, source, times, idle, pause and literal text')
    finally:service.stop();launch_dev.donation_goal_service.stop();launch_dev.avatar_mic_service.stop();server.shutdown();server.server_close()
