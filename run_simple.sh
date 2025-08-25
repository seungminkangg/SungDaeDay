#!/bin/bash

echo "HayDay Dynamic Balancing Simulator - Setup & Run"
echo "================================================="

# Python 설치 확인
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Python 명령어 결정
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version

echo ""
echo "Installing required packages..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "WARNING: Some packages failed to install"
    echo "Trying alternative installation..."
    $PYTHON_CMD -m pip install pandas numpy streamlit plotly flask jinja2 matplotlib seaborn requests openpyxl
fi

echo ""
echo "Starting servers..."

# Flask 서버 백그라운드 실행
echo "Starting Flask Web UI..."
cd webui
$PYTHON_CMD app.py &
FLASK_PID=$!

# 잠시 대기
sleep 3

# Streamlit 서버 백그라운드 실행
echo "Starting Streamlit Dashboard..."
cd ..
streamlit run hayday_simulator.py --server.address 0.0.0.0 --server.port 8502 &
STREAMLIT_PID=$!

echo ""
echo "================================================="
echo "Servers started successfully!"
echo "Flask Web UI: http://localhost:5001"
echo "Streamlit Dashboard: http://localhost:8502"
echo "Network Access: http://YOUR_LOCAL_IP:5001"
echo "================================================="
echo "Press Ctrl+C to stop all servers"
echo ""

# 종료 시그널 처리
trap 'echo "Stopping servers..."; kill $FLASK_PID $STREAMLIT_PID 2>/dev/null; exit' INT

# 서버들이 실행 중인 동안 대기
wait