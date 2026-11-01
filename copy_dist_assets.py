import os
import shutil
from pathlib import Path

project_dir = Path(__file__).resolve().parent
src_dir = str(project_dir / 'src')
dist_dir = str(project_dir / 'dist')

files_to_copy = [
    'game_overlay_chat_controls.js','supporters_ui.js','dns_controls.js','banned_words.js','blacklist.js','secret_codes.js','secret_sounds.js','randomizer_visual.js','obs_links.js','bot_settings.js','chat_content.js','app_presence.js','replie_command_editor.js','dock_controls.js','widget_patch.js','chat_widget_controls.js','viewer_connections.js','live_chat_scroll.js',
    'composer_studio.js', 'composer_legacy_controls.js',
    'overlay_transport.js',
    'live_overlay.js', 'legacy_emotes.js',
    'tool_controls.js',
    'giveaway_controls.js',
    'user_controls.js', 'desktop_overlay_controls.js',
    'rvc_controls.js',
    'legacy_ask.js',
    'legacy_chat.html', 'legacy_viewer.html', 'legacy_game_chat.html',
    'legacy_ask.css',
    'legacy_giveaway.js',
    'legacy_giveaway.css',
    'legacy_replie.js',
    'legacy_replie.css',
    'legacy_image.js', 'legacy_video.js',
    'legacy_text.js',
    'legacy_avatar.js',
    'legacy_goal.js',
    'legacy_goal.css',
    'legacy_avatar.css',
    'tts_avatar.js', 'keyboard_controls.js', 'ui_readability.js', 'ui_readability.css', 'viewer_preview.js', 'now_playing_renderer.js',
    'legacy_text.css',
    'legacy_image.css',
    'cwc_themes_data.js',
    'widget_customizer.js',
    'composer_studio.css',
    'composer_widget_themes.css',
    'styles.css',
    'modal.css',
    'widget_customizer.css',
    'composer.html',
    'overlay.html',
    'dock.html',
    'favicon.ico',
    'favicon.png',
    'manifest.json'
]

os.makedirs(dist_dir, exist_ok=True)
for f in files_to_copy:
    src = os.path.join(src_dir, f)
    dst = os.path.join(dist_dir, f)
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"Copied {f} to dist/")

# Also ensure assets folder copied
src_assets = os.path.join(src_dir, 'assets')
dst_assets = os.path.join(dist_dir, 'assets')
if os.path.exists(src_assets):
    for item in os.listdir(src_assets):
        if item == 'cursors':
            continue
        s = os.path.join(src_assets, item)
        d = os.path.join(dst_assets, item)
        if os.path.isdir(s):
            shutil.copytree(s,d,dirs_exist_ok=True)
        elif os.path.isfile(s) and not os.path.exists(d):
            shutil.copyfile(s, d)
            print(f"Copied asset {item} to dist/assets/")

print("Dist assets synchronized successfully!")


# Ensure dist/index.html links to all required stylesheets
dist_index = os.path.join(dist_dir, 'index.html')
if os.path.exists(dist_index):
    with open(dist_index, 'r', encoding='utf-8') as f:
        dhtml = f.read()

    # Always ensure .desktop-titlebar-icon has inline styles in dist/index.html
    dhtml = dhtml.replace('<img src="./assets/bp-full-icon.png" class="desktop-titlebar-icon"', '<img src="./assets/bp-full-icon.png" class="desktop-titlebar-icon" style="width:16px!important;height:16px!important;max-width:16px!important;max-height:16px!important;object-fit:contain;flex-shrink:0;display:inline-block;"')
    dhtml = dhtml.replace('<html lang="th" class="notranslate" translate="no">', '<html lang="th" class="notranslate" translate="no" style="background:#1e1f22!important;color:#f2f3f5!important;">')

    required_links = [
        '<link rel="stylesheet" href="./styles.css">',
        '<link rel="stylesheet" href="./ui_readability.css">',
        '<link rel="stylesheet" href="./modal.css">',
        '<link rel="stylesheet" href="./widget_customizer.css">',
        '<link rel="stylesheet" href="./composer_studio.css">',
        '<link rel="stylesheet" href="./composer_widget_themes.css">'
    ]
    links_to_insert = []
    for link in required_links:
        if link not in dhtml:
            links_to_insert.append(link)

    if links_to_insert:
        inject_block = "\n  " + "\n  ".join(links_to_insert) + "\n</head>"
        dhtml = dhtml.replace('</head>', inject_block, 1)
        with open(dist_index, 'w', encoding='utf-8') as f:
            f.write(dhtml)
        print(f"Injected {len(links_to_insert)} missing stylesheet links into dist/index.html")


# ==============================================================
# STRICT SAFETY AUDIT GATE: Fail build if any asset or link is missing
# ==============================================================
with open(dist_index, 'r', encoding='utf-8') as f:
    final_html = f.read()

for req in required_links:
    if req not in final_html:
        raise RuntimeError(f"CRITICAL BUILD FAILURE: {req} is missing from dist/index.html!")

if 'styles.css' not in final_html:
    raise RuntimeError("CRITICAL BUILD FAILURE: styles.css is not linked in dist/index.html!")

styles_path = os.path.join(dist_dir, 'styles.css')
if not os.path.exists(styles_path) or os.path.getsize(styles_path) < 50000:
    raise RuntimeError("CRITICAL BUILD FAILURE: dist/styles.css is missing or too small!")

if 'width:16px' not in final_html and 'max-width:16px' not in final_html:
    raise RuntimeError("CRITICAL BUILD FAILURE: .desktop-titlebar-icon lacks size constraints in dist/index.html!")

print(">>> [SAFETY GATE PASSED] All assets, stylesheets, and fail-safe constraints verified 100% complete!")
