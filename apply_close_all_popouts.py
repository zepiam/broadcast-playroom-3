import sys

sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update the script inside popoutToolWindow to include the parent heartbeat, BroadcastChannel, and storage listeners
old_pop_script = text.find('if (window.opener) {\n      window.switchSettingsSection = function(id) {')
assert old_pop_script != -1, "old_pop_script not found"

new_pop_child_script = """// 1. Auto-close when main window (opener) is closed or disconnected
    const _parentHeartbeat = setInterval(() => {
      try {
        if (!window.opener || window.opener.closed) {
          clearInterval(_parentHeartbeat);
          window.close();
        }
      } catch (e) {
        clearInterval(_parentHeartbeat);
        window.close();
      }
    }, 200);

    // 2. Storage event listener for broadcast shutdown signal
    window.addEventListener('storage', (e) => {
      if (e.key === 'bp3_app_shutdown_signal') {
        window.close();
      }
    });

    // 3. BroadcastChannel listener for instant shutdown
    try {
      const _bc = new BroadcastChannel('bp3_app_bus');
      _bc.onmessage = (e) => {
        if (e.data && e.data.type === 'SHUTDOWN_ALL') {
          window.close();
        }
      };
    } catch (e) {}

    if (window.opener) {
      window.switchSettingsSection = function(id) {"""

text = text[:old_pop_script] + new_pop_child_script + text[old_pop_script + len('if (window.opener) {\n      window.switchSettingsSection = function(id) {'):]
print("Injected auto-close heartbeat & shutdown listeners into popout child windows.")

# 2. Add closeAllPopoutWindows function and listeners to parent window
old_dock_tool = text.find('function dockToolWindow(name) {')
assert old_dock_tool != -1, "dockToolWindow not found"

parent_close_handler = """function closeAllPopoutWindows() {
      // 1. Broadcast shutdown signal via BroadcastChannel
      try {
        const bc = new BroadcastChannel('bp3_app_bus');
        bc.postMessage({ type: 'SHUTDOWN_ALL' });
      } catch (e) {}

      // 2. Broadcast via localStorage storage event
      try {
        localStorage.setItem('bp3_app_shutdown_signal', Date.now().toString());
      } catch (e) {}

      // 3. Directly close all tracked popout windows
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

    // Auto-close all child windows when parent window closes or navigates
    window.addEventListener('beforeunload', closeAllPopoutWindows);
    window.addEventListener('unload', closeAllPopoutWindows);
    window.addEventListener('pagehide', closeAllPopoutWindows);

    // Tauri window close requested event
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

text = text[:old_dock_tool] + parent_close_handler + text[old_dock_tool:]
print("Added closeAllPopoutWindows and lifecycle listeners in parent window.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved updated src/index.html successfully.")
