![Good artists copy, great artists steal - Pablo Picasso](./ca7de3f42d939a1f0eb6f7b169baa2c4.jpg)

# 🚜 SungDaeDay - 헤이데이 동적 밸런싱 시뮬레이터

**실제 헤이데이 게임 데이터 분석 및 동적 밸런싱 시뮬레이션 시스템**

> Real HayDay game data analysis and dynamic balancing simulation system

[![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/seungminkangg/SungDaeDay)
[![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=F0F0F0)](https://github.com/seungminkangg/SungDaeDay)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/seungminkangg/SungDaeDay)

## 🌟 최신 기능 / Latest Features

### 🦎 **NEW!** 진짜 도마뱀 애니메이션
- **자연스러운 기어다니기**: 물리학 기반 움직임 & 구불구불한 경로
- **클릭 폭발 효과**: 20개 컬러풀한 파티클 폭발 💥
- **부활 시스템**: 10초 후 자동 부활
- **인터랙티브**: 클릭 가능한 이스터 에그

### 🎛️ **NEW!** 고급 파라미터 시스템
- **자동 모드**: 실제 HayDay 로직 (레벨별 어려움 지수 자동 생성)
- **수동 모드**: 모든 파라미터 직접 조절 (어려움 0-100, 가치 배율 50%-300%)
- **프리셋 시스템**: 설정 저장/로드 (LocalStorage)
- **실시간 적용**: 즉시 반영되는 파라미터 변경

### 🏗️ **완전한 HayDay 시뮬레이션**
- **465개 건물 데이터**: 모든 생산 건물의 언락레벨 적용
- **400+ 아이템**: 57개 생산 건물에서 나오는 모든 제품
- **레벨 기반 필터링**: 플레이어 레벨에 따른 정확한 아이템 제한
- **보트 시스템**: 레벨 17+ 보트 언락 (그 전에는 트럭으로 대체)

### 🌐 **메인 인터페이스**: http://localhost:5001 (주문 관리)
- **🎯 스마트 주문 생성**: 레벨별 동적 주문 (실제 헤이데이 로직)
- **📊 실시간 통계**: 주문 가치, 난이도, 생산시간 분석
- **🎮 게임화**: 도마뱀 애니메이션 & 인터랙티브 요소
- **💾 프리셋 관리**: 사용자 설정 영구 저장

### 📊 **Streamlit 대시보드**: http://localhost:8503
- **📈 경제 시뮬레이션**: 어려움 지수 밸런싱을 통한 30일 시뮬레이션
- **🏭 생산 체인 분석**: 모든 생산 건물의 효율성 분석  
- **📋 데이터 탐색**: 언락 레벨, 가격, 생산 시간 인터랙티브 시각화
- **🔗 실시간 연동**: Flask UI와 데이터 동기화

## 🚀 빠른 시작 / Quick Start

---

## 🪟 **Windows 개발환경 첫 설정 가이드** (Windows First-Time Setup)

### **1단계: Python 설치**
1. **Python 공식 웹사이트** 방문: https://www.python.org/downloads/
2. **"Download Python 3.11.x"** 클릭 (최신 안정 버전)
3. 설치 시 **⚠️ 중요**: **"Add Python to PATH"** 체크박스 꼭 선택!
4. **"Install Now"** 클릭

### **2단계: Git 설치**
1. **Git 공식 웹사이트** 방문: https://git-scm.com/download/win
2. **"Download for Windows"** 클릭
3. 기본 설정으로 설치 진행

### **3단계: 개발환경 확인**
**Command Prompt (관리자 권한)** 또는 **PowerShell** 열고:
```cmd
# Python 설치 확인
python --version
# 출력 예: Python 3.11.5

# pip 설치 확인  
pip --version
# 출력 예: pip 23.2.1

# Git 설치 확인
git --version
# 출력 예: git version 2.41.0.windows.1
```

### **4단계: 프로젝트 다운로드**
```cmd
# 원하는 폴더로 이동 (예: 바탕화면)
cd C:\Users\%USERNAME%\Desktop

# GitHub에서 프로젝트 다운로드
git clone https://github.com/seungminkangg/SungDaeDay.git

# 프로젝트 폴더로 이동
cd SungDaeDay
```

### **5단계: 자동 설정 및 실행 (추천)**

**✨ 완전 자동 방법 (한 번에 설치+실행):**
```cmd
# 더블클릭으로 실행하거나 CMD에서:
run_simple.bat
```

**🔧 수동 설정 (처음 한 번만):**
```cmd
# 라이브러리 설치만 따로 하고 싶다면:
setup.bat

# 그 후 실행:
run_simple.bat
```

### **6단계: 대체 실행 방법들**

**Git Bash 사용 (추천 - 더 안정적):**
```bash
# Git Bash에서 실행
./run_simple.sh
```

**수동 실행 (고급 사용자용):**
```cmd
# 방법 1: 기존 자동 실행 스크립트
python start_servers.py

# 방법 2: Flask 웹 UI만 실행
cd webui
python app.py

# 방법 3: Streamlit만 실행  
streamlit run hayday_simulator.py --server.address 0.0.0.0 --server.port 8502
```

### **6단계: 브라우저에서 확인**
- **Flask 웹 UI**: http://localhost:5001 (기본)
- **Streamlit 대시보드**: http://localhost:8502

### **🔧 Windows 문제해결**

#### **"python을 찾을 수 없습니다" 오류**
```cmd
# Python 경로 수동 추가 (재부팅 후 적용)
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"
# 또는 Python 재설치시 "Add to PATH" 체크
```

#### **"pip를 찾을 수 없습니다" 오류**  
```cmd
# pip 재설치
python -m ensurepip --upgrade
```

#### **"모듈을 찾을 수 없습니다" 오류**
```cmd
# 의존성 강제 재설치
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

#### **포트 사용 중 오류**
```cmd
# 사용 중인 프로세스 확인 및 종료 (관리자 권한 필요)
netstat -ano | findstr :5001
taskkill /PID [PID번호] /F

# 또는 다른 포트 사용
streamlit run hayday_simulator.py --server.port 8503
```

---

## 🐧 **macOS/Linux 빠른 설정**

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

---

# 🧮 **동적 밸런싱 수식 원리** (Dynamic Balancing Formula Principles)

## 🎯 **핵심 시스템 개요**

HayDay 동적 밸런싱 시뮬레이터는 **실제 게임의 경제 시스템**을 정확하게 모델링하여, 플레이어의 행동 패턴과 게임 난이도를 실시간으로 조절하는 복합적인 알고리즘을 구현합니다.

## 📊 **1. 어려움 지수(Struggle Score) 계산 시스템**

### **기본 공식**
```python
struggle_score = base_difficulty + time_pressure_factor + resource_scarcity_factor + completion_rate_factor
```

### **상세 구성 요소**

#### **A. 기본 난이도 (Base Difficulty)**
```python
base_difficulty = player_level * 0.5 + random.uniform(-5, 5)
```
- **목적**: 플레이어 레벨에 따른 기본적인 게임 난이도 설정
- **레벨 1**: ~0.5점, **레벨 50**: ~25점, **레벨 100**: ~50점
- **랜덤 요소**: ±5점 변동으로 예측 불가능성 추가

#### **B. 시간 압박 요소 (Time Pressure Factor)**
```python
time_pressure = min(15, max(-15, (target_time - actual_time) / target_time * 20))
```
- **빠른 완료**: 음수 값 (난이도 감소)
- **느린 완료**: 양수 값 (난이도 증가)  
- **범위**: -15점 ~ +15점

#### **C. 자원 희소성 (Resource Scarcity Factor)**
```python
resource_factor = sum([
    (required_quantity / available_quantity - 1) * 10 
    for item in order_requirements
]) / len(order_requirements)
```
- **부족한 자원**: 양수 값 (난이도 증가)
- **풍부한 자원**: 음수 값 (난이도 감소)

#### **D. 완료율 보정 (Completion Rate Factor)**
```python
completion_rate_factor = (1 - recent_completion_rate) * 25
```
- **높은 완료율**: 음수 값 (난이도 감소)
- **낮은 완료율**: 양수 값 (난이도 증가)

## 🏭 **2. 생산 체인 효율성 계산**

### **건물 슬롯 시스템 적용**
```python
production_efficiency = (base_production_rate * slot_utilization_rate * 
                        building_mastery_bonus * time_optimization_factor)
```

#### **A. 슬롯 활용률 (Slot Utilization Rate)**
```python
slot_utilization = active_slots / total_building_slots
building_efficiency_multiplier = 1 + (slot_utilization - 0.5) * 0.4
```
- **전체 슬롯 사용**: 1.2배 효율
- **50% 슬롯 사용**: 1.0배 효율  
- **최소 슬롯 사용**: 0.8배 효율

#### **B. 건물 숙련도 보너스 (Building Mastery Bonus)**
```python
mastery_bonus = 1 + (mastery_level / max_mastery_level) * 0.3
```
- **최대 숙련도**: +30% 생산 효율
- **단계적 증가**: 숙련도 레벨에 비례

#### **C. 시간 최적화 요소 (Time Optimization)**
```python
time_efficiency = max(0.7, min(1.5, 
    ideal_production_time / actual_production_time))
```
- **최적 타이밍**: 1.5배 효율
- **비효율적 타이밍**: 0.7배 효율

## 🚛 **3. 주문 가치 동적 조정 시스템**

### **기본 가치 계산**
```python
order_value = base_item_value * difficulty_multiplier * urgency_bonus * rarity_premium
```

#### **A. 난이도 승수 (Difficulty Multiplier)**
```python
difficulty_multiplier = 1 + (struggle_score / 100) * 0.8
```
- **어려움 지수 0**: 1.0배 가치
- **어려움 지수 50**: 1.4배 가치
- **어려움 지수 100**: 1.8배 가치

#### **B. 긴급도 보너스 (Urgency Bonus)**
```python
urgency_bonus = 1 + max(0, (1 - time_remaining_ratio)) * 0.5
```
- **시간 충분**: 1.0배 가치
- **시간 부족**: 최대 1.5배 가치

#### **C. 희귀도 프리미엄 (Rarity Premium)**
```python
rarity_premium = 1 + (item_unlock_level / max_level) * 0.6
```
- **기본 아이템**: 1.0배 가치
- **고급 아이템**: 최대 1.6배 가치

## ⚖️ **4. 동적 밸런싱 피드백 루프**

### **실시간 조정 메커니즘**
```python
def dynamic_adjustment(current_struggle, target_struggle_range):
    if current_struggle < target_struggle_range[0]:
        # 게임이 너무 쉬움 - 난이도 증가
        difficulty_adjustment = +0.1 * (target_struggle_range[0] - current_struggle)
    elif current_struggle > target_struggle_range[1]:
        # 게임이 너무 어려움 - 난이도 감소
        difficulty_adjustment = -0.1 * (current_struggle - target_struggle_range[1])
    else:
        # 적정 난이도 유지
        difficulty_adjustment = 0
    
    return difficulty_adjustment
```

### **플레이어 행동 패턴 분석**
```python
behavior_pattern = {
    'completion_rate': completed_orders / total_orders,
    'average_completion_time': sum(completion_times) / len(completion_times),
    'resource_management_efficiency': available_resources / optimal_resources,
    'building_utilization': active_buildings / total_buildings
}
```

## 🎮 **5. 게임플레이 최적화 지표**

### **플레이어 만족도 함수**
```python
satisfaction_score = (
    completion_rate_satisfaction * 0.4 +
    challenge_level_satisfaction * 0.3 +
    progression_satisfaction * 0.2 +
    variety_satisfaction * 0.1
)
```

#### **구성 요소별 가중치**
- **완료율 만족도 (40%)**: 너무 쉽지도 어렵지도 않은 적정 도전
- **도전 레벨 만족도 (30%)**: 점진적인 난이도 증가
- **진행도 만족도 (20%)**: 지속적인 성장과 발전
- **다양성 만족도 (10%)**: 다채로운 주문과 콘텐츠

### **경제 균형 지표**
```python
economic_balance = {
    'inflation_rate': (current_prices - base_prices) / base_prices,
    'supply_demand_ratio': total_production / total_demand,
    'resource_circulation_velocity': transactions_per_day / total_resources
}
```

## 🔄 **6. 시뮬레이션 검증 시스템**

### **실제 게임 데이터와의 일치도 검증**
```python
validation_accuracy = {
    'price_accuracy': 1 - abs(simulated_prices - actual_prices) / actual_prices,
    'difficulty_accuracy': 1 - abs(simulated_difficulty - player_reported_difficulty) / 100,
    'progression_accuracy': correlation(simulated_progression, actual_progression)
}
```

이러한 **수학적 모델링**을 통해 HayDay의 복잡한 경제 시스템을 정확하게 재현하고, 플레이어에게 최적화된 게임 경험을 제공하는 **데이터 기반 시뮬레이션**을 구현했습니다.

---

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
