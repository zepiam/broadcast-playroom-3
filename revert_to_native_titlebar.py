import os
import sys
import re

BASE_DIR = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"

# 1. Update launch_dev.py
launch_dev_path = os.path.join(BASE_DIR, "launch_dev.py")
with open(launch_dev_path, "r", encoding="utf-8") as f:
    ld = f.read()

# Change frameless=True to frameless=False in webview.create_window
ld = re.sub(r'frameless\s*=\s*True', 'frameless=False', ld)
ld = re.sub(r'easy_drag\s*=\s*True', 'easy_drag=False', ld)

# Disable setup_discord_frame call
old_discord_call = '''                    setup_app_window_icon(h)
                    from app_window_frame import setup_discord_frame
                    setup_discord_frame(h)'''
new_discord_call = '''                    setup_app_window_icon(h)
                    # Native Windows title bar retained (no discord frameless strip)'''

if old_discord_call in ld:
    ld = ld.replace(old_discord_call, new_discord_call)
    print("Disabled setup_discord_frame in launch_dev.py")
else:
    # Try regex in case of slight whitespace
    ld = re.sub(r'setup_app_window_icon\(h\)\s*from app_window_frame import setup_discord_frame\s*setup_discord_frame\(h\)',
                'setup_app_window_icon(h)\n                    # Native Windows title bar retained', ld)
    print("Replaced setup_discord_frame via regex")

with open(launch_dev_path, "w", encoding="utf-8") as f:
    f.write(ld)
print("launch_dev.py updated successfully!")

# 2. Update src/styles.css to hide custom desktop-titlebar and resizers completely
styles_path = os.path.join(BASE_DIR, "src", "styles.css")
with open(styles_path, "r", encoding="utf-8") as f:
    css = f.read()

css_hide = '''
/* Revert to Native Windows Title Bar: Hide Custom Desktop Titlebar and Resizers */
#desktopTitlebar,
.desktop-titlebar,
#appWindowResizers,
.app-window-resizers,
#snapLayoutsFlyout,
.snap-layouts-flyout {
  display: none !important;
}
'''
if '#desktopTitlebar,' not in css:
    css += css_hide
    with open(styles_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("src/styles.css updated with titlebar hide rules!")

# 3. Update src/index.html & dist/index.html
reload_script = '''
<script>
// Global shortcut: Ctrl+R, Ctrl+Shift+R, F5 for instant reload & cache bust across all environments
window.addEventListener('keydown', (e) => {
  if ((e.ctrlKey && (e.key === 'r' || e.key === 'R')) || e.key === 'F5') {
    e.preventDefault();
    console.log('[BP3] Manual hard reload requested via keyboard shortcut');
    const url = new URL(window.location.href);
    url.searchParams.set('t', Date.now().toString());
    window.location.href = url.toString();
  }
});
</script>
'''

for html_rel in ["src/index.html", "dist/index.html"]:
    html_path = os.path.join(BASE_DIR, html_rel)
    if os.path.isfile(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            h = f.read()

        # Add titlebar hide style to head
        hide_style = '<style id="nativeTitlebarEnforcement">#desktopTitlebar, .desktop-titlebar, #appWindowResizers, .app-window-resizers, #snapLayoutsFlyout, .snap-layouts-flyout { display: none !important; }</style>'
        if 'id="nativeTitlebarEnforcement"' not in h:
            h = h.replace('</head>', f'{hide_style}\n</head>')

        # Add reload script to head
        if 'Manual hard reload requested' not in h:
            h = h.replace('</head>', f'{reload_script}\n</head>')

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(h)
        print(f"{html_rel} updated with native titlebar enforcement and Ctrl+R reload handler!")
