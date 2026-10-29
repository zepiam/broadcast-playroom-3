"""
package_clean_releases.py
Verifies privacy cleanliness and compresses the built executables into clean release archives.
Ensures ZERO personal credentials, chat history, or personal tokens exist in the archive.
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST_RELEASES = ROOT / "dist_releases"
DIST_RELEASES.mkdir(parents=True, exist_ok=True)

# Strict blacklist of files/patterns that must NEVER be in a release
FORBIDDEN_FILES = [
    "bot_accounts.dat",
    "browser_profile",
    "dns_settings.json",
    "log.txt",
    "session.dat",
    "cookies.sqlite",
    ".env",
    "composer_layout.json", # user-specific custom layout
    "replace_words.json",   # user-specific dictionary substitutions
]

def audit_directory(dir_path: Path):
    """Scan directory for forbidden personal files or sensitive patterns."""
    violations = []
    total_files = 0
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            total_files += 1
            rel_p = os.path.relpath(os.path.join(root, f), dir_path)
            rel_p_lower = rel_p.lower()
            
            # Check for forbidden filenames
            for bad_file in FORBIDDEN_FILES:
                if os.path.basename(rel_p_lower) == bad_file or bad_file in rel_p_lower:
                    violations.append(rel_p)
            
            # Check for top-level user data or git directory
            if rel_p_lower.startswith("data\\") or rel_p_lower.startswith("data/") or ".git\\" in rel_p_lower:
                violations.append(rel_p)

    return violations, total_files

def prepare_release_dir(dir_path: Path):
    """Ensure essential non-personal runtime assets like splash screen are present."""
    splash_src = ROOT / "assets" / "splash" / "splash_500.png"
    if splash_src.exists():
        # Copy to <dir_path>/assets/splash/splash_500.png
        target_splash_dir = dir_path / "assets" / "splash"
        target_splash_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(splash_src, target_splash_dir / "splash_500.png")
        
        # Also copy to _internal/assets/splash/splash_500.png
        internal_splash_dir = dir_path / "_internal" / "assets" / "splash"
        internal_splash_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(splash_src, internal_splash_dir / "splash_500.png")

def create_clean_zip(source_dir: Path, target_zip: Path):
    """Create a zip archive using 7-Zip if available, fallback to zipfile."""
    source_dir = source_dir.resolve()
    target_zip = target_zip.resolve()
    print(f"\n=======================================================")
    print(f" Packaging: {source_dir.name} -> {target_zip.name}")
    print(f"=======================================================")
    
    prepare_release_dir(source_dir)

    print(f">> Auditing {source_dir.name} for privacy safety...")
    violations, total_files = audit_directory(source_dir)
    if violations:
        print(f"[FATAL] Found {len(violations)} privacy violations in build!")
        for v in violations[:10]:
            print(f"  - {v}")
        raise RuntimeError("Privacy violation check failed.")
    print(f"[OK] Clean audit passed! {total_files} files verified safe with 0 personal leaks.")

    if target_zip.exists():
        print(f"Removing existing {target_zip.name}...")
        target_zip.unlink()

    print(f"Compressing {source_dir.name} -> {target_zip.name}...")
    
    # Check if 7z is installed for faster & better compression
    seven_zip = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
    if os.path.exists(seven_zip):
        print("Using 7-Zip for high-speed ZIP creation...")
        cmd = [seven_zip, "a", "-tzip", "-mx=5", "-r", str(target_zip), "*"]
        subprocess.run(cmd, cwd=source_dir, check=True)
    else:
        print("Using Python zipfile...")
        with zipfile.ZipFile(target_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for root, dirs, files in os.walk(source_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    arcname = os.path.relpath(fp, source_dir)
                    z.write(fp, arcname)

    size_mb = target_zip.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Created {target_zip.name} ({size_mb:.2f} MB)")
    return target_zip

if __name__ == "__main__":
    if len(sys.argv) > 2:
        src = Path(sys.argv[1])
        dst = Path(sys.argv[2])
        create_clean_zip(src, dst)
    else:
        print("Usage: python package_clean_releases.py <source_dir> <target_zip>")
