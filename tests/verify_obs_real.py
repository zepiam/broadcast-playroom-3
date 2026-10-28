import uuid
import sys,os,json,time,threading,tempfile,hashlib,base64,io
from pathlib import Path
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'work'/'compat-audit'
OUT.mkdir(parents=True,exist_ok=True)
WORK=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parents[1]/'work'/'obs-audit'
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from PIL import Image
import obsws_python as obs
import launch_dev
from chat_twitch import ChatMessage
connection=json.loads((WORK/'obs_connection.json').read_text(encoding='utf-8'))
client=obs.ReqClient(host='127.0.0.1',port=connection['port'],password=connection['password'],timeout=5)
results=[];errors=[];server=None
SCENE_NAME='BP3Audit-'+uuid.uuid4().hex[:8]
SOURCE_NAME='BP3 OBS Audit-'+uuid.uuid4().hex[:8]
personal=Path(os.environ['APPDATA'])/'obs-studio'
def profile_hash():
 digest=hashlib.sha256()
 if personal.is_dir():
  for path in sorted(personal.rglob('*')):
   if path.is_file() and path.suffix in ('.json','.ini'):digest.update(path.read_bytes())
 return digest.hexdigest()
original_profile=profile_hash()
layout_hash=hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest()
def record(test,passed,detail=''):
 item=dict(test=test,status='PASS' if passed else 'FAIL',detail=detail);results.append(item);print(item,flush=True)
def screenshot(name):
 data=client.get_source_screenshot(SOURCE_NAME,'png',1920,1080,-1).image_data
 content=base64.b64decode(data.split(',',1)[1]);image=Image.open(io.BytesIO(content)).convert('RGBA');(OUT/name).write_bytes(content)
 return image

def pixels(image):return sum(1 for value in image.getchannel('A').getdata() if value>10)
class Handler(launch_dev.QuietHandler):
 def do_GET(self):
  if self.path=='/obs-audit-image.svg':
   data=b'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200"><rect width="320" height="200" fill="red"/></svg>'
   self.send_response(200);self.send_header('Content-Type','image/svg+xml');self.end_headers();self.wfile.write(data);return
  super().do_GET()
try:
 record('Actual OBS authenticated portable connection',True,client.get_version().obs_version)
 record('OBS test is not streaming or recording',not client.get_stream_status().output_active and not client.get_record_status().output_active)
 with tempfile.TemporaryDirectory(prefix='bp3-obs-') as directory:
  launch_dev.LAYOUT_FILE=str(Path(directory)/'layout.json');launch_dev._LAYOUT_CACHE=None
  widgets=[dict(id=kind,type=kind,x=0,y=0,width=1920,height=1080) for kind in ['ask','giveaway','replie','randomizer','playroom']]
  widgets.append(dict(id='chat',type='chat',x=30,y=30,width=650,height=400))
  launch_dev.save_layout(dict(activePageId='obs',pages=[dict(id='obs',name='OBS',widgets=widgets)]))
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
  client.create_scene(SCENE_NAME)
  client.create_input(SCENE_NAME,SOURCE_NAME,'browser_source',dict(url=base+'/?p=1',width=1920,height=1080,fps=30,shutdown=False,restart_when_active=False,reroute_audio=False),True)
  client.set_current_program_scene(SCENE_NAME)
  with sync_playwright() as play:
   browser=play.chromium.launch(headless=True)
   context=browser.new_context(viewport=dict(width=1920,height=1080));context.route('https://**/*',lambda route:route.abort());context.add_init_script("if(location.protocol==='http:')localStorage.setItem('bp3_master_tts','false')")
   context.on('page',lambda page:page.on('pageerror',lambda error:errors.append(str(error))))
   answers=[];context.on('dialog',lambda dialog:dialog.accept(answers.pop(0)) if answers else dialog.dismiss())
   app=context.new_page();app.goto(base+'/index.html');app.wait_for_timeout(3500)
   record('Actual OBS Browser Source standby is transparent',pixels(screenshot('obs-01-idle.png'))==0)
   def opened(selector):
    with app.expect_popup() as info:app.locator(selector).click()
    popup=info.value;popup.wait_for_load_state('domcontentloaded');return popup
   def close(popup):
    popup.locator('.floating-header .close-red').first.click();app.wait_for_timeout(200)
   ask=opened('#btnRailAsk');ask.locator('#askQuestion').fill('OBS ACTUAL CEF POLL');ask.locator('#askDurationSelect').select_option('0');ask.locator('#askFooterIdle button.primary').click();app.wait_for_timeout(1500)
   record('App poll click renders in actual OBS CEF',pixels(screenshot('obs-02-ask.png'))>1000)
   launch_dev.chat_bridge._on_message('Twitch',ChatMessage(platform='twitch',author='OBS audit viewer',text='A'));app.wait_for_timeout(800)
   screenshot('obs-03-vote-chat.png')
   ask.locator('#askFooterVoting button[onclick="endAskPoll()"]').click();app.wait_for_timeout(800)
   client.set_input_settings(SOURCE_NAME,dict(url=base+'/?p=1&obsrefresh=1'),True);app.wait_for_timeout(2500)
   record('Actual OBS source refresh restores active poll',pixels(screenshot('obs-04-refresh.png'))>1000)
   ask.locator('#askFooterEnded button[onclick="closeAskOverlay()"]').click();app.locator('[data-item-id="clear-chat"]').click();app.wait_for_timeout(1200)
   record('Actual OBS clears poll and chat back to transparency',pixels(screenshot('obs-05-clear.png'))==0);close(ask)
   rand=opened('#btnRailRandomizer');rand.locator('#randItemsText').fill('OBS ONLY WINNER');rand.locator('button[onclick="runSpinRandomizer()"]').click();app.wait_for_timeout(900)
   record('Randomizer button renders in actual OBS',pixels(screenshot('obs-06-randomizer.png'))>1000)
   app.wait_for_timeout(12000);record('Randomizer releases actual OBS surface after timeout',pixels(screenshot('obs-07-randomizer-cleared.png'))==0);close(rand)
   gw=opened('#btnRailGw');gw.locator('#btnGwToggleLiveCode').click();app.wait_for_timeout(1200)
   record('Giveaway code appears in actual OBS',pixels(screenshot('obs-08-giveaway-code.png'))>1000)
   launch_dev.chat_bridge._on_message('Twitch',ChatMessage(platform='twitch',author='OBS actual entrant',text='#join'));app.wait_for_timeout(1000)
   gw.locator('#btnGwDraw').click();app.wait_for_timeout(7500)
   record('Giveaway draw renders in actual OBS',pixels(screenshot('obs-09-giveaway-winner.png'))>1000)
   gw.locator('[onclick="resetGiveaway()"]').click();app.locator('[data-item-id="clear-chat"]').click();app.wait_for_timeout(1000);close(gw)
   replie=opened('#btnRailReplie');replie.locator('#paneReplieTab1 button').filter(has_text='DEMO').first.click();app.wait_for_timeout(1000)
   record('Replie demo renders in actual OBS',pixels(screenshot('obs-10-replie.png'))>1000)
   app.evaluate("BP3_BUS.emit('REPLIE_DISMISS',{})");app.wait_for_timeout(800);close(replie)
   media=opened('#btnRailPlayroom');answers.extend(['OBS Actual Image',base+'/obs-audit-image.svg']);media.locator('button[onclick="addPlayroomClipRow()"]').click();media.locator('#btnPlayroomTab2').click();media.locator('#rngPlayroomImgDur').fill('3');media.locator('#btnPlayroomTab1').click();media.locator('#tbodyPlayroomClips tr').filter(has_text='OBS Actual Image').locator('button[onclick^="playroomTestClip"]').click();app.wait_for_timeout(1000)
   image=screenshot('obs-11-playroom.png');red=sum(1 for r,g,b,a in image.getdata() if r>200 and g<30 and b<30 and a>200)
   record('Selected real Playroom image decodes in actual OBS',red>1000)
   app.wait_for_timeout(3500);record('Actual OBS returns to fully transparent idle after all tools',pixels(screenshot('obs-12-final-idle.png'))==0)
   close(media);record('No app JavaScript errors in actual OBS click suite',not errors,json.dumps(errors));browser.close()
except Exception as error:
 import traceback
 record('Actual OBS harness completed',False,traceback.format_exc())
finally:
 try:client.remove_input(SOURCE_NAME)
 except Exception:pass
 try:client.remove_scene(SCENE_NAME)
 except Exception:pass
 client.disconnect()
 if server:server.shutdown();server.server_close()
 record('Original user OBS profile remains unchanged',original_profile==profile_hash())
 record('Production app layout remains unchanged',layout_hash==hashlib.sha256((ROOT/'composer_layout.json').read_bytes()).hexdigest())
 (OUT/'obs-real.json').write_text(json.dumps(dict(results=results,fixture='Actual installed OBS portable copy with isolated profile, authenticated WebSocket, app clicked in Chromium; synthetic provider callbacks, no streaming/recording'),ensure_ascii=False,indent=2),encoding='utf-8')
 print('OBS RESULTS',sum(r['status']=='PASS' for r in results),'PASS',sum(r['status']=='FAIL' for r in results),'FAIL',flush=True)

if any(item['status']=='FAIL' for item in results):sys.exit(1)
