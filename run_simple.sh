#!/bin/bash

# 색상 정의 (터미널 지원)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    GRAY='\033[0;37m'
    NC='\033[0m' # No Color
else
    RED='' GREEN='' YELLOW='' BLUE='' PURPLE='' CYAN='' GRAY='' NC=''
fi

echo ""
echo "${CYAN}======================================================${NC}"
echo "${CYAN}  [HayDay Dynamic Balancing Simulator - macOS/Linux]${NC}"
echo "${CYAN}           크로스플랫폼 실행 스크립트 v2.0${NC}"
echo "${CYAN}======================================================${NC}"
echo ""

# 프로젝트 루트 디렉토리 확인
if [ ! -d "webui" ]; then
    echo "${RED}[ERROR]${NC} webui 폴더를 찾을 수 없습니다"
    echo "   현재 디렉토리: $(pwd)"
    echo "   프로젝트 루트에서 실행해주세요"
    exit 1
fi

# Python 설치 확인
echo "Python 설치 확인..."
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VER=$(python3 --version)
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VER=$(python --version)
else
    echo "${RED}[ERROR]${NC} Python이 설치되지 않았습니다"
    echo ""
    echo "해결 방법:"
    echo "  ${YELLOW}macOS:${NC} brew install python3"
    echo "  ${YELLOW}Ubuntu/Debian:${NC} sudo apt install python3 python3-pip"
    echo "  ${YELLOW}CentOS/RHEL:${NC} sudo yum install python3 python3-pip"
    echo "  ${YELLOW}수동 설치:${NC} https://python.org/downloads/"
    exit 1
fi

echo "${GREEN}[OK]${NC} $PYTHON_VER 감지됨"

# pip 확인
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "${YELLOW}[WARNING]${NC} pip가 설치되지 않음 - 설치 시도"
    if command -v curl &> /dev/null; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    else
        echo "${RED}[ERROR]${NC} pip 설치 실패. 수동으로 설치하세요:"
        echo "  curl https://bootstrap.pypa.io/get-pip.py | python3"
        exit 1
    fi
fi

# 필수 패키지 확인
echo ""
echo "필수 패키지 확인..."

if ! $PYTHON_CMD -c "import flask, pandas" &> /dev/null; then
    echo "${YELLOW}[WARNING]${NC} 필수 패키지가 설치되지 않음 - 자동 설치 시작"
    echo ""
    
    echo "pip 업그레이드..."
    $PYTHON_CMD -m pip install --upgrade pip --quiet
    
    # requirements.txt가 있으면 사용
    if [ -f "requirements.txt" ]; then
        echo "${GREEN}[OK]${NC} requirements.txt 발견 - 자동 설치"
        $PYTHON_CMD -m pip install -r requirements.txt --quiet
        
        if [ $? -ne 0 ]; then
            echo "${YELLOW}[WARNING]${NC} requirements.txt 설치 실패 - 수동 설치 시도"
            $PYTHON_CMD -m pip install pandas numpy flask jinja2 requests openpyxl --quiet
        fi
    else
        echo "${YELLOW}[WARNING]${NC} requirements.txt 없음 - 필수 패키지 설치"
        $PYTHON_CMD -m pip install pandas numpy flask jinja2 requests openpyxl --quiet
    fi
    
    if [ $? -ne 0 ]; then
        echo "${YELLOW}[WARNING]${NC} 일부 패키지 설치 실패 - 사용자 설치 시도"
        $PYTHON_CMD -m pip install --user pandas numpy flask jinja2 requests openpyxl --quiet
        
        if [ $? -ne 0 ]; then
            echo "${RED}[ERROR]${NC} 패키지 설치 완전 실패"
            echo ""
            echo "해결 방법:"
            echo "  1. 인터넷 연결 확인"
            echo "  2. pip 권한 확인 (sudo pip install 시도)"
            echo "  3. 가상환경 사용 권장"
            exit 1
        fi
    fi
    echo "${GREEN}[OK]${NC} 패키지 설치 완료"
else
    echo "${GREEN}[OK]${NC} 필수 패키지 설치 확인됨"
fi

# 포트 사용 확인
echo ""
echo "포트 상태 확인..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "${YELLOW}[WARNING]${NC} 포트 5001이 이미 사용 중입니다"
    echo "   기존 HayDay Simulator가 실행 중이거나 다른 프로그램이 사용 중일 수 있습니다"
    echo ""
    read -p "   계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "스크립트를 중단합니다"
        exit 1
    fi
fi

echo ""
echo "HayDay Flask Web UI 시작 중..."

# Flask 서버 백그라운드 실행
echo "   서버를 백그라운드에서 시작합니다..."
cd webui
$PYTHON_CMD app.py > ../flask.log 2>&1 &
FLASK_PID=$!
cd ..

# 서버 시작 확인
echo "   서버 초기화 대기 중..."
sleep 3

# 서버 상태 확인
if kill -0 $FLASK_PID 2>/dev/null; then
    echo "${GREEN}[OK]${NC} Flask 서버가 성공적으로 시작됨 (PID: $FLASK_PID)"
else
    echo "${RED}[ERROR]${NC} Flask 서버 시작 실패"
    echo "로그 확인: cat flask.log"
    exit 1
fi

# 브라우저에서 열기 (macOS/Linux 감지)
if command -v open &> /dev/null; then
    # macOS
    echo "   기본 브라우저에서 열기 (macOS)..."
    open http://localhost:5001 &
elif command -v xdg-open &> /dev/null; then
    # Linux
    echo "   기본 브라우저에서 열기 (Linux)..."
    xdg-open http://localhost:5001 &
else
    echo "   브라우저를 수동으로 열어주세요"
fi

echo ""
echo "${CYAN}======================================================${NC}"
echo "${CYAN}                [실행 완료!]${NC}"
echo "${CYAN}======================================================${NC}"
echo ""
echo "접속 주소:"
echo "  ${GREEN}┌─────────────────────────────────────────────────┐${NC}"
echo "  ${GREEN}│${NC} 메인 페이지: http://localhost:5001            ${GREEN}│${NC}"
echo "  ${GREEN}│${NC} 주문 관리:   http://localhost:5001/orders     ${GREEN}│${NC}"
echo "  ${GREEN}│${NC} 데이터 분석: http://localhost:5001/data       ${GREEN}│${NC}"
echo "  ${GREEN}│${NC} 대시보드:    http://localhost:5001/dashboard  ${GREEN}│${NC}"
echo "  ${GREEN}└─────────────────────────────────────────────────┘${NC}"
echo ""
echo "네트워크 접속:"
echo "  1. 내 IP 확인: ${YELLOW}ifconfig | grep inet${NC} 또는 ${YELLOW}ip addr${NC}"
echo "  2. http://내IP주소:5001 로 접속"
echo ""
echo "서버 관리:"
echo "  - ${RED}서버 중지: Ctrl+C${NC} (이 터미널에서)"
echo "  - 서버 재시작: 이 스크립트 다시 실행"
echo "  - 로그 확인: ${YELLOW}tail -f flask.log${NC}"
echo ""
echo "추가 기능:"
echo "  - Streamlit 대시보드: ${PURPLE}streamlit run hayday_simulator.py${NC}"
echo "  - 포트 변경: webui/app.py에서 port=5001 수정"
echo ""

# 종료 시그널 처리
cleanup() {
    echo ""
    echo "${YELLOW}서버를 중지하는 중...${NC}"
    if kill $FLASK_PID 2>/dev/null; then
        echo "${GREEN}[OK]${NC} Flask 서버가 중지되었습니다"
    fi
    
    # 로그 파일 정리 여부 확인
    if [ -f "flask.log" ]; then
        read -p "로그 파일을 삭제하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm flask.log
            echo "로그 파일이 삭제되었습니다"
        fi
    fi
    
    echo "스크립트를 종료합니다"
    exit 0
}

trap cleanup INT

# 서버 실행 상태 모니터링
echo "${GRAY}서버가 백그라운드에서 실행 중입니다...${NC}"
echo "${GRAY}Ctrl+C를 눌러 서버를 중지하세요${NC}"
echo ""

# 서버가 실행 중인 동안 대기
while kill -0 $FLASK_PID 2>/dev/null; do
    sleep 5
done

echo "${RED}[WARNING]${NC} Flask 서버가 예상치 못하게 중지되었습니다"
echo "로그 확인: cat flask.log"