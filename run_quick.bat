@echo off
chcp 65001 > nul

echo ========================================
echo   HayDay Simulator 빠른 실행
echo ========================================
echo.

REM 기본 확인
if not exist "webui\" (
    echo ❌ ERROR: webui 폴더가 없습니다
    echo 현재 위치: %CD%
    echo.
    pause
    exit /b 1
)

REM Python 확인 (간단하게)
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ ERROR: Python이 설치되지 않았습니다
        echo.
        echo 해결방법:
        echo 1. https://python.org 에서 Python 다운로드
        echo 2. 설치시 "Add Python to PATH" 체크
        echo 3. 설치 후 재실행
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ Python 확인됨: %PYTHON_CMD%

REM 패키지 설치 (간단하게)
echo.
echo 📦 필수 패키지 설치 중...
%PYTHON_CMD% -m pip install flask pandas numpy requests openpyxl --quiet --user
if errorlevel 1 (
    echo ⚠️ 패키지 설치 실패 - 계속 진행합니다
)

REM 서버 시작
echo.
echo 🚀 서버 시작 중...
cd webui

echo.
echo ========================================
echo   서버가 시작됩니다!
echo   브라우저에서 http://localhost:5001 접속
echo   종료하려면 Ctrl+C 누르세요
echo ========================================
echo.

%PYTHON_CMD% app.py

echo.
echo 서버가 종료되었습니다
pause