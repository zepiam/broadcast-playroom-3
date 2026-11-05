from pathlib import Path

p = Path(r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html")
text = p.read_text(encoding="utf-8")

# Remove mistaken showFastUpdateModal from start of checkAppUpdate
mistake = "if (manual) {\n            showFastUpdateModal();\n\n\n\n        if (btn) {"
correct_start = "if (manual) {\n\n\n\n        if (btn) {"
if mistake in text:
    text = text.replace(mistake, correct_start, 1)
    print("[OK] Removed premature modal call from start of checkAppUpdate.")

# Add showFastUpdateModal inside data.has_update block
old_has_update_manual = """if (manual) {



            showToast(`🎉 พบเวอร์ชันใหม่"""

# Let's search by finding "data.has_update" and then "if (manual)"
idx_has = text.find("if (data.has_update) {")
if idx_has != -1:
    idx_man = text.find("if (manual) {", idx_has)
    # Check if showFastUpdateModal() is already right after
    after_chunk = text[idx_man:idx_man+50]
    if "showFastUpdateModal();" not in after_chunk:
        text = text[:idx_man] + "if (manual) {\n            showFastUpdateModal();\n" + text[idx_man+len("if (manual) {\n"):]
        print("[OK] Added showFastUpdateModal() inside data.has_update branch.")

p.write_text(text, encoding="utf-8")
print("[OK] Finished updating index.html")
