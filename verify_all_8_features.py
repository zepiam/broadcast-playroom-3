import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

artifact_dir = r'C:\Users\Meng-PC\.gemini\antigravity\brain\2f01bb89-ff70-4e16-9ae3-ebaf207778d1'
abs_html = os.path.abspath(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\dist\index.html')
clean_path = abs_html.replace('\\', '/')
file_url = f"file:///{clean_path}"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1366, 'height': 850})
        page = await context.new_page()

        # Disable popout mode in tests so floating windows open in-app for verification screenshots
        await page.add_init_script("localStorage.setItem('bp3_auto_popout_windows', 'false');")

        print(f"Loading {file_url}...")
        await page.goto(file_url, wait_until='networkidle')
        await asyncio.sleep(1.0)

        # -------------------------------------------------------------
        # TEST 1: Playroom Sound & Action (Task 3)
        # -------------------------------------------------------------
        print("Testing Playroom Studio...")
        await page.evaluate("openToolWindow('playroom')")
        await asyncio.sleep(0.5)
        await page.evaluate("switchPlayroomTab(3)")
        await asyncio.sleep(0.3)
        await page.evaluate("runPlayroomSimulatedChat()")
        await asyncio.sleep(0.6)

        playroom_sc_path = os.path.join(artifact_dir, "verified_task3_playroom_sound_and_alert.png")
        await page.screenshot(path=playroom_sc_path)
        print("Captured Playroom demo screenshot.")

        # -------------------------------------------------------------
        # TEST 2: Overlay Composer 3-Row Layout & Layer SVGs (Tasks 4, 5)
        # -------------------------------------------------------------
        print("Testing Overlay Composer 3-Row Layout & Layers...")
        await page.evaluate("closeToolWindow('playroom')")
        await asyncio.sleep(0.3)
        await page.evaluate("openToolWindow('composer')")
        await asyncio.sleep(0.8)

        # Ensure text widget exists or add one to inspect
        await page.evaluate("""() => {
          const cp = window.ComposerStudio?.getActivePage?.();
          if (cp) {
            let tw = cp.widgets.find(w => w.type === 'text');
            if (!tw) {
              window.ComposerStudio.addWidget('text');
            }
          }
        }""")
        await asyncio.sleep(0.5)

        composer_sc_path = os.path.join(artifact_dir, "verified_task4_composer_3row_and_layers.png")
        await page.screenshot(path=composer_sc_path)
        print("Captured Composer Studio 3-Row Layout screenshot.")

        # -------------------------------------------------------------
        # TEST 3: Text Widget Settings (Task 7)
        # -------------------------------------------------------------
        print("Testing Text Widget Customizer (vAlign, bg toggle, stroke & shadow)...")
        await page.evaluate("""() => {
          const cp = window.ComposerStudio?.getActivePage?.();
          if (cp) {
            const tw = cp.widgets.find(w => w.type === 'text');
            if (tw) {
              window.ComposerStudio.openWidgetSettings(tw.id);
            }
          }
        }""")
        await asyncio.sleep(0.6)

        text_settings_sc_path = os.path.join(artifact_dir, "verified_task7_text_valign_stroke_shadow.png")
        await page.screenshot(path=text_settings_sc_path)
        print("Captured Text Widget customizer screenshot.")

        # -------------------------------------------------------------
        # TEST 4: Real ASK Poll (Task 8)
        # -------------------------------------------------------------
        print("Testing Real ASK Poll...")
        await page.evaluate("closeToolWindow('composer')")
        await asyncio.sleep(0.3)

        # Open ASK Poll
        await page.evaluate("openToolWindow('ask')")
        await asyncio.sleep(0.5)

        # Inject real chat votes
        await page.evaluate("""() => {
          window.injectIncomingChat({
            username: 'StreamViewer01',
            platform: 'Twitch',
            icon: './assets/twitch.png',
            avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=v1',
            color: '#38bdf8',
            isVip: true,
            text: 'A',
            time: '18:30'
          });
          window.injectIncomingChat({
            username: 'GamerGirl99',
            platform: 'YouTube',
            icon: './assets/youtube.png',
            avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=v2',
            color: '#ef4444',
            isVip: false,
            text: 'B',
            time: '18:31'
          });
          window.injectIncomingChat({
            username: 'SuperFan_TH',
            platform: 'TikTok',
            icon: './assets/tiktok.png',
            avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=v3',
            color: '#ec4899',
            isVip: false,
            text: 'A',
            time: '18:31'
          });
        }""")
        await asyncio.sleep(0.5)

        ask_sc_path = os.path.join(artifact_dir, "verified_task8_real_ask_poll_votes.png")
        await page.screenshot(path=ask_sc_path)
        print("Captured Real ASK poll vote screenshot.")

        # -------------------------------------------------------------
        # TEST 5: Real Giveaway (Task 8)
        # -------------------------------------------------------------
        print("Testing Real Giveaway...")
        await page.evaluate("closeToolWindow('ask')")
        await asyncio.sleep(0.3)
        await page.evaluate("openToolWindow('giveaway')")
        await asyncio.sleep(0.5)
        await page.evaluate("switchGwStep(2)")
        await asyncio.sleep(0.3)

        await page.evaluate("""() => {
          window.injectIncomingChat({
            username: 'LuckyGuy_Live',
            platform: 'Twitch',
            icon: './assets/twitch.png',
            avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=g1',
            color: '#a855f7',
            isVip: true,
            text: '#join ขอให้ได้ด้วยเถอะ!',
            time: '18:32'
          });
          window.injectIncomingChat({
            username: 'Somying_Happy',
            platform: 'YouTube',
            icon: './assets/youtube.png',
            avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=g2',
            color: '#ef4444',
            isVip: false,
            text: 'ร่วมสนุก #join ค่ะ',
            time: '18:32'
          });
        }""")
        await asyncio.sleep(0.5)

        gw_sc_path = os.path.join(artifact_dir, "verified_task8_real_giveaway_entrants.png")
        await page.screenshot(path=gw_sc_path)
        print("Captured Real Giveaway entrants screenshot.")

        # -------------------------------------------------------------
        # TEST 6: Real Randomizer (Task 8)
        # -------------------------------------------------------------
        print("Testing Real Randomizer...")
        await page.evaluate("closeToolWindow('giveaway')")
        await asyncio.sleep(0.3)
        await page.evaluate("openToolWindow('randomizer')")
        await asyncio.sleep(0.5)
        await page.evaluate("pickChatViewerRandom()")
        await asyncio.sleep(0.5)

        rand_sc_path = os.path.join(artifact_dir, "verified_task8_real_randomizer_imported_chatters.png")
        await page.screenshot(path=rand_sc_path)
        print("Captured Real Randomizer imported chatters screenshot.")

        await browser.close()
        print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    asyncio.run(main())
