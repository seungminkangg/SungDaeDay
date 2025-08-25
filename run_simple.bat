@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo ========================================================
echo      [HayDay Dynamic Balancing Simulator]
echo           Windows 실행 스크립트 v2.0
echo ========================================================
echo.

REM 프로젝트 루트 디렉토리 확인
if not exist "webui\" (
    echo [ERROR] webui 폴더를 찾을 수 없습니다
    echo    현재 디렉토리: %CD%
    echo    프로젝트 루트에서 실행해주세요
    pause
    exit /b 1
)

echo Python 설치 확인...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python이 설치되지 않았거나 PATH에 등록되지 않음
    echo.
    echo 해결 방법:
    echo   1. setup.bat 먼저 실행 (자동 설치)
    echo   2. 또는 https://python.org 에서 수동 설치
    echo   3. 설치 시 "Add Python to PATH" 필수 체크!
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do set PYTHON_VER=%%a
echo [OK] %PYTHON_VER% 감지됨

REM 필수 패키지 확인 및 설치
echo.
echo 필수 패키지 확인...

python -c "import flask, pandas" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] 필수 패키지가 설치되지 않음 - 자동 설치 시작
    echo    (setup.bat을 먼저 실행하는 것을 권장)
    echo.
    
    echo pip 업그레이드...
    python -m pip install --upgrade pip --quiet
    
    echo 필수 패키지 설치...
    python -m pip install pandas numpy flask jinja2 requests openpyxl --quiet
    if errorlevel 1 (
        echo [WARNING] 일부 패키지 설치 실패 - 사용자 설치 시도
        python -m pip install --user pandas numpy flask jinja2 requests openpyxl --quiet
        if errorlevel 1 (
            echo.
            echo [ERROR] 패키지 설치가 완전히 실패했습니다
            echo.
            echo 해결 방법:
            echo   1. setup.bat을 관리자 권한으로 실행
            echo   2. 인터넷 연결 확인
            echo   3. Python 재설치 (PATH 포함)
            echo.
            pause
            exit /b 1
        )
    )
    echo [OK] 패키지 설치 완료
) else (
    echo [OK] 필수 패키지 설치 확인됨
)

REM 포트 사용 확인
echo.
echo 포트 상태 확인...
netstat -an | findstr ":5001" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] 포트 5001이 이미 사용 중입니다
    echo    기존 HayDay Simulator가 실행 중이거나 다른 프로그램이 사용 중일 수 있습니다
    echo.
    echo    계속 진행하시겠습니까? (Y/N)
    choice /c YN /n /m "Y: 계속, N: 중단"
    if errorlevel 2 goto end_script
)

echo.
echo HayDay Flask Web UI 시작 중...
cd webui

REM 서버 백그라운드 실행
echo    서버를 새 창에서 시작합니다...
start "[HayDay Simulator - Flask Server]" /min python app.py

echo.
echo    서버 초기화 대기 중...
timeout /t 3 > nul

REM 브라우저에서 열기
echo 기본 브라우저에서 열기...
start "" "http://localhost:5001"

echo.
echo ========================================================
echo                [실행 완료!]
echo ========================================================
echo.
echo 접속 주소:
echo   +---------------------------------------------+
echo   | 메인 페이지: http://localhost:5001         |
echo   | 주문 관리:   http://localhost:5001/orders  |
echo   | 데이터 분석: http://localhost:5001/data    |
echo   | 대시보드:    http://localhost:5001/dashboard|
echo   +---------------------------------------------+
echo.
echo 모바일/다른 기기 접속:
echo   1. ipconfig 명령으로 내 IP 확인
echo   2. http://내IP주소:5001 로 접속
echo.
echo 서버 관리:
echo   - 서버 중지: 새로 열린 "HayDay Simulator" 창 닫기
echo   - 서버 재시작: 이 스크립트 다시 실행
echo   - 로그 확인: "HayDay Simulator" 창에서 오류 메시지 확인
echo.
echo 추가 기능:
echo   - Streamlit 대시보드: streamlit run hayday_simulator.py
echo   - 포트 변경: webui\app.py에서 port=5001 수정
echo.
echo.

REM 사용자가 종료할 때까지 대기
echo 서버가 백그라운드에서 실행 중입니다...
echo    아무 키나 누르면 이 창을 닫습니다 (서버는 계속 실행)
echo    서버를 중지하려면 "HayDay Simulator" 창을 닫으세요
echo.
pause > nul

:end_script
echo.
echo 스크립트를 종료합니다
echo    서버는 백그라운드에서 계속 실행됩니다