"""
Broadcast Playroom 3 - Automated Hugging Face Release Uploader
Uploads built release artifacts to men9ch/broadcast-playroom-3 automatically.
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from huggingface_hub import HfApi, login, get_token
except ImportError:
    print("[ERROR] huggingface_hub is not installed. Run: pip install huggingface_hub")
    sys.exit(1)

REPO_ID = "men9ch/broadcast-playroom-3"
DIST_DIR = Path(__file__).resolve().parent / "dist_releases"


def main():
    parser = argparse.ArgumentParser(description="Upload releases to Hugging Face")
    parser.add_argument("--token", default=None, help="Hugging Face write token (optional if already logged in)")
    parser.add_argument("--target", choices=["all", "full", "lite", "setup"], default="all", help="Target to upload")
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN") or get_token()
    if not token:
        print("[ERROR] No Hugging Face token found!")
        print("Please provide a token with Write access by either:")
        print("  1. Passing --token hf_xxxx")
        print("  2. Setting $env:HF_TOKEN = 'hf_xxxx'")
        print("  3. Running `huggingface-cli login` once in your terminal")
        print("Generate token at: https://huggingface.co/settings/tokens")
        sys.exit(1)

    api = HfApi(token=token)

    files_to_upload = []
    if args.target in ["all", "full"]:
        full_path = DIST_DIR / "BroadcastPlayroom3-Full.zip"
        if full_path.exists():
            files_to_upload.append(full_path)
    if args.target in ["all", "lite"]:
        lite_path = DIST_DIR / "BroadcastPlayroom3-Lite.zip"
        if lite_path.exists():
            files_to_upload.append(lite_path)
    if args.target in ["setup"]:
        setup_path = DIST_DIR / "BroadcastPlayroom3-Setup.exe"
        if setup_path.exists():
            files_to_upload.append(setup_path)

    if not files_to_upload:
        print(f"[WARN] No release files found in {DIST_DIR}")
        sys.exit(1)

    print(f"=== Starting Upload to Hugging Face: {REPO_ID} ===")
    for file_path in files_to_upload:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f">> Uploading {file_path.name} ({size_mb:.2f} MB)...")
        try:
            api.upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=file_path.name,
                repo_id=REPO_ID,
                repo_type="model",
            )
            print(f"   [OK] Successfully uploaded: {file_path.name}")
        except Exception as e:
            print(f"   [FAILED] Error uploading {file_path.name}: {e}")
            sys.exit(1)

    print("=== All requested files uploaded successfully! ===")


if __name__ == "__main__":
    main()
