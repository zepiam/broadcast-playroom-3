"""translator.py — Auto Translate (Google GTX / DeepL / deep-translator)
Broadcast Playroom 3
"""
from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from typing import Optional

_log = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_requests: int = 120, window_seconds: int = 300):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: list[float] = []
        self._rate_limited_until: float = 0

    def can_request(self) -> bool:
        now = time.time()
        if now < self._rate_limited_until:
            return False
        self._timestamps = [t for t in self._timestamps if now - t < self.window_seconds]
        if len(self._timestamps) >= self.max_requests:
            oldest = self._timestamps[0] if self._timestamps else now
            self._rate_limited_until = oldest + self.window_seconds
            return False
        self._timestamps.append(now)
        return True


class Translator:
    _rate_limiter = RateLimiter(max_requests=120, window_seconds=300)
    _cache: dict[str, tuple[str, str]] = {}  # cache_key -> (translated_text, detected_lang)

    def __init__(self, provider: str = "google", api_key: str = "", host: str = "", target_lang: str = "th", supported_langs: list = None, **kwargs):
        self.provider = provider or "google"
        self.api_key = api_key or ""
        self.host = host or ""
        self.target_lang = target_lang or "th"
        self.supported_langs = supported_langs or []

    def translate_text(self, text: str, source_lang: str = "auto") -> Optional[str]:
        """Convenience method returning only the translated text or None."""
        translated, _ = self.translate(text, source_lang)
        return translated

    def translate(self, text: str, source_lang: str = "auto") -> tuple[Optional[str], Optional[str]]:
        """Returns (translated_text, detected_source_lang) or (None, None)."""
        clean = (text or "").strip()
        if not clean or len(clean) > 500:
            return None, None

        # Ignore bot commands, symbols and triggers (!command, -voice, etc.)
        if clean.startswith(('!', '/', '-', '#', '$', '~')):
            return None, None

        # Skip text without any alphabetic letters (only digits, punctuation, emojis)
        if not any(ch.isalpha() for ch in clean):
            return None, None

        # Check if already purely Thai or punctuation/digits
        has_thai = any('\u0E00' <= ch <= '\u0E7F' for ch in clean)
        has_latin_or_cjk = any(('a' <= ch.lower() <= 'z') or ('\u4e00' <= ch <= '\u9fff') or ('\u3040' <= ch <= '\u30ff') or ('\uac00' <= ch <= '\ud7af') for ch in clean)
        
        # If text has mostly Thai characters and no foreign words, no translation needed
        if has_thai and not has_latin_or_cjk:
            return None, "th"

        cache_key = f"{self.provider}:{self.target_lang}:{clean}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self._rate_limiter.can_request():
            return None, None

        # 0. DeepL API if provider is deepl and API key is provided
        if self.provider == "deepl" and self.api_key:
            try:
                base = (self.host or "https://api-free.deepl.com").rstrip("/")
                url = f"{base}/v2/translate"
                params = urllib.parse.urlencode({
                    "auth_key": self.api_key,
                    "text": clean,
                    "target_lang": self.target_lang.upper() if self.target_lang != "th" else "TH",
                }).encode("utf-8")
                req = urllib.request.Request(url, data=params, headers={"User-Agent": "BroadcastPlayroom/3.0"})
                with urllib.request.urlopen(req, timeout=5) as res:
                    raw = res.read().decode("utf-8")
                    data = json.loads(raw)
                    trans = data.get("translations", [{}])[0].get("text", "").strip()
                    detected = (data.get("translations", [{}])[0].get("detected_source_language", "auto") or "auto").lower()
                    if trans and trans.lower() != clean.lower():
                        self._cache[cache_key] = (trans, detected)
                        return trans, detected
                    return None, detected
            except Exception as exc:
                _log.debug("DeepL translate error: %s", exc)

        try:
            # 1. Primary: Google GTX Translation API (free, reliable, built-in)
            q = urllib.parse.quote(clean)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={self.target_lang}&dt=t&q={q}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as res:
                raw = res.read().decode("utf-8")
                data = json.loads(raw)
                detected = data[2] if len(data) > 2 and isinstance(data[2], str) else "auto"
                if detected == self.target_lang:
                    self._cache[cache_key] = (clean, detected)
                    return None, detected
                
                parts = []
                if isinstance(data[0], list):
                    for segment in data[0]:
                        if segment and isinstance(segment[0], str):
                            parts.append(segment[0])
                translated = "".join(parts).strip()
                if translated and translated.lower() != clean.lower():
                    self._cache[cache_key] = (translated, detected)
                    while len(self._cache) > 2000:
                        self._cache.pop(next(iter(self._cache)), None)
                    return translated, detected
                return None, detected
        except Exception as exc:
            _log.debug("Primary GTX translate error: %s", exc)

        # 2. Fallback to deep_translator if installed
        try:
            from deep_translator import GoogleTranslator
            t = GoogleTranslator(source=source_lang, target=self.target_lang)
            res = t.translate(clean)
            if res and res.strip() and res.strip().lower() != clean.lower():
                self._cache[cache_key] = (res.strip(), "auto")
                return res.strip(), "auto"
        except Exception:
            pass

        return None, None
