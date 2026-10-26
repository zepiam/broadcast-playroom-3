import os

composer_path = r"E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js"

with open(composer_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix playroom title class and stage initial display
code = code.replace(
    """<div id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#c084fc; margin-bottom:4px;">""",
    """<div class="playroom-clip-title" id="compPlayroomTitle_${w.id}" style="font-size:16px; font-weight:800; color:#c084fc; margin-bottom:4px;">"""
)

# Fix stage display:none so it doesn't have duplicate display:flex in initial style
code = code.replace(
    """<div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; position:absolute; inset:0; z-index:10; display:flex; flex-direction:column; align-items:center; justify-content:center;">""",
    """<div class="playroom-stage" id="compPlayroomStage_${w.id}" style="display:none; width:100%; height:100%; position:absolute; inset:0; z-index:10; flex-direction:column; align-items:center; justify-content:center;">"""
)

with open(composer_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed playroom title class and stage display in composer_studio.js!")
