import subprocess, shutil, os

base = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3"
dist = os.path.join(base, "dist")
src = os.path.join(base, "src")

# Run vite build
print("Running npm run build...")
res = subprocess.run(["npm.cmd", "run", "build"], cwd=base, capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print("Build error:", res.stderr)

# Copy runtime files
for fn in ["widget_customizer.css", "widget_customizer.js", "cwc_themes_data.js", "composer_studio.css", "composer_studio.js"]:
    src_fp = os.path.join(src, fn)
    dst_fp = os.path.join(dist, fn)
    if os.path.exists(src_fp):
        shutil.copy2(src_fp, dst_fp)
        print(f"Copied {fn} to dist")

# Copy platform assets
plat_src = os.path.join(src, "assets", "platforms")
plat_dist = os.path.join(dist, "assets", "platforms")
os.makedirs(plat_dist, exist_ok=True)
if os.path.exists(plat_src):
    for f in os.listdir(plat_src):
        shutil.copy2(os.path.join(plat_src, f), os.path.join(plat_dist, f))
        shutil.copy2(os.path.join(plat_src, f), os.path.join(dist, "assets", f))
    print("Copied platform assets to dist")

# Strip crossorigin from dist/index.html
idx_path = os.path.join(dist, "index.html")
if os.path.exists(idx_path):
    with open(idx_path, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace(' crossorigin', '')
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Stripped crossorigin from dist/index.html")

print("Build & copy complete!")
