"""Local OAuth accounts for the bot. Tokens never leave the backend API."""
import importlib
import json
import os
import tempfile
import threading
import time
from pathlib import Path

class OAuthFlowError(Exception):
    pass

class BotAccounts:
    def __init__(self, path, apply_account=None, modules=None, protect=None, unprotect=None):
        self.path=Path(path);self.apply_account=apply_account or (lambda platform, account: None)
        self.generations={p:0 for p in ('twitch','kick')};self.modules=modules or {};self.lock=threading.RLock();self.accounts={};self.statuses={p:{'state':'disconnected'} for p in ('twitch','kick')}
        if protect is None or unprotect is None:
            import win32crypt
            protect=lambda data:win32crypt.CryptProtectData(data,'Broadcast Playroom bot',None,None,None,0)
            unprotect=lambda data:win32crypt.CryptUnprotectData(data,None,None,None,0)[1]
        self.protect=protect;self.unprotect=unprotect
        try:
            if self.path.exists():
                data=json.loads(self.unprotect(self.path.read_bytes()).decode('utf-8'))
                if isinstance(data,dict): self.accounts={k:v for k,v in data.items() if k in self.statuses and isinstance(v,dict)}
                for p,account in self.accounts.items(): self.statuses[p]={'state':'saved','username':account.get('username','')}
        except Exception:
            for p in self.statuses:self.statuses[p]={'state':'error','error':'ไม่สามารถอ่านบัญชีบอทที่บันทึกไว้'}

    def _module(self, platform):
        return self.modules.get(platform) or importlib.import_module(platform+'_oauth')

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        encrypted=self.protect(json.dumps(self.accounts,ensure_ascii=False).encode('utf-8'))
        tmp=None
        try:
            with tempfile.NamedTemporaryFile(dir=self.path.parent,delete=False) as out:
                tmp=out.name;out.write(encrypted)
            os.replace(tmp,self.path);tmp=None
        finally:
            if tmp:
                try:os.unlink(tmp)
                except OSError:pass

    def public(self):
        with self.lock:
            result = {p: dict(s) for p, s in self.statuses.items()}
            for platform, account in self.accounts.items():
                if account.get('username'):
                    result[platform]['username'] = account['username']
            return result

    def get(self, platform):
        with self.lock:
            account=dict(self.accounts.get(platform) or {})
            generation=self.generations.get(platform)
        if not account:return None
        if account.get('expires_at') and account['expires_at'] <= time.time()+120:
            if not account.get('refresh_token'):
                with self.lock:self.statuses[platform]={'state':'error','error':'สิทธิ์หมดอายุ กรุณาเชื่อมบัญชีใหม่'}
                return None
            try:
                refreshed=self._module(platform).refresh_access_token(account['refresh_token'])
                if not refreshed or not refreshed.get('access_token'):raise ValueError('refresh failed')
                previous_refresh=account.get('refresh_token');account.update(refreshed)
                account['refresh_token']=refreshed.get('refresh_token') or previous_refresh
                account['expires_at']=time.time()+int(refreshed['expires_in']) if refreshed.get('expires_in') else 0
                with self.lock:
                    if self.generations.get(platform)!=generation:return None
                    self.accounts[platform]=account;self._save()
            except Exception:
                with self.lock:
                    if self.generations.get(platform)==generation:self.statuses[platform]={'state':'error','error':'ต่ออายุสิทธิ์ไม่สำเร็จ กรุณาเชื่อมบัญชีใหม่'}
                return None
        return account

    def start(self, platform):
        if platform not in self.statuses:raise ValueError('Unknown platform')
        module=self._module(platform)
        if hasattr(module,'DEFAULT_CLIENT_ID') and not module.DEFAULT_CLIENT_ID:
            raise ValueError('ไม่พบข้อมูลแอปสำหรับเชื่อมบัญชี โปรดตรวจสอบแพ็กเกจโปรแกรม')
        if hasattr(module,'DEFAULT_CLIENT_SECRET') and not module.DEFAULT_CLIENT_SECRET:
            raise ValueError('ไม่พบข้อมูลแอปสำหรับเชื่อมบัญชี โปรดตรวจสอบแพ็กเกจโปรแกรม')
        with self.lock:
            if self.statuses[platform].get('state')=='authorizing':raise ValueError('กำลังเชื่อมบัญชีอยู่')
            self.generations[platform]+=1;generation=self.generations[platform]
            self.statuses[platform]={'state':'authorizing'}
        def work():
            try:
                result=module.start_oauth_flow()
                if not result or not result.get('access_token') or not result.get('username'):raise ValueError('authorization failed')
                account={k:result.get(k) for k in ('access_token','refresh_token','username','user_id')}
                account['expires_at']=time.time()+int(result.get('expires_in') or 0) if result.get('expires_in') else 0
                with self.lock:
                    if self.generations[platform]!=generation:return
                    self.accounts[platform]=account;self._save();self.statuses[platform]={'state':'saved','username':account['username']}
                self.apply_account(platform, account)
            except Exception as exc:
                with self.lock:
                    if self.generations[platform]==generation:self.statuses[platform]={'state':'error','error':str(exc) if isinstance(exc, OAuthFlowError) else 'เชื่อมบัญชีไม่สำเร็จหรือถูกยกเลิก'}
        thread=threading.Thread(target=work,name='BotOAuth-'+platform,daemon=True);thread.start()

    def refresh_tokens(self, platform, access, refresh, expires=0):
        with self.lock:
            account=self.accounts.get(platform)
            if not account:return
            account.update(access_token=access, refresh_token=refresh or account.get('refresh_token'), expires_at=time.time()+int(expires) if expires else 0)
            self._save()

    def disconnect(self, platform):
        with self.lock:
            self.generations[platform]+=1
            self.accounts.pop(platform,None);self._save();self.statuses[platform]={'state':'disconnected'}
        self.apply_account(platform,None)
