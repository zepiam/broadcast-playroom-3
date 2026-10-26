# -*- coding: utf-8 -*-
"""
Builds the complete, enhanced src/composer_studio.js
"""
import os
import re

out_js_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\composer_studio.js'

# Read the current composer_studio.js to inspect functions and variables
with open(out_js_path, 'r', encoding='utf-8') as f:
    current_js = f.read()

print("Current JS length:", len(current_js))
