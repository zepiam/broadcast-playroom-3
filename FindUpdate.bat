@echo off
setlocal
cd /d "%~dp0"
title Broadcast Playroom 3 - FindUpdate ^& System Repair

echo ================================================================
echo   Broadcast Playroom 3 - FindUpdate ^& System Repair
echo ================================================================
echo.

:: Try Python if available
if exist "python.exe" (
    "python.exe" findupdate.py
    if %errorlevel% equ 0 goto success
)

if exist "_internal\python.exe" (
    "_internal\python.exe" findupdate.py
    if %errorlevel% equ 0 goto success
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    python findupdate.py
    if %errorlevel% equ 0 goto success
)

:: If python is not available or failed, run standalone PowerShell updater
echo [INFO] Running Standalone System Repair & Updater...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Checking for latest version...' -ForegroundColor Cyan; try { $meta = Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/zepiam/broadcast-playroom-3/master/version.json' -TimeoutSec 10 } catch { $meta = Invoke-RestMethod -Uri 'https://huggingface.co/men9ch/broadcast-playroom-3/raw/main/version.json' -TimeoutSec 10 }; $ver = $meta.latest_version; Write-Host ('Latest version: v' + $ver) -ForegroundColor Green; $zipUrl = $meta.full.url; $zipPath = Join-Path $PWD ('bp3_patch_v' + $ver + '.zip'); Write-Host ('Downloading update from ' + $zipUrl + ' ...') -ForegroundColor Cyan; try { (New-Object System.Net.WebClient).DownloadFile($zipUrl, $zipPath) } catch { Write-Host 'Downloading from mirror...' -ForegroundColor Yellow; (New-Object System.Net.WebClient).DownloadFile($meta.full.mirrors[0], $zipPath) }; Write-Host 'Applying update files...' -ForegroundColor Cyan; Expand-Archive -Path $zipPath -DestinationPath $PWD -Force; Remove-Item $zipPath -ErrorAction SilentlyContinue; Write-Host 'Update applied successfully! You can now start Broadcast Playroom 3.' -ForegroundColor Green } catch { Write-Host ('Error: ' + $_) -ForegroundColor Red; Read-Host 'Press Enter to exit...' } }"

:success
echo.
echo ================================================================
echo   Finished! Please launch Broadcast Playroom 3.
echo ================================================================
echo.
pause
