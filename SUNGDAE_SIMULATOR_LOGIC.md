# SungDae 시뮬레이터 핵심 로직 문서

## 개요
SungDae 시뮬레이터는 HayDay의 고급 다이나믹 밸런싱 시스템으로, 실시간 스트러글 스코어 기반의 지능형 주문 생성 시스템입니다.

## 핵심 특징

### 1. 다이나믹 밸런싱 시스템
- **스트러글 스코어**: 0-100 범위의 동적 어려움 지수
- **실시간 조정**: 플레이어의 성과에 따른 자동 난이도 조절
- **예측 알고리즘**: 10단계 프로세스 기반 주문 생성

### 2. 고급 패턴 시스템
```python
delivery_patterns = {
    "easy_crops": {
        difficulty_weight: 0.2,
        item_count_range: (2, 4),
        layer_distribution: {CROPS: 0.8, MID: 0.2, TOP: 0.0},
        struggle_modifier: 0.8
    },
    "normal_mixed": {
        difficulty_weight: 0.5,
        item_count_range: (3, 6),  
        layer_distribution: {CROPS: 0.5, MID: 0.4, TOP: 0.1},
        struggle_modifier: 1.0
    },
    "hard_production": {
        difficulty_weight: 0.8,
        item_count_range: (4, 8),
        layer_distribution: {CROPS: 0.2, MID: 0.5, TOP: 0.3},
        struggle_modifier: 1.3
    },
    "extreme_challenge": {
        difficulty_weight: 1.0,
        item_count_range: (6, 12),
        layer_distribution: {CROPS: 0.1, MID: 0.4, TOP: 0.5},
        struggle_modifier: 1.6
    }
}
```

### 3. 10단계 주문 생성 프로세스
1. **패턴 후보 선별**: 플레이어 레벨 기반 필터링
2. **납품 타입 최적화**: Train/Truck별 특화 로직
3. **스트러글 스코어 분석**: 현재 어려움 상태 평가
4. **아이템 레이어 분석**: CROPS → MID → TOP 계층 구조
5. **가중치 적용**: 스트러글 스코어 반영한 패턴 선택
6. **아이템 풀 생성**: 65+ 실제 HayDay 아이템 활용
7. **수량 최적화**: 생산 시간/가치 기반 밸런싱
8. **리소스 소스 분석**: 창고/진열대/시장/생산 가중치
9. **품질 검증**: 중복 제거 및 밸런스 체크
10. **최종 주문 생성**: 난이도 등급 및 가치 계산

### 4. 지능형 난이도 시스템
```python
# 기차 납품 (더 높은 난이도 기준)
if delivery_type == DeliveryType.TRAIN:
    if struggle_score < 35: difficulty = EASY
    elif struggle_score < 60: difficulty = NORMAL  
    elif struggle_score < 85: difficulty = HARD
    else: difficulty = VERY_HARD
# 트럭 납품 (기본 난이도)
else:
    if struggle_score < 25: difficulty = EASY
    elif struggle_score < 50: difficulty = NORMAL
    elif struggle_score < 75: difficulty = HARD
    else: difficulty = VERY_HARD
```

### 5. 실시간 시스템 상태 추적
- **현재 스트러글 스코어**: 실시간 어려움 지수
- **총 생성 주문 수**: 누적 주문 생성 통계
- **희소 아이템 수**: 부족한 리소스 개수
- **평균 밸런스**: 전체 시스템 안정성 지표

### 6. Township 기차 시스템 (v2.1)
- **칸 구조**: 3-5개 기차칸으로 구성 (Township 실제 규칙)
- **수량 분배**: 칸별로 다른 수량 요구 (앞쪽 칸 1.5배, 뒤쪽 칸 감소)
- **레이어별 칸당 기본값**: 작물 3개, 중급품 2개, 고급품 1개
- **최대 수량 제한**: 아이템당 최대 25개 (Township 게임 내 제한)
- **칸별 난이도 계산**: 칸 수에 따른 복잡도 보너스 시스템

### 7. 배치 생성 시스템
- **병렬 생성**: 최대 10개 주문 동시 생성
- **다양성 보장**: 각기 다른 패턴 적용
- **효율성 최적화**: 중복 연산 최소화

### 8. 핵심 아이템 데이터베이스 (65+ 아이템)
```python
hayday_items = {
    # 기본 작물
    "Wheat": {"base_price": 1, "production_time": 2, "layer": "CROPS"},
    "Corn": {"base_price": 2, "production_time": 5, "layer": "CROPS"},
    "Carrot": {"base_price": 3, "production_time": 10, "layer": "CROPS"},
    
    # 가공 제품
    "Bread": {"base_price": 27, "production_time": 30, "layer": "MID"},
    "Bacon": {"base_price": 73, "production_time": 180, "layer": "MID"},
    
    # 고급 제품
    "Wedding Cake": {"base_price": 599, "production_time": 1440, "layer": "TOP"},
    "Diamond Ring": {"base_price": 699, "production_time": 1440, "layer": "TOP"}
}
```

## API 엔드포인트

### 주요 API
- `POST /api/sungdae/generate-order`: 단일 주문 생성
- `POST /api/sungdae/batch-orders`: 배치 주문 생성
- `POST /api/sungdae/adjust-struggle`: 스트러글 스코어 조정
- `GET /api/sungdae/stats`: 시스템 상태 조회
- `POST /api/sungdae/simulate-time`: 시간 경과 시뮬레이션
- `GET /api/sungdae/available-items`: 사용 가능한 아이템 목록

### 요청 예시
```json
// 단일 주문 생성
{
    "player_level": 50,
    "delivery_type": "Train",
    "struggle_score": 75.5,
    "use_struggle_adjustment": true
}

// 배치 주문 생성  
{
    "count": 10,
    "delivery_types": ["Train", "Truck"]
}
```

## 고급 기능

### 1. 시간 진행 시뮬레이션
- 시간 경과에 따른 스트러글 스코어 자동 조정
- 아이템 가격 변동 시뮬레이션
- 시장 상황 반영

### 2. 학습 알고리즘
- 플레이어 패턴 학습
- 개인화된 난이도 조정
- 성과 기반 최적화

### 3. 데이터 내보내기
- Excel 형식 시뮬레이션 데이터 내보내기
- 통계 분석 지원
- 성과 리포트 생성

## 기술적 특징

### 성능 최적화
- 메모리 효율적인 패턴 매칭
- 지연 로딩을 통한 빠른 초기화
- 캐시 기반 아이템 정보 관리

### 확장성
- 모듈화된 패턴 시스템
- 플러그인 형태의 난이도 알고리즘
- 다국어 지원 (EN/KR)

### 안정성
- 예외 처리 및 오류 복구
- 데이터 일관성 보장
- 실시간 상태 검증

---

## 현재 상태
- **구현 상태**: ✅ Township 기차 시스템 개선 완료 (`sungdae_simulator.py.disabled`)
- **UI 상태**: ❌ 비활성화됨 (UI 통합 실패)
- **파일 위치**: `C:\Users\zi_zi\OneDrive\문서\SungDaeDay\sungdae_simulator.py.disabled`
- **비활성화 이유**: UI 통합 복잡도로 인한 기존 시스템 충돌
- **최신 개선**: Township 실제 기차 규칙 적용 (3-5칸, 알고리즘 기반 수량 분배)

## 재활성화 방법
1. 파일명을 `sungdae_simulator.py.disabled` → `sungdae_simulator.py`로 변경
2. 독립적인 Flask 라우트 및 템플릿 구축 
3. 기존 orders.html과 분리된 UI 인터페이스 개발

## Township 기차 시스템 개선 사항 (v2.1)

### 핵심 변경점
1. **실제 Township 규칙 적용**: 3-5개 기차칸 구조
2. **알고리즘 기반 수량 분배**: 칸별로 다른 수량 요구
3. **정확한 수량 제한**: 아이템당 최대 25개 (게임 내 제한)
4. **칸별 난이도 시스템**: 칸 수에 따른 복잡도 보너스
5. **메타데이터 확장**: Township 기차 전용 정보 추가

### 기술적 개선
- `_select_train_items_and_quantities()`: Township 3-5칸 규칙 적용
- `_calculate_township_train_quantity()`: 칸별 수량 분배 알고리즘
- `_apply_train_scarcity_algorithm()`: 칸 단위 희소성 조정
- `_calculate_train_struggle_score()`: Township 기차 특화 스코어링
- `_get_car_distribution_info()`: 칸별 분배 메타데이터 생성

## 핵심 가치
- **혁신성**: 업계 최초의 다이나믹 밸런싱 시스템
- **기술적 우수성**: Township 실제 규칙 기반 10단계 지능형 알고리즘 
- **확장성**: 모든 시뮬레이션 게임에 적용 가능
- **정확성**: 실제 게임 메커닉 기반 구현
- **상업적 가치**: 게임 산업 게임체인저 잠재력

**우선순위**: 보류 (안정성 우선, 향후 독립 개발 예정)