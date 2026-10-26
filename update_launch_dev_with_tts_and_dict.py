import re

file_path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/launch_dev.py'

with open(file_path, 'r', encoding='utf-8') as f:
    c = f.read()

# Add imports
if 'from dictionary_manager import dict_manager' not in c:
    c = c.replace(
        'from chat_bridge import chat_bridge',
        'from chat_bridge import chat_bridge\nfrom dictionary_manager import dict_manager\nfrom tts_service import tts_service'
    )

new_handle_api = """    def handle_api(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        path = parsed.path
        
        # 1. Handle TTS Audio streaming
        if path == '/api/tts':
            text = qs.get('text', [''])[0]
            gender = qs.get('gender', ['female'])[0]
            rate = qs.get('rate', ['+0%'])[0]
            pitch = qs.get('pitch', ['+0Hz'])[0]
            volume = qs.get('volume', ['+0%'])[0]
            
            # Step 1 in Pipeline: Apply Word Replacement Dictionary
            processed_text = dict_manager.apply_replace(text)
            
            # Step 2 in Pipeline: Synthesize with Edge-TTS
            audio_bytes = tts_service.generate_audio_bytes(processed_text, gender, rate, pitch, volume)
            if audio_bytes:
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Length', str(len(audio_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(audio_bytes)
                return
            else:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                return

        response_data = {}
        if path == '/api/connect':
            platform = qs.get('platform', [''])[0]
            target = qs.get('target', [''])[0]
            response_data = chat_bridge.connect(platform, target)
        elif path == '/api/disconnect':
            platform = qs.get('platform', [''])[0]
            response_data = chat_bridge.disconnect(platform)
        elif path == '/api/status':
            response_data = chat_bridge.get_status()
        elif path == '/api/messages':
            last_id = int(qs.get('last_id', [0])[0])
            response_data = {'messages': chat_bridge.get_messages(last_id)}
        elif path == '/api/dictionary':
            response_data = dict_manager.get_all()
        elif path == '/api/dictionary/sync':
            response_data = dict_manager.sync_remote()
        elif path == '/api/dictionary/add':
            find_w = qs.get('find', [''])[0]
            rep_w = qs.get('replace', [''])[0]
            response_data = dict_manager.add_word(find_w, rep_w)
        elif path == '/api/dictionary/delete':
            word = qs.get('word', [''])[0]
            response_data = dict_manager.delete_word(word)
        else:
            response_data = {'error': 'Unknown endpoint'}

        payload = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(payload)"""

pattern_handle_api = r'    def handle_api\(self, parsed\):.*?self\.wfile\.write\(payload\)'
c = re.sub(pattern_handle_api, new_handle_api, c, count=1, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated launch_dev.py with Dictionary and Edge-TTS API successfully!")
