# -*- coding: utf-8 -*-
import sys, io, time
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 950})

        url = 'file:///E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html'
        print(f"Loading {url}...")
        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Open Composer Tool Window
        page.evaluate("if (typeof openToolWindow === 'function') openToolWindow('composer');")
        time.sleep(1)

        # Make sure Composer Studio is rendered
        page.evaluate("if (window.initComposerStudio) window.initComposerStudio();")
        time.sleep(1)

        # 1. TEST DRAWER BEHAVIOR
        # Collapse left panel first to test clicking doesn't expand it
        page.evaluate("document.getElementById('composerSidebarLeft').classList.add('collapsed')")
        time.sleep(0.3)

        # Click on widget on canvas
        chat_el = page.locator('#widget-w-chat-1')
        print(f"Chat widget visible: {chat_el.is_visible()}")
        chat_el.click(position={"x": 50, "y": 50})
        time.sleep(0.5)

        is_collapsed_after_click = page.evaluate("document.getElementById('composerSidebarLeft').classList.contains('collapsed')")
        print(f"1. Sidebar collapsed after widget click: {is_collapsed_after_click}")
        assert is_collapsed_after_click == True, "Sidebar should NOT pop open when simply selecting a widget!"

        # Now click the Gear button ⚙️ on the badge
        gear_btn = chat_el.locator('.btn-widget-gear')
        print(f"Gear button visible: {gear_btn.is_visible()}")
        gear_btn.click()
        time.sleep(0.5)

        is_collapsed_after_gear = page.evaluate("document.getElementById('composerSidebarLeft').classList.contains('collapsed')")
        print(f"1. Sidebar collapsed after Gear click: {is_collapsed_after_gear}")
        assert is_collapsed_after_gear == False, "Sidebar MUST expand when clicking Gear button ⚙️!"

        # Screenshot test 1
        page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/v3_test1_gear_and_drawer.png")

        # 2. TEST CHAT WIDGET LIVE PREVIEW & THEMES
        print("2. Testing Chat Widget customizer & live sync...")
        tab_theme = page.locator('#tabSubTheme')
        if tab_theme.count() > 0:
            tab_theme.click()
            time.sleep(0.5)
            first_theme_card = page.locator('#cwcPresetsGrid .cwc-preset-card').first
            theme_name = first_theme_card.get_attribute('data-theme') or first_theme_card.get_attribute('data-chat-theme')
            first_theme_card.dispatch_event('click')
            time.sleep(0.5)
            has_theme_class = page.evaluate(f"document.querySelector('#widget-w-chat-1').classList.contains('theme-{theme_name}')")
            print(f"2. Canvas Chat has theme-{theme_name} class: {has_theme_class}")
            assert has_theme_class == True, f"Canvas Chat widget must apply theme-{theme_name} class!"

        # Switch back to Default tab and change text color
        tab_std = page.locator('#tabSubStandard')
        if tab_std.count() > 0:
            tab_std.click()
            time.sleep(0.5)
            page.evaluate("""
                const w = window.ComposerStudio.getState().pages[0].widgets.find(x => x.type === 'chat');
                w.fontColor = '#ff0055';
                w.usernameColor = '#00ffcc';
                w.fontSize = 22;
                window.ComposerStudio.getState().selectedWidgetId = w.id;
                window.ComposerStudio.renderCanvasWidgets();
            """)
            time.sleep(0.5)
            chat_color = page.evaluate("document.querySelector('#widget-w-chat-1 .text').style.color")
            print(f"2. Canvas Chat text color: {chat_color}")
            assert '255, 0, 85' in chat_color or '#ff0055' in chat_color, "Canvas chat must sync fontColor!"

        # 3. TEST WEBCAM FRAME RATIO & TRANSPARENCY
        print("3. Testing Webcam Frame ratio and transparency...")
        page.evaluate("""
            const st = window.ComposerStudio.getState();
            st.pages[0].widgets = st.pages[0].widgets.filter(x => x.type !== 'webcam');
            window.ComposerStudio.addWidget('webcam');
        """)
        time.sleep(0.5)
        wc = page.evaluate("window.ComposerStudio.getState().pages[0].widgets.find(x => x.type === 'webcam')")
        print(f"3. Added webcam widget: w={wc['width']}, h={wc['height']}, ratio={wc.get('ratio')}")

        page.evaluate(f"window.ComposerStudio.openWidgetSettings('{wc['id']}')")
        time.sleep(0.5)

        # Check ratio change to 4:3
        page.select_option('#compWebcamRatio', '4:3')
        time.sleep(0.5)
        wc_after_4_3 = page.evaluate("window.ComposerStudio.getState().pages[0].widgets.find(x => x.type === 'webcam')")
        expected_h = int(round(wc_after_4_3['width'] * 3 / 4))
        print(f"3. Webcam ratio 4:3 -> width={wc_after_4_3['width']}, height={wc_after_4_3['height']}, expected={expected_h}")
        assert wc_after_4_3['height'] == expected_h, "Webcam height must update dynamically on ratio change!"

        # Check transparency of webcam
        wc_bg = page.evaluate("window.getComputedStyle(document.querySelector('.composer-widget.type-webcam .webcam-frame')).backgroundColor")
        print(f"3. Webcam frame background: {wc_bg}")
        assert 'rgba(0, 0, 0, 0)' in wc_bg or 'transparent' in wc_bg, "Webcam frame interior must be 100% transparent!"

        # 4. TEST TEXT WIDGET & MARQUEE SPEED
        print("4. Testing Text Widget & Marquee Speed...")
        page.evaluate("window.ComposerStudio.addWidget('text');")
        time.sleep(0.5)
        txt_w = page.evaluate("window.ComposerStudio.getState().pages[0].widgets.find(x => x.type === 'text')")
        page.evaluate(f"window.ComposerStudio.openWidgetSettings('{txt_w['id']}')")
        time.sleep(0.5)

        speed_display = page.evaluate("document.getElementById('compTextSpeedRow').style.display")
        print(f"4. Speed row display in ticker mode: {speed_display}")
        assert speed_display != 'none', "Marquee speed slider must be visible in ticker mode!"

        # Switch to static mode
        page.select_option('#compTextMode', 'static')
        time.sleep(0.5)
        speed_display_static = page.evaluate("document.getElementById('compTextSpeedRow').style.display")
        print(f"4. Speed row display in static mode: {speed_display_static}")
        assert speed_display_static == 'none', "Marquee speed slider must be hidden in static mode!"

        # 5. TEST VIEWER WIDGET V2 & NUMBER TICKER
        print("5. Testing Viewer Widget V2 & Number Ticker...")
        page.evaluate("window.ComposerStudio.addWidget('viewer');")
        time.sleep(0.5)
        viewer_w = page.evaluate("window.ComposerStudio.getState().pages[0].widgets.find(x => x.type === 'viewer')")
        page.evaluate(f"window.ComposerStudio.openWidgetSettings('{viewer_w['id']}')")
        time.sleep(0.5)

        vt_cols_count = page.locator(f"#widget-{viewer_w['id']} .vt-col").count()
        print(f"5. Viewer rolling ticker columns count: {vt_cols_count}")
        assert vt_cols_count > 0, "Viewer widget must use animated rolling number ticker columns (.vt-col)!"

        # Click demo button +50
        initial_val = page.evaluate(f"window.ComposerStudio.getState().pages[0].widgets.find(x => x.id === '{viewer_w['id']}').mockViewerCount")
        page.click('#btnDemoViewerAdd')
        time.sleep(0.5)
        val_after_add = page.evaluate(f"window.ComposerStudio.getState().pages[0].widgets.find(x => x.id === '{viewer_w['id']}').mockViewerCount")
        print(f"5. Viewer count after +50 demo: initial={initial_val}, after={val_after_add}")
        assert val_after_add == initial_val + 50, "Viewer count must increment by +50 on demo button click!"

        # 6. TEST CHARACTER DRAG & TRANSPARENCY
        print("6. Testing Character Widget drag pointer-events...")
        page.evaluate("window.ComposerStudio.addWidget('character');")
        time.sleep(0.5)
        char_pe = page.evaluate("window.getComputedStyle(document.querySelector('.composer-widget.type-character img')).pointerEvents")
        char_drag = page.evaluate("document.querySelector('.composer-widget.type-character img').draggable")
        print(f"6. Character img pointer-events: {char_pe}, draggable: {char_drag}")
        assert char_pe == 'none', "Character image must have pointer-events: none to prevent ghost drag!"
        assert char_drag == False, "Character image must have draggable=false!"

        # 7. TEST TRANSPARENT WIDGETS
        print("7. Testing transparent widgets standby rules...")
        for t in ['image', 'video', 'alert', 'now_playing', 'emote_party']:
            page.evaluate(f"window.ComposerStudio.addWidget('{t}')")
            time.sleep(0.3)
            bg = page.evaluate(f"window.getComputedStyle(document.querySelector('.composer-widget.type-{t} .composer-widget-inner')).backgroundColor")
            print(f"7. Widget {t} inner background: {bg}")
            assert 'rgba(0, 0, 0, 0)' in bg or 'transparent' in bg, f"Widget {t} must have transparent background in standby!"

        page.screenshot(path="C:/Users/Meng-PC/.gemini/antigravity/brain/2f01bb89-ff70-4e16-9ae3-ebaf207778d1/v3_test_all_features_summary.png")
        print("All tests passed with flying colors! Screenshot saved.")
        browser.close()

if __name__ == '__main__':
    test()
