@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===== Release Broadcast Playroom v3.62 =====
where python >nul 2>nul || (echo [ERROR] ไม่พบ python & pause & exit /b 1)
where npm >nul 2>nul || (echo [ERROR] ไม่พบ npm & pause & exit /b 1)
gh auth status >nul 2>nul || (echo [ERROR] ยังไม่ได้ล็อกอิน GitHub: รัน gh auth login ก่อน & pause & exit /b 1)
python -c "import huggingface_hub" >nul 2>nul || (echo กำลังติดตั้ง huggingface_hub... & pip install huggingface_hub)
echo.
echo กำลังเริ่ม release ห้ามปิดหน้าต่างนี้จนกว่าจะเสร็จ
python publish_release_v362.py
echo.
if errorlevel 1 (echo [FAILED] มีข้อผิดพลาด ห้ามรันซ้ำ ส่งข้อความด้านบนให้ผู้ช่วยดูก่อน) else (echo [DONE] release เสร็จเรียบร้อย)
pause
