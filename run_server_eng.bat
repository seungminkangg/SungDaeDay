@echo off
chcp 65001 > nul

echo ========================================
echo   HayDay Simulator Server
echo ========================================
echo.

REM Check webui folder
if not exist "webui\" (
    echo [ERROR] webui folder not found
    echo Current location: %CD%
    echo.
    echo Please run this script from project root directory
    echo.
    pause
    exit /b 1
)

REM Check Python (simple)
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not installed
        echo.
        echo Solution:
        echo 1. Download Python from https://python.org
        echo 2. Check "Add Python to PATH" during installation
        echo 3. Restart and run again
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo [OK] Python detected: %PYTHON_CMD%

REM Install packages (simple)
echo.
echo [INFO] Installing required packages...
%PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl --quiet --user
if errorlevel 1 (
    echo [WARNING] Package installation failed - continuing anyway
)

REM Get network IP
echo.
echo [INFO] Network setup...
set LOCAL_IP=
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do (
        set LOCAL_IP=%%j
        goto ip_found_server
    )
)
:ip_found_server

REM Start server
echo.
echo [INFO] Starting server...
cd webui

echo.
echo ========================================
echo   Server Starting!
echo ========================================
echo.
echo Local access:
echo   http://localhost:5001
echo.
if defined LOCAL_IP (
    echo Network access ^(other devices^):
    echo   http://%LOCAL_IP%:5001
    echo.
)
echo Press Ctrl+C to stop server
echo ========================================
echo.

%PYTHON_CMD% app.py

echo.
echo Server stopped
pause