import os

composer_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js"

with open(composer_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace window.composerStudioState with window.ComposerStudio?.getActivePage?.()
old_snippet = """    const curPage = window.composerStudioState?.pages?.[window.composerStudioState.activePageIndex];"""
new_snippet = """    const curPage = window.ComposerStudio?.getActivePage?.() || window.ComposerStudio?.state?.pages?.[window.ComposerStudio?.state?.activePageIndex];"""

code = code.replace(old_snippet, new_snippet)

with open(composer_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated composer_studio.js bus listener with window.ComposerStudio!")
