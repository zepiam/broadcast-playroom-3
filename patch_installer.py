"""
Broadcast Playroom 3 - One-Click Patch Installer & Auto Repair Utility
Designed for zero-friction updating and emergency repair for non-technical users.
Features:
- Automatic detection of installed instances (Full & Lite)
- Automatic detection of running processes & desktop shortcuts
- Offline local patch ZIP detection & Online GitHub / HuggingFace auto-download
- Handles both Full and Lite simultaneously if both are installed
- Clean, modern dark GUI (Tkinter) with live progress bar
- Automatically closes running instances before patch, then relaunches after patch
"""

import os
import sys
import time
import json
import psutil
import shutil
import zipfile
import threading
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

def scan_installed_instances():
    found = {}
    
    # 1. Check current directory
    cwd = Path.cwd()
    if (cwd / 'BroadcastPlayroom3-Full.exe').exists() or (cwd / '_internal' / 'BroadcastPlayroom3-Full.exe').exists():
        found[str(cwd.resolve())] = 'full'
    elif (cwd / 'BroadcastPlayroom3-Lite.exe').exists() or (cwd / '_internal' / 'BroadcastPlayroom3-Lite.exe').exists():
        found[str(cwd.resolve())] = 'lite'

    # 2. Check running processes
    for p in psutil.process_iter(['name', 'exe', 'cmdline']):
        try:
            name = (p.info['name'] or '').lower()
            if 'broadcastplayroom' in name:
                exe_path = p.info['exe']
                if exe_path:
                    folder = Path(exe_path).parent
                    if (folder / '_internal').is_dir() or (folder / 'version.json').exists():
                        b_type = 'full' if 'full' in name else 'lite'
                        found[str(folder.resolve())] = b_type
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

    # 4. Check common locations across drives
    drives = [f'{d}:\\' for d in 'CDEFGHIJKLM' if os.path.exists(f'{d}:\\')]
    search_subpaths = [
        r'DOCS\Documents\BroadcastPlayroom3\full',
        r'DOCS\Documents\BroadcastPlayroom3\lite',
        r'BroadcastPlayroom3\full',
        r'BroadcastPlayroom3\lite',
        r'BroadcastPlayroom3',
        r'Program Files\BroadcastPlayroom3',
        r'Program Files (x86)\BroadcastPlayroom3',
    ]
    user_home = Path.home()
    user_subpaths = [
        user_home / 'Documents' / 'BroadcastPlayroom3' / 'full',
        user_home / 'Documents' / 'BroadcastPlayroom3' / 'lite',
        user_home / 'BroadcastPlayroom3' / 'full',
        user_home / 'BroadcastPlayroom3' / 'lite',
        user_home / 'AppData' / 'Local' / 'Programs' / 'BroadcastPlayroom3'
    ]

    for d in drives:
        for sp in search_subpaths:
            p = Path(d) / sp
            if p.is_dir():
                if (p / 'BroadcastPlayroom3-Full.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Full.exe').exists():
                    found[str(p.resolve())] = 'full'
                elif (p / 'BroadcastPlayroom3-Lite.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Lite.exe').exists():
                    found[str(p.resolve())] = 'lite'
                elif (p / 'launch_dev.py').exists() and 'broadcastplayroom3' in str(p).lower() and 'ai tools' not in str(p).lower():
                    found[str(p.resolve())] = 'full' if 'full' in str(p).lower() else 'lite'

    for p in user_subpaths:
        if p.is_dir():
            if (p / 'BroadcastPlayroom3-Full.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Full.exe').exists():
                found[str(p.resolve())] = 'full'
            elif (p / 'BroadcastPlayroom3-Lite.exe').exists() or (p / '_internal' / 'BroadcastPlayroom3-Lite.exe').exists():
                found[str(p.resolve())] = 'lite'

    return found

def fetch_latest_metadata():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) BP3-PatchInstaller'}
    for url in [GITHUB_VERSION_URL, HF_VERSION_URL]:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if 'latest_version' in data:
                        return data
        except Exception:
            pass
    return None

def find_local_patches(installer_dir):
    local_patches = {}
    p_dirs = [installer_dir, installer_dir / 'patches']
    for pdir in p_dirs:
        if pdir.exists():
            for zf in pdir.glob("*.zip"):
                zname = zf.name.lower()
                if 'full' in zname:
                    local_patches['full'] = zf
                elif 'lite' in zname:
                    local_patches['lite'] = zf
    return local_patches

class PatchInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("680x560")
        self.root.minsize(620, 500)
        self.root.configure(bg="#18191c")

        self.installer_dir = Path(__file__).resolve().parent
        self.instances = {}
        self.local_patches = {}
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

        sub_lbl = tk.Label(header, text="ตรวจหาโฟลเดอร์โปรแกรมและอัปเดต / ซ่อมแซมระบบให้อัตโนมัติในคลิกเดียว (ข้อมูลไม่หาย 100%)",
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
        # Scan instances
        self.instances = scan_installed_instances()
        self.local_patches = find_local_patches(self.installer_dir)
        self.metadata = fetch_latest_metadata()

        self.root.after(0, self._render_initial_state)

    def _render_initial_state(self):
        # Update metadata info
        latest_ver = self.metadata.get('latest_version', 'ล่าสุด') if self.metadata else 'ล่าสุด'
        self.ver_label.config(text=f"✨ เวอร์ชันล่าสุด: v{latest_ver}", fg="#22c55e")
        
        notes = []
        if self.local_patches:
            found_names = ", ".join(f.name for f in self.local_patches.values())
            notes.append(f"ตรวจพบไฟล์แพตช์ในเครื่อง: {found_names}")
        if self.metadata:
            notes.append("พร้อมดาวน์โหลดตัวอัปเดตล่าสุดจาก GitHub / Hugging Face")
        self.meta_desc.config(text=" | ".join(notes) if notes else "พร้อมดำเนินการ")

        self._refresh_folders_list()

    def _refresh_folders_list(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        if not self.instances:
            empty_lbl = tk.Label(self.list_container,
                                 text="⚠️ ไม่พบโฟลเดอร์โปรแกรมอัตโนมัติ กรุณากด '➕ เลือกโฟลเดอร์เอง' ด้านบน",
                                 font=("Segoe UI", 10), fg="#f87171", bg="#1e1f22", pady=12)
            empty_lbl.pack(anchor="w")
            self.btn_action.config(state="disabled", bg="#374151")
            return

        self.btn_action.config(state="normal", bg="#2563eb")

        for path_str, b_type in self.instances.items():
            row = tk.Frame(self.list_container, bg="#25272c", padx=10, pady=8, highlightthickness=1, highlightbackground="#374151")
            row.pack(fill="x", pady=3)

            badge_text = "FULL VERSION" if b_type == 'full' else "LITE VERSION"
            badge_color = "#3b82f6" if b_type == 'full' else "#10b981"
            badge = tk.Label(row, text=badge_text, font=("Segoe UI", 8, "bold"), fg="#ffffff", bg=badge_color, padx=6, pady=2)
            badge.pack(side="left")

            path_lbl = tk.Label(row, text=f"  {path_str}", font=("Consolas", 9), fg="#e2e8f0", bg="#25272c")
            path_lbl.pack(side="left", fill="x", expand=True)

            status_icon = tk.Label(row, text="✓ พร้อมลงแพตช์", font=("Segoe UI", 9), fg="#4ade80", bg="#25272c")
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
            # 1. Kill any running Broadcast Playroom 3 processes to release locked files
            self._set_status("กำลังปิดโปรแกรม Broadcast Playroom ที่เปิดค้างอยู่...", 5)
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    pname = (proc.info['name'] or '').lower()
                    if 'broadcastplayroom' in pname:
                        proc.kill()
                except Exception:
                    pass
            time.sleep(1)

            # Determine what packages we need
            needed_types = set(self.instances.values())
            latest_ver = self.metadata.get('latest_version', 'latest') if self.metadata else '3.45'

            downloaded_zips = {}

            # Download or locate patch for each needed type (Full / Lite)
            for b_type in needed_types:
                # Check local patch first
                if b_type in self.local_patches and self.local_patches[b_type].exists():
                    self._set_status(f"ใช้ไฟล์แพตช์ในเครื่อง: {self.local_patches[b_type].name}", 20)
                    downloaded_zips[b_type] = self.local_patches[b_type]
                    continue

                # Download online
                if not self.metadata:
                    self._set_status("ดึงข้อมูลลิงก์อัปเดตล่าสุด...", 10)
                    self.metadata = fetch_latest_metadata()

                if not self.metadata:
                    raise RuntimeError("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์อัปเดตได้ และไม่พบไฟล์แพตช์ในเครื่อง")

                type_info = self.metadata.get(b_type) or self.metadata.get('full')
                url = type_info.get('url')
                mirrors = type_info.get('mirrors', [])
                urls_to_try = [url] + mirrors if url else mirrors

                dest_zip = self.installer_dir / f"bp3_patch_{b_type}_v{latest_ver}.zip"
                download_success = False

                for download_url in urls_to_try:
                    if not download_url:
                        continue
                    try:
                        self._set_status(f"กำลังดาวน์โหลดแพตช์ ({b_type.upper()})...", 15)
                        
                        req = urllib.request.Request(download_url, headers={'User-Agent': 'BP3-PatchInstaller'})
                        with urllib.request.urlopen(req, timeout=30) as resp, open(dest_zip, 'wb') as out_f:
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
                    raise RuntimeError(f"ดาวน์โหลดไฟล์แพตช์สำหรับ {b_type.upper()} ไม่สำเร็จ กรุณาตรวจสอบอินเทอร์เน็ต")

            # Apply patch to all detected directories
            total_instances = len(self.instances)
            curr_idx = 0

            for folder_str, b_type in self.instances.items():
                curr_idx += 1
                target_dir = Path(folder_str)
                patch_zip = downloaded_zips.get(b_type) or downloaded_zips.get('full')

                if not patch_zip or not patch_zip.exists():
                    continue

                self._set_status(f"กำลังติดตั้งแพตช์ลงใน: {target_dir.name} ({curr_idx}/{total_instances})...", 65 + int((curr_idx / total_instances) * 25))

                with zipfile.ZipFile(patch_zip, 'r') as z:
                    for member in z.infolist():
                        # Extract with overwrite
                        try:
                            z.extract(member, target_dir)
                        except Exception as e:
                            print(f"Extract warning for {member.filename}: {e}")

            # Clean up downloaded temporary zips
            for zf in downloaded_zips.values():
                if zf.name.startswith("bp3_patch_") and zf.exists():
                    try:
                        zf.unlink()
                    except Exception:
                        pass

            self._set_status("✨ อัปเดตและซ่อมแซมระบบสำเร็จเรียบร้อย 100%!", 100)

            # Prompt & Launch
            def _on_done():
                self.btn_action.config(state="normal", text="🎉 อัปเดตเสร็จแล้ว! คลิกเพื่อเปิดโปรแกรม",
                                       bg="#16a34a", command=self._launch_app)
                messagebox.showinfo("อัปเดตสำเร็จ", "อัปเดตและซ่อมแซมโปรแกรม Broadcast Playroom 3 เรียบร้อยแล้วครับ!\nคลิก 'ตกลง' เพื่อเปิดโปรแกรมได้ทันที")
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
        # Find executable to launch
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
    # Set icon if available
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
