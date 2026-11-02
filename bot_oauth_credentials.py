"""Protected application OAuth configuration with encrypted credential storage."""
import os
import base64
from pathlib import Path

_KEY = 'bp3_secure_auth_token_key_2026'

def _decode(enc: str) -> str:
    try:
        raw = base64.b64decode(enc.encode('ascii')).decode('latin1')
        res = [chr(ord(c) ^ ord(_KEY[i % len(_KEY)])) for i, c in enumerate(raw)]
        return ''.join(res)
    except Exception:
        return ''

_PROTECTED_CREDENTIALS = {
    'twitch': {
        'DEFAULT_CLIENT_ID': 'DRNcMkcDCgMKCzQSAQEPbkcAWg8YPR0DGmoCVEdG',
        'DEFAULT_CLIENT_SECRET': 'DEdeLAQQUxsZXSwRBRdRKRZbWgwUOlINGjYKUQdM',
    },
    'kick': {
        'DEFAULT_CLIENT_ID': 'UkF+b0M1ICFBVAgmLCIqFDY+KTUjaDFdKA4=',
        'DEFAULT_CLIENT_SECRET': 'VBULPEJTVkIXXGYFQ0YOZ0YOD1Jcb1JTGzwAAwAPVxVSPhJcVhFKBmpSE0NePkZbXFNYOwpVGztUAAYPARJXaw==',
    }
}

def get_client_credential(platform, name):
    env = 'BP3_' + platform.upper() + '_' + name.removeprefix('DEFAULT_')
    if os.environ.get(env):
        return os.environ[env]
    enc_val = _PROTECTED_CREDENTIALS.get(platform, {}).get(name, '')
    if enc_val:
        return _decode(enc_val)
    return ''
