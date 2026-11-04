path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

insertion = """
<style id="nativeTitlebarEnforcement">
  #desktopTitlebar,
  .desktop-titlebar,
  #appWindowResizers,
  .app-window-resizers,
  #snapLayoutsFlyout,
  .snap-layouts-flyout {
    display: none !important;
  }
</style>
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
"""

for i, l in enumerate(lines):
    if "</head>" in l:
        lines.insert(i, insertion)
        break

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("src/index.html updated successfully at line", i)
