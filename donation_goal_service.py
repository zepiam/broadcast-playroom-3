"""Legacy EasyDonate watchers, scoped to configured widgets and current layout."""
import threading
from easydonate_api import DonateGoalWatcher

class DonationGoalService:
    def __init__(self, factory=DonateGoalWatcher):
        self.factory=factory
        self.lock=threading.RLock()
        self.watchers={}
        self.states={}

    def sync(self,layout):
        desired={}
        for page in (layout or {}).get('pages',[]):
            for widget in page.get('widgets',[]):
                if widget.get('type')=='donate_goal' and not widget.get('hidden'):
                    key=str(widget.get('dg_api_key') or widget.get('dgApiKey') or '').strip()
                    if key:
                        desired[str(widget['id'])]=(key,float(widget.get('dg_goal_amount') or widget.get('dgGoalAmount') or 1000))
        with self.lock:
            for wid in list(self.watchers):
                signature,watcher=self.watchers[wid]
                if desired.get(wid)!=signature:
                    self.watchers.pop(wid);self.states.pop(wid,None)
                    threading.Thread(target=watcher.stop,daemon=True).start()
            for wid,signature in desired.items():
                if wid in self.watchers:continue
                def update(current,goal,donor,amount,count,wid=wid,signature=signature):
                    with self.lock:
                        if wid not in self.watchers or self.watchers[wid][0]!=signature:return
                        self.states[wid]=dict(widget_id=wid,current=current,goal=goal,last_donor=donor,last_amount=amount,donor_count=count,status='ready')
                watcher=self.factory(signature[0],on_update=update)
                self.watchers[wid]=(signature,watcher)
                self.states[wid]=dict(widget_id=wid,current=0,goal=signature[1],last_donor='',last_amount=0,donor_count=0,status='loading')
                def start(wid=wid,signature=signature,watcher=watcher):
                    ok=watcher.start(goal_amount=signature[1])
                    with self.lock:
                        still_current=self.watchers.get(wid)==(signature,watcher)
                        if still_current and not ok:self.states[wid]['status']='error'
                    if not still_current:watcher.stop()
                threading.Thread(target=start,name='BP3-DonationGoal',daemon=True).start()

    def snapshot(self):
        with self.lock:return {wid:dict(data) for wid,data in self.states.items()}

    def stop(self):
        with self.lock:
            old=list(self.watchers.values());self.watchers.clear()
        for _,watcher in old:watcher.stop()

donation_goal_service=DonationGoalService()
