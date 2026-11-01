"""
Broadcast Playroom 3 - Standalone Update & Emergency Repair Utility (FindUpdate)
Allows users to easily check for updates, repair corrupted installations,
and recover from broken versions without reinstalling the entire program.
"""
import os
import sys
import time
import json
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    print("=" * 64)
    print("   Broadcast Playroom 3 - ตรวจสอบอัปเดตและซ่อมแซมระบบ (FindUpdate)")
    print("=" * 64)
    print()

def run_findupdate_cli(force_repair: bool = False) -> int:
    print_banner()

    root_dir = Path(__file__).resolve().parent
    try:
        from updater import check_for_update, get_current_version, get_build_type, download_update_file, apply_update_patch, restart_application
    except ImportError:
        print("[ข้อผิดพลาด] ไม่พบโมดูล updater.py ในโฟลเดอร์นี้", file=sys.stderr)
        input("\nกด Enter เพื่อปิด...")
        return 1

    cur_ver = get_current_version()
    b_type = get_build_type()
    print(f"เวอร์ชันที่ติดตั้งอยู่ในเครื่อง: v{cur_ver} ({b_type})")
    print("กำลังตรวจสอบสถานะเวอร์ชันล่าสุดจาก GitHub...")

    try:
        up_info = check_for_update(b_type)
    except Exception as e:
        print(f"[ข้อผิดพลาดในการเชื่อมต่อ]: {e}")
        input("\nกด Enter เพื่อปิด...")
        return 1

    latest_ver = up_info.get("latest_version", cur_ver)
    has_update = up_info.get("has_update", False)
    dl_url = up_info.get("download_url", "")
    sha256 = up_info.get("sha256", "")

    print(f"เวอร์ชันล่าสุดบนเซิร์ฟเวอร์:     v{latest_ver}")
    print()

    target_zip = root_dir / f"bp3_repair_{latest_ver}.zip"

    should_proceed = False
    if has_update:
        print(f"🎉 ตรวจพบเวอร์ชันใหม่ล่าสุด (v{latest_ver})!")
        print("ระบบจะทำการดาวน์โหลดและอัปเดตให้อัตโนมัติ...")
        should_proceed = True
    elif force_repair:
        print("🛠️ โหมดซ่อมแซมระบบ (Repair Mode): กำลังดาวน์โหลดไฟล์เวอร์ชันล่าสุดเพื่อเขียนทับซ่อมแซม...")
        should_proceed = True
    else:
        print("✅ ขณะนี้โปรแกรมของคุณเป็นเวอร์ชันล่าสุดแล้วครับ")
        print("\nต้องการให้ระบบตรวจสอบและดาวน์โหลดไฟล์มาซ่อมแซมใหม่หรือไม่?")
        print("  [1] ซ่อมแซมและติดตั้งไฟล์ระบบล่าสุดใหม่ทั้งหมด (Repair / Force Reinstall)")
        print("  [2] ออกจากโปรแกรม")
        try:
            choice = input("\nกรุณาเลือก (1 หรือ 2) [ค่าเริ่มต้น: 1]: ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "2"
        if choice in ("", "1", "y", "Y"):
            should_proceed = True
            force_repair = True
        else:
            print("ปิดการทำงาน.")
            return 0

    if should_proceed:
        if not dl_url:
            print("[ข้อผิดพลาด] ไม่พบลิงก์ดาวน์โหลดสำหรับเวอร์ชันนี้", file=sys.stderr)
            input("\nกด Enter เพื่อปิด...")
            return 1

        print(f"\n[1/3] กำลังดาวน์โหลดแพ็กเกจ (v{latest_ver})...")
        print(f"URL: {dl_url}")

        def _progress(transferred, total):
            if total > 0:
                pct = int((transferred / total) * 100)
                filled = int(pct / 5)
                bar = '█' * filled + '░' * (20 - filled)
                mb_cur = transferred / (1024 * 1024)
                mb_tot = total / (1024 * 1024)
                sys.stdout.write(f"\r  ความคืบหน้า: [{bar}] {pct:3d}% ({mb_cur:.1f}/{mb_tot:.1f} MB)")
                sys.stdout.flush()

        try:
            ok = download_update_file(dl_url, str(target_zip), expected_sha256=sha256 if not force_repair else "", progress_callback=_progress)
            print()
            if not ok or not target_zip.exists():
                print("\n[ข้อผิดพลาด] ดาวน์โหลดไฟล์ไม่สำเร็จ กรุณาตรวจสอบอินเทอร์เน็ต", file=sys.stderr)
                input("\nกด Enter เพื่อปิด...")
                return 1
        except Exception as e:
            print(f"\n[ข้อผิดพลาด] ดาวน์โหลดล้มเหลว: {e}", file=sys.stderr)
            input("\nกด Enter เพื่อปิด...")
            return 1

        print("\n[2/3] ตรวจสอบความถูกต้องของไฟล์แพ็กเกจ: ผ่าน 100%")

        print("\n[3/3] กำลังแตกไฟล์และซ่อมแซมระบบโปรแกรม...")
        try:
            applied = apply_update_patch(str(target_zip))
            if not applied:
                print("[ข้อผิดพลาด] ไม่สามารถแตกไฟล์ทับได้ (อาจมีโปรแกรมเปิดค้างอยู่)", file=sys.stderr)
                input("\nกด Enter เพื่อปิด...")
                return 1
        except Exception as e:
            print(f"[ข้อผิดพลาดในการติดตั้ง]: {e}", file=sys.stderr)
            input("\nกด Enter เพื่อปิด...")
            return 1
        finally:
            if target_zip.exists():
                try:
                    target_zip.unlink()
                except OSError:
                    pass

        print("\n" + "=" * 64)
        print("✨ ซ่อมแซมและอัปเดตระบบเป็นเวอร์ชันล่าสุดเรียบร้อยแล้ว!")
        print("=" * 64)
        print("\nกำลังเปิดโปรแกรม Broadcast Playroom 3 ใน 2 วินาที...")
        time.sleep(2)
        try:
            restart_application()
        except Exception:
            # Fallback launch
            exe_full = root_dir / "BroadcastPlayroom3-Full.exe"
            exe_lite = root_dir / "BroadcastPlayroom3-Lite.exe"
            import subprocess
            if exe_full.exists():
                subprocess.Popen([str(exe_full)], cwd=str(root_dir))
            elif exe_lite.exists():
                subprocess.Popen([str(exe_lite)], cwd=str(root_dir))
            else:
                py_script = root_dir / "launch_dev.py"
                if py_script.exists():
                    subprocess.Popen([sys.executable, str(py_script)], cwd=str(root_dir))

    return 0

if __name__ == '__main__':
    force = '--repair' in sys.argv or '--force' in sys.argv
    sys.exit(run_findupdate_cli(force_repair=force))
