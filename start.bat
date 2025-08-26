@echo off
chcp 65001 > nul

echo.
echo ========================================
echo   HayDay Simulator - Windows Launcher
echo ========================================
echo.
echo Select option:
echo   [1] Quick Start (Flask only)
echo   [2] System Diagnosis
echo   [3] Full Install (with admin)
echo   [4] Exit
echo.

choice /c 1234 /n /m "Enter choice (1-4): "
set CHOICE_RESULT=%ERRORLEVEL%

if %CHOICE_RESULT%==1 goto quick_start
if %CHOICE_RESULT%==2 goto diagnosis
if %CHOICE_RESULT%==3 goto full_install
if %CHOICE_RESULT%==4 goto exit

:quick_start
echo.
echo === Quick Start Mode ===
echo.

REM Check basics
if not exist "webui\" (
    echo [ERROR] webui folder missing
    echo Run from project root directory
    pause & goto menu
)

python --version >nul 2>&1 || py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Install Python from https://python.org
    pause & goto menu
)

REM Set Python command
python --version >nul 2>&1 && set PYTHON_CMD=python || set PYTHON_CMD=py

REM Install essentials
echo Installing Flask essentials...
%PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl --quiet --user >nul 2>&1

REM Get network IP
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do set LOCAL_IP=%%j & goto start_flask
)
:start_flask

cd webui
echo.
echo ========================================
echo   Server Starting!
echo ========================================
echo   Local:   http://localhost:5001
if defined LOCAL_IP echo   Network: http://%LOCAL_IP%:5001
echo   Press Ctrl+C to stop
echo ========================================
echo.

%PYTHON_CMD% app.py
cd ..
pause
goto menu

:diagnosis
echo.
echo === System Diagnosis ===
echo.

echo [1] Current directory: %CD%
echo [2] Files: 
dir /b | findstr /v "\.git"

echo [3] webui folder:
if exist "webui\" (echo     [OK] exists) else (echo     [ERROR] missing)

echo [4] Python check:
python --version >nul 2>&1 && echo     [OK] python available || echo     [ERROR] python missing
py --version >nul 2>&1 && echo     [OK] py available || echo     [ERROR] py missing

echo [5] requirements.txt:
if exist "requirements.txt" (echo     [OK] exists) else (echo     [ERROR] missing)

echo [6] webui/app.py:
if exist "webui\app.py" (echo     [OK] exists) else (echo     [ERROR] missing)

echo [7] Network IP:
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do echo     IP: %%j & goto diag_done
)
:diag_done

echo.
pause
goto menu

:full_install
echo.
echo === Full Installation Mode ===
echo.

NET SESSION >nul 2>&1
if errorlevel 1 (
    echo Requesting admin privileges...
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    exit /b 0
)

echo Running with admin privileges...
echo.

REM Check project structure
if not exist "webui\" (
    echo [ERROR] webui folder missing
    pause & goto menu
)

REM Python installation with Chocolatey if needed
python --version >nul 2>&1 || py --version >nul 2>&1
if errorlevel 1 (
    echo Installing Python via Chocolatey...
    
    choco --version >nul 2>&1
    if errorlevel 1 (
        echo Installing Chocolatey...
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    )
    
    choco install python -y
    refreshenv
)

REM Set Python command
python --version >nul 2>&1 && set PYTHON_CMD=python || set PYTHON_CMD=py

REM Install packages
echo Installing packages from requirements.txt...
if exist "requirements.txt" (
    %PYTHON_CMD% -m pip install -r requirements.txt
) else (
    %PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl
)

REM Firewall rule
echo Adding firewall rule...
netsh advfirewall firewall add rule name="HayDay Simulator" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1

echo.
echo Installation complete!
pause
goto menu

:menu
cls
echo.
echo ========================================
echo   HayDay Simulator - Windows Launcher
echo ========================================
echo.
echo Select option:
echo   [1] Quick Start (Flask only)
echo   [2] System Diagnosis  
echo   [3] Full Install (with admin)
echo   [4] Exit
echo.

choice /c 1234 /n /m "Enter choice (1-4): "
set CHOICE_RESULT=%ERRORLEVEL%

if %CHOICE_RESULT%==1 goto quick_start
if %CHOICE_RESULT%==2 goto diagnosis
if %CHOICE_RESULT%==3 goto full_install
if %CHOICE_RESULT%==4 goto exit

:exit
echo.
echo Goodbye!
timeout /t 2 > nul