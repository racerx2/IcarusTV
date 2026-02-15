@echo off
title Icarus TV Relay Server
setlocal enabledelayedexpansion

echo ========================================
echo   Icarus TV Relay Server - Launcher
echo ========================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo   Download Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo   IMPORTANT: Check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [OK] Python %%v

REM --- Check FFmpeg ---
if not exist "%~dp0ffmpeg\ffmpeg.exe" (
    echo.
    echo [SETUP] FFmpeg not found - downloading...
    echo.
    mkdir "%~dp0ffmpeg" 2>nul
    
    REM Download ffmpeg-release-essentials zip
    set "FFURL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    set "FFZIP=%~dp0ffmpeg\ffmpeg-download.zip"
    
    echo   Downloading from gyan.dev...
    powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '%FFURL%' -OutFile '%FFZIP%' -UseBasicParsing } catch { Write-Host '[ERROR] Download failed:' $_.Exception.Message; exit 1 }"
    if errorlevel 1 (
        echo.
        echo   Auto-download failed. Please download FFmpeg manually:
        echo   1. Go to https://www.gyan.dev/ffmpeg/builds/
        echo   2. Download "ffmpeg-release-essentials.zip"
        echo   3. Extract ffmpeg.exe into: %~dp0ffmpeg\
        echo.
        pause
        exit /b 1
    )
    
    echo   Extracting ffmpeg.exe...
    powershell -Command "$zip = '%FFZIP%'; $dest = '%~dp0ffmpeg'; Add-Type -Assembly System.IO.Compression.FileSystem; $archive = [IO.Compression.ZipFile]::OpenRead($zip); foreach ($entry in $archive.Entries) { if ($entry.Name -eq 'ffmpeg.exe') { $stream = $entry.Open(); $file = [IO.File]::Create((Join-Path $dest 'ffmpeg.exe')); $stream.CopyTo($file); $file.Close(); $stream.Close(); break } }; $archive.Dispose()"
    
    del "%FFZIP%" 2>nul
    
    if exist "%~dp0ffmpeg\ffmpeg.exe" (
        echo   [OK] FFmpeg installed successfully.
    ) else (
        echo   [ERROR] Extraction failed. Please install FFmpeg manually.
        echo   Place ffmpeg.exe in: %~dp0ffmpeg\
        pause
        exit /b 1
    )
) else (
    echo [OK] FFmpeg found
)

REM --- Check Cloudflared (optional - needed for friend/remote access) ---
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Cloudflared not found - remote "Friend URL" feature won't work.
    echo   To enable it, install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    echo   Or run:  winget install Cloudflare.cloudflared
    echo   ^(Local streaming to your own PC will still work fine^)
) else (
    echo [OK] Cloudflared found
)

REM --- Check tkinter (comes with Python on Windows, but just in case) ---
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python tkinter module not found!
    echo   Reinstall Python and make sure "tcl/tk" is checked in the installer.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   All dependencies OK - starting server
echo ========================================
echo.

python -u "%~dp0icarus_relay.py"
echo.
echo Server stopped.
pause
