"""App-owned global Clip Marker shortcut; never suppresses the underlying key."""
import json, os, tempfile, threading
from pathlib import Path

class ClipHotkey:
    def __init__(self, path, markers, keyboard_module=None):
        self.path=Path(path);self.markers=markers;self.keyboard=keyboard_module;self.lock=threading.RLock();self.busy=threading.Lock();self.handle=None;self.message='';self.shortcut='f9'
        try:
            if self.path.exists():self.shortcut=str(json.loads(self.path.read_text(encoding='utf8')).get('shortcut','f9'))
        except (OSError,ValueError,TypeError):self.message='อ่านปุ่มลัดไม่ได้ ใช้ F9'

    def _module(self):
        if self.keyboard is None:import keyboard;self.keyboard=keyboard
        return self.keyboard

    def public(self):
        with self.lock:return {'shortcut':self.shortcut,'active':self.handle is not None,'message':self.message}

    def _fire(self):
        if not self.busy.acquire(blocking=False):return
        def run():
            try:
                result=self.markers.mark()
                with self.lock:self.message=result.get('message','')
            except Exception:
                with self.lock:self.message='มาร์กคลิปไม่สำเร็จ'
            finally:self.busy.release()
        threading.Thread(target=run,name='clip-hotkey-action',daemon=True).start()

    def set(self, shortcut, save=True):
        shortcut=str(shortcut).strip().lower()
        if len(shortcut)>60 or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789 +-' for c in shortcut):raise ValueError('รูปแบบปุ่มลัดไม่ถูกต้อง')
        with self.lock:
            old=self.handle
            if shortcut==self.shortcut and old is not None:return self.public()
            new=None
            if shortcut:
                try:new=self._module().add_hotkey(shortcut,self._fire,suppress=False)
                except Exception:raise ValueError('ตั้งปุ่มลัดไม่สำเร็จ กรุณาตรวจรูปแบบหรือปุ่มที่ถูกใช้อยู่')
            try:
                if save:
                    self.path.parent.mkdir(parents=True,exist_ok=True);temp=None
                    try:
                        with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',dir=self.path.parent,delete=False) as out:temp=out.name;json.dump({'shortcut':shortcut},out)
                        os.replace(temp,self.path);temp=None
                    finally:
                        if temp and os.path.exists(temp):os.unlink(temp)
            except Exception:
                if new is not None:self._module().remove_hotkey(new)
                raise
            self.handle=new;self.shortcut=shortcut;self.message=''
            if old is not None:
                try:self._module().remove_hotkey(old)
                except Exception:pass
            return self.public()

    def start(self):
        try:self.set(self.shortcut,save=False)
        except (ValueError,ImportError):
            with self.lock:self.message='เปิดปุ่มลัดมาร์กคลิปไม่สำเร็จ'

    def stop(self):
        with self.lock:
            if self.handle is not None:
                try:self._module().remove_hotkey(self.handle)
                except Exception:pass
                self.handle=None
