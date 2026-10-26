import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = 'window.dockBackToolWindow = dockBackToolWindow;'
assert target in text, "dockBackToolWindow assignment not found"

# Replace duplicate assignment if present
if 'window.dockBackToolWindow = dockBackToolWindow;\n    window.dockBackToolWindow = dockBackToolWindow;' in text:
    text = text.replace('window.dockBackToolWindow = dockBackToolWindow;\n    window.dockBackToolWindow = dockBackToolWindow;', 'window.dockBackToolWindow = dockBackToolWindow;')

close_all_code = """
    // ==============================================================================
    // AUTO-CLOSE ALL CHILD / POPOUT WINDOWS WHEN MAIN WINDOW CLOSES
    // ==============================================================================
    function closeAllPopoutWindows() {
      // 1. Broadcast shutdown signal via BroadcastChannel
      try {
        const bc = new BroadcastChannel('bp3_app_bus');
        bc.postMessage({ type: 'SHUTDOWN_ALL' });
      } catch (e) {}

      // 2. Broadcast shutdown signal via localStorage storage event
      try {
        localStorage.setItem('bp3_app_shutdown_signal', Date.now().toString());
      } catch (e) {}

      // 3. Directly close all popout windows tracked in window._popoutWindows
      if (window._popoutWindows) {
        for (const [name, pop] of Object.entries(window._popoutWindows)) {
          if (pop && !pop.closed) {
            try {
              pop.close();
            } catch (e) {}
          }
        }
        window._popoutWindows = {};
      }
    }
    window.closeAllPopoutWindows = closeAllPopoutWindows;

    // Listen to standard browser and Webview unload lifecycle events
    window.addEventListener('beforeunload', closeAllPopoutWindows);
    window.addEventListener('unload', closeAllPopoutWindows);
    window.addEventListener('pagehide', closeAllPopoutWindows);

    // Listen to native Tauri close-requested event
    if (window.__TAURI__ && window.__TAURI__.window) {
      try {
        const curWin = window.__TAURI__.window.getCurrentWindow();
        if (curWin && curWin.listen) {
          curWin.listen('tauri://close-requested', async () => {
            closeAllPopoutWindows();
          });
        }
        if (curWin && curWin.onCloseRequested) {
          curWin.onCloseRequested(async () => {
            closeAllPopoutWindows();
          });
        }
      } catch (e) {}
    }
"""

text = text.replace('window.dockBackToolWindow = dockBackToolWindow;', 'window.dockBackToolWindow = dockBackToolWindow;\n' + close_all_code, 1)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Inserted closeAllPopoutWindows and lifecycle handlers successfully.")
