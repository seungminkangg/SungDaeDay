@echo off
chcp 65001 > nul
echo ========================================
echo   HayDay Simulator Debug Mode
echo ========================================
echo.

echo [1] Current directory: %CD%
echo.

echo [2] File list:
dir /b
echo.

echo [3] webui folder check...
if exist "webui\" (
    echo    [OK] webui folder exists
    echo    webui folder contents:
    dir webui /b
) else (
    echo    [ERROR] webui folder missing
)
echo.

echo [4] Python installation check...
python --version 2>nul && echo    [OK] python command available || echo    [ERROR] python command missing
py --version 2>nul && echo    [OK] py command available || echo    [ERROR] py command missing  
python3 --version 2>nul && echo    [OK] python3 command available || echo    [ERROR] python3 command missing
echo.

echo [5] requirements.txt check...
if exist "requirements.txt" (
    echo    [OK] requirements.txt exists
) else (
    echo    [ERROR] requirements.txt missing
)
echo.

echo [6] webui/app.py check...
if exist "webui\app.py" (
    echo    [OK] webui/app.py exists
) else (
    echo    [ERROR] webui/app.py missing
)
echo.

echo [7] Network IP detection...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do (
        echo    [INFO] Detected IP: %%j
        goto ip_done
    )
)
:ip_done
echo.

echo ========================================
echo   Diagnosis Complete
echo ========================================
echo.
echo Press any key to exit...
pause > nul