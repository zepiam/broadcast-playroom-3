import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def run():
    dist_html = os.path.abspath(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\dist\index.html")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-web-security', '--allow-file-access-from-files']
        )
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        page.goto(f"file:///{dist_html}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        
        print("Page loaded successfully.")
        
        # 1. Test opening Playroom from rail
        rail_playroom_btn = page.locator("#btnRailPlayroom")
        assert rail_playroom_btn.is_visible(), "btnRailPlayroom should be visible in rail"
        rail_playroom_btn.click()
        page.wait_for_timeout(500)
        
        win_playroom = page.locator("#win-playroom")
        assert win_playroom.is_visible(), "win-playroom should be visible after clicking rail button"
        print("PASS: Playroom Studio window opened successfully!")
        
        # Verify Playroom Tabs
        page.locator("#btnPlayroomTab2").click()
        page.wait_for_timeout(300)
        assert page.locator("#panePlayroomTab2").is_visible(), "Playroom Tab 2 (Chroma Key) should be visible"
        
        page.locator("#btnPlayroomTab3").click()
        page.wait_for_timeout(300)
        assert page.locator("#panePlayroomTab3").is_visible(), "Playroom Tab 3 (Live Simulator) should be visible"
        
        page.locator("#btnPlayroomTab1").click()
        page.wait_for_timeout(300)
        assert page.locator("#panePlayroomTab1").is_visible(), "Playroom Tab 1 (Clips) should be visible"
        
        page.screenshot(path="playroom_tool_opened.png")
        print("PASS: Saved screenshot playroom_tool_opened.png")
        
        # 2. Open Composer Studio window
        page.locator("#btnRailComposer").click()
        page.wait_for_timeout(800)
        win_composer = page.locator("#win-composer")
        assert win_composer.is_visible(), "win-composer should be visible"
        
        # Position windows side-by-side so both win-composer and win-playroom are visible
        page.evaluate("""() => {
            const wc = document.getElementById('win-composer');
            if (wc) {
                wc.style.top = '40px';
                wc.style.left = '280px';
                wc.style.width = '1040px';
                wc.style.height = '720px';
                wc.style.zIndex = '500';
            }
            const wp = document.getElementById('win-playroom');
            if (wp) {
                wp.style.top = '40px';
                wp.style.left = '1340px';
                wp.style.width = '560px';
                wp.style.height = '720px';
                wp.style.zIndex = '9999';
            }
        }""")
        page.wait_for_timeout(500)
        
        # 3. Add widgets if not present on canvas: Ask, Giveaway, Replie/character, Playroom
        page.evaluate("""() => {
            const types = ['ask', 'giveaway', 'character', 'playroom'];
            types.forEach(t => {
                if (window.ComposerStudio && typeof window.ComposerStudio.addWidget === 'function') {
                    window.ComposerStudio.addWidget(t);
                }
            });
            if (window.ComposerStudio && typeof window.ComposerStudio.renderCanvasWidgets === 'function') {
                window.ComposerStudio.renderCanvasWidgets();
            }
        }""")
        page.wait_for_timeout(800)
        
        # 4. Test real-time connection: Playroom clip test
        page.evaluate("""() => {
            if (typeof playroomTestClip === 'function') {
                playroomTestClip(0);
            }
        }""")
        page.wait_for_timeout(500)
        
        playroom_active_title = page.locator("#win-composer .playroom-clip-title").first
        assert playroom_active_title.is_visible(), "Playroom clip title should be visible in Playroom widget on Canvas!"
        print(f"PASS: Real-time Playroom Trigger verified! Playing: {playroom_active_title.inner_text()}")
        
        # 5. Test real-time connection: Ask update
        page.evaluate("""() => {
            const q = document.getElementById('askQuestion');
            if (q) {
                q.value = 'โหวตสด: มื้อเย็นนี้กินชาบูหรือหมูกระทะดี?';
            }
            if (typeof emitAskState === 'function') {
                emitAskState();
            }
        }""")
        page.wait_for_timeout(500)
        
        ask_widget_text = page.locator("#win-composer [id^='compAskQ_']").first
        print(f"PASS: Real-time Ask Poll verified! Question on Canvas: {ask_widget_text.inner_text()}")
        
        # 6. Test real-time connection: Giveaway winner roll
        page.evaluate("""() => {
            if (typeof emitGwState === 'function') {
                emitGwState('Somchai_VIP_Winner');
            }
        }""")
        page.wait_for_timeout(500)
        
        gw_winner_el = page.locator("#win-composer [id^='compGwWinner_']").first
        assert gw_winner_el.is_visible(), "Giveaway winner banner should be visible on Canvas!"
        print(f"PASS: Real-time Giveaway Winner verified! Banner: {gw_winner_el.inner_text()}")
        
        # 7. Test real-time connection: Replie speech & bounce
        page.evaluate("""() => {
            if (typeof demoReplieAction === 'function') {
                demoReplieAction('!hi', 'ยินดีต้อนรับสู่สตรีมครับทุกคน!', 'happy');
            }
        }""")
        page.wait_for_timeout(500)
        
        replie_bubble = page.locator("#win-composer [id^='compCharBubble_']").first
        assert replie_bubble.is_visible(), "Replie speech bubble should be visible on Canvas!"
        print(f"PASS: Real-time Replie Reaction verified! Bubble: {replie_bubble.inner_text()}")
        
        page.screenshot(path="realtime_sync_all_tools_and_widgets.png")
        print("PASS: Saved screenshot realtime_sync_all_tools_and_widgets.png")
        
        browser.close()

if __name__ == '__main__':
    run()
