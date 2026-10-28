"""kick_oauth.py — KICK OAuth 2.1 flow สำหรับ login เพื่อส่งแชท + bot + แก้ชื่อห้อง

Flow:
1. User กดปุ่ม "เชื่อมต่อ KICK" → เปิดเบราว์เซอร์ไป id.kick.com/oauth/authorize
2. User กด Authorize → KICK redirect กลับมา http://localhost:17564/callback?code=xxx
3. เรารัน HTTP server ชั่วคราวรอ callback → ได้ code
4. แลก code เป็น access_token + refresh_token (POST id.kick.com/oauth/token + PKCE verifier)
5. ดึง user info (GET api.kick.com/public/v1/users/me) → เก็บ user_id + name
6. เก็บ token ใน settings → ใช้ส่งแชท (POST /public/v1/chat) + แก้ชื่อห้อง (PATCH /public/v1/channels)

★ KICK บังคับ OAuth 2.1: state + PKCE (S256) ต้องมีเสมอ
★ Refresh token หมุนเวียน (rotate) — ทุกครั้งที่ refresh ต้องเก็บอันใหม่ทับเสมอ
   และห้ามใช้ refresh token เก่าซ้ำ (KICK จะ revoke ทิ้ง)
★ ใช้ stdlib (http.server + urllib) เหมือน twitch_oauth — ไม่ต้องลง dependency ใหม่
"""
import logging
from bot_oauth_credentials import get_client_credential
from bot_auth import OAuthFlowError
import urllib.parse
import urllib.request
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger("kick_oauth")

# ═══ KICK OAuth endpoints (OAuth server แยกจาก API server) ═══
KICK_AUTH_URL = "https://id.kick.com/oauth/authorize"
KICK_TOKEN_URL = "https://id.kick.com/oauth/token"
KICK_USERS_ME_URL = "https://api.kick.com/public/v1/users"

# ═══ Config ═══
REDIRECT_PORT = 17564
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
# Scopes: user:read (ดูข้อมูลตัวเอง) + channel:read/write (อ่าน/แก้ชื่อห้อง)
#         + chat:write (โพสแชท)
SCOPES = ["user:read", "channel:read", "channel:write", "chat:write"]

# ★ Broadcast Playroom KICK App — สร้างที่ kick.com/settings/developer
#   (2FA ต้องเปิดก่อนถึงจะเข้า Developer tab ได้)
DEFAULT_CLIENT_ID = get_client_credential('kick', 'DEFAULT_CLIENT_ID')
DEFAULT_CLIENT_SECRET = get_client_credential('kick', 'DEFAULT_CLIENT_SECRET')


class _CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler รอรับ OAuth callback (?code=xxx หรือ ?error=xxx)"""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # ★ ตรวจ state (กัน CSRF — OAuth 2.1 บังคับ)
        expected_state = getattr(self.server, "oauth_state", "")
        received_state = params.get("state", [""])[0]
        if expected_state and received_state != expected_state:
            self.server.oauth_error = "state_mismatch"
            self._respond_error("state mismatch (possible CSRF)")
            return

        if "code" in params:
            self.server.oauth_code = params["code"][0]
            self._respond_success()
        elif "error" in params:
            self.server.oauth_error = params.get("error", ["unknown"])[0]
            self._respond_error(self.server.oauth_error)
        else:
            self._respond_error("missing code")

    def _respond_success(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = (
            "<html><body style='font-family:sans-serif;text-align:center;padding:60px;'>"
            "<h1>✅ เชื่อมต่อ KICK สำเร็จ!</h1>"
            "<p>คุณสามารถปิดหน้าต่างนี้แล้วกลับไปที่โปรแกรมได้เลย</p>"
            "<script>setTimeout(()=>window.close(),3000);</script>"
            "</body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def _respond_error(self, error):
        self.send_response(400)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = (
            f"<html><body style='font-family:sans-serif;text-align:center;padding:60px;'>"
            f"<h1>❌ เชื่อมต่อไม่สำเร็จ</h1>"
            f"<p>Error: {error}</p>"
            "</body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        pass


def start_oauth_flow(client_id: str = "", client_secret: str = "") -> dict | None:
    """เริ่ม OAuth flow — เปิดเบราว์เซอร์ + รอ callback

    Returns:
        dict: {
            "access_token": str,
            "refresh_token": str,
            "username": str,       # ชื่อบัญชี KICK
            "user_id": int,        # broadcaster_user_id (ใช้ส่งแชท type=user)
            "expires_in": int,
        }
        หรือ None ถ้า fail / user cancel
    """
    cid = client_id or DEFAULT_CLIENT_ID
    csec = client_secret or DEFAULT_CLIENT_SECRET
    if not cid or not csec:
        logger.error("No Client ID/Secret provided")
        return None

    # ★ state (CSRF) + PKCE (S256) — OAuth 2.1 บังคับทั้งคู่
    import secrets as _secrets
    import hashlib as _hashlib
    import base64 as _b64
    oauth_state = _secrets.token_urlsafe(32)
    code_verifier = _secrets.token_urlsafe(64)
    code_challenge = _b64.urlsafe_b64encode(
        _hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    params = {
        "client_id": cid,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": oauth_state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{KICK_AUTH_URL}?{urllib.parse.urlencode(params)}"

    # ★ รัน HTTP server รอ callback (timeout 5 นาที)
    try:
        server = HTTPServer(("127.0.0.1", REDIRECT_PORT), _CallbackHandler)
    except OSError as e:
        logger.error("Cannot bind OAuth callback port")
        raise OAuthFlowError("พอร์ตสำหรับเชื่อมบัญชี KICK ถูกใช้งานอยู่ กรุณาปิดหน้าต่างเชื่อมบัญชีเดิมแล้วลองใหม่")
    server.oauth_code = None
    server.oauth_error = None
    server.oauth_state = oauth_state
    server.timeout = 1

    logger.info("Opening browser for KICK OAuth")
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        server.server_close()
        return None

    import time
    deadline = time.time() + 300
    while time.time() < deadline:
        server.handle_request()
        if server.oauth_code or server.oauth_error:
            break

    server.server_close()

    if server.oauth_error:
        logger.error("KICK authorization rejected")
        raise OAuthFlowError("KICK ไม่อนุมัติการเชื่อมบัญชี กรุณาลองใหม่และตรวจสอบสิทธิ์")
    if not server.oauth_code:
        logger.error("OAuth timeout — user did not authorize")
        raise OAuthFlowError("หมดเวลารอเข้าสู่ระบบ KICK กรุณาลองเชื่อมต่อใหม่")

    return _exchange_code(server.oauth_code, cid, csec, code_verifier)


def _exchange_code(code: str, client_id: str, client_secret: str, code_verifier: str) -> dict | None:
    """แลก authorization code เป็น token

    POST https://id.kick.com/oauth/token (x-www-form-urlencoded)
    """
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(KICK_TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.error("Token exchange failed: HTTP %s", e.code)
        raise OAuthFlowError(f"KICK ไม่ยอมรับการเชื่อมบัญชี (HTTP {e.code}) กรุณาตรวจสอบการตั้งค่าแอป KICK")
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return None

    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    if not access_token:
        logger.error("No access_token in response")
        return None

    # ★ ดึง user info (user_id ใช้เป็น broadcaster_user_id ตอนส่ง type=user)
    user_info = get_user_info(access_token)
    if not user_info or not user_info.get("name"):
        raise OAuthFlowError("เชื่อม KICK แล้ว แต่ไม่สามารถอ่านข้อมูลบัญชี กรุณาตรวจสอบสิทธิ์ user:read")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token or "",
        "username": user_info.get("name", "") if user_info else "",
        "user_id": user_info.get("user_id", 0) if user_info else 0,
        "expires_in": result.get("expires_in", 0),
    }


def get_user_info(access_token: str) -> dict | None:
    """ดึงข้อมูล user ปัจจุบัน

    GET https://api.kick.com/public/v1/users/me (scope: user:read)
    Returns: {user_id, name, email} หรือ None ถ้า fail
    """
    try:
        req = urllib.request.Request(KICK_USERS_ME_URL)
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug(f"get_user_info failed: {e}")
        return None
    # ★ KICK API ห่อ response ใน "data" — เป็น dict หรือ list ก็ได้
    data = result.get("data") if isinstance(result, dict) else result
    if isinstance(data, list) and data:
        data = data[0]
    if not isinstance(data, dict):
        return None
    return {
        "user_id": data.get("user_id") or data.get("id") or 0,
        "name": data.get("name") or data.get("username") or "",
        "email": data.get("email") or "",
    }


def verify_token(access_token: str) -> str:
    """ตรวจ token → คืน username ("" ถ้า invalid)"""
    info = get_user_info(access_token)
    return info.get("name", "") if info else ""


def refresh_access_token(refresh_token: str, client_id: str = "", client_secret: str = "") -> dict | None:
    """แลก refresh_token เป็น access_token ใหม่

    ★ KICK หมุน refresh token — ต้องเก็บอันใหม่จาก response ทับเสมอ
    Returns: {"access_token", "refresh_token", "expires_in"} หรือ None
    """
    cid = client_id or DEFAULT_CLIENT_ID
    csec = client_secret or DEFAULT_CLIENT_SECRET
    if not cid or not csec or not refresh_token:
        return None

    data = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": csec,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(KICK_TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.error("KICK refresh failed: HTTP %s", e.code)
        return None
    except Exception as e:
        logger.error(f"KICK refresh failed: {e}")
        return None

    new_access = result.get("access_token", "")
    new_refresh = result.get("refresh_token", "")
    if not new_access:
        return None
    return {
        "access_token": new_access,
        # ★ ถ้า KICKไม่ส่ง refresh ใหม่ → ใช้อันเก่า (บาง server ไม่ rotate)
        "refresh_token": new_refresh or refresh_token,
        "expires_in": result.get("expires_in", 0),
    }
