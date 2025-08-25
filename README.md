![Good artists copy, great artists steal - Pablo Picasso](https://i.imgur.com/8XvH9kM.png)

# 🚜 SungDaeDay - 헤이데이 동적 밸런싱 시뮬레이터

**실제 헤이데이 게임 데이터 분석 및 동적 밸런싱 시뮬레이션 시스템**

> Real HayDay game data analysis and dynamic balancing simulation system

## 🌟 주요 기능 / Features

### 📊 Streamlit 대시보드 (http://localhost:8501)
- **🎯 실시간 주문 생성**: 레벨별 동적 주문 생성 (실제 헤이데이 데이터 기반)
- **📈 경제 시뮬레이션**: 어려움 지수 밸런싱을 통한 30일 경제 시뮬레이션
- **🏭 생산 체인 분석**: 모든 생산 건물의 효율성 분석
- **📋 헤이데이 데이터 탐색**: 언락 레벨, 가격, 생산 시간 인터랙티브 시각화

### 🌐 Flask 웹 UI (http://localhost:5001)
- **📊 인터랙티브 데이터 뷰어**: 한국어/영어 현지화 데이터 (Tabulator.js)
- **🎲 실시간 주문 생성기**: 상세 분석과 함께하는 실시간 주문 생성
- **🔗 Streamlit 연동**: 두 인터페이스 간 원활한 데이터 동기화
- **📱 접을 수 있는 사이드바**: 깔끔하고 반응형 인터페이스 디자인

## 🚀 빠른 시작 / Quick Start

### 처음 설치하는 경우 (Fresh Installation)

#### 1. 필수 요구사항 확인
```bash
# Python 3.8+ 확인 (Check Python 3.8+)
python3 --version

# Git 확인 (Check Git)
git --version
```

#### 2. 저장소 클론 및 설정
```bash
# 저장소 클론 (Clone repository)
git clone git@github.com:seungminkangg/SungDaeDay.git
cd SungDaeDay

# 가상환경 생성 (Create virtual environment)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치 (Install dependencies)
pip install -r requirements.txt
```

#### 3. 서버 실행 (Run Servers)

**🚀 Option 1: 두 서버 자동 실행 (추천)**
```bash
python3 start_servers.py
```

**Option 2: Flask 웹 UI만 실행**
```bash
cd webui
python3 app.py
```

**Option 3: Streamlit 대시보드만 실행**
```bash
streamlit run hayday_simulator.py --server.port 8502
```

**Option 4: 수동으로 두 서버 모두 실행 (터미널 2개 필요)**
```bash
# 터미널 1: Flask (기본)
cd webui && python3 app.py

# 터미널 2: Streamlit
streamlit run hayday_simulator.py --server.port 8502
```

#### 4. 접속 주소 (Access URLs)
- 🌐 **Flask 웹 UI (기본)**: http://localhost:5001  
- 📊 **Streamlit 대시보드**: http://localhost:8502
- 🎲 **주문 생성기**: http://localhost:5001/order-generator
- 🔗 **두 인터페이스 간 자유로운 이동 가능**

#### 🔧 문제 해결 (Troubleshooting)
- **Port already in use**: 포트가 사용 중이면 다른 포트 사용
  ```bash
  streamlit run hayday_simulator.py --server.port 8502
  ```
- **ModuleNotFoundError**: 의존성 재설치
  ```bash
  pip install -r requirements.txt --force-reinstall
  ```

## 📂 프로젝트 구조 / Project Structure

```
SungDaeDay/
├── hayday_simulator.py          # 📊 Streamlit 메인 대시보드
├── requirements.txt             # 📦 Python 의존성 목록
├── hayday_extracted_data/       # 🗃️ 원본 헤이데이 게임 데이터
│   ├── core_data/              # 📋 게임 메커니즘 CSV 파일
│   │   ├── animals.csv         # 🐄 동물 데이터
│   │   ├── bakery_goods.csv    # 🍞 베이커리 제품
│   │   ├── dairy_goods.csv     # 🥛 유제품
│   │   ├── exp_levels.csv      # ⭐ 레벨 진행
│   │   └── ...                 # 🏗️ 모든 생산 건물 데이터
│   ├── localization/           # 🌐 다국어 지원 (한국어/영어)
│   └── game_data/              # 🎮 추가 게임 데이터
└── webui/                      # 🌐 Flask 웹 인터페이스
    ├── app.py                  # 🚀 Flask 애플리케이션
    ├── templates/              # 🎨 HTML 템플릿
    │   ├── base.html           # 📄 기본 템플릿
    │   ├── data.html           # 📊 데이터 뷰어
    │   ├── orders.html         # 🚚 주문 관리
    │   ├── simulation.html     # 📈 시뮬레이션
    │   └── production.html     # 🏭 생산 분석
    └── static/                 # 🎨 CSS/JS 리소스
```

## 📸 스크린샷 / Screenshots

### 📊 Streamlit 대시보드
![Streamlit Dashboard](https://via.placeholder.com/800x400/4CAF50/white?text=Streamlit+Dashboard)

### 🌐 Flask 웹 인터페이스  
![Flask Web UI](https://via.placeholder.com/800x400/2196F3/white?text=Flask+Web+UI)

### 🎲 주문 생성기
![Order Generator](https://via.placeholder.com/800x400/FF9800/white?text=Order+Generator)

## 🎯 핵심 기능 / Key Features

### 🧠 동적 밸런싱 시스템 / Dynamic Balancing System
- **어려움 지수**: 플레이어 성과에 따른 적응형 난이도 조절
- **레벨별 언락**: 플레이어 레벨에 따른 정확한 아이템 가용성
- **실제 헤이데이 데이터**: 게임의 실제 생산 시간, 가격, 언락 레벨 적용

### 📊 데이터 기반 분석 / Data-Driven Analysis
- **20+ 생산 건물**: 모든 헤이데이 생산 체인의 완전한 분석
- **8,606개 현지화 텍스트**: 모든 게임 아이템의 한국어/영어 번역
- **경제 모델링**: 수익 최적화 및 효율성 계산

### 🔗 이중 인터페이스 시스템 / Dual Interface System
- **Streamlit**: 고급 분석 및 시뮬레이션 시각화  
- **Flask**: 데이터 탐색 및 실시간 주문 생성
- **양방향 동기화**: 인터페이스 간 원활한 데이터 공유

## 🛠️ 기술 스택 / Technical Stack

- **백엔드**: Python, Pandas, NumPy
- **Streamlit**: Plotly, 인터랙티브 위젯, 실시간 시뮬레이션
- **Flask**: Jinja2 템플릿, Bootstrap 5, Tabulator.js
- **데이터**: CSV 기반 헤이데이 게임 데이터 추출

## 📈 사용 예제 / Usage Examples

### 레벨별 주문 생성
```python
# 레벨 10 플레이어 - 기본 아이템만 사용 가능
simulator.generate_delivery_order(player_level=10, struggle_score=50)
# 결과: 빵, 버터, 옥수수 (레벨 10에 적합한 아이템)

# 레벨 50 플레이어 - 고급 아이템 사용 가능  
simulator.generate_delivery_order(player_level=50, struggle_score=30)
# 결과: 피자, 스시, 복잡한 아이템 (높은 레벨에서 언락)
```

### 경제 시뮬레이션
```python
# 30일 경제 시뮬레이션 실행
results = simulator.simulate_economy(days=30, player_level=25)
# 결과: 일일 어려움 지수, 주문 가치, 난이도 진행
```

## 🤝 Contributing

This project analyzes HayDay game mechanics for educational purposes. All data is extracted from publicly available game files.

## 📄 License

MIT License - see LICENSE file for details.

---

**🎮 Made for HayDay fans who love data-driven gameplay optimization! 🚜**
