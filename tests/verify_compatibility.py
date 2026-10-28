import sys; sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import json, threading, functools, time, traceback, urllib.parse, hashlib, os, shutil
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'work'/'compat-audit'
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'work').mkdir(exist_ok=True)
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT))
import launch_dev
from chat_twitch import ChatMessage
from tempfile import TemporaryDirectory
fixture_dir=TemporaryDirectory(prefix='bp3-audit-',dir=str(ROOT/'work'))
from playroom_media import PlayroomMedia
launch_dev.playroom_media=PlayroomMedia(Path(fixture_dir.name)/'uploaded-media')
launch_dev.LAYOUT_FILE=str(Path(fixture_dir.name)/'layout.json')
launch_dev._LAYOUT_CACHE=None
launch_dev._LAYOUT_MTIME=0
layout=json.loads((ROOT/'composer_layout.json').read_text(encoding='utf-8'))
original_hash=hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest()
layout['pages'][0]['widgets'] += [dict(id='audit-replie',type='replie',x=0,y=0,width=1920,height=1080,isFullScreen=True),dict(id='audit-playroom',type='playroom',x=0,y=0,width=1920,height=1080,isFullScreen=True)]
launch_dev.save_layout(layout)
messages=launch_dev.chat_bridge._messages
import io,wave
audio_buffer=io.BytesIO()
with wave.open(audio_buffer,'wb') as wave_file:
 wave_file.setnchannels(1);wave_file.setsampwidth(2);wave_file.setframerate(8000);wave_file.writeframes(b'\0\0'*400)
silent_audio=audio_buffer.getvalue()
tts_requests=[]
tts_backend_passthrough=False
results=[];errors=[];compat_servers=[]
class Handler(launch_dev.QuietHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  path=urllib.parse.urlparse(self.path)
  if path.path=='/api/tts' and not tts_backend_passthrough:
   tts_requests.append(urllib.parse.parse_qs(path.query).get('text',[''])[0])
   self.send_response(200);self.send_header('Content-Type','audio/wav');self.send_header('Content-Length',str(len(silent_audio)));self.end_headers();self.wfile.write(silent_audio);return
  if path.path=='/audit/image.svg':
   self.send_response(200);self.send_header('Content-Type','image/svg+xml');self.end_headers();self.wfile.write(b'<svg xmlns="http://www.w3.org/2000/svg" width="160" height="100"><rect width="160" height="100" fill="red"/></svg>');return
  data=None
  if path.path=='/api/composer/layout':data=launch_dev.get_layout()
  elif path.path=='/api/status':data={}
  elif path.path=='/api/dictionary':data={'replace_words':{}}
  elif path.path=='/api/server_status':data={'status':'online','port':self.server.server_port}
  elif path.path.startswith('/api/') and path.path not in ('/api/app-presence','/api/app-presence/stream','/api/dock/status','/api/viewer-overlay','/api/overlay/events','/api/messages','/api/tts','/api/capabilities','/api/rvc/models','/api/rvc/status','/api/rvc/catalog'):data={}
  if data is not None:
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(data).encode());return
  super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
def record(name,passed,detail=''):
 results.append(dict(test=name,status='PASS' if passed else 'FAIL',detail=detail));print(results[-1],flush=True)
def incoming(author,text):
 launch_dev.chat_bridge._on_message('Twitch',ChatMessage(platform='twitch',author=author,text=text))
def close_tool(page):
 if page.opener() is not None:
  # Detached tools use the native titlebar close button; the in-app one is hidden.
  page.close(run_before_unload=True)
  if not page.is_closed():page.wait_for_event('close')
 else:
  page.locator('.floating-header .close-red').first.click()

def shot(page,name):page.screenshot(path=str(OUT/(name+'.png')),omit_background=True,timeout=10000)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  ctx=browser.new_context(viewport={'width':1920,'height':1080})
  ctx.route('https://**/*',lambda r:r.abort())
  ctx.on('page',lambda page:page.on('pageerror',lambda error:errors.append(str(error))))
  ctx.add_init_script("if(location.protocol==='http:' && !localStorage.getItem('bp3_playroom_clips'))localStorage.setItem('bp3_playroom_clips',JSON.stringify({'!fortune':[{name:'Explicit test fixture',url:location.origin+'/audit/image.svg',type:'image',vol:85,weight:100}]}));")
  ctx.add_init_script("window.auditAudioVolumes=[];const originalPlay=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){if(this.src.includes('/api/tts'))window.auditAudioVolumes.push({volume:this.volume,url:this.src});return originalPlay.call(this);};")
  ctx.add_init_script("window.auditSpeech=[];if(window.speechSynthesis)window.speechSynthesis.speak=(u)=>window.auditSpeech.push(u.text);window.auditEvents=[];window.addEventListener('DOMContentLoaded',()=>{let b=new BroadcastChannel('bp3_system_channel');b.onmessage=e=>window.auditEvents.push(e.data)});")
  answers=[]
  ctx.on('dialog',lambda dialog: dialog.accept(answers.pop(0)) if answers else dialog.dismiss())
  app=ctx.new_page();app.on('pageerror',lambda e:errors.append(str(e)));app.goto(base+'/index.html');app.wait_for_timeout(1200)
  overlay=ctx.new_page();overlay.on('pageerror',lambda e:errors.append(str(e)));overlay.goto(base+'/composer.html?p=1');overlay.wait_for_selector('.widget',state='attached')
  remote=browser.new_context(viewport={'width':1920,'height':1080});remote.route('https://**/*',lambda r:r.abort())
  remote.on('page',lambda page:page.on('pageerror',lambda error:errors.append(str(error))))
  obs=remote.new_page();obs.goto(base+'/composer.html?p=1');obs.wait_for_selector('.widget',state='attached')
  def opened(rail):
   with app.expect_popup() as info:app.locator(rail).click()
   pop=info.value;pop.on('pageerror',lambda e:errors.append(str(e)));pop.wait_for_load_state('domcontentloaded');return pop
  ask='#compAskPanel_w-ask-1';gw='#compGwPanel_w-gw-1'
  record('Standby Ask/Giveaway hidden',not overlay.locator(ask).is_visible() and not overlay.locator(gw).is_visible())
  record('Event list contains no seeded mock entries',app.locator('#eventsList .event-box').count()==0)
  record('Viewer roster starts without seeded mock people',app.locator('#userRosterBody .user-row').count()==0)
  record('Overlay chat starts empty',overlay.frame_locator('#legacyChat_w-chat-1').locator('#chat').inner_text().strip()=='')
  shot(overlay,'01-standby')
  poll=opened('#btnRailAsk')
  poll.locator('#askQuestion').fill('AUDIT: choose a game')
  choices=poll.locator('#askChoicesList input');choices.nth(0).fill('FIRST');choices.nth(1).fill('SECOND')
  poll.locator('#askDurationSelect').select_option('0')
  poll.locator('#askFooterIdle button.primary').click();overlay.wait_for_timeout(700)
  record('ASK click start reaches same browser',overlay.locator(ask).is_visible() and 'AUDIT: choose a game' in overlay.locator(ask).inner_text())
  record('ASK click start reaches separate browser storage',obs.locator(ask).is_visible(),'Separate context models app versus OBS; no actual OBS engine used')
  incoming('auditor1','B');incoming('auditor2','B');incoming('auditor3','A');app.wait_for_timeout(1700)
  state=app.evaluate('window._askPollState')
  record('ASK inbound messages count votes',state['choices'][0]['votes']==1 and state['choices'][1]['votes']==2,json.dumps(state['choices']))
  record('CHAT inbound text appears in app','auditor1' in app.locator('#chatList').inner_text())
  record('CHAT inbound text reaches overlay','auditor1' in overlay.frame_locator('#legacyChat_w-chat-1').locator('#chat').inner_text())
  poll.locator('#btnAskPause').click();overlay.wait_for_timeout(200)
  record('ASK pause preserves visible poll',overlay.locator(ask).is_visible(),'Actual visibility after pause')
  poll.locator('#btnAskPause').click()
  poll.locator('#askFooterVoting button[onclick="endAskPoll()"]').click();overlay.wait_for_timeout(300)
  shot(overlay,'02-ask-ended')
  text=overlay.locator('#compAskChoicesList_w-ask-1').inner_text()
  record('ASK final results rank winner first',text.find('SECOND')<text.find('FIRST'),text)
  overlay.reload();overlay.wait_for_selector('.widget',state='attached');overlay.wait_for_timeout(900)
  record('ASK result survives overlay refresh',overlay.locator(ask).is_visible())
  poll.locator('#askFooterEnded button[onclick="closeAskOverlay()"]').click();overlay.wait_for_timeout(300)
  overlay.wait_for_selector(ask,state='hidden',timeout=3000)
  record('ASK click close hides overlay',not overlay.locator(ask).is_visible())
  poll.locator('#askQuestion').fill('AUDIT SECOND POLL');poll.locator('#askFooterIdle button.primary').click();overlay.wait_for_timeout(250)
  record('ASK restart uses new question','AUDIT SECOND POLL' in overlay.locator(ask).inner_text())
  poll.locator('#askFooterVoting button[onclick="closeAskOverlay()"]').click()
  close_tool(poll)
  rand=opened('#btnRailRandomizer');rand.locator('#randItemsText').fill('AUDIT ONLY WINNER')
  rand.locator('button[onclick="runSpinRandomizer()"]').click();overlay.wait_for_timeout(400)
  record('Randomizer button opens overlay',overlay.locator('#on-demand-randomizer-overlay').is_visible())
  record('Randomizer reaches separate browser',obs.locator('#on-demand-randomizer-overlay').count()>0)
  overlay.wait_for_timeout(4200);shot(overlay,'03-randomizer-winner')
  record('Randomizer shows chosen winner',overlay.locator('#on-demand-randomizer-overlay').count()>0 and 'AUDIT ONLY WINNER' in overlay.locator('#on-demand-randomizer-overlay').inner_text())
  overlay.wait_for_selector('#on-demand-randomizer-overlay',state='detached',timeout=15000)
  record('Randomizer removes overlay automatically',True)
  close_tool(rand)
  giveaway=opened('#btnRailGw')
  record('Giveaway opens directly to code and names without prize setup',giveaway.locator('#gwInputCodeCustom').is_visible() and giveaway.locator('#gwPrizeTableBody').count()==0)
  giveaway.locator('#btnGwToggleLiveCode').click();overlay.wait_for_timeout(250)
  record('Giveaway click open code shows overlay',overlay.locator(gw).is_visible())
  record('Giveaway reaches separate browser',obs.locator(gw).is_visible())
  code=giveaway.locator('#gwActiveCodeLabel').inner_text().strip()
  incoming('giveaway_auditor',code);app.wait_for_timeout(1000)
  record('Giveaway chat code registers entrant',app.evaluate("window._gwParticipants.some(x=>x.username==='giveaway_auditor')"))

  giveaway.locator('#btnGwDraw').click();overlay.wait_for_function("document.querySelector('.gacha-winner-name')?.textContent.includes('giveaway_auditor')",timeout=10000)
  record('Giveaway click draw shows real entrant','giveaway_auditor' in overlay.locator(gw).inner_text())
  shot(overlay,'04-giveaway-winner')

  giveaway.locator('[onclick="resetGiveaway()"]').click();overlay.wait_for_timeout(250)
  record('Giveaway finish/reset hides old result',not overlay.locator(gw).is_visible())
  giveaway.locator('#btnGwToggleLiveCode').click();overlay.wait_for_timeout(350);giveaway.locator('#btnGwToggleLiveCode').click();overlay.wait_for_timeout(350)
  record('Giveaway close code hides overlay',not overlay.locator(gw).is_visible())
  close_tool(giveaway)
  replie=opened('#btnRailReplie');replie.get_by_role('button',name='▶ DEMO',exact=True).first.click();overlay.wait_for_timeout(500)
  record('Replie DEMO click renders reply on overlay','สวัสดีครับทุกคน' in overlay.locator('#obsCanvasStage').inner_text())
  shot(overlay,'05-replie-after-demo');close_tool(replie)
  play=opened('#btnRailPlayroom');play.locator('button[onclick="playroomFireActiveClip()"]').click();overlay.wait_for_timeout(500)
  record('Playroom test button shows clip on overlay',overlay.locator('#compPlayroomStage_audit-playroom').is_visible())
  shot(overlay,'06-playroom-after-test');close_tool(play)
  record('Layout on disk unchanged',original_hash==hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest())
  record('No JavaScript page errors',not errors,json.dumps(sorted(set(errors))))
  # Extended real-click regression: configuration, media, persistence and remote controls.
  incoming('event_auditor','LIVE EVENT');messages[-1]['event']='sub';app.wait_for_timeout(1200)
  record('Real incoming activity populates Event list','event_auditor' in app.locator('#eventsList').inner_text())
  replie2=opened('#btnRailReplie')
  replie2.locator('#paneReplieTab1 button.primary').click()
  replie2.locator('#replieEdit_command').fill('!audit');replie2.locator('#replieEdit_mode').select_option('combo');replie2.locator('#replieEdit_ticker_text').fill('AUDIT REPLY');replie2.locator('#replieEdit_image_image_url').fill(base+'/audit/image.svg');replie2.locator('#replieEdit_duration_sec').fill('4');replie2.locator('#replieCommandEditor button[type=submit]').click()
  row=replie2.locator('#paneReplieTab1 tr').filter(has_text='!audit')
  record('Replie create stores actual command',row.count()==1)
  row.get_by_role('button',name='▶ DEMO',exact=True).click()
  overlay.wait_for_selector('.replie-card-image',timeout=3000)
  record('Replie imported image loads',overlay.locator('.replie-card-image').first.evaluate('(img)=>img.complete && img.naturalWidth>0'))
  obs.wait_for_function("document.querySelector('#obsCanvasStage')?.textContent.includes('AUDIT REPLY')",timeout=3000)
  record('Replie custom text reaches separate browser','AUDIT REPLY' in obs.locator('#obsCanvasStage').inner_text())
  shot(overlay,'07-replie-image')
  row.get_by_role('button',name='✏️ แก้ไข',exact=True).click()
  replie2.locator('#replieEdit_ticker_text').fill('AUDIT EDITED');replie2.locator('#replieEdit_duration_sec').fill('1');replie2.locator('#replieCommandEditor button[type=submit]').click()
  record('Replie edit persists text',app.evaluate("window._replieCommands['!audit'].text==='AUDIT EDITED'"))
  replie2.locator('#btnReplieTab2').click();replie2.locator('#paneReplieTab2 input[type="number"]').fill('1')
  replie2.locator('#win-replie .floating-footer button.primary').click();replie2=opened('#btnRailReplie');replie2.locator('#btnReplieTab1').click()
  row=replie2.locator('#paneReplieTab1 tr').filter(has_text='!audit')
  row.get_by_role('button',name='▶ DEMO',exact=True).click()
  overlay.wait_for_selector('.replie-wrapper',state='detached',timeout=3500)
  record('Replie configured timeout cleans all elements',overlay.locator('.replie-wrapper').count()==0)
  row.get_by_role('button',name='✕',exact=True).click()
  record('Replie delete updates stored commands',app.evaluate("!window._replieCommands['!audit']"))
  close_tool(replie2)
  play2=opened('#btnRailPlayroom');answers.extend(['AUDIT IMAGE',base+'/audit/image.svg'])
  play2.locator('button[onclick="addPlayroomClipRow()"]').click()
  record('Playroom add stores provided media URL',app.evaluate("_activePlayroomClips.some(c=>c.name==='AUDIT IMAGE' && c.type==='image')"))
  play2.locator('#btnPlayroomTab2').click();play2.locator('#rngPlayroomImgDur').fill('2');play2.locator('#btnPlayroomTab1').click()
  cliprow=play2.locator('#tbodyPlayroomClips tr').filter(has_text='AUDIT IMAGE');cliprow.locator('button[onclick^="playroomTestClip"]').click()
  overlay.wait_for_selector('[data-live-media]:visible',state='visible',timeout=3000)
  record('Playroom button displays real image',overlay.locator('#compPlayroomStage_audit-playroom img[data-live-media]').evaluate("(img)=>img.tagName==='IMG' && img.complete && img.naturalWidth>0"))
  record('Playroom image reaches separate browser',obs.locator('#compPlayroomStage_audit-playroom img[data-live-media]').count()==1)
  shot(overlay,'08-playroom-image')
  overlay.wait_for_function("document.querySelectorAll('[data-live-media]').length===0",timeout=4000)
  record('Playroom timeout releases media',overlay.locator('[data-live-media]').count()==0)
  cliprow.locator('button[onclick^="deletePlayroomClip"]').click()
  record('Playroom delete updates persisted list',app.evaluate("!_activePlayroomClips.some(c=>c.name==='AUDIT IMAGE')"))
  local_file=Path(fixture_dir.name)/'นำเข้าจริง.svg';local_file.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="50"><rect width="80" height="50" fill="red"/></svg>',encoding='utf-8')
  with play2.expect_file_chooser() as chooser:play2.locator('#btnPlayroomImportLocal').click()
  chooser.value.set_files(str(local_file));play2.wait_for_selector('#tbodyPlayroomClips tr:has-text("นำเข้าจริง")')
  local_row=play2.locator('#tbodyPlayroomClips tr').filter(has_text='นำเข้าจริง')
  record('Playroom local file picker imports Thai-named file into isolated cache',app.evaluate("_activePlayroomClips.some(c=>c.name==='นำเข้าจริง' && c.url.startsWith('/playroom-media/'))") and len(list(launch_dev.playroom_media.root.iterdir()))==1)
  local_row.locator('[data-clip-weight]').fill('7');local_row.locator('[data-clip-volume]').fill('0');play2.locator('#playroomDailyLimit').fill('2')
  record('Playroom weight, zero volume and daily limit persist',app.evaluate("JSON.parse(localStorage.getItem('bp3_playroom_clips'))[_activePlayroomTrigger].some(c=>c.name==='นำเข้าจริง' && c.weight===7 && c.vol===0) && JSON.parse(localStorage.getItem('bp3_playroom_trigger_meta'))[_activePlayroomTrigger].daily_limit===2"))
  play2.locator('#selPlayroomTrigger').select_option('!scare');play2.locator('#selPlayroomTrigger').select_option('!fortune')
  record('Playroom switching triggers retains newly imported clips',play2.locator('#tbodyPlayroomClips tr').filter(has_text='นำเข้าจริง').count()==1)
  local_row=play2.locator('#tbodyPlayroomClips tr').filter(has_text='นำเข้าจริง');local_row.locator('button[onclick^="playroomTestClip"]').click()
  overlay.wait_for_function("document.querySelector('img[data-live-media]')?.src.includes('/playroom-media/')",timeout=5000)
  record('Locally imported media decodes on overlay',overlay.locator('#compPlayroomStage_audit-playroom img[data-live-media]').evaluate('(image)=>image.complete && image.naturalWidth===80'))
  overlay.wait_for_function("document.querySelectorAll('[data-live-media]').length===0",timeout=5000)
  local_row.locator('button[onclick^="deletePlayroomClip"]').click()
  close_tool(play2)
  poll2=opened('#btnRailAsk');poll2.locator('#askQuestion').fill('AUDIT PRESET')
  answers.append('AUDIT SAVED POLL');poll2.locator('#askPresetSelect').locator('..').locator('button').first.click()
  poll2.locator('#askQuestion').fill('CHANGED');poll2.locator('#askPresetSelect').select_option('AUDIT SAVED POLL')
  record('Ask preset restores question',poll2.locator('#askQuestion').input_value()=='AUDIT PRESET')
  poll2.locator('#askAnswerMode').select_option('numbers');poll2.locator('#askDurationSelect').select_option('0');poll2.locator('#askResultsDuration').fill('1')
  poll2.locator('#askRealtime').select_option(index=1)
  poll2.locator('#askFooterIdle button.primary').click();incoming('numeric_auditor','2');app.wait_for_timeout(1200)
  record('Numeric voting counts numeric key',app.evaluate("window._askPollState.choices[1].votes===1 && window._askPollState.choices[1].label==='2'"))
  record('Hidden voting mode conceals totals',overlay.locator('.ask-choice-count').count()==0)
  incoming('numeric_auditor','2');incoming('invalid_auditor','INVALID');app.wait_for_timeout(1000)
  record('Repeat and invalid votes ignored',app.evaluate('window._askPollState.choices.reduce((n,c)=>n+c.votes,0)===1'))
  poll2.locator('#askFooterVoting button[onclick="endAskPoll()"]').click()
  overlay.wait_for_selector(ask,state='hidden',timeout=3500)
  record('Ask result timeout hides overlay',not overlay.locator(ask).is_visible())
  close_tool(poll2)
  rand2=opened('#btnRailRandomizer');rand2.locator('#randItemsText').fill('SAVED ONE\nSAVED TWO')
  answers.append('AUDIT SAVED RANDOM');rand2.locator('#randomizerPresetSelect').locator('..').locator('button').first.click()
  rand2.locator('#randItemsText').fill('CHANGED');rand2.locator('#randomizerPresetSelect').select_option('AUDIT SAVED RANDOM')
  record('Randomizer preset restores items',rand2.locator('#randItemsText').input_value()=='SAVED ONE\nSAVED TWO')
  close_tool(rand2)
  app.locator('[data-item-id="clear-chat"]').click();overlay.wait_for_timeout(700)
  record('Clear chat button clears both overlays',overlay.frame_locator('#legacyChat_w-chat-1').locator('#chat').inner_text().strip()=='' and obs.frame_locator('#legacyChat_w-chat-1').locator('#chat').inner_text().strip()=='')
  obs.reload();obs.wait_for_selector('.widget',state='attached');obs.wait_for_timeout(500)
  record('Clear chat survives overlay refresh',obs.frame_locator('#legacyChat_w-chat-1').locator('#chat').inner_text().strip()=='')
  dock=remote.new_page();dock.goto(base+'/dock.html');dock.locator('.btn-ask-quick').click();dock.locator('#inpAskQuestion').fill('DOCK AUDIT');dock.locator('#btnModeNumbers').click();dock.locator('button[onclick="startQuickAsk()"]').click();dock.locator('#btnConfirmLaunchPreset').click();obs.wait_for_selector(ask,state='visible',timeout=4000)
  record('OBS Dock click starts app poll across contexts',app.evaluate("window._askPollState.phase==='voting'"))
  dock.locator('button[onclick="clearLiveChatBox()"]').click();obs.wait_for_timeout(600)
  record('OBS Dock clear command reaches app',app.locator('#chatList').inner_text().strip().startswith('(ล้าง'))
  record('No extended JavaScript errors',not errors,json.dumps(sorted(set(errors))))
  record('Production layout remains unchanged after extended suite',original_hash==hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest())
  # Incoming commands must trigger their tools without reaching either TTS backend.
  app.wait_for_function('_audioTtsQueue.length===0 && !_isAudioTtsPlaying',timeout=8000)
  incoming('speech_normal_before','ORDINARY MESSAGE BEFORE COMMANDS');app.wait_for_timeout(1200)
  record('Ordinary incoming chat still reaches TTS',any('ORDINARY MESSAGE BEFORE COMMANDS' in text for text in tts_requests) or app.evaluate("window.auditSpeech.some(s=>s.includes('ORDINARY MESSAGE BEFORE COMMANDS'))"))
  app.wait_for_function('_audioTtsQueue.length===0 && !_isAudioTtsPlaying',timeout=8000)
  requests_before=len(tts_requests);fallbacks_before=app.evaluate('window.auditSpeech.length')
  for index,command in enumerate(['!discord','!unknown','!hi','!fortune','#join','join','  JOIN  ','2']):incoming('command_auditor_'+str(index),command)
  app.wait_for_timeout(1800)
  record('Viewer commands never request synthesized speech',len(tts_requests)==requests_before,str(tts_requests[requests_before:]))
  record('Viewer commands never fall back to Web Speech',app.evaluate('window.auditSpeech.length')==fallbacks_before)
  record('Silenced voting command still counts',app.evaluate("window._askPollState.choices[1].votes>0"))
  record('Command chat rows show they were not spoken',app.locator('#chatList .tts-skipped').count()>=8)
  replie_filter=opened('#btnRailReplie');replie_filter.locator('#paneReplieTab1 button.primary').click();replie_filter.locator('#replieEdit_command').fill('auditword');replie_filter.locator('#replieEdit_ticker_text').fill('CUSTOM COMMAND ACTION');replie_filter.locator('#replieCommandEditor button[type=submit]').click()
  requests_before=len(tts_requests);fallbacks_before=app.evaluate('window.auditSpeech.length')
  incoming('configured_command_auditor','auditword');app.wait_for_timeout(1200)
  record('Configured command without punctuation is silent',len(tts_requests)==requests_before and app.evaluate('window.auditSpeech.length')==fallbacks_before)
  record('Silent configured command still renders overlay','CUSTOM COMMAND ACTION' in overlay.locator('#obsCanvasStage').inner_text())
  replie_filter.locator('#paneReplieTab1 tr').filter(has_text='auditword').get_by_role('button',name='✕',exact=True).click();close_tool(replie_filter)
  incoming('speech_normal_after','I enjoy joining the room after commands');app.wait_for_timeout(1300)
  record('Normal text containing a command substring still speaks',any('I enjoy joining the room after commands' in text for text in tts_requests) or app.evaluate("window.auditSpeech.some(s=>s.includes('I enjoy joining the room after commands'))"))
  record('TTS queue remains usable after ignored commands',app.evaluate('_audioTtsQueue.length===0 && !_isAudioTtsPlaying'))

  requests_before=len(tts_requests)
  app.locator('#btn-mute-twitch').click();incoming('muted_platform_auditor','THIS PLATFORM IS MUTED');app.wait_for_timeout(1000)
  record('Platform mute prevents incoming TTS requests',len(tts_requests)==requests_before)
  app.locator('#btn-mute-twitch').click()
  app.locator('#topbarMasterVol').fill('80');app.locator('#vol-twitch').fill('25')
  audio_before=app.evaluate('window.auditAudioVolumes.length');incoming('platform_volume_auditor','CHECK PLATFORM VOLUME')
  app.wait_for_function(f'window.auditAudioVolumes.length>{audio_before}',timeout=4000)
  record('Platform volume multiplies master volume on actual audio',app.evaluate('Math.abs(window.auditAudioVolumes.at(-1).volume-.2)<.001'))
  app.wait_for_timeout(400);app.locator('#topbarMasterVol').fill('0')
  audio_before=app.evaluate('window.auditAudioVolumes.length');incoming('master_zero_auditor','CHECK ZERO MASTER VOLUME')
  app.wait_for_function(f'window.auditAudioVolumes.length>{audio_before}',timeout=4000)
  record('Master volume zero remains silent instead of defaulting to 80',app.evaluate('window.auditAudioVolumes.at(-1).volume===0'))
  record('Platform audio setting persists',app.evaluate("JSON.parse(localStorage.getItem('bp3_platform_audio')).twitch.volume===25"))
  app.locator('#topbarMasterVol').fill('80');app.locator('#vol-twitch').fill('100');app.wait_for_timeout(400)

  incoming('embedded_command_auditor','WORDS BEFORE !fortune WORDS AFTER');app.wait_for_timeout(1200)
  record('Configured command inside ordinary text is removed before TTS',any('WORDS BEFORE WORDS AFTER' in text and '!fortune' not in text for text in tts_requests))
  weighted=app.evaluate("""()=>{PLAYROOM_PRESETS['#weighted']=[{name:'light',url:location.origin+'/audit/image.svg',type:'image',weight:1},{name:'heavy',url:location.origin+'/audit/image.svg',type:'image',weight:99}];_playroomTriggerMeta['#weighted']={daily_limit:1,widget_ids:['audit-playroom']};const events=[],emit=BP3_BUS.emit,random=Math.random;BP3_BUS.emit=function(event,payload){if(event==='PLAYROOM_PLAY_CLIP')events.push(payload);return emit.call(this,event,payload);};Math.random=()=>.5;try{checkRealPlayroomCommand({username:'Daily auditor',text:'hello #weighted there'});checkRealPlayroomCommand({username:'Daily auditor',text:'#weighted'});}finally{Math.random=random;BP3_BUS.emit=emit;}return events;}""")
  record('Playroom respects clip weight, daily limit and target widget metadata',len(weighted)==1 and weighted[0]['name']=='heavy' and weighted[0]['targetWidgetIds']==['audit-playroom'])

  # Legacy profile import/export through the existing Composer buttons.
  import urllib.request
  from legacy_compat import make_server, DEFAULT_PORTS
  record('Legacy default listener ports match v2',launch_dev.PORT==8801 and DEFAULT_PORTS=={'composer_compat':8080,'chat':8765,'playroom':8766,'viewer':8790})
  composer=opened('#btnRailComposer')
  flat={'version':'1.0','canvas_size':'720p','canvas_w':1280,'canvas_h':720,'widgets':[{'id':'old-flat-text','type':'text','text':'FLAT LEGACY PROFILE','x':11,'y':22,'w':333,'h':44,'alpha':0.37,'enabled':True}]}
  flat_file=Path(fixture_dir.name)/'flat-legacy.json';flat_file.write_text(json.dumps(flat),encoding='utf-8')
  with composer.expect_file_chooser() as choose:composer.locator('#btnCompImport').click()
  choose.value.set_files(str(flat_file))
  app.wait_for_function("window.ComposerStudio.getActivePage().widgets.some(w=>w.id==='old-flat-text')")
  app.wait_for_function("async()=>{const layout=await (await fetch('/api/composer/layout')).json();return layout.pages?.[0]?.widgets?.[0]?.id==='old-flat-text' && layout.pages[0].widgets[0].width===333}",timeout=5000)
  record('Legacy flat profile imports through file picker',launch_dev.get_layout()['pages'][0]['widgets'][0]['width']==333)
  multi={'composer_canvas_size':'720p','composer_active_page':'p-two','composer_pages':[
    {'id':'p-one','name':'FIRST','widgets':[{'id':'old-first','type':'text','text':'FIRST PAGE','x':30,'y':40,'w':300,'h':60}]},
    {'id':'p-two','name':'SECOND','widgets':[
     {'id':'old-second','type':'text','text':'SECOND PAGE','x':11,'y':22,'w':333,'h':44,'alpha':0.37,'enabled':True,'old_custom_setting':{'keep':True}},
     {'id':'old-hidden','type':'text','text':'MUST STAY HIDDEN','x':0,'y':0,'w':100,'h':50,'enabled':False},
     {'id':'old-replie','type':'replie','x':0,'y':0,'w':1280,'h':720}]}]}
  import legacy_media, subprocess
  legacy_media.MEDIA_ROOT=Path(fixture_dir.name)/'legacy-cache'
  image_dir=legacy_media.MEDIA_ROOT/'widget_images'/'old-image';image_dir.mkdir(parents=True)
  image_dir.joinpath('image-a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80"><rect width="120" height="80" fill="red"/></svg>',encoding='utf-8')
  image_dir.joinpath('image-b.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80"><rect width="120" height="80" fill="blue"/></svg>',encoding='utf-8')
  multi['composer_pages'][1]['widgets'].append({'id':'old-image','type':'image','x':10,'y':100,'w':120,'h':80,'images':[{'id':'image-a'},{'id':'image-b'}],'slide_interval':1,'slide_interval_unit':'seconds','transition':'none'})
  video_dir=legacy_media.MEDIA_ROOT/'widget_videos'/'old-video';video_dir.mkdir(parents=True)
  video_file=video_dir/'video-a.webm'
  subprocess.run([(os.environ.get('BP3_FFMPEG') or shutil.which('ffmpeg') or str(ROOT.parent/'broadcast playroom dev/ffmpeg.exe')),'-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=red:s=128x72:d=1','-c:v','libvpx-vp9','-an','-y',str(video_file)],check=True,timeout=30)
  multi['composer_pages'][1]['widgets'].append({'id':'old-video','type':'video','x':150,'y':100,'w':128,'h':72,'video_url':'/widget-video/old-video/video-a'})
  multi_file=Path(fixture_dir.name)/'multi-legacy.json';multi_file.write_text(json.dumps({'type':'full_settings','settings':multi}),encoding='utf-8')
  with composer.expect_file_chooser() as choose:composer.locator('#btnCompImport').click()
  choose.value.set_files(str(multi_file))
  app.wait_for_function("window.ComposerStudio.getState().activePageId==='p-two'")
  app.wait_for_timeout(400)
  imported=launch_dev.get_layout()
  record('Legacy import preserves page order and active ID',[p['id'] for p in imported['pages']]==['p-one','p-two'] and imported['activePageId']=='p-two')
  record('Legacy import preserves canvas size',imported['canvasWidth']==1280 and imported['canvasHeight']==720)
  record('Legacy import preserves Replie type',imported['pages'][1]['widgets'][2]['type']=='replie')
  record('Legacy import retains unrecognized widget options',imported['pages'][1]['widgets'][0]['old_custom_setting']=={'keep':True})
  obs.goto(base+'/?p=2');obs.wait_for_selector('.widget[data-id="old-second"]')
  bounds=obs.locator('.widget[data-id="old-second"]').bounding_box()
  record('Legacy p=2 URL preserves widget geometry',bounds['x']==11 and bounds['y']==22 and bounds['width']==333 and bounds['height']==44,str(bounds))
  obs.wait_for_function("document.querySelector('.widget[data-id=old-image] .slide.active')?.complete && document.querySelector('.widget[data-id=old-image] .slide.active')?.naturalWidth>0",timeout=5000)
  record('Migrated cached image loads with its original URL',obs.locator('.widget[data-id="old-image"] .slide').count()==2)
  first_slide=obs.locator('.widget[data-id="old-image"] .slide.active').get_attribute('src')
  obs.wait_for_function("previous=>document.querySelector('.widget[data-id=old-image] .slide.active')?.getAttribute('src')!==previous",arg=first_slide,timeout=4000)
  record('Legacy slideshow rotates migrated images',True)
  obs.wait_for_function("document.querySelector('.widget[data-id=old-video] video')?.readyState>=2",timeout=5000)
  record('Migrated video decodes through original media URL',obs.locator('.widget[data-id="old-video"] video').evaluate('(v)=>v.videoWidth===128'))
  request=urllib.request.Request(base+'/widget-video/old-video/video-a',headers={'Range':'bytes=0-9'})
  with urllib.request.urlopen(request) as response:
   record('Legacy video byte ranges support OBS seeking',response.status==206 and len(response.read())==10 and response.headers.get('Content-Range').startswith('bytes 0-9/'))
  record('Legacy alpha and disabled flags preserved',abs(float(obs.locator('.widget[data-id="old-second"]').evaluate('(el)=>getComputedStyle(el).opacity'))-.37)<.001 and obs.locator('.widget[data-id="old-hidden"]').count()==0)
  record('Legacy 720p canvas rendered at native size',obs.locator('#obsCanvasStage').evaluate('(el)=>el.offsetWidth===1280 && el.offsetHeight===720'))
  obs.goto(base+'/?p=p-one');obs.wait_for_selector('.widget[data-id="old-first"]')
  record('Legacy page ID URL selects original page',obs.locator('.widget[data-id="old-first"]').count()==1)
  obs.goto(base+'/?p=second');obs.wait_for_selector('.widget[data-id="old-second"]')
  record('Legacy page name URL ignores letter case',obs.locator('.widget[data-id="old-second"]').count()==1)
  obs.goto(base+'/');obs.wait_for_selector('.widget[data-id="old-second"]')
  record('Legacy root URL follows active page',obs.locator('.widget[data-id="old-second"]').count()==1)
  with app.expect_download() as downloaded:composer.locator('#btnCompExport').click()
  exported=json.loads(Path(downloaded.value.path()).read_text(encoding='utf-8'))
  record('Export retains migrated pages and canvas',exported['activePageId']=='p-two' and exported['canvasWidth']==1280 and len(exported['pages'])==2)
  close_tool(composer)
  # Each legacy listener retains only its original component, sharing real event state.
  legacy_bases={}
  for view in ['composer_compat','chat','playroom','viewer']:
   alias=make_server(Handler,view,0);threading.Thread(target=alias.serve_forever,daemon=True).start();compat_servers.append(alias)
   legacy_bases[view]=f'http://localhost:{alias.server_port}'
  legacy_context=browser.new_context(viewport={'width':640,'height':360});legacy_context.route('https://**/*',lambda route:route.abort())
  legacy_context.on('page',lambda page:page.on('pageerror',lambda error:errors.append(str(error))))
  legacy_chat=legacy_context.new_page();legacy_chat.goto(legacy_bases['chat']+'/');legacy_chat.wait_for_selector('.widget.type-chat',state='attached')
  record('Legacy standalone chat fills existing OBS source size',legacy_chat.locator('.widget.type-chat').bounding_box()=={'x':0,'y':0,'width':640,'height':360})
  incoming('legacy_chat_auditor','LEGACY CHAT MESSAGE');legacy_chat.frame_locator('iframe[data-legacy-chat]').locator('#chat').filter(has_text='LEGACY CHAT MESSAGE').wait_for(state='attached',timeout=4000)
  record('Legacy chat root receives actual chat pipeline','LEGACY CHAT MESSAGE' in legacy_chat.frame_locator('iframe[data-legacy-chat]').locator('#chat').inner_text())
  legacy_composer=legacy_context.new_page();legacy_composer.goto(legacy_bases['composer_compat']+'/?p=1');legacy_composer.wait_for_selector('.widget[data-id="old-first"]')
  record('New 8080 URL format remains available alongside old root',legacy_composer.locator('.widget[data-id="old-first"]').count()==1)
  legacy_dock=legacy_context.new_page();legacy_dock.goto(legacy_bases['composer_compat']+'/dock')
  record('Legacy /dock URL opens working controls',legacy_dock.locator('#btnTtsToggle').is_visible())
  legacy_viewer=legacy_context.new_page();legacy_viewer.goto(legacy_bases['viewer']+'/');legacy_viewer.wait_for_selector('#viewer',state='attached')
  launch_dev.chat_bridge._on_status('twitch','connected');launch_dev.chat_bridge._on_viewer_count('twitch',123)
  legacy_viewer.wait_for_function("document.querySelector('#viewer .v-count')?.textContent==='123'",timeout=4000)
  record('Legacy viewer root receives real count callbacks',legacy_viewer.locator('#viewer .v-count').inner_text()=='123')
  launch_dev.chat_bridge._on_status('twitch','disconnected')
  legacy_viewer.wait_for_function("document.querySelector('#viewer .v-count')?.textContent==='0'",timeout=4000)
  record('Disconnected platform removes stale viewer count',legacy_viewer.locator('#viewer .v-count').inner_text()=='0')
  standalone_gw=legacy_context.new_page();standalone_gw.goto(legacy_bases['chat']+'/giveaway');standalone_gw.wait_for_selector('.widget.type-giveaway',state='attached')
  giveaway3=opened('#btnRailGw');giveaway3.locator('#btnGwToggleLiveCode').click()
  standalone_gw.wait_for_selector('.giveaway-cp-box.visible',timeout=4000)
  record('Legacy /giveaway URL receives giveaway only',standalone_gw.locator('.widget').count()==1 and standalone_gw.locator('.widget.type-giveaway').count()==1)
  record('Standalone chat excludes giveaway overlay',legacy_chat.locator('.widget.type-giveaway').count()==0 and legacy_chat.locator('.giveaway-cp-box').count()==0)
  giveaway3.locator('#btnGwToggleLiveCode').click();close_tool(giveaway3)
  record('Production layout file untouched by migration tests',original_hash==hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest())
  record('No migration JavaScript errors',not errors,json.dumps(sorted(set(errors))))

  # FULL/Lite capability gates and model UI, with small model fixtures (no remote weights).
  from rvc_service import RVCService
  class AuditEngine:
   def __init__(self,path):self.is_loaded=False;self.convert_calls=0
   def load(self):self.is_loaded=True
   def unload(self):self.is_loaded=False
   def convert_array(self,audio,rate):self.convert_calls+=1;return audio*.5,rate
  def fixture_download(voice,destination,progress,cancel):
   progress(1,2);Path(destination,'downloaded-audit.pth').write_bytes(b'AUDIT MODEL FIXTURE');progress(2,2);return 'downloaded-audit.pth'
  full_models=Path(fixture_dir.name)/'full-models';full_models.mkdir()
  (full_models/'actual-local-model.pth').write_bytes(b'AUDIT MODEL FIXTURE')
  original_rvc=launch_dev.rvc_service
  full_service=RVCService(edition='full',model_dir=full_models,state_file=Path(fixture_dir.name)/'full-rvc.json',roots=[full_models],engine_factory=AuditEngine,downloader=fixture_download)
  launch_dev.rvc_service=full_service
  full_context=browser.new_context(viewport={'width':1920,'height':1080});full_context.route('https://**/*',lambda route:route.abort())
  full_context.on('page',lambda page:page.on('pageerror',lambda error:errors.append(str(error))))
  full_app=full_context.new_page();full_app.goto(base+'/index.html');full_app.wait_for_function("window.BP3Capabilities?.edition==='full'")
  with full_app.expect_popup() as info:full_app.locator('#btnRailVoiceSettings').click()
  full_voice=info.value;full_voice.wait_for_load_state('domcontentloaded');full_voice.wait_for_selector('#rvcVoiceCard',state='visible')
  record('FULL shows RVC controls',full_voice.locator('#winRvcSelect').is_visible())
  labels=full_voice.locator('#winRvcSelect').inner_text()
  record('FULL lists files instead of invented model names','actual-local-model' in labels and not any(name in labels for name in ['Baitoei','Meng Custom','Anime Maid','Cyberpunk']))
  actual_id=full_service.public_models()[0]['id'];full_voice.locator('#winRvcSelect').select_option(actual_id)
  full_voice.wait_for_function("document.getElementById('chkEnableRvc')?.checked===true",timeout=5000)
  record('FULL model selection invokes loader and persists selection',full_service.status()['loaded'] and full_service.state_file.is_file())
  original_tts=launch_dev.tts_service.generate_audio_bytes;launch_dev.tts_service.generate_audio_bytes=lambda *args,**kwargs:silent_audio
  tts_backend_passthrough=True
  with urllib.request.urlopen(base+'/api/tts?text=RVC_PIPELINE_TEST') as response:
   converted=response.read();record('FULL TTS pipeline passes through selected RVC engine',response.headers.get_content_type()=='audio/wav' and converted[:4]==b'RIFF' and full_service.engine.convert_calls>0)
  tts_backend_passthrough=False;launch_dev.tts_service.generate_audio_bytes=original_tts
  with full_voice.expect_file_chooser() as choose:full_voice.locator('[onclick="importRvcModelFile()"]').click()
  local_model=Path(fixture_dir.name)/'โมเดลทดสอบ.pth';local_model.write_bytes(b'USER IMPORT FIXTURE');choose.value.set_files(str(local_model))
  full_voice.wait_for_function("Array.from(document.querySelector('#winRvcSelect').options).some(option=>option.textContent==='โมเดลทดสอบ')",timeout=5000)
  record('FULL model file picker imports actual bytes',(full_models/'โมเดลทดสอบ.pth').read_bytes()==b'USER IMPORT FIXTURE')
  full_voice.locator('[onclick="openRvcDownloader()"]').click();full_voice.wait_for_selector('#rvcDownloadDialog[open]')
  record('FULL opens legacy model catalog',full_voice.locator('#rvcCatalogSelect option').count()>0)
  full_voice.locator('#btnRvcDownload').click()
  full_voice.wait_for_function("Array.from(document.querySelector('#winRvcSelect').options).some(option=>option.textContent==='downloaded-audit')",timeout=5000)
  record('FULL download completes and refreshes model list',(full_models/'downloaded-audit.pth').is_file() and full_service.status()['progress']==100)
  full_voice.get_by_role('button',name='ปิด',exact=True).click();close_tool(full_voice)
  restored_service=RVCService(edition='full',model_dir=full_models,state_file=full_service.state_file,roots=[full_models],engine_factory=AuditEngine)
  if(restored_service.worker):restored_service.worker.join(timeout=5)
  record('FULL restores selected enabled model after restart',restored_service.status()['selected']==actual_id and restored_service.status()['loaded'])
  if(restored_service.engine):restored_service.engine.unload()
  # Lite enforces the restriction in the backend as well as removing the interface.
  lite_models=Path(fixture_dir.name)/'lite-models'
  lite_service=RVCService(edition='lite',model_dir=lite_models,state_file=Path(fixture_dir.name)/'lite-rvc.json',roots=[lite_models])
  launch_dev.rvc_service=lite_service
  lite_context=browser.new_context(viewport={'width':1920,'height':1080});lite_context.route('https://**/*',lambda route:route.abort())
  lite_context.on('page',lambda page:page.on('pageerror',lambda error:errors.append(str(error))))
  lite_app=lite_context.new_page();lite_app.goto(base+'/index.html');lite_app.wait_for_function("window.BP3Capabilities?.edition==='lite'")
  with lite_app.expect_popup() as info:lite_app.locator('#btnRailVoiceSettings').click()
  lite_voice=info.value;lite_voice.wait_for_load_state('domcontentloaded')
  record('Lite has no model selector or downloader',lite_voice.locator('#rvcVoiceCard,#winRvcSelect,[onclick="openRvcDownloader()"],[onclick="importRvcModelFile()"]').count()==0)
  record('Lite removes secondary settings RVC toggle',lite_app.locator('#chkEnableRvcSettings').count()==0)
  rejected=[]
  for path,body in [('/api/rvc/models',None),('/api/rvc/catalog',None),('/api/rvc/select',{'id':actual_id}),('/api/rvc/download',{'id':'0'}),('/api/rvc/open-folder',{})]:
   request=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
   try:urllib.request.urlopen(request);rejected.append(False)
   except urllib.error.HTTPError as error:rejected.append(error.code==403)
  record('Lite rejects model listing/loading/downloading APIs',all(rejected))
  record('Lite creates no model or settings files',not lite_models.exists() and not lite_service.state_file.exists())
  record('Lite does not import the heavy inference engine','rvc_engine' not in sys.modules)
  close_tool(lite_voice);lite_context.close();full_context.close();launch_dev.rvc_service=original_rvc

  # Redesigned Giveaway: code, unique names, direct draw; no prize definitions.
  gwcfg=opened('#btnRailGw');gwcfg.locator('[onclick="resetGiveaway()"]').click()
  record('Giveaway contains no prize sets, tiers or checkpoint setup',gwcfg.locator('#btnGwMode2,#gwPrizeTableBody,#gwCheckpointSelect').count()==0 and gwcfg.locator('#btnGwDraw').is_visible())
  gwcfg.locator('#gwInputCodeCustom').fill('#names');gwcfg.locator('#btnGwToggleLiveCode').click()
  incoming('name_first','#names');incoming('name_first','#names');incoming('name_second','#names');incoming('not_joined','ordinary message');app.wait_for_function("_gwParticipants.length===2 && _gwParticipants.some(person=>person.username==='name_first') && _gwParticipants.some(person=>person.username==='name_second')",timeout=6000)
  record('Giveaway code collects unique actual names only',app.evaluate("_gwParticipants.length===2 && _gwParticipants.some(person=>person.username==='name_first') && _gwParticipants.some(person=>person.username==='name_second')"))
  gwcfg.locator('#gwTableBody tr').filter(has_text='name_first').locator('button').click()
  record('Giveaway removes selected participant from the draw pool',app.evaluate("getGwEligibleParticipants().length===1 && getGwEligibleParticipants()[0].username==='name_second'"))
  gwcfg.locator('#btnGwDraw').click();gwcfg.wait_for_function("document.querySelectorAll('#gwWinnerHistory tr').length===1",timeout=10000)
  record('Giveaway draws directly from collected names without configuring a prize','name_second' in (gwcfg.locator('#gwWinnerHistory').text_content() or '') and app.evaluate("!Object.hasOwn(_liveGwState,'prize')"))
  gwcfg.locator('#btnGwDraw').click();gwcfg.wait_for_function("document.querySelectorAll('#gwWinnerHistory tr').length===2",timeout=10000)
  record('Giveaway rerolls the existing list without prize quota or points',app.evaluate('getGwEligibleParticipants().length===1') and gwcfg.locator('#gwWinnerHistory tr').count()==2)
  for draw_style in ['gachapon','slot','shuffle']:
   gwcfg.locator('#gwDrawStyle').select_option(draw_style);before=gwcfg.locator('#gwWinnerHistory tr').count();gwcfg.locator('#btnGwDraw').click();gwcfg.wait_for_function('n=>document.querySelectorAll("#gwWinnerHistory tr").length>n',arg=before,timeout=10000)
   record('Giveaway sends selected '+draw_style+' style with winner',app.evaluate('s=>_liveGwState.style===s && Boolean(_liveGwState.winner)',draw_style))
  with gwcfg.expect_download() as download:gwcfg.locator('#btnGiveawayExportCsv').click()
  csv_path=Path(fixture_dir.name)/'giveaway-names.csv';download.value.save_as(str(csv_path));csv_bytes=csv_path.read_bytes()
  record('Giveaway CSV exports actual names and draw history without prize fields',csv_bytes.startswith(b'\xef\xbb\xbf') and 'name_second' in csv_bytes.decode('utf-8-sig') and 'ของรางวัล' not in csv_bytes.decode('utf-8-sig'))
  gwcfg.locator('[onclick="resetGiveaway()"]').click()
  record('Giveaway reset clears participants and draw history',app.evaluate('_gwParticipants.length===0') and gwcfg.locator('#gwWinnerHistory tr').count()==0)
  print('GIVEAWAY STEP screenshot',flush=True)
  shot(gwcfg,'09-giveaway-direct')
  print('GIVEAWAY STEP image chooser',flush=True)
  gwcfg.locator('#gwOverlaySettings summary').click()
  image=Path(fixture_dir.name)/'giveaway-banner.svg';image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="90"><rect width="300" height="90" fill="purple"/></svg>',encoding='utf-8');image_hash=hashlib.sha256(image.read_bytes()).hexdigest()
  with gwcfg.expect_file_chooser() as chooser:gwcfg.locator('#btnGiveawayImportImage').click()
  chooser.value.set_files(str(image));app.wait_for_function("hash=>getGwOverlayOptions().config.overlay_image_url.endsWith(hash+'.svg')",arg=image_hash,timeout=8000)
  print('GIVEAWAY STEP independent image',flush=True)
  gwcfg.locator('#btnGwToggleLiveCode').click();standalone_gw.locator('.giveaway-image-box.visible').wait_for(state='visible')
  try:
   standalone_gw.wait_for_function("hash=>{const image=document.querySelector('.giveaway-custom-img');return image?.complete && image.naturalWidth===300 && image.src.endsWith(hash+'.svg');}",arg=image_hash,timeout=8000)
  except Exception:
   print('GIVEAWAY DEBUG',app.evaluate('getGwOverlayOptions()'),standalone_gw.locator('.giveaway-custom-img').evaluate("e=>({src:e.src,attr:e.getAttribute('src'),width:e.naturalWidth,complete:e.complete})"),flush=True);raise
  record('Giveaway selected image banner decodes on independent overlay',True)
  gwcfg.locator('#btnGwToggleLiveCode').click();gwcfg.locator('[name="gwOverlayMode"][value="banner"]').check();gwcfg.locator('#gwReceiveDuration').fill('1');gwcfg.locator('#btnSaveGiveawaySettings').click();gwcfg.locator('#btnGwToggleLiveCode').click();app.wait_for_function('window._isGwCodeBroadcasting===false',timeout=4000)
  record('Giveaway optional reception timer stops accepting names',not app.evaluate('_isGwCodeBroadcasting'))
  saved=launch_dev.get_layout()['legacyTools']['giveaway'];record('Giveaway profile stores only reception and overlay settings',saved['code']=='#names' and saved['duration']==1 and 'prizeSets' not in saved and 'presets' not in saved)
  record('Giveaway import leaves original selected file unchanged',hashlib.sha256(image.read_bytes()).hexdigest()==image_hash)
  gwcfg.locator('[onclick="resetGiveaway()"]').click();close_tool(gwcfg)

  roster=opened('#btnRailUserManager');incoming('Roster Auditor','ROSTER FIRST MESSAGE');roster.wait_for_timeout(900)
  roster_row=roster.locator('#userRosterBody tr').filter(has_text='Roster Auditor')
  record('Actual messages update the detached viewer roster',roster_row.count()==1 and roster_row.locator('td').nth(3).inner_text()=='1')
  answers.append('Roster Alias');roster_row.locator('td').nth(1).click();roster.wait_for_timeout(200)
  record('Viewer nickname edits persist in the real roster',app.evaluate("JSON.parse(localStorage.getItem('bp3_custom_nicknames'))['Roster Auditor']==='Roster Alias'") and 'Roster Alias' in roster.locator('#userRosterBody').inner_text())
  with ctx.expect_page() as profile_info:roster.locator('#userRosterBody tr').filter(has_text='Roster Auditor').get_by_role('button',name='โปรไฟล์',exact=True).click()
  profile=profile_info.value;profile.wait_for_load_state('domcontentloaded');profile.wait_for_timeout(150)
  record('Viewer profile shows real statistics and history',profile.locator('#profMsgCount').inner_text()=='1 ข้อความ' and 'ROSTER FIRST MESSAGE' in profile.locator('#paneProfTab1').inner_text())
  profile.locator('#btnToggleMuteTts').click();requests_before=len(tts_requests);incoming('Roster Auditor','MUTED USER MESSAGE');profile.wait_for_timeout(1000)
  record('Per-user mute suppresses TTS while preserving chat',len(tts_requests)==requests_before and 'MUTED USER MESSAGE' in app.locator('#chatList').inner_text())
  profile.locator('#btnToggleMuteTts').click();profile.locator('[onclick="blockUserFromProfile()"]').click();profile.locator('[data-block-rule="all"]').check();profile.locator('#profileBlockRules button').click();close_tool(profile);roster.wait_for_timeout(300)
  requests_before=len(tts_requests);incoming('Roster Auditor','BLOCKED USER UNIQUE MESSAGE');roster.wait_for_timeout(1000)
  record('Blocking a viewer suppresses both chat and TTS',len(tts_requests)==requests_before and 'BLOCKED USER UNIQUE MESSAGE' not in app.locator('#chatList').inner_text() and 'BLOCKED USER UNIQUE MESSAGE' not in obs.locator('#obsCanvasStage').inner_text())
  roster.locator('#btnFilterBlocked').click();record('Blocked viewer filter uses real saved state',roster.locator('#userRosterBody tr').filter(has_text='Roster Auditor').count()==1 and app.evaluate("JSON.parse(localStorage.getItem('bp3_blocked_users'))['roster auditor'].all===true"))
  with ctx.expect_page() as profile_info:roster.locator('#userRosterBody tr').filter(has_text='Roster Auditor').get_by_role('button',name='โปรไฟล์',exact=True).click()
  profile=profile_info.value;profile.wait_for_load_state('domcontentloaded');profile.wait_for_timeout(150);profile.locator('#btnProfTab3').click()
  record('New viewer notes contain no mock biography',profile.locator('#paneProfTab3 textarea').input_value()=='')
  profile.locator('#paneProfTab3 textarea').fill('ACTUAL SAVED NOTE');profile.locator('#btnSaveUserNotes').click()
  record('Viewer profile notes save actual content',app.evaluate("JSON.parse(localStorage.getItem('bp3_user_notes'))['roster auditor']==='ACTUAL SAVED NOTE'"))
  with ctx.expect_page() as profile_info:roster.locator('#userRosterBody tr').filter(has_text='Roster Auditor').get_by_role('button',name='โปรไฟล์',exact=True).click()
  profile=profile_info.value;profile.wait_for_load_state('domcontentloaded');profile.wait_for_timeout(150);profile.locator('[onclick="blockUserFromProfile()"]').click();profile.locator('[data-block-rule="all"]').uncheck();profile.locator('#profileBlockRules button').click();close_tool(profile);incoming('Roster Auditor','UNBLOCKED USER MESSAGE');roster.wait_for_timeout(1000)
  record('Unblocking a viewer restores incoming chat',not app.evaluate("Boolean(window._blockedUsers['roster auditor'])") and 'UNBLOCKED USER MESSAGE' in app.locator('#chatList').inner_text())
  roster.locator('#btnFilterAll').click()
  with roster.expect_download() as download:roster.locator('#btnUserRosterExport').click()
  roster_csv=Path(fixture_dir.name)/'viewers.csv';download.value.save_as(str(roster_csv));csv=roster_csv.read_text(encoding='utf-8-sig')
  record('Viewer CSV exports real names, aliases and counts','Roster Auditor' in csv and 'Roster Alias' in csv and 'Somchai_VIP' not in csv)
  close_tool(roster)



  app.evaluate("applyLegacyToolData({legacyTools:{twitch_channel:'legacy_twitch',youtube_url:'https://youtube.com/watch?v=legacy',soop_bid:'legacy_soop',read_tts_twitch:false,tts_volume_soop:42}})")
  record('Legacy channel and per-platform audio settings migrate',app.evaluate("getPlatformChannel('twitch')==='legacy_twitch' && getPlatformChannel('soop')==='legacy_soop' && _platformStates.twitch.muted && _platformStates.soop.volume===42"))
  record('No JavaScript errors across all audited flows',not errors,json.dumps(sorted(set(errors))))
  browser.close()
except Exception:
 record('Harness completion',False,traceback.format_exc());print(traceback.format_exc(),flush=True)
finally:
 for alias in compat_servers: alias.shutdown();alias.server_close()
 server.shutdown();server.server_close();fixture_dir.cleanup()
 (OUT/'results.json').write_text(json.dumps({'results':results,'page_errors':errors,'fixture':{'chat':'synthetic provider callbacks through real ChatBridge and HTTP endpoints','layout':'temporary file; production file hash checked','tts':'silent WAV response and recorded Web Speech; verifies command suppression without generating speech','rvc':'UI/API use a small model fixture, engine double and local download fixture; actual model inference is verified separately in rvc-smoke.json','media':'real cached SVG slideshow and decoded generated WebM','browser':'independent Chromium contexts, not actual OBS/CEF; external resources blocked'}},ensure_ascii=False,indent=2),encoding='utf-8')
 print('RESULTS',sum(r['status']=='PASS' for r in results),'PASS',sum(r['status']=='FAIL' for r in results),'FAIL',flush=True)




if any(result['status']=='FAIL' for result in results):sys.exit(1)
