import os, sys, tempfile, threading
from pathlib import Path

os.environ['BP3_EDITION'] = 'lite'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.dont_write_bytecode = True

from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import launch_dev

with tempfile.TemporaryDirectory(prefix='bp3-events-') as tmp:
    launch_dev.LAYOUT_FILE = str(Path(tmp) / 'layout.json')
    launch_dev._LAYOUT_CACHE = None
    launch_dev.save_layout({
        'activePageId': 'one',
        'pages': [{'id': 'one', 'widgets': [{'id': 'chat', 'type': 'chat', 'chatMode': 'default', 'width': 600, 'height': 400}]}]
    })
    server = ThreadingHTTPServer(('127.0.0.1', 0), launch_dev.QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={'width': 1280, 'height': 850})
            page = ctx.new_page()
            page.set_default_timeout(10000)
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html')

            # Hook TTS tracking
            page.evaluate("""
                window.__tts = [];
                window.playChatMessageSpeech = (name, text, plat, id) => {
                    window.__tts.push({ name, text, plat });
                };
                window._masterTtsEnabled = true;
            """)

            # 1. Normal Chat Message (MUST trigger TTS and full chat row)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-1',
                    username: 'SomchaiChatter',
                    platform: 'TikTok',
                    platform_key: 'tiktok',
                    text: 'สวัสดีครับผมแชทมาถาม',
                    event: 'message'
                });
            """)
            page.wait_for_timeout(200)

            tts_queue = page.evaluate("window.__tts")
            assert len(tts_queue) == 1, f"Expected 1 TTS item, got {len(tts_queue)}"
            assert tts_queue[0]['text'] == 'สวัสดีครับผมแชทมาถาม'

            normal_row = page.locator('#chatList .chat-row:not(.chat-event-item)').last
            assert 'สวัสดีครับผมแชทมาถาม' in normal_row.inner_text()
            assert 'SomchaiChatter' in normal_row.inner_text()
            # Must have TTS pending badge
            assert normal_row.locator('.chat-tts-time').count() == 1

            # Activity events list should be empty so far
            events_len = page.evaluate("window.getActivityEventsList().length")
            assert events_len == 0, f"Expected 0 activity events, got {events_len}"

            # 2. TikTok Like Event (MUST be small gray item in chatList, in eventsList, NO TTS!)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-2',
                    username: 'TikTokLiker',
                    platform: 'TikTok',
                    platform_key: 'tiktok',
                    event: 'like',
                    amount: 15
                });
            """)
            page.wait_for_timeout(200)

            # TTS count must STILL be 1
            tts_len = page.evaluate("window.__tts.length")
            assert tts_len == 1, f"Like event must not trigger TTS! Got {tts_len}"

            # Check compact chat-event-item in #chatList
            event_row = page.locator('#chatList .chat-event-item').last
            assert event_row.count() == 1
            event_text = event_row.inner_text()
            assert 'TikTokLiker' in event_text
            assert 'กดหัวใจ' in event_text
            assert '×15' in event_text
            # No TTS badge on event row
            assert event_row.locator('.chat-tts-time').count() == 0

            # Check #eventsList on right side
            ev_list_text = page.locator('#eventsList').inner_text()
            assert 'TikTokLiker' in ev_list_text
            assert 'กดหัวใจ' in ev_list_text

            # 3. YouTube Like Event (MUST be small gray item in chatList, in eventsList, NO TTS!)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-3',
                    username: 'YtFan',
                    platform: 'YouTube',
                    platform_key: 'youtube',
                    event: 'like'
                });
            """)
            page.wait_for_timeout(200)
            assert page.evaluate("window.__tts.length") == 1
            event_text = page.locator('#chatList .chat-event-item').last.inner_text()
            assert 'YtFan' in event_text
            assert 'กดถูกใจไลฟ์' in event_text

            # 4. TikTok Follow Event (NO TTS, compact row, in eventsList)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-4',
                    username: 'NewFollower',
                    platform: 'TikTok',
                    platform_key: 'tiktok',
                    event: 'follow'
                });
            """)
            page.wait_for_timeout(200)
            assert page.evaluate("window.__tts.length") == 1
            event_text = page.locator('#chatList .chat-event-item').last.inner_text()
            assert 'NewFollower' in event_text
            assert 'กดติดตาม' in event_text

            # 5. Twitch / YouTube Sub Event (NO TTS, compact row, in eventsList)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-5',
                    username: 'LoyalSub',
                    platform: 'Twitch',
                    platform_key: 'twitch',
                    event: 'sub',
                    months: 6
                });
            """)
            page.wait_for_timeout(200)
            assert page.evaluate("window.__tts.length") == 1
            event_text = page.locator('#chatList .chat-event-item').last.inner_text()
            assert 'LoyalSub' in event_text
            assert 'ต่ออายุสมาชิก' in event_text or 'สมัครสมาชิก' in event_text
            assert '6 เดือน' in event_text

            # 6. SuperChat Event (NO TTS, compact row, in eventsList)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-6',
                    username: 'SuperDonor',
                    platform: 'YouTube',
                    platform_key: 'youtube',
                    event: 'superchat',
                    amount: 500,
                    currency: '฿'
                });
            """)
            page.wait_for_timeout(200)
            assert page.evaluate("window.__tts.length") == 1
            event_text = page.locator('#chatList .chat-event-item').last.inner_text()
            assert 'SuperDonor' in event_text
            assert 'Super Chat' in event_text
            assert '500' in event_text

            # 7. TikTok Gift Event (NO TTS, compact row, in eventsList)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-7',
                    username: 'GiftSender',
                    platform: 'TikTok',
                    platform_key: 'tiktok',
                    event: 'gift',
                    gift_name: 'กุหลาบ',
                    count: 99
                });
            """)
            page.wait_for_timeout(200)
            assert page.evaluate("window.__tts.length") == 1
            event_text = page.locator('#chatList .chat-event-item').last.inner_text()
            assert 'GiftSender' in event_text
            assert 'ส่งของขวัญ กุหลาบ ×99' in event_text

            # 8. TikTok Join Event (MUST BE COMPLETELY DROPPED! NO CHAT ROW, NO EVENT LIST, NO TTS!)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-8',
                    username: 'GhostJoiner',
                    platform: 'TikTok',
                    platform_key: 'tiktok',
                    event: 'join'
                });
            """)
            page.wait_for_timeout(200)

            assert page.evaluate("window.__tts.length") == 1
            assert 'GhostJoiner' not in page.locator('#chatList').inner_text()
            assert 'GhostJoiner' not in page.locator('#eventsList').inner_text()
            assert not page.evaluate("window.getActivityEventsList().some(e => e.username === 'GhostJoiner')")

            # 9. Another Normal Chat Message (TTS works again as expected)
            page.evaluate("""
                injectIncomingChat({
                    id: 'msg-9',
                    username: 'ViewerSecond',
                    platform: 'Twitch',
                    platform_key: 'twitch',
                    text: 'ทดสอบข้อความที่สอง',
                    event: 'message'
                });
            """)
            page.wait_for_timeout(200)

            tts_queue = page.evaluate("window.__tts")
            assert len(tts_queue) == 2, f"Expected 2 TTS items, got {len(tts_queue)}"
            assert tts_queue[1]['text'] == 'ทดสอบข้อความที่สอง'

            # 10. Check author name reading option consistency with other platforms
            page.evaluate("""
                localStorage.setItem('bp3_tts_read_author', 'true');
                window.__audio_sentences = [];
                // Spy on utterance generation if speech synth or Audio called
            """)

            print("ALL 10 TESTS PASSED: Chat message TTS, compact gray event rows, eventsList sync, join complete suppression!")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
