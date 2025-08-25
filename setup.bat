@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo ========================================================
echo   [HayDay Dynamic Balancing Simulator - Setup]
echo          Windows 자동 설치 스크립트 v2.0
echo ========================================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] 관리자 권한으로 실행됨
) else (
    echo [WARNING] 일반 사용자 권한으로 실행됨 (일부 패키지 설치 시 문제 발생 가능)
)

echo.
echo Python 설치 확인...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python이 설치되지 않았거나 PATH에 등록되지 않음
    echo.
    echo Python 설치 가이드:
    echo   1. https://python.org/downloads/ 방문
    echo   2. 최신 Python 3.11+ 다운로드
    echo   3. 설치 시 "Add Python to PATH" 체크박스 [필수체크!]
    echo   4. 설치 완료 후 명령 프롬프트 재시작
    echo   5. 이 스크립트 다시 실행
    echo.
    echo 경로 문제 해결:
    echo   - 제어판 ^> 시스템 ^> 고급 시스템 설정 ^> 환경변수
    echo   - Path에 Python 설치 경로 추가 (예: C:\Python311;C:\Python311\Scripts)
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do set PYTHON_VER=%%a
echo [OK] %PYTHON_VER% 감지됨

echo.
echo pip 업그레이드...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] pip 업그레이드 실패 - 계속 진행
) else (
    echo [OK] pip 업그레이드 완료
)

echo.
echo requirements.txt 파일 확인...
if exist requirements.txt (
    echo [OK] requirements.txt 발견 - 자동 설치 진행
    python -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [WARNING] requirements.txt 설치 실패 - 수동 설치 진행
        goto manual_install
    ) else (
        echo [OK] requirements.txt로 패키지 설치 완료
        goto setup_complete
    )
) else (
    echo [WARNING] requirements.txt 없음 - 수동 설치 진행
)

:manual_install
echo.
echo 필수 패키지 수동 설치...
echo   (네트워크 속도에 따라 1-3분 소요)

set packages=pandas numpy streamlit plotly flask jinja2 matplotlib seaborn requests openpyxl

echo.
echo 설치할 패키지: %packages%
echo.

python -m pip install %packages% --quiet
if errorlevel 1 (
    echo.
    echo [WARNING] 일부 패키지 설치 실패 - 개별 설치 시도...
    
    REM 개별 패키지 설치
    for %%p in (%packages%) do (
        echo   - %%p 설치 중...
        python -m pip install %%p --quiet
        if errorlevel 1 (
            echo     [FAIL] %%p 설치 실패
        ) else (
            echo     [OK] %%p 설치 성공
        )
    )
) else (
    echo [OK] 모든 패키지 설치 완료
)

:setup_complete
echo.
echo.
echo ========================================================
echo                [설치 완료!]
echo ========================================================
echo.
echo 시뮬레이터 실행 방법:
echo   1. [추천] run_simple.bat 더블클릭
echo   2. CMD에서: run_simple.bat
echo   3. Git Bash에서: ./run_simple.sh
echo   4. PowerShell에서: .\run_simple.bat
echo.
echo 접속 주소:
echo   - 메인 UI: http://localhost:5001 (주문 관리)
echo   - 대시보드: http://localhost:8502 (데이터 분석)
echo.
echo 모바일/다른 기기에서 접속:
echo   1. ipconfig 명령으로 IP 확인
echo   2. http://YOUR_IP:5001 로 접속
echo.
echo 문제 해결:
echo   - 포트 충돌: 다른 프로그램이 5001/8502 포트 사용 중일 수 있음
echo   - 방화벽: Windows 방화벽에서 Python 허용 확인
echo   - 재부팅: 설치 후 PC 재부팅 권장
echo.
echo 지금 시뮬레이터를 실행하시겠습니까? (Y/N)
choice /c YN /n /m "Y: 실행, N: 나중에"
if errorlevel 2 goto exit_setup
if errorlevel 1 goto run_now

:run_now
echo.
echo 시뮬레이터 시작 중...
call run_simple.bat
goto end

:exit_setup
echo.
echo 설정이 완료되었습니다! 
echo    언제든지 run_simple.bat을 실행하세요.

:end
echo.
echo 아무 키나 누르면 종료됩니다...
pause > nul