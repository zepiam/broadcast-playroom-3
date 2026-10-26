import os
import re

files_to_patch = [
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/dock.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/dock.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer.html',
    'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer.html',
]

meta_tags = """  <meta name="google" content="notranslate">
  <meta name="googlebot" content="notranslate">"""

for file_path in files_to_patch:
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Patch <html ...>
    content = re.sub(r'<html\b([^>]*)>', r'<html\1 class="notranslate" translate="no">', content, count=1)
    content = content.replace('class="notranslate" translate="no" class="notranslate" translate="no"', 'class="notranslate" translate="no"')

    # 2. Add meta tags in <head>
    if 'name="google" content="notranslate"' not in content:
        content = re.sub(r'(<head[^>]*>)', r'\1\n' + meta_tags, content, count=1)

    # 3. Patch <body ...>
    if 'translate="no"' not in content[content.find('<body'):content.find('<body')+100]:
        content = re.sub(r'<body\b([^>]*)>', r'<body\1 translate="no" class="notranslate">', content, count=1)

    # 4. Remove crossorigin from stylesheet links for file:// compatibility
    content = content.replace('<link rel="stylesheet" crossorigin href="./assets/', '<link rel="stylesheet" href="./assets/')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Patched translate-block on: {file_path}")

# Sync static js and css files from src to dist
src_dir = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src'
dist_dir = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist'
import shutil
for js_file in ['cwc_themes_data.js', 'widget_customizer.js', 'composer_studio.js', 'composer_studio.css', 'styles.css', 'modal.css', 'widget_customizer.css']:
    s = os.path.join(src_dir, js_file)
    d = os.path.join(dist_dir, js_file)
    if os.path.exists(s):
        shutil.copy2(s, d)
        print(f"Synced {js_file} to dist/")

print("All HTML files patched to strictly forbid translation & crossorigin fixed!")
