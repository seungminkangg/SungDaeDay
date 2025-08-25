@echo off
chcp 65001 > nul
echo HayDay Dynamic Balancing Simulator - Windows Setup
echo ===================================================

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing required packages (Flask standalone)...
python -m pip install --upgrade pip
python -m pip install pandas numpy flask jinja2 requests openpyxl

if errorlevel 1 (
    echo WARNING: Some packages failed to install
    echo Trying alternative installation...
    python -m pip install pandas numpy flask jinja2 requests openpyxl
)

echo.
echo Starting HayDay Flask Web UI...
cd webui
start "HayDay Simulator" python app.py

timeout /t 2 > nul

echo.
echo ===================================================
echo HayDay Flask Web UI is starting...
echo Main URL: http://localhost:5001 (주문 관리)
echo Data Explorer: http://localhost:5001/data
echo Network Access: http://YOUR_LOCAL_IP:5001
echo ===================================================
echo Server will open in a separate window
echo Close that window to stop the server
echo Press any key to close this setup window
pause > nul