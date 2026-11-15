@echo off
chcp 65001 >nul
title Broadcast Playroom 3 - Release Manager
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] ไม่พบ Python ในระบบ กรุณาตรวจสอบ PATH
    pause
    exit /b 1
)

python run_release.py %*
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)
