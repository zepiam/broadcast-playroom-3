@echo off
setlocal
title Broadcast Playroom 3 - Release Manager (Full + Local Sync)
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    pause
    exit /b 1
)

python run_release.py --sync-local %*
if errorlevel 1 (
    pause
    exit /b %errorlevel%
)
endlocal
