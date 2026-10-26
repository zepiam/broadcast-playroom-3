import re

js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect where renderWidgetInnerHtml starts and where getWidgetIcon starts
idx_inner_start = code.find('function renderWidgetInnerHtml(w) {')
idx_get_icon = code.find('function getWidgetIcon(type) {')

print("idx_inner_start:", idx_inner_start)
print("idx_get_icon:", idx_get_icon)

# Let's inspect where renderWidgetCustomizerPanel starts and ends
idx_cust_start = code.find('function renderWidgetCustomizerPanel(id) {')
idx_toolbar_bind = code.find("// Add Widget Buttons", idx_cust_start)
print("idx_cust_start:", idx_cust_start)
print("idx_toolbar_bind:", idx_toolbar_bind)
