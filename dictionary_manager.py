import os
import sys
import json
import urllib.request
import ssl
import re

DICT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'replace_words.json'))
OFFICIAL_DICT_URL = "https://men9ch.com/wiki/ng-replace.php?pid=broadcast-playroom&download=1"

class DictionaryManager:
    def __init__(self):
        self._words = {}
        self._last_sync_time = "ยังไม่ได้ซิงค์"
        self.load_local()
        # Initial sync if empty
        if not self._words:
            self.sync_remote()

    def load_local(self):
        if os.path.exists(DICT_FILE):
            try:
                with open(DICT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._words = data.get('replace_words', {})
                    self._last_sync_time = data.get('last_sync', 'บันทึกในเครื่อง')
                    print(f"[DICT] Loaded {len(self._words)} words from local {DICT_FILE}")
            except Exception as e:
                print(f"[DICT] Error loading local dictionary: {e}")

    def save_local(self):
        try:
            with open(DICT_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'type': 'replace_words',
                    'last_sync': self._last_sync_time,
                    'total': len(self._words),
                    'replace_words': self._words
                }, f, ensure_ascii=False, indent=2)
            print(f"[DICT] Saved {len(self._words)} words to {DICT_FILE}")
            return True
        except Exception as e:
            print(f"[DICT] Error saving dictionary: {e}")
            return False

    def sync_remote(self):
        print(f"[DICT] Syncing official dictionary from {OFFICIAL_DICT_URL}...")
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(
                OFFICIAL_DICT_URL,
                headers={"User-Agent": "BroadcastPlayroom/3.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
            
            incoming = data.get("replace_words", {})
            if isinstance(incoming, dict) and incoming:
                # Merge into existing words
                for k, v in incoming.items():
                    if isinstance(v, dict):
                        read_word = v.get('read', '') or v.get('display', '') or k
                        self._words[k] = read_word
                    elif isinstance(v, str):
                        self._words[k] = v
                import time
                self._last_sync_time = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
                self.save_local()
                print(f"[DICT] Successfully synced {len(incoming)} words from men9ch.com! Total: {len(self._words)}")
                return {'success': True, 'count': len(self._words), 'last_sync': self._last_sync_time}
        except Exception as e:
            print(f"[DICT] Sync failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_all(self):
        return {
            'replace_words': self._words,
            'words': self._words,
            'total': len(self._words),
            'last_sync': self._last_sync_time
        }

    def add_word(self, find_word: str, replace_word: str):
        find_word = find_word.strip()
        replace_word = replace_word.strip()
        if not find_word or not replace_word:
            return {'success': False, 'error': 'คำค้นหาและคำแทนที่ต้องไม่ว่างเปล่า'}
        self._words[find_word] = replace_word
        self.save_local()
        return {'success': True, 'find': find_word, 'replace': replace_word}

    def delete_word(self, find_word: str):
        find_word = find_word.strip()
        if find_word in self._words:
            del self._words[find_word]
            self.save_local()
            return {'success': True, 'deleted': find_word}
        return {'success': False, 'error': 'ไม่พบคำนี้ในคลัง'}

    def apply_replace(self, text: str) -> str:
        """แปลงคำตามคลังศัพท์ก่อนส่งเข้า TTS Pipeline"""
        if not text or not self._words:
            return text
        
        # Sort by length descending to replace longer phrases first
        sorted_keys = sorted(self._words.keys(), key=len, reverse=True)
        for key in sorted_keys:
            rep = self._words[key]
            # Use regex word boundaries for alphanumeric words, or direct replace for thai/symbols
            if re.match(r'^[a-zA-Z0-9_]+$', key):
                pattern = re.compile(r'\b' + re.escape(key) + r'\b', re.IGNORECASE)
                text = pattern.sub(rep, text)
            else:
                text = text.replace(key, rep)
        return text

# Global singleton
dict_manager = DictionaryManager()
