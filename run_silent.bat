@echo off
cd /d "%~dp0"

set "PYW=pythonw"
where pythonw >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe" (
        set "PYW=%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe"
    )
)

start "" "%PYW%" launch_dev.py
