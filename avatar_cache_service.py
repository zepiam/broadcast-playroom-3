"""
Broadcast Playroom - Real Platform Avatar Fetcher & 50px Cache Service
Fetches real user avatars from Twitch / platforms, resizes them to 50x50 PNGs,
and stores them in a local cache directory.
"""
import io
import os
import re
import urllib.request
from pathlib import Path
from PIL import Image

def get_avatar_cache_dir(data_root: Path) -> Path:
    cache_dir = Path(data_root) / "avatar_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_cache_info(data_root: Path) -> dict:
    cache_dir = get_avatar_cache_dir(data_root)
    total_bytes = 0
    count = 0
    try:
        for f in cache_dir.iterdir():
            if f.is_file():
                total_bytes += f.stat().st_size
                count += 1
    except Exception:
        pass
    size_mb = total_bytes / (1024 * 1024)
    return {
        "size_bytes": total_bytes,
        "size_mb": f"{size_mb:.2f}",
        "count": count
    }

def clear_cache(data_root: Path) -> bool:
    cache_dir = get_avatar_cache_dir(data_root)
    try:
        for f in cache_dir.iterdir():
            if f.is_file():
                try:
                    f.unlink()
                except OSError:
                    pass
        return True
    except Exception:
        return False

def get_or_fetch_avatar(data_root: Path, platform: str, username: str) -> bytes | None:
    if not username:
        return None
    platform = (platform or "twitch").lower()
    safe_user = re.sub(r'[^a-zA-Z0-9_\u0E00-\u0E7F-]', '_', username.lower().strip())
    if not safe_user:
        return None

    cache_dir = get_avatar_cache_dir(data_root)
    cache_file = cache_dir / f"{platform}_{safe_user}.png"

    # Return cached 50x50 avatar if available
    if cache_file.exists() and cache_file.stat().st_size > 50:
        try:
            return cache_file.read_bytes()
        except Exception:
            pass

    # Fetch from platform
    avatar_url = None
    if platform == "twitch":
        try:
            req = urllib.request.Request(
                f"https://decapi.me/twitch/avatar/{safe_user}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as r:
                res_url = r.read().decode("utf-8").strip()
                if res_url.startswith("http"):
                    avatar_url = res_url
        except Exception:
            pass

    if not avatar_url:
        return None

    # Download and resize to 50x50 PNG
    try:
        img_req = urllib.request.Request(avatar_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(img_req, timeout=3.5) as r:
            img_data = r.read()

        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        img.thumbnail((50, 50), Image.Resampling.LANCZOS)

        out_io = io.BytesIO()
        img.save(out_io, format="PNG", optimize=True)
        final_bytes = out_io.getvalue()

        # Save to cache
        cache_file.write_bytes(final_bytes)
        return final_bytes
    except Exception:
        return None
