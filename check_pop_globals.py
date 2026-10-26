from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('file:///E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html')
    
    with page.expect_popup() as pop_info:
        page.evaluate("popoutToolWindow('ask')")
    pop = pop_info.value
    pop.wait_for_load_state("domcontentloaded")
    
    bp3_bus_in_page = page.evaluate("typeof window.BP3_BUS")
    bp3_bus_in_pop = pop.evaluate("typeof window.BP3_BUS")
    ask_state_in_page = page.evaluate("typeof window._askPollState")
    ask_state_in_pop = pop.evaluate("typeof window._askPollState")
    
    print(f"window.BP3_BUS in main page: {bp3_bus_in_page}")
    print(f"window.BP3_BUS in popout: {bp3_bus_in_pop}")
    print(f"window._askPollState in main page: {ask_state_in_page}")
    print(f"window._askPollState in popout: {ask_state_in_pop}")
    
    browser.close()
