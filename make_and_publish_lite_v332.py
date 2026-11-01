import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

root = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3")
sys.path.insert(0, str(root))
from package_clean_releases import audit_directory, prepare_release_dir

dist_releases = root / "dist_releases"
dist_releases.mkdir(parents=True, exist_ok=True)

lite_target_zip = dist_releases / "BroadcastPlayroom3-Lite.zip"
lite_dir = root / "build_trials" / "lite" / "BroadcastPlayroom3-Lite"
dist_src = root / "dist"

CORE_PYTHON_FILES = [
    'launch_dev.py', 'updater.py', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py',
    'bot_auth.py', 'bot_oauth_credentials.py', 'twitch_oauth.py', 'kick_oauth.py',
    'chat_bridge.py', 'chat_twitch.py', 'chat_kick.py', 'chat_youtube.py',
    'chat_soop.py', 'chat_mylive.py', 'tts_service.py', 'dns_settings.py',
    'dist_integrity.py', 'smoke_test_gate.py', 'findupdate.py', 'FindUpdate.bat', 'avatar_cache_service.py'
]

print("=== Step 1: Updating BroadcastPlayroom3-Lite Staging Directory ===")
assert lite_dir.exists(), f"Lite directory not found: {lite_dir}"

# 1. Update _internal/dist
internal_dist = lite_dir / "_internal" / "dist"
if internal_dist.exists():
    shutil.rmtree(internal_dist)
shutil.copytree(dist_src, internal_dist)
print(f"  [OK] Synchronized dist/ to {internal_dist}")

# 2. Update core python files
for f in CORE_PYTHON_FILES:
    sf = root / f
    if sf.exists():
        shutil.copy2(sf, lite_dir / "_internal" / f)
print("  [OK] Updated CORE_PYTHON_FILES in _internal")

# 3. Update version.json
manifest_file = root / "version.json"
manifest_data = manifest_file.read_text(encoding='utf-8')
(lite_dir / "version.json").write_text(manifest_data, encoding='utf-8')
(lite_dir / "_internal" / "version.json").write_text(manifest_data, encoding='utf-8')
print("  [OK] Updated version.json in Lite staging")

# 4. Prepare assets & splash
prepare_release_dir(lite_dir)

# 5. Privacy Audit
violations, f_count = audit_directory(lite_dir)
if violations:
    raise RuntimeError(f"Privacy violations found: {violations}")
print(f"  [OK] Privacy audit passed: {f_count} files verified 100% clean (0 leaks).")

# 6. Compress with 7-Zip
print(f"\n=== Step 2: Compressing {lite_target_zip.name} with 7-Zip ===")
seven_zip = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
if lite_target_zip.exists():
    lite_target_zip.unlink()

cmd_7z = [
    seven_zip, "a", "-tzip", "-mx=5", "-r",
    str(lite_target_zip),
    "*"
]
subprocess.run(cmd_7z, cwd=lite_dir, check=True)
size_mb = lite_target_zip.stat().st_size / (1024 * 1024)
print(f"  [SUCCESS] Created {lite_target_zip.name} ({size_mb:.2f} MB)")

# 7. Upload to HuggingFace
print(f"\n=== Step 3: Uploading {lite_target_zip.name} to Hugging Face ===")
from huggingface_hub import HfApi
api = HfApi()
repo_id = "men9ch/broadcast-playroom-3"

api.upload_file(
    path_or_fileobj=str(lite_target_zip),
    path_in_repo="BroadcastPlayroom3-Lite.zip",
    repo_id=repo_id,
    commit_message="Release v3.32: BroadcastPlayroom3-Lite.zip installer package"
)
print("  [SUCCESS] Uploaded BroadcastPlayroom3-Lite.zip to HuggingFace root successfully!")

print("\n=== FINISHED ALL TASKS FOR LITE ARCHIVE ===")
