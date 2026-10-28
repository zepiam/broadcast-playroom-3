"""FULL-only RVC models, downloads and voice conversion. Heavy imports are lazy."""
from __future__ import annotations
import hashlib, importlib.util, io, json, logging, os, shutil, tempfile, threading
from pathlib import Path

ROOT=Path(__file__).resolve().parent

class RVCService:
    def __init__(self, edition=None, model_dir=None, state_file=None, roots=None, engine_factory=None, downloader=None):
        self.edition=(edition or os.environ.get('BP3_EDITION','full')).lower()
        if self.edition not in ('full','lite'):raise ValueError('Edition must be full or lite')
        data_root=Path(os.environ.get('BP3_DATA_DIR', ROOT))
        self.model_dir=Path(model_dir or data_root/'rvc_models')
        self.state_file=Path(state_file or data_root/'rvc_settings.json')
        self.roots=list(roots or [self.model_dir,ROOT.parent/'broadcast playroom dev'/'rvc_models',Path.home()/'.tts-for-livestream'/'voices'])
        self.lock=threading.RLock();self.model_lock=threading.Lock()
        self.engine_factory=engine_factory;self.downloader=downloader
        self.engine=None;self.cancel_event=threading.Event();self.worker=None
        self.data={'enabled':False,'selected':None,'state':'idle','progress':0,'error':'','loaded':False}
        if self.edition=='full' and self.state_file.is_file():
            try:
                previous=json.loads(self.state_file.read_text(encoding='utf-8'))
                self.data['selected']=previous.get('selected')
                if previous.get('enabled') and self.data['selected']:
                    try:self.select(self.data['selected'],enabled=True)
                    except Exception as error:self.data.update(state='error',error=str(error),loaded=False,enabled=False)
            except (OSError,ValueError):pass

    def require_full(self):
        if self.edition!='full':raise PermissionError('RVC is available only in FULL')

    def capabilities(self):
        return {'edition':self.edition,'rvc':self.edition=='full','model_downloads':self.edition=='full'}

    def models(self):
        self.require_full();found={}
        for root in self.roots:
            root=Path(root)
            if not root.is_dir():continue
            for path in root.rglob('*.pth'):
                if any(part.startswith('.download-') for part in path.parts):continue
                resolved=path.resolve();key=hashlib.sha256(str(resolved).lower().encode()).hexdigest()[:20]
                found[key]={'id':key,'name':path.stem,'filename':path.name,'size':path.stat().st_size,'path':resolved}
        return found

    def public_models(self):
        return [{key:value for key,value in model.items() if key!='path'} for model in self.models().values()]

    def status(self):
        self.require_full()
        with self.lock:return dict(self.data,device=getattr(self.engine,'device',None) if self.engine else None)

    def _save(self):
        self.state_file.parent.mkdir(parents=True,exist_ok=True)
        temporary=self.state_file.with_suffix('.tmp')
        temporary.write_text(json.dumps({'selected':self.data['selected'],'enabled':self.data['enabled']}),encoding='utf-8')
        os.replace(temporary,self.state_file)

    def _start(self,task):
        self.require_full()
        with self.lock:
            if self.worker and self.worker.is_alive():raise ValueError('RVC is busy')
            self.cancel_event=threading.Event()
            self.worker=threading.Thread(target=task,daemon=True)
            self.worker.start()

    def select(self,model_id,enabled=True):
        self.require_full()
        if not enabled or model_id in (None,'','none'):
            with self.lock:
                if self.worker and self.worker.is_alive():raise ValueError('Wait for the current model operation')
                self.data.update(enabled=False,loaded=False,state='idle',error='')
            with self.model_lock:
                if self.engine:self.engine.unload()
                self.engine=None
            self._save();return self.status()
        model=self.models().get(model_id)
        if not model:raise ValueError('Model not found; refresh the list')
        def load():
            try:
                with self.lock:self.data.update(state='loading',selected=model_id,enabled=False,loaded=False,error='',progress=0)
                with self.model_lock:
                    if self.engine:self.engine.unload()
                    if self.engine_factory:engine=self.engine_factory(str(model['path']))
                    else:
                        from rvc_engine import RVCEngine
                        engine=RVCEngine(model_path=str(model['path']))
                    engine.load()
                    if not engine.is_loaded:raise RuntimeError('Model did not load')
                    self.engine=engine
                    matching=[p for p in model['path'].parent.glob('*.index') if model['path'].stem.lower() in p.stem.lower()]
                    self.index_path=str(matching[0]) if matching else ''
                with self.lock:self.data.update(state='ready',enabled=True,loaded=True,progress=100,error='')
                self._save()
            except Exception as error:
                logging.getLogger(__name__).exception('RVC model loading failed')
                with self.lock:self.data.update(state='error',enabled=False,loaded=False,error=str(error))
        self._start(load);return self.status()

    def catalog(self):
        self.require_full()
        from voice_downloader import get_catalog_voices
        return get_catalog_voices()

    def public_catalog(self):
        return [{'id':str(index),'name':voice.name,'category':voice.category,'size':voice.size} for index,voice in enumerate(self.catalog())]

    def download(self,catalog_id):
        self.require_full()
        catalog=self.catalog()
        try:voice=catalog[int(catalog_id)]
        except (ValueError,IndexError,TypeError):raise ValueError('Unknown catalog model')
        if int(catalog_id)<0:raise ValueError('Unknown catalog model')
        def perform():
            staging=None
            try:
                with self.lock:self.data.update(state='downloading',progress=0,error='')
                self.model_dir.mkdir(parents=True,exist_ok=True)
                staging=Path(tempfile.mkdtemp(prefix='.download-',dir=self.model_dir))
                def progress(done,total):
                    with self.lock:self.data['progress']=min(99,round(done*100/max(1,total)))
                if self.downloader:download=self.downloader
                else:
                    from voice_downloader import download_voice
                    download=download_voice
                download(voice,str(staging),progress,self.cancel_event)
                if self.cancel_event.is_set():raise InterruptedError('Download cancelled')
                files=[p for p in staging.iterdir() if p.suffix.lower() in ('.pth','.index') and p.is_file()]
                if not any(p.suffix.lower()=='.pth' for p in files):raise ValueError('Download contained no model')
                for path in files:
                    destination=self.model_dir/path.name
                    if destination.exists():raise FileExistsError('A model with this filename already exists')
                for path in files:os.replace(path,self.model_dir/path.name)
                with self.lock:self.data.update(state='ready' if self.engine else 'idle',progress=100,error='')
            except InterruptedError:
                with self.lock:self.data.update(state='ready' if self.engine else 'idle',progress=0,error='Download cancelled')
            except Exception as error:
                with self.lock:self.data.update(state='error',error=str(error))
            finally:
                if staging and staging.is_dir() and staging.resolve().parent==self.model_dir.resolve() and staging.name.startswith('.download-'):shutil.rmtree(staging)
        self._start(perform);return self.status()

    def cancel(self):
        self.require_full();self.cancel_event.set();return self.status()

    def convert(self,audio_bytes):
        if self.edition!='full':return audio_bytes,'audio/mpeg'
        with self.lock:enabled=self.data['enabled'] and self.data['loaded']
        if not enabled:return audio_bytes,'audio/mpeg'
        import numpy as np
        import soundfile as sf
        with self.model_lock:
            if not self.engine:return audio_bytes,'audio/mpeg'
            audio,sample_rate=sf.read(io.BytesIO(audio_bytes),dtype='float32')
            if getattr(audio,'ndim',1)>1:audio=audio.mean(axis=1)
            if self.engine_factory:
                result,rate=self.engine.convert_array(audio,sample_rate)
            else:
                from rvc_engine import RVCParams
                result,rate=self.engine.convert_array(audio,sample_rate,RVCParams(index_path=getattr(self,'index_path','')))
        out=io.BytesIO();sf.write(out,np.asarray(result),int(rate),format='WAV',subtype='PCM_16')
        return out.getvalue(),'audio/wav'

rvc_service=RVCService()
