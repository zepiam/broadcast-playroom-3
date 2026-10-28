"""Read-only serving of v2 media IDs and explicitly registered clips."""
import mimetypes, os, re
from pathlib import Path
from urllib.parse import unquote
MEDIA_ROOT=Path(os.environ.get('BP3_LEGACY_MEDIA_ROOT',str(Path.home()/'.tts-for-livestream')))
APP_ROOT=Path(__file__).resolve().parent
SAFE_ID=re.compile(r'^[A-Za-z0-9_-]+$')
def find_media(path,layout):
 parts=[unquote(p) for p in path.strip('/').split('/')]
 if len(parts)==3 and parts[0]=='avatar-preset':
  roles={'idle':'1','talk':'2','blink_idle':'3','blink_talk':'4'}
  if parts[1] in ('man','girl') and parts[2] in roles:
   candidate=APP_ROOT/'src'/'assets'/'avatar'/(parts[1]+roles[parts[2]]+'.png')
   return candidate if candidate.is_file() else None
 if len(parts)==3 and parts[0] in ('widget-image','widget-video'):
  kind,wid,mid=parts
  if not SAFE_ID.fullmatch(wid) or not SAFE_ID.fullmatch(mid):return None
  if not any(str(w.get('id'))==wid for p in layout.get('pages',[]) for w in p.get('widgets',[])):return None
  folder='widget_images' if kind=='widget-image' else 'widget_videos'
  extensions=('.png','.jpg','.jpeg','.webp','.gif','.svg') if kind=='widget-image' else ('.mp4','.webm','.mov','.ogv')
  for ext in extensions:
   candidate=MEDIA_ROOT/folder/wid/(mid+ext)
   if candidate.is_file():return candidate
 if len(parts)==2 and parts[0]=='character' and SAFE_ID.fullmatch(parts[1]):
  settings=layout.get('legacyChat') or {}
  configured=next((job.get('image') for job in settings.get('character_jobs',[]) if str(job.get('name','')).lower()==parts[1].lower() and job.get('image')),None)
  configured=configured or settings.get('character_default_image')
  if configured:
   candidate=Path(configured)
   if not candidate.is_absolute():candidate=APP_ROOT/candidate
   if candidate.is_file() and candidate.suffix.lower() in ('.png','.jpg','.jpeg','.gif','.webp'):return candidate

  for ext in ('.png','.jpg','.jpeg','.gif','.webp'):
   candidate=MEDIA_ROOT/'character_images'/(parts[1]+ext)
   if candidate.is_file():return candidate
  candidate=APP_ROOT/'src'/'assets'/'legacy_character.png'
  if candidate.is_file():return candidate
 if len(parts)==2 and parts[0]=='clip':
  for trigger in layout.get('legacyPlayroomTriggers',[]):
   for clip in trigger.get('clips',[]):
    if clip.get('name')==parts[1] and clip.get('path'):
     candidate=Path(clip['path'])
     if not candidate.is_absolute():candidate=APP_ROOT/candidate
     if candidate.suffix.lower() in ('.mp4','.webm','.mov','.ogv','.png','.jpg','.jpeg','.gif','.webp','.bmp','.svg','.mp3','.wav','.ogg') and candidate.is_file():return candidate
 return None
def serve_media(handler,path):
 size=path.stat().st_size;start,end=0,size-1;range_header=handler.headers.get('Range')
 if range_header:
  match=re.fullmatch(r'bytes=(\d*)-(\d*)',range_header.strip())
  if not match or not any(match.groups()):handler.send_error(416);return
  first,last=match.groups()
  if first:start=int(first);end=min(int(last),end) if last else end
  else:start=max(0,size-int(last))
  if start>=size or end<start:
   handler.send_response(416);handler.send_header('Content-Range',f'bytes */{size}');handler.end_headers();return
 handler.send_response(206 if range_header else 200)
 handler.send_header('Content-Type',mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
 handler.send_header('Accept-Ranges','bytes');handler.send_header('Content-Length',str(max(0,end-start+1)))
 if range_header:handler.send_header('Content-Range',f'bytes {start}-{end}/{size}')
 handler.send_header('Cache-Control','no-cache');handler.send_cors_headers();handler.end_headers()
 with path.open('rb') as stream:
  stream.seek(start);remaining=end-start+1
  while remaining>0:
   data=stream.read(min(65536,remaining))
   if not data:break
   handler.wfile.write(data);remaining-=len(data)
