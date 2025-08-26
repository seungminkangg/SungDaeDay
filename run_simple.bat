@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM 관리자 권한 확인 및 요청
NET SESSION >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================================
    echo      [HayDay Dynamic Balancing Simulator]
    echo         관리자 권한 필요 - 자동 권한 요청
    echo ========================================================
    echo.
    echo Python 설치 및 패키지 관리를 위해 관리자 권한이 필요합니다.
    echo 잠시 후 UAC(사용자 계정 컨트롤) 창이 나타나면 "예"를 클릭해주세요.
    echo.
    timeout /t 3 > nul
    
    REM 관리자 권한으로 재실행
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    exit /b 0
)

echo.
echo ========================================================
echo      [HayDay Dynamic Balancing Simulator]
echo           Windows 실행 스크립트 v3.0 (관리자)
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

REM Python 명령어들 확인 (우선순위 순)
set PYTHON_CMD=
python --version >nul 2>&1 && set PYTHON_CMD=python && goto python_found
py -3 --version >nul 2>&1 && set PYTHON_CMD=py -3 && goto python_found
py --version >nul 2>&1 && set PYTHON_CMD=py && goto python_found
python3 --version >nul 2>&1 && set PYTHON_CMD=python3 && goto python_found

REM Python이 없는 경우 자동 설치 시도
echo [WARNING] Python이 설치되지 않았습니다
echo.
echo 자동 Python 설치를 시도하겠습니다...
echo.

REM Chocolatey가 있는지 확인하고 설치
choco --version >nul 2>&1
if errorlevel 1 (
    echo Chocolatey 패키지 매니저 설치 중...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if errorlevel 1 (
        echo [ERROR] Chocolatey 설치 실패
        goto manual_python_install
    )
    REM PATH 새로고침
    refreshenv
    choco --version >nul 2>&1
    if errorlevel 1 goto manual_python_install
)

echo Chocolatey로 Python 설치 중...
choco install python -y
if errorlevel 1 goto manual_python_install

echo Python 설치 완료! PATH 새로고침 중...
refreshenv >nul 2>&1
timeout /t 2 > nul

REM 재확인
python --version >nul 2>&1 && set PYTHON_CMD=python && goto python_found
py --version >nul 2>&1 && set PYTHON_CMD=py && goto python_found

:manual_python_install
echo.
echo [ERROR] 자동 Python 설치가 실패했습니다
echo.
echo 수동 설치 방법:
echo   1. https://python.org/downloads 에서 Python 3.9 이상 다운로드
echo   2. 설치 시 "Add Python to PATH" 반드시 체크!
echo   3. 설치 후 이 스크립트 다시 실행
echo.
set /p INSTALL_MANUAL="브라우저에서 Python 다운로드 페이지를 여시겠습니까? [y/N]: "
if /i "!INSTALL_MANUAL!"=="y" start "" "https://www.python.org/downloads/"
pause
exit /b 1

:python_found

for /f "tokens=*" %%a in ('!PYTHON_CMD! --version') do set PYTHON_VER=%%a
echo [OK] %PYTHON_VER% 감지됨

REM 필수 패키지 확인 및 설치
echo.
echo 필수 패키지 확인...

REM requirements.txt 파일 체크 우선
if exist "requirements.txt" (
    echo requirements.txt 파일 발견 - 사용하여 설치 진행
    goto install_from_requirements
)

REM 개별 패키지 확인
!PYTHON_CMD! -c "import flask, pandas" >nul 2>&1
if errorlevel 1 goto install_packages

echo [OK] 필수 패키지 설치 확인됨
goto skip_install

:install_from_requirements
echo.
echo [INFO] requirements.txt로 패키지 설치 중...
!PYTHON_CMD! -m pip install --upgrade pip --quiet >nul 2>&1
!PYTHON_CMD! -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] 시스템 설치 실패 - 사용자 모드로 재시도
    !PYTHON_CMD! -m pip install --user -r requirements.txt --quiet
    if errorlevel 1 goto install_error
)
echo [OK] requirements.txt 패키지 설치 완료
goto skip_install

:install_packages
echo [WARNING] 필수 패키지가 설치되지 않음 - 자동 설치 시작
echo.

echo pip 업그레이드...
!PYTHON_CMD! -m pip install --upgrade pip --quiet >nul 2>&1

echo 필수 패키지 설치 중...
!PYTHON_CMD! -m pip install pandas numpy flask jinja2 requests openpyxl --quiet
if errorlevel 1 (
    echo [WARNING] 시스템 설치 실패 - 사용자 모드로 재시도
    !PYTHON_CMD! -m pip install --user pandas numpy flask jinja2 requests openpyxl --quiet
    if errorlevel 1 goto install_error
)
echo [OK] 패키지 설치 완료
goto skip_install

:install_error
echo.
echo [ERROR] 패키지 설치가 실패했습니다
echo.
echo 해결 방법:
echo   1. 관리자 권한으로 cmd 실행 후 다시 시도
echo   2. 인터넷 연결 확인
echo   3. Python과 pip이 최신 버전인지 확인
echo   4. 방화벽/백신 소프트웨어 임시 해제
echo.
set /p CONTINUE="계속 진행하시겠습니까? (패키지가 없으면 오류 발생 가능) [y/N]: "
if /i "!CONTINUE!"=="y" goto skip_install
pause
exit /b 1

:skip_install

REM 방화벽 규칙 자동 추가 (네트워크 공유용)
echo.
echo 네트워크 공유를 위한 방화벽 설정...
netsh advfirewall firewall show rule name="HayDay Simulator" >nul 2>&1
if errorlevel 1 (
    echo    방화벽 규칙 추가 중... (외부 접속 허용)
    netsh advfirewall firewall add rule name="HayDay Simulator" dir=in action=allow protocol=TCP localport=5001 >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] 방화벽 규칙 추가 실패 - 수동으로 허용해야 할 수 있음
    ) else (
        echo [OK] 방화벽에서 포트 5001 허용됨
    )
) else (
    echo [OK] 방화벽 규칙이 이미 존재함
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
start "[HayDay Simulator - Flask Server]" /min !PYTHON_CMD! app.py

echo.
echo    서버 초기화 대기 중...
timeout /t 3 > nul

REM 서버 시작 확인
echo 서버 시작 확인 중...
for /l %%i in (1,1,10) do (
    !PYTHON_CMD! -c "import urllib.request; urllib.request.urlopen('http://localhost:5001', timeout=1)" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] 서버 시작 확인됨
        goto server_ready
    )
    echo    대기 중... (%%i/10)
    timeout /t 2 > nul
)
echo [WARNING] 서버 응답 확인 실패 - 수동으로 확인 필요

:server_ready
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
echo ================================================================
echo                   🌐 네트워크 공유 안내
echo ================================================================
echo.
echo 같은 WiFi/랜에 있는 다른 기기에서 접속하려면:
echo.
echo 1단계: 내 컴퓨터의 IP 주소 확인
echo   - Windows+R → cmd → ipconfig 입력
echo   - 또는 아래 명령어가 자동으로 IP를 찾아줍니다:
echo.

REM 현재 컴퓨터의 IP 주소 자동 검색
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do (
        set LOCAL_IP=%%j
        goto ip_found
    )
)
:ip_found

if defined LOCAL_IP (
    echo ✅ 자동 감지된 IP 주소: %LOCAL_IP%
    echo.
    echo 2단계: 다른 기기에서 브라우저로 접속
    echo   📱 스마트폰/태블릿: http://%LOCAL_IP%:5001
    echo   💻 다른 컴퓨터: http://%LOCAL_IP%:5001
) else (
    echo ⚠️ IP 주소 자동 감지 실패
    echo.
    echo 2단계: 수동으로 IP 확인 후 접속
    echo   - cmd에서 ipconfig 명령어 실행
    echo   - IPv4 주소를 찾아서 http://해당IP:5001 로 접속
)

echo.
echo 📌 네트워크 공유 문제해결:
echo   - 방화벽 해제: 제어판 → Windows Defender 방화벽 → 끄기
echo   - 같은 WiFi 확인: 모든 기기가 동일한 WiFi에 연결되어 있는지 확인
echo   - 포트 차단 확인: 일부 공용 WiFi는 포트를 차단할 수 있음
echo.
echo 서버 관리:
echo   - 서버 중지: "HayDay Simulator" 창 닫기 또는 Ctrl+C
echo   - 서버 재시작: 이 스크립트 다시 실행
echo   - 로그 확인: "HayDay Simulator" 창에서 오류 메시지 확인
echo.
echo 문제해결 가이드:
echo   - 포트 사용 중 오류: 작업 관리자에서 python.exe 프로세스 종료
echo   - 패키지 오류: 이 스크립트를 관리자 권한으로 다시 실행
echo   - 브라우저가 안 열림: 수동으로 http://localhost:5001 접속
echo   - Python 오류: Python을 재설치하고 "Add to PATH" 체크
echo.
echo 추가 기능:
echo   - Excel 내보내기: 웹 인터페이스에서 "Excel 다운로드" 버튼
echo   - 포트 변경: webui\app.py에서 port=5001 수정
echo.

REM 자동 종료 타이머 추가
echo ================================================================
echo.
echo 🎯 HayDay Simulator가 성공적으로 시작되었습니다!
echo.
echo 📍 이 창은 30초 후 자동으로 닫힙니다 (서버는 계속 실행됩니다)
echo 📍 즉시 닫으려면 아무 키나 누르세요
echo 📍 서버를 중지하려면 "HayDay Simulator" 창을 닫으세요
echo.

REM 30초 타이머 또는 사용자 입력 대기
timeout /t 30 > nul

:end_script
echo.
echo 스크립트를 종료합니다
echo    서버는 백그라운드에서 계속 실행됩니다