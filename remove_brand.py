for p in ['E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html']:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    target = """      <div class="brand-badge">
        <img src="./assets/icon.png" alt="Logo" style="width: 24px; height: 24px; border-radius: 6px;">
        <span class="brand-name">Broadcast Playroom</span>
        <span class="brand-tag">v3.0.0</span>
      </div>

      <div class="topbar-divider"></div>"""

    if target in c:
        c = c.replace(target, '')
        print("Replaced exact target in", p)
    else:
        # fallback regex
        import re
        c = re.sub(r'\s*<div class="brand-badge">.*?</div>\s*<div class="topbar-divider"></div>', '', c, flags=re.DOTALL)
        print("Replaced via regex in", p)

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
