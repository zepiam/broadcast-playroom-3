import os,sys,tempfile,threading
from pathlib import Path
from unittest.mock import patch
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev
import supporters_service
with tempfile.TemporaryDirectory(prefix='supporters-ui-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}';calls=[];errors=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1500,'height':950});ctx.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))))
   data=[{'name':'Person '+str(i),'amount':i,'currency':'THB','date':'2026-10-%02d'%i,'source':'Broadcast Playroom','message':'hello','platform':'twitch','channel_url':'https://twitch.tv/example'} for i in range(1,8)]
   fetch_patch=patch.object(supporters_service,'fetch',return_value={'ok':True,'supporters':data});fetch_patch.start()
   def action(body):
    calls.append(body);kind=body['action'];return {'ok':True,**({'tx_id':'fixture-tx','amount':50,'currency':'THB'} if kind=='redeem' else {})}
   action_patch=patch.object(supporters_service,'action',side_effect=action);action_patch.start()
   page=ctx.new_page();page.goto(base+'/index.html');assert 'Modern & Lightweight' not in page.locator('.statusbar').inner_text()
   with page.expect_popup() as opened:page.locator('.status-support-link').click()
   settings=opened.value;settings.wait_for_load_state();settings.locator('#sec-supporters').wait_for(state='visible');settings.locator('.support-person').first.wait_for();settings.screenshot(path=r'C:\Users\Meng-PC\Documents\Codex\2026-10-26\new-chat\outputs\overlay-audit\supporters-settings.png');assert settings.locator('#nav-sec-supporters').inner_text().strip().endswith('สนับสนุน');assert settings.locator('.support-person').count()==5
   settings.locator('#supportNext').click();print('page2',settings.locator('.support-person').count(),flush=True);assert settings.locator('.support-person').count()==2;settings.locator('#supportSortAmount').click();print('first',settings.locator('.support-person').first.inner_text(),flush=True);assert 'Person 7' in settings.locator('.support-person').first.inner_text();settings.wait_for_function("document.querySelector('.support-channel img')?.naturalWidth>0",timeout=3000);print('PASS footer navigation, real-page presentation, sorting, pagination and platform icons')
   page.evaluate("BP3UiText.setMode('xlarge')");settings.wait_for_timeout(200)
   assert settings.locator('.support-method').evaluate_all("es=>es.every(e=>{const a=e.getBoundingClientRect(),b=e.querySelector('button').getBoundingClientRect();return b.left>=a.left && b.right<=a.right && b.bottom<=a.bottom})")
   page.evaluate("BP3UiText.setMode('normal')");settings.wait_for_timeout(150);print('PASS layout stays within cards at larger font')
   settings.locator('button[onclick="SupportersUI.open(\'qr\')"]').click(timeout=3000);assert settings.locator('#supportQrDialog').is_visible();settings.locator('.support-qr').wait_for();assert settings.locator('.support-qr').evaluate('e=>e.complete && e.naturalWidth>0');settings.locator('button[onclick="SupportersUI.close(\'qr\')"]').click();print('PASS QR display')
   settings.locator('button[onclick="SupportersUI.open(\'voucher\')"]').click();settings.locator('#supportVoucherUrl').fill('https://gift.truemoney.com/campaign/?v=fixture');settings.locator('#supportVoucherForm button[type=submit]').click();settings.locator('#supportVoucherComplete').wait_for(state='visible');settings.locator('#supportVoucherName').fill('Fixture');settings.locator('#supportVoucherPlatform').select_option('twitch');assert settings.locator('#supportVoucherPlatformIcon').is_visible();settings.locator('#supportVoucherComplete button[type=submit]').click();settings.locator('#supportVoucherStatus').filter(has_text='บันทึกข้อมูลแล้ว').wait_for();settings.locator('button[onclick="SupportersUI.close(\'voucher\')"]').click();assert [c['action'] for c in calls[:2]]==['redeem','complete'];print('PASS voucher and supporter details with mocked transactions')
   settings.locator('button[onclick="SupportersUI.open(\'bank\')"]').click();settings.locator('#supportBankMethod').select_option('manual');settings.locator('#supportBankName').select_option('SCB');settings.locator('#supportTransferDate').fill('2026-10-27');settings.locator('#supportTransferTime').fill('10:30');settings.locator('#supportBankAmount').fill('100');settings.locator('#supportBankSupporter').fill('Fixture');settings.locator('#supportBankForm button[type=submit]').click();settings.locator('#supportBankStatus').filter(has_text='ส่งข้อมูลแล้ว').wait_for();assert calls[-1]['method']=='manual';print('PASS manual bank submission with mocked service')
   assert settings.locator('#supportSlipField').is_visible() and settings.locator('#supportManualFields').is_hidden();settings.locator('#supportBankAmount').fill('30');settings.locator('#supportBankSupporter').fill('Slip Fixture');settings.locator('#supportSlip').set_input_files(str(Path('src/assets/supporters-kit/twitch.png').resolve()));settings.locator('#supportBankPlatform').select_option('other');assert settings.locator('#supportBankPlatformIcon').get_attribute('src').endswith('/homepage.png');settings.locator('#supportBankForm button[type=submit]').click();settings.locator('#supportBankStatus').filter(has_text='ส่งข้อมูลแล้ว').wait_for();assert calls[-1]['method']=='slip' and calls[-1]['slip'].startswith('data:image/png;base64,') and calls[-1]['platform']=='other';print('PASS slip upload and other-platform icon with mocked service')
   assert not errors,errors;browser.close()
 finally:server.shutdown();server.server_close()
