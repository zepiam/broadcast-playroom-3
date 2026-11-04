@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Broadcast Playroom 3 - FindUpdate ^& System Repair

echo ================================================================
echo   Broadcast Playroom 3 - ตรวจสอบอัปเดตและซ่อมแซมระบบ (FindUpdate)
echo ================================================================
echo.

:: 1. If dedicated GUI Patch Installer exists, launch it directly
if exist "BP3_PatchInstaller.exe" (
    echo [INFO] กำลังเปิดโปรแกรมอัปเดตและซ่อมแซมระบบ (BP3_PatchInstaller)...
    start "" "BP3_PatchInstaller.exe"
    exit /b 0
)

if exist "_internal\BP3_PatchInstaller.exe" (
    echo [INFO] กำลังเปิดโปรแกรมอัปเดตและซ่อมแซมระบบ (BP3_PatchInstaller)...
    start "" "_internal\BP3_PatchInstaller.exe"
    exit /b 0
)

:: 2. Try Python CLI if available
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

:: 3. Standalone PowerShell Fallback Updater (Works on all Windows 10/11 machines without Python)
echo [INFO] เริ่มต้นระบบดาวน์โหลดและซ่อมแซมผ่าน Windows PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;
    Write-Host '------------------------------------------------------------' -ForegroundColor DarkGray;
    Write-Host ' กำลังปิดโปรแกรมที่เปิดค้างอยู่เพื่อปลดล็อกไฟล์ระบบ...' -ForegroundColor Yellow;
    Stop-Process -Name 'BroadcastPlayroom3-Full', 'BroadcastPlayroom3-Lite', 'msedgewebview2' -Force -ErrorAction SilentlyContinue;
    Start-Sleep -Seconds 1;

    Write-Host ' กำลังตรวจสอบเวอร์ชันล่าสุด...' -ForegroundColor Cyan;
    $meta = $null;
    foreach ($url in @('https://huggingface.co/men9ch/broadcast-playroom-3/raw/main/version.json', 'https://raw.githubusercontent.com/zepiam/broadcast-playroom-3/master/version.json')) {
        try {
            $meta = Invoke-RestMethod -Uri $url -TimeoutSec 8;
            if ($meta -and ($meta.version -or $meta.latest_version)) { break; }
        } catch {}
    }
    if (-not $meta) {
        Write-Host '[ข้อผิดพลาด] ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์อัปเดตได้ กรุณาตรวจสอบอินเทอร์เน็ต' -ForegroundColor Red;
        Read-Host 'กด Enter เพื่อออก...';
        exit 1;
    }

    $ver = if ($meta.version) { $meta.version } else { $meta.latest_version };
    Write-Host (' พบเวอร์ชันล่าสุดบนเซิร์ฟเวอร์: v' + $ver) -ForegroundColor Green;

    # Detect edition (Lite vs Full)
    $isLite = Test-Path (Join-Path $PWD 'BroadcastPlayroom3-Lite.exe');
    $edition = if ($isLite) { 'lite' } else { 'full' };
    Write-Host (' ประเภทโปรแกรมในเครื่อง: ' + $edition.ToUpper()) -ForegroundColor Cyan;

    # Find download URL from meta
    $zipUrl = '';
    if ($meta.$edition -and $meta.$edition.url) { $zipUrl = $meta.$edition.url; }
    elseif ($meta.packages -and $meta.packages.$edition -and $meta.packages.$edition.url) { $zipUrl = $meta.packages.$edition.url; }
    elseif ($meta.patches -and $meta.patches.$edition -and $meta.patches.$edition.url) { $zipUrl = $meta.patches.$edition.url; }
    elseif ($meta.full -and $meta.full.url) { $zipUrl = $meta.full.url; }

    if (-not $zipUrl) {
        Write-Host '[ข้อผิดพลาด] ไม่พบลิงก์ดาวน์โหลดสำหรับเวอร์ชันนี้' -ForegroundColor Red;
        Read-Host 'กด Enter เพื่อออก...';
        exit 1;
    }

    $tempZip = Join-Path ([System.IO.Path]::GetTempPath()) ('bp3_update_' + $ver + '_' + $edition + '.zip');
    Write-Host (' กำลังดาวน์โหลดแพตช์จาก Hugging Face CDN...') -ForegroundColor Cyan;
    try {
        (New-Object System.Net.WebClient).DownloadFile($zipUrl, $tempZip);
    } catch {
        Write-Host (' กำลังลองดาวน์โหลดจากลิงก์สำรอง...') -ForegroundColor Yellow;
        $mirrorUrl = if ($meta.$edition -and $meta.$edition.mirrors) { $meta.$edition.mirrors[0] } else { '' };
        if ($mirrorUrl) {
            (New-Object System.Net.WebClient).DownloadFile($mirrorUrl, $tempZip);
        } else {
            throw $_;
        }
    }

    Write-Host ' กำลังแตกไฟล์แพตช์อัปเดตทับไฟล์ระบบเดิม...' -ForegroundColor Cyan;
    Expand-Archive -Path $tempZip -DestinationPath $PWD -Force;

    # Sync into _internal directory if present
    $internalDir = Join-Path $PWD '_internal';
    if (Test-Path $internalDir) {
        Write-Host ' กำลังซิงค์ไฟล์เข้าโฟลเดอร์ระบบ _internal...' -ForegroundColor DarkGray;
        $distSrc = Join-Path $PWD 'dist';
        $distDest = Join-Path $internalDir 'dist';
        if (Test-Path $distSrc) {
            Copy-Item -Path $distSrc -Destination $internalDir -Recurse -Force;
        }
        foreach ($f in @('launch_dev.py', 'updater.py', 'version.json', 'desktop_overlay_service.py', 'desktop_overlay_qt.py', 'viewer_overlay_config.py', 'defender_helper.py')) {
            $fSrc = Join-Path $PWD $f;
            if (Test-Path $fSrc) {
                Copy-Item -Path $fSrc -Destination $internalDir -Force;
            }
        }
    }

    # Purge stale WebView2 / Chrome caches
    foreach ($cRoot in @((Join-Path $PWD 'data\browser_profile'), (Join-Path $PWD 'data\webview_data'), (Join-Path $env:LOCALAPPDATA 'BroadcastPlayroom3\browser_profile'), (Join-Path $env:LOCALAPPDATA 'BroadcastPlayroom3\webview_data'))) {
        foreach ($sub in @('Default\Cache', 'Default\Code Cache', 'EBWebView\Default\Cache', 'EBWebView\Default\Code Cache')) {
            $p = Join-Path $cRoot $sub;
            if (Test-Path $p) { Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue; }
        }
    }

    Remove-Item $tempZip -ErrorAction SilentlyContinue;

    Write-Host '------------------------------------------------------------' -ForegroundColor DarkGray;
    Write-Host ('✨ อัปเดตและซ่อมแซมระบบเป็น v' + $ver + ' สำเร็จเรียบร้อย 100%!') -ForegroundColor Green;
    Write-Host ' กำลังเปิดโปรแกรม Broadcast Playroom 3 ใน 2 วินาที...' -ForegroundColor Cyan;
    Start-Sleep -Seconds 2;

    $exeFull = Join-Path $PWD 'BroadcastPlayroom3-Full.exe';
    $exeLite = Join-Path $PWD 'BroadcastPlayroom3-Lite.exe';
    if (Test-Path $exeFull) { Start-Process $exeFull; }
    elseif (Test-Path $exeLite) { Start-Process $exeLite; }
}"

:success
echo.
echo ================================================================
echo   อัปเดตเสร็จสมบูรณ์!
echo ================================================================
echo.
