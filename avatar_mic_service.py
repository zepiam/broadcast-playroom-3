"""Configured PNGTuber microphone state using the legacy PyAudio reader."""
import threading,time,statistics
from mic_level_watcher import MicLevelWatcher
from overlay_events import overlay_events

class AvatarMicService:
    def __init__(self,factory=MicLevelWatcher,relay=overlay_events):
        self.factory=factory;self.relay=relay;self.lock=threading.RLock();self.instances={}

    def sync(self,layout):
        desired={}
        for page in (layout or {}).get('pages',[]):
            for w in page.get('widgets',[]):
                if w.get('type')!='avatar' or w.get('hidden') or w.get('avatar_mode',w.get('avatarMode','tts'))!='mic':continue
                raw=w.get('avatar_mic_device',w.get('avatarMicDevice',''))
                try:device=int(raw) if raw not in ('',None) else None
                except (ValueError,TypeError):device=None
                threshold=max(-60,min(0,float(w.get('avatar_mic_threshold',w.get('avatarMicThreshold',-35)))))
                gain=max(1,min(1000,float(w.get('avatar_mic_gain',w.get('avatarMicGain',100)))))
                desired[str(w['id'])]=(device,threshold,gain)
        to_stop=[]
        with self.lock:
            for wid in list(self.instances):
                if desired.get(wid)!=self.instances[wid]['signature']:
                    instance=self.instances.pop(wid);to_stop.append(instance['watcher'])
                    self.relay.publish({'event':'AVATAR_STATE','payload':{'widget_id':wid,'talking':False}})
            for wid,signature in desired.items():
                if wid in self.instances:continue
                instance=dict(signature=signature,talking=False,loud=0,silent=0,threshold=signature[1],samples=[],started=time.monotonic(),calibrated=False)
                def level(db,wid=wid,instance=instance):
                    with self.lock:
                        if self.instances.get(wid) is not instance:return
                        if not instance['calibrated']:
                            instance['samples'].append(float(db))
                            if time.monotonic()-instance['started']>=2:
                                floor=statistics.median(instance['samples'])
                                if instance['threshold']<floor:instance['threshold']=min(-5,floor+5)
                                instance['samples']=[];instance['calibrated']=True
                        if db>instance['threshold']:
                            instance['loud']+=1;instance['silent']=0
                            talking=True if instance['loud']>=2 else instance['talking']
                        else:
                            instance['silent']+=1;instance['loud']=0
                            talking=False if instance['silent']>=5 else instance['talking']
                        if talking!=instance['talking']:
                            instance['talking']=talking
                            self.relay.publish({'event':'AVATAR_STATE','payload':{'widget_id':wid,'talking':talking}})
                watcher=self.factory(on_level=level,device_index=signature[0],gain=signature[2]);instance['watcher']=watcher
                self.instances[wid]=instance;watcher.start()
        for watcher in to_stop:watcher.stop()

    def stop(self):
        with self.lock:old=list(self.instances.values());self.instances.clear()
        for instance in old:instance['watcher'].stop()

avatar_mic_service=AvatarMicService()
