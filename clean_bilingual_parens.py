# -*- coding: utf-8 -*-
import re

html_path = r'E:\DOCS\Documents\AI TOOLS\broadcast playroom 3\src\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

replacements = [
    ('เลือกตำแหน่งหลักบนหน้าจอ (9-Grid Position)', 'เลือกตำแหน่งหลักบนหน้าจอ 9 ทิศทาง'),
    ('จัดการรายชื่อคนดู (User Manager)', 'จัดการรายชื่อคนดู'),
    ('การตั้งค่าระบบ (System Settings)', 'การตั้งค่าระบบ'),
    ('ปิดเสียงอ่านโค้ดลับ (Secret Code Muted)', 'ปิดเสียงอ่านโค้ดลับ'),
    ('เปิดระบบอ่านออกเสียงแชท (Master TTS)', 'เปิดระบบอ่านออกเสียงแชท'),
    ('เปิดแถบแสดงกิจกรรมสด (Event List)', 'เปิดแถบแสดงกิจกรรมสด'),
    ('แสดงกรอบ (Edit Mode)', 'แสดงกรอบปรับแต่ง'),
    ('(Edit Mode)', 'โหมดปรับแต่ง')
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"Replaced: {old} -> {new}")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Cleaned index.html")
