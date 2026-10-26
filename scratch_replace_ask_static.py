import sys
sys.stdout.reconfigure(encoding='utf-8')
html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_start = text.find('<!-- Live Preview Bar Graph -->')
target_end = text.find('<!-- TAB 2: หน้าตา OVERLAY', target_start)

assert target_start != -1 and target_end != -1, "Target preview block not found"

new_preview_block = """<!-- Live Preview Bar Graph -->
        <div class="section-card">
          <div class="section-card-title">
            <span>📊 ตัวอย่างแท่งคะแนนโหวตสด</span>
            <span style="font-size: 11px; color: #34d399;" id="lblAskTotalVotes">ยอดโหวตรวม: 0 โหวต</span>
          </div>
          <div id="askLiveGraphContainer" style="display:flex; flex-direction:column; gap:8px;">
            <!-- Populated dynamically by emitAskState() -->
          </div>
        </div>

      </div>

      """

text = text[:target_start] + new_preview_block + text[target_end:]

# Call emitAskState on DOMContentLoaded so initial 0-vote state renders
dom_load_idx = text.find('window.addEventListener(\'DOMContentLoaded\', () => {')
if dom_load_idx != -1:
    init_call = 'emitAskState();\n      '
    text = text[:dom_load_idx + 49] + init_call + text[dom_load_idx + 49:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced static ASK preview with dynamic container and hooked DOMContentLoaded initialization.")
