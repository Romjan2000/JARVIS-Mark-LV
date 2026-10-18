@echo off
title JARVIS Mark-LV
cd /d "%~dp0"

:: Check if virtual environment exists and activate it if present
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Launch JARVIS
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ====================================================
    echo JARVIS exited with an error code: %ERRORLEVEL%
    echo If this is your first run, make sure to execute:
    echo     python setup.py
    echo ====================================================
    pause
)
