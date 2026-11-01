"""Build, package, and publish Broadcast Playroom v3.21 release."""
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

root = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

print("Step 1: Building frontend for v3.21...")
subprocess.run(['npm.cmd', 'run', 'build'], cwd=root, check=True)

dist_src = root / 'dist'
build_trials = root / 'build_trials'
build_trials.mkdir(exist_ok=True)

patch_lite = build_trials / 'patch-v3.21-lite.zip'
patch_full = build_trials / 'patch-v3.21-full.zip'

CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py'
]

def package_patch(src_patch, dst_patch, build_type):
    if dst_patch.exists(): dst_patch.unlink()
    with zipfile.ZipFile(dst_patch, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 1. dist/ at root and inside _internal/dist/
        for p in dist_src.rglob('*'):
            if p.is_file():
                rel = p.relative_to(dist_src).as_posix()
                zf.write(p, f"dist/{rel}")
                zf.write(p, f"_internal/dist/{rel}")
        # 2. Python runtime core scripts at root and inside _internal/
        for py_file in CORE_PYTHON_FILES:
            f_path = root / py_file
            if f_path.exists():
                zf.write(f_path, py_file)
                zf.write(f_path, f"_internal/{py_file}")
        # 3. version.json at root and inside _internal/
        v_info = {
            "product": "broadcast-playroom-3",
            "version": "3.21",
            "latest_version": "3.21",
            "build_type": build_type
        }
        zf.writestr('version.json', json.dumps(v_info, indent=2))
        zf.writestr('_internal/version.json', json.dumps(v_info, indent=2))
        # 4. broadcast playroom dev oauth credentials for legacy frozen exe fallback
        dev_dir = root.parent / 'broadcast playroom dev'
        if dev_dir.exists():
            for f in ['twitch_oauth.py', 'kick_oauth.py']:
                fp = dev_dir / f
                if fp.exists():
                    zf.write(fp, f"broadcast playroom dev/{f}")
                    zf.write(fp, f"_internal/broadcast playroom dev/{f}")
    print(f"Packaged {dst_patch.name} ({dst_patch.stat().st_size:,} bytes)")

package_patch(dist_src, patch_lite, 'lite')
package_patch(dist_src, patch_full, 'full')

hash_lite = digest(patch_lite)
hash_full = digest(patch_full)

changelog = """### Broadcast Playroom v3.21 Update Highlights

- **แก้ไขระบบเชื่อมต่อ Twitch Chatbot ให้พร้อมใช้งานทันที 100% (Instant Twitch Chatbot Authorization)**:
  - บรรจุกุญแจแอป Twitch และ KICK (OAuth Credentials) ในตัวแพ็กเกจโปรแกรมแบบ Built-in พร้อมระบบลงทะเบียน Environment Variables อัตโนมัติ
  - แก้ไขปัญหา "ไม่พบข้อมูลแอปสำหรับเชื่อมบัญชี" โดยมีตัวสำรองทั้งในระดับระบบ Windows และโฟลเดอร์แอป ไม่ต้องตั้งค่าใดๆ เพิ่มเติม
  - ปรับปรุงการตอบสนองของปุ่ม "เชื่อมต่อ Chatbot" ให้แสดงผล "กำลังเปิดเบราว์เซอร์…" ทันทีที่คลิก
- **ระบบป้องกัน Cache ค้าง & บังคับโหลดอัปเดตล่าสุด (Hard Anti-Cache Enforcement)**:
  - กำหนด Header `Cache-Control: no-cache, no-store, must-revalidate` ให้กับเซิร์ฟเวอร์ภายในตัวโปรแกรม
  - ใส่พารามิเตอร์ Cache-Busting (`&_v=...`) บนทุกหน้าต่างเครื่องมือและหน้าต่างตั้งค่า ป้องกัน WebView2 ดึงไฟล์เก่าจากดิสก์
  - เพิ่มระบบ Auto-Purge ล้างโฟลเดอร์แคชของ WebView2 และ Browser Profile อัตโนมัติทุกครั้งที่มีการลงอัปเดตใหม่
- **แก้ไขปัญหาดีเลย์ 2 นาทีเมื่อเปิดสตรีมยาวหรือไม่มีแชทนานๆ (Long Idle Chat & TTS Latency Fix)**:
  - ปิดการลดทอนความถี่ของตัวจับเวลาในระบบเบื้องหลัง (`--disable-background-timer-throttling`) เพื่อให้โปรแกรมดึงแชทและประมวลผลเสียงแบบเรียลไทม์เสมอแม้จะสลับหน้าจอไปเล่นเกมเต็มจอ
  - เพิ่ม Web Worker Heartbeat Ticker (800ms) ป้องกันบราวเซอร์หยุดทำงานเมื่อหน้าต่างหลักถูกย่อหรือบัง
  - เพิ่ม Audio Keep-alive และระบบเชื่อมต่อล่วงหน้า (TLS/DNS Warmup) ทุก 3 นาทีเพื่อให้อ่านออกเสียงได้ทันทีโดยไม่มีอาการสะดุด
"""

manifest = {
    "product": "broadcast-playroom-3",
    "version": "3.21",
    "latest_version": "3.21",
    "critical": False,
    "changelog": changelog.strip(),
    "lite": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.21/patch-v3.21-lite.zip",
        "sha256": hash_lite,
        "size": patch_lite.stat().st_size
    },
    "full": {
        "url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.21/patch-v3.21-full.zip",
        "sha256": hash_full,
        "size": patch_full.stat().st_size
    },
    "packages": {
        "lite": {
            "version": "3.21",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.21/patch-v3.21-lite.zip",
            "patch_sha256": hash_lite,
            "patch_size": patch_lite.stat().st_size
        },
        "full": {
            "version": "3.21",
            "patch_url": "https://github.com/zepiam/broadcast-playroom-3/releases/download/v3.21/patch-v3.21-full.zip",
            "patch_sha256": hash_full,
            "patch_size": patch_full.stat().st_size
        }
    }
}

# Update installed full directory with the newly generated patch and files
dst_full = Path(r"E:\DOCS\Documents\BroadcastPlayroom3\full")
if dst_full.exists():
    for f in CORE_PYTHON_FILES:
        sf = root / f
        if sf.exists():
            shutil.copy2(sf, dst_full / f)
            if (dst_full / '_internal').exists():
                shutil.copy2(sf, dst_full / '_internal' / f)
    # Sync dist
    for p in dist_src.rglob('*'):
        if p.is_file():
            rel = p.relative_to(dist_src)
            out1 = dst_full / 'dist' / rel
            out1.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out1)
            if (dst_full / '_internal').exists():
                out2 = dst_full / '_internal' / 'dist' / rel
                out2.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out2)
    # Write version.json
    (dst_full / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    if (dst_full / '_internal').exists():
        (dst_full / '_internal' / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print("Updated local full installation directory with v3.21 files.")

# Also save version.json locally in root
(root / 'version.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

# Clean out any old pending_update on this machine so fresh new zip is downloaded
pending_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'BroadcastPlayroom3/pending_update'
if pending_dir.exists():
    for f in pending_dir.iterdir():
        try:
            f.unlink()
        except OSError:
            pass
    print("Cleaned pending_update cache directory.")

print("Manifest for v3.21 generated successfully!")
