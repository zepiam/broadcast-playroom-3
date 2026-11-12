"""updater.py — In-App Update Engine for Broadcast Playroom 3



สถาปัตยกรรมระบบอัปเดตอัตโนมัติสำหรับ Broadcast Playroom 3 (v3.0.0+)

- ตรวจสอบเวอร์ชันล่าสุดผ่าน GitHub Releases และ static manifest (version.json)

- รองรับทั้งรุ่น Full (มี RVC/PyTorch) และ Lite (ไม่มี RVC)

- ป้องกันการเขียนทับข้อมูลผู้ใช้ (Settings/Profile/Models) ใน LocalAppData เด็ดขาด

- ตรวจสอบความถูกต้องของไฟล์อัปเดตด้วย SHA-256 Checksum

"""



from __future__ import annotations



import hashlib

import json

import logging

import os

import ssl

import sys

import tempfile

import threading

import time

import urllib.request

from pathlib import Path

from typing import Callable, Optional



logger = logging.getLogger("updater")



CURRENT_VERSION = "3.72"

REPO_OWNER = "zepiam"

REPO_NAME = "broadcast-playroom-3"



PENDING_UPDATE_DIR = Path(os.environ.get('LOCALAPPDATA', '') or Path.home()) / 'BroadcastPlayroom3' / 'pending_update'

PENDING_UPDATE_MANIFEST = PENDING_UPDATE_DIR / 'update_manifest.json'

PENDING_UPDATE_ZIP = PENDING_UPDATE_DIR / 'update.zip'



_update_lock = threading.Lock()

_update_runtime_state = {

    "status": "idle",       # 'idle' | 'downloading' | 'ready_to_install' | 'error'

    "percent": 0.0,

    "bytes_done": 0,

    "bytes_total": 0,

    "version": None,

    "changelog": "",

    "error": None,

    "is_pending": False,

}

_download_thread = None



# 1. Static raw manifest จาก master branch (ไม่ติด rate limit)

# 1. Hugging Face CDN (ความเร็วสูง ไม่ติดบล็อกเน็ตในไทย)
HF_MANIFEST_URL = "https://huggingface.co/men9ch/broadcast-playroom-3/raw/main/version.json"
# 2. jsDelivr Fastly CDN
JSDELIVR_MANIFEST_URL = f"https://cdn.jsdelivr.net/gh/{REPO_OWNER}/{REPO_NAME}@master/version.json"
# 3. Static raw manifest จาก master branch
RAW_MANIFEST_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/version.json"

# 2. Release asset manifest (สำหรับ release build)

RELEASE_MANIFEST_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/version.json"

# 3. Fallback GitHub Releases API

GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"



USER_AGENT = "BroadcastPlayroom/3.1 (Windows NT 10.0; Win64; x64)"





def get_current_version() -> str:

    """อ่านเวอร์ชันปัจจุบันจาก version.json ในเครื่อง หรือคืนค่า CURRENT_VERSION"""

    install_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

    candidates = [

        os.path.join(install_dir, "version.json"),

        os.path.join(install_dir, "_internal", "version.json"),

    ]

    highest_ver = None

    for path in candidates:

        try:

            if os.path.isfile(path):

                with open(path, "r", encoding="utf-8") as f:

                    data = json.load(f)

                ver = data.get("version")

                if ver and ver != "0.0.0":

                    if highest_ver is None or is_version_newer(ver, highest_ver):

                        highest_ver = ver

        except Exception:

            pass

    # Self-heal: If CURRENT_VERSION in code is newer than stale version.json on disk, trust CURRENT_VERSION
    if highest_ver is None or is_version_newer(CURRENT_VERSION, highest_ver):
        highest_ver = CURRENT_VERSION
        for path in candidates:
            try:
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        d = json.load(f)
                    d["version"] = highest_ver
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(d, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    return highest_ver





def get_build_type() -> str:

    """ตรวจสอบประเภทของโปรแกรม: 'full' (มี RVC AI Voice) หรือ 'lite' (ไม่มี RVC)"""

    try:

        exe_name = os.path.basename(sys.executable).lower()

        if "full" in exe_name:

            return "full"

        if "lite" in exe_name:

            return "lite"

    except Exception:

        pass

    try:

        import importlib.util as _ilu  # check install without loading torch (saves RAM/CPU)

        return "full" if _ilu.find_spec("torch") is not None else "lite"

    except Exception:

        return "lite"





def _parse_version(v: str) -> list[int]:

    """แปลงสตริงเวอร์ชัน '3.0.0' หรือ 'v3.0.1' เป็น [3, 0, 0] สำหรับเปรียบเทียบ"""

    cleaned = (v or "").strip().lower().lstrip("v")

    parts = []

    for p in cleaned.split("."):

        num = ""

        for ch in p:

            if ch.isdigit():

                num += ch

            else:

                break

        if num:

            parts.append(int(num))

    return parts or [0]





def is_version_newer(remote: str, local: str) -> bool:

    """เปรียบเทียบเวอร์ชัน — คืนค่า True หาก remote ใหม่กว่า local"""

    return _parse_version(remote) > _parse_version(local)





def fetch_remote_manifest(timeout: int = 8) -> Optional[dict]:

    """ดาวน์โหลด manifest (version.json) จาก GitHub โดยมี fallback หลายช่องทาง"""

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
    }

    override_url = os.environ.get("BP3_UPDATE_MANIFEST_URL")
    if override_url:
        urls = [override_url]
    else:
        urls = [
            HF_MANIFEST_URL + f"?t={int(time.time())}",
            JSDELIVR_MANIFEST_URL + f"?t={int(time.time())}",
            RELEASE_MANIFEST_URL,
            RAW_MANIFEST_URL + f"?t={int(time.time())}",
            HF_MANIFEST_URL,
            RAW_MANIFEST_URL,
        ]



    for url in urls:

        for ctx_mode in ("win_cert", "default", "unverified"):

            try:

                ctx = None

                if ctx_mode == "win_cert":

                    ctx = ssl.create_default_context()

                    try:

                        ctx.load_default_certs()

                    except Exception:

                        pass

                elif ctx_mode == "unverified":

                    ctx = ssl._create_unverified_context()



                req = urllib.request.Request(url, headers=headers)

                kw = {"timeout": timeout}

                if ctx is not None:

                    kw["context"] = ctx



                with urllib.request.urlopen(req, **kw) as response:

                    if response.status == 200:

                        raw = response.read().decode("utf-8")

                        return json.loads(raw)

            except Exception as e:

                logger.debug(f"fetch_remote_manifest failed ({url}, {ctx_mode}): {e}")



    # Fallback to GitHub Contents API or Releases API

    contents_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"

    try:

        import base64

        req = urllib.request.Request(contents_url, headers=headers)

        with urllib.request.urlopen(req, timeout=timeout) as response:

            if response.status == 200:

                data = json.loads(response.read().decode("utf-8"))

                if "content" in data:

                    raw_content = base64.b64decode(data["content"]).decode("utf-8")

                    return json.loads(raw_content)

    except Exception as e:

        logger.debug(f"GitHub Contents API fallback failed: {e}")



    # Fallback to GitHub Releases API

    try:

        req = urllib.request.Request(GITHUB_API_URL, headers=headers)

        with urllib.request.urlopen(req, timeout=timeout) as response:

            if response.status == 200:

                data = json.loads(response.read().decode("utf-8"))

                tag_name = data.get("tag_name", "").lstrip("v")

                body = data.get("body", "")

                return {

                    "version": tag_name,

                    "changelog": body,

                    "lite": {"url": data.get("html_url", ""), "type": "installer"},

                    "full": {"url": data.get("html_url", ""), "type": "installer"},

                }

    except Exception as e:

        logger.debug(f"GitHub API fallback failed: {e}")



    return None





def check_for_update(build_type: Optional[str] = None) -> dict:

    """ตรวจสอบการอัปเดตสำหรับ Broadcast Playroom 3



    Returns dict:

      - has_update: bool

      - current_version: str

      - latest_version: str

      - changelog: str

      - download_url: str

      - sha256: str

      - build_type: str ('full' | 'lite')

      - message: str

      - status: 'up_to_date' | 'update_available' | 'error'

    """

    current_ver = get_current_version()

    bt = build_type or get_build_type()



    try:

        manifest = fetch_remote_manifest(timeout=6)

    except Exception as exc:

        return {

            "has_update": False,

            "current_version": current_ver,

            "latest_version": current_ver,

            "changelog": "",

            "download_url": "",

            "sha256": "",

            "build_type": bt,

            "status": "error",

            "message": f"ไม่สามารถตรวจสอบอัปเดตได้: {exc}",

        }



    if not manifest:

        return {

            "has_update": False,

            "current_version": current_ver,

            "latest_version": current_ver,

            "changelog": "",

            "download_url": "",

            "sha256": "",

            "build_type": bt,

            "status": "error",

            "message": "ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ตรวจสอบอัปเดตได้",

        }



    latest_ver = manifest.get("version") or manifest.get("latest_version") or current_ver

    edition_info = manifest.get(bt, {})
    if not edition_info and "packages" in manifest:
        edition_info = manifest.get("packages", {}).get(bt, {})
    if not edition_info and "patches" in manifest:
        edition_info = manifest.get("patches", {}).get(bt, {})



    if is_version_newer(latest_ver, current_ver):

        return {

            "has_update": True,

            "current_version": current_ver,

            "latest_version": latest_ver,

            "changelog": manifest.get("changelog", ""),

            "download_url": edition_info.get("url") or edition_info.get("patch_url") or "",

            "sha256": edition_info.get("sha256") or edition_info.get("patch_sha256") or "",
            "mirrors": edition_info.get("mirrors") or edition_info.get("patch_mirrors") or [],

            "build_type": bt,

            "type": edition_info.get("type", "patch"),

            "status": "update_available",

            "message": f"พบเวอร์ชันใหม่: v{latest_ver} (ปัจจุบัน v{current_ver})",

        }

    else:

        return {

            "has_update": False,

            "current_version": current_ver,

            "latest_version": latest_ver,

            "changelog": manifest.get("changelog", ""),

            "download_url": "",

            "sha256": "",

            "build_type": bt,

            "status": "up_to_date",

            "message": f"คุณกำลังใช้งานเวอร์ชันล่าสุด (v{current_ver}) แล้วครับ",

        }





def download_update_file(
    url: str,
    dest_path: str,
    on_progress: Optional[Callable[[int, int, float], None]] = None,
    expected_sha256: str = "",
    progress_callback: Optional[Callable] = None,
) -> bool:
    """ดาวน์โหลดไฟล์แพตช์/อัปเดตพร้อม Progress Callback และตรวจสอบ SHA256 Checksum (ทนทานต่อ SSL/Proxy/Antivirus)"""
    if not url:
        return False

    prog = on_progress or progress_callback
    temp_path = dest_path + ".downloading"
    
    # รองรับการเชื่อมต่อ HTTPS ทุกรูปแบบ (Windows Certs, Default, Unverified สำหรับ Antivirus SSL Inspection)
    ssl_contexts = []
    try:
        ctx_win = ssl.create_default_context()
        ctx_win.load_default_certs()
        ssl_contexts.append(ctx_win)
    except Exception:
        pass
    try:
        ssl_contexts.append(ssl.create_default_context())
    except Exception:
        pass
    try:
        ssl_contexts.append(ssl._create_unverified_context())
    except Exception:
        pass
    if not ssl_contexts:
        ssl_contexts = [None]

    last_error = None
    for ctx in ssl_contexts:
        sha = hashlib.sha256()
        total_size = 0
        downloaded = 0
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "*/*",
                "Cache-Control": "no-cache",
            })
            kw = {"timeout": 45}
            if ctx is not None:
                kw["context"] = ctx

            with urllib.request.urlopen(req, **kw) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = resp.read(64 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        sha.update(chunk)
                        downloaded += len(chunk)
                        if prog:
                            pct = (downloaded / total_size * 100) if total_size > 0 else 0.0
                            try:
                                prog(downloaded, total_size, pct)
                            except TypeError:
                                try:
                                    prog(downloaded, total_size)
                                except Exception:
                                    pass

            if expected_sha256:
                calc_hash = sha.hexdigest().lower()
                if calc_hash != expected_sha256.lower().strip():
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise ValueError(f"Checksum mismatch: expected {expected_sha256}, got {calc_hash}")

            # ป้องกัน Antivirus ล็อคไฟล์ชั่วคราวตอน rename
            for retry in range(5):
                try:
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    os.rename(temp_path, dest_path)
                    return True
                except PermissionError:
                    time.sleep(0.3)

            return True

        except Exception as e:
            last_error = e
            logger.warning(f"Download attempt failed with ctx {type(ctx)}: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            continue

    logger.error(f"Download update failed after all attempts: {last_error}")
    return False

def _merge_platform_settings_dicts(target_dict: dict, source_dict: dict):
    if not isinstance(source_dict, dict):
        return
    for k, v in source_dict.items():
        if k.startswith('channel_'):
            if v and str(v).strip():
                if k not in target_dict or not target_dict[k]:
                    target_dict[k] = str(v).strip()
        elif k.startswith('auto_connect_'):
            if k not in target_dict:
                target_dict[k] = bool(v)
        elif k == 'hidden_platforms':
            if isinstance(v, list) and v:
                if 'hidden_platforms' not in target_dict or not target_dict['hidden_platforms']:
                    target_dict['hidden_platforms'] = v
            elif 'hidden_platforms' not in target_dict:
                target_dict['hidden_platforms'] = v
        else:
            target_dict[k] = v

def _merge_user_roster_lists(base_list: list, incoming_list: list) -> list:
    """ผสานรายชื่อผู้ชมและประวัติการแชทเข้าด้วยกัน ไม่ให้ข้อมูลผู้ชมคนใดคนหนึ่งสูญหายจากการอัปเดต"""
    merged_map = {}
    for item in (base_list or []) + (incoming_list or []):
        if not isinstance(item, dict):
            continue
        u = str(item.get('username') or item.get('name') or '').strip()
        if not u:
            continue
        plat = str(item.get('platform') or 'Twitch').strip()
        k = f"{plat}:{u}".lower()
        if k not in merged_map:
            merged_map[k] = dict(item)
            merged_map[k]['username'] = u
            merged_map[k]['platform'] = plat
        else:
            cur = merged_map[k]
            cur['count'] = max(int(cur.get('count') or 0), int(item.get('count') or 0))
            cur['joinCount'] = max(int(cur.get('joinCount') or 0), int(item.get('joinCount') or 0))
            cur['lastSeen'] = max(int(cur.get('lastSeen') or 0), int(item.get('lastSeen') or 0))
            cur['isVip'] = bool(cur.get('isVip') or item.get('isVip'))
            if not cur.get('avatar') and item.get('avatar'):
                cur['avatar'] = item['avatar']
            if not cur.get('nickname') and item.get('nickname'):
                cur['nickname'] = item['nickname']
            # merge history
            h_combined = (cur.get('history') or []) + (item.get('history') or [])
            h_seen = set()
            h_unique = []
            for h in h_combined:
                if isinstance(h, dict):
                    hk = (h.get('time'), str(h.get('text') or '').strip())
                    if hk not in h_seen:
                        h_seen.add(hk)
                        h_unique.append(h)
            h_unique.sort(key=lambda x: x.get('time') or 0)
            cur['history'] = h_unique[-250:]
            # merge events
            ev_combined = (cur.get('events') or []) + (item.get('events') or [])
            ev_seen = set()
            ev_unique = []
            for ev in ev_combined:
                if isinstance(ev, dict):
                    evk = (ev.get('time'), ev.get('event'), str(ev.get('text') or '').strip())
                    if evk not in ev_seen:
                        ev_seen.add(evk)
                        ev_unique.append(ev)
            ev_unique.sort(key=lambda x: x.get('time') or 0)
            cur['events'] = ev_unique[-250:]
    return list(merged_map.values())

def backup_user_settings(install_dir: str):
    """สำรองข้อมูลการตั้งค่าและช่องทางสตรีมของผู้ใช้ทั้งหมดก่อนลงอัปเดตใหม่ โดยใช้ Deep Merge เพื่อป้องกันข้อมูลสูญหาย 100%"""
    import shutil
    try:
        lad = os.environ.get('LOCALAPPDATA', '') or str(Path.home() / 'AppData' / 'Local')
        backup_dirs = [
            Path(lad) / 'BroadcastPlayroom3' / 'settings_backup',
            Path(install_dir) / 'settings_backup'
        ]
        for b_dir in backup_dirs:
            b_dir.mkdir(parents=True, exist_ok=True)
            
        search_dirs = [
            Path(install_dir) / 'data',
            Path(install_dir) / 'userdata',
            Path(install_dir),
            Path(lad) / 'BroadcastPlayroom3',
            Path(install_dir).parent / 'data'
        ]
        
        config_names = [
            'platform_settings.json', 'composer_layout.json', 'bot_accounts.dat',
            'obs_connection.dat', 'defender_state.json', 'dns_settings.json',
            'replace_words.json', 'rvc_settings.json', 'user_roster.json'
        ]
        
        for c_name in config_names:
            if c_name == 'platform_settings.json':
                merged_settings = {}
                found_any = False
                for s_dir in search_dirs:
                    src_file = s_dir / c_name
                    if src_file.is_file() and src_file.stat().st_size > 0:
                        try:
                            with open(src_file, 'r', encoding='utf-8') as sf:
                                s_data = json.load(sf)
                            if isinstance(s_data, dict):
                                _merge_platform_settings_dicts(merged_settings, s_data)
                                found_any = True
                        except Exception:
                            pass
                if found_any and merged_settings:
                    for b_dir in backup_dirs:
                        try:
                            with open(b_dir / c_name, 'w', encoding='utf-8') as bf:
                                json.dump(merged_settings, bf, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                continue

            if c_name == 'user_roster.json':
                merged_roster = []
                found_any = False
                for s_dir in search_dirs:
                    src_file = s_dir / c_name
                    if src_file.is_file() and src_file.stat().st_size > 0:
                        try:
                            with open(src_file, 'r', encoding='utf-8') as sf:
                                s_data = json.load(sf)
                            items = s_data.get('roster') if isinstance(s_data, dict) and isinstance(s_data.get('roster'), list) else s_data
                            if isinstance(items, list) and len(items) > 0:
                                merged_roster = _merge_user_roster_lists(merged_roster, items)
                                found_any = True
                        except Exception:
                            pass
                if found_any and len(merged_roster) > 0:
                    for b_dir in backup_dirs:
                        try:
                            with open(b_dir / c_name, 'w', encoding='utf-8') as bf:
                                json.dump(merged_roster, bf, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                continue

            best_src = None
            best_mtime = -1
            for s_dir in search_dirs:
                src_file = s_dir / c_name
                if src_file.is_file() and src_file.stat().st_size > 0:
                    try:
                        mt = src_file.stat().st_mtime
                        if mt > best_mtime:
                            best_mtime = mt
                            best_src = src_file
                    except Exception:
                        pass
            if best_src:
                for b_dir in backup_dirs:
                    try:
                        dst = b_dir / c_name
                        shutil.copy2(best_src, dst)
                    except Exception:
                        pass
    except Exception as e:
        logger.warning(f"Failed to backup user settings: {e}")

def restore_user_settings(install_dir: str):
    """กู้คืนไฟล์คอนฟิกกลับมายังไดเรกทอรี data โดยใช้ Deep Merge เพื่อผสานข้อมูลเดิมและใหม่เข้าด้วยกัน ไม่มีการเขียนทับจนข้อมูลหาย"""
    import shutil
    try:
        lad = os.environ.get('LOCALAPPDATA', '') or str(Path.home() / 'AppData' / 'Local')
        backup_dirs = [
            Path(lad) / 'BroadcastPlayroom3' / 'settings_backup',
            Path(install_dir) / 'settings_backup'
        ]
        target_dirs = [
            Path(install_dir) / 'data',
            Path(lad) / 'BroadcastPlayroom3',
            Path(install_dir).parent / 'data'
        ]
        config_names = [
            'platform_settings.json', 'composer_layout.json', 'bot_accounts.dat',
            'obs_connection.dat', 'defender_state.json', 'dns_settings.json',
            'replace_words.json', 'rvc_settings.json', 'user_roster.json'
        ]
        for c_name in config_names:
            if c_name == 'platform_settings.json':
                merged_settings = {}
                for b_dir in backup_dirs:
                    b_file = b_dir / c_name
                    if b_file.is_file() and b_file.stat().st_size > 0:
                        try:
                            with open(b_file, 'r', encoding='utf-8') as bf:
                                b_data = json.load(bf)
                            if isinstance(b_data, dict):
                                _merge_platform_settings_dicts(merged_settings, b_data)
                        except Exception:
                            pass
                if merged_settings:
                    for t_dir in target_dirs:
                        if t_dir.exists():
                            try:
                                cur_data = {}
                                t_file = t_dir / c_name
                                if t_file.is_file() and t_file.stat().st_size > 0:
                                    try:
                                        with open(t_file, 'r', encoding='utf-8') as tf:
                                            cur_data = json.load(tf)
                                    except Exception:
                                        cur_data = {}
                                _merge_platform_settings_dicts(cur_data, merged_settings)
                                with open(t_file, 'w', encoding='utf-8') as tf:
                                    json.dump(cur_data, tf, ensure_ascii=False, indent=2)
                            except Exception:
                                pass
                continue

            found_src = None
            best_mtime = -1
            for b_dir in backup_dirs:
                candidate = b_dir / c_name
                if candidate.is_file() and candidate.stat().st_size > 0:
                    try:
                        mt = candidate.stat().st_mtime
                        if mt > best_mtime:
                            best_mtime = mt
                            found_src = candidate
                    except Exception:
                        pass
            if found_src:
                for t_dir in target_dirs:
                    if t_dir.exists():
                        target_file = t_dir / c_name
                        try:
                            if c_name.endswith('.json') and target_file.exists() and target_file.stat().st_size > 0:
                                try:
                                    with open(target_file, 'r', encoding='utf-8') as tf:
                                        t_data = json.load(tf)
                                    with open(found_src, 'r', encoding='utf-8') as sf:
                                        s_data = json.load(sf)
                                    if isinstance(t_data, dict) and isinstance(s_data, dict):
                                        t_data.update(s_data)
                                        with open(target_file, 'w', encoding='utf-8') as tf:
                                            json.dump(t_data, tf, ensure_ascii=False, indent=2)
                                        continue
                                    elif isinstance(t_data, list) and isinstance(s_data, list):
                                        merged_list = _merge_user_roster_lists(t_data, s_data)
                                        with open(target_file, 'w', encoding='utf-8') as tf:
                                            json.dump(merged_list, tf, ensure_ascii=False, indent=2)
                                        continue
                                except Exception:
                                    pass
                            shutil.copy2(found_src, target_file)
                        except Exception:
                            pass
    except Exception as e:
        logger.warning(f"Failed to restore user settings: {e}")

def apply_update_patch(patch_zip: str) -> bool:

    """ติดตั้งแพตช์อัปเดตแบบ Safe Atomic Swap (เตรียมไว้สำหรับ v3.0.1+)"""

    import zipfile

    if not os.path.isfile(patch_zip):

        return False

    install_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

    try:

        backup_user_settings(install_dir)
        with zipfile.ZipFile(patch_zip, "r") as zf:

            # ตรวจสอบ path traversal attack ก่อน extract

            for member in zf.namelist():

                norm = os.path.normpath(member)

                if norm.startswith("..") or os.path.isabs(norm):

                    raise ValueError(f"Suspicious path in update archive: {member}")

            zf.extractall(install_dir)
            internal_dir = os.path.join(install_dir, "_internal")
            if os.path.isdir(internal_dir):
                zf.extractall(internal_dir)
        restore_user_settings(install_dir)
        # Clean up legacy un-obfuscated development folders to protect app credentials
        try:
            import shutil
            from pathlib import Path
            for legacy_sub in [
                'broadcast playroom dev',
                '_internal/broadcast playroom dev',
                '../broadcast playroom dev'
            ]:
                leg_p = Path(install_dir) / legacy_sub
                if leg_p.is_dir():
                    shutil.rmtree(leg_p, ignore_errors=True)
        except Exception:
            pass
        # Purge stale WebView2 and browser profile caches so updated code loads immediately
        try:
            import shutil
            from pathlib import Path
            app_data_candidates = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "BroadcastPlayroom3",
                Path(install_dir) / "data",
                Path(install_dir).parent / "data",
                Path(install_dir)
            ]
            for root_c in app_data_candidates:
                wv_dir = root_c / "webview_data"
                if wv_dir.is_dir():
                    for sub in ["EBWebView/Default/Cache", "EBWebView/Default/Code Cache", "EBWebView/Default/GPUCache", "EBWebView/Default/DawnCache", "Default/Cache", "Default/Code Cache"]:
                        c_path = wv_dir / sub
                        if c_path.is_dir():
                            shutil.rmtree(c_path, ignore_errors=True)
                bp_dir = root_c / "browser_profile"
                if bp_dir.is_dir():
                    for sub in ["Default/Cache", "Default/Code Cache", "GrShaderCache", "ShaderCache"]:
                        c_path = bp_dir / sub
                        if c_path.is_dir():
                            shutil.rmtree(c_path, ignore_errors=True)
        except Exception:
            pass
        return True

    except Exception as e:

        logger.error(f"Failed to apply patch: {e}")

        return False





def restart_application():

    """สั่งรีสตาร์ทกระบวนการโปรแกรมใหม่"""

    import subprocess

    import threading



    def _do_restart():

        time.sleep(1.0)

        try:

            if getattr(sys, "frozen", False):

                subprocess.Popen([sys.executable], close_fds=True)

            else:

                subprocess.Popen([sys.executable] + sys.argv, close_fds=True)

        except Exception as e:

            logger.error(f"Restart failed: {e}")

        finally:

            os._exit(0)



    t = threading.Thread(target=_do_restart, daemon=True)

    t.start()





def perform_update_and_restart(build_type: Optional[str] = None) -> dict:
    """ดาวน์โหลด ติดตั้งแพตช์อัปเดต และรีสตาร์ทโปรแกรมอัตโนมัติ"""
    info = check_for_update(build_type)

    if not info.get("has_update"):
        return {
            "success": False,
            "message": "โปรแกรมเป็นเวอร์ชันล่าสุดแล้ว",
            "restarting": False,
        }

    download_url = info.get("download_url", "")
    expected_sha = info.get("sha256", "")

    if not download_url:
        return {
            "success": False,
            "message": "ไม่พบที่อยู่ดาวน์โหลดไฟล์อัปเดต",
            "restarting": False,
        }

    if download_url.endswith(".zip"):
        import tempfile
        temp_dir = tempfile.gettempdir()
        dest_zip = os.path.join(temp_dir, f"bp3_update_{info.get('latest_version')}.zip")

        candidate_urls = [download_url] + [m for m in info.get("mirrors", []) if m and m != download_url]
        downloaded = False
        for cur_url in candidate_urls:
            if cur_url != download_url:
                logger.info(f"Failing over to mirror: {cur_url}")
            downloaded = download_update_file(cur_url, dest_zip, expected_sha256=expected_sha)
            if downloaded:
                break

        if not downloaded:
            return {
                "success": False,
                "message": "ดาวน์โหลดไฟล์อัปเดตไม่สำเร็จ กรุณาลองใหม่อีกครั้ง",
                "restarting": False,
            }

        # รัน restart_application_with_patch เพื่อให้ process ปิดตัวลงก่อนคลายไฟล์ทับ ป้องกัน Error 13 Permission Denied
        restart_application_with_patch(dest_zip)
        return {
            "success": True,
            "message": "ดาวน์โหลดสำเร็จ กำลังรีสตาร์ทเพื่อติดตั้งอัปเดต...",
            "restarting": True,
        }

    return {
        "success": False,
        "message": "รูปแบบไฟล์อัปเดตไม่ถูกต้อง",
        "restarting": False,
    }


def get_update_runtime_status() -> dict:

    """คืนค่าสถานะการอัปเดต ณ ปัจจุบัน (idle, downloading, ready_to_install, error)"""

    with _update_lock:

        st = dict(_update_runtime_state)



    # หากไม่ได้กำลังดาวน์โหลด แต่มี pending update ที่ดาวน์โหลดเสร็จสมบูรณ์ค้างอยู่บนดิสก์

    if st["status"] != "downloading":

        if PENDING_UPDATE_MANIFEST.is_file() and PENDING_UPDATE_ZIP.is_file():

            try:

                data = json.loads(PENDING_UPDATE_MANIFEST.read_text(encoding="utf-8"))

                pending_ver = data.get("version")

                current_ver = get_current_version()

                if pending_ver and is_version_newer(pending_ver, current_ver) and data.get("download_completed"):

                    st["status"] = "ready_to_install"

                    st["percent"] = 100.0

                    st["version"] = pending_ver

                    st["changelog"] = data.get("changelog", "")

                    st["is_pending"] = True

            except Exception as e:

                logger.debug(f"Error reading pending update manifest: {e}")



    return st





def start_background_download(info: dict) -> dict:

    """เริ่มดาวน์โหลดไฟล์อัปเดตใหม่ในเบื้องหลังทันทีโดยไม่ขัดขวางการทำงานของผู้ใช้"""

    global _download_thread



    latest_ver = info.get("latest_version")

    download_url = info.get("download_url")

    expected_sha = info.get("sha256", "")

    changelog = info.get("changelog", "")



    if not download_url or not latest_ver:

        return get_update_runtime_status()



    # ตรวจสอบว่ามีไฟล์ที่ดาวน์โหลดเสร็จแล้วในเครื่องหรือไม่

    current_st = get_update_runtime_status()

    if current_st["status"] == "ready_to_install" and current_st.get("version") == latest_ver:

        return current_st



    with _update_lock:

        if _update_runtime_state["status"] == "downloading":

            return dict(_update_runtime_state)

        _update_runtime_state["status"] = "downloading"

        _update_runtime_state["percent"] = 0.0

        _update_runtime_state["bytes_done"] = 0

        _update_runtime_state["bytes_total"] = 0

        _update_runtime_state["version"] = latest_ver

        _update_runtime_state["changelog"] = changelog

        _update_runtime_state["error"] = None

        _update_runtime_state["is_pending"] = False



    def _worker():
        nonlocal download_url
        try:

            PENDING_UPDATE_DIR.mkdir(parents=True, exist_ok=True)

            target_zip = PENDING_UPDATE_ZIP



            def _on_prog(done, total, pct):

                with _update_lock:

                    _update_runtime_state["bytes_done"] = done

                    _update_runtime_state["bytes_total"] = total

                    _update_runtime_state["percent"] = round(pct, 1)



            # Candidate URLs: primary download_url first, mirrors as backup fallback
            urls_to_try = []
            if download_url:
                urls_to_try.append(download_url)
            mirrors = info.get("mirrors") or []
            for m in mirrors:
                if m and m not in urls_to_try:
                    urls_to_try.append(m)

            ok = False
            for cand_url in urls_to_try:
                ok = download_update_file(
                    cand_url,
                    str(target_zip),
                    on_progress=_on_prog,
                    expected_sha256=expected_sha,
                )
                if ok:
                    download_url = cand_url
                    break



            if not ok:

                with _update_lock:

                    _update_runtime_state["status"] = "error"

                    _update_runtime_state["error"] = "ดาวน์โหลดไฟล์อัปเดตไม่สำเร็จ"

                return



            manifest_data = {

                "version": latest_ver,

                "download_url": download_url,

                "sha256": expected_sha,

                "changelog": changelog,

                "download_completed": True,

                "timestamp": time.time(),

            }

            PENDING_UPDATE_MANIFEST.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")



            with _update_lock:

                _update_runtime_state["status"] = "ready_to_install"

                _update_runtime_state["percent"] = 100.0

                _update_runtime_state["is_pending"] = True

                _update_runtime_state["error"] = None

            logger.info(f"Background update download completed for v{latest_ver}")

        except Exception as e:

            logger.error(f"Background update download error: {e}")

            with _update_lock:

                _update_runtime_state["status"] = "error"

                _update_runtime_state["error"] = str(e)



    _download_thread = threading.Thread(target=_worker, daemon=True, name="BP3-Update-Downloader")

    _download_thread.start()

    return get_update_runtime_status()





def apply_pending_update_on_startup(splash_ctrl=None) -> bool:

    """ติดตั้งอัปเดตที่ดาวน์โหลดค้างไว้โดยอัตโนมัติขณะเปิดโปรแกรม (ก่อนเริ่มเซิร์ฟเวอร์ใดๆ)"""

    try:

        if not PENDING_UPDATE_MANIFEST.is_file() or not PENDING_UPDATE_ZIP.is_file():

            return False



        data = json.loads(PENDING_UPDATE_MANIFEST.read_text(encoding="utf-8"))

        pending_ver = data.get("version")

        current_ver = get_current_version()



        if not pending_ver or not data.get("download_completed"):

            return False



        if not is_version_newer(pending_ver, current_ver):

            # หากเวอร์ชันที่ค้างอยู่ไม่ได้ใหม่กว่าปัจจุบัน ให้ลบทิ้ง

            try:

                PENDING_UPDATE_ZIP.unlink(missing_ok=True)

                PENDING_UPDATE_MANIFEST.unlink(missing_ok=True)

            except Exception:

                pass

            return False



        logger.info(f"Found pending update v{pending_ver} (current: v{current_ver}). Applying update...")

        if splash_ctrl:

            try:

                splash_ctrl.set_progress(10, f"กำลังติดตั้งอัปเดตอัตโนมัติเป็น v{pending_ver}...")

            except Exception:

                pass



        applied = apply_update_patch(str(PENDING_UPDATE_ZIP))

        if applied:

            try:

                PENDING_UPDATE_ZIP.unlink(missing_ok=True)

                PENDING_UPDATE_MANIFEST.unlink(missing_ok=True)

            except Exception:

                pass

            if splash_ctrl:

                try:

                    splash_ctrl.set_progress(25, f"อัปเดตเป็น v{pending_ver} สำเร็จเรียบร้อย กำลังเริ่มต้นระบบ...")

                except Exception:

                    pass

            logger.info(f"Successfully applied pending update to v{pending_ver}")

            return True

        else:

            logger.error(f"Failed to extract pending update v{pending_ver}")

            try:

                PENDING_UPDATE_ZIP.unlink(missing_ok=True)

                PENDING_UPDATE_MANIFEST.unlink(missing_ok=True)

            except Exception:

                pass

            return False

    except Exception as e:

        logger.error(f"apply_pending_update_on_startup error: {e}")

        return False





def restart_application_with_patch(patch_zip: Optional[str] = None):

    """สั่งรีสตาร์ทกระบวนการโปรแกรมใหม่ โดยหากมี patch_zip จะรอ process เดิมปิดแล้วแตก zip ทับก่อนเริ่มรันใหม่"""

    import subprocess

    import threading



    def _do_restart():

        time.sleep(1.0)

        try:

            install_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

            exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])



            if patch_zip and os.path.isfile(patch_zip):

                bat_script = rf"""@echo off

set "BP3_WAIT_COUNT=0"
:wait_for_exit
tasklist /FI "PID eq {os.getpid()}" /NH | findstr /R /C:" {os.getpid()} " >nul
if errorlevel 1 goto wait_extra
set /a BP3_WAIT_COUNT+=1
if %BP3_WAIT_COUNT% GEQ 120 goto update_failed
timeout /t 1 /nobreak >nul
goto wait_for_exit

:wait_extra
rem Allow OS and Windows Defender 2 seconds to release file handles completely
timeout /t 2 /nobreak >nul
:apply_patch
if not exist "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup" mkdir "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup"
if exist "{install_dir}\..\data\platform_settings.json" copy /y "{install_dir}\..\data\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul
if exist "{install_dir}\data\platform_settings.json" copy /y "{install_dir}\data\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul
if exist "%LOCALAPPDATA%\BroadcastPlayroom3\platform_settings.json" copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul

rem Backup user roster safely: only copy if non-empty (>10 bytes)
if exist "{install_dir}\..\data\user_roster.json" for %%F in ("{install_dir}\..\data\user_roster.json") do if %%~zF GTR 10 copy /y "%%~fF" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul
if exist "{install_dir}\data\user_roster.json" for %%F in ("{install_dir}\data\user_roster.json") do if %%~zF GTR 10 copy /y "%%~fF" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul
if exist "%LOCALAPPDATA%\BroadcastPlayroom3\user_roster.json" for %%F in ("%LOCALAPPDATA%\BroadcastPlayroom3\user_roster.json") do if %%~zF GTR 10 copy /y "%%~fF" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul

set "BP3_TAR_RETRY=0"
:do_tar
tar -xf "{patch_zip}" -C "{install_dir}"
if not errorlevel 1 goto tar_done
set /a BP3_TAR_RETRY+=1
if %BP3_TAR_RETRY% GEQ 5 goto update_failed
timeout /t 2 /nobreak >nul
goto do_tar
:tar_done
if exist "{install_dir}\_internal" (
    if exist "{install_dir}\dist" xcopy /e /y /q "{install_dir}\dist" "{install_dir}\_internal\dist\" >nul
    if exist "{install_dir}\updater.py" copy /y "{install_dir}\updater.py" "{install_dir}\_internal\" >nul
    if exist "{install_dir}\launch_dev.py" copy /y "{install_dir}\launch_dev.py" "{install_dir}\_internal\" >nul
    if exist "{install_dir}\version.json" copy /y "{install_dir}\version.json" "{install_dir}\_internal\" >nul
    if exist "{install_dir}\desktop_overlay_service.py" copy /y "{install_dir}\desktop_overlay_service.py" "{install_dir}\_internal\" >nul
    if exist "{install_dir}\desktop_overlay_qt.py" copy /y "{install_dir}\desktop_overlay_qt.py" "{install_dir}\_internal\" >nul
    if exist "{install_dir}\viewer_overlay_config.py" copy /y "{install_dir}\viewer_overlay_config.py" "{install_dir}\_internal\" >nul
)

if exist "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" (
    if exist "{install_dir}\data" copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" "{install_dir}\data\" >nul
    if exist "{install_dir}\..\data" copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" "{install_dir}\..\data\" >nul
    copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\" >nul
)
if exist "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\user_roster.json" (
    for %%F in ("%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\user_roster.json") do if %%~zF GTR 10 (
        if exist "{install_dir}\data" copy /y "%%~fF" "{install_dir}\data\" >nul
        if exist "{install_dir}\..\data" copy /y "%%~fF" "{install_dir}\..\data\" >nul
        copy /y "%%~fF" "%LOCALAPPDATA%\BroadcastPlayroom3\" >nul
    )
)

del "{patch_zip}"

rem Purge WebView2 & Browser Profile stale caches to ensure updated HTML/JS is executed
for %%D in ("{install_dir}\data\browser_profile" "{install_dir}\..\data\browser_profile" "%LOCALAPPDATA%\BroadcastPlayroom3\browser_profile" "%LOCALAPPDATA%\BroadcastPlayroom3\data\browser_profile" "{install_dir}\data\webview_data" "{install_dir}\..\data\webview_data" "%LOCALAPPDATA%\BroadcastPlayroom3\webview_data" "%LOCALAPPDATA%\BroadcastPlayroom3\data\webview_data") do (
    if exist "%%~D\EBWebView\Default\Cache" rmdir /s /q "%%~D\EBWebView\Default\Cache" >nul 2>&1
    if exist "%%~D\EBWebView\Default\Code Cache" rmdir /s /q "%%~D\EBWebView\Default\Code Cache" >nul 2>&1
    if exist "%%~D\EBWebView\Default\GPUCache" rmdir /s /q "%%~D\EBWebView\Default\GPUCache" >nul 2>&1
    if exist "%%~D\EBWebView\Default\DawnCache" rmdir /s /q "%%~D\EBWebView\Default\DawnCache" >nul 2>&1
    if exist "%%~D\Default\Cache" rmdir /s /q "%%~D\Default\Cache" >nul 2>&1
    if exist "%%~D\Default\Code Cache" rmdir /s /q "%%~D\Default\Code Cache" >nul 2>&1
    if exist "%%~D\Default\GPUCache" rmdir /s /q "%%~D\Default\GPUCache" >nul 2>&1
    if exist "%%~D\ShaderCache" rmdir /s /q "%%~D\ShaderCache" >nul 2>&1
)

if exist "{install_dir}\broadcast playroom dev" rmdir /s /q "{install_dir}\broadcast playroom dev" >nul 2>&1
if exist "{install_dir}\..\broadcast playroom dev" rmdir /s /q "{install_dir}\..\broadcast playroom dev" >nul 2>&1
if exist "{install_dir}\_internal\broadcast playroom dev" rmdir /s /q "{install_dir}\_internal\broadcast playroom dev" >nul 2>&1

start "" "{exe_path}"

del "%~f0"
exit /b 0
:update_failed
echo Update failed. Archive retained: "{patch_zip}" > "{install_dir}\update_failure.txt"
exit /b 1

"""

                bat_path = os.path.join(tempfile.gettempdir(), "bp3_finish_update.bat")

                with open(bat_path, "w", encoding="utf-8") as f:

                    f.write(bat_script)

                subprocess.Popen(["cmd.exe", "/c", bat_path], close_fds=True, creationflags=0x08000000 if os.name == 'nt' else 0)

            else:

                if getattr(sys, "frozen", False):

                    subprocess.Popen([sys.executable], close_fds=True)

                else:

                    subprocess.Popen([sys.executable] + sys.argv, close_fds=True)

        except Exception as e:

            logger.error(f"Restart failed: {e}")

        finally:

            os._exit(0)



    t = threading.Thread(target=_do_restart, daemon=True)

    t.start()





def restart_and_apply_update() -> dict:

    """สั่งติดตั้งและรีสตาร์ทโปรแกรมทันที (เมื่อผู้ใช้กดปุ่ม OK ในกล่องข้อความอัปเดต)"""

    if PENDING_UPDATE_ZIP.is_file():

        # ถ้ามี pending zip ที่พร้อมติดตั้งอยู่แล้ว

        try:

            PENDING_UPDATE_MANIFEST.unlink(missing_ok=True)

        except Exception:

            pass

        restart_application_with_patch(str(PENDING_UPDATE_ZIP))

        return {

            "success": True,

            "message": "กำลังรีสตาร์ทเพื่อติดตั้งอัปเดต...",

            "restarting": True,

        }



    # หากยังไม่ได้โหลดล่วงหน้า ให้ fallback ไปโหลดและรีสตาร์ท

    return perform_update_and_restart()





if __name__ == "__main__":

    print(f"Broadcast Playroom 3 Updater Module")

    print(f"Current version: {get_current_version()}")

    print(f"Build type: {get_build_type()}")

    res = check_for_update()

    print("Check result:", json.dumps(res, ensure_ascii=False, indent=2))

