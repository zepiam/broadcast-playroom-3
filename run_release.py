"""
run_release.py — Universal One-Click Release Launcher for Broadcast Playroom 3
รันผ่าน release.bat เพื่อบิลด์ ตรวจสอบ และปล่อยอัปเดตขึ้น GitHub และ Hugging Face อัตโนมัติ
"""
import os
import sys
import re
import glob
import json
import shutil
import subprocess
import time
from pathlib import Path

# Force UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(r"""
========================================================================
       🚀 BROADCAST PLAYROOM 3 — ONE-CLICK RELEASE MANAGER
========================================================================
""")

def check_command(cmd, name):
    try:
        subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        return False

def get_latest_release_script():
    scripts = glob.glob(str(ROOT / "publish_release_v*.py"))
    if not scripts:
        return None, None
    def ver_key(p):
        numbers = re.findall(r'\d+', Path(p).stem)
        return tuple(int(x) for x in numbers) if numbers else (0,)
    sorted_scripts = sorted(scripts, key=ver_key)
    latest = Path(sorted_scripts[-1])
    m = re.search(r'v(\d+)', latest.stem)
    ver_str = m.group(1) if m else "unknown"
    # Format e.g. 375 -> 3.75
    if len(ver_str) == 3 and ver_str.isdigit():
        ver_formatted = f"{ver_str[0]}.{ver_str[1:]}"
    elif len(ver_str) == 4 and ver_str.isdigit():
        ver_formatted = f"{ver_str[0]}.{ver_str[1:]}"
    else:
        ver_formatted = ver_str
    return latest, ver_formatted

def check_huggingface_token():
    try:
        from huggingface_hub import get_token
        token = get_token()
        if token:
            return True
    except Exception:
        pass
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    if token_file.exists() and token_file.read_text(encoding='utf-8').strip():
        return True
    return False

def check_gh_auth():
    try:
        res = subprocess.run(["gh", "auth", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def main():
    clear_screen()
    print_banner()

    print("🔍 กำลังตรวจสอบความพร้อมของระบบ...")
    
    # 1. Check Python
    py_ok = sys.version_info >= (3, 10)
    print(f"  [{'✓' if py_ok else '✗'}] Python: {sys.version.split()[0]} {'(พร้อมใช้งาน)' if py_ok else '(ต้องการ 3.10+)'}")
    if not py_ok:
        print("\n[ERROR] กรุณาใช้ Python 3.10 ขึ้นไป")
        return 1

    # 2. Check Node/npm
    npm_ok = check_command("npm.cmd", "npm") or check_command("npm", "npm")
    print(f"  [{'✓' if npm_ok else '✗'}] Node.js & npm: {'พร้อมใช้งาน' if npm_ok else 'ไม่พบคำสั่ง npm'}")
    if not npm_ok:
        print("\n[ERROR] ไม่พบ npm ในระบบ กรุณาติดตั้ง Node.js ก่อนดำเนินการ")
        return 1

    # 3. Check GitHub CLI
    gh_ok = check_gh_auth()
    print(f"  [{'✓' if gh_ok else '✗'}] GitHub CLI (gh auth): {'ล็อกอินเรียบร้อย' if gh_ok else 'ยังไม่ได้ล็อกอิน (รัน gh auth login ก่อน)'}")
    if not gh_ok:
        print("\n[ERROR] กรุณาล็อกอิน GitHub ด้วยคำสั่ง: gh auth login")
        return 1

    # 4. Check Hugging Face Token
    hf_ok = check_huggingface_token()
    print(f"  [{'✓' if hf_ok else '✗'}] Hugging Face Token: {'ตรวจพบเรียบร้อย' if hf_ok else 'ไม่พบ Token ในเครื่อง'}")
    if not hf_ok:
        print("\n[ERROR] ไม่พบ Hugging Face Token กรุณารัน: huggingface-cli login หรือวาง token ใน ~/.cache/huggingface/token")
        return 1

    # 5. Detect Release Script & Version
    script_path, ver_str = get_latest_release_script()
    if not script_path or not script_path.is_file():
        print("\n[ERROR] ไม่พบไฟล์สคริปต์ publish_release_v*.py ในโฟลเดอร์โปรเจกต์")
        return 1

    # Read version from package.json if present
    pkg_ver = ver_str
    pkg_file = ROOT / "package.json"
    if pkg_file.is_file():
        try:
            pkg_data = json.loads(pkg_file.read_text(encoding='utf-8'))
            pkg_ver = pkg_data.get("version", ver_str)
        except Exception:
            pass

    sync_local = "--sync-local" in sys.argv

    print("\n" + "-" * 72)
    print(f"  📦 สคริปต์ที่จะรัน : {script_path.name}")
    print(f"  🏷️  เวอร์ชันที่จะปล่อย : v{pkg_ver}")
    if sync_local:
        print(f"  🌐 ปลายทาง        : GitHub + Hugging Face + 🔄 ซิงค์ลงเครื่อง (BroadcastPlayroom3\\full)")
    else:
        print(f"  🌐 ปลายทาง        : GitHub + Hugging Face (เฉพาะ Cloud ไม่แตะต้องไฟล์ในเครื่อง)")
    print("-" * 72 + "\n")

    # Confirmation prompt
    try:
        reply = input("👉 กด [Enter] หรือพิมพ์ Y เพื่อเริ่มปล่อย Release ทันที (หรือ N เพื่อยกเลิก): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nยกเลิกการทำงาน")
        return 0

    if reply and reply not in ('y', 'yes'):
        print("\nยกเลิกการปล่อย Release เรียบร้อยครับ")
        return 0

    print("\n" + "=" * 72)
    print("🚀 เริ่มต้นกระบวนการ Release... (ห้ามปิดหน้าต่างนี้จนกว่าจะเสร็จสิ้น)")
    print("=" * 72 + "\n")

    start_time = time.time()

    # Revert transient files before building
    try:
        subprocess.run(["git", "checkout", "composer_layout.json"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # Execute the release script
    res = subprocess.run([sys.executable, str(script_path)], cwd=ROOT)
    elapsed = time.time() - start_time

    print("\n" + "=" * 72)
    if res.returncode == 0:
        print(f"🎉 สำเร็จสมบูรณ์! ปล่อย Release v{pkg_ver} เรียบร้อยแล้ว (ใช้เวลา {elapsed:.1f} วินาที)")
        print(f"   • GitHub  : https://github.com/zepiam/broadcast-playroom-3/releases/tag/v{pkg_ver}")
        print(f"   • HF Mirror: https://huggingface.co/men9ch/broadcast-playroom-3")
        
        # Sync to local installation if requested
        if sync_local:
            inst_full = Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full")
            if inst_full.is_dir():
                print("\n🔄 กำลังซิงค์ไฟล์ล่าสุดลงโฟลเดอร์โปรแกรมในเครื่องของคุณ...")
                sync_files = ['launch_dev.py', 'tts_service.py', 'rvc_service.py', 'package_numba_cache.py', 'version.json']
                for sf in sync_files:
                    src_f = ROOT / sf
                    if src_f.is_file():
                        try:
                            shutil.copy2(src_f, inst_full / sf)
                            internal_dir = inst_full / "_internal"
                            if internal_dir.is_dir():
                                shutil.copy2(src_f, internal_dir / sf)
                        except Exception as ex:
                            print(f"   [!] ข้อสังเกตตอนซิงค์ {sf}: {ex}")
                print("   [✓] ซิงค์ไฟล์ลงโฟลเดอร์ติดตั้งในเครื่องเรียบร้อยแล้ว!")

        # Play chime
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
    else:
        print(f"❌ มีข้อผิดพลาดเกิดขึ้นระหว่างการปล่อย Release (Exit code: {res.returncode})")
        print("   กรุณาตรวจสอบข้อความ Error ด้านบน")

    print("=" * 72 + "\n")
    return res.returncode

if __name__ == '__main__':
    code = main()
    try:
        input("กด [Enter] เพื่อปิดหน้าต่างนี้...")
    except Exception:
        pass
    sys.exit(code)
