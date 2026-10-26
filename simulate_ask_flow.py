from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('file:///E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html')
    
    # 1. Open ask window (docked or popout)
    page.evaluate("openToolWindow('ask')")
    
    # Let's inspect the UI state
    print("Initial state:")
    s1 = page.evaluate("""() => ({
        phase: window._askPollState?.phase,
        footerIdle: document.getElementById('askFooterIdle')?.style.display,
        footerVoting: document.getElementById('askFooterVoting')?.style.display,
        footerEnded: document.getElementById('askFooterEnded')?.style.display,
        qDisabled: document.getElementById('askQuestion')?.disabled
    })""")
    print("  State 1 (Idle):", s1)
    
    # Start poll
    print("\nCalling startAskPoll()...")
    page.evaluate("startAskPoll()")
    s2 = page.evaluate("""() => ({
        phase: window._askPollState?.phase,
        footerIdle: document.getElementById('askFooterIdle')?.style.display,
        footerVoting: document.getElementById('askFooterVoting')?.style.display,
        footerEnded: document.getElementById('askFooterEnded')?.style.display,
        qDisabled: document.getElementById('askQuestion')?.disabled
    })""")
    print("  State 2 (Voting):", s2)
    
    # End poll
    print("\nCalling endAskPoll()...")
    page.evaluate("endAskPoll()")
    s3 = page.evaluate("""() => ({
        phase: window._askPollState?.phase,
        footerIdle: document.getElementById('askFooterIdle')?.style.display,
        footerVoting: document.getElementById('askFooterVoting')?.style.display,
        footerEnded: document.getElementById('askFooterEnded')?.style.display,
        qDisabled: document.getElementById('askQuestion')?.disabled
    })""")
    print("  State 3 (Ended):", s3)
    
    # Close overlay
    print("\nCalling closeAskOverlay()...")
    page.evaluate("closeAskOverlay()")
    s4 = page.evaluate("""() => ({
        phase: window._askPollState?.phase,
        liveAskState: window._liveAskState,
        footerIdle: document.getElementById('askFooterIdle')?.style.display,
        footerVoting: document.getElementById('askFooterVoting')?.style.display,
        footerEnded: document.getElementById('askFooterEnded')?.style.display,
        qDisabled: document.getElementById('askQuestion')?.disabled
    })""")
    print("  State 4 (Closed):", s4)
    
    # Now user tries to start new poll again:
    print("\nCalling startAskPoll() again for new poll...")
    page.evaluate("startAskPoll()")
    s5 = page.evaluate("""() => ({
        phase: window._askPollState?.phase,
        footerIdle: document.getElementById('askFooterIdle')?.style.display,
        footerVoting: document.getElementById('askFooterVoting')?.style.display,
        footerEnded: document.getElementById('askFooterEnded')?.style.display,
        qDisabled: document.getElementById('askQuestion')?.disabled
    })""")
    print("  State 5 (Restarted):", s5)
    
    browser.close()
