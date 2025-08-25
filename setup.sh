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
echo "${CYAN}  [HayDay Dynamic Balancing Simulator - Setup]${NC}"
echo "${CYAN}         macOS/Linux 자동 설치 스크립트 v2.0${NC}"
echo "${CYAN}======================================================${NC}"
echo ""

# 관리자 권한 확인 (선택적)
if [ "$EUID" -eq 0 ]; then
    echo "${YELLOW}[WARNING]${NC} root 권한으로 실행됨 (권장하지 않음)"
    echo "   일반 사용자 권한으로 실행하는 것을 권장합니다"
    echo ""
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "스크립트를 중단합니다"
        exit 1
    fi
else
    echo "${GREEN}[OK]${NC} 일반 사용자 권한으로 실행됨"
fi

# Python 설치 확인
echo ""
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
    echo "Python 설치 가이드:"
    echo "  ${YELLOW}macOS:${NC}"
    echo "    - Homebrew: ${CYAN}brew install python${NC}"
    echo "    - 공식 설치: https://python.org/downloads/"
    echo ""
    echo "  ${YELLOW}Ubuntu/Debian:${NC}"
    echo "    - ${CYAN}sudo apt update && sudo apt install python3 python3-pip${NC}"
    echo ""
    echo "  ${YELLOW}CentOS/RHEL:${NC}"
    echo "    - ${CYAN}sudo yum install python3 python3-pip${NC}"
    echo ""
    echo "  ${YELLOW}Fedora:${NC}"
    echo "    - ${CYAN}sudo dnf install python3 python3-pip${NC}"
    echo ""
    echo "  ${YELLOW}Arch Linux:${NC}"
    echo "    - ${CYAN}sudo pacman -S python python-pip${NC}"
    echo ""
    exit 1
fi

echo "${GREEN}[OK]${NC} $PYTHON_VER 감지됨"

# pip 확인 및 설치
echo ""
echo "pip 확인..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "${YELLOW}[WARNING]${NC} pip가 설치되지 않음 - 설치 시도"
    
    if command -v curl &> /dev/null; then
        echo "curl을 사용하여 pip 설치..."
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py --user
        rm get-pip.py
    elif command -v wget &> /dev/null; then
        echo "wget을 사용하여 pip 설치..."
        wget https://bootstrap.pypa.io/get-pip.py
        $PYTHON_CMD get-pip.py --user
        rm get-pip.py
    else
        echo "${RED}[ERROR]${NC} curl 또는 wget이 필요합니다"
        echo ""
        echo "해결 방법:"
        echo "  ${YELLOW}macOS:${NC} brew install curl wget"
        echo "  ${YELLOW}Ubuntu/Debian:${NC} sudo apt install curl wget"
        echo "  ${YELLOW}CentOS/RHEL:${NC} sudo yum install curl wget"
        exit 1
    fi
    
    # pip 설치 확인
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        echo "${RED}[ERROR]${NC} pip 설치 실패"
        exit 1
    fi
fi

PIP_VER=$($PYTHON_CMD -m pip --version)
echo "${GREEN}[OK]${NC} $PIP_VER 감지됨"

# pip 업그레이드
echo ""
echo "pip 업그레이드..."
$PYTHON_CMD -m pip install --upgrade pip --user --quiet
if [ $? -eq 0 ]; then
    echo "${GREEN}[OK]${NC} pip 업그레이드 완료"
else
    echo "${YELLOW}[WARNING]${NC} pip 업그레이드 실패 - 계속 진행"
fi

# 패키지 설치
echo ""
echo "requirements.txt 파일 확인..."
if [ -f "requirements.txt" ]; then
    echo "${GREEN}[OK]${NC} requirements.txt 발견 - 자동 설치 진행"
    
    $PYTHON_CMD -m pip install -r requirements.txt --user --quiet
    if [ $? -eq 0 ]; then
        echo "${GREEN}[OK]${NC} requirements.txt로 패키지 설치 완료"
    else
        echo "${YELLOW}[WARNING]${NC} requirements.txt 설치 실패 - 수동 설치 진행"
        MANUAL_INSTALL=true
    fi
else
    echo "${YELLOW}[WARNING]${NC} requirements.txt 없음 - 수동 설치 진행"
    MANUAL_INSTALL=true
fi

# 수동 패키지 설치
if [ "$MANUAL_INSTALL" = true ]; then
    echo ""
    echo "필수 패키지 수동 설치..."
    echo "   (네트워크 속도에 따라 1-5분 소요)"
    
    PACKAGES="pandas numpy streamlit plotly flask jinja2 matplotlib seaborn requests openpyxl"
    echo ""
    echo "설치할 패키지: $PACKAGES"
    echo ""
    
    $PYTHON_CMD -m pip install $PACKAGES --user --quiet
    if [ $? -eq 0 ]; then
        echo "${GREEN}[OK]${NC} 모든 패키지 설치 완료"
    else
        echo "${YELLOW}[WARNING]${NC} 일부 패키지 설치 실패 - 개별 설치 시도"
        
        # 개별 패키지 설치
        for package in $PACKAGES; do
            echo "   - $package 설치 중..."
            $PYTHON_CMD -m pip install $package --user --quiet
            if [ $? -eq 0 ]; then
                echo "     ${GREEN}[OK]${NC} $package 설치 성공"
            else
                echo "     ${RED}[FAIL]${NC} $package 설치 실패"
            fi
        done
    fi
fi

# 설치 검증
echo ""
echo "설치 검증..."
FAILED_PACKAGES=""

for package in "pandas" "numpy" "flask" "jinja2" "requests"; do
    if ! $PYTHON_CMD -c "import $package" &> /dev/null; then
        FAILED_PACKAGES="$FAILED_PACKAGES $package"
    fi
done

if [ -n "$FAILED_PACKAGES" ]; then
    echo "${RED}[ERROR]${NC} 다음 필수 패키지 설치 실패:$FAILED_PACKAGES"
    echo ""
    echo "해결 방법:"
    echo "  1. 인터넷 연결 확인"
    echo "  2. Python 권한 확인"
    echo "  3. 가상환경 사용 권장:"
    echo "     ${CYAN}python3 -m venv venv${NC}"
    echo "     ${CYAN}source venv/bin/activate${NC}"
    echo "     ${CYAN}pip install -r requirements.txt${NC}"
    exit 1
else
    echo "${GREEN}[OK]${NC} 모든 필수 패키지 검증 완료"
fi

# 실행 권한 설정
echo ""
echo "실행 권한 설정..."
if [ -f "run_simple.sh" ]; then
    chmod +x run_simple.sh
    echo "${GREEN}[OK]${NC} run_simple.sh 실행 권한 설정"
fi

if [ -f "setup.sh" ]; then
    chmod +x setup.sh
    echo "${GREEN}[OK]${NC} setup.sh 실행 권한 설정"
fi

echo ""
echo "${CYAN}======================================================${NC}"
echo "${CYAN}                [설치 완료!]${NC}"
echo "${CYAN}======================================================${NC}"
echo ""
echo "시뮬레이터 실행 방법:"
echo "  1. ${GREEN}[추천]${NC} ./run_simple.sh"
echo "  2. bash run_simple.sh"
echo "  3. chmod +x run_simple.sh && ./run_simple.sh"
echo ""
echo "접속 주소:"
echo "  - 메인 UI: http://localhost:5001 (주문 관리)"
echo "  - 대시보드: http://localhost:8502 (데이터 분석)"
echo ""
echo "네트워크 접속:"
echo "  1. IP 확인: ${YELLOW}ifconfig | grep inet${NC} 또는 ${YELLOW}ip addr show${NC}"
echo "  2. http://YOUR_IP:5001 로 접속"
echo ""
echo "문제 해결:"
echo "  - 포트 충돌: 다른 프로그램이 5001/8502 포트 사용 중일 수 있음"
echo "  - 권한 문제: 가상환경 사용 권장"
echo "  - 패키지 오류: ${CYAN}pip install --user 패키지명${NC}"
echo ""
echo "고급 사용법:"
echo "  - 가상환경 생성: ${CYAN}python3 -m venv hayday_env${NC}"
echo "  - 가상환경 활성화: ${CYAN}source hayday_env/bin/activate${NC}"
echo "  - Streamlit만 실행: ${CYAN}streamlit run hayday_simulator.py${NC}"
echo ""

# 실행 여부 선택
echo "지금 시뮬레이터를 실행하시겠습니까? (Y/n)"
read -p ": " -r
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "${GREEN}설정이 완료되었습니다!${NC}"
    echo "언제든지 ${CYAN}./run_simple.sh${NC}를 실행하세요."
else
    echo ""
    echo "시뮬레이터 시작 중..."
    sleep 1
    ./run_simple.sh
fi