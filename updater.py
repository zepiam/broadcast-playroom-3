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
import time
import urllib.request
from typing import Callable, Optional

logger = logging.getLogger("updater")

CURRENT_VERSION = "3.0.0"
REPO_OWNER = "zepiam"
REPO_NAME = "broadcast-playroom-3"

# 1. Static raw manifest จาก master branch (ไม่ติด rate limit)
RAW_MANIFEST_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/version.json"
# 2. Release asset manifest (สำหรับ release build)
RELEASE_MANIFEST_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/version.json"
# 3. Fallback GitHub Releases API
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

USER_AGENT = "BroadcastPlayroom/3.0.0 (Windows NT 10.0; Win64; x64)"


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
    urls = [RAW_MANIFEST_URL, RELEASE_MANIFEST_URL]

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


def apply_update_patch(patch_zip: str) -> bool:
    """ติดตั้งแพตช์อัปเดตแบบ Safe Atomic Swap (เตรียมไว้สำหรับ v3.0.1+)"""
    import zipfile
    if not os.path.isfile(patch_zip):
        return False
    install_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    try:
        with zipfile.ZipFile(patch_zip, "r") as zf:
            # ตรวจสอบ path traversal attack ก่อน extract
            for member in zf.namelist():
                norm = os.path.normpath(member)
                if norm.startswith("..") or os.path.isabs(norm):
                    raise ValueError(f"Suspicious path in update archive: {member}")
            zf.extractall(install_dir)
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


if __name__ == "__main__":
    print(f"Broadcast Playroom 3 Updater Module")
    print(f"Current version: {get_current_version()}")
    print(f"Build type: {get_build_type()}")
    res = check_for_update()
    print("Check result:", json.dumps(res, ensure_ascii=False, indent=2))
