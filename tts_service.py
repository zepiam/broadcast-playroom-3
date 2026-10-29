import asyncio
import io
import logging
import re
import sys
import socket
import aiohttp
from types import SimpleNamespace

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import edge_tts

logger = logging.getLogger("tts_service")

VOICES = {
    'female_th': 'th-TH-PremwadeeNeural',
    'male_th': 'th-TH-NiwatNeural',
    'female_en': 'th-TH-PremwadeeNeural',
    'male_en': 'th-TH-NiwatNeural',
    'female_ja': 'ja-JP-NanamiNeural',
    'male_ja': 'ja-JP-KeitaNeural',
    'female_ko': 'ko-KR-SunHiNeural',
    'male_ko': 'ko-KR-InJoonNeural',
    'female_zh': 'zh-CN-XiaoxiaoNeural',
    'male_zh': 'zh-CN-YunxiNeural',
    'female_zh-TW': 'zh-TW-HsiaoChenNeural',
    'male_zh-TW': 'zh-TW-YunJheNeural',
    'female_fr': 'fr-FR-DeniseNeural',
    'male_fr': 'fr-FR-HenriNeural',
}

def sanitize_text(text: str) -> str:
    """Sanitize and clean text to prevent Edge-TTS syntax errors"""
    if not text:
        return ""
    # 1. 555+ or 55555+ -> 555
    text = re.sub(r'555\++', '555', text)
    # 2. 1+1 -> 1 บวก 1
    text = re.sub(r'(?<=\d)\+(?=\d)', ' บวก ', text)
    # 3. Clean trailing special punctuation that can corrupt SSML
    text = re.sub(r'[\+\*\~\^\=\#\$\@\%\&\_\|\<\>\{\}\[\]\\]+$', '', text)
    # 4. Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()

def clean_prosody(val: str, default_unit: str = '%') -> str:
    if not val:
        return ""
    val = str(val).strip()
    num_match = re.search(r'([+-]?\s*\d+)', val)
    if not num_match:
        return ""
    num_str = num_match.group(1).replace(' ', '')
    if not num_str.startswith(('+', '-')):
        num_str = '+' + num_str
    return num_str + default_unit

def resolve_voice_for_lang(lang: str, gender: str = 'female') -> str:
    g = 'male' if str(gender).lower() in ['male', 'man', 'boy', 'niwat'] else 'female'
    if lang in ('th', 'en'):
        return VOICES[f'{g}_th']
    voice_key = f'{g}_{lang}'
    if voice_key in VOICES:
        return VOICES[voice_key]
    return VOICES[f'{g}_th']

def split_text_by_language(text: str) -> list[tuple[str, str]]:
    """
    Split text into segments by language for multilingual TTS.
    English is grouped into 'th' so it is read together with Thai using the Thai voice model.
    Other languages (ja, ko, zh, fr, etc.) form their own segments to be read by their native models.
    """
    from language_detect import _char_lang
    segments = []
    current_text = ''
    current_lang = None

    for ch in text:
        lang = _char_lang(ch)
        if lang == 'en':
            lang = 'th'

        if lang is None:
            current_text += ch
            continue

        if current_lang is None:
            current_lang = lang
            current_text += ch
        elif lang == current_lang:
            current_text += ch
        else:
            if current_text.strip():
                segments.append((current_text.strip(), current_lang or 'th'))
            current_text = ch
            current_lang = lang

    if current_text.strip():
        segments.append((current_text.strip(), current_lang or 'th'))

    return segments

def merge_audio_segments(audio_parts: list[bytes]) -> bytes:
    """
    Merge multiple MP3 audio byte chunks with trimmed trailing silence and 50ms gap.
    Falls back to direct byte concatenation if soundfile or numpy are unavailable.
    """
    if not audio_parts:
        return b""
    if len(audio_parts) == 1:
        return audio_parts[0]

    try:
        import numpy as np
        import soundfile as sf
        audios = []
        sample_rate = 24000
        for b in audio_parts:
            data, sr = sf.read(io.BytesIO(b), dtype='float32')
            if getattr(data, 'ndim', 1) > 1:
                data = data.mean(axis=1)
            sample_rate = sr
            # Trim trailing silence (threshold 0.01)
            mask = np.abs(data) >= 0.01
            indices = np.where(mask)[0]
            if len(indices) > 0:
                data = data[:indices[-1] + 1]
            audios.append(data)

        if not audios:
            return b"".join(audio_parts)

        gap = np.zeros(int(sample_rate * 0.05), dtype=np.float32)  # 50ms gap
        merged = audios[0]
        for a in audios[1:]:
            merged = np.concatenate([merged, gap, a])

        out = io.BytesIO()
        sf.write(out, merged, sample_rate, format='MP3')
        result = out.getvalue()
        if result:
            return result
    except Exception as e:
        logger.warning(f"Audio merge with soundfile failed: {e}; falling back to raw byte concat")

    return b"".join(audio_parts)

def resolve_voice(text: str, gender: str = 'female') -> tuple[str, str]:
    """
    Select voice strictly matching the specified gender and detected language.
    - If text is Thai or English: Thai voice model of chosen gender (ไทยและอังกฤษ ใช้โมเดล TTS ไทยเป็นคนอ่านสำเนียงไทย ตามแบบเวอร์ชันเดิม).
    - If other languages (Japanese, Korean, Chinese, French): voice model of that language.
    Returns (voice_name, gender_key)
    """
    g = 'male' if str(gender).lower() in ['male', 'man', 'boy', 'niwat'] else 'female'
    # Thai characters -> Thai voice model
    if re.search(r'[฀-๿]', text):
        return VOICES[f'{g}_th'], g
    try:
        from language_detect import detect_language
        lang = detect_language(text)
        # Thai and English both use Thai TTS voice model
        if lang in ('th', 'en'):
            return VOICES[f'{g}_th'], g
        voice_key = f'{g}_{lang}'
        if voice_key in VOICES:
            return VOICES[voice_key], g
    except Exception:
        pass
    # English characters or fallback -> Thai voice model
    return VOICES[f'{g}_th'], g

class TTSService:
    def __init__(self):
        self.dns_settings = None

    async def _synthesize_single(self, text: str, voice: str, rate: str = '', pitch: str = '', volume: str = '') -> bytes:
        kwargs = {}
        c_rate = clean_prosody(rate, '%')
        if c_rate and c_rate not in ['+0%', '0%', '-0%']:
            kwargs['rate'] = c_rate

        c_pitch = clean_prosody(pitch, 'Hz')
        if c_pitch and c_pitch not in ['+0Hz', '0Hz', '-0Hz']:
            kwargs['pitch'] = c_pitch

        c_vol = clean_prosody(volume, '%')
        if c_vol and c_vol not in ['+0%', '0%', '-0%']:
            kwargs['volume'] = c_vol

        # Match the legacy engine: force IPv4 and retry the selected voice.
        for attempt in range(2):
            try:
                options = {'family': socket.AF_INET}
                dns = self.dns_settings.public() if self.dns_settings else {'enabled': False}
                if dns.get('enabled'):
                    from network_dns import AppDnsResolver
                    options['resolver'] = AppDnsResolver(SimpleNamespace(dns_service=dns['service'], dns_custom=dns['custom']))
                async with aiohttp.TCPConnector(**options) as connector:
                    comm = edge_tts.Communicate(text, voice=voice, connector=connector,
                                                connect_timeout=8, receive_timeout=20, **kwargs)
                    buf = io.BytesIO()
                    async for chunk in comm.stream():
                        if chunk['type'] == 'audio':
                            buf.write(chunk['data'])
                    audio = buf.getvalue()
                    if audio:
                        return audio
            except Exception as error:
                logger.warning('TTS voice %s attempt %d failed: %s', voice, attempt + 1, error)
            if attempt == 0:
                await asyncio.sleep(0.3)
        return b''

    async def synthesize(self, text: str, gender: str = 'female', rate: str = '', pitch: str = '', volume: str = '') -> bytes:
        text = sanitize_text(text)
        if not text:
            return b""

        segments = split_text_by_language(text)
        if not segments:
            return b""

        if len(segments) == 1:
            seg_text, seg_lang = segments[0]
            voice = resolve_voice_for_lang(seg_lang, gender)
            return await self._synthesize_single(seg_text, voice, rate, pitch, volume)

        # Multilingual: synthesize each segment concurrently with its native language voice
        tasks = []
        for seg_text, seg_lang in segments:
            voice = resolve_voice_for_lang(seg_lang, gender)
            tasks.append(self._synthesize_single(seg_text, voice, rate, pitch, volume))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        audio_parts = []
        for res in results:
            if isinstance(res, bytes) and res:
                audio_parts.append(res)
            elif isinstance(res, Exception):
                logger.warning("Multilingual segment synthesis failed: %s", res)

        if not audio_parts:
            return b""
        if len(audio_parts) == 1:
            return audio_parts[0]

        return merge_audio_segments(audio_parts)

    def generate_audio_bytes(self, text: str, gender: str = 'female', rate: str = '', pitch: str = '', volume: str = '') -> bytes:
        """Synchronous wrapper to run async synthesis safely across threads and event loops"""
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(asyncio.run, self.synthesize(text, gender, rate, pitch, volume)).result()
            return asyncio.run(self.synthesize(text, gender, rate, pitch, volume))
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return b""

tts_service = TTSService()
