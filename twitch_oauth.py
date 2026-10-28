"""twitch_oauth.py — Twitch OAuth 2.0 flow สำหรับ login เพื่อส่งแชท + bot

Flow:
1. User กดปุ่ม "เชื่อมต่อ Twitch" → เปิดเบราว์เซอร์ไปหน้า authorize
2. User กด Authorize → Twitch redirect กลับมา http://localhost:17563/?code=xxx
3. เรารัน HTTP server ชั่วคราวรอ callback → ได้ code
4. แลก code เป็น access_token + refresh_token (POST /oauth2/token)
5. เก็บ token ใน settings → ใช้ส่งแชทผ่าน IRC

★ ใช้ stdlib (http.server + urllib) — ไม่ต้องลง dependency ใหม่
★ Token หมดอายุ ~60 วัน → เก็บ refresh_token ไว้แลกใหม่อัตโนมัติ
"""
import logging
from bot_oauth_credentials import get_client_credential
import threading
import urllib.parse
import urllib.request
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger("twitch_oauth")

# ═══ Twitch OAuth endpoints ═══
TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"

# ═══ Config ═══
REDIRECT_PORT = 17563
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
# Scopes สำหรับ: อ่านแชท + ส่งแชท + ข้อมูล user
SCOPES = ["chat:read", "chat:edit", "user:read:chat"]

# ★ Client ID ของแอป — user ต้องสมัคร Twitch Developer App เอง
#   ไป https://dev.twitch.tv/console → Register Application
#   ตั้ง OAuth Redirect URLs = http://localhost:17563
#   Category = Chat Bot / Other
DEFAULT_CLIENT_ID = get_client_credential('twitch', 'DEFAULT_CLIENT_ID')


class _CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler รอรับ OAuth callback (?code=xxx หรือ ?error=xxx)"""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # ★ ตรวจ state (กัน CSRF/login substitution) — ต้องตรงกับที่ generate ตอนเริ่ม flow
        expected_state = getattr(self.server, "oauth_state", "")
        received_state = params.get("state", [""])[0]
        if expected_state and received_state != expected_state:
            self.server.oauth_error = "state_mismatch"
            self._respond_error("state mismatch (possible CSRF)")
            return

        # ส่งผลกลับไปให้ server instance
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
            "<h1>✅ เชื่อมต่อ Twitch สำเร็จ!</h1>"
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
            f"<p>กรุณาลองอีกครั้ง</p>"
            "</body></html>"
        )
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        # ปิด log default ของ HTTP server (กวน log)
        pass


def start_oauth_flow(client_id: str = "") -> dict:
    """เริ่ม OAuth flow — เปิดเบราว์เซอร์ + รอ callback

    Args:
        client_id: Twitch Client ID (ถ้าว่าง → ใช้ DEFAULT_CLIENT_ID)

    Returns:
        dict: {
            "access_token": str,
            "refresh_token": str,
            "username": str,      # login name
            "expires_in": int,    # วินาที
        }
        หรือ None ถ้า fail / user cancel
    """
    cid = client_id or DEFAULT_CLIENT_ID
    if not cid:
        logger.error("No Client ID provided")
        return None

    # ★ สร้าง authorize URL (+ state กัน CSRF + PKCE กัน authorization code interception)
    import secrets as _secrets
    import hashlib as _hashlib
    import base64 as _b64
    oauth_state = _secrets.token_urlsafe(32)
    # PKCE: verifier สุ่ม → challenge = S256(verifier) ส่งใน URL, verifier ใช้ตอน exchange
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
        "force_verify": "true",  # บังคับขอ consent ทุกครั้ง (กัน cache บัญชีเก่า)
    }
    auth_url = f"{TWITCH_AUTH_URL}?{urllib.parse.urlencode(params)}"

    # ★ รัน HTTP server รอ callback (timeout 5 นาที)
    server = HTTPServer(("127.0.0.1", REDIRECT_PORT), _CallbackHandler)
    server.oauth_code = None
    server.oauth_error = None
    server.oauth_state = oauth_state
    server.timeout = 1  # check ทุก 1 วิ

    # ★ เปิดเบราว์เซอร์
    logger.info(f"Opening browser for Twitch OAuth: {auth_url}")
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        return None

    # ★ รอ callback (max 5 นาที)
    import time
    deadline = time.time() + 300  # 5 นาที
    while time.time() < deadline:
        server.handle_request()  # รอ 1 request (block ตาม timeout)
        if server.oauth_code or server.oauth_error:
            break

    server.server_close()

    if server.oauth_error:
        logger.error(f"OAuth error: {server.oauth_error}")
        return None
    if not server.oauth_code:
        logger.error("OAuth timeout — user did not authorize")
        return None

    # ★ แลก code เป็น token (พร้อม code_verifier ของ PKCE)
    return _exchange_code(server.oauth_code, cid, code_verifier)


def _exchange_code(code: str, client_id: str, code_verifier: str = "") -> dict:
    """แลก authorization code เป็น access_token + refresh_token

    POST https://id.twitch.tv/oauth2/token
    """
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": DEFAULT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        # ★ PKCE — ถ้า flow เริ่มด้วย code_challenge ต้องส่ง verifier ตอน exchange
        "code_verifier": code_verifier,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(TWITCH_TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.error("Token exchange failed: HTTP %s", e.code)
        return None
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return None

    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    if not access_token:
        logger.error("No access_token in response")
        return None

    # ★ ดึง username จาก validate endpoint
    username = verify_token(access_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token or "",
        "username": username or "",
        "expires_in": result.get("expires_in", 0),
    }


# ★ Client Secret — ต้องตั้งให้ตรงกับ Twitch App
#   (ถ้าไม่มี → flow จะ fail ที่ _exchange_code)
DEFAULT_CLIENT_SECRET = get_client_credential('twitch', 'DEFAULT_CLIENT_SECRET')


def verify_token(access_token: str) -> str:
    """ตรวจสอบ token → คืน username (login)

    GET https://id.twitch.tv/oauth2/validate
    Returns: login name หรือ "" ถ้า invalid
    """
    try:
        req = urllib.request.Request(TWITCH_VALIDATE_URL)
        req.add_header("Authorization", f"OAuth {access_token}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result.get("login", "")
    except Exception as e:
        logger.debug(f"verify_token failed: {e}")
        return ""


def refresh_access_token(refresh_token: str, client_id: str = "") -> dict:
    """แลก refresh_token เป็น access_token ใหม่ (เมื่อ token เก่าหมดอายุ)

    POST https://id.twitch.tv/oauth2/token (grant_type=refresh_token)
    Returns: {"access_token": ..., "refresh_token": ..., "expires_in": ...} หรือ None
    """
    cid = client_id or DEFAULT_CLIENT_ID
    if not cid or not refresh_token:
        return None

    data = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": DEFAULT_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(TWITCH_TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return {
            "access_token": result.get("access_token", ""),
            "refresh_token": result.get("refresh_token", refresh_token),
            "expires_in": result.get("expires_in", 0),
        }
    except Exception as e:
        logger.error(f"refresh_token failed: {e}")
        return None
