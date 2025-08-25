@echo off
chcp 65001 > nul
echo Starting HayDay Dynamic Balancing Simulator
echo ============================================

echo Starting Flask Web UI...
cd webui
start "Flask Server" python app.py

echo Starting Streamlit Dashboard...
cd ..
start "Streamlit Dashboard" streamlit run hayday_simulator.py --server.address 0.0.0.0 --server.port 8502

echo.
echo Servers are starting...
echo Flask Web UI: http://localhost:5001
echo Streamlit Dashboard: http://localhost:8502
echo Network Access: http://YOUR_LOCAL_IP:5001
echo.
echo Press any key to close this window
pause > nul