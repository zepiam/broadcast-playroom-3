@echo off
title Broadcast Playroom 3 (Dev Mode)
cd /d "%~dp0"

set "PY=python"
where python >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    )
)

echo [INFO] Starting Broadcast Playroom 3 Dev Mode...

"%PY%" -u launch_dev.py

if errorlevel 1 (
    echo.
    echo [ERROR] An error occurred while launching.
    pause
)
