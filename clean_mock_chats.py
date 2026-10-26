import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

empty_state_html = """
        <!-- สถานะพร้อมรับแชทจริง -->
        <div id="chatEmptyState" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; min-height:280px; color:#949ba4; gap:12px; padding:30px; text-align:center;">
          <span style="font-size:38px; opacity:0.65;">💬</span>
          <div style="font-size:14px; font-weight:700; color:#e2e8f0;">พร้อมรับข้อความแชทสด</div>
          <div style="font-size:12px; color:#64748b; max-width:320px; line-height:1.5;">พิมพ์ชื่อแชนแนลแล้วคลิกปุ่ม <strong>"เชื่อมต่อ"</strong> ที่แพลตฟอร์มด้านซ้าย หรือเปิดหน้าต่าง <strong>ตั้งค่า &gt; ช่องทางสตรีม</strong> เพื่อเริ่มดึงแชทจริง</div>
        </div>
      """

for file_path in ['E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/src/index.html', 'E:/DOCS/Documents/AI TOOLS/broadcast playroom 3/dist/index.html']:
    with open(file_path, 'r', encoding='utf-8') as f:
        c = f.read()

    tag_str = 'id="chatList">'
    idx_start = c.find(tag_str)
    if idx_start == -1:
        print("Not found id=chatList in", file_path)
        continue
    
    idx_content_start = idx_start + len(tag_str)
    
    # Find next section: chat-input-bar
    idx_input_bar = c.find('class="chat-input-bar"', idx_content_start)
    if idx_input_bar == -1:
        idx_input_bar = c.find('chat-input-container', idx_content_start)
    
    idx_close = c.rfind('</div>', idx_content_start, idx_input_bar)
    print(f"In {file_path}: content length before: {idx_close - idx_content_start}")

    new_content = c[:idx_content_start] + empty_state_html + c[idx_close:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Cleaned mock chats successfully in:", file_path)
