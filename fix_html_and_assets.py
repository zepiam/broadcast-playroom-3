import os

# 1. Update src/index.html
with open('src/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Inline style on desktop-titlebar-icon
target_icon = '<img src="./assets/bp-full-icon.png" class="desktop-titlebar-icon"'
replacement_icon = '<img src="./assets/bp-full-icon.png" class="desktop-titlebar-icon" style="width:16px!important;height:16px!important;max-width:16px!important;max-height:16px!important;object-fit:contain;flex-shrink:0;display:inline-block;"'

if target_icon in html and 'width:16px!important' not in html:
    html = html.replace(target_icon, replacement_icon)
    print("Injected inline styles into .desktop-titlebar-icon in src/index.html")

# Ensure html/body have dark background directly
if '<html lang="th" class="notranslate" translate="no">' in html:
    html = html.replace('<html lang="th" class="notranslate" translate="no">', '<html lang="th" class="notranslate" translate="no" style="background:#1e1f22!important;color:#f2f3f5!important;">')
    print("Injected dark background into <html> in src/index.html")

with open('src/index.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 2. Update copy_dist_assets.py to always inject required stylesheets into dist/index.html
with open('copy_dist_assets.py', 'r', encoding='utf-8') as f:
    copy_script = f.read()

injection_logic = '''
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
        inject_block = "\\n  " + "\\n  ".join(links_to_insert) + "\\n</head>"
        dhtml = dhtml.replace('</head>', inject_block, 1)
        with open(dist_index, 'w', encoding='utf-8') as f:
            f.write(dhtml)
        print(f"Injected {len(links_to_insert)} missing stylesheet links into dist/index.html")
'''

if "Ensure dist/index.html links to all required stylesheets" not in copy_script:
    copy_script += "\n" + injection_logic
    with open('copy_dist_assets.py', 'w', encoding='utf-8') as f:
        f.write(copy_script)
    print("copy_dist_assets.py updated with stylesheet injection logic")
