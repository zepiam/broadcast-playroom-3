@echo off
setlocal
cd /d "%~dp0"
title Broadcast Playroom 3 - FindUpdate

echo ================================================================
echo   Broadcast Playroom 3 - FindUpdate ^& System Repair
echo ================================================================
echo.

if exist "BroadcastPlayroom3-Full.exe" (
    "BroadcastPlayroom3-Full.exe" --findupdate
    goto done
)

if exist "BroadcastPlayroom3-Lite.exe" (
    "BroadcastPlayroom3-Lite.exe" --findupdate
    goto done
)

if exist "_internal\BroadcastPlayroom3-Full.exe" (
    "_internal\BroadcastPlayroom3-Full.exe" --findupdate
    goto done
)

if exist "_internal\BroadcastPlayroom3-Lite.exe" (
    "_internal\BroadcastPlayroom3-Lite.exe" --findupdate
    goto done
)

if exist "python.exe" (
    "python.exe" findupdate.py
    goto done
)

if exist "_internal\python.exe" (
    "_internal\python.exe" findupdate.py
    goto done
)

python findupdate.py

:done
if %errorlevel% neq 0 (
    echo.
    pause
)
