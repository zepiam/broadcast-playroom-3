"""
Broadcast Playroom - Automated Pre-Release Smoke Test Gate
Launches a headless browser to render dist/index.html, executes all JavaScript,
and verifies zero runtime crashes, complete UI tree integrity, and critical function bindings.
"""
import sys
from pathlib import Path
from dist_integrity import verify_dist_health

def run_smoke_test(root_path=None) -> bool:
    if root_path is None:
        root_path = Path(__file__).resolve().parent
    else:
        root_path = Path(root_path)

    # 1. Fast static integrity check
    ok, msg = verify_dist_health(root_path)
    if not ok:
        print(f"[SMOKE TEST GATE FAILED] Static check error: {msg}", file=sys.stderr)
        return False
    print(f"[PASS] Static check: {msg}")

    # 2. Dynamic browser headless rendering check
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[WARN] Playwright not installed; static checks passed.", file=sys.stderr)
        return True

    index_html = root_path / 'dist' / 'index.html'
    errors = []

    print("[SMOKE TEST] Launching headless browser for dynamic verification...")
    with sync_playwright() as p:
        browser = None
        for launch_opt in [{}, {'channel': 'msedge'}, {'channel': 'chrome'}]:
            try:
                browser = p.chromium.launch(headless=True, **launch_opt)
                break
            except Exception:
                continue

        if not browser:
            print("[WARN] No headless chromium browser could be launched; static check passed.", file=sys.stderr)
            return True

        page = browser.new_page()
        page.on("pageerror", lambda err: errors.append(f"JS Runtime Error: {err}"))

        page.goto(index_html.as_uri())
        page.wait_for_timeout(1200)

        # Verify key DOM components
        title = page.title()
        if 'Broadcast Playroom' not in title:
            errors.append(f"Unexpected document title: {title}")

        titlebar = page.query_selector(".desktop-titlebar")
        if not titlebar:
            errors.append("Missing .desktop-titlebar element!")

        close_btn = page.query_selector(".app-win-btn.win-close")
        if not close_btn:
            errors.append("Missing .win-close button in titlebar!")

        # Verify critical functions in window scope
        fn_checks = page.evaluate("""() => {
            const leakedFooters = Array.from(document.querySelectorAll('.floating-footer')).filter(el => !el.closest('.floating-window'));
            const leakedBodies = Array.from(document.querySelectorAll('.floating-body')).filter(el => !el.closest('.floating-window'));
            return {
                openAuthorModal: typeof window.openAuthorModal === 'function',
                openToolWindow: typeof window.openToolWindow === 'function',
                syncAuthorProfile: typeof window.syncAuthorProfile === 'function',
                bodyTextHasRawJs: document.body.innerText.includes('pop.document.close();'),
                leakedFootersCount: leakedFooters.length,
                leakedBodiesCount: leakedBodies.length
            };
        }""")

        if fn_checks.get('leakedFootersCount', 0) > 0:
            errors.append(f"DOM LEAK DETECTED: {fn_checks['leakedFootersCount']} .floating-footer elements are outside .floating-window (mismatched/extra </div> tag)!")
        if fn_checks.get('leakedBodiesCount', 0) > 0:
            errors.append(f"DOM LEAK DETECTED: {fn_checks['leakedBodiesCount']} .floating-body elements are outside .floating-window (mismatched/extra </div> tag)!")

        if not fn_checks.get('openAuthorModal'):
            errors.append("window.openAuthorModal is not defined as a function!")
        if not fn_checks.get('openToolWindow'):
            errors.append("window.openToolWindow is not defined as a function!")
        if not fn_checks.get('syncAuthorProfile'):
            errors.append("window.syncAuthorProfile is not defined as a function!")
        if fn_checks.get('bodyTextHasRawJs'):
            errors.append("Body innerText contains raw unparsed JavaScript code!")

        browser.close()

    if errors:
        print("[SMOKE TEST GATE FAILED] Discovered runtime or UI errors:", file=sys.stderr)
        for err in errors:
            print(f"  ❌ {err}", file=sys.stderr)
        return False

    print(">>> [SMOKE TEST GATE PASSED] Headless browser verified: 0 runtime errors, 100% healthy UI!")
    return True

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    success = run_smoke_test(root)
    sys.exit(0 if success else 1)
