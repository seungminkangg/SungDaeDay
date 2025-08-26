#!/bin/bash

# HayDay Simulator - macOS 네트워크 서버 실행 스크립트
# 다른 기기에서 접속 가능한 서버 모드

echo ""
echo "========================================================"
echo "    🚜 HayDay Dynamic Balancing Simulator"
echo "        macOS 네트워크 서버 v1.0"
echo "========================================================"
echo ""

# 프로젝트 루트 확인
if [ ! -d "webui" ]; then
    echo "❌ [ERROR] webui 폴더를 찾을 수 없습니다"
    echo "   현재 디렉토리: $(pwd)"
    echo "   프로젝트 루트에서 실행해주세요"
    exit 1
fi

# Python 설치 확인
echo "🐍 Python 설치 확인..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VER=$(python3 --version)
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VER=$(python --version)
else
    echo "❌ [ERROR] Python이 설치되지 않았습니다"
    echo ""
    echo "해결 방법:"
    echo "  1. Homebrew 설치: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  2. Python 설치: brew install python"
    echo "  3. 또는 python.org에서 직접 다운로드"
    exit 1
fi

echo "✅ [OK] $PYTHON_VER 감지됨"

# 가상환경 확인 및 생성 (선택사항)
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 가상환경이 없습니다. 생성하시겠습니까? (권장)"
    read -p "가상환경 생성 [y/N]: " create_venv
    if [[ $create_venv =~ ^[Yy]$ ]]; then
        echo "   가상환경 생성 중..."
        $PYTHON_CMD -m venv venv
        echo "   가상환경 활성화..."
        source venv/bin/activate
        echo "✅ 가상환경이 생성되고 활성화되었습니다"
    fi
else
    echo "🔧 가상환경 활성화 중..."
    source venv/bin/activate
    echo "✅ 가상환경 활성화됨"
fi

# 패키지 설치 확인
echo ""
echo "📦 필수 패키지 확인..."
if [ -f "requirements.txt" ]; then
    echo "   requirements.txt 발견 - 패키지 설치 확인 중..."
    $PYTHON_CMD -c "import flask, pandas" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️  필수 패키지가 없습니다. 설치 중..."
        $PYTHON_CMD -m pip install --upgrade pip
        $PYTHON_CMD -m pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            echo "✅ requirements.txt 패키지 설치 완료"
        else
            echo "❌ 패키지 설치 실패"
            exit 1
        fi
    else
        echo "✅ 필수 패키지 설치 확인됨"
    fi
else
    echo "   개별 패키지 설치 확인 중..."
    $PYTHON_CMD -c "import flask, pandas" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️  필수 패키지가 없습니다. 설치 중..."
        $PYTHON_CMD -m pip install --upgrade pip
        $PYTHON_CMD -m pip install flask pandas numpy requests openpyxl
        if [ $? -eq 0 ]; then
            echo "✅ 필수 패키지 설치 완료"
        else
            echo "❌ 패키지 설치 실패"
            exit 1
        fi
    else
        echo "✅ 필수 패키지 설치 확인됨"
    fi
fi

# 포트 사용 확인
echo ""
echo "🔍 포트 5001 상태 확인..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  포트 5001이 이미 사용 중입니다"
    echo "   기존 서버가 실행 중이거나 다른 프로그램이 사용 중일 수 있습니다"
    echo ""
    read -p "계속 진행하시겠습니까? [y/N]: " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        echo "스크립트를 종료합니다"
        exit 0
    fi
fi

# 로컬 네트워크 IP 주소 찾기
echo ""
echo "🌐 네트워크 설정 확인..."
LOCAL_IP=""

# WiFi IP 주소 확인 (가장 일반적)
WIFI_IP=$(ifconfig en0 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}')
if [ ! -z "$WIFI_IP" ] && [[ $WIFI_IP =~ ^192\.168\.|^10\.|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-1]\. ]]; then
    LOCAL_IP=$WIFI_IP
fi

# 이더넷 IP 주소 확인 (WiFi가 없는 경우)
if [ -z "$LOCAL_IP" ]; then
    ETHERNET_IP=$(ifconfig en1 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}')
    if [ ! -z "$ETHERNET_IP" ] && [[ $ETHERNET_IP =~ ^192\.168\.|^10\.|^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-1]\. ]]; then
        LOCAL_IP=$ETHERNET_IP
    fi
fi

# 기타 네트워크 인터페이스 확인
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | grep -E '192\.168\.|10\.|172\.1[6-9]\.|172\.2[0-9]\.|172\.3[0-1]\.' | head -1 | awk '{print $2}')
fi

# 방화벽 설정 안내 (macOS는 기본적으로 허용적)
echo ""
echo "🔥 macOS 방화벽 확인..."
if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
    echo "⚠️  방화벽이 활성화되어 있습니다"
    echo "   다른 기기에서 접속할 수 없을 수 있습니다"
    echo ""
    echo "해결 방법:"
    echo "  1. 시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽"
    echo "  2. '방화벽 옵션' 클릭"
    echo "  3. 'Python' 또는 'Python3'를 찾아서 '들어오는 연결 허용' 설정"
    echo ""
    read -p "계속 진행하시겠습니까? [y/N]: " continue_firewall
    if [[ ! $continue_firewall =~ ^[Yy]$ ]]; then
        echo "스크립트를 종료합니다"
        exit 0
    fi
else
    echo "✅ 방화벽이 비활성화되어 있거나 허용적으로 설정됨"
fi

# 서버 시작
echo ""
echo "🚀 HayDay Flask 웹 서버 시작 중..."
cd webui

echo ""
echo "========================================================"
echo "              🎯 서버가 시작되었습니다!"
echo "========================================================"
echo ""
echo "📍 로컬 접속 주소:"
echo "   http://localhost:5001"
echo "   http://127.0.0.1:5001"
echo ""

if [ ! -z "$LOCAL_IP" ]; then
    echo "🌐 네트워크 접속 주소 (다른 기기에서 접속):"
    echo "   📱 스마트폰/태블릿: http://$LOCAL_IP:5001"
    echo "   💻 다른 컴퓨터: http://$LOCAL_IP:5001"
    echo ""
    echo "✅ 자동 감지된 IP: $LOCAL_IP"
else
    echo "⚠️  네트워크 IP를 자동으로 찾을 수 없습니다"
    echo ""
    echo "수동으로 확인하는 방법:"
    echo "  1. 터미널에서: ifconfig | grep 'inet '"
    echo "  2. 192.168.x.x 또는 10.x.x.x 형태의 IP 찾기"
    echo "  3. http://찾은IP:5001 로 접속"
fi

echo ""
echo "========================================================"
echo "                   📋 사용 가이드"
echo "========================================================"
echo ""
echo "🎮 주요 기능:"
echo "  • 메인 페이지: / (대시보드)"
echo "  • 주문 관리: /orders"
echo "  • 데이터 분석: /data"
echo "  • 성과 대시보드: /dashboard"
echo ""
echo "🛠️  서버 관리:"
echo "  • 서버 중지: Ctrl+C"
echo "  • 서버 재시작: 이 스크립트 다시 실행"
echo ""
echo "🔧 문제 해결:"
echo "  • 접속 안 됨: 같은 WiFi에 연결되어 있는지 확인"
echo "  • 방화벽 오류: 시스템 환경설정에서 Python 허용"
echo "  • 포트 충돌: 다른 프로그램에서 5001 포트 사용 중"
echo ""
echo "========================================================"
echo ""

# 자동으로 브라우저 열기 (선택사항)
sleep 2
if command -v open &> /dev/null; then
    echo "🌐 기본 브라우저에서 열기..."
    open "http://localhost:5001"
fi

echo ""
echo "서버 실행 중... (Ctrl+C로 중지)"
echo ""

# Flask 서버 실행
$PYTHON_CMD app.py