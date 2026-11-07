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

rem Dev mode serves the files in src\ directly, so edits show up without running a build.
set "BP3_DEV_SERVE_SRC=1"

echo [INFO] Starting Broadcast Playroom 3 Dev Mode...

"%PY%" -u launch_dev.py

if errorlevel 1 (
    echo.
    echo [ERROR] An error occurred while launching.
    pause
) else (
    echo.
    echo [INFO] Broadcast Playroom 3 session ended.
    pause
)
