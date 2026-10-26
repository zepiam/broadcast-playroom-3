import os
import shutil

src_dir = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src'
dist_dir = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist'

files_to_copy = [
    'composer_studio.js',
    'cwc_themes_data.js',
    'widget_customizer.js',
    'composer_studio.css',
    'composer_widget_themes.css',
    'styles.css',
    'modal.css',
    'widget_customizer.css',
    'composer.html',
    'overlay.html',
    'dock.html'
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
        if os.path.isfile(s) and not os.path.exists(d):
            shutil.copyfile(s, d)
            print(f"Copied asset {item} to dist/assets/")

print("Dist assets synchronized successfully!")
