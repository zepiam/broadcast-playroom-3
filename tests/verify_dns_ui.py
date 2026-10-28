import os,sys,tempfile,threading
from pathlib import Path
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev,network_dns
with tempfile.TemporaryDirectory(prefix='bp3-dns-ui-') as folder:
 launch_dev.dns_settings=launch_dev.DnsSettings(Path(folder)/'dns.json');launch_dev.tts_service.dns_settings=launch_dev.dns_settings
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;launch_dev.save_layout({'activePageId':'one','pages':[{'id':'one','widgets':[]}]})
 original=network_dns.test_dns_connection;calls=[];network_dns.test_dns_connection=lambda service,custom:(calls.append((service,custom)) or (True,125.4,'127.0.0.1','ok'))
 server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1280,'height':850});page=ctx.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('networking')");settings.wait_for_timeout(300)
   assert not settings.locator('#chkEnableDns').is_checked();settings.locator('#selDnsProvider').select_option('google_doh');settings.locator('#chkEnableDns').check()
   settings.wait_for_timeout(300);assert launch_dev.dns_settings.public()['service']=='google_doh' and launch_dev.dns_settings.public()['enabled']
   settings.locator('button[onclick="testCustomDns()"]').click();settings.locator('#dnsTestResult').filter(has_text='125 ms').wait_for();assert calls==[('google_doh','')]
   network_dns._DNS_CACHE['example']=(['127.0.0.1'],9999999999);settings.locator('button[onclick="clearCustomDnsCache()"]').click();settings.locator('#dnsTestResult').filter(has_text='ล้างแคช').wait_for();assert not network_dns._DNS_CACHE
   settings.close();page.reload()
   with page.expect_popup() as pop:page.locator('#btnRailSettings').click()
   settings=pop.value;settings.wait_for_load_state();settings.evaluate("switchSettingsSection('networking')");settings.wait_for_timeout(300);assert settings.locator('#selDnsProvider').input_value()=='google_doh' and settings.locator('#chkEnableDns').is_checked()
   print('PASS DNS settings, actual connector configuration, test, app cache and restart');browser.close()
 finally:network_dns.test_dns_connection=original;server.shutdown();server.server_close()
