from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('file:///E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html')
    
    # Check rows in main document before popout
    rows_before = page.evaluate("document.querySelectorAll('#askChoicesList .ask-choice-row').length")
    print(f"Rows in main document before popout: {rows_before}")
    
    # Pop out ASK window
    with page.expect_popup() as pop_info:
        page.evaluate("popoutToolWindow('ask')")
    pop = pop_info.value
    pop.wait_for_load_state("domcontentloaded")
    
    # Check rows in main document after popout
    rows_in_main_after = page.evaluate("document.querySelectorAll('#askChoicesList .ask-choice-row').length")
    print(f"Rows in main document after popout: {rows_in_main_after}")
    
    # Check rows in popup document
    rows_in_pop = pop.evaluate("document.querySelectorAll('#askChoicesList .ask-choice-row').length")
    print(f"Rows in popup document: {rows_in_pop}")
    
    # Try calling startAskPoll from popup
    res = pop.evaluate("""() => {
        try {
            startAskPoll();
            return { success: true, phase: window._askPollState?.phase };
        } catch(e) {
            return { error: String(e) };
        }
    }""")
    print(f"Calling startAskPoll from popout: {res}")
    
    browser.close()
