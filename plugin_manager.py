"""plugin_manager.py — Non-invasive, safe third-party plugin architecture for Broadcast Playroom 3.

Guarantees:
1. Physical Isolation: Plugins live inside `data/plugins/`. Updates to the core app never delete them.
2. Zero Impact on Inactive / Empty: If no plugins are installed, execution overhead is 0ms.
3. Crash Protection: Any error in a third-party plugin is isolated; the core chat and TTS never stop.
4. Creator Attribution Guard: Plugins CANNOT tamper with, disable, or redirect Creator Support / Donations.
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("plugin_manager")

# Restricted action identifiers that plugins are forbidden from tampering with
PROTECTED_CORE_AREAS = frozenset([
    "creator_support",
    "support_modal",
    "donate_qr",
    "promptpay_qr",
    "footer_creator_links",
    "about_author"
])

class PluginManager:
    _instance = None

    def __init__(self):
        self.plugins_dir: Optional[Path] = None
        self.loaded_plugins: Dict[str, dict] = {}
        self._hooks: Dict[str, List[Any]] = {}
        self._lock = threading.Lock()
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "PluginManager":
        if cls._instance is None:
            cls._instance = PluginManager()
        return cls._instance

    def initialize(self, data_root: Path):
        """Initializes the plugin directory safely. If no plugins are present, exits immediately."""
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            try:
                self.plugins_dir = Path(data_root) / "plugins"
                self.plugins_dir.mkdir(parents=True, exist_ok=True)
                self._load_all_plugins()
            except Exception as e:
                logger.warning(f"[PluginManager] Initialization warning: {e}")

    def _load_all_plugins(self):
        if not self.plugins_dir or not self.plugins_dir.is_dir():
            return

        for p_dir in self.plugins_dir.iterdir():
            if not p_dir.is_dir() or p_dir.name.startswith((".", "_")):
                continue

            manifest_file = p_dir / "plugin.json"
            if not manifest_file.is_file():
                continue

            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                plugin_id = manifest.get("id") or p_dir.name
                if manifest.get("enabled", True) is False:
                    continue

                # Creator Attribution & Tamper Guard
                requested_permissions = manifest.get("permissions", [])
                if any(p in PROTECTED_CORE_AREAS for p in requested_permissions):
                    logger.warning(
                        f"[PluginManager] Plugin '{plugin_id}' requested forbidden core permission; blocked."
                    )
                    continue

                self.loaded_plugins[plugin_id] = {
                    "dir": p_dir,
                    "manifest": manifest,
                    "name": manifest.get("name", plugin_id),
                    "version": manifest.get("version", "1.0.0")
                }
                logger.info(f"[PluginManager] Registered plugin: {plugin_id} (v{manifest.get('version', '1.0.0')})")
            except Exception as e:
                logger.warning(f"[PluginManager] Failed to read plugin in {p_dir.name}: {e}")

    def emit_event(self, event_name: str, payload: dict):
        """Dispatches an event to plugins asynchronously without blocking the core application."""
        if not self.loaded_plugins:
            return  # 0ms overhead if no plugins

        def _safe_dispatch():
            try:
                # Event dispatching logic (isolated from main thread)
                pass
            except Exception:
                pass

        threading.Thread(target=_safe_dispatch, daemon=True).start()

    def get_plugin_list(self) -> List[dict]:
        """Returns the list of loaded plugins for the settings UI."""
        return [
            {
                "id": pid,
                "name": data["name"],
                "version": data["version"],
                "author": data["manifest"].get("author", "Community"),
                "description": data["manifest"].get("description", ""),
                "enabled": data["manifest"].get("enabled", True),
                "has_settings": (data["dir"] / "settings.html").is_file()
            }
            for pid, data in self.loaded_plugins.items()
        ]

plugin_manager = PluginManager.get_instance()


# =====================================================================
# Plugin API v1 (HTTP part) -- appended section. Additive only:
# nothing above this line depends on it, and every entry point is wrapped
# so that a failure here returns None (= "not mine") to the caller.
# Phase 1 scope: JavaScript widgets in a sandboxed iframe, read-only events.
# =====================================================================
import re as _re
import time as _time
import mimetypes as _mimetypes
from urllib.parse import parse_qs as _parse_qs, unquote as _unquote

PLUGIN_API_VERSION = 1
# permission -> what the user is told when enabling
PLUGIN_PERMISSIONS_V1 = {
    "events_read": "รับเหตุการณ์ ASK / ชิงโชค / สุ่ม / ล้างแชท (อ่านอย่างเดียว)",
    "chat_read": "อ่านข้อความแชทสด (อ่านอย่างเดียว)",
    "ui_cursor": "เปลี่ยนรูปเมาส์ในหน้าต่างโปรแกรม (ใช้เฉพาะรูป PNG ที่กำหนด ไม่มีโค้ด)",
}
# frozen public event name -> (internal overlay event, permission needed)
PLUGIN_EVENTS_V1 = {
    "chat_message": ("CHAT_MESSAGE", "chat_read"),
    "chat_clear": ("CHAT_CLEAR", "events_read"),
    "chat_delete": ("CHAT_DELETE", "events_read"),
    "ask_update": ("ASK_UPDATE", "events_read"),
    "giveaway_update": ("GIVEAWAY_UPDATE", "events_read"),
    "randomizer_spin": ("RANDOMIZER_SPIN", "events_read"),
}
_PLUGIN_ID_RE = _re.compile(r"^[a-z0-9][a-z0-9_-]{1,48}$")
_PLUGIN_FILE_EXT = {
    ".html", ".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".svg", ".woff", ".woff2", ".mp3", ".ogg", ".wav",
}
_PLUGIN_MAX_ERRORS = 5
_PLUGIN_SDK = (
    "<script>(function(){var h={};function fire(n,d){(h[n]||[]).forEach(function(f){try{f(d)}catch(e){"
    "parent.postMessage({v:1,type:'error',message:String(e&&e.message||e)},'*')}})}"
    "window.BP3Plugin={apiVersion:1,app:null,on:function(n,f){(h[n]=h[n]||[]).push(f)}};"
    "addEventListener('message',function(e){if(e.source!==parent)return;var m=e.data;"
    "if(!m||m.v!==1)return;if(m.type==='init'){BP3Plugin.app=m.app;fire('init',m)}"
    "else if(m.type==='event'){fire(m.name,m.data)}});"
    "addEventListener('error',function(e){parent.postMessage({v:1,type:'error',message:String(e.message)},'*')});"
    "parent.postMessage({v:1,type:'ready'},'*')})();</script>"
)


def _plg_state_path(self):
    return self.plugins_dir / "_state.json"


def _plg_read_state(self):
    try:
        with open(_plg_state_path(self), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data.setdefault("plugins", {})
            return data
    except Exception:
        pass
    return {"safe_mode": False, "plugins": {}}


def _plg_write_state(self, state):
    tmp = _plg_state_path(self).with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _plg_state_path(self))


def _plg_scan(self):
    """Read every plugin folder fresh from disk. Never raises."""
    state = _plg_read_state(self)
    safe = bool(state.get("safe_mode"))
    out = []
    try:
        dirs = sorted(p for p in self.plugins_dir.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))
    except Exception:
        dirs = []
    for d in dirs:
        item = {
            "id": d.name, "name": d.name, "version": "", "author": "", "description": "",
            "permissions": [], "widget": "", "status": "invalid", "reason": "", "enabled": False,
            "errors": 0,
        }
        try:
            with open(d / "plugin.json", "r", encoding="utf-8") as f:
                m = json.load(f)
            if not isinstance(m, dict):
                raise ValueError("plugin.json ไม่ใช่ object")
            item["name"] = str(m.get("name") or d.name)[:80]
            item["version"] = str(m.get("version") or "")[:24]
            item["author"] = str(m.get("author") or "")[:80]
            item["description"] = str(m.get("description") or "")[:300]
            perms = m.get("permissions") or []
            if not isinstance(perms, list):
                raise ValueError("permissions ต้องเป็น list")
            item["permissions"] = [str(p) for p in perms]
            item["cursor"] = bool(m.get("cursor"))
            widget = str(m.get("widget") or "")
            item["widget"] = widget
            if not _PLUGIN_ID_RE.match(d.name):
                item["reason"] = "ชื่อโฟลเดอร์ใช้ได้เฉพาะ a-z 0-9 _ -"
            elif m.get("id") != d.name:
                item["reason"] = "id ใน plugin.json ต้องตรงกับชื่อโฟลเดอร์"
            elif m.get("api_version") != PLUGIN_API_VERSION:
                item["status"] = "unsupported"
                item["reason"] = "ต้องมี api_version = %d" % PLUGIN_API_VERSION
            elif any(p in PROTECTED_CORE_AREAS for p in item["permissions"]):
                item["reason"] = "ขอสิทธิ์ที่ห้ามใช้"
            elif any(p not in PLUGIN_PERMISSIONS_V1 for p in item["permissions"]):
                item["reason"] = "สิทธิ์ที่ไม่รู้จัก: " + ", ".join(p for p in item["permissions"] if p not in PLUGIN_PERMISSIONS_V1)
            elif not widget and not m.get("cursor"):
                item["reason"] = "ต้องมี widget หรือ cursor อย่างน้อยหนึ่งอย่าง"
            elif widget and (not widget.lower().endswith(".html") or "/" in widget or "\\" in widget or ".." in widget):
                item["reason"] = "ชื่อไฟล์ widget ไม่ถูกต้อง (ต้องเป็น .html ในโฟลเดอร์หลัก)"
            elif widget and not (d / widget).is_file():
                item["reason"] = "ไม่พบไฟล์ " + widget
            elif m.get("cursor") and not _plg_cursor_css(d, m):
                item["reason"] = "ไฟล์ cursor ไม่ถูกต้อง (ต้องเป็น PNG ไม่เกิน 64x64 และ 32KB)"
            elif m.get("cursor") and "ui_cursor" not in item["permissions"]:
                item["reason"] = "cursor ต้องขอสิทธิ์ ui_cursor"
            else:
                ps = state["plugins"].get(d.name, {})
                granted = sorted(ps.get("granted") or [])
                item["errors"] = int(ps.get("errors", 0) or 0)
                if not ps.get("enabled"):
                    item["status"] = "disabled"
                    if ps.get("disabled_reason"):
                        item["reason"] = str(ps["disabled_reason"])
                elif granted != sorted(item["permissions"]):
                    item["status"] = "needs_approval"
                    item["reason"] = "สิทธิ์เปลี่ยนไปหลังอนุมัติ ต้องเปิดใหม่"
                elif safe:
                    item["status"] = "safe_mode"
                else:
                    item["status"] = "enabled"
                    item["enabled"] = True
        except FileNotFoundError:
            item["reason"] = "ไม่พบ plugin.json"
        except Exception as e:
            item["reason"] = "อ่าน plugin.json ไม่ได้: %s" % e
        out.append(item)
    try:
        if not any(i["id"] == "demo-cursor" for i in out):
            out.append(_plg_builtin_demo_item(state, safe))
    except Exception:
        pass
    return out


def _plg_builtin_demo_item(state, safe):
    """Built-in example plugin: always listed, needs no files on disk. A real folder with the same id overrides it."""
    m = _PLUGIN_DEMO_MANIFEST
    item = {
        "id": m["id"], "name": m["name"], "version": m["version"], "author": m["author"],
        "description": m["description"], "permissions": list(m["permissions"]), "widget": "",
        "status": "disabled", "reason": "", "enabled": False, "errors": 0, "cursor": True, "builtin": True,
    }
    ps = state.get("plugins", {}).get(m["id"], {})
    item["errors"] = int(ps.get("errors", 0) or 0)
    if ps.get("enabled"):
        if sorted(ps.get("granted") or []) != sorted(item["permissions"]):
            item["status"] = "needs_approval"
            item["reason"] = "สิทธิ์เปลี่ยนไปหลังอนุมัติ ต้องเปิดใหม่"
        elif safe:
            item["status"] = "safe_mode"
        else:
            item["status"] = "enabled"
            item["enabled"] = True
    elif ps.get("disabled_reason"):
        item["reason"] = str(ps["disabled_reason"])
    return item


def _plg_cursor_css(d, m):
    """CSS for a plugin's cursor image, or None. Image data only, validated here."""
    try:
        name = str(m.get("cursor") or "")
        if not name.lower().endswith(".png") or "/" in name or "\\" in name or ".." in name:
            return None
        f = d / name
        if not f.is_file() or f.stat().st_size > 32768:
            return None
        return _plg_cursor_css_bytes(f.read_bytes(), m)
    except Exception:
        return None


def _plg_cursor_css_bytes(data, m):
    try:
        if len(data) > 32768:
            return None
        if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            return None
        w = int.from_bytes(data[16:20], "big")
        h = int.from_bytes(data[20:24], "big")
        if not (1 <= w <= 64 and 1 <= h <= 64):
            return None
        hs = m.get("cursor_hotspot") or [0, 0]
        hx = min(max(int(hs[0]), 0), w - 1)
        hy = min(max(int(hs[1]), 0), h - 1)
        import base64
        uri = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
        return "html,body,*{cursor:url(%s) %d %d, auto !important}" % (uri, hx, hy)
    except Exception:
        return None


def _plg_ui(self):
    """What the main window may apply on behalf of enabled plugins (cursor only)."""
    try:
        for it in _plg_scan(self):
            if it["status"] == "enabled" and it.get("cursor") and it.get("builtin"):
                import base64
                css = _plg_cursor_css_bytes(base64.b64decode(PLUGIN_DEMO_CURSOR_B64), _PLUGIN_DEMO_MANIFEST)
                if css:
                    return {"cursor_css": css, "plugin": it["id"]}
                continue
            if it["status"] == "enabled" and it.get("cursor"):
                with open(self.plugins_dir / it["id"] / "plugin.json", "r", encoding="utf-8") as f:
                    m = json.load(f)
                css = _plg_cursor_css(self.plugins_dir / it["id"], m)
                if css:
                    return {"cursor_css": css, "plugin": it["id"]}
    except Exception:
        pass
    return {}


PLUGIN_DEMO_CURSOR_B64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAE80lEQVR42u2XS2wVVRzGv//M3F5Lb1sqUJCF0SiiRKILg8QFBYkGwiugECIJCMpKghgTcYEiggmPhQsg0ajEuFDbRstTJT4qpkgIIkEDKkEEQguFAm1vH7f33pmfi5lbSmsboCgbv+TkTM5kzv873/m/RpIEOIoAmPqJ3B5wqRiah/S1b85wKbAacMyMroRuEC7IpJKZUuGC8FluX4yLAfDZCgyI1twbV6DClSRaa3bS8vV+yRGsdPoiUAKcD0n43wOl0bp3A/I7gAsUc+6lS9QtbAOGRGtOXwQu45MlxBFSjLgeEqGBChcpun+mUD8G6kcDzJIkJIMKNyJzxSdobAwJNLXDxq/SEYmztLaOjTaLXYcCBcAkWrbv48/8gOP5AS3bfgQmAQX//FGOQCoL41YGLPkgS1saoJXW1LTelAAsGkXAXFKHPuX8G7XUlcHxAjiicBxPQF0Z1L9WS/vP24BFwCDAnG47SrcnpJpjrha/G6j20gANiG+npf15M8v2kK4TTZ6kgfJbB8tvyJdSV782JKWk4HKh1FYsqURqzeupQHsGpq4NmLAKxq6AyWt9Dv3lA9CWWtHpZCt7D1NgIDCFlq3dr2A6MKi3PHA1soGUuE1qbnO09EPT7l+yyo+vpiOzycwCW2VB9+QVqjPbNbNGM9ulghlrlBhtKrzXVDB9g5ltN7OLVMx2AS+nZO8e7gdS3JP8wPR6uafaixktmvACPkN1rm6BmbUBrpn5ZoYkv0tWNUk14rFLCpoKJO0FXM/MtzmVfhQofSiQQ4DkOKEam3fHtObzjBw9reHDv+RsstTM/O7OaWaBVCkza1LR3IMqnPerSQ2VkvzTzBPEBa4UKuBcQ1yFREoSUtWBmJZsySrNOA1LVNOUGhE5ZzclZ5tJUv6jO5SYuENmwZGTisnTGh2WJzM/8kw515HipCGF0k8nPC3clNWFllEqiv9AOj02ItE1V/jI1CKVVyU7KnWWOW8O0GeK6y7doXJd4BmdYZB6hGEPFzXJotHWITUkw/XDpzzNWJdVzR/D5LrfkMlMNbNMTgkzQwRWaHZ+Vm38jKQEUkyBJClPUpG80P+8Po0n26V4LLyC+WXS3aXhO8+R2jOe2jsCoQJ53g5gsZm9D5iZobCqmmOWRNqiaj7SSJ1Qk57SA5bMmelJIHfiiy3SovG+Tjc42nXIlM5Kkx6SpIykWJja5UjRuaT3gKGS1gGBmQVhdGCqlqvxQnXaoPuVVTWexsuXWTfnMQtPm2xHyyajBWWujtRJe45KVQcCPTvRUXHecjU0fyEzV7E8X0XxqM5IkhJXIqFLGpygbORHmxSGbC+1oDUNT76VZefBKPt1vA3sY9XWgHuWpvl4P8Be3Wx0EkimfI6eAQhIZ1+MEss8TjbBw69kmbbejyrlE1Hdj0Vz57jRHu5KQwIXSWUmh+vVHpAPnGJFJdyzNM23vwfAd917yf42kcWR8d9obh6VK7+5sAJe5XQzPPhyhvmbcyqM6W/r1pXAMKAcGNy19nfW+2SyFGhi+ScB9y3LcLQeoOpmEoh17em6t1rRvJlTjTByWYbn3gkAHxjZXxJOFDaZ3GmvDqGQg8ykDm3UncVZzRxjGlrcIR9H0pqb8R9xTQ1nNG+jK3x/T9SO2b9KJNeKkck8DhzH99cDj+i/BmAcOxbXrUYUos6tMm76HzcRfwM1V/kA2LyNcwAAAABJRU5ErkJggg=="
_PLUGIN_DEMO_MANIFEST = {
    "id": "demo-cursor",
    "name": "เมาส์พิเศษ (ตัวอย่าง)",
    "version": "1.0.0",
    "author": "Broadcast Playroom",
    "description": "ตัวอย่าง plugin: เปลี่ยนรูปเมาส์ในหน้าต่างโปรแกรมเป็นลูกศรสีชมพูมีประกาย ปิดแล้วกลับเป็นเมาส์ปกติทันที",
    "api_version": 1,
    "permissions": ["ui_cursor"],
    "cursor": "cursor.png",
    "cursor_hotspot": [2, 1],
}


def _plg_seed(self):
    """Install the bundled demo plugin once (switched OFF). Never re-created if the user deletes it."""
    if getattr(self, "_plg_seeded", False):
        return
    self._plg_seeded = True
    try:
        import base64
        with self._lock:
            state = _plg_read_state(self)
            seeded = state.setdefault("seeded", [])
            if "demo-cursor" in seeded:
                return
            d = self.plugins_dir / "demo-cursor"
            if not d.exists():
                d.mkdir(parents=True)
                with open(d / "plugin.json", "w", encoding="utf-8") as f:
                    json.dump(_PLUGIN_DEMO_MANIFEST, f, ensure_ascii=False, indent=2)
                (d / "cursor.png").write_bytes(base64.b64decode(PLUGIN_DEMO_CURSOR_B64))
                state["plugins"].setdefault("demo-cursor", {"enabled": False, "granted": [], "errors": 0})
            seeded.append("demo-cursor")
            _plg_write_state(self, state)
    except Exception:
        pass


PLUGIN_GUIDE_MD = '# คู่มือสร้าง Plugin — Broadcast Playroom 3 (Plugin API v1)\n\n> เอกสารนี้เขียนให้ **AI อ่านแล้วสร้าง plugin ให้ผู้ใช้ได้เลย** (และคนอ่านเองก็ได้)\n> ผู้ใช้: ส่งทั้งไฟล์นี้ให้ AI พร้อมบอกว่าอยากได้ plugin อะไร แล้ววางโฟลเดอร์ที่ AI สร้างลงในโฟลเดอร์ plugins ของโปรแกรม\n> AI: ทำตามกติกาในเอกสารนี้อย่างเคร่งครัด อย่าเดา API ที่ไม่ได้เขียนไว้ที่นี่ — ถ้าไม่มีในเอกสาร แปลว่า **ยังทำไม่ได้**\n\nAPI เวอร์ชัน 1 **ถูกล็อก** หลังจากนี้โปรแกรมจะไม่เปลี่ยนความหมายของสิ่งที่เขียนไว้ที่นี่ plugin ที่เขียนตามเอกสารนี้จะยังใช้ได้หลังอัปเดตโปรแกรม (ถ้าจะเพิ่มความสามารถ จะเพิ่มเป็น API เวอร์ชันใหม่ ไม่แก้ของเดิม)\n\n---\n\n## 1. Plugin ทำอะไรได้ / ทำอะไรไม่ได้\n\n**ทำได้ (เฟสนี้ รองรับ JavaScript ล้วนเท่านั้น):**\n\n1. **Widget** — หน้า HTML ที่แสดงผลบนจอสตรีม (ใส่ใน OBS เป็น Browser Source) โดยรับข้อมูลสดจากโปรแกรม (แชท, ASK/โหวต, ชิงโชค, สุ่ม) แบบอ่านอย่างเดียว\n2. **เมาส์พิเศษ** — เปลี่ยนรูปเมาส์ (cursor) ในหน้าต่างโปรแกรมด้วยรูป PNG\n\n**ทำไม่ได้ (อย่าพยายามเขียน):**\n\n- เรียกอินเทอร์เน็ต/API ภายนอก (ถูกบล็อกโดย sandbox) — ยังไม่รองรับในเวอร์ชันนี้\n- Python / ไฟล์ `main.py` / โค้ดที่รันนอก sandbox\n- สั่งโปรแกรมทำอะไร (ส่งข้อความ, อ่านออกเสียง, ควบคุม overlay, เขียนไฟล์) — ทุกอย่างเป็น **อ่านอย่างเดียว**\n- แก้ไข ซ่อน หรือลบ **เครดิตผู้พัฒนา** และ **ปุ่ม/เนื้อหา "สนับสนุนการพัฒนาโปรแกรม"** — plugin เข้าถึงหน้าหลักของโปรแกรมไม่ได้อยู่แล้ว และห้ามขอสิทธิ์เหล่านี้\n- เข้าถึงหน้าหลักของโปรแกรม (DOM, localStorage, cookie) — plugin รันในกล่องแยก (sandbox)\n\n---\n\n## 2. ตำแหน่งและโครงสร้างโฟลเดอร์\n\nPlugin 1 ตัว = 1 โฟลเดอร์ ใน `<โฟลเดอร์ข้อมูลโปรแกรม>/plugins/` (ผู้ใช้กดปุ่ม **"เปิดโฟลเดอร์ plugins"** ในหน้า ตั้งค่า > ปลั๊กอิน เพื่อเปิดโฟลเดอร์นี้) การอัปเดตโปรแกรมไม่แตะโฟลเดอร์นี้\n\n```text\nplugins/\n└── my-plugin/            ← ชื่อโฟลเดอร์ = id (ดูกฎข้อ 3)\n    ├── plugin.json       ← จำเป็น\n    ├── widget.html       ← ถ้าเป็น widget (ไฟล์เดียวจบ ดูข้อ 5)\n    └── cursor.png        ← ถ้าเป็นเมาส์พิเศษ\n```\n\nชื่อโฟลเดอร์ที่ขึ้นต้นด้วย `_` หรือ `.` จะถูกข้าม\n\n---\n\n## 3. `plugin.json` (ต้องมี)\n\n```json\n{\n  "id": "my-plugin",\n  "name": "ชื่อที่แสดงในหน้าตั้งค่า",\n  "version": "1.0.0",\n  "author": "ชื่อผู้สร้าง",\n  "description": "อธิบายสั้นๆ ว่าทำอะไร",\n  "api_version": 1,\n  "permissions": ["chat_read"],\n  "widget": "widget.html"\n}\n```\n\n| ฟิลด์ | กฎ |\n|---|---|\n| `id` | **ต้องเท่ากับชื่อโฟลเดอร์เป๊ะ** ใช้ได้เฉพาะ `a-z 0-9 _ -` ยาว 2–49 ตัว ขึ้นต้นด้วย a-z หรือ 0-9 |\n| `api_version` | ต้องเป็นตัวเลข `1` (ไม่ใช่ข้อความ) ไม่งั้นโปรแกรมจะไม่รองรับ |\n| `name`, `version`, `author`, `description` | ข้อความ แสดงในหน้าตั้งค่า (ไม่บังคับแต่ควรมี) |\n| `permissions` | list ของสิทธิ์จากตารางข้อ 4 เท่านั้น ใส่สิทธิ์ที่ไม่รู้จัก = plugin ใช้งานไม่ได้ |\n| `widget` | ชื่อไฟล์ `.html` ในโฟลเดอร์หลักของ plugin (ห้ามมี `/` `\\` หรือ `..`) |\n| `cursor` | ชื่อไฟล์ `.png` สำหรับเมาส์พิเศษ (ดูข้อ 6) |\n| `cursor_hotspot` | `[x, y]` จุดที่ใช้คลิกบนรูปเมาส์ ค่าเริ่มต้น `[0, 0]` |\n\nต้องมี **อย่างน้อยหนึ่งอย่าง** ระหว่าง `widget` กับ `cursor`\n\n## 4. สิทธิ์ (permissions) ที่มีในเวอร์ชัน 1\n\nผู้ใช้จะเห็นสิทธิ์ที่ plugin ขอ และต้องกดอนุมัติก่อนเปิด **ขอเท่าที่จำเป็นเท่านั้น** ถ้าแก้ `permissions` ทีหลัง ผู้ใช้ต้องอนุมัติใหม่\n\n| สิทธิ์ | ให้อะไร |\n|---|---|\n| `chat_read` | รับ event `chat_message` (ข้อความแชทสด) |\n| `events_read` | รับ event `chat_clear`, `chat_delete`, `ask_update`, `giveaway_update`, `randomizer_spin` |\n| `ui_cursor` | ใช้ `cursor` เปลี่ยนรูปเมาส์ในหน้าต่างโปรแกรม (ใช้ได้แค่รูป PNG) |\n\nห้ามขอสิทธิ์อื่นเด็ดขาด โดยเฉพาะที่เกี่ยวกับ `creator_support`, `support_modal`, `donate_qr`, `promptpay_qr`, `footer_creator_links`, `about_author` — plugin ที่ขอจะถูกปฏิเสธ\n\n---\n\n## 5. Widget — เขียนอย่างไร\n\nผู้ใช้ก๊อปลิงก์ `http://127.0.0.1:<พอร์ต>/plugins/host/<id>` จากหน้าตั้งค่า ไปใส่เป็น **Browser Source** ใน OBS (ตั้งความกว้าง/สูงเองใน OBS) หน้า widget ต้องเปิดอยู่ได้ทั้งตอนใน OBS และเบราว์เซอร์\n\n### กฎเหล็กของ widget (เพราะ sandbox)\n\n1. **ไฟล์เดียวจบ** — HTML + CSS + JavaScript ต้องอยู่ในไฟล์ `widget.html` ไฟล์เดียว ใช้ `<style>` และ `<script>` แบบ **inline** เท่านั้น\n   (ไฟล์ `.js` / `.css` แยก, `<script src>`, `<link rel=stylesheet>` จะถูกบล็อก)\n2. **รูป/ฟอนต์/เสียง ต้องฝังเป็น `data:` URI** (เช่น `data:image/png;base64,...`) — โหลดจากอินเทอร์เน็ตหรือไฟล์ข้างๆ ไม่ได้ ใช้ SVG แบบ inline หรือ emoji/CSS ได้\n3. **ห้ามเรียกเครือข่าย** — `fetch`, `XMLHttpRequest`, `WebSocket`, `<img src="http...">` ถูกบล็อกทั้งหมด\n4. **พื้นหลังต้องโปร่งใส** — ใส่ `html,body{background:transparent;margin:0}` เพื่อให้ซ้อนบนภาพสตรีมได้\n5. ห้ามใช้ `localStorage`/`sessionStorage`/cookie (ใช้ไม่ได้ใน sandbox) เก็บสถานะในตัวแปร JavaScript\n6. ห้ามใช้ `alert`/`confirm`/`prompt`/`window.open`/`<form>` submit\n7. ประหยัดทรัพยากร: อย่าทำ animation วนไม่หยุดที่หนัก GPU (หลีกเลี่ยง `backdrop-filter: blur`, ภาพเคลื่อนไหวต่อเนื่องที่ไม่จำเป็น) เมื่อไม่มีอะไรเปลี่ยนให้หยุดนิ่ง\n\n### SDK — `BP3Plugin` (โปรแกรมฉีดให้เองในหน้า widget ไม่ต้อง import)\n\n```js\nBP3Plugin.apiVersion;          // 1\nBP3Plugin.app;                 // ข้อมูลโปรแกรม เช่น { version: "3.61" } (มีค่าหลัง event \'init\')\nBP3Plugin.on(eventName, fn);   // ลงทะเบียนรับ event; fn(data)\n```\n\nชื่อ event ที่รับได้ (สิทธิ์ที่ต้องมีอยู่ในวงเล็บ):\n\n| event | ความหมาย | สิทธิ์ |\n|---|---|---|\n| `init` | widget เริ่มทำงาน ได้ `{ plugin:{id,permissions}, app:{version}, api_version }` | — |\n| `chat_message` | มีข้อความแชทใหม่ | `chat_read` |\n| `chat_clear` | ล้างแชท | `events_read` |\n| `chat_delete` | ลบข้อความหนึ่งข้อความ (`data.id`) | `events_read` |\n| `ask_update` | สถานะ ASK/โหวตเปลี่ยน | `events_read` |\n| `giveaway_update` | สถานะชิงโชคเปลี่ยน | `events_read` |\n| `randomizer_spin` | มีการสุ่ม | `events_read` |\n\n### ข้อมูล (payload) ที่ส่งมา\n\n- `chat_message` — ฟิลด์ที่ใช้ได้: `id` (ตัวเลข), `username` (ชื่อคนส่ง), `text` (ข้อความ; อาจมี `raw_text` เป็นข้อความดิบ), `platform` (ชื่อแพลตฟอร์ม เช่น twitch, youtube, kick, tiktok, mylive, soop) ฟิลด์อื่นอาจมีเพิ่มได้\n- event อื่น ๆ — เป็นข้อมูลสถานะภายในของโปรแกรม โครงสร้างอาจมีฟิลด์เพิ่ม **ให้อ่านเฉพาะฟิลด์ที่ต้องใช้ และเผื่อกรณีเป็น `undefined` เสมอ** (ใช้ `d && d.field`) อย่าสมมติว่ามีฟิลด์ที่ไม่ได้ระบุ\n- widget ได้รับเฉพาะ event ที่เกิดหลังจาก widget เปิดแล้ว (ไม่มีการย้อนส่งแชทเก่าให้) และแสดงข้อความจากผู้ชมที่ไม่น่าเชื่อถือ — **ห้ามใส่ข้อความแชทเข้า `innerHTML`** ให้ใช้ `textContent` เสมอ (กัน XSS)\n\n### ตัวอย่าง widget ครบ — แสดงแชทล่าสุด 5 ข้อความ\n\n`plugin.json`\n\n```json\n{\n  "id": "recent-chat",\n  "name": "แชทล่าสุด 5 ข้อความ",\n  "version": "1.0.0",\n  "author": "ตัวอย่าง",\n  "description": "แสดงข้อความแชทล่าสุดบนจอสตรีม",\n  "api_version": 1,\n  "permissions": ["chat_read", "events_read"],\n  "widget": "widget.html"\n}\n```\n\n`widget.html`\n\n```html\n<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n<style>\n  html, body { margin: 0; background: transparent; }\n  body { font: 600 26px system-ui, sans-serif; color: #fff; text-shadow: 0 2px 6px #000; padding: 12px; }\n  .row { margin: 4px 0; }\n  .who { color: #ffd54f; }\n</style>\n</head>\n<body>\n<div id="list"></div>\n<script>\n  var list = document.getElementById(\'list\');\n  function add(d) {\n    var row = document.createElement(\'div\');\n    row.className = \'row\';\n    var who = document.createElement(\'span\');\n    who.className = \'who\';\n    who.textContent = ((d && d.username) || \'ไม่ระบุชื่อ\') + \': \';\n    var msg = document.createElement(\'span\');\n    msg.textContent = (d && (d.text || d.raw_text)) || \'\';\n    row.appendChild(who); row.appendChild(msg);\n    list.appendChild(row);\n    while (list.children.length > 5) list.removeChild(list.firstChild);\n  }\n  BP3Plugin.on(\'chat_message\', add);\n  BP3Plugin.on(\'chat_clear\', function () { list.textContent = \'\'; });\n</script>\n</body>\n</html>\n```\n\n---\n\n## 6. เมาส์พิเศษ (cursor)\n\n```json\n{\n  "id": "my-cursor",\n  "name": "เมาส์ของฉัน",\n  "version": "1.0.0",\n  "author": "ชื่อผู้สร้าง",\n  "description": "เปลี่ยนรูปเมาส์ในโปรแกรม",\n  "api_version": 1,\n  "permissions": ["ui_cursor"],\n  "cursor": "cursor.png",\n  "cursor_hotspot": [2, 1]\n}\n```\n\n- ไฟล์ต้องเป็น **PNG จริง** ขนาด **ไม่เกิน 64×64 พิกเซล** และ **ไม่เกิน 32 KB** (แนะนำ 32×32) พื้นหลังโปร่งใส\n- ถ้าไฟล์ไม่ผ่านเงื่อนไข plugin จะแสดงว่า "ใช้งานไม่ได้" พร้อมเหตุผล\n- `cursor_hotspot` คือพิกัดจุดคลิกในรูป (ปลายลูกศร) นับจากมุมซ้ายบน\n- ถ้าเปิดหลายตัวพร้อมกัน ใช้ตัวแรก (เรียงตามชื่อโฟลเดอร์) การเปลี่ยนมีผลหลังรีเฟรช/เปิดหน้าต่างใหม่ ปิด plugin แล้วกลับเป็นเมาส์ปกติ\n- plugin เมาส์ไม่มีโค้ด — ส่งแค่รูป โปรแกรมเป็นคนเปลี่ยนให้เอง\n\n---\n\n## 7. สถานะและการจัดการ (ผู้ใช้เห็นในหน้า ตั้งค่า > ปลั๊กอิน)\n\n- plugin ที่เพิ่งวางลงโฟลเดอร์จะ **ปิดอยู่เสมอ** จนกว่าผู้ใช้จะกดเปิดและอนุมัติสิทธิ์ (หลังวางต้องกด "โหลดใหม่")\n- ถ้า widget เกิด error (`throw` ที่ไม่ได้จับ) ซ้ำ **5 ครั้ง** โปรแกรมจะปิด plugin นั้นให้อัตโนมัติ — จับ error ใน handler ของตัวเองด้วย `try/catch`\n- **Safe Mode** ปิด plugin ทุกตัวชั่วคราว (ใช้ตอนสงสัยว่า plugin ทำให้มีปัญหา)\n- ปิดหรือลบ plugin แล้วโปรแกรมทำงานเหมือนเดิม 100%\n\n## 8. Checklist ก่อนส่งงานให้ผู้ใช้ (AI ตรวจเองทุกข้อ)\n\n- [ ] `id` ใน plugin.json = ชื่อโฟลเดอร์ ใช้เฉพาะ `a-z 0-9 _ -`\n- [ ] `api_version` เป็นตัวเลข `1`\n- [ ] `permissions` มีเฉพาะ `chat_read`, `events_read`, `ui_cursor` และขอเท่าที่ใช้จริง\n- [ ] `widget` เป็นชื่อไฟล์ .html ในโฟลเดอร์หลัก และไฟล์มีอยู่จริง (หรือมี `cursor` ที่เป็น PNG ถูกเงื่อนไข)\n- [ ] widget เป็นไฟล์เดียว ไม่มี `<script src>` / `<link>` / `fetch` / รูปจากภายนอก\n- [ ] พื้นหลังโปร่งใส ไม่มีการใช้ localStorage / alert\n- [ ] ข้อความจากแชทใส่ผ่าน `textContent` เท่านั้น\n- [ ] อ่านฟิลด์ของ event แบบเผื่อ `undefined`\n- [ ] ไม่แตะ/ไม่อ้างถึงเครดิตผู้พัฒนาหรือปุ่มสนับสนุนการพัฒนาโปรแกรม\n\n## 9. ข้อความสำหรับผู้ใช้ส่งให้ AI (ก๊อปไปใช้ได้เลย)\n\n> ฉันอยากได้ plugin สำหรับ Broadcast Playroom 3: **[อธิบายสิ่งที่อยากได้]**\n> ให้อ่านคู่มือที่แนบมาแล้วสร้างโฟลเดอร์ plugin ให้ครบ (plugin.json + ไฟล์ที่จำเป็น) ตามกติกาในคู่มือ\n> ใช้ได้เฉพาะ API ที่คู่มือเขียนไว้ ถ้าสิ่งที่ฉันขอทำไม่ได้ในเวอร์ชันนี้ ให้บอกตรงๆ และเสนอสิ่งที่ใกล้เคียงที่ทำได้\n> พอเสร็จ ให้ตรวจตาม Checklist ท้ายคู่มือ แล้วบอกวิธีวางโฟลเดอร์และวิธีทดสอบ\n'


def _plg_find(self, pid):
    for it in _plg_scan(self):
        if it["id"] == pid:
            return it
    return None


def _plg_origin_ok(headers):
    """Block cross-site POSTs to the loopback server."""
    try:
        if str(headers.get("X-BP3-Plugin", "")) != "1":
            return False
        origin = headers.get("Origin")
        if origin:
            host = headers.get("Host", "")
            if origin.split("://", 1)[-1] != host:
                return False
        return True
    except Exception:
        return False


def _plg_json(obj, status=200):
    return status, {"Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store"}, json.dumps(obj, ensure_ascii=False).encode("utf-8")


def _plg_html(html, status=200, extra=None):
    h = {"Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store"}
    if extra:
        h.update(extra)
    return status, h, html.encode("utf-8")


def _plg_handle_http(self, method, path, query="", body=None, headers=None):
    """Return (status, headers, bytes) when the request belongs to the plugin
    system, otherwise None. Never raises."""
    try:
        if not (path == "/plugins" or path.startswith("/plugins/") or path == "/api/plugins" or path.startswith("/api/plugins/")):
            return None
        if not self.plugins_dir:
            return None
        headers = headers or {}
        if method == "GET":
            if path == "/plugins":
                return _plg_html(_PLG_MANAGER_HTML)
            if path == "/api/plugins":
                state = _plg_read_state(self)
                return _plg_json({"plugins": _plg_scan(self), "api_version": PLUGIN_API_VERSION,
                                  "safe_mode": bool(state.get("safe_mode")),
                                  "permissions": PLUGIN_PERMISSIONS_V1})
            if path == "/api/plugins/ui":
                return _plg_json(_plg_ui(self))
            if path == "/plugins/docs":
                h = {"Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store"}
                if "download=1" in (query or ""):
                    h["Content-Disposition"] = 'attachment; filename="BP3_Plugin_Guide.md"'
                return 200, h, PLUGIN_GUIDE_MD.encode("utf-8")
            m = _re.match(r"^/plugins/host/([^/]+)$", path)
            if m:
                it = _plg_find(self, _unquote(m.group(1)))
                if not it or it["status"] != "enabled" or not it["widget"]:
                    return _plg_html("<!doctype html><meta charset=utf-8><body style='background:transparent'>", 404)
                page = (_PLG_HOST_HTML.replace("__PID__", json.dumps(it["id"]))
                        .replace("__PERMS__", json.dumps(it["permissions"]))
                        .replace("__WIDGET__", json.dumps(it["widget"])))
                return _plg_html(page)
            m = _re.match(r"^/plugins/file/([^/]+)/(.+)$", path)
            if m:
                return _plg_serve_file(self, _unquote(m.group(1)), _unquote(m.group(2)))
            return _plg_json({"error": "not found"}, 404)
        if method == "POST":
            if not _plg_origin_ok(headers):
                return _plg_json({"ok": False, "error": "forbidden"}, 403)
            try:
                data = json.loads((body or b"{}").decode("utf-8") or "{}")
            except Exception:
                return _plg_json({"ok": False, "error": "bad json"}, 400)
            if not isinstance(data, dict):
                return _plg_json({"ok": False, "error": "bad json"}, 400)
            with self._lock:
                state = _plg_read_state(self)
                if path == "/api/plugins/enable":
                    it = _plg_find(self, str(data.get("id", "")))
                    if not it or it["status"] in ("invalid", "unsupported"):
                        return _plg_json({"ok": False, "error": "plugin ใช้งานไม่ได้"}, 400)
                    if data.get("enabled"):
                        if sorted(data.get("granted") or []) != sorted(it["permissions"]):
                            return _plg_json({"ok": False, "error": "ต้องอนุมัติสิทธิ์ให้ครบ"}, 400)
                        state["plugins"][it["id"]] = {"enabled": True, "granted": it["permissions"], "errors": 0}
                    else:
                        state["plugins"][it["id"]] = {"enabled": False, "granted": [], "errors": 0}
                    try:
                        _plg_write_state(self, state)
                    except Exception as e:
                        return _plg_json({"ok": False, "error": "บันทึกสถานะไม่ได้ (%s) โฟลเดอร์: %s" % (e, self.plugins_dir)}, 500)
                    return _plg_json({"ok": True})
                if path == "/api/plugins/safe-mode":
                    state["safe_mode"] = bool(data.get("on"))
                    _plg_write_state(self, state)
                    return _plg_json({"ok": True})
                if path == "/api/plugins/report":
                    pid = str(data.get("id", ""))
                    ps = state["plugins"].get(pid)
                    if not ps or not ps.get("enabled"):
                        return _plg_json({"ok": True})
                    ps["errors"] = int(ps.get("errors", 0)) + 1
                    ps["last_error"] = str(data.get("message", ""))[:300]
                    if ps["errors"] >= _PLUGIN_MAX_ERRORS:
                        ps["enabled"] = False
                        ps["granted"] = []
                        ps["disabled_reason"] = "ปิดอัตโนมัติ: error ซ้ำ %d ครั้ง (%s)" % (ps["errors"], ps["last_error"][:80])
                    _plg_write_state(self, state)
                    return _plg_json({"ok": True})
            if path == "/api/plugins/open-folder":
                try:
                    if hasattr(os, "startfile"):
                        os.startfile(str(self.plugins_dir))  # Windows only
                        return _plg_json({"ok": True})
                except Exception:
                    pass
                return _plg_json({"ok": False, "error": "เปิดโฟลเดอร์ไม่ได้", "path": str(self.plugins_dir)})
            return _plg_json({"error": "not found"}, 404)
        return None
    except Exception as e:  # never let the plugin layer break a core request
        try:
            logger.warning("[PluginManager] http error: %s", e)
        except Exception:
            pass
        return None


def _plg_serve_file(self, pid, rel):
    it = _plg_find(self, pid)
    if not it or it["status"] != "enabled":
        return _plg_json({"error": "not available"}, 404)
    base = (self.plugins_dir / pid).resolve()
    target = (base / rel).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        return _plg_json({"error": "not found"}, 404)
    if not target.is_file() or target.suffix.lower() not in _PLUGIN_FILE_EXT or target.name.startswith("."):
        return _plg_json({"error": "not found"}, 404)
    data = target.read_bytes()
    ctype = _mimetypes.guess_type(str(target))[0] or "application/octet-stream"
    headers = {
        "Content-Type": ctype + ("; charset=utf-8" if ctype.startswith("text/") or ctype.endswith("javascript") or ctype.endswith("json") else ""),
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
        # sandbox WITHOUT allow-same-origin => unique origin, cannot touch the app,
        # its cookies/localStorage or same-origin APIs. connect-src 'none' => no network.
        "Content-Security-Policy": (
            "sandbox allow-scripts; default-src 'none'; script-src 'unsafe-inline'; "
            "style-src 'unsafe-inline'; img-src data: blob:; media-src data: blob:; "
            "font-src data:; connect-src 'none'; frame-src 'none'; form-action 'none'"
        ),
    }
    if target.name == it["widget"]:
        text = data.decode("utf-8", errors="replace")
        idx = text.lower().find("</head>")
        text = (text[:idx] + _PLUGIN_SDK + text[idx:]) if idx >= 0 else (_PLUGIN_SDK + text)
        data = text.encode("utf-8")
    return 200, headers, data


_PLG_HOST_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>plugin host</title>
<style>html,body{margin:0;height:100%;background:transparent;overflow:hidden}iframe{border:0;width:100%;height:100%;background:transparent}</style></head>
<body><iframe id="f" sandbox="allow-scripts" allow=""></iframe>
<script>
(function(){
  var PID=__PID__, PERMS=__PERMS__, W=__WIDGET__;
  var EV=%EVMAP%;
  var f=document.getElementById('f'), appInfo={};
  f.src='/plugins/file/'+encodeURIComponent(PID)+'/'+encodeURIComponent(W);
  function post(m){try{f.contentWindow.postMessage(m,'*')}catch(e){}}
  function report(msg){try{fetch('/api/plugins/report',{method:'POST',headers:{'Content-Type':'application/json','X-BP3-Plugin':'1'},body:JSON.stringify({id:PID,message:msg})})}catch(e){}}
  window.addEventListener('message',function(e){
    if(e.source!==f.contentWindow)return;var m=e.data;if(!m||m.v!==1)return;
    if(m.type==='ready')post({v:1,type:'init',app:appInfo,plugin:{id:PID,permissions:PERMS},api_version:1});
    else if(m.type==='error')report(String(m.message||'').slice(0,300));
  });
  fetch('/api/version',{cache:'no-store'}).then(function(r){return r.json()}).then(function(v){appInfo={version:v.version}}).catch(function(){});
  var cursor=null,epoch=null;
  function poll(){
    var q=cursor===null?'':'?after='+cursor+'&epoch='+encodeURIComponent(epoch||'');
    fetch('/api/overlay/events'+q,{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(d){
      epoch=d.epoch;cursor=d.cursor;
      (d.events||[]).forEach(function(it){
        if(d.reset)return;
        var pub=EV[it.event];if(!pub||PERMS.indexOf(pub[1])<0)return;
        post({v:1,type:'event',name:pub[0],data:it.payload});
      });
    }).catch(function(){}).then(function(){setTimeout(poll,300)});
  }
  poll();
})();
</script></body></html>""".replace("%EVMAP%", json.dumps({v[0]: [k, v[1]] for k, v in PLUGIN_EVENTS_V1.items()}))

_PLG_MANAGER_HTML = """<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ปลั๊กอิน — Broadcast Playroom 3</title>
<style>
:root{color-scheme:dark;--bg:#14161a;--card:#1d2026;--line:#2c313a;--tx:#e8eaed;--mut:#9aa3af;--ok:#3ecf8e;--warn:#f5a524;--bad:#f0616d;--acc:#6aa7ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.5 system-ui,'Segoe UI',Tahoma,sans-serif;padding:20px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);margin:0 0 16px}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
button{background:var(--card);color:var(--tx);border:1px solid var(--line);border-radius:8px;padding:7px 12px;font:inherit;cursor:pointer}button:hover{border-color:var(--acc)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:10px}
.row{display:flex;gap:12px;align-items:flex-start;justify-content:space-between}.nm{font-weight:600}.meta{color:var(--mut);font-size:12px}
.tag{display:inline-block;font-size:11px;padding:1px 8px;border-radius:99px;border:1px solid var(--line);margin-left:6px}
.t-enabled{color:var(--ok);border-color:var(--ok)}.t-disabled{color:var(--mut)}.t-bad{color:var(--bad);border-color:var(--bad)}.t-warn{color:var(--warn);border-color:var(--warn)}
.sw{position:relative;width:44px;height:24px;flex:none}.sw input{opacity:0;width:100%;height:100%;margin:0;position:absolute;cursor:pointer;z-index:1}
.sw i{position:absolute;inset:0;background:#3a404a;border-radius:99px;transition:.15s}.sw i:after{content:'';position:absolute;left:3px;top:3px;width:18px;height:18px;background:#fff;border-radius:50%;transition:.15s}
.sw input:checked+i{background:var(--ok)}.sw input:checked+i:after{left:23px}.sw input:disabled{cursor:not-allowed}.sw input:disabled+i{opacity:.4}
code{background:#0e1013;padding:2px 6px;border-radius:5px;font-size:12px;word-break:break-all}
.empty{color:var(--mut);text-align:center;padding:30px}.perm{margin:6px 0 0;padding-left:18px;color:var(--mut);font-size:12px}
#modal{position:fixed;inset:0;background:#000a;display:none;align-items:center;justify-content:center;padding:16px}#modal .box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;max-width:440px;width:100%}
</style></head><body>
<h1>ปลั๊กอิน</h1>
<p class="sub">ปลั๊กอินทำงานในกล่องแยก (sandbox) แตะระบบหลักไม่ได้ และอ่านข้อมูลได้เฉพาะสิทธิ์ที่คุณอนุมัติ — ปิดปลั๊กอินแล้วโปรแกรมทำงานเหมือนเดิม</p>
<div class="bar"><button id="refresh">โหลดใหม่</button><button id="folder">เปิดโฟลเดอร์ plugins</button>
<label><input type="checkbox" id="safe"> Safe Mode (ปิดปลั๊กอินทั้งหมดชั่วคราว)</label></div>
<div id="list"></div>
<div id="modal"><div class="box"><div id="mt" style="font-weight:600;margin-bottom:6px"></div><div id="mb" class="meta"></div><ul id="mp" class="perm"></ul>
<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:14px"><button id="mno">ยกเลิก</button><button id="myes" style="border-color:var(--ok)">อนุมัติและเปิด</button></div></div></div>
<script>
var H={'Content-Type':'application/json','X-BP3-Plugin':'1'},PERMS={},cur=[];
function $(i){return document.getElementById(i)}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var LBL={enabled:['เปิดอยู่','t-enabled'],disabled:['ปิดอยู่','t-disabled'],needs_approval:['ต้องอนุมัติใหม่','t-warn'],safe_mode:['ถูกปิดโดย Safe Mode','t-warn'],unsupported:['API ไม่รองรับ','t-bad'],invalid:['ใช้งานไม่ได้','t-bad']};
function post(p,b){return fetch(p,{method:'POST',headers:H,body:JSON.stringify(b)}).then(function(r){return r.json()})}
function load(){fetch('/api/plugins',{cache:'no-store'}).then(function(r){return r.json()}).then(function(d){PERMS=d.permissions||{};cur=d.plugins||[];$('safe').checked=!!d.safe_mode;render()}).catch(function(){$('list').innerHTML='<div class="empty">โหลดรายการไม่ได้</div>'})}
function render(){
  if(!cur.length){$('list').innerHTML='<div class="empty">ยังไม่มีปลั๊กอิน — วางโฟลเดอร์ปลั๊กอินลงใน plugins แล้วกด “โหลดใหม่”</div>';return}
  $('list').innerHTML=cur.map(function(p,i){
    var l=LBL[p.status]||['?','t-bad'],can=p.status!=='invalid'&&p.status!=='unsupported';
    var url=location.origin+'/plugins/host/'+encodeURIComponent(p.id);
    return '<div class="card"><div class="row"><div><span class="nm">'+esc(p.name)+'</span><span class="tag '+l[1]+'">'+l[0]+'</span>'+
    '<div class="meta">'+esc(p.version?('v'+p.version):'')+(p.author?' · '+esc(p.author):'')+'</div>'+
    (p.description?'<div>'+esc(p.description)+'</div>':'')+
    (p.reason?'<div class="meta" style="color:var(--warn)">'+esc(p.reason)+'</div>':'')+
    (p.permissions.length?'<ul class="perm">'+p.permissions.map(function(k){return '<li>'+esc(PERMS[k]||k)+'</li>'}).join('')+'</ul>':'')+
    (p.status==='enabled'&&p.widget?'<div class="meta" style="margin-top:6px">ลิงก์สำหรับ OBS (Browser Source): <code>'+esc(url)+'</code> <button data-c="'+i+'">คัดลอก</button></div>':'')+
    '</div><label class="sw"><input type="checkbox" data-i="'+i+'" '+(p.enabled?'checked':'')+(can?'':' disabled')+'><i></i></label></div></div>'}).join('');
  [].forEach.call(document.querySelectorAll('input[data-i]'),function(el){el.onchange=function(){toggle(+el.dataset.i,el)}});
  [].forEach.call(document.querySelectorAll('button[data-c]'),function(b){b.onclick=function(){var p=cur[+b.dataset.c];navigator.clipboard&&navigator.clipboard.writeText(location.origin+'/plugins/host/'+encodeURIComponent(p.id))}});
}
function toggle(i,el){
  var p=cur[i];
  if(!el.checked){post('/api/plugins/enable',{id:p.id,enabled:false}).then(load);return}
  el.checked=false;
  $('mt').textContent='เปิด “'+p.name+'” ?';$('mb').textContent=p.permissions.length?'ปลั๊กอินนี้ขอสิทธิ์:':'ปลั๊กอินนี้ไม่ขอสิทธิ์ใดเลย (แสดงผลอย่างเดียว)';
  $('mp').innerHTML=p.permissions.map(function(k){return '<li>'+esc(PERMS[k]||k)+'</li>'}).join('');
  $('modal').style.display='flex';
  $('mno').onclick=function(){$('modal').style.display='none'};
  $('myes').onclick=function(){$('modal').style.display='none';post('/api/plugins/enable',{id:p.id,enabled:true,granted:p.permissions}).then(function(r){if(!r.ok)alert(r.error||'เปิดไม่ได้');load()})};
}
$('refresh').onclick=load;
$('folder').onclick=function(){post('/api/plugins/open-folder',{}).then(function(r){if(!r.ok)alert('เปิดเองไม่ได้ โฟลเดอร์อยู่ที่: '+(r.path||''))})};
$('safe').onchange=function(){post('/api/plugins/safe-mode',{on:$('safe').checked}).then(load)};
load();
</script></body></html>"""

PluginManager.handle_http = _plg_handle_http
