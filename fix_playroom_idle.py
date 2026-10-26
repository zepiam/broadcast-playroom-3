path = 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/composer_studio.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''          <!-- Idle Waiting Banner -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="background:rgba(15,23,42,0.85); border:1.5px dashed rgba(168,85,247,0.45); border-radius:14px; padding:14px 20px; text-align:center; color:#c084fc;">
            <div style="font-size:24px; margin-bottom:4px;">🎮</div>
            <div style="font-size:13px; font-weight:700;">Playroom Interactive Overlay</div>
            <div style="font-size:11px; color:#94a3b8; margin-top:2px;">รอคำสั่งจากแชทสด หรือยิงคลิปจากแผง Playroom Studio</div>
          </div>'''

replacement = '''          <!-- Idle Waiting Banner (Hidden on Standby) -->
          <div class="playroom-idle-banner" id="compPlayroomIdle_${w.id}" style="display:none !important;"></div>'''

if target in c:
    c = c.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    with open('E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/composer_studio.js', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Successfully hidden playroom idle banner!")
else:
    print("Warning: target not found!")
