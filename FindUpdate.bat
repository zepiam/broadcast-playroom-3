@echo off
chcp 65001 >nul
title Broadcast Playroom 3 - ตรวจสอบอัปเดตและซ่อมแซมระบบ (FindUpdate)
cd /d "%~dp0"

echo ================================================================
echo   Broadcast Playroom 3 - ตรวจสอบอัปเดตและซ่อมแซมระบบ (FindUpdate)
echo ================================================================
echo.

if exist "BroadcastPlayroom3-Full.exe" (
    "BroadcastPlayroom3-Full.exe" --findupdate
    goto end
)

if exist "BroadcastPlayroom3-Lite.exe" (
    "BroadcastPlayroom3-Lite.exe" --findupdate
    goto end
)

if exist "python.exe" (
    "python.exe" findupdate.py
    goto end
)

python findupdate.py

:end
if %errorlevel% neq 0 (
    echo.
    echo มีข้อผิดพลาดเกิดขึ้น กรุณากดปุ่มใดๆ เพื่อปิดหน้าต่าง...
    pause >nul
)
