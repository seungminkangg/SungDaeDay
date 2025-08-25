# 🌍 크로스 플랫폼 사용 가이드

## 맥/윈도우/리눅스 완벽 호환

### 🚀 빠른 시작

#### Windows
```cmd
# Git 클론
git clone https://github.com/seungminkangg/SungDaeDay
cd SungDaeDay

# 자동 설치 및 실행
run_simple.bat
```

#### Mac/Linux  
```bash
# Git 클론
git clone https://github.com/seungminkangg/SungDaeDay
cd SungDaeDay

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# 의존성 설치
pip install -r requirements.txt

# 웹 서버 실행
cd webui && python app.py
```

### 🔧 주요 기능 (모든 플랫폼 동일)

#### ✨ HayDay 시뮬레이터 
- **주소**: http://localhost:5001
- **핵심**: 주문 관리 시스템
- **데이터**: 57개 생산 건물, 465개 건물 정보, 400+ 아이템

#### 🎮 고급 파라미터 시스템
- **자동 모드**: 실제 HayDay 로직 (레벨별 어려움 지수)
- **수동 모드**: 모든 파라미터 직접 조절
- **프리셋**: 설정 저장/로드 (브라우저 저장)

#### 🦎 진짜 도마뱀 애니메이션
- **기어다니기**: 물리학 기반 자연스러운 움직임
- **폭발 효과**: 클릭시 20개 파티클 폭발
- **부활 시스템**: 10초 후 자동 부활

### 🛠️ 기술 사양

#### 언어 & 프레임워크
- **Backend**: Python 3.8+ (Flask)
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **데이터**: Pandas, NumPy
- **UI**: Bootstrap 5, Chart.js

#### 브라우저 호환성
- ✅ Chrome 80+
- ✅ Firefox 75+  
- ✅ Safari 13+
- ✅ Edge 80+

### 🎯 사용법

#### 1. 기본 주문 생성
1. 플레이어 레벨 설정 (1-100)
2. 납품 타입 선택 (트럭/기차/보트)
3. "주문 생성" 버튼 클릭

#### 2. 고급 설정 모드
1. "고급 설정" 토글 활성화
2. 어려움 지수, 가치 배율, 특별주문 확률 조절
3. 프리셋으로 설정 저장

#### 3. 도마뱀 게임
1. 10초 후 화면에 도마뱀 등장
2. 클릭하면 화려한 폭발 효과
3. 10초 후 자동 부활

### 🔍 문제 해결

#### Port 충돌 (Windows)
```cmd
netstat -an | findstr :5001
# 다른 프로세스가 5001 포트 사용시
taskkill /f /pid <PID번호>
```

#### Python 가상환경 (Mac/Linux)
```bash
# Python 버전 확인
python3 --version  # 3.8+ 필요

# pip 업그레이드
pip install --upgrade pip
```

#### 브라우저 문제
- 캐시 삭제: Ctrl+F5 (Windows), Cmd+Shift+R (Mac)
- 시크릿/프라이빗 모드에서 테스트

### 📊 성능 최적화

#### 메모리 사용량
- **기본**: ~50MB RAM
- **대량 주문**: ~100MB RAM
- **도마뱀 다수**: +10MB per lizard

#### CPU 사용량
- **idle**: <1% CPU
- **주문 생성**: 2-5% CPU spike
- **애니메이션**: 3-8% CPU (GPU 가속 시 더 낮음)

### 🌟 고급 기능

#### API 엔드포인트
```javascript
// 주문 생성
POST /api/generate-order
{
  "player_level": 50,
  "manual_mode": true,
  "struggle_score": 75,
  "value_multiplier": 1.5,
  "delivery_type": "Boat"
}

// 통계 조회  
GET /api/stats
```

#### 개발자 모드
- F12 개발자 도구 → Console
- `createLizard()` - 즉시 도마뱀 생성
- `generatedOrders` - 생성된 주문 목록 확인

### 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

### 🆘 지원

- GitHub Issues: 버그 리포트 및 기능 요청
- 이메일: 기술적 문의사항

---

**💡 팁**: 최상의 경험을 위해 Chrome 브라우저와 1920x1080 이상 해상도를 권장합니다.