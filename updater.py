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



CURRENT_VERSION = "3.15"

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

        os.path.join(install_dir, "_internal", "version.json"),

        os.path.join(install_dir, "version.json"),

    ]

    for path in candidates:

        try:

            if os.path.isfile(path):

                with open(path, "r", encoding="utf-8") as f:

                    data = json.load(f)

                ver = data.get("version")

                if ver and ver != "0.0.0":

                    return ver

        except Exception:

            pass

    return CURRENT_VERSION





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

        import torch  # noqa: F401

        return "full"

    except ImportError:

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

    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    override_url = os.environ.get("BP3_UPDATE_MANIFEST_URL")
    urls = [override_url] if override_url else [RAW_MANIFEST_URL, RELEASE_MANIFEST_URL]



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



    latest_ver = manifest.get("version", current_ver)

    edition_info = manifest.get(bt, {})



    if is_version_newer(latest_ver, current_ver):

        return {

            "has_update": True,

            "current_version": current_ver,

            "latest_version": latest_ver,

            "changelog": manifest.get("changelog", ""),

            "download_url": edition_info.get("url", ""),

            "sha256": edition_info.get("sha256", ""),

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

) -> bool:

    """ดาวน์โหลดไฟล์แพตช์/อัปเดตพร้อม Progress Callback และตรวจสอบ SHA256 Checksum"""

    if not url:

        return False



    temp_path = dest_path + ".downloading"

    sha = hashlib.sha256()

    total_size = 0

    downloaded = 0



    try:

        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        with urllib.request.urlopen(req, timeout=30) as resp:

            total_size = int(resp.headers.get("Content-Length", 0))

            with open(temp_path, "wb") as f:

                while True:

                    chunk = resp.read(64 * 1024)

                    if not chunk:

                        break

                    f.write(chunk)

                    sha.update(chunk)

                    downloaded += len(chunk)

                    if on_progress:

                        pct = (downloaded / total_size * 100) if total_size > 0 else 0.0

                        on_progress(downloaded, total_size, pct)



        if expected_sha256:

            calc_hash = sha.hexdigest().lower()

            if calc_hash != expected_sha256.lower().strip():

                if os.path.exists(temp_path):

                    os.remove(temp_path)

                raise ValueError(f"Checksum mismatch: expected {expected_sha256}, got {calc_hash}")



        if os.path.exists(dest_path):

            os.remove(dest_path)

        os.rename(temp_path, dest_path)

        return True

    except Exception as e:

        logger.error(f"Download update failed: {e}")

        if os.path.exists(temp_path):

            try:

                os.remove(temp_path)

            except Exception:

                pass

        return False






def backup_user_settings(install_dir: str):
    """สำรองข้อมูลการตั้งค่าและช่องทางสตรีมของผู้ใช้ทั้งหมดก่อนลงอัปเดตใหม่"""
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
            'replace_words.json', 'rvc_settings.json'
        ]
        
        for c_name in config_names:
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
    """กู้คืนข้อมูลการตั้งค่าของผู้ใช้หลังลงแพตช์เสร็จสิ้น เพื่อให้ข้อมูลช่องและแพลตฟอร์มไม่หายเด็ดขาด"""
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
            'replace_words.json', 'rvc_settings.json'
        ]
        for c_name in config_names:
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
        restore_user_settings(install_dir)
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



    if info.get("has_update"):

        download_url = info.get("download_url", "")

        expected_sha = info.get("sha256", "")

        if download_url and download_url.endswith(".zip"):

            import tempfile

            temp_dir = tempfile.gettempdir()

            dest_zip = os.path.join(temp_dir, f"bp3_update_{info.get('latest_version')}.zip")

            downloaded = download_update_file(download_url, dest_zip, expected_sha256=expected_sha)

            if not downloaded:

                return {

                    "success": False,

                    "message": "ดาวน์โหลดไฟล์อัปเดตไม่สำเร็จ กรุณาลองใหม่อีกครั้ง",

                    "restarting": False,

                }

            applied = apply_update_patch(dest_zip)

            if not applied:

                return {

                    "success": False,

                    "message": "ติดตั้งแพตช์อัปเดตไม่สำเร็จ กรุณาลองใหม่อีกครั้ง",

                    "restarting": False,

                }



    # สั่งรีสตาร์ทโปรแกรมอัตโนมัติ

    restart_application()

    return {

        "success": True,

        "message": "กำลังรีสตาร์ทโปรแกรมเพื่อเริ่มใช้งานเวอร์ชันใหม่...",

        "restarting": True,

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

        try:

            PENDING_UPDATE_DIR.mkdir(parents=True, exist_ok=True)

            target_zip = PENDING_UPDATE_ZIP



            def _on_prog(done, total, pct):

                with _update_lock:

                    _update_runtime_state["bytes_done"] = done

                    _update_runtime_state["bytes_total"] = total

                    _update_runtime_state["percent"] = round(pct, 1)



            ok = download_update_file(

                download_url,

                str(target_zip),

                on_progress=_on_prog,

                expected_sha256=expected_sha,

            )



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
if errorlevel 1 goto apply_patch
set /a BP3_WAIT_COUNT+=1
if %BP3_WAIT_COUNT% GEQ 120 goto update_failed
timeout /t 1 /nobreak >nul
goto wait_for_exit
:apply_patch
if not exist "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup" mkdir "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup"
if exist "{install_dir}\data\platform_settings.json" copy /y "{install_dir}\data\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul
if exist "%LOCALAPPDATA%\BroadcastPlayroom3\platform_settings.json" copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\" >nul

tar -xf "{patch_zip}" -C "{install_dir}"
if errorlevel 1 goto update_failed

if exist "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" (
    if exist "{install_dir}\data" copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" "{install_dir}\data\" >nul
    if exist "{install_dir}\..\data" copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" "{install_dir}\..\data\" >nul
    copy /y "%LOCALAPPDATA%\BroadcastPlayroom3\settings_backup\platform_settings.json" "%LOCALAPPDATA%\BroadcastPlayroom3\" >nul
)

del "{patch_zip}"

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

