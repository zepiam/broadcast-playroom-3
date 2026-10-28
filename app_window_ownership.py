"""Keep owned tool windows above the app, without pinning them above other applications."""
import os
import time
from pathlib import Path

TITLES = {
 'composer':'composer','settings':'ตั้งค่าระบบ (Settings)', 'user-manager':'จัดการผู้ชม (User Manager)',
 'voice-settings':'ตั้งค่าเสียงอ่าน (Voice Settings)','chat-settings':'chat-settings','chat-widget':'Chat Widget Customizer',
 'author-profile':'โปรไฟล์ผู้ชม','playroom':'Playroom Studio ไลฟ์ซาวด์ & คลิปสั้น',
 'giveaway':'Giveaway Tool สุ่มแจกรางวัล','ask':'ASK Widget ตั้งคำถามโหวต',
 'replie':'Replie Tools ข้อความตอบกลับ','randomizer':'Quick Randomizer สุ่มชื่อ / เลข',
}
FREE_WINDOWS = frozenset(('giveaway','ask','randomizer','replie'))

def set_owner(hwnd, owner):
    import win32con,win32gui
    previous=win32gui.GetWindow(hwnd,win32con.GW_OWNER)
    if previous != owner:
        win32gui.SetWindowLong(hwnd,win32con.GWL_HWNDPARENT,owner)
    return win32gui.GetWindow(hwnd,win32con.GW_OWNER) == owner

def set_tool_owner(name, timeout=3.0):
    if name not in TITLES:return {'ok':False,'error':'unknown window'}
    try:
        import psutil,win32con,win32gui,win32process
        profile=os.path.normcase(os.path.realpath(str(Path(os.environ.get('LOCALAPPDATA') or Path.home())/'BroadcastPlayroom3'/'browser_profile')))
        def app_process(pid):
            try:
                process=psutil.Process(pid)
                if process.name().lower() not in ('chrome.exe','msedge.exe'):return False
                return any(arg.lower().startswith('--user-data-dir=') and os.path.normcase(os.path.realpath(arg.split('=',1)[1].strip('"')))==profile for arg in process.cmdline())
            except (psutil.Error,OSError):return False
        title=TITLES[name]+' - Broadcast Playroom 3'
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            windows=[]
            def collect(hwnd,_):
                if not win32gui.IsWindowVisible(hwnd):return
                label=win32gui.GetWindowText(hwnd)
                if label not in ('Broadcast Playroom 3',title,title+' - Google Chrome',title+' - Microsoft Edge'):return
                pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                if app_process(pid):windows.append((hwnd,label,pid))
            win32gui.EnumWindows(collect,None)
            mains=[entry for entry in windows if entry[1]=='Broadcast Playroom 3']
            children=[entry for entry in windows if entry[1]!= 'Broadcast Playroom 3']
            if len(mains)==1 and len(children)==1 and mains[0][2]==children[0][2]:
                main,child=mains[0][0],children[0][0]
                previous=win32gui.GetWindow(child,win32con.GW_OWNER)
                if name in FREE_WINDOWS:
                    if previous==main:return {'ok':set_owner(child,0),'owned':False}
                    return {'ok':True,'owned':False}
                if previous not in (0,main):return {'ok':False,'error':'window already owned by another window'}
                return {'ok':set_owner(child,main),'owned':True}
            time.sleep(.15)
        return {'ok':False,'error':'application windows not found or ambiguous'}
    except Exception:
        return {'ok':False,'error':'window ownership unavailable'}
