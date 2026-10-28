"""Persistent opt-in DNS configuration, scoped to TTS within the app."""
import ipaddress,json,os,tempfile,threading
from pathlib import Path
from urllib.parse import urlsplit
from network_dns import DOH_PRESETS,clear_dns_cache
class DnsSettings:
 def __init__(self,path):
  self.path=Path(path);self.lock=threading.RLock();self.config={'enabled':False,'service':'cloudflare_doh','custom':''}
  try:
   if self.path.exists():self.config.update(self._validate(json.loads(self.path.read_text(encoding='utf8'))))
  except (OSError,ValueError,TypeError,AttributeError):pass
 def _validate(self,data):
  service=data.get('service','cloudflare_doh');custom=str(data.get('custom','')).strip()
  if service not in DOH_PRESETS or len(custom)>500:raise ValueError('Invalid DNS configuration')
  if service=='custom':
   if custom.startswith('https://'):
    parsed=urlsplit(custom)
    if not parsed.hostname or parsed.username or parsed.password or parsed.fragment:raise ValueError('Invalid DNS address')
   else:
    try:ipaddress.IPv4Address(custom)
    except ValueError:raise ValueError('Invalid DNS address')
  return {'enabled':data.get('enabled') is True,'service':service,'custom':custom}
 def public(self):
  with self.lock:return dict(self.config)
 def save(self,data):
  config=self._validate(data)
  with self.lock:
   self.path.parent.mkdir(parents=True,exist_ok=True);tmp=None
   try:
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',dir=self.path.parent,delete=False) as f:tmp=f.name;json.dump(config,f)
    os.replace(tmp,self.path);tmp=None
   finally:
    if tmp and os.path.exists(tmp):os.unlink(tmp)
   if config!=self.config:clear_dns_cache()
   self.config=config
  return self.public()
