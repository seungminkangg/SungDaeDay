@echo off
chcp 65001 > nul

REM Change to the directory where this batch file is located
cd /d "%~dp0"

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

REM Check basics - show current info for debugging
echo Current directory: %CD%
echo.
echo Files in current directory:
dir /b | findstr /v "\.git"
echo.

if not exist "webui\" (
    if not exist "webui" (
        echo [ERROR] webui folder missing
        echo Current location: %CD%
        echo.
        echo Make sure you are in the SungDaeDay project directory
        echo and that the webui folder exists.
        echo.
        pause & goto menu
    ) else (
        echo [INFO] Found webui folder (no backslash)
    )
) else (
    echo [INFO] Found webui\ folder
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
%PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl --quiet --user

REM Get network IP
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do set LOCAL_IP=%%j & goto start_flask
)
:start_flask

REM Change to webui directory (try both ways)
if exist "webui\" (
    cd webui
) else (
    if exist "webui" (
        cd webui
    ) else (
        echo [ERROR] Cannot find webui folder
        pause & goto menu
    )
)

echo.
echo ========================================
echo   Server Starting!
echo ========================================
echo   Local:   http://localhost:5001
if defined LOCAL_IP echo   Network: http://%LOCAL_IP%:5001
echo   Press Ctrl+C to stop
echo ========================================
echo.

if exist "app.py" (
    %PYTHON_CMD% app.py
) else (
    echo [ERROR] app.py not found in webui folder
    echo Current webui directory contents:
    dir /b
    pause
)

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
if exist "webui\" (
    echo     [OK] webui\ exists
) else (
    if exist "webui" (
        echo     [OK] webui exists (no backslash)
    ) else (
        echo     [ERROR] webui missing
    )
)

echo [4] Python check:
python --version >nul 2>&1 && echo     [OK] python available || echo     [ERROR] python missing
py --version >nul 2>&1 && echo     [OK] py available || echo     [ERROR] py missing

echo [5] requirements.txt:
if exist "requirements.txt" (echo     [OK] exists) else (echo     [ERROR] missing)

echo [6] webui/app.py:
if exist "webui\app.py" (
    echo     [OK] webui\app.py exists
) else (
    if exist "webui/app.py" (
        echo     [OK] webui/app.py exists
    ) else (
        echo     [ERROR] webui/app.py missing
    )
)

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
echo Checking project structure...
echo Current directory: %CD%
if not exist "webui\" (
    if not exist "webui" (
        echo [ERROR] webui folder missing
        echo Current files:
        dir /b
        pause & goto menu
    )
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

REM Install packages (avoid requirements.txt encoding issues)
echo Installing essential packages directly...
%PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl

REM Firewall rule
echo Adding firewall rule...
netsh advfirewall firewall add rule name="HayDay Simulator" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1

echo.
echo Installation complete!
pause
goto menu

:menu
cls
REM Ensure we're in the correct directory
cd /d "%~dp0"

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