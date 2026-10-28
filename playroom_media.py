"""Local media imports stored by content hash; legacy files are never moved."""
import hashlib,os,re,tempfile
from pathlib import Path
from urllib.parse import unquote

class PlayroomMedia:
    MAX_SIZE=512*1024*1024
    IMAGE={'.png','.jpg','.jpeg','.webp','.gif','.bmp','.svg'}
    VIDEO={'.mp4','.webm','.mov','.ogv'}
    AUDIO={'.mp3','.wav','.ogg','.flac','.m4a','.aac'}
    def __init__(self,root=None):self.root=Path(root or Path.home()/'.tts-for-livestream'/'playroom_uploads')
    def import_file(self,stream,size,filename):
        name=unquote(filename)
        if not name or any(char in name for char in ('/','\\','\0')):raise ValueError('Invalid filename')
        ext=Path(name).suffix.lower()
        if ext not in self.IMAGE|self.VIDEO|self.AUDIO:raise ValueError('Unsupported media file type')
        if not 0<size<=self.MAX_SIZE:raise ValueError('Media file must be 1 byte to 512 MB')
        self.root.mkdir(parents=True,exist_ok=True)
        descriptor,temp=tempfile.mkstemp(prefix='.upload-',dir=self.root)
        try:
            digest=hashlib.sha256();remaining=size
            with os.fdopen(descriptor,'wb') as output:
                while remaining:
                    chunk=stream.read(min(1024*1024,remaining))
                    if not chunk:raise ValueError('Incomplete file upload')
                    output.write(chunk);digest.update(chunk);remaining-=len(chunk)
            identifier=digest.hexdigest()+ext;target=self.root/identifier
            if target.exists():os.unlink(temp)
            else:os.replace(temp,target)
            return dict(name=Path(name).stem,url='/playroom-media/'+identifier,type='image' if ext in self.IMAGE else 'video' if ext in self.VIDEO else 'audio',size=size)
        finally:
            if os.path.exists(temp):os.unlink(temp)
    def find(self,path):
        identifier=path.removeprefix('/playroom-media/')
        if not re.fullmatch(r'[a-f0-9]{64}\.[a-z0-9]+',identifier):return None
        target=self.root/identifier
        if target.suffix not in self.IMAGE|self.VIDEO|self.AUDIO:return None
        return target if target.is_file() else None

playroom_media=PlayroomMedia()
