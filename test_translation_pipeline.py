import sys
import unittest

from chat_bridge import ChatBridge, ChatMessage
from translator import Translator
from tts_service import resolve_voice
from language_detect import detect_language

class TestTranslationPipeline(unittest.TestCase):
    def test_language_detect(self):
        self.assertEqual(detect_language("Hello everyone"), "en")
        self.assertEqual(detect_language("สวัสดีชาวโลก"), "th")
        self.assertEqual(detect_language("こんにちは"), "ja")
        self.assertEqual(detect_language("안녕하세요"), "ko")

    def test_translator_direct(self):
        t = Translator()
        # English -> Thai
        res, lang = t.translate("Good morning")
        self.assertIsNotNone(res)
        self.assertIn("สวัสด", res)
        self.assertEqual(lang, "en")

        # Commands should not be translated
        res_cmd, _ = t.translate("!ask who is the best?")
        self.assertIsNone(res_cmd)

        # Thai text should not be re-translated
        res_th, detected_th = t.translate("สวัสดีครับท่านผู้ชม")
        self.assertIsNone(res_th)
        self.assertEqual(detected_th, "th")

    def test_tts_voice_resolution(self):
        # Thai female & male
        v, g = resolve_voice("สวัสดีครับ", "female")
        self.assertEqual(v, "th-TH-PremwadeeNeural")
        self.assertEqual(g, "female")
        v, g = resolve_voice("สวัสดีครับ", "male")
        self.assertEqual(v, "th-TH-NiwatNeural")
        self.assertEqual(g, "male")

        # English female & male (routed to Thai TTS model as designed)
        v, g = resolve_voice("Hello world", "female")
        self.assertEqual(v, "th-TH-PremwadeeNeural")
        self.assertEqual(g, "female")
        v, g = resolve_voice("Hello world", "male")
        self.assertEqual(v, "th-TH-NiwatNeural")
        self.assertEqual(g, "male")

        # Japanese
        v, g = resolve_voice("こんにちは", "female")
        self.assertEqual(v, "ja-JP-NanamiNeural")
        v, g = resolve_voice("こんにちは", "male")
        self.assertEqual(v, "ja-JP-KeitaNeural")

        # Korean
        v, g = resolve_voice("안녕하세요", "female")
        self.assertEqual(v, "ko-KR-SunHiNeural")

    def test_chat_bridge_translate_mode(self):
        cb = ChatBridge()
        cb.translator = Translator()
        cb.set_translate_mode("translate")
        self.assertEqual(cb.get_translate_mode(), "translate")

        # 1. Foreign message in translate mode
        m1 = ChatMessage("youtube", "John", "Nice stream today!")
        cb._on_message("YouTube", m1)
        last1 = cb.get_messages(0)[-1]
        self.assertTrue(last1["is_translated"])
        self.assertEqual(last1["original_text"], "Nice stream today!")
        self.assertTrue(len(last1["text"]) > 0)
        self.assertNotEqual(last1["text"], "Nice stream today!")

        # 2. Command in translate mode (should NOT translate)
        m2 = ChatMessage("youtube", "John", "!roll 100")
        cb._on_message("YouTube", m2)
        last2 = cb.get_messages(0)[-1]
        self.assertFalse(last2["is_translated"])
        self.assertEqual(last2["text"], "!roll 100")

        # 3. Thai message in translate mode
        m3 = ChatMessage("twitch", "Somchai", "สตรีมสนุกมากครับ")
        cb._on_message("Twitch", m3)
        last3 = cb.get_messages(0)[-1]
        self.assertFalse(last3["is_translated"])
        self.assertEqual(last3["text"], "สตรีมสนุกมากครับ")

        # 4. Multilang mode (should NOT translate)
        cb.set_translate_mode("multilang")
        self.assertEqual(cb.get_translate_mode(), "multilang")
        m4 = ChatMessage("twitch", "Alice", "See you tomorrow!")
        cb._on_message("Twitch", m4)
        last4 = cb.get_messages(0)[-1]
        self.assertFalse(last4["is_translated"])
        self.assertEqual(last4["text"], "See you tomorrow!")

if __name__ == "__main__":
    unittest.main()
