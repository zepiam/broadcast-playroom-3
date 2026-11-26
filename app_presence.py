"""Main-window presence, including minimized windows with throttled JS timers."""
import threading
import time
import uuid
from collections import deque

class AppPresence:
    def __init__(self):
        self.lock=threading.Lock()
        self.sessions={}
        self.ever_connected=False
        self.inactive_since=None
        self.launch_reserved_until=0
        self.closing=False
        self.closed=deque(maxlen=256)
        self.hold_since=None
        self.hold_notified=False

    def open(self,client):
        with self.lock:
            if self.closing or client in self.closed:return None
            self.launch_reserved_until=0
            self.ever_connected=True
            self.inactive_since=None
            token=uuid.uuid4().hex
            self.sessions[token]=(client,time.monotonic())
            return token

    def touch(self,token):
        with self.lock:
            value=self.sessions.get(token)
            if self.closing or not value or value[0] in self.closed:return False
            self.sessions[token]=(value[0],time.monotonic())
            return True

    def close(self,token):
        with self.lock:self.sessions.pop(token,None)

    def leave(self,client):
        with self.lock:
            self.closed.append(client)
            for token,value in list(self.sessions.items()):
                if value[0]==client:self.sessions.pop(token,None)

    def status(self):
        with self.lock:
            now=time.monotonic()
            self.sessions={token:value for token,value in self.sessions.items() if now-value[1]<6}
            return {'active':bool(self.sessions) and not self.closing,'closing':self.closing}

    def reserve_launch(self,seconds=15):
        with self.lock:
            if self.closing:return False
            self.launch_reserved_until=time.monotonic()+seconds
            return True

    def should_exit(self,grace=3,browser_alive=None,hold_max=600,on_hold=None):
        """True once no app window has been connected for `grace` seconds.
        browser_alive(): if the app's browser process is still running, the page lost its connection
        without the user closing the window (crashed/grey/frozen page). Stay up (at most hold_max s)
        so the UI watchdog can restart the window instead of the whole program silently quitting."""
        active=self.status()['active']
        with self.lock:
            now=time.monotonic()
            if active:
                self.inactive_since=None
                self.hold_since=None
                return False
            if not self.ever_connected or now<self.launch_reserved_until:return False
            if self.inactive_since is None:self.inactive_since=now
            if now-self.inactive_since<grace:return False
        if browser_alive is not None:
            try:alive=bool(browser_alive())
            except Exception:alive=False
            if alive:
                notify=False
                with self.lock:
                    if getattr(self,'hold_since',None) is None:
                        self.hold_since=now;self.hold_notified=False
                    # a normal close ends the browser within a second or two; only report real holds
                    if not self.hold_notified and now-self.hold_since>=10:
                        self.hold_notified=True;notify=True
                    held=now-self.hold_since
                if notify and on_hold:
                    try:on_hold()
                    except Exception:pass
                if held<hold_max:return False
        with self.lock:
            self.closing=True
            return True

    def begin_shutdown(self):
        with self.lock:self.closing=True


app_presence=AppPresence()
