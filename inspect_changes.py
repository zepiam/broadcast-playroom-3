#!/usr/bin/env python3
"""
inspect_changes.py — Antigravity Git Change Inspector & Audit Tool
===================================================================
เครื่องมือตรวจสอบความเปลี่ยนแปลงหลัง git pull หรือเริ่มต้นเซสชันใหม่
ช่วยให้รู้ทันทีว่ามีไฟล์อะไรเปลี่ยนบ้าง ฟังก์ชันหรือจุดไหนถูกแก้ไข
เพื่อตรวจสอบได้ตรงจุด ไม่ต้องไปรื้อโค้ดใหม่ทั้งหมด
"""

import os
import subprocess
import sys
from pathlib import Path

# Set output encoding to UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_git(cmd):
    try:
        res = subprocess.check_output(['git'] + cmd, stderr=subprocess.STDOUT)
        return res.decode('utf-8', errors='replace').strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='replace').strip()
    except Exception as ex:
        return f"Error executing git {cmd}: {ex}"

def main():
    target_ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD~1'
    
    print("=" * 75)
    print("🔍 [ANTIGRAVITY CODEBASE CHANGE INSPECTOR]")
    print("=" * 75)

    # 1. Current Branch & Status
    branch = run_git(['branch', '--show-current'])
    print(f"📌 Branch ปัจจุบัน: {branch}")
    
    status = run_git(['status', '--short'])
    if status:
        print("\n⚠️  [Uncommitted / Staged Changes]:")
        for line in status.splitlines():
            print(f"   {line}")
    else:
        print("\n✅ Working tree สะอาด (ไม่มีไฟล์ค้างแก้)")

    # 2. Recent Commits
    print("\n📜 [ประวัติ 7 Commits ล่าสุด]:")
    recent_logs = run_git(['log', '-n', '7', '--pretty=format:%h | %cd | %s', '--date=format:%Y-%m-%d %H:%M'])
    for line in recent_logs.splitlines():
        print(f"   • {line}")

    # 3. Diff against Target Ref
    print(f"\n🔎 [สิ่งที่เปลี่ยนแปลงเปรียบเทียบกับ {target_ref}..HEAD]:")
    changed_files = run_git(['diff', '--name-status', target_ref, 'HEAD'])
    
    categories = {
        'Frontend (HTML/Template)': [],
        'Stylesheets (CSS)': [],
        'Frontend Scripts (JS)': [],
        'Backend / Runtime (Python)': [],
        'Config / Manifest / Others': []
    }
    
    for line in changed_files.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            status_code, filepath = parts[0], parts[1]
            p = filepath.lower()
            item = f"{status_code}\t{filepath}"
            if p.endswith('.html'):
                categories['Frontend (HTML/Template)'].append(item)
            elif p.endswith('.css'):
                categories['Stylesheets (CSS)'].append(item)
            elif p.endswith('.js'):
                categories['Frontend Scripts (JS)'].append(item)
            elif p.endswith('.py'):
                categories['Backend / Runtime (Python)'].append(item)
            else:
                categories['Config / Manifest / Others'].append(item)

    has_files = False
    for cat_name, file_list in categories.items():
        if file_list:
            has_files = True
            print(f"\n   📁 {cat_name}:")
            for f in file_list:
                print(f"      - {f}")
    
    if not has_files:
        print("   (ไม่มีไฟล์เปลี่ยนแปลงในช่วงที่เลือก)")

    # 4. Detailed Function / Header Diff Summary
    print(f"\n📝 [สรุปฟังก์ชัน / ส่วนโค้ดที่ถูกแก้ไข ({target_ref}..HEAD)]:")
    func_diff = run_git(['diff', '-U0', target_ref, 'HEAD'])
    found_functions = set()
    for line in func_diff.splitlines():
        if line.startswith('@@'):
            parts = line.split('@@')
            if len(parts) >= 3 and parts[2].strip():
                func_context = parts[2].strip()
                found_functions.add(func_context)
    
    if found_functions:
        for fn in sorted(found_functions)[:25]:
            print(f"   ⚡ {fn}")
        if len(found_functions) > 25:
            print(f"   ... และอีก {len(found_functions) - 25} จุด")
    else:
        print("   (ไม่พบ function header ที่ชัดเจน หรือเป็นการแก้ส่วน layout/markup)")

    # 5. Diff Stat
    print("\n📊 [สถิติจำนวนบรรทัดที่เปลี่ยนแปลง]:")
    stat = run_git(['diff', '--stat', target_ref, 'HEAD'])
    for line in stat.splitlines():
        print(f"   {line}")

    print("\n" + "=" * 75)
    print("💡 ข้อแนะนำสำหรับ Antigravity:")
    print(f"   1. รัน 'git diff {target_ref} <filepath>' เพื่อดูโค้ดเฉพาะจุดที่เปลี่ยน")
    print("   2. ตรวจสอบเฉพาะจุดที่กระทบ ไม่แก้สุ่มสี่สุ่มห้าหรือรื้อส่วนที่ไม่เกี่ยวข้อง")
    print("   3. รันเทสต์ E2E บน dist/ เสมอก่อนปล่อยอัปเดต")
    print("=" * 75)

if __name__ == '__main__':
    main()
