import asyncio,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from dns_settings import DnsSettings
import tts_service,network_dns
seen=[]
class FakeCommunicate:
 def __init__(self,*args,connector=None,**kwargs):seen.append(connector._resolver)
 async def stream(self):yield {'type':'audio','data':b'test-audio'}
original=tts_service.edge_tts.Communicate;tts_service.edge_tts.Communicate=FakeCommunicate
with tempfile.TemporaryDirectory(prefix='bp3-dns-') as folder:
 service=DnsSettings(Path(folder)/'dns.json');tts=tts_service.TTSService();tts.dns_settings=service
 try:
  assert not service.public()['enabled'];assert asyncio.run(tts.synthesize('ทดสอบ'))==b'test-audio';assert not isinstance(seen[-1],network_dns.AppDnsResolver)
  service.save({'enabled':True,'service':'google_doh','custom':''});assert asyncio.run(tts.synthesize('ทดสอบ'))==b'test-audio';assert isinstance(seen[-1],network_dns.AppDnsResolver) and seen[-1].settings.dns_service=='google_doh'
  assert DnsSettings(service.path).public()['service']=='google_doh'
  try:service.save({'enabled':True,'service':'custom','custom':'http://invalid'});raise AssertionError('insecure URL accepted')
  except ValueError:pass
  assert service.public()['service']=='google_doh'
  print('PASS default DNS, real TTS connector custom resolver, persistence and validation')
 finally:tts_service.edge_tts.Communicate=original
