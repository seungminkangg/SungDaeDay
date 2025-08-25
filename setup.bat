@echo off
chcp 65001 > nul
echo HayDay Dynamic Balancing Simulator - Initial Setup
echo ====================================================

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, make sure to check
    echo "Add Python to PATH" option!
    echo.
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages for HayDay Simulator...
echo This may take a few minutes...

python -m pip install pandas>=2.0.0
python -m pip install numpy>=1.24.0
python -m pip install streamlit>=1.28.0
python -m pip install plotly>=5.15.0
python -m pip install Flask>=2.3.0
python -m pip install Jinja2>=3.1.0
python -m pip install matplotlib>=3.7.0
python -m pip install seaborn>=0.12.0
python -m pip install requests>=2.31.0
python -m pip install openpyxl>=3.1.0

echo.
echo ====================================================
echo Setup completed successfully!
echo ====================================================
echo.
echo To run the simulator:
echo   1. Double-click "run_simple.bat"
echo   2. Or run "run_simple.bat" from command prompt
echo   3. Or use Git Bash: "./run_simple.sh"
echo.
echo The simulator will be available at:
echo   - Flask Web UI: http://localhost:5001
echo   - Streamlit Dashboard: http://localhost:8502
echo.
echo Network access for other devices:
echo   - Find your IP: ipconfig
echo   - Access: http://YOUR_IP:5001
echo.
echo Press any key to exit
pause > nul