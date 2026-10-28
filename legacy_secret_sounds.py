"""Expose only sound files explicitly configured in the previous app."""
import hashlib,json,threading
from pathlib import Path
from legacy_user_filters import candidates

class LegacySecretSounds:
    EXTENSIONS={'.mp3','.wav','.ogg','.flac','.m4a','.aac'}
    def __init__(self):self.paths={};self.lock=threading.Lock()
    def read(self, paths=None):
        for settings_path in paths if paths is not None else candidates():
            try:
                settings_path=Path(settings_path)
                if not settings_path.is_file() or settings_path.stat().st_size>4*1024*1024:continue
                data=json.loads(settings_path.read_text(encoding='utf8'))
                if not isinstance(data,dict) or not isinstance(data.get('secret_codes'),list):continue
                rows=[];paths_by_id={}
                for entry in data['secret_codes'][:1000]:
                    if not isinstance(entry,dict):continue
                    code=str(entry.get('code','')).strip()[:100];raw=str(entry.get('sound_path','')).strip()
                    if not code or not raw:continue
                    path=Path(raw)
                    if not path.is_absolute():path=(settings_path.parent.parent/path).resolve()
                    try:available=path.is_file() and path.suffix.lower() in self.EXTENSIONS
                    except OSError:available=False
                    ident=hashlib.sha256(str(path).encode('utf8')).hexdigest()
                    if available:paths_by_id[ident]=path
                    try:volume=max(0,min(1,float(entry.get('volume',1))))
                    except (TypeError,ValueError):volume=1
                    rows.append({'code':code,'name':path.name,'url':'/legacy-secret-sound/'+ident if available else '', 'volume':volume,'available':available})
                try:limit=max(0,min(100,int(data.get('secret_code_daily_limit',0))))
                except (TypeError,ValueError):limit=0
                with self.lock:self.paths=paths_by_id
                return {'found':True,'entries':rows,'daily_limit':limit,'muted':bool(data.get('code_sound_muted',False))}
            except (OSError,ValueError,TypeError):continue
        return {'found':False,'entries':[],'daily_limit':0,'muted':False}
    def find(self, ident):
        with self.lock:path=self.paths.get(ident)
        return path if path and path.is_file() and path.suffix.lower() in self.EXTENSIONS else None
