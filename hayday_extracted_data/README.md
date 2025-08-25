# HayDay Extracted Data

이 폴더는 HayDay v1.66.159 APK에서 추출한 중요한 데이터들을 정리한 것입니다.

## 📁 폴더 구조

### `game_data/` (319 files)
게임의 핵심 데이터 CSV 파일들
- **동물 관련**: `animals.csv`, `animal_feed.csv`, `animal_goods.csv` 등
- **생산 건물**: `bakery_goods.csv`, `dairy_goods.csv`, `cafe_goods.csv` 등  
- **레벨 시스템**: `exp_levels.csv` (1500 레벨), `achievements.csv` (200개)
- **경제 시스템**: 각종 상품, 가격, 보상 데이터

### `localization/`
다국어 지원 파일들
- `ms.csv` - 말레이어
- `en.csv` - 영어
- `ko.csv` - 한국어 (있는 경우)
- 기타 언어별 번역 파일들

### `config/`
게임 설정 및 구성 파일들
- `supercell_id_config.json` - Supercell ID 설정
- `fingerprint.json` - 버전 추적
- `goods_template.csv` - 아이템 템플릿
- `AndroidManifest.xml` - Android 앱 매니페스트

### `analysis/`
데이터 분석 결과들
- `hayday_data_summary.json` - 전체 요약
- `hayday_file_structure.json` - 파일 구조
- `hayday_categories_report.txt` - 카테고리별 리포트

## 🎮 주요 데이터 파일

### 핵심 게임 데이터
- **`animals.csv`**: 14개 동물 타입, 32개 속성
- **`exp_levels.csv`**: 1500개 레벨, 82개 속성
- **`fields.csv`**: 40개 농작물 설정
- **`achievements.csv`**: 200개 업적
- **`boosters.csv`**: 256개 부스터 아이템

### 경제 시스템
- **`*_goods.csv`**: 57개 생산 카테고리
- **`boat_*.csv`**: 보트 거래 시스템
- **`car_*.csv`**: 트럭 주문 시스템
- **`cash_packages.csv`**: 인앱 구매 설정

### 소셜 & 이벤트
- **`calendar_events.csv`**: 시즌 이벤트
- **`neighborhood_*.csv`**: 이웃 시스템
- **`farm_pass_road.csv`**: 배틀패스

## 📊 데이터 통계

- **총 CSV 파일**: 319개
- **게임 레벨**: 1500개
- **동물 종류**: 14개
- **생산 건물**: 57개 카테고리
- **업적**: 200개
- **부스터**: 256개

## 🔧 사용법

```python
import pandas as pd

# 동물 데이터 읽기
animals = pd.read_csv('game_data/animals.csv')

# 레벨 데이터 읽기  
levels = pd.read_csv('game_data/exp_levels.csv')

# 현지화 데이터 읽기
translations = pd.read_csv('localization/ms.csv')
```

## 📈 데이터 구조

모든 CSV 파일은 다음 형식을 따릅니다:
1. **1행**: 컬럼 이름
2. **2행**: 데이터 타입 (String, int, Boolean 등)  
3. **3행 이후**: 실제 게임 데이터

## 🔍 추가 정보

전체 분석 리포트는 상위 디렉토리의 `HAYDAY_DATA_ANALYSIS_REPORT.md`를 참조하세요.