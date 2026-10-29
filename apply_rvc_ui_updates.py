import pathlib

src_html = pathlib.Path(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html')
content = src_html.read_text(encoding='utf-8')

# 1. Insert CSS in <head>
css_to_insert = """
  <style id="rvc-badge-and-progress-styles">
    @keyframes bp3-rvc-lp-boil {
      0%   { transform: translate(0px, 0px) rotate(0deg); }
      25%  { transform: translate(-1px, 1px) rotate(-1deg); }
      50%  { transform: translate(1px, -1px) rotate(1deg); }
      75%  { transform: translate(-0.5px, -0.5px) rotate(-0.5deg); }
      100% { transform: translate(0px, 0px) rotate(0deg); }
    }
    @keyframes bp3-rvc-tx-hanging-sway {
      0%   { transform: rotate(0deg); }
      20%  { transform: rotate(8deg); }
      40%  { transform: rotate(-6deg); }
      60%  { transform: rotate(3deg); }
      80%  { transform: rotate(-1.5deg); }
      100% { transform: rotate(0deg); }
    }
    @keyframes rvc-shimmer {
      0% { background-position: -200% 0; }
      100% { background-position: 200% 0; }
    }
    .topbar-rvc-badge {
      display: inline-flex !important;
      align-items: center;
      gap: 6px;
      height: 28px;
      padding: 0 10px;
      border-radius: 6px;
      font-family: inherit;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      cursor: pointer;
      user-select: none;
      border: 1px solid rgba(255, 255, 255, 0.12);
      background: #1e1f22;
      color: #94a3b8;
      margin-left: 6px;
      transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
      contain: layout style;
      -webkit-app-region: no-drag;
    }
    .topbar-rvc-badge:hover {
      border-color: rgba(255, 255, 255, 0.28);
      background: #2b2d31;
    }
    .topbar-rvc-badge .rvc-badge-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background-color: #64748b;
      flex-shrink: 0;
      transition: background-color 0.2s ease, box-shadow 0.2s ease;
    }
    .topbar-rvc-badge.rvc-loading {
      background: rgba(245, 158, 11, 0.15) !important;
      border-color: rgba(245, 158, 11, 0.6) !important;
      color: #fbbf24 !important;
      animation: bp3-rvc-lp-boil 0.35s steps(3, end) infinite;
    }
    .topbar-rvc-badge.rvc-loading .rvc-badge-dot {
      background-color: #f59e0b !important;
      box-shadow: 0 0 8px #f59e0b;
    }
    .topbar-rvc-badge.rvc-ready {
      background: rgba(16, 185, 129, 0.15) !important;
      border-color: rgba(16, 185, 129, 0.55) !important;
      color: #34d399 !important;
      transform-origin: 50% 0%;
      animation: bp3-rvc-tx-hanging-sway 1.5s cubic-bezier(0.25, 1, 0.5, 1) 1 forwards;
    }
    .topbar-rvc-badge.rvc-ready .rvc-badge-dot {
      background-color: #10b981 !important;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
    }
    .topbar-rvc-badge.rvc-off {
      opacity: 0.65;
    }
  </style>
"""

if 'id="rvc-badge-and-progress-styles"' not in content:
    head_pos = content.find('</head>')
    content = content[:head_pos] + css_to_insert + content[head_pos:]
    print("Inserted CSS in <head>")

# 2. Insert Progress Box in secRvcVoiceCard
progress_box_sec = """
            <!-- หลอดแสดงสถานะและความคืบหน้าขณะโหลดโมเดล RVC เข้า GPU/RAM -->
            <div class="rvc-loading-progress-box" id="secRvcProgressBox" style="display: none; margin-top: 10px; padding: 10px 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span class="rvc-loading-msg" style="font-size: 11.5px; font-weight: 600; color: #fbbf24; display: flex; align-items: center; gap: 6px;">
                  <span class="rvc-loading-spinner">⏳</span>
                  <span class="rvc-loading-text">กำลังโหลดโมเดลเข้าหน่วยความจำ (GPU/RAM)...</span>
                </span>
                <span class="rvc-loading-pct" style="font-size: 11px; color: #94a3b8; font-weight: 600;">กรุณารอสักครู่</span>
              </div>
              <div class="rvc-progress-track" style="height: 6px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; position: relative;">
                <div class="rvc-progress-bar-fill" style="width: 100%; height: 100%; background: linear-gradient(90deg, #f59e0b, #eab308, #10b981); border-radius: 999px; animation: rvc-shimmer 1.5s infinite linear; background-size: 200% 100%;"></div>
              </div>
            </div>
"""

idx_sec = content.find('id="secRvcDeviceLabel"')
if idx_sec != -1 and 'id="secRvcProgressBox"' not in content:
    end_div = content.find('</div>', idx_sec) + len('</div>')
    content = content[:end_div] + progress_box_sec + content[end_div:]
    print("Inserted secRvcProgressBox")

# 3. Insert Progress Box in rvcVoiceCard
progress_box_win = """
        <!-- หลอดแสดงสถานะและความคืบหน้าขณะโหลดโมเดล RVC เข้า GPU/RAM -->
        <div class="rvc-loading-progress-box" id="winRvcProgressBox" style="display: none; margin-top: 10px; padding: 10px 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span class="rvc-loading-msg" style="font-size: 11.5px; font-weight: 600; color: #fbbf24; display: flex; align-items: center; gap: 6px;">
              <span class="rvc-loading-spinner">⏳</span>
              <span class="rvc-loading-text">กำลังโหลดโมเดลเข้าหน่วยความจำ (GPU/RAM)...</span>
            </span>
            <span class="rvc-loading-pct" style="font-size: 11px; color: #94a3b8; font-weight: 600;">กรุณารอสักครู่</span>
          </div>
          <div class="rvc-progress-track" style="height: 6px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; position: relative;">
            <div class="rvc-progress-bar-fill" style="width: 100%; height: 100%; background: linear-gradient(90deg, #f59e0b, #eab308, #10b981); border-radius: 999px; animation: rvc-shimmer 1.5s infinite linear; background-size: 200% 100%;"></div>
          </div>
        </div>
"""

idx_win = content.find('id="rvcDeviceLabel"')
if idx_win != -1 and 'id="winRvcProgressBox"' not in content:
    end_div = content.find('</div>', idx_win) + len('</div>')
    content = content[:end_div] + progress_box_win + content[end_div:]
    print("Inserted winRvcProgressBox")

src_html.write_text(content, encoding='utf-8')

# Also sync to dist/index.html
dist_html = pathlib.Path(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\dist\index.html')
dist_html.write_text(content, encoding='utf-8')
print("Synced to dist/index.html")

# Also sync to installed folder so user testing has it immediately
installed_dist = pathlib.Path(r'E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\dist\index.html')
if installed_dist.parent.exists():
    installed_dist.write_text(content, encoding='utf-8')
    print("Synced to installed BroadcastPlayroom3 full dist/index.html")

installed_js = pathlib.Path(r'E:\DOCS\Documents\BroadcastPlayroom3\full\_internal\dist\rvc_controls.js')
src_js = pathlib.Path(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\rvc_controls.js')
if installed_js.parent.exists() and src_js.exists():
    installed_js.write_text(src_js.read_text(encoding='utf-8'), encoding='utf-8')
    print("Synced rvc_controls.js to installed BroadcastPlayroom3 full dist")

# Sync rvc_controls.js to dist
dist_js = pathlib.Path(r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\dist\rvc_controls.js')
if src_js.exists():
    dist_js.write_text(src_js.read_text(encoding='utf-8'), encoding='utf-8')
    print("Synced rvc_controls.js to dist")

print("All updates applied cleanly!")
