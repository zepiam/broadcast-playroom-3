# -*- coding: utf-8 -*-
js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'
with open(js_path, 'r', encoding='utf-8') as f:
    code = f.read()

if not code.strip().startswith('(function'):
    code = "(function () {\n  'use strict';\n\n" + code
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added IIFE header to composer_studio.js")
else:
    print("IIFE header already present")
