import unittest
import sys
import os
import io
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rvc_service import rvc_service
from tts_service import tts_service
import soundfile as sf

class TestRVCStartupReadiness(unittest.TestCase):
    def test_rvc_conversion_and_warmup(self):
        # 1. Check edition and status
        self.assertEqual(rvc_service.edition, 'full')
        status = rvc_service.status()
        self.assertTrue(status.get('enabled') or rvc_service.worker)
        
        # 2. Synthesize audio
        audio_mp3 = tts_service.generate_audio_bytes("สวัสดีครับ こんにちは", gender="female")
        self.assertGreater(len(audio_mp3), 1000)
        
        # 3. Convert with RVC
        t0 = time.time()
        converted_audio, mime = rvc_service.convert(audio_mp3)
        elapsed = time.time() - t0
        print(f"RVC conversion completed in {elapsed:.2f}s, mime={mime}, size={len(converted_audio)}")
        
        self.assertEqual(mime, 'audio/wav')
        self.assertGreater(len(converted_audio), 5000)
        
        # 4. Verify soundfile reads the converted WAV
        data, sr = sf.read(io.BytesIO(converted_audio), dtype='float32')
        self.assertGreater(len(data), 0)
        print(f"Verified converted audio: sample_rate={sr}, duration={len(data)/sr:.2f}s")

if __name__ == '__main__':
    unittest.main()
