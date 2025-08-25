#!/bin/bash

echo "Starting HayDay Dynamic Balancing Simulator"
echo "============================================"

# Flask 서버 백그라운드 실행
echo "Starting Flask Web UI..."
cd webui
python app.py &
FLASK_PID=$!

# 잠시 대기
sleep 3

# Streamlit 서버 백그라운드 실행
echo "Starting Streamlit Dashboard..."
cd ..
streamlit run hayday_simulator.py --server.address 0.0.0.0 --server.port 8502 &
STREAMLIT_PID=$!

echo ""
echo "============================================"
echo "Servers started successfully!"
echo "Flask Web UI: http://localhost:5001"
echo "Streamlit Dashboard: http://localhost:8502"
echo "Network Access: http://YOUR_LOCAL_IP:5001"
echo "============================================"
echo "Press Ctrl+C to stop all servers"
echo ""

# 종료 시그널 처리
trap 'echo "Stopping servers..."; kill $FLASK_PID $STREAMLIT_PID 2>/dev/null; exit' INT

# 서버들이 실행 중인 동안 대기
wait