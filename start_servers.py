#!/usr/bin/env python3
"""
HayDay Dynamic Balancing - 두 서버 동시 실행 스크립트
Flask 앱(기본)과 Streamlit 앱을 동시에 실행합니다.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from concurrent.futures import ThreadPoolExecutor

class ServerManager:
    def __init__(self):
        self.processes = []
        self.flask_port = 5001
        self.streamlit_port = 8502
        
    def start_flask(self):
        """Flask 서버 시작"""
        try:
            print("🌐 Flask 웹 UI 시작 중...")
            os.chdir(os.path.join(os.path.dirname(__file__), 'webui'))
            
            # 가상환경 활성화 및 Flask 실행
            if os.name == 'nt':  # Windows
                cmd = f'..\\venv\\Scripts\\python.exe app.py'
            else:  # Unix/Linux/macOS
                cmd = '../venv/bin/python3 app.py'
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.processes.append(('flask', process))
            
            # Flask 로그 출력
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"[Flask] {line.strip()}")
                    if "Running on" in line:
                        print(f"✅ Flask 웹 UI 실행됨: http://localhost:{self.flask_port}")
                        
        except Exception as e:
            print(f"❌ Flask 서버 시작 실패: {e}")
    
    def start_streamlit(self):
        """Streamlit 서버 시작"""
        try:
            print("📊 Streamlit 대시보드 시작 중...")
            os.chdir(os.path.dirname(__file__))
            
            # 가상환경 활성화 및 Streamlit 실행
            if os.name == 'nt':  # Windows
                cmd = f'venv\\Scripts\\streamlit.exe run hayday_simulator.py --server.port {self.streamlit_port}'
            else:  # Unix/Linux/macOS
                cmd = f'venv/bin/streamlit run hayday_simulator.py --server.port {self.streamlit_port}'
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.processes.append(('streamlit', process))
            
            # Streamlit 로그 출력
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"[Streamlit] {line.strip()}")
                    if f"localhost:{self.streamlit_port}" in line:
                        print(f"✅ Streamlit 대시보드 실행됨: http://localhost:{self.streamlit_port}")
                        
        except Exception as e:
            print(f"❌ Streamlit 서버 시작 실패: {e}")
    
    def check_port(self, port):
        """포트 사용 가능 여부 확인"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except OSError:
                return False
    
    def kill_existing_processes(self):
        """기존 프로세스 종료"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(f'taskkill /F /IM python.exe', shell=True, capture_output=True)
                subprocess.run(f'taskkill /F /IM streamlit.exe', shell=True, capture_output=True)
            else:  # Unix/Linux/macOS
                subprocess.run(f'pkill -f "streamlit.*{self.streamlit_port}"', shell=True, capture_output=True)
                subprocess.run(f'pkill -f ".*{self.flask_port}"', shell=True, capture_output=True)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 기존 프로세스 종료 중 오류: {e}")
    
    def start_servers(self):
        """두 서버 동시 시작"""
        print("🚜 HayDay Dynamic Balancing - 서버 시작")
        print("=" * 60)
        
        # 기존 프로세스 종료
        self.kill_existing_processes()
        
        # 포트 확인
        if not self.check_port(self.flask_port):
            print(f"⚠️ 포트 {self.flask_port}가 사용 중입니다.")
        if not self.check_port(self.streamlit_port):
            print(f"⚠️ 포트 {self.streamlit_port}가 사용 중입니다.")
        
        print("🔄 서버 시작 중...")
        
        # ThreadPoolExecutor로 두 서버를 병렬 실행
        with ThreadPoolExecutor(max_workers=2) as executor:
            flask_future = executor.submit(self.start_flask)
            streamlit_future = executor.submit(self.start_streamlit)
            
            # 서버 시작 완료까지 대기
            time.sleep(5)
            
            print("\n" + "=" * 60)
            print("🎉 서버 시작 완료!")
            print(f"📍 Flask 웹 UI (기본): http://localhost:{self.flask_port}")
            print(f"📍 Streamlit 대시보드: http://localhost:{self.streamlit_port}")
            print("=" * 60)
            print("💡 Flask 웹 UI가 기본 인터페이스입니다.")
            print("🔗 두 인터페이스를 자유롭게 오갈 수 있습니다.")
            print("⚠️  종료하려면 Ctrl+C를 누르세요")
            print("=" * 60)
            
        # 프로세스 감시
        try:
            while True:
                time.sleep(1)
                # 프로세스 상태 확인
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"❌ {name} 서버가 종료되었습니다.")
        except KeyboardInterrupt:
            self.cleanup()
    
    def cleanup(self):
        """서버 정리 및 종료"""
        print("\n🛑 서버 종료 중...")
        
        for name, process in self.processes:
            try:
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:  # Unix/Linux/macOS
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                print(f"✅ {name} 서버 종료 완료")
            except Exception as e:
                print(f"⚠️ {name} 서버 종료 중 오류: {e}")
        
        print("👋 모든 서버가 정상적으로 종료되었습니다.")
        sys.exit(0)

def main():
    """메인 실행 함수"""
    # 가상환경 확인
    venv_path = os.path.join(os.path.dirname(__file__), 'venv')
    if not os.path.exists(venv_path):
        print("❌ 가상환경이 설정되지 않았습니다.")
        print("먼저 다음 명령어를 실행하세요:")
        print("python3 -m venv venv")
        print("source venv/bin/activate  # Windows: venv\\Scripts\\activate")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # 서버 매니저 시작
    manager = ServerManager()
    
    try:
        manager.start_servers()
    except KeyboardInterrupt:
        manager.cleanup()
    except Exception as e:
        print(f"❌ 서버 시작 중 오류: {e}")
        manager.cleanup()

if __name__ == "__main__":
    main()