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
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo WARNING: Some packages failed to install
    echo Trying alternative installation...
    python -m pip install pandas numpy streamlit plotly flask jinja2 matplotlib seaborn requests openpyxl
)

echo.
echo Starting Flask Web UI...
cd webui
start "Flask Server" python app.py

echo Starting Streamlit Dashboard...
cd ..
start "Streamlit Dashboard" streamlit run hayday_simulator.py --server.address 0.0.0.0 --server.port 8503

echo.
echo ===================================================
echo Servers are starting...
echo Flask Web UI: http://localhost:5001
echo Streamlit Dashboard: http://localhost:8503
echo Network Access: http://YOUR_LOCAL_IP:5001
echo ===================================================
echo Both servers will open in separate windows
echo Close those windows to stop the servers
echo Press any key to close this setup window
pause > nul