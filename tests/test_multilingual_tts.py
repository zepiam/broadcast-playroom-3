import unittest
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_service import split_text_by_language, resolve_voice_for_lang, tts_service
import soundfile as sf

class TestMultilingualTTS(unittest.TestCase):
    def test_split_text_thai_english(self):
        segs = split_text_by_language("สวัสดีครับ hello world")
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0], ("สวัสดีครับ hello world", "th"))

    def test_split_text_pure_english(self):
        segs = split_text_by_language("Good morning everyone!")
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0], ("Good morning everyone!", "th"))

    def test_split_text_thai_japanese(self):
        segs = split_text_by_language("สวัสดีครับ こんにちは")
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0], ("สวัสดีครับ", "th"))
        self.assertEqual(segs[1], ("こんにちは", "ja"))

    def test_split_text_thai_english_japanese(self):
        segs = split_text_by_language("สวัสดีครับ hello my friend こんにちは")
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0], ("สวัสดีครับ hello my friend", "th"))
        self.assertEqual(segs[1], ("こんにちは", "ja"))

    def test_split_text_japanese_then_thai(self):
        segs = split_text_by_language("こんにちは สวัสดีครับ")
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0], ("こんにちは", "ja"))
        self.assertEqual(segs[1], ("สวัสดีครับ", "th"))

    def test_voice_routing(self):
        self.assertEqual(resolve_voice_for_lang("th", "female"), "th-TH-PremwadeeNeural")
        self.assertEqual(resolve_voice_for_lang("th", "male"), "th-TH-NiwatNeural")
        self.assertEqual(resolve_voice_for_lang("en", "female"), "th-TH-PremwadeeNeural")
        self.assertEqual(resolve_voice_for_lang("en", "male"), "th-TH-NiwatNeural")
        self.assertEqual(resolve_voice_for_lang("ja", "female"), "ja-JP-NanamiNeural")
        self.assertEqual(resolve_voice_for_lang("ja", "male"), "ja-JP-KeitaNeural")
        self.assertEqual(resolve_voice_for_lang("ko", "female"), "ko-KR-SunHiNeural")
        self.assertEqual(resolve_voice_for_lang("zh", "female"), "zh-CN-XiaoxiaoNeural")

    def test_real_synthesis_thai_japanese(self):
        # Actual synthesis test with Thai followed by Japanese
        audio = tts_service.generate_audio_bytes("สวัสดีครับ こんにちは", gender="female")
        self.assertIsNotNone(audio)
        self.assertGreater(len(audio), 5000)
        
        # Verify valid audio stream with soundfile
        data, sr = sf.read(io.BytesIO(audio), dtype='float32')
        self.assertEqual(sr, 24000)
        # Duration should be long enough to cover both phrases (> 1.2s)
        duration = len(data) / sr
        self.assertGreater(duration, 1.2)

if __name__ == '__main__':
    unittest.main()
