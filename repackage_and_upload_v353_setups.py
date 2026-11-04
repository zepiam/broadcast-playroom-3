import os
import sys
import shutil
import hashlib
import json
import subprocess
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from huggingface_hub import HfApi
except ImportError:
    print("Error: huggingface_hub not installed.")
    sys.exit(1)

ROOT = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")
DIST_RELEASES = ROOT / "dist_releases"
DIST_RELEASES.mkdir(parents=True, exist_ok=True)

SEVEN_ZIP = Path(r"C:\Program Files\7-Zip\7z.exe")
VERSION = "3.53"

CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_tiktok.py', 'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat',
    'avatar_cache_service.py', 'plugin_manager.py', 'app_window_frame.py', 'defender_helper.py',
    'BP3_PatchInstaller.exe', 'version.json', 'package.json'
]

TARGETS = [
    ("lite", ROOT / "build_trials" / "lite" / "BroadcastPlayroom3-Lite", DIST_RELEASES / "BroadcastPlayroom3-Lite.zip"),
    ("full", ROOT / "build_trials" / "full" / "BroadcastPlayroom3-Full", DIST_RELEASES / "BroadcastPlayroom3-Full.zip"),
]

def clean_stale_caches(target_dir: Path):
    """Remove any stale cache files, browser profiles, or __pycache__ before packaging."""
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for d in dirs:
            if d in ('__pycache__', 'browser_profile', 'webview_data', 'Cache', 'Code Cache', 'GPUCache', 'ShaderCache'):
                dp = Path(root) / d
                try:
                    shutil.rmtree(dp, ignore_errors=True)
                except Exception:
                    pass

def sync_edition_folder(edition: str, target_dir: Path):
    print(f"\n--- Synchronizing {edition.upper()} edition directory ({target_dir}) ---")
    if not target_dir.exists():
        raise RuntimeError(f"Target directory {target_dir} does not exist!")

    # 1. Clean stale caches
    clean_stale_caches(target_dir)

    # 2. Copy core python files to root and _internal
    for f in CORE_PYTHON_FILES:
        sf = ROOT / f
        if sf.exists():
            shutil.copy2(sf, target_dir / f)
            internal_f = target_dir / "_internal" / f
            internal_f.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sf, internal_f)

    # 3. Copy docs and plugins
    for extra_folder in ['docs', 'plugins']:
        src_extra = ROOT / extra_folder
        if src_extra.is_dir():
            dst_extra = target_dir / extra_folder
            dst_extra.mkdir(parents=True, exist_ok=True)
            for item in src_extra.rglob('*'):
                if item.is_file():
                    rel = item.relative_to(src_extra)
                    dest_file = dst_extra / rel
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
                    int_dest = target_dir / "_internal" / extra_folder / rel
                    int_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, int_dest)

    # 4. Copy dist directory
    dist_src = ROOT / "dist"
    for dst_dist in [target_dir / "dist", target_dir / "_internal" / "dist"]:
        dst_dist.mkdir(parents=True, exist_ok=True)
        for item in dist_src.rglob('*'):
            if item.is_file():
                rel = item.relative_to(dist_src)
                target_file = dst_dist / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_file)

    # 5. Verify version.json inside target
    ver_file = target_dir / "version.json"
    with open(ver_file, "r", encoding="utf-8") as vf:
        v_data = json.load(vf)
    print(f"  [VERIFY] {edition.upper()} version is {v_data.get('version')}")
    assert v_data.get('version') == VERSION, f"Expected version {VERSION}, got {v_data.get('version')}"

def compress_archive(source_dir: Path, target_zip: Path):
    print(f"\n--- Compressing {source_dir.name} -> {target_zip.name} ---")
    if target_zip.exists():
        target_zip.unlink()

    cmd = [
        str(SEVEN_ZIP),
        "a",
        "-tzip",
        "-mx=5",
        "-r",
        str(target_zip),
        "*"
    ]
    t0 = time.time()
    subprocess.run(cmd, cwd=source_dir, check=True)
    elapsed = time.time() - t0
    size_mb = target_zip.stat().st_size / (1024 * 1024)
    print(f"  [OK] Created {target_zip.name} ({size_mb:.2f} MB in {elapsed:.1f}s)")

def rebuild_setup_installer():
    print("\n--- Rebuilding BroadcastPlayroom3-Setup.exe ---")
    setup_spec = ROOT / "BroadcastPlayroom3-Setup.spec"
    if setup_spec.exists():
        subprocess.run(["pyinstaller", "BroadcastPlayroom3-Setup.spec", "--noconfirm", "--distpath", str(DIST_RELEASES)], cwd=ROOT, check=True)
    else:
        subprocess.run([sys.executable, "build_setup_installer.py"], cwd=ROOT, check=True)
    setup_exe = DIST_RELEASES / "BroadcastPlayroom3-Setup.exe"
    assert setup_exe.exists(), "BroadcastPlayroom3-Setup.exe was not created!"
    print(f"  [OK] BroadcastPlayroom3-Setup.exe built ({setup_exe.stat().st_size / (1024*1024):.2f} MB)")
    return setup_exe

def upload_to_huggingface(files_to_upload):
    print("\n--- Uploading Standalone Setup Distributions to Hugging Face ---")
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        token_path = Path.home() / ".cache" / "huggingface" / "token"
        if token_path.exists():
            hf_token = token_path.read_text().strip()

    if not hf_token:
        print("Error: HF_TOKEN not found!")
        return False

    api = HfApi(token=hf_token)
    repo_id = "men9ch/broadcast-playroom-3"

    for local_path, repo_path in files_to_upload:
        print(f"Uploading {local_path.name} -> {repo_path}...")
        api.upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=repo_path,
            repo_id=repo_id,
            repo_type="model"
        )
        print(f"  [OK] Uploaded {local_path.name} to Hugging Face!")
    return True

if __name__ == "__main__":
    t_start = time.time()
    print("=================================================================")
    print(f" REPACKAGING STANDALONE SETUP DISTRIBUTIONS FOR v{VERSION}")
    print("=================================================================")

    # Step 1: Sync both folders
    for edition, src_folder, dst_zip in TARGETS:
        sync_edition_folder(edition, src_folder)

    # Step 2: Compress both archives
    for edition, src_folder, dst_zip in TARGETS:
        compress_archive(src_folder, dst_zip)

    # Step 3: Rebuild Setup installer
    setup_exe = rebuild_setup_installer()

    # Step 4: Upload to Hugging Face
    upload_list = [
        (setup_exe, "BroadcastPlayroom3-Setup.exe"),
        (DIST_RELEASES / "BroadcastPlayroom3-Lite.zip", "BroadcastPlayroom3-Lite.zip"),
        (DIST_RELEASES / "BroadcastPlayroom3-Full.zip", "BroadcastPlayroom3-Full.zip"),
    ]
    upload_to_huggingface(upload_list)

    total_time = time.time() - t_start
    print(f"\n=================================================================")
    print(f" ALL PACKAGES REPACKAGED & UPLOADED IN {total_time:.1f} SECONDS!")
    print(f"=================================================================")
