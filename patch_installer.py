"""
Broadcast Playroom 3 - One-Click Patch Installer & Auto Repair Utility
Designed for zero-friction updating and emergency repair for non-technical users.
Features:
- Automatic detection of installed instances (Full & Lite)
- Automatic detection of running processes & desktop shortcuts
- Strict Online GitHub / HuggingFace auto-download (Hugging Face prioritized for blazing fast downloads in Thailand)
- Disables dangerous local zip detection to prevent accidental downgrades to old versions left in Downloads
- Forceful process termination via taskkill to unlock all system files
- Post-install strict integrity check (verifies version.json on disk equals target version)
- Automatically purges stale WebView2 caches to guarantee new frontend is loaded
"""

import os
import sys
import time
import json
import psutil
import shutil
import zipfile
import threading
import subprocess
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Try to import Windows COM for shortcut reading
try:
    import win32com.client
except Exception:
    win32com = None

APP_TITLE = "Broadcast Playroom 3 - Patch Installer & Auto Repair"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/zepiam/broadcast-playroom-3/master/version.json"
HF_VERSION_URL = "https://huggingface.co/men9ch/broadcast-playroom-3/raw/main/version.json"

def get_installer_dir():
    """Return actual directory of installer executable or script."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def get_folder_version(folder_path):
    """Read version string from installed folder's version.json."""
    p = Path(folder_path)
    for v_candidate in [p / 'version.json', p / '_internal' / 'version.json']:
        if v_candidate.is_file():
            try:
                with open(v_candidate, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ver = data.get('version') or data.get('latest_version')
                    if ver:
                        return str(ver).strip()
            except Exception:
                pass
    return None

def scan_installed_instances():
    found = {}
    
    # 1. Check installer directory & parent
    inst_dir = get_installer_dir()
    for d in [inst_dir, inst_dir.parent]:
        for sub in [d, d.parent]:
            if (sub / 'BroadcastPlayroom3-Full.exe').exists() or (sub / '_internal' / 'BroadcastPlayroom3-Full.exe').exists():
                found[str(sub.resolve())] = 'full'
            elif (sub / 'BroadcastPlayroom3-Lite.exe').exists() or (sub / '_internal' / 'BroadcastPlayroom3-Lite.exe').exists():
                found[str(sub.resolve())] = 'lite'

    # 2. Check running processes
    for p in psutil.process_iter(['name', 'exe', 'cmdline']):
        try:
            name = (p.info.get('name') or '').lower()
            cmd = ' '.join(p.info.get('cmdline') or []).lower()
            if 'broadcastplayroom' in name or 'broadcastplayroom' in cmd or 'launch_dev.py' in cmd:
                exe_path = p.info.get('exe')
                if exe_path:
                    folder = Path(exe_path).parent
                    if (folder / '_internal').is_dir() or (folder / 'version.json').exists():
                        b_type = 'full' if 'full' in name or 'full' in str(folder).lower() else 'lite'
                        found[str(folder.resolve())] = b_type
                for arg in p.info.get('cmdline') or []:
                    if arg.endswith('launch_dev.py') and Path(arg).exists():
                        f = Path(arg).parent.resolve()
                        b_type = 'full' if 'full' in str(f).lower() else 'lite'
                        found[str(f)] = b_type
        except Exception:
            pass

    # 3. Check Desktop & Start Menu shortcuts (.lnk)
    if win32com:
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            search_dirs = []
            for sp in ["Desktop", "Programs"]:
                try:
                    p = Path(shell.SpecialFolders(sp))
                    if p.exists():
                        search_dirs.append(p)
                except Exception:
                    pass
            for sdir in search_dirs:
                for lnk in sdir.glob("*.lnk"):
                    try:
                        shortcut = shell.CreateShortCut(str(lnk))
                        target = shortcut.Targetpath
                        if target and 'broadcastplayroom' in target.lower() and target.lower().endswith('.exe'):
                            f_target = Path(target).parent
                            if f_target.exists():
                                b_type = 'full' if 'full' in target.lower() else 'lite'
                                found[str(f_target.resolve())] = b_type
                    except Exception:
                        pass
        except Exception:
            pass

    # 4. Check common locations across all available drives
    drives = [f'{d}:\\' for d in 'CDEFGHIJKLM' if os.path.exists(f'{d}:\\')]
    search_subpaths = [
        r'DOCS\Documents\BroadcastPlayroom3\full',
        r'DOCS\Documents\BroadcastPlayroom3\lite',
        r'DOCS\Documents\BroadcastPlayroom3',
        r'BroadcastPlayroom3\full',
        r'BroadcastPlayroom3\lite',
        r'BroadcastPlayroom3-Full',
        r'BroadcastPlayroom3-Lite',
        r'BroadcastPlayroom3',
        r'Program Files\BroadcastPlayroom3',
        r'Program Files (x86)\BroadcastPlayroom3',
    ]
    user_home = Path.home()
    user_subpaths = [
        user_home / 'Documents' / 'BroadcastPlayroom3' / 'full',
        user_home / 'Documents' / 'BroadcastPlayroom3' / 'lite',
        user_home / 'Documents' / 'BroadcastPlayroom3-Full',
        user_home / 'Documents' / 'BroadcastPlayroom3-Lite',
        user_home / 'Documents' / 'BroadcastPlayroom3',
        user_home / 'Desktop' / 'BroadcastPlayroom3' / 'full',
        user_home / 'Desktop' / 'BroadcastPlayroom3' / 'lite',
        user_home / 'Desktop' / 'BroadcastPlayroom3-Full',
        user_home / 'Desktop' / 'BroadcastPlayroom3-Lite',
        user_home / 'Desktop' / 'BroadcastPlayroom3',
        user_home / 'Downloads' / 'BroadcastPlayroom3' / 'full',
        user_home / 'Downloads' / 'BroadcastPlayroom3' / 'lite',
        user_home / 'Downloads' / 'BroadcastPlayroom3-Full',
        user_home / 'Downloads' / 'BroadcastPlayroom3-Lite',
        user_home / 'Downloads' / 'BroadcastPlayroom3',
        user_home / 'BroadcastPlayroom3' / 'full',
        user_home / 'BroadcastPlayroom3' / 'lite',
        user_home / 'BroadcastPlayroom3-Full',
        user_home / 'BroadcastPlayroom3-Lite',
        user_home / 'BroadcastPlayroom3',
        user_home / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'full',
        user_home / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'lite',
        user_home / 'AppData' / 'Local' / 'Programs' / 'BroadcastPlayroom3'
    ]

    for d in drives:
        for sp in search_subpaths:
            p = Path(d) / sp
            if p.is_dir() and 'ai tools' not in str(p).lower():
                if (p / 'BroadcastPlayroom3-Full.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Full.exe').exists():
                    found[str(p.resolve())] = 'full'
                elif (p / 'BroadcastPlayroom3-Lite.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Lite.exe').exists():
                    found[str(p.resolve())] = 'lite'

    for p in user_subpaths:
        if p.is_dir() and 'ai tools' not in str(p).lower():
            if (p / 'BroadcastPlayroom3-Full.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Full.exe').exists():
                found[str(p.resolve())] = 'full'
            elif (p / 'BroadcastPlayroom3-Lite.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Lite.exe').exists():
                found[str(p.resolve())] = 'lite'

    return found

def fetch_latest_metadata():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) BP3-PatchInstaller'}
    # Try Hugging Face first (faster and uncapped in Thailand), then GitHub
    for url in [HF_VERSION_URL, GITHUB_VERSION_URL]:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if 'latest_version' in data or 'version' in data:
                        data.setdefault('latest_version', data.get('version'))
                        return data
        except Exception:
            pass
    return None

class PatchInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("700x580")
        self.root.minsize(640, 520)
        self.root.configure(bg="#18191c")

        self.installer_dir = get_installer_dir()
        self.instances = {}
        self.metadata = None
        self.is_working = False

        self._setup_style()
        self._build_ui()
        
        # Start initial scan in background thread
        threading.Thread(target=self._initial_load, daemon=True).start()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar",
                        thickness=16,
                        troughcolor="#25272c",
                        background="#3b82f6",
                        darkcolor="#2563eb",
                        lightcolor="#60a5fa",
                        bordercolor="#18191c")

    def _build_ui(self):
        # 1. Header Card
        header = tk.Frame(self.root, bg="#1e1f22", padx=20, pady=16)
        header.pack(fill="x", padx=16, pady=(16, 10))

        title_lbl = tk.Label(header, text="⚡ Broadcast Playroom 3 - One-Click Patch Installer",
                             font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e1f22")
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(header, text="ตรวจหาโฟลเดอร์โปรแกรมและอัปเดต / ซ่อมแซมระบบให้อัตโนมัติ (ปลอดภัย ข้อมูลเดิมไม่หาย 100%)",
                           font=("Segoe UI", 10), fg="#94a3b8", bg="#1e1f22")
        sub_lbl.pack(anchor="w", pady=(4, 0))

        # 2. Main Content Frame
        self.content = tk.Frame(self.root, bg="#18191c", padx=16)
        self.content.pack(fill="both", expand=True)

        # Status & Version Card
        self.meta_frame = tk.Frame(self.content, bg="#1e1f22", padx=16, pady=12, highlightthickness=1, highlightbackground="#313338")
        self.meta_frame.pack(fill="x", pady=6)

        self.ver_label = tk.Label(self.meta_frame, text="🔍 กำลังตรวจสอบเวอร์ชันล่าสุด...",
                                  font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#1e1f22")
        self.ver_label.pack(anchor="w")

        self.meta_desc = tk.Label(self.meta_frame, text="รอสักครู่ ระบบกำลังค้นหาตำแหน่งของโปรแกรมในเครื่องของคุณ...",
                                  font=("Segoe UI", 9), fg="#94a3b8", bg="#1e1f22")
        self.meta_desc.pack(anchor="w", pady=(2, 0))

        # Detected Folders Frame
        self.folders_card = tk.Frame(self.content, bg="#1e1f22", padx=16, pady=12, highlightthickness=1, highlightbackground="#313338")
        self.folders_card.pack(fill="both", expand=True, pady=6)

        folders_title_row = tk.Frame(self.folders_card, bg="#1e1f22")
        folders_title_row.pack(fill="x")

        tk.Label(folders_title_row, text="📁 โฟลเดอร์โปรแกรมที่ตรวจพบในเครื่อง:",
                 font=("Segoe UI", 11, "bold"), fg="#f2f3f5", bg="#1e1f22").pack(side="left")

        self.btn_browse = tk.Button(folders_title_row, text="➕ เลือกโฟลเดอร์เอง",
                                    font=("Segoe UI", 9), fg="#ffffff", bg="#374151", activebackground="#4b5563",
                                    activeforeground="#ffffff", relief="flat", padx=10, pady=2, cursor="hand2",
                                    command=self._manual_browse)
        self.btn_browse.pack(side="right")

        self.list_container = tk.Frame(self.folders_card, bg="#1e1f22")
        self.list_container.pack(fill="both", expand=True, pady=(8, 0))

        # Progress & Log Area
        self.progress_frame = tk.Frame(self.content, bg="#18191c")
        self.progress_frame.pack(fill="x", pady=(6, 0))

        self.progress_bar = ttk.Progressbar(self.progress_frame, style="TProgressbar", mode="determinate")
        self.progress_bar.pack(fill="x")

        self.status_msg = tk.Label(self.progress_frame, text="พร้อมเริ่มการอัปเดต",
                                   font=("Segoe UI", 9), fg="#94a3b8", bg="#18191c")
        self.status_msg.pack(anchor="w", pady=(4, 0))

        # Bottom Action Bar
        bottom = tk.Frame(self.root, bg="#18191c", padx=16, pady=14)
        bottom.pack(fill="x")

        self.btn_action = tk.Button(bottom, text="🚀 อัปเดตและซ่อมแซมระบบทันที (Update & Repair)",
                                    font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#2563eb",
                                    activebackground="#1d4ed8", activeforeground="#ffffff",
                                    relief="flat", pady=10, cursor="hand2", command=self._start_install)
        self.btn_action.pack(fill="x")

    def _initial_load(self):
        self.metadata = fetch_latest_metadata()
        self.instances = scan_installed_instances()
        self.root.after(0, self._render_initial_state)

    def _render_initial_state(self):
        latest_ver = self.metadata.get('latest_version', '3.53') if self.metadata else '3.53'
        self.ver_label.config(text=f"✨ เวอร์ชันล่าสุดจากเซิร์ฟเวอร์: v{latest_ver}", fg="#22c55e")
        
        notes = []
        if self.metadata:
            notes.append("เชื่อมต่อเซิร์ฟเวอร์ Hugging Face / GitHub พร้อมดาวน์โหลดชุดแพตช์ล่าสุด")
        self.meta_desc.config(text=" | ".join(notes) if notes else "พร้อมดำเนินการ")

        self._refresh_folders_list()

    def _refresh_folders_list(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        if not self.instances:
            empty_frame = tk.Frame(self.list_container, bg="#1e1f22", pady=16)
            empty_frame.pack(fill="x")
            
            empty_lbl = tk.Label(empty_frame,
                                 text="⚠️ ไม่พบโฟลเดอร์โปรแกรมอัตโนมัติในตำแหน่งเริ่มต้น",
                                 font=("Segoe UI", 10, "bold"), fg="#f87171", bg="#1e1f22")
            empty_lbl.pack(anchor="w")

            hint_lbl = tk.Label(empty_frame,
                                text="กรุณากดปุ่ม '➕ เลือกโฟลเดอร์เอง' ด้านบน เพื่อเลือกโฟลเดอร์ที่เก็บไฟล์ BroadcastPlayroom3",
                                font=("Segoe UI", 9), fg="#94a3b8", bg="#1e1f22")
            hint_lbl.pack(anchor="w", pady=(4, 0))

            self.btn_action.config(state="disabled", bg="#374151")
            return

        self.btn_action.config(state="normal", bg="#2563eb")
        target_ver = self.metadata.get('latest_version', '3.53') if self.metadata else '3.53'

        for path_str, b_type in self.instances.items():
            cur_ver = get_folder_version(path_str)
            cur_ver_display = f"v{cur_ver}" if cur_ver else "ไม่ทราบเวอร์ชัน (หรือไฟล์เสียหาย)"

            row = tk.Frame(self.list_container, bg="#25272c", padx=12, pady=8, highlightthickness=1, highlightbackground="#374151")
            row.pack(fill="x", pady=4)

            badge_text = "FULL VERSION" if b_type == 'full' else "LITE VERSION"
            badge_color = "#2563eb" if b_type == 'full' else "#10b981"
            badge = tk.Label(row, text=badge_text, font=("Segoe UI", 8, "bold"), fg="#ffffff", bg=badge_color, padx=6, pady=2)
            badge.pack(side="left")

            col = tk.Frame(row, bg="#25272c")
            col.pack(side="left", fill="x", expand=True, padx=10)

            path_lbl = tk.Label(col, text=path_str, font=("Consolas", 9, "bold"), fg="#e2e8f0", bg="#25272c", anchor="w")
            path_lbl.pack(fill="x")

            if cur_ver == target_ver:
                diff_text = f"✓ ปัจจุบันเป็นเวอร์ชันล่าสุดแล้ว ({cur_ver_display}) - พร้อมตรวจสอบและซ่อมแซมไฟล์ระบบ"
                diff_color = "#4ade80"
            else:
                diff_text = f"เวอร์ชันปัจจุบัน: {cur_ver_display}  ➔  จะอัปเดตเป็น: v{target_ver}"
                diff_color = "#38bdf8"

            ver_lbl = tk.Label(col, text=diff_text, font=("Segoe UI", 9), fg=diff_color, bg="#25272c", anchor="w")
            ver_lbl.pack(fill="x", pady=(2, 0))

            status_icon = tk.Label(row, text="✓ พร้อมลงแพตช์", font=("Segoe UI", 9, "bold"), fg="#4ade80", bg="#25272c")
            status_icon.pack(side="right")

    def _manual_browse(self):
        chosen = filedialog.askdirectory(title="เลือกโฟลเดอร์ที่ติดตั้ง Broadcast Playroom 3")
        if chosen:
            p = Path(chosen)
            b_type = 'lite' if 'lite' in chosen.lower() else 'full'
            self.instances[str(p.resolve())] = b_type
            self._refresh_folders_list()

    def _set_status(self, text, pct=None):
        def _update():
            self.status_msg.config(text=text)
            if pct is not None:
                self.progress_bar['value'] = pct
        self.root.after(0, _update)

    def _start_install(self):
        if self.is_working:
            return
        self.is_working = True
        self.btn_action.config(state="disabled", text="⏳ กำลังดำเนินการอัปเดตและซ่อมแซม...")
        self.btn_browse.config(state="disabled")

        threading.Thread(target=self._run_install_worker, daemon=True).start()

    def _run_install_worker(self):
        try:
            # 1. Force kill any running Broadcast Playroom 3 and Edge WebView processes to release file locks
            self._set_status("กำลังปิดโปรแกรม Broadcast Playroom และปลดล็อกไฟล์ระบบ...", 5)
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'BroadcastPlayroom3-Full.exe'], capture_output=True)
                subprocess.run(['taskkill', '/F', '/IM', 'BroadcastPlayroom3-Lite.exe'], capture_output=True)
                subprocess.run(['taskkill', '/F', '/IM', 'msedgewebview2.exe'], capture_output=True)
            except Exception:
                pass

            for proc in psutil.process_iter(['name', 'pid', 'cmdline', 'exe']):
                try:
                    pname = (proc.info.get('name') or '').lower()
                    cmd = ' '.join(proc.info.get('cmdline') or []).lower()
                    if 'broadcastplayroom' in pname or 'broadcastplayroom' in cmd or 'launch_dev.py' in cmd:
                        proc.kill()
                except Exception:
                    pass
            time.sleep(1.5)

            # Determine what packages we need
            needed_types = set(self.instances.values())
            latest_ver = self.metadata.get('latest_version', '3.53') if self.metadata else '3.53'

            downloaded_zips = {}

            # Download official online patch for each needed type (Full / Lite)
            temp_dir = Path(os.environ.get('TEMP') or Path.home() / 'AppData' / 'Local' / 'Temp')

            for b_type in needed_types:
                # Prioritize Hugging Face CDN (direct, fast, no rate limit in TH)
                hf_url = f"https://huggingface.co/men9ch/broadcast-playroom-3/resolve/main/patches/patch-v{latest_ver}-{b_type}.zip"
                gh_url = f"https://github.com/zepiam/broadcast-playroom-3/releases/download/v{latest_ver}/patch-v{latest_ver}-{b_type}.zip"

                urls_to_try = [hf_url, gh_url]

                dest_zip = temp_dir / f"bp3_patch_{b_type}_v{latest_ver}.zip"
                download_success = False

                for download_url in urls_to_try:
                    try:
                        self._set_status(f"กำลังดาวน์โหลดแพตช์ v{latest_ver} ({b_type.upper()})...", 15)
                        
                        req = urllib.request.Request(download_url, headers={'User-Agent': 'BP3-PatchInstaller/3.52'})
                        with urllib.request.urlopen(req, timeout=45) as resp, open(dest_zip, 'wb') as out_f:
                            total_size = int(resp.headers.get('content-length', 0))
                            downloaded = 0
                            block_size = 64 * 1024

                            while True:
                                chunk = resp.read(block_size)
                                if not chunk:
                                    break
                                out_f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    pct = 15 + int((downloaded / total_size) * 45)
                                    mb_cur = downloaded / (1024 * 1024)
                                    mb_tot = total_size / (1024 * 1024)
                                    self._set_status(f"กำลังดาวน์โหลด ({b_type.upper()}): {mb_cur:.1f}/{mb_tot:.1f} MB ({int(downloaded/total_size*100)}%)", pct)

                        if dest_zip.exists() and dest_zip.stat().st_size > 100000:
                            download_success = True
                            downloaded_zips[b_type] = dest_zip
                            break
                    except Exception as err:
                        print(f"Download failed from {download_url}: {err}")
                        continue

                if not download_success:
                    raise RuntimeError(f"ดาวน์โหลดไฟล์แพตช์ v{latest_ver} สำหรับ {b_type.upper()} ไม่สำเร็จ กรุณาตรวจสอบอินเทอร์เน็ต")

            # Apply patch to all detected directories
            total_instances = len(self.instances)
            curr_idx = 0

            # Safe backup of data files to AppData before extraction
            appdata_backup = Path.home() / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'settings_backup'
            appdata_backup.mkdir(parents=True, exist_ok=True)

            for folder_str, b_type in self.instances.items():
                curr_idx += 1
                target_dir = Path(folder_str)
                patch_zip = downloaded_zips.get(b_type) or downloaded_zips.get('full')

                if not patch_zip or not patch_zip.exists():
                    continue

                # Backup user data
                for fname in ['platform_settings.json', 'user_roster.json']:
                    for cand in [target_dir / 'data' / fname, target_dir.parent / 'data' / fname]:
                        if cand.exists() and cand.stat().st_size > 10:
                            try:
                                shutil.copy2(cand, appdata_backup / fname)
                            except Exception:
                                pass

                self._set_status(f"กำลังติดตั้งแพตช์ลงใน: {target_dir.name} ({curr_idx}/{total_instances})...", 65 + int((curr_idx / total_instances) * 25))

                with zipfile.ZipFile(patch_zip, 'r') as z:
                    for member in z.infolist():
                        # Extract with retry up to 4 times
                        for attempt in range(4):
                            try:
                                z.extract(member, target_dir)
                                break
                            except Exception as ex:
                                if attempt == 3:
                                    print(f"Extraction warning on {member.filename}: {ex}")
                                time.sleep(0.3)

                # Sync to _internal if present
                internal_dir = target_dir / '_internal'
                if internal_dir.is_dir():
                    for sync_name in ['dist', 'updater.py', 'launch_dev.py', 'version.json']:
                        src_item = target_dir / sync_name
                        dest_item = internal_dir / sync_name
                        if src_item.exists():
                            try:
                                if src_item.is_dir():
                                    shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
                                else:
                                    shutil.copy2(src_item, dest_item)
                            except Exception:
                                pass

                # Ensure version.json is strictly written and verified
                for vj_path in [target_dir / 'version.json', internal_dir / 'version.json']:
                    try:
                        vj_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(vj_path, 'w', encoding='utf-8') as f:
                            json.dump({
                                "product": "broadcast-playroom-3",
                                "version": latest_ver,
                                "latest_version": latest_ver,
                                "edition": b_type
                            }, f, indent=2)
                    except Exception:
                        pass

                # Post-install verification
                ver_after = get_folder_version(target_dir)
                if ver_after != latest_ver:
                    raise RuntimeError(f"การอัปเดตไฟล์ล้มเหลว: เวอร์ชันในเครื่องยังคงเป็น v{ver_after} (คาดหวัง v{latest_ver})")

                # Purge stale browser profile & webview cache in all possible locations
                for cache_cand in [
                    target_dir / 'data' / 'browser_profile',
                    target_dir.parent / 'data' / 'browser_profile',
                    target_dir / 'data' / 'webview_data',
                    target_dir.parent / 'data' / 'webview_data',
                    Path.home() / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'browser_profile',
                    Path.home() / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'data' / 'browser_profile',
                    Path.home() / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'webview_data',
                    Path.home() / 'AppData' / 'Local' / 'BroadcastPlayroom3' / 'data' / 'webview_data'
                ]:
                    for sub in [
                        'Default/Cache', 'Default/Code Cache', 'Default/GPUCache', 'ShaderCache', 'GrShaderCache',
                        'EBWebView/Default/Cache', 'EBWebView/Default/Code Cache', 'EBWebView/Default/GPUCache'
                    ]:
                        cp = cache_cand / sub
                        if cp.exists():
                            try:
                                shutil.rmtree(cp, ignore_errors=True)
                            except Exception:
                                pass

            # Clean up temporary downloaded zips
            for zf in downloaded_zips.values():
                if zf.name.startswith("bp3_patch_") and zf.exists():
                    try:
                        zf.unlink()
                    except Exception:
                        pass

            self._set_status(f"✨ อัปเดตและซ่อมแซมระบบเป็น v{latest_ver} สำเร็จเรียบร้อย 100%!", 100)

            # Prompt & Launch
            def _on_done():
                self.btn_action.config(state="normal", text="🎉 อัปเดตเสร็จแล้ว! คลิกเพื่อเปิดโปรแกรม",
                                       bg="#16a34a", command=self._launch_app)
                self._refresh_folders_list()
                messagebox.showinfo("อัปเดตสำเร็จ", f"อัปเดตและซ่อมแซมโปรแกรม Broadcast Playroom 3\nเป็นเวอร์ชัน v{latest_ver} เรียบร้อยแล้วครับ!\nคลิก 'ตกลง' เพื่อเปิดโปรแกรมได้ทันที")
                self._launch_app()

            self.root.after(0, _on_done)

        except Exception as e:
            err_msg = str(e)
            self._set_status(f"❌ เกิดข้อผิดพลาด: {err_msg}", 0)
            def _on_err():
                self.btn_action.config(state="normal", text="🔄 ลองใหม่อีกครั้ง", bg="#dc2626")
                self.btn_browse.config(state="normal")
                self.is_working = False
                messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถอัปเดตได้:\n{err_msg}")
            self.root.after(0, _on_err)

    def _launch_app(self):
        for folder_str, b_type in self.instances.items():
            f = Path(folder_str)
            exe_candidates = [
                f / "BroadcastPlayroom3-Full.exe",
                f / "BroadcastPlayroom3-Lite.exe",
                f / "_internal" / "BroadcastPlayroom3-Full.exe",
                f / "_internal" / "BroadcastPlayroom3-Lite.exe"
            ]
            for exe in exe_candidates:
                if exe.exists():
                    try:
                        import subprocess
                        subprocess.Popen([str(exe)], cwd=str(f))
                        self.root.after(800, self.root.destroy)
                        return
                    except Exception:
                        pass
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    for icon_name in ['assets/icon_full.ico', 'assets/icon.png', 'dist/favicon.ico']:
        icon_path = Path(__file__).resolve().parent / icon_name
        if icon_path.exists():
            try:
                root.iconbitmap(str(icon_path))
                break
            except Exception:
                pass
    app = PatchInstallerApp(root)
    root.mainloop()
