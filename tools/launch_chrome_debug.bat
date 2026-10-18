@echo off
title Launch Chrome for JARVIS
echo ========================================================
echo   Launching Google Chrome with Remote Debugging (Port 9222)
echo   This allows JARVIS to connect directly to your real Chrome!
echo ========================================================

:: Check if Chrome is already listening on port 9222
powershell -Command "try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:9222/json/version' -TimeoutSec 1; Write-Host 'Chrome is already running with remote debugging!'; exit 0 } catch { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo Chrome is already connected and ready for JARVIS.
    pause
    exit /b 0
)

:: Try finding Chrome in standard locations
set CHROME_EXE=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_EXE="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_EXE="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_EXE="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

if %CHROME_EXE%=="" (
    echo Error: Could not locate chrome.exe automatically.
    pause
    exit /b 1
)

echo Starting Chrome with DevTools Protocol...
start "" %CHROME_EXE% --remote-debugging-port=9222 --remote-allow-origins=* --restore-last-session
echo Done! Chrome is now running and ready for JARVIS commands.
timeout /t 3 >nul
