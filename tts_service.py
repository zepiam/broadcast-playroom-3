import asyncio
import io
import logging
import re
import sys

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
    'female_en': 'en-US-AvaNeural',
    'male_en': 'en-US-GuyNeural',
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
    val = val.strip()
    if val.startswith(' '):
        val = '+' + val.strip()
    if not val.startswith(('+', '-')):
        if val != '0' and not val.startswith('0'):
            val = '+' + val
    if not val.endswith(default_unit):
        val += default_unit
    return val

def resolve_voice(text: str, gender: str = 'female') -> tuple[str, str]:
    """
    Select voice strictly matching the specified gender for both Thai and English.
    - If text has no Thai characters but has English/Latin: English voice of chosen gender.
    - If text has Thai characters or default: Thai voice of chosen gender.
    Returns (voice_name, gender_key)
    """
    g = 'male' if str(gender).lower() in ['male', 'man', 'boy', 'niwat'] else 'female'
    has_thai = bool(re.search(r'[\u0e00-\u0e7f]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))
    
    if not has_thai and has_english:
        return VOICES[f'{g}_en'], g
    return VOICES[f'{g}_th'], g

class TTSService:
    def __init__(self):
        pass

    async def synthesize(self, text: str, gender: str = 'female', rate: str = '', pitch: str = '', volume: str = '') -> bytes:
        text = sanitize_text(text)
        if not text:
            return b""
        
        voice, g = resolve_voice(text, gender)
        
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

        try:
            comm = edge_tts.Communicate(text, voice=voice, **kwargs)
            buf = io.BytesIO()
            async for chunk in comm.stream():
                if chunk['type'] == 'audio':
                    buf.write(chunk['data'])
            val = buf.getvalue()
            if len(val) > 0:
                return val
        except Exception as e:
            logger.warning(f"TTS stream error with voice {voice}: {e}")

        # Fallback within the EXACT same gender
        try:
            alt_voice = VOICES[f'{g}_en'] if voice == VOICES[f'{g}_th'] else VOICES[f'{g}_th']
            comm_alt = edge_tts.Communicate(text, voice=alt_voice, **kwargs)
            buf = io.BytesIO()
            async for chunk in comm_alt.stream():
                if chunk['type'] == 'audio':
                    buf.write(chunk['data'])
            return buf.getvalue()
        except Exception as e:
            logger.error(f"TTS fallback stream error: {e}")
            return b""

    def generate_audio_bytes(self, text: str, gender: str = 'female', rate: str = '', pitch: str = '', volume: str = '') -> bytes:
        """Synchronous wrapper to run async synthesis safely"""
        try:
            return asyncio.run(self.synthesize(text, gender, rate, pitch, volume))
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return b""

tts_service = TTSService()
