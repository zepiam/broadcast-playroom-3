"""installer_gui.py — Modern Smart Web Installer for Broadcast Playroom 3

ตัวติดตั้งอัตโนมัติแบบรวมศูนย์ (Single Unified Setup Executable)
- สถาปัตยกรรมโฟลเดอร์แบบรวมศูนย์ (Unified Root Folder Structure):
  <Root>/
    ├── full/   (ไฟล์โปรแกรม Full Edition: โมเดล AI Voice RVC, PyTorch, CUDA)
    ├── lite/   (ไฟล์โปรแกรม Lite Edition: ขนาดกะทัดรัด แชทสด, TTS, โอเวอร์เลย์)
    └── data/   (ข้อมูลส่วนกลางที่แชร์ร่วมกัน: บัญชีบอท, การตั้งค่า, เลย์เอาต์, คุกกี้)
- สามารถติดตั้งทั้ง 2 เวอร์ชันในเครื่องเดียวกันได้อย่างสมบูรณ์แบบ ข้อมูลเชื่อมโยงกันอัตโนมัติ
- รองรับ Portable Mode 100%: ติดตั้งบนไดรฟ์ D:\, E:\, F:\ ฟอร์แมตเครื่องไดรฟ์ C:\ ข้อมูลก็ไม่หาย
- ระบบดาวน์โหลด Failover สลับ Hugging Face (หลัก) / Google Drive (สำรอง) อัตโนมัติ
- ระบบข้ามหน้าแจ้งเตือน Google Drive ขนาดใหญ่ (>100MB / 4GB) อัตโนมัติ
- สแกนและเพิ่ม Windows Defender Exclusion โฟลเดอร์หลักให้อัตโนมัติ
- แตกไฟล์ลงเครื่องปลายทาง และลบไฟล์บีบอัดชั่วคราวทิ้งทันที
"""
import os
import sys
import json
import time
import shutil
import zipfile
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QPixmap, QCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QCheckBox,
    QProgressBar, QStackedWidget, QFrame
)

# -------------------------------------------------------------
# DEFAULT MIRRORS CONFIGURATION
# -------------------------------------------------------------
DOWNLOAD_MIRRORS = {
    "lite": [
        # Mirror 1: Google Drive (Primary - สปีดดาวน์โหลดสูงสุดในประเทศ)
        "https://drive.google.com/uc?export=download&id=15J6EGBD3fIveLuwoJkTWBBxBbUkvdEyx",
        # Mirror 2: Hugging Face (สำรอง - ไม่จำกัด Quota/Bandwidth)
        "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/BroadcastPlayroom3-Lite.zip",
    ],
    "full": [
        # Mirror 1: Google Drive (Primary - สปีดดาวน์โหลดสูงสุดในประเทศ)
        "https://drive.google.com/uc?export=download&id=17gpfsUfVM7wt1sAS6pGj7UnAcfs6werV",
        # Mirror 2: Hugging Face (สำรอง - ไม่จำกัด Quota/Bandwidth)
        "https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/BroadcastPlayroom3-Full.zip",
    ]
}

def get_asset_path(filename):
    if hasattr(sys, '_MEIPASS'):
        for sub in ('src/assets', 'assets/icons', 'assets', ''):
            p = os.path.join(sys._MEIPASS, sub, filename) if sub else os.path.join(sys._MEIPASS, filename)
            if os.path.isfile(p):
                return p
    for base in (
        os.path.join(os.path.dirname(__file__), 'assets', 'icons'),
        os.path.join(os.path.dirname(__file__), 'src', 'assets'),
        os.path.dirname(__file__),
    ):
        p = os.path.join(base, filename)
        if os.path.isfile(p):
            return p
    return ''

DEFAULT_ROOT_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
    "Programs",
    "BroadcastPlayroom3"
)

# -------------------------------------------------------------
# DOWNLOAD & INSTALL WORKER THREAD
# -------------------------------------------------------------
class InstallWorker(QThread):
    progress_changed = Signal(int, str, str)  # (percent, title_status, detail_status)
    install_finished = Signal(bool, str)       # (success, message)

    def __init__(self, edition, root_dir, create_desktop, create_start, add_defender, launch_after):
        super().__init__()
        self.edition = edition
        self.root_dir = os.path.abspath(root_dir)
        self.edition_folder = "full" if edition == "full" else "lite"
        self.app_dir = os.path.join(self.root_dir, self.edition_folder)
        self.data_dir = os.path.join(self.root_dir, "data")
        self.create_desktop = create_desktop
        self.create_start = create_start
        self.add_defender = add_defender
        self.launch_after = launch_after
        self._is_cancelled = False

    def run(self):
        try:
            # 1. Create directory structure (Root / Edition / Data)
            os.makedirs(self.app_dir, exist_ok=True)
            os.makedirs(self.data_dir, exist_ok=True)

            # Mark root with .portable if installed on non-C: drive
            drive = os.path.splitdrive(self.root_dir)[0].upper()
            if drive and not drive.startswith("C:"):
                try:
                    with open(os.path.join(self.root_dir, ".portable"), "w", encoding="utf-8") as pf:
                        pf.write("portable=1\n")
                except Exception:
                    pass

            # 2. Windows Defender Exclusion on root folder (protects full, lite, and data)
            if self.add_defender:
                self.progress_changed.emit(5, "🛡️ กำลังตั้งค่า Windows Defender Exclusion...", f"เพิ่มข้อยกเว้นโฟลเดอร์หลัก: {self.root_dir}")
                self._apply_defender_exclusion(self.root_dir)
                time.sleep(1.0)

            # 3. Download ZIP Archive
            temp_dir = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "BP3_Installer_Temp")
            os.makedirs(temp_dir, exist_ok=True)
            zip_dest = os.path.join(temp_dir, f"bp3_{self.edition}.zip")

            # Check if local zip archive is present side-by-side with Setup.exe (Instant Local / Offline Install)
            setup_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
            local_candidates = [
                os.path.join(setup_dir, f"BroadcastPlayroom3-{self.edition.capitalize()}.zip"),
                os.path.join(setup_dir, "dist_releases", f"BroadcastPlayroom3-{self.edition.capitalize()}.zip"),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "dist_releases", f"BroadcastPlayroom3-{self.edition.capitalize()}.zip")),
            ]
            found_local = next((cand for cand in local_candidates if os.path.isfile(cand)), None)

            download_success = False
            if found_local:
                self.progress_changed.emit(40, "⚡ พบไฟล์ติดตั้งในเครื่อง (Instant Local Install)...", f"ติดตั้งจาก: {os.path.basename(found_local)}")
                shutil.copy2(found_local, zip_dest)
                download_success = True

            mirrors = DOWNLOAD_MIRRORS.get(self.edition, [])

            for idx, mirror_url in enumerate(mirrors, 1):
                if not mirror_url or "REPLACE_WITH" in mirror_url:
                    continue
                domain = self._get_domain(mirror_url)
                mirror_name = "Google Drive (ความเร็วสูง)" if "drive.google.com" in mirror_url else "Hugging Face (สำรอง)"
                self.progress_changed.emit(10, f"⏳ กำลังเชื่อมต่อเซิร์ฟเวอร์ ({mirror_name})...", f"กำลังดาวน์โหลดจาก: {domain}")
                try:
                    self._download_file(mirror_url, zip_dest)
                    download_success = True
                    break
                except Exception as e:
                    print(f"Mirror {idx} ({mirror_name}) failed: {e}")
                    self.progress_changed.emit(10, f"⚠️ เซิร์ฟเวอร์หลักจำกัดโควตา กำลังสลับไปใช้ช่องทางสำรอง...", str(e))
                    time.sleep(1.0)

            if not download_success:
                # ตรวจสอบว่ามีไฟล์ zip ในเครื่องหรือไม่ (สำหรับ offline/local test)
                local_candidates = [
                    os.path.abspath(os.path.join(os.path.dirname(__file__), "dist_releases", f"BroadcastPlayroom3-{self.edition.capitalize()}.zip")),
                    os.path.abspath(f"BroadcastPlayroom3-{self.edition.capitalize()}.zip")
                ]
                found_local = False
                for cand in local_candidates:
                    if os.path.isfile(cand):
                        shutil.copy2(cand, zip_dest)
                        found_local = True
                        break
                if not found_local:
                    self.install_finished.emit(False, "ไม่สามารถดาวน์โหลดไฟล์ติดตั้งได้ กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ตหรือลิงก์เซิร์ฟเวอร์")
                    return

            # 4. Extract Archive into app_dir (<Root>/full or <Root>/lite)
            self.progress_changed.emit(70, f"📦 กำลังแตกไฟล์ ({self.edition_folder.upper()})...", f"กำลังติดตั้งลงใน: {self.app_dir}")
            self._extract_zip(zip_dest, self.app_dir)

            # 5. Remove Temporary ZIP File Immediately (Zero Residual Waste)
            self.progress_changed.emit(90, "🧹 กำลังทำความสะอาดไฟล์ชั่วคราว...", "ลบไฟล์บีบอัดชั่วคราวทิ้ง ไม่เปลืองพื้นที่ฮาร์ดดิสก์")
            if os.path.isfile(zip_dest):
                try:
                    os.remove(zip_dest)
                except Exception:
                    pass

            # Patch PE subsystem of executable to Windows GUI (subsystem 2) so CMD NEVER opens
            exe_name = f"BroadcastPlayroom3-{self.edition.capitalize()}.exe"
            exe_path = os.path.join(self.app_dir, exe_name)
            if not os.path.isfile(exe_path):
                nested_exe = os.path.join(self.app_dir, f"BroadcastPlayroom3-{self.edition.capitalize()}", exe_name)
                if os.path.isfile(nested_exe):
                    exe_path = nested_exe

            self._patch_pe_subsystem_to_gui(exe_path)

            # 6. Create Shortcuts & Uninstaller with explicit new icon
            edition_label = "Full" if self.edition == "full" else "Lite"
            shortcut_name = f"Broadcast Playroom 3 ({edition_label}).lnk"
            self.progress_changed.emit(95, "🔗 กำลังสร้างไอคอนและชอร์ตคัต...", "บันทึกข้อมูลเข้าสู่ระบบ Windows")

            # Ensure model folder and seed default models for full edition
            if self.edition == "full":
                models_dest = os.path.join(self.data_dir, "rvc_models")
                os.makedirs(models_dest, exist_ok=True)
                dev_models = os.path.join(os.path.dirname(__file__), "rvc_models")
                if os.path.isdir(dev_models):
                    for mf in os.listdir(dev_models):
                        src_mf = os.path.join(dev_models, mf)
                        dst_mf = os.path.join(models_dest, mf)
                        if os.path.isfile(src_mf) and not os.path.exists(dst_mf):
                            try:
                                shutil.copy2(src_mf, dst_mf)
                            except Exception:
                                pass

            # Copy explicit custom icon directly into app_dir for bulletproof Windows shortcut resolution
            target_ico = f"icon_{self.edition}.ico"
            custom_ico = f"bp-{self.edition}-icon.ico"
            dest_ico_path = os.path.join(self.app_dir, target_ico)
            
            src_ico = get_asset_path(custom_ico) or get_asset_path(target_ico)
            if src_ico and os.path.isfile(src_ico):
                try:
                    shutil.copy2(src_ico, dest_ico_path)
                except Exception:
                    pass

            chosen_icon = dest_ico_path if os.path.isfile(dest_ico_path) else (src_ico or exe_path)

            if self.create_desktop:
                desktops = [os.path.join(os.environ["USERPROFILE"], "Desktop")]
                onedrive_desktop = os.path.join(os.environ["USERPROFILE"], "OneDrive", "Desktop")
                if os.path.isdir(onedrive_desktop) and onedrive_desktop not in desktops:
                    desktops.append(onedrive_desktop)
                for d in desktops:
                    self._create_shortcut(shortcut_name, exe_path, d, chosen_icon)

            if self.create_start:
                start_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Broadcast Playroom 3")
                os.makedirs(start_dir, exist_ok=True)
                self._create_shortcut(shortcut_name, exe_path, start_dir, chosen_icon)

            self._create_uninstaller(self.root_dir, self.app_dir, exe_name, edition_label)

            # Record defender state and installation record
            self._save_defender_state(self.root_dir)
            self._save_install_record(self.root_dir, self.edition)

            self.progress_changed.emit(100, "✅ ติดตั้งเสร็จสมบูรณ์ 100%!", f"พร้อมเปิดใช้งาน Broadcast Playroom 3 ({edition_label}) ทันที")
            time.sleep(0.5)

            if self.launch_after and os.path.isfile(exe_path):
                subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path), creationflags=0x08000000, close_fds=True)

            self.install_finished.emit(True, f"ติดตั้ง Broadcast Playroom 3 ({edition_label}) สำเร็จเรียบร้อยแล้วครับ!\n(ข้อมูลการใช้งานจะถูกบันทึกร่วมกันในโฟลเดอร์ data)")

        except Exception as e:
            self.install_finished.emit(False, f"เกิดข้อผิดพลาดระหว่างการติดตั้ง: {e}")

    def _patch_pe_subsystem_to_gui(self, exe_path):
        """Patch PE header subsystem from 3 (Console) to 2 (Windows GUI) to ensure ZERO CMD window ever pops up."""
        import struct
        try:
            if not os.path.isfile(exe_path):
                return
            with open(exe_path, "r+b") as f:
                f.seek(0x3C)
                pe_offset = struct.unpack("<I", f.read(4))[0]
                sub_offset = pe_offset + 0x5C
                f.seek(sub_offset)
                current_sub = struct.unpack("<H", f.read(2))[0]
                if current_sub == 3:  # IMAGE_SUBSYSTEM_WINDOWS_CUI
                    f.seek(sub_offset)
                    f.write(struct.pack("<H", 2))  # IMAGE_SUBSYSTEM_WINDOWS_GUI
                    print(f"Patched {exe_path} to Windows GUI (no console) successfully!")
        except Exception as e:
            print(f"Error patching PE subsystem: {e}")

    def _get_domain(self, url):
        try:
            return urllib.parse.urlparse(url).netloc
        except Exception:
            return url

    def _download_file(self, url, dest_path):
        import http.cookiejar
        import re

        # Normalize Hugging Face blob -> resolve
        if "huggingface.co" in url and "/blob/" in url:
            url = url.replace("/blob/", "/resolve/")

        # Smart handler for Google Drive
        if "drive.google.com" in url:
            file_id = None
            m = re.search(r'[?&]id=([0-9A-Za-z_-]+)', url)
            if m:
                file_id = m.group(1)
            else:
                m2 = re.search(r'/file/d/([0-9A-Za-z_-]+)', url)
                if m2:
                    file_id = m2.group(1)

            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            init_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            req = urllib.request.Request(init_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BroadcastPlayroomSetup/3.0"})
            resp = opener.open(req, timeout=35)
            content_type = resp.headers.get('Content-Type', '')

            if 'html' in content_type.lower():
                html = resp.read().decode('utf-8', errors='ignore')
                if "quota" in html.lower() or "too many users" in html.lower() or "exceeded" in html.lower():
                    raise RuntimeError("โควตาดาวน์โหลด Google Drive เกินขีดจำกัดชั่วคราว (กำลังสลับไปช่องทางสำรองอัตโนมัติ)")
                form_match = re.search(r'<form[^>]*action="([^"]+)"', html)
                if not form_match:
                    raise RuntimeError("Google Drive ไม่สามารถดาวน์โหลดได้ในขณะนี้ (กำลังสลับไปช่องทางสำรอง)")
                action_url = form_match.group(1)
                params = {}
                for inp in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html):
                    params[inp.group(1)] = inp.group(2)
                for inp in re.finditer(r'<input[^>]*value="([^"]*)"[^>]*name="([^"]+)"', html):
                    params[inp.group(2)] = inp.group(1)

                download_url = f"{action_url}?{urllib.parse.urlencode(params)}"
                req2 = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BroadcastPlayroomSetup/3.0"})
                resp = opener.open(req2, timeout=35)
                ct2 = resp.headers.get('Content-Type', '')
                if 'html' in ct2.lower():
                    raise RuntimeError("โควตาดาวน์โหลด Google Drive เกินขีดจำกัดชั่วคราว (กำลังสลับไปช่องทางสำรองอัตโนมัติ)")
        else:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BroadcastPlayroomSetup/3.0"}
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=35)

        with resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            start_time = time.time()

            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(128 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    elapsed = time.time() - start_time
                    speed_mb = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0.1 else 0.0

                    if total > 0:
                        pct = int(10 + (downloaded / total) * 58)  # 10% to 68%
                        mb_done = downloaded / (1024 * 1024)
                        mb_total = total / (1024 * 1024)
                        detail = f"ดาวน์โหลดแล้ว: {mb_done:.1f} / {mb_total:.1f} MB ({pct}%) • ความเร็ว: {speed_mb:.2f} MB/s"
                    else:
                        pct = 40
                        mb_done = downloaded / (1024 * 1024)
                        detail = f"ดาวน์โหลดแล้ว: {mb_done:.1f} MB • ความเร็ว: {speed_mb:.2f} MB/s"

                    self.progress_changed.emit(pct, f"⚡ กำลังดาวน์โหลดแพ็กเกจ ({self.edition.upper()})...", detail)

    def _extract_zip(self, zip_path, extract_to):
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.infolist()
            total = len(members)
            for idx, member in enumerate(members):
                zf.extract(member, extract_to)
                if idx % 100 == 0:
                    pct = int(70 + (idx / total) * 18)
                    self.progress_changed.emit(pct, "📦 กำลังแตกไฟล์และติดตั้งลงในเครื่อง...", f"กำลังแตกไฟล์: {member.filename[:45]} ({idx}/{total})")

    def _apply_defender_exclusion(self, folder_path):
        folder_clean = folder_path.replace("'", "''")
        cmd = f"Add-MpPreference -ExclusionPath '{folder_clean}' -ErrorAction SilentlyContinue"
        runner = f"Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -Command \"{cmd}\"' -Verb RunAs -WindowStyle Hidden"
        try:
            subprocess.Popen(["powershell", "-Command", runner], shell=False)
        except Exception as e:
            print(f"Defender exclusion elevation error: {e}")

    def _save_defender_state(self, folder_path):
        try:
            base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "BroadcastPlayroom3"
            base.mkdir(parents=True, exist_ok=True)
            state_file = base / "defender_state.json"
            data = {
                "excluded_path": str(folder_path),
                "applied_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "active"
            }
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _save_install_record(self, root_dir, edition):
        try:
            base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "BroadcastPlayroom3"
            base.mkdir(parents=True, exist_ok=True)
            info_file = base / "install_info.json"
            data = {}
            if info_file.is_file():
                try:
                    with open(info_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            data["root_dir"] = str(root_dir)
            editions = data.get("installed_editions", [])
            if edition not in editions:
                editions.append(edition)
            data["installed_editions"] = editions
            data["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving install record: {e}")

    def _create_shortcut(self, shortcut_name, target_path, dest_dir, icon_path=None):
        try:
            os.makedirs(dest_dir, exist_ok=True)
            lnk_path = os.path.join(dest_dir, shortcut_name).replace("'", "''")
            target_clean = target_path.replace("'", "''")
            work_dir = os.path.dirname(target_path).replace("'", "''")
            icon_script = ""
            if icon_path and os.path.isfile(icon_path):
                icon_clean = icon_path.replace("'", "''")
                icon_script = f"$Shortcut.IconLocation = '{icon_clean},0'; "
            ps = (
                f"$WshShell = New-Object -ComObject WScript.Shell; "
                f"$Shortcut = $WshShell.CreateShortcut('{lnk_path}'); "
                f"$Shortcut.TargetPath = '{target_clean}'; "
                f"$Shortcut.WorkingDirectory = '{work_dir}'; "
                f"{icon_script}"
                f"$Shortcut.Save();"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
        except Exception as e:
            print(f"Error creating shortcut: {e}")

    def _create_uninstaller(self, root_dir, app_dir, exe_name, edition_label):
        uninstall_bat = os.path.join(app_dir, 'uninstall.cmd')
        root_clean = root_dir.replace("'", "''")
        app_clean = app_dir.replace("'", "''")
        other_sub = 'lite' if edition_label == 'Full' else 'full'
        other_dir_clean = os.path.join(root_dir, other_sub).replace("'", "''")
        try:
            with open(uninstall_bat, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
chcp 65001 >nul
title ถอนการติดตั้ง Broadcast Playroom 3 ({edition_label} Edition)
cls
echo.
echo  =============================================================
echo    ยืนยันการถอนการติดตั้ง Broadcast Playroom 3 ({edition_label} Edition)
echo  =============================================================
echo.
echo  [คำเตือน] คุณกำลังจะลบโปรแกรม Broadcast Playroom 3 ({edition_label} Edition)
echo  หากเผลอกดเปิดไฟล์นี้โดยไม่ได้ตั้งใจ สามารถกดยกเลิกได้ทันทีครับ
echo.
set "confirm="
set /p confirm="  คุณต้องการถอนการติดตั้งจริงหรือไม่? [y=ยืนยันลบ / n=ยกเลิก]: "

if /i not "%confirm%"=="y" goto CANCEL

echo.
echo  =============================================================
echo    กำลังเริ่มกระบวนการถอนการติดตั้ง...
echo  =============================================================
echo.
echo  [1/3] กำลังปิดโปรแกรมที่กำลังทำงานอยู่...
taskkill /F /IM "{exe_name}" >nul 2>&1
taskkill /F /IM "QtWebEngineProcess.exe" >nul 2>&1
timeout /t 1 >nul

echo  [2/3] กำลังลบไอคอนชอร์ตคัตของ {edition_label} Edition...
del /F /Q "%USERPROFILE%\Desktop\Broadcast Playroom 3 ({edition_label}).lnk" >nul 2>&1
del /F /Q "%USERPROFILE%\OneDrive\Desktop\Broadcast Playroom 3 ({edition_label}).lnk" >nul 2>&1
del /F /Q "%PUBLIC%\Desktop\Broadcast Playroom 3 ({edition_label}).lnk" >nul 2>&1
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Broadcast Playroom 3\Broadcast Playroom 3 ({edition_label}).lnk" >nul 2>&1

echo  [3/3] กำลังลบไฟล์โปรแกรม...
cd /d "%TEMP%"
start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 1; Remove-Item -LiteralPath '{app_clean}' -Recurse -Force -ErrorAction SilentlyContinue; if (Test-Path -LiteralPath '{other_dir_clean}') {{ Write-Output 'Other edition exists, keeping root and data'; }} else {{ Remove-Item -LiteralPath '{root_clean}' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -LiteralPath '%APPDATA%\Microsoft\Windows\Start Menu\Programs\Broadcast Playroom 3' -Recurse -Force -ErrorAction SilentlyContinue; }}"

echo.
echo  =============================================================
echo    ถอนการติดตั้ง {edition_label} Edition เรียบร้อยแล้วครับ!
echo    (หากมีอีกเวอร์ชันติดตั้งอยู่ ข้อมูลส่วนกลางและเวอร์ชันนั้นจะยังคงอยู่)
echo  =============================================================
echo.
timeout /t 3 >nul
exit

:CANCEL
echo.
echo  =============================================================
echo    ยกเลิกการถอนการติดตั้งเรียบร้อยแล้ว!
echo    ไฟล์โปรแกรมและการตั้งค่าทั้งหมดยังคงอยู่ครบถ้วน ปลอดภัย 100% ครับ
echo  =============================================================
echo.
echo  กดปุ่มใดก็ได้เพื่อปิดหน้าต่างนี้...
pause >nul
exit
''')
        except Exception:
            pass

# -------------------------------------------------------------
# CUSTOM MODERN INTERACTIVE EDITION CARD
# -------------------------------------------------------------
class EditionCard(QFrame):
    clicked = Signal(str)

    def __init__(self, edition_id, title, badge_text, desc, specs, is_selected=False):
        super().__init__()
        self.edition_id = edition_id
        self.is_selected = is_selected
        self.orig_badge_text = badge_text
        self.is_installed = False
        self.setObjectName(f"card_{edition_id}")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(114)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(6)

        # Header Row
        h_row = QHBoxLayout()
        h_row.setSpacing(10)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 14.5px; font-weight: 800; color: #ffffff; background: transparent; border: none;")

        self.lbl_badge = QLabel(badge_text)
        if "แนะนำ" in badge_text:
            self.lbl_badge.setStyleSheet("font-size: 11px; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 2px 8px;")
        else:
            self.lbl_badge.setStyleSheet("font-size: 11px; font-weight: 700; color: #a1a1aa; background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 6px; padding: 2px 8px;")

        self.lbl_check = QLabel("✓")
        self.lbl_check.setAlignment(Qt.AlignCenter)
        self.lbl_check.setFixedSize(22, 22)

        h_row.addWidget(self.lbl_title)
        h_row.addWidget(self.lbl_badge)
        h_row.addStretch()
        h_row.addWidget(self.lbl_check)
        layout.addLayout(h_row)

        # Description
        self.lbl_desc = QLabel(desc)
        self.lbl_desc.setStyleSheet("font-size: 12px; color: #dbdee1; background: transparent; border: none; line-height: 1.4;")
        self.lbl_desc.setWordWrap(True)
        layout.addWidget(self.lbl_desc)

        # Specs Footnote
        self.lbl_specs = QLabel(specs)
        self.lbl_specs.setStyleSheet("font-size: 11px; color: #949ba4; background: transparent; border: none;")
        layout.addWidget(self.lbl_specs)

        self.update_style()

    def set_installed_state(self, is_installed):
        self.is_installed = is_installed
        if is_installed:
            self.lbl_badge.setText("✅ ติดตั้งแล้ว")
            self.lbl_badge.setStyleSheet("font-size: 11px; font-weight: 700; color: #4ade80; background: rgba(74, 222, 128, 0.15); border: 1px solid rgba(74, 222, 128, 0.35); border-radius: 6px; padding: 2px 8px;")
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.setStyleSheet(f"""
                QFrame#card_{self.edition_id} {{
                    background-color: #161719;
                    border: 1.5px dashed #42444a;
                    border-radius: 10px;
                }}
            """)
            self.lbl_check.setStyleSheet("background-color: rgba(74, 222, 128, 0.2); color: #4ade80; font-weight: 900; font-size: 12px; border: 1px solid #4ade80; border-radius: 11px;")
            self.lbl_check.setText("✓")
        else:
            self.lbl_badge.setText(self.orig_badge_text)
            if "แนะนำ" in self.orig_badge_text:
                self.lbl_badge.setStyleSheet("font-size: 11px; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 2px 8px;")
            else:
                self.lbl_badge.setStyleSheet("font-size: 11px; font-weight: 700; color: #a1a1aa; background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 6px; padding: 2px 8px;")
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.update_style()

    def set_selected(self, selected):
        self.is_selected = selected
        if not self.is_installed:
            self.update_style()

    def update_style(self):
        if self.is_installed:
            return
        if self.is_selected:
            self.setStyleSheet(f"""
                QFrame#card_{self.edition_id} {{
                    background-color: #1e2238;
                    border: 2px solid #5865f2;
                    border-radius: 10px;
                }}
            """)
            self.lbl_check.setStyleSheet("background-color: #5865f2; color: #ffffff; font-weight: 900; font-size: 13px; border-radius: 11px; border: none;")
            self.lbl_check.setText("✓")
        else:
            self.setStyleSheet(f"""
                QFrame#card_{self.edition_id} {{
                    background-color: #2b2d31;
                    border: 1.5px solid #3f4147;
                    border-radius: 10px;
                }}
                QFrame#card_{self.edition_id}:hover {{
                    border: 1.5px solid #5865f2;
                    background-color: #313338;
                }}
            """)
            self.lbl_check.setStyleSheet("background-color: #1e1f22; color: transparent; border: 1.5px solid #4e5058; border-radius: 11px;")
            self.lbl_check.setText("")

    def mousePressEvent(self, event):
        if self.is_installed:
            return  # Installed, disabled from clicking
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.edition_id)
        super().mousePressEvent(event)


# -------------------------------------------------------------
# MAIN MODERN INSTALLER WINDOW (PYSIDE6)
# -------------------------------------------------------------
class SetupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ติดตั้ง Broadcast Playroom 3 — Setup")
        self.resize(720, 660)
        self.setFixedSize(720, 660)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #111214;
            }
            QWidget {
                font-family: 'Segoe UI', 'Sarabun', Tahoma, sans-serif;
            }
            QLabel {
                color: #f2f3f5;
            }
            QCheckBox {
                color: #dbdee1;
                font-size: 12.5px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border-radius: 4px;
                border: 1.5px solid #4e5058;
                background-color: #2b2d31;
            }
            QCheckBox::indicator:hover {
                border-color: #5865f2;
            }
            QCheckBox::indicator:checked {
                background-color: #5865f2;
                border-color: #5865f2;
            }
            QLineEdit {
                background-color: #1e1f22;
                border: 1px solid #3f4147;
                border-radius: 6px;
                padding: 7px 12px;
                color: #38bdf8;
                font-size: 12px;
                font-family: Consolas, monospace;
            }
            QLineEdit:focus {
                border-color: #5865f2;
            }
            QPushButton.btn-browse {
                background-color: #2b2d31;
                color: #f2f3f5;
                border: 1px solid #3f4147;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton.btn-browse:hover {
                background-color: #35373c;
                border-color: #4e5058;
            }
            QPushButton.btn-cancel {
                background-color: #2b2d31;
                color: #b5bac1;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton.btn-cancel:hover {
                background-color: #35373c;
                color: #ffffff;
            }
            QPushButton.btn-primary {
                background-color: #23a55a;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 28px;
                font-size: 13.5px;
                font-weight: 700;
            }
            QPushButton.btn-primary:hover {
                background-color: #1f934f;
            }
            QProgressBar {
                background-color: #1e1f22;
                border: 1px solid #2b2d31;
                border-radius: 6px;
                height: 14px;
                text-align: center;
                color: #f2f3f5;
                font-size: 11px;
                font-weight: 700;
            }
            QProgressBar::chunk {
                background-color: #23a55a;
                border-radius: 5px;
            }
        """)

        # Set Icon
        ico = get_asset_path("icon.ico")
        if ico:
            self.setWindowIcon(QIcon(ico))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self._init_config_page()
        self._init_progress_page()
        self._init_finish_page()

    def _init_config_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(36, 24, 36, 24)
        main_layout.setSpacing(14)

        # 1. Hero Header
        header = QHBoxLayout()
        header.setSpacing(16)

        logo_path = get_asset_path("icon.png")
        lbl_logo = QLabel()
        if logo_path:
            pm = QPixmap(logo_path).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_logo.setPixmap(pm)
        lbl_logo.setFixedSize(56, 56)

        header_text = QVBoxLayout()
        header_text.setSpacing(3)
        h_title_row = QHBoxLayout()
        lbl_title = QLabel("Broadcast Playroom 3")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        lbl_tag = QLabel("v3.1 Stable")
        lbl_tag.setStyleSheet("font-size: 11px; font-weight: 700; color: #5865f2; background: rgba(88, 101, 242, 0.15); border: 1px solid rgba(88, 101, 242, 0.35); border-radius: 6px; padding: 2px 8px;")
        h_title_row.addWidget(lbl_title)
        h_title_row.addWidget(lbl_tag)
        h_title_row.addStretch()

        lbl_sub = QLabel("ระบบสตูดิโอจัดแชทสดและอินเทอร์แอกทีฟโอเวอร์เลย์สำหรับสตรีมเมอร์")
        lbl_sub.setStyleSheet("font-size: 12.5px; color: #949ba4;")

        header_text.addLayout(h_title_row)
        header_text.addWidget(lbl_sub)

        header.addWidget(lbl_logo)
        header.addLayout(header_text)
        main_layout.addLayout(header)

        # Divider
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("border: none; background-color: #232428; height: 1px;")
        main_layout.addWidget(sep)

        # 2. Selectable Cards
        lbl_select = QLabel("เลือกเวอร์ชันที่ต้องการติดตั้ง:")
        lbl_select.setStyleSheet("font-size: 13px; font-weight: 700; color: #dbdee1;")
        main_layout.addWidget(lbl_select)

        self.selected_edition = "full"

        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(16)

        self.card_full = EditionCard(
            edition_id="full",
            title="🚀 Full Edition (ครบวงจร)",
            badge_text="✨ แนะนำสำหรับสตรีมเมอร์",
            desc="บรรจุโมเดลแปลงเสียง AI Voice RVC, PyTorch, CUDA และเอฟเฟกต์เสียงอ่านสดครบครัน",
            specs="ดาวน์โหลด ~4.0 GB • พื้นที่ติดตั้ง ~6.7 GB (รองรับ GPU และ CPU)",
            is_selected=True
        )
        self.card_full.clicked.connect(self._select_edition)

        self.card_lite = EditionCard(
            edition_id="lite",
            title="⚡ Lite Edition (ขนาดกะทัดรัด)",
            badge_text="รุ่นประหยัดพื้นที่",
            desc="เน้นดึงแชทสดทุกแพลตฟอร์ม โอเวอร์เลย์ วิดเจ็ต และเสียงอ่าน TTS ทั่วไป (ไม่มี AI แปลงเสียง)",
            specs="ดาวน์โหลด ~318 MB • พื้นที่ติดตั้ง ~800 MB (เปิดโปรแกรมได้รวดเร็วทันใจ)",
            is_selected=False
        )
        self.card_lite.clicked.connect(self._select_edition)

        cards_layout.addWidget(self.card_full)
        cards_layout.addWidget(self.card_lite)
        main_layout.addLayout(cards_layout)

        # 3. Destination Root Folder
        dir_box = QVBoxLayout()
        dir_box.setSpacing(6)
        lbl_dir = QLabel("โฟลเดอร์หลักสำหรับติดตั้ง (Root Directory):")
        lbl_dir.setStyleSheet("font-size: 12px; font-weight: 700; color: #b5bac1;")

        dir_h = QHBoxLayout()
        dir_h.setSpacing(8)
        saved_root = self._get_saved_install_root()
        initial_dir = saved_root if saved_root else DEFAULT_ROOT_DIR
        self.txt_dir = QLineEdit(initial_dir)
        self.txt_dir.textChanged.connect(self._update_paths_preview)

        btn_browse = QPushButton("เลือกโฟลเดอร์...")
        btn_browse.setProperty("class", "btn-browse")
        btn_browse.setCursor(QCursor(Qt.PointingHandCursor))
        btn_browse.clicked.connect(self._browse_dir)

        dir_h.addWidget(self.txt_dir)
        dir_h.addWidget(btn_browse)

        self.lbl_path_tree = QLabel()
        self.lbl_path_tree.setWordWrap(True)

        self.lbl_portable_hint = QLabel()
        self.lbl_portable_hint.setWordWrap(True)

        dir_box.addWidget(lbl_dir)
        dir_box.addLayout(dir_h)
        dir_box.addWidget(self.lbl_path_tree)
        dir_box.addWidget(self.lbl_portable_hint)
        main_layout.addLayout(dir_box)

        # 4. Checkbox Options (2 Structured Rows to prevent text truncation)
        opt_box = QVBoxLayout()
        opt_box.setSpacing(8)

        row1 = QHBoxLayout()
        self.chk_defender = QCheckBox("🛡️ เพิ่มข้อยกเว้น Windows Defender (แนะนำ เพื่อความปลอดภัยของโมเดล AI)")
        self.chk_defender.setChecked(True)
        row1.addWidget(self.chk_defender)
        row1.addStretch()

        row2 = QHBoxLayout()
        row2.setSpacing(20)
        self.chk_desktop = QCheckBox("🖥️ สร้างไอคอน Desktop")
        self.chk_desktop.setChecked(True)
        self.chk_start = QCheckBox("📁 เพิ่มใน Start Menu")
        self.chk_start.setChecked(True)
        self.chk_launch = QCheckBox("🚀 เปิดโปรแกรมทันทีหลังติดตั้ง")
        self.chk_launch.setChecked(True)

        row2.addWidget(self.chk_desktop)
        row2.addWidget(self.chk_start)
        row2.addWidget(self.chk_launch)
        row2.addStretch()

        opt_box.addLayout(row1)
        opt_box.addLayout(row2)
        main_layout.addLayout(opt_box)

        main_layout.addStretch()

        # 5. Bottom Actions
        bottom_h = QHBoxLayout()
        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setProperty("class", "btn-cancel")
        btn_cancel.setCursor(QCursor(Qt.PointingHandCursor))
        btn_cancel.clicked.connect(self.close)

        self.btn_install = QPushButton("⚡ เริ่มการติดตั้ง (Install Now)")
        self.btn_install.setProperty("class", "btn-primary")
        self.btn_install.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_install.clicked.connect(self._start_installation)

        bottom_h.addStretch()
        bottom_h.addWidget(btn_cancel)
        bottom_h.addWidget(self.btn_install)
        main_layout.addLayout(bottom_h)

        self._update_paths_preview()

        self.stack.addWidget(page)

    def _init_progress_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 60, 48, 48)
        layout.setSpacing(20)

        # Header
        h_box = QHBoxLayout()
        lbl_p_title = QLabel("กำลังติดตั้ง Broadcast Playroom 3")
        lbl_p_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #ffffff;")
        h_box.addWidget(lbl_p_title)
        h_box.addStretch()
        layout.addLayout(h_box)

        layout.addSpacing(16)

        self.lbl_progress_title = QLabel("กำลังเตรียมการติดตั้ง...")
        self.lbl_progress_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #38bdf8;")

        self.pbar = QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setTextVisible(True)
        self.pbar.setFixedHeight(18)

        self.lbl_progress_detail = QLabel("กำลังเริ่มต้นกระบวนการ...")
        self.lbl_progress_detail.setStyleSheet("font-size: 12.5px; color: #949ba4; line-height: 1.5;")
        self.lbl_progress_detail.setWordWrap(True)

        layout.addWidget(self.lbl_progress_title)
        layout.addWidget(self.pbar)
        layout.addWidget(self.lbl_progress_detail)

        layout.addStretch()
        self.stack.addWidget(page)

    def _init_finish_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 60, 48, 48)
        layout.setSpacing(20)

        self.lbl_finish_title = QLabel("✅ ติดตั้งเสร็จสมบูรณ์!")
        self.lbl_finish_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #23a55a;")

        self.lbl_finish_msg = QLabel("Broadcast Playroom 3 ได้รับการติดตั้งลงในเครื่องของคุณเรียบร้อยแล้ว พร้อมเปิดใช้งานทันที")
        self.lbl_finish_msg.setStyleSheet("font-size: 13.5px; color: #dbdee1; line-height: 1.6;")
        self.lbl_finish_msg.setWordWrap(True)

        btn_finish = QPushButton("เสร็จสิ้น (ปิดหน้าต่าง)")
        btn_finish.setProperty("class", "btn-primary")
        btn_finish.setCursor(QCursor(Qt.PointingHandCursor))
        btn_finish.clicked.connect(self.close)

        layout.addWidget(self.lbl_finish_title)
        layout.addWidget(self.lbl_finish_msg)
        layout.addSpacing(30)
        layout.addWidget(btn_finish, alignment=Qt.AlignRight)
        layout.addStretch()

        self.stack.addWidget(page)

    def _detect_installed_editions(self, root_dir):
        if not root_dir or not os.path.isdir(root_dir):
            return False, False
        full_exe = os.path.join(root_dir, "full", "BroadcastPlayroom3-Full.exe")
        lite_exe = os.path.join(root_dir, "lite", "BroadcastPlayroom3-Lite.exe")
        return os.path.isfile(full_exe), os.path.isfile(lite_exe)

    def _get_saved_install_root(self):
        try:
            base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "BroadcastPlayroom3"
            info_file = base / "install_info.json"
            if info_file.is_file():
                with open(info_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    root_dir = data.get("root_dir")
                    if root_dir and os.path.isdir(root_dir):
                        return root_dir
        except Exception:
            pass
        if os.path.isdir(DEFAULT_ROOT_DIR):
            f_exe = os.path.join(DEFAULT_ROOT_DIR, "full", "BroadcastPlayroom3-Full.exe")
            l_exe = os.path.join(DEFAULT_ROOT_DIR, "lite", "BroadcastPlayroom3-Lite.exe")
            if os.path.isfile(f_exe) or os.path.isfile(l_exe):
                return DEFAULT_ROOT_DIR
        return ""

    def _select_edition(self, edition_id):
        has_full, has_lite = self._detect_installed_editions(self.txt_dir.text().strip())
        if edition_id == "full" and has_full:
            return
        if edition_id == "lite" and has_lite:
            return

        self.selected_edition = edition_id
        self.card_full.set_selected(edition_id == "full")
        self.card_lite.set_selected(edition_id == "lite")
        self._update_paths_preview()

    def _update_paths_preview(self):
        if not hasattr(self, 'btn_install') or not hasattr(self, 'txt_dir'):
            return
        root = self.txt_dir.text().strip()
        has_full, has_lite = self._detect_installed_editions(root)

        self.card_full.set_installed_state(has_full)
        self.card_lite.set_installed_state(has_lite)

        if has_full and not has_lite:
            self.selected_edition = "lite"
            self.card_lite.set_selected(True)
            self.card_full.set_selected(False)
            self.btn_install.setText("⚡ ติดตั้ง Lite Edition เพิ่มเติม")
            self.btn_install.setEnabled(True)
        elif has_lite and not has_full:
            self.selected_edition = "full"
            self.card_full.set_selected(True)
            self.card_lite.set_selected(False)
            self.btn_install.setText("⚡ ติดตั้ง Full Edition เพิ่มเติม")
            self.btn_install.setEnabled(True)
        elif has_full and has_lite:
            self.card_full.set_selected(False)
            self.card_lite.set_selected(False)
            self.btn_install.setText("✨ ติดตั้งครบทั้ง 2 เวอร์ชันแล้ว")
            self.btn_install.setEnabled(False)
        else:
            self.btn_install.setText("⚡ เริ่มการติดตั้ง (Install Now)")
            self.btn_install.setEnabled(True)
            self.card_full.set_selected(self.selected_edition == "full")
            self.card_lite.set_selected(self.selected_edition == "lite")

        edition_folder = "full" if self.selected_edition == "full" else "lite"
        app_target = os.path.join(root, edition_folder)
        data_target = os.path.join(root, "data")

        if has_full and has_lite:
            self.lbl_path_tree.setText(
                f"✅ <b>ตรวจพบการติดตั้งทั้ง 2 เวอร์ชันแล้วใน:</b> <span style='color: #4ade80;'>{root}</span><br>"
                f"💾 <b>ข้อมูลการใช้งานส่วนกลาง:</b> <span style='color: #a1a1aa;'>{data_target}</span>"
            )
        elif has_full or has_lite:
            installed_name = "Full Edition" if has_full else "Lite Edition"
            self.lbl_path_tree.setText(
                f"🔍 <b>ตรวจพบ {installed_name} ติดตั้งแล้วในโฟลเดอร์นี้</b> — เลือกลงอีกเวอร์ชันเพิ่มเติมได้ทันที<br>"
                f"📁 <b>ปลายทางเวอร์ชันใหม่:</b> <span style='color: #38bdf8;'>{app_target}</span> • 💾 <b>แชร์ข้อมูลร่วมกัน:</b> <span style='color: #a1a1aa;'>{data_target}</span>"
            )
        else:
            self.lbl_path_tree.setText(
                f"📁 <b>โปรแกรมจะติดตั้งลงใน:</b> <span style='color: #38bdf8;'>{app_target}</span><br>"
                f"💾 <b>ข้อมูลการใช้งานส่วนกลาง:</b> <span style='color: #a1a1aa;'>{data_target} (แชร์ร่วมกันทั้ง Full และ Lite)</span>"
            )
        self.lbl_path_tree.setStyleSheet("font-size: 11.5px; color: #dbdee1; line-height: 1.5; padding-top: 2px;")

        drive = os.path.splitdrive(root)[0].upper()
        if drive and not drive.startswith("C:"):
            self.lbl_portable_hint.setText(f"✨ <b>ตรวจพบไดรฟ์สำรอง ({drive}):</b> บันทึกข้อมูลแบบ Portable ทั้งหมดลงในไดรฟ์นี้ เมื่อฟอร์แมตเครื่อง C:\ ข้อมูลจะไม่หาย")
            self.lbl_portable_hint.setStyleSheet("font-size: 11.5px; color: #4ade80; font-weight: 500; padding-top: 3px;")
        else:
            self.lbl_portable_hint.setText("💡 <i>คำแนะนำ: หากต้องการให้ข้อมูลไม่หายเวลาฟอร์แมตคอม สามารถกด 'เลือกโฟลเดอร์...' ไปไว้ไดรฟ์ D:\ หรือ E:\ ได้ครับ</i>")
            self.lbl_portable_hint.setStyleSheet("font-size: 11px; color: #949ba4; padding-top: 2px;")

    def _browse_dir(self):
        chosen = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์หลักสำหรับติดตั้ง", self.txt_dir.text())
        if chosen:
            chosen_path = os.path.abspath(chosen)
            # If user selected an existing full/lite/data folder inside, step up 1 level
            if os.path.basename(chosen_path).lower() in ["full", "lite", "data"]:
                chosen_path = os.path.dirname(chosen_path)

            # Auto-append BroadcastPlayroom3 so it never mixes with existing personal files (e.g. Documents, Games)
            base_name = os.path.basename(chosen_path).lower()
            if not (base_name.startswith("broadcastplayroom") or base_name == "broadcast playroom 3"):
                chosen_path = os.path.join(chosen_path, "BroadcastPlayroom3")

            self.txt_dir.setText(chosen_path)

    def _start_installation(self):
        edition = self.selected_edition
        root_dir = self.txt_dir.text().strip()
        if not root_dir:
            return

        # Double safeguard: ensure root_dir has dedicated subfolder so user files are never polluted
        base_name = os.path.basename(os.path.abspath(root_dir)).lower()
        if not (base_name.startswith("broadcastplayroom") or base_name == "broadcast playroom 3"):
            root_dir = os.path.join(root_dir, "BroadcastPlayroom3")
            self.txt_dir.setText(root_dir)

        self.stack.setCurrentIndex(1)

        self.worker = InstallWorker(
            edition=edition,
            root_dir=root_dir,
            create_desktop=self.chk_desktop.isChecked(),
            create_start=self.chk_start.isChecked(),
            add_defender=self.chk_defender.isChecked(),
            launch_after=self.chk_launch.isChecked()
        )
        self.worker.progress_changed.connect(self._on_progress)
        self.worker.install_finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, pct, title, detail):
        self.pbar.setValue(pct)
        self.lbl_progress_title.setText(title)
        self.lbl_progress_detail.setText(detail)

    def _on_finished(self, success, msg):
        self.stack.setCurrentIndex(2)
        edition_label = "Full" if self.selected_edition == "full" else "Lite"
        if success:
            self.lbl_finish_title.setText(f"🎉 ติดตั้ง Broadcast Playroom 3 ({edition_label}) สำเร็จ!")
            self.lbl_finish_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #23a55a;")
            self.lbl_finish_msg.setText(msg)
        else:
            self.lbl_finish_title.setText("❌ การติดตั้งไม่สำเร็จ")
            self.lbl_finish_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #ef4444;")
            self.lbl_finish_msg.setText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SetupWindow()
    win.show()
    sys.exit(app.exec())
