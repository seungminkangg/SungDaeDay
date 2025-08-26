@echo off
chcp 65001 > nul

echo ========================================
echo   HayDay Flask Server (Streamlit Free)
echo ========================================
echo.

REM Check webui folder
if not exist "webui\" (
    echo [ERROR] webui folder not found
    echo Current location: %CD%
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not installed
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo [OK] Python: %PYTHON_CMD%

REM Install only essential packages
echo.
echo [INFO] Installing Flask essentials only...
%PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl --quiet --user

REM Get IP for network access
echo.
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do (
        set LOCAL_IP=%%j
        goto start_server
    )
)

:start_server
cd webui

echo.
echo ========================================
echo   Flask Server Starting
echo ========================================
echo.
echo Local: http://localhost:5001
if defined LOCAL_IP echo Network: http://%LOCAL_IP%:5001
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

%PYTHON_CMD% app.py

pause