@echo off
echo ========================================
echo   HayDay Simulator Debug Mode
echo ========================================
echo.

echo [1] 현재 디렉토리: %CD%
echo.

echo [2] 파일 목록:
dir /b
echo.

echo [3] webui 폴더 확인...
if exist "webui\" (
    echo    ✅ webui 폴더 존재함
    echo    webui 폴더 내용:
    dir webui /b
) else (
    echo    ❌ webui 폴더 없음
)
echo.

echo [4] Python 설치 확인...
python --version 2>nul && echo    ✅ python 명령어 사용 가능 || echo    ❌ python 명령어 없음
py --version 2>nul && echo    ✅ py 명령어 사용 가능 || echo    ❌ py 명령어 없음
python3 --version 2>nul && echo    ✅ python3 명령어 사용 가능 || echo    ❌ python3 명령어 없음
echo.

echo [5] requirements.txt 확인...
if exist "requirements.txt" (
    echo    ✅ requirements.txt 존재함
) else (
    echo    ❌ requirements.txt 없음
)
echo.

echo [6] webui/app.py 확인...
if exist "webui\app.py" (
    echo    ✅ webui/app.py 존재함
) else (
    echo    ❌ webui/app.py 없음
)
echo.

echo ========================================
echo   진단 완료 - 위 정보를 확인하세요
echo ========================================
echo.
echo 아무 키나 누르면 종료됩니다...
pause > nul