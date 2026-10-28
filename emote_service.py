"""Twitch image proxy: read existing legacy cache or bounded CDN response."""
from pathlib import Path
import re,urllib.request,threading
class EmoteService:
 def __init__(self,cache_root=None):
  self.root=Path(cache_root) if cache_root else Path.home()/'.tts-for-livestream'/'emote_cache'
  self.memory={};self.lock=threading.Lock()
 def read(self,eid,animated=True):
  if not re.fullmatch(r'[A-Za-z0-9_-]+',eid):return None
  key=(eid,bool(animated))
  with self.lock:
   if key in self.memory:return self.memory[key]
  for ext,mime in ([('.gif','image/gif'),('.apng','image/apng'),('.png','image/png')] if animated else [('.png','image/png')]):
   file=self.root/(eid+'_1.0'+ext)
   if file.is_file() and 0<file.stat().st_size<=8*1024*1024:return file.read_bytes(),mime
  mode='animated' if animated else 'static'
  urls=[f'https://static-cdn.jtvnw.net/emoticons/v2/{eid}/{mode}/dark/1.0',f'https://static-cdn.jtvnw.net/emoticons/v2/{eid}/static/dark/1.0']
  if eid.isdigit():urls.append(f'https://static-cdn.jtvnw.net/emoticons/v1/{eid}/1.0')
  for url in dict.fromkeys(urls):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=5) as response:
     mime=response.headers.get_content_type();data=response.read(8*1024*1024+1)
    if not mime.startswith('image/') or not data or len(data)>8*1024*1024:continue
    with self.lock:
     if len(self.memory)>=64:self.memory.pop(next(iter(self.memory)))
     self.memory[key]=(data,mime)
    return data,mime
   except Exception:continue
  return None
