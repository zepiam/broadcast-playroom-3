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
    'tts_avatar.js', 'ragnarok_cursor_skin.js', 'keyboard_controls.js', 'ui_readability.js', 'ui_readability.css', 'viewer_preview.js', 'now_playing_renderer.js',
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
        s = os.path.join(src_assets, item)
        d = os.path.join(dst_assets, item)
        if os.path.isdir(s):
            shutil.copytree(s,d,dirs_exist_ok=True)
        elif os.path.isfile(s) and not os.path.exists(d):
            shutil.copyfile(s, d)
            print(f"Copied asset {item} to dist/assets/")

print("Dist assets synchronized successfully!")
