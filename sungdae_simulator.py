"""
SungDae 모드 시뮬레이터
RabbitHole의 다이나믹 밸런싱 시스템을 HayDay 아이템으로 구현
기존 HayDay 시뮬레이터에 영향을 주지 않는 독립적인 모드
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict
import json

class ResourceSource(Enum):
    """리소스 획득 소스 (PDF: RH-일반 납품 - 세부 로직)"""
    STORAGE = "STORAGE"      # 창고에서 직접 획득
    SHELF = "SHELF"          # 진열대에서 획득
    MARKET = "MARKET"        # 마켓에서 구매
    PRODUCTION = "PRODUCTION" # 생산 필요

class ItemLayer(Enum):
    """아이템 레이어 분류 (PDF: 분석 문서)"""
    TOP = "TOP"         # 최고급 아이템
    MID = "MID"         # 중급 아이템  
    CROPS = "CROPS"     # 기본 작물

class DeliveryDifficulty(Enum):
    """납품 난이도 등급"""
    EASY = "쉬움"
    NORMAL = "보통"
    HARD = "어려움"
    VERY_HARD = "매우어려움"

class DeliveryType(Enum):
    """납품 타입 (PDF: 기차 vs 트럭 납품)"""
    TRUCK = "Truck"   # 일반 트럭 납품 (기본 로직)
    TRAIN = "Train"   # 기차 납품 (11차 스프린트 로직)

@dataclass
class ResourceState:
    """리소스 상태 정보 (10단계 프로세스 1단계)"""
    item_name: str
    layer: ItemLayer
    current_stock: int
    max_capacity: int
    production_time: int
    production_buildings: List[str]
    shelf_available: bool
    market_available: bool
    
    @property
    def stock_ratio(self) -> float:
        """재고 비율 (0.0 ~ 1.0)"""
        return self.current_stock / max(self.max_capacity, 1)
    
    @property
    def is_deficit(self) -> bool:
        """부족 상태 여부 (희소성 알고리즘 기준)"""
        return self.stock_ratio < 0.3

@dataclass
class ProductionPressure:
    """생산 압박 정보 (10단계 프로세스 3단계)"""
    building_name: str
    current_load: float  # 0.0 ~ 1.0
    max_capacity: int
    items_in_queue: List[str]
    
    @property
    def pressure_level(self) -> float:
        """압박 수준 (0.0 = 여유, 1.0 = 포화)"""
        return self.current_load

@dataclass
class DeliveryPattern:
    """납품 패턴 (10단계 프로세스 6단계)"""
    pattern_id: str
    difficulty_weight: float
    item_count_range: Tuple[int, int]
    layer_distribution: Dict[ItemLayer, float]
    source_preference: Dict[ResourceSource, float]
    struggle_modifier: float

@dataclass
class DeliveryOrder:
    """생성된 납품 주문"""
    order_id: str
    delivery_type: DeliveryType
    items: Dict[str, int]  # 아이템명: 수량
    difficulty: DeliveryDifficulty
    total_value: int
    struggle_score: float
    level_requirement: int
    avg_production_time: float
    total_production_time: float
    expiry_time: int  # 만료 시간 (분)
    generation_metadata: Dict  # 생성 과정 메타데이터

class SungDaeSimulator:
    """
    성대 모드 시뮬레이터
    RabbitHole 다이나믹 밸런싱 시스템의 완전한 구현
    """
    
    def __init__(self, hayday_items: Dict, player_level: int = 5):
        self.hayday_items = hayday_items
        self.player_level = player_level
        
        # 상태 추적
        self.resource_states: Dict[str, ResourceState] = {}
        self.production_pressures: Dict[str, ProductionPressure] = {}
        self.current_struggle_score: float = 50.0  # 초기값 50
        
        # 히스토리 추적
        self.delivery_history: List[DeliveryOrder] = []
        self.struggle_history: List[float] = []
        self.balance_adjustments: List[Dict] = []
        
        # 설정값
        self.scarcity_threshold = 0.3  # 희소성 임계값
        self.production_pressure_limit = 0.8  # 생산 압박 한계
        self.auto_generation = True  # 자동 생성 모드
        
        # 납품 패턴 정의 (PDF 기반)
        self._initialize_delivery_patterns()
        self._initialize_resource_states()
        self._initialize_production_systems()
    
    def _initialize_delivery_patterns(self):
        """납품 패턴 초기화 (PDF: 패턴 가중치 적용)"""
        self.delivery_patterns = {
            "easy_crops": DeliveryPattern(
                pattern_id="easy_crops",
                difficulty_weight=0.2,
                item_count_range=(2, 4),
                layer_distribution={ItemLayer.CROPS: 0.8, ItemLayer.MID: 0.2, ItemLayer.TOP: 0.0},
                source_preference={ResourceSource.STORAGE: 0.6, ResourceSource.SHELF: 0.3, 
                                 ResourceSource.MARKET: 0.1, ResourceSource.PRODUCTION: 0.0},
                struggle_modifier=0.8
            ),
            "normal_mixed": DeliveryPattern(
                pattern_id="normal_mixed",
                difficulty_weight=0.5,
                item_count_range=(3, 6),
                layer_distribution={ItemLayer.CROPS: 0.5, ItemLayer.MID: 0.4, ItemLayer.TOP: 0.1},
                source_preference={ResourceSource.STORAGE: 0.4, ResourceSource.SHELF: 0.3,
                                 ResourceSource.MARKET: 0.2, ResourceSource.PRODUCTION: 0.1},
                struggle_modifier=1.0
            ),
            "hard_production": DeliveryPattern(
                pattern_id="hard_production",
                difficulty_weight=0.8,
                item_count_range=(4, 8),
                layer_distribution={ItemLayer.CROPS: 0.2, ItemLayer.MID: 0.5, ItemLayer.TOP: 0.3},
                source_preference={ResourceSource.STORAGE: 0.2, ResourceSource.SHELF: 0.2,
                                 ResourceSource.MARKET: 0.3, ResourceSource.PRODUCTION: 0.3},
                struggle_modifier=1.3
            ),
            "extreme_challenge": DeliveryPattern(
                pattern_id="extreme_challenge",
                difficulty_weight=1.0,
                item_count_range=(6, 12),
                layer_distribution={ItemLayer.CROPS: 0.1, ItemLayer.MID: 0.4, ItemLayer.TOP: 0.5},
                source_preference={ResourceSource.STORAGE: 0.1, ResourceSource.SHELF: 0.1,
                                 ResourceSource.MARKET: 0.4, ResourceSource.PRODUCTION: 0.4},
                struggle_modifier=1.6
            )
        }
    
    def _initialize_resource_states(self):
        """리소스 상태 초기화 (HayDay 아이템 기반)"""
        # HayDay 아이템을 레이어별로 분류
        layer_classification = self._classify_items_by_layer()
        
        for item_name, item_data in self.hayday_items.items():
            # 유효하지 않은 아이템은 건너뛰기
            if not self._is_valid_item(item_name):
                continue
            
            # 플레이어 레벨보다 높은 언락 레벨의 아이템은 건너뛰기
            unlock_level = item_data.get('unlock_level', 1)
            if unlock_level > self.player_level:
                continue
                
            layer = layer_classification.get(item_name, ItemLayer.CROPS)
            
            # 초기 재고량은 레이어에 따라 다르게 설정
            base_stock = {
                ItemLayer.CROPS: random.randint(20, 50),
                ItemLayer.MID: random.randint(10, 30),
                ItemLayer.TOP: random.randint(3, 15)
            }[layer]
            
            self.resource_states[item_name] = ResourceState(
                item_name=item_name,
                layer=layer,
                current_stock=base_stock,
                max_capacity=base_stock * 2,
                production_time=item_data.get('production_time', 300),
                production_buildings=item_data.get('buildings', []),
                shelf_available=random.choice([True, False]),
                market_available=layer != ItemLayer.TOP  # TOP 레이어는 마켓 구매 불가
            )
    
    def _initialize_production_systems(self):
        """생산 시스템 초기화"""
        building_types = ['bakery', 'dairy', 'sugar_mill', 'feed_mill', 'popcorn_pot', 
                         'bbq_grill', 'pie_oven', 'loom', 'knitting', 'tailoring', 
                         'jeweler', 'mining', 'smelter', 'cake_oven']
        
        for building in building_types:
            self.production_pressures[building] = ProductionPressure(
                building_name=building,
                current_load=random.uniform(0.1, 0.6),
                max_capacity=random.randint(3, 8),
                items_in_queue=[]
            )
    
    def _classify_items_by_layer(self) -> Dict[str, ItemLayer]:
        """아이템을 레이어별로 분류 (PDF 분석 기반)"""
        classification = {}
        
        # 기본 작물류 (CROPS) - 정확한 이름으로 매칭
        crops = ['wheat', 'corn', 'carrot', 'soybean', 'sugarcane', 'cocoa', 'coffee', 
                'tomato', 'potato', 'cotton', 'indigo', 'pumpkin', 'chili']
        
        # 중급 가공품 (MID) - 정확한 이름으로 매칭
        mid_items = ['bread', 'cookie', 'milk', 'butter', 'cheese', 'cream',
                    'bacon', 'wool', 'fabric', 'dress', 'sweater', 'egg',
                    'feed', 'sugar', 'syrup', 'hamburger', 'pizza', 'juice']
        
        # 최고급 제품 (TOP) - 정확한 이름으로 매칭
        top_items = ['ring', 'necklace', 'bracelet', 'ore', 'bar', 'cake', 
                    'muffin', 'tuxedo', 'platinum', 'gold', 'silver']
        
        for item_name in self.hayday_items.keys():
            if any(crop in item_name.lower() for crop in crops):
                classification[item_name] = ItemLayer.CROPS
            elif any(mid in item_name.lower() for mid in mid_items):
                classification[item_name] = ItemLayer.MID
            elif any(top in item_name.lower() for top in top_items):
                classification[item_name] = ItemLayer.TOP
            else:
                # 기본값은 MID 레이어
                classification[item_name] = ItemLayer.MID
                
        return classification
    
    def generate_delivery_order(self, delivery_type: DeliveryType = DeliveryType.TRUCK, 
                               use_struggle_adjustment: bool = True) -> DeliveryOrder:
        """
        납품 주문 생성 - 10단계 다이나믹 밸런싱 프로세스 구현
        (PDF: RH-일반 납품 - 세부 로직 완전 구현)
        
        기차 납품과 트럭 납품을 구분하여 처리:
        - 트럭: 기본 10단계 로직 적용
        - 기차: 11차 스프린트 고급 로직 적용 (더 복잡한 패턴, 높은 가치)
        """
        
        # 기차 납품의 경우 전용 로직 사용
        if delivery_type == DeliveryType.TRAIN:
            return self._generate_train_delivery_order(use_struggle_adjustment)
        else:
            return self._generate_truck_delivery_order(use_struggle_adjustment)
    
    def _generate_truck_delivery_order(self, use_struggle_adjustment: bool = True) -> DeliveryOrder:
        """트럭 납품 주문 생성 (기본 10단계 로직)"""
        
        # 1단계: 리소스 상태 분석
        resource_analysis = self._analyze_resource_state()
        
        # 2단계: 소스 태깅
        source_tags = self._perform_source_tagging(resource_analysis)
        
        # 3단계: 생산 압박 계산
        production_pressure = self._calculate_production_pressure()
        
        # 4단계: 납품 패턴 후보 선정
        pattern_candidates = self._select_pattern_candidates(resource_analysis, production_pressure)
        
        # 5단계: 가중치 적용
        weighted_patterns = self._apply_pattern_weights(pattern_candidates, use_struggle_adjustment)
        
        # 6단계: 납품 패턴 결정
        selected_pattern = self._select_final_pattern(weighted_patterns)
        
        # 7단계: 아이템 선정 및 수량 결정
        selected_items = self._select_items_and_quantities(selected_pattern, source_tags)
        
        # 8단계: 희소성 알고리즘 적용
        scarcity_adjusted_items = self._apply_scarcity_algorithm(selected_items)
        
        # 9단계: 스코어 계산
        struggle_score = self._calculate_struggle_score(scarcity_adjusted_items, selected_pattern)
        
        # 10단계: 최종 주문 생성
        order = self._create_final_order(scarcity_adjusted_items, struggle_score, selected_pattern, DeliveryType.TRUCK)
        
        # 히스토리 업데이트
        self.delivery_history.append(order)
        self.struggle_history.append(struggle_score)
        self.current_struggle_score = struggle_score
        
        return order
    
    def _generate_train_delivery_order(self, use_struggle_adjustment: bool = True) -> DeliveryOrder:
        """
        기차 납품 주문 생성 (11차 스프린트 고급 로직)
        PDF: RH-[11차 스프린트] 기차 납품 구현
        
        기차 납품 특징:
        1. 더 높은 가치 목표 (트럭의 1.5-2.0배)
        2. 더 복잡한 아이템 조합
        3. TOP 레이어 아이템 선호
        4. 연속 납품 패턴 (체인 효과)
        5. 특별 보상 시스템
        """
        
        # 기차 전용 분석 시작
        resource_analysis = self._analyze_resource_state()
        source_tags = self._perform_source_tagging(resource_analysis)
        production_pressure = self._calculate_production_pressure()
        
        # 기차 전용 패턴 후보 (더 도전적인 패턴들)
        train_pattern_candidates = self._select_train_pattern_candidates(resource_analysis, production_pressure)
        
        # 기차 전용 가중치 (더 높은 난이도 선호)
        weighted_patterns = self._apply_train_pattern_weights(train_pattern_candidates, use_struggle_adjustment)
        
        # 패턴 결정
        selected_pattern = self._select_final_pattern(weighted_patterns)
        
        # 기차 전용 아이템 선정 (TOP 레이어 선호, 더 많은 수량)
        selected_items = self._select_train_items_and_quantities(selected_pattern, source_tags)
        
        # 기차 전용 희소성 알고리즘 (더 공격적)
        scarcity_adjusted_items = self._apply_train_scarcity_algorithm(selected_items)
        
        # 기차 전용 스코어 계산 (더 높은 기준점)
        struggle_score = self._calculate_train_struggle_score(scarcity_adjusted_items, selected_pattern)
        
        # 기차 전용 최종 주문 생성
        order = self._create_final_order(scarcity_adjusted_items, struggle_score, selected_pattern, DeliveryType.TRAIN)
        
        # 히스토리 업데이트
        self.delivery_history.append(order)
        self.struggle_history.append(struggle_score)
        self.current_struggle_score = struggle_score
        
        return order
    
    def _select_train_pattern_candidates(self, resource_analysis: Dict, production_pressure: Dict) -> List[str]:
        """기차 전용 패턴 후보 선정 (더 도전적인 패턴들)"""
        candidates = []
        
        deficit_ratio = resource_analysis['total_deficit_ratio']
        overall_pressure = production_pressure['overall_pressure']
        
        # 기차는 항상 중간 이상의 난이도 패턴 사용
        if deficit_ratio < 0.3 and overall_pressure < 0.5:
            # 여유로운 상황에서도 도전적 패턴
            candidates.extend(['hard_production', 'extreme_challenge'])
        elif deficit_ratio < 0.6:
            # 보통 상황 - 어려운 패턴들
            candidates.extend(['normal_mixed', 'hard_production', 'extreme_challenge'])
        else:
            # 압박 상황에서도 중간 이상 유지
            candidates.extend(['normal_mixed', 'hard_production'])
        
        # 기차는 극한 도전을 더 자주 포함
        if len(resource_analysis['abundant_items']) > 5:
            candidates.append('extreme_challenge')
            
        return candidates
    
    def _apply_train_pattern_weights(self, pattern_candidates: List[str], use_struggle_adjustment: bool) -> Dict[str, float]:
        """기차 전용 가중치 적용 (높은 난이도 선호)"""
        weights = {}
        
        for pattern_id in pattern_candidates:
            pattern = self.delivery_patterns[pattern_id]
            base_weight = pattern.difficulty_weight
            
            # 기차는 어려운 패턴을 더 선호
            train_bonus = 1.5 if base_weight > 0.6 else 1.0
            base_weight *= train_bonus
            
            if use_struggle_adjustment:
                struggle_modifier = self._get_train_struggle_modifier(pattern.struggle_modifier)
                adjusted_weight = base_weight * struggle_modifier
            else:
                adjusted_weight = base_weight
            
            weights[pattern_id] = adjusted_weight
        
        return weights
    
    def _get_train_struggle_modifier(self, base_modifier: float) -> float:
        """기차 전용 스트러글 스코어 조정 (더 공격적)"""
        if self.current_struggle_score > 85:
            # 매우 높은 스트러글에서도 중간 난이도 유지
            return base_modifier * 0.7 if base_modifier > 1.0 else base_modifier * 1.3
        elif self.current_struggle_score > 65:
            return base_modifier * 0.9 if base_modifier > 1.0 else base_modifier * 1.1
        elif self.current_struggle_score < 25:
            # 낮은 스트러글에서 매우 어려운 패턴
            return base_modifier * 2.0 if base_modifier > 1.0 else base_modifier * 0.5
        elif self.current_struggle_score < 45:
            return base_modifier * 1.5 if base_modifier > 1.0 else base_modifier * 0.7
        else:
            return base_modifier * 1.2
    
    def _select_train_items_and_quantities(self, pattern: DeliveryPattern, source_tags: Dict) -> Dict[str, int]:
        """기차 전용 아이템 선정 (Township 규칙: 3-5칸 구성, 알고리즘 기반 수량)"""
        selected_items = {}
        
        # Township 기차 규칙: 3-5개 칸, 다양한 아이템 타입 보장
        train_cars = random.randint(3, 5)  # 3-5개 기차칸
        # 최소 3개, 최대 6개 아이템 타입 (다양성 보장)
        train_item_count = random.randint(3, min(6, train_cars + 1))
        
        # 기차 전용 레이어 분포 (TOP 레이어 강화)
        train_layer_distribution = {
            ItemLayer.TOP: pattern.layer_distribution.get(ItemLayer.TOP, 0.1) + 0.2,
            ItemLayer.MID: pattern.layer_distribution.get(ItemLayer.MID, 0.4),
            ItemLayer.CROPS: max(0.1, pattern.layer_distribution.get(ItemLayer.CROPS, 0.5) - 0.2)
        }
        
        # 정규화
        total_ratio = sum(train_layer_distribution.values())
        train_layer_distribution = {k: v/total_ratio for k, v in train_layer_distribution.items()}
        
        # 레이어별 아이템 수량 계산 (다양성 보장)
        layer_counts = {}
        
        # 각 레이어별 최소 1개씩은 보장
        for layer in train_layer_distribution.keys():
            layer_counts[layer] = 1
        
        # 남은 아이템들을 레이어별 비율로 분배
        remaining_count = train_item_count - len(layer_counts)
        
        for layer, ratio in train_layer_distribution.items():
            additional = int(remaining_count * ratio)
            layer_counts[layer] += additional
        
        # 각 레이어별로 아이템 선정
        for layer, count in layer_counts.items():
            layer_items = [item for item, resource in self.resource_states.items() 
                          if resource.layer == layer and self._is_valid_item(item) and self._is_unlocked_item(item)]
            
            if not layer_items:
                continue
            
            # 다양성 보장: 레이어에서 최소 요구 수량만큼 다양한 아이템 선택
            selected_layer_items = self._select_items_by_source_preference(
                layer_items, max(count, 1), pattern.source_preference, source_tags
            )
            
            # Township 기차 수량: 알고리즘 기반 분산 (칸별 다른 수량)
            for item in selected_layer_items:
                car_quantity = self._calculate_township_train_quantity(layer, train_cars)
                selected_items[item] = car_quantity
        
        return selected_items
    
    def _calculate_township_train_quantity(self, layer: ItemLayer, train_cars: int) -> int:
        """Township 기차 수량 알고리즘 (플레이어 레벨 기반, 칸별 분산)"""
        # 플레이어 레벨에 따른 기본 수량 조정
        level_multiplier = 1.0 + (self.player_level - 1) * 0.03  # 레벨당 3% 증가 (기차는 트럭보다 높음)
        level_multiplier = max(1.0, min(level_multiplier, 4.0))  # 1.0-4.0배 제한
        
        # Township 기차는 칸별로 다른 수량 요구 (레벨 보정된 기본값)
        base_per_car = {
            ItemLayer.CROPS: max(2, int(4 * level_multiplier)),   # 작물: 칸당 최소 2개
            ItemLayer.MID: max(1, int(3 * level_multiplier)),     # 중급품: 칸당 최소 1개  
            ItemLayer.TOP: max(1, int(2 * level_multiplier))      # 고급품: 칸당 최소 1개
        }.get(layer, max(1, int(2 * level_multiplier)))
        
        # 기차칸 수에 따른 분산 시스템 - 실제로는 한 아이템이 여러 칸에 걸쳐있음
        # 예: 옥수수가 1칸에 6개, 2칸에 6개 이런 식
        cars_for_this_item = random.randint(1, min(3, train_cars))  # 한 아이템이 최대 3칸
        
        total_quantity = 0
        for i in range(cars_for_this_item):
            # 칸별로 다른 수량 (Township 실제 패턴)
            car_quantity = random.randint(base_per_car, base_per_car + 3)
            total_quantity += car_quantity
        
        # 최소 1개, 최대 25개 제한 (Township 게임 내 제한)
        return max(1, min(total_quantity, 25))
    
    def _apply_train_scarcity_algorithm(self, selected_items: Dict[str, int]) -> Dict[str, int]:
        """Township 기차 희소성 알고리즘 (칸별 분산 기반 조정)"""
        adjusted_items = selected_items.copy()
        
        for item_name, quantity in selected_items.items():
            resource = self.resource_states[item_name]
            
            # Township 특화: 칸별 수량이므로 더 정밀한 부족 상태 생성
            if resource.current_stock < quantity:
                # 부족분을 칸 단위로 조정 (Township의 칸별 시스템)
                cars_needed = math.ceil(quantity / 5)  # 평균 칸당 5개 기준
                near_miss_buffer = random.randint(1, 3)  # 칸 1-3개만큼 부족
                
                adjusted_items[item_name] = max(
                    resource.current_stock - near_miss_buffer,
                    quantity - (cars_needed * 2)  # 칸 2개분만큼 부족하게
                )
            
            # Township 기차는 풍부한 자원도 칸 단위로 대량 요구
            elif resource.stock_ratio > 0.6:
                # 칸 수에 비례한 증가 (3-5칸이므로 3-5배 증가 가능)
                car_multiplier = random.uniform(1.2, 1.8)
                adjusted_items[item_name] = int(quantity * car_multiplier)
            
            # 최소 1개, 최대 25개 제한 (Township 게임 내 제한)
            adjusted_items[item_name] = max(1, min(adjusted_items[item_name], 25))
        
        return adjusted_items
    
    def _calculate_train_struggle_score(self, items: Dict[str, int], pattern: DeliveryPattern) -> float:
        """Township 기차 스트러글 스코어 (칸별 분산 시스템 반영)"""
        base_score = 0.0
        item_count = len(items)
        total_cars_needed = 0
        
        for item_name, quantity in items.items():
            resource = self.resource_states[item_name]
            
            # Township 칸별 난이도 계산
            cars_for_item = math.ceil(quantity / 5)  # 평균 칸당 5개 기준
            total_cars_needed += cars_for_item
            
            # Township 레이어별 칸 난이도 (칸별로 다른 가중치)
            car_difficulty = {
                ItemLayer.CROPS: cars_for_item * 2.0,    # 작물칸 난이도
                ItemLayer.MID: cars_for_item * 4.0,      # 중급품칸 난이도  
                ItemLayer.TOP: cars_for_item * 6.0       # 고급품칸 난이도
            }[resource.layer]
            
            # Township 특화: 칸별 부족 상태 점수
            car_deficit_bonus = 0.0
            if resource.current_stock < quantity:
                deficit_cars = math.ceil((quantity - resource.current_stock) / 5)
                car_deficit_bonus = deficit_cars * 15.0  # 칸당 15점 보너스
            elif resource.is_deficit:
                car_deficit_bonus = cars_for_item * 10.0  # 희소 아이템 칸당 10점
            
            base_score += car_difficulty + car_deficit_bonus
        
        # Township 기차 특화: 총 칸 수에 따른 복잡도
        car_complexity_bonus = 0.0
        if total_cars_needed >= 5:  # 5칸 풀 기차
            car_complexity_bonus = 25.0
        elif total_cars_needed >= 4:  # 4칸 기차
            car_complexity_bonus = 15.0
        elif total_cars_needed >= 3:  # 3칸 기차
            car_complexity_bonus = 5.0
        
        # 최종 스코어 계산 (Township 알고리즘)
        final_score = (base_score + car_complexity_bonus) * pattern.struggle_modifier / max(item_count, 1)
        
        # Township 기차는 25-95점 범위 (더 엄격한 범위)
        normalized_score = max(25.0, min(95.0, final_score))
        
        return normalized_score
    
    def _analyze_resource_state(self) -> Dict:
        """1단계: 리소스 상태 분석"""
        analysis = {
            'deficit_items': [],  # 부족한 아이템들
            'abundant_items': [], # 풍부한 아이템들
            'balanced_items': [], # 균형잡힌 아이템들
            'total_deficit_ratio': 0.0
        }
        
        deficit_count = 0
        for item_name, resource in self.resource_states.items():
            if resource.is_deficit:
                analysis['deficit_items'].append(item_name)
                deficit_count += 1
            elif resource.stock_ratio > 0.7:
                analysis['abundant_items'].append(item_name)
            else:
                analysis['balanced_items'].append(item_name)
        
        analysis['total_deficit_ratio'] = deficit_count / len(self.resource_states)
        return analysis
    
    def _perform_source_tagging(self, resource_analysis: Dict) -> Dict:
        """2단계: 소스 태깅 (획득 가능 소스별 아이템 분류)"""
        source_tags = {
            ResourceSource.STORAGE: [],
            ResourceSource.SHELF: [],
            ResourceSource.MARKET: [],
            ResourceSource.PRODUCTION: []
        }
        
        for item_name, resource in self.resource_states.items():
            # 창고에 충분한 재고가 있는 경우
            if resource.current_stock >= 3:
                source_tags[ResourceSource.STORAGE].append(item_name)
            
            # 진열대에서 구매 가능한 경우
            if resource.shelf_available:
                source_tags[ResourceSource.SHELF].append(item_name)
            
            # 마켓에서 구매 가능한 경우
            if resource.market_available:
                source_tags[ResourceSource.MARKET].append(item_name)
            
            # 생산이 필요한 경우 (재고 부족)
            if resource.current_stock < 5 or resource.is_deficit:
                source_tags[ResourceSource.PRODUCTION].append(item_name)
        
        return source_tags
    
    def _calculate_production_pressure(self) -> Dict:
        """3단계: 생산 압박 계산"""
        pressure_analysis = {
            'high_pressure_buildings': [],
            'medium_pressure_buildings': [],
            'low_pressure_buildings': [],
            'overall_pressure': 0.0
        }
        
        total_pressure = 0.0
        for building_name, pressure in self.production_pressures.items():
            if pressure.pressure_level > 0.8:
                pressure_analysis['high_pressure_buildings'].append(building_name)
            elif pressure.pressure_level > 0.5:
                pressure_analysis['medium_pressure_buildings'].append(building_name)
            else:
                pressure_analysis['low_pressure_buildings'].append(building_name)
            
            total_pressure += pressure.pressure_level
        
        pressure_analysis['overall_pressure'] = total_pressure / len(self.production_pressures)
        return pressure_analysis
    
    def _select_pattern_candidates(self, resource_analysis: Dict, production_pressure: Dict) -> List[str]:
        """4단계: 납품 패턴 후보 선정"""
        candidates = []
        
        # 리소스 상태에 따른 패턴 선정
        deficit_ratio = resource_analysis['total_deficit_ratio']
        overall_pressure = production_pressure['overall_pressure']
        
        if deficit_ratio < 0.2 and overall_pressure < 0.4:
            # 여유로운 상황 - 쉬운 패턴 제외
            candidates.extend(['normal_mixed', 'hard_production'])
        elif deficit_ratio < 0.5 and overall_pressure < 0.7:
            # 보통 상황 - 모든 패턴 가능
            candidates.extend(['easy_crops', 'normal_mixed', 'hard_production'])
        else:
            # 압박 상황 - 쉬운 패턴 선호
            candidates.extend(['easy_crops', 'normal_mixed'])
        
        # 극한 도전은 특별한 조건에서만
        if self.current_struggle_score < 30 and len(resource_analysis['abundant_items']) > 10:
            candidates.append('extreme_challenge')
        
        return candidates
    
    def _apply_pattern_weights(self, pattern_candidates: List[str], use_struggle_adjustment: bool) -> Dict[str, float]:
        """5단계: 가중치 적용 (스트러글 스코어 반영)"""
        weights = {}
        
        for pattern_id in pattern_candidates:
            pattern = self.delivery_patterns[pattern_id]
            base_weight = pattern.difficulty_weight
            
            if use_struggle_adjustment:
                # 스트러글 스코어에 따른 가중치 조정
                struggle_modifier = self._get_struggle_modifier(pattern.struggle_modifier)
                adjusted_weight = base_weight * struggle_modifier
            else:
                adjusted_weight = base_weight
            
            weights[pattern_id] = adjusted_weight
        
        return weights
    
    def _get_struggle_modifier(self, base_modifier: float) -> float:
        """스트러글 스코어에 따른 가중치 조정"""
        if self.current_struggle_score > 80:
            # 스트러글이 높으면 쉬운 패턴 선호
            return base_modifier * 0.5 if base_modifier > 1.0 else base_modifier * 1.5
        elif self.current_struggle_score > 60:
            return base_modifier * 0.8 if base_modifier > 1.0 else base_modifier * 1.2
        elif self.current_struggle_score < 20:
            # 스트러글이 낮으면 어려운 패턴 선호
            return base_modifier * 1.8 if base_modifier > 1.0 else base_modifier * 0.6
        elif self.current_struggle_score < 40:
            return base_modifier * 1.3 if base_modifier > 1.0 else base_modifier * 0.8
        else:
            return base_modifier
    
    def _select_final_pattern(self, weighted_patterns: Dict[str, float]) -> DeliveryPattern:
        """6단계: 최종 납품 패턴 결정 (가중 랜덤 선택)"""
        pattern_ids = list(weighted_patterns.keys())
        weights = list(weighted_patterns.values())
        
        # 가중치가 모두 0인 경우 균등 선택
        if sum(weights) == 0:
            weights = [1.0] * len(weights)
        
        selected_id = random.choices(pattern_ids, weights=weights)[0]
        return self.delivery_patterns[selected_id]
    
    def _select_items_and_quantities(self, pattern: DeliveryPattern, source_tags: Dict) -> Dict[str, int]:
        """7단계: 아이템 선정 및 수량 결정"""
        selected_items = {}
        
        # 아이템 개수 결정
        item_count = random.randint(*pattern.item_count_range)
        
        # 레이어별 아이템 수량 계산
        layer_counts = {}
        remaining_count = item_count
        
        for layer, ratio in pattern.layer_distribution.items():
            count = max(1, int(item_count * ratio))
            layer_counts[layer] = min(count, remaining_count)
            remaining_count -= layer_counts[layer]
            if remaining_count <= 0:
                break
        
        # 각 레이어별로 아이템 선정
        for layer, count in layer_counts.items():
            layer_items = [item for item, resource in self.resource_states.items() 
                          if resource.layer == layer and self._is_valid_item(item) and self._is_unlocked_item(item)]
            
            if not layer_items:
                continue
            
            # 소스 선호도에 따른 아이템 선정
            selected_layer_items = self._select_items_by_source_preference(
                layer_items, count, pattern.source_preference, source_tags
            )
            
            # 수량 결정 (플레이어 레벨과 아이템 희소성 고려)
            for item in selected_layer_items:
                base_quantity = self._get_base_quantity_for_layer(layer)
                resource = self.resource_states.get(item)
                
                # 아이템별 수량 범위 계산
                min_quantity = base_quantity
                max_quantity = max(base_quantity + 1, int(base_quantity * 1.8))
                
                # 희소 아이템은 더 적게, 풍부한 아이템은 더 많이
                if resource and resource.is_deficit:
                    max_quantity = int(max_quantity * 0.7)  # 희소 아이템 30% 감소
                elif resource and resource.stock_ratio > 0.8:
                    min_quantity = int(min_quantity * 1.2)  # 풍부한 아이템 20% 증가
                    max_quantity = int(max_quantity * 1.5)
                
                # 최종 수량 결정 (최소 1개)
                final_quantity = random.randint(max(1, min_quantity), max(1, max_quantity))
                selected_items[item] = final_quantity
        
        return selected_items
    
    def _select_items_by_source_preference(self, layer_items: List[str], count: int, 
                                         source_preference: Dict, source_tags: Dict) -> List[str]:
        """소스 선호도에 따른 아이템 선정"""
        scored_items = []
        
        for item in layer_items:
            score = 0.0
            
            # 각 소스에서의 이용 가능성에 따른 점수 계산
            for source, preference in source_preference.items():
                if item in source_tags[source]:
                    score += preference
            
            # 희소성 보너스
            resource = self.resource_states[item]
            if resource.is_deficit:
                score += 0.3
            elif resource.stock_ratio > 0.8:
                score -= 0.2
            
            scored_items.append((item, score))
        
        # 점수 순으로 정렬하고 상위 아이템 선택
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # 가중 랜덤 선택으로 다양성 확보
        selected = []
        available_items = scored_items[:count * 2]  # 후보군 확대
        
        for _ in range(min(count, len(available_items))):
            if not available_items:
                break
                
            # 점수 기반 가중 선택
            weights = [item[1] + 0.1 for item in available_items]  # 최소 가중치 보장
            chosen_idx = random.choices(range(len(available_items)), weights=weights)[0]
            
            selected.append(available_items[chosen_idx][0])
            available_items.pop(chosen_idx)
        
        return selected
    
    def _is_valid_item(self, item_name: str) -> bool:
        """유효한 아이템인지 확인 (EmptyField 등 잘못된 아이템 필터링)"""
        if not item_name or not isinstance(item_name, str):
            return False
        
        # 잘못된 아이템명 필터링
        invalid_items = {
            'EmptyField', 'emptyfield', 'empty', '', 'null', 'None', 
            'undefined', 'placeholder', 'dummy', 'test'
        }
        
        if item_name.lower().strip() in [invalid.lower() for invalid in invalid_items]:
            return False
        
        # 아이템명이 너무 짧거나 특수문자로만 구성된 경우
        if len(item_name.strip()) < 2:
            return False
        
        # 숫자로만 구성된 경우
        if item_name.strip().isdigit():
            return False
            
        return True
    
    def _is_unlocked_item(self, item_name: str) -> bool:
        """플레이어 레벨에서 언락된 아이템인지 확인"""
        item_data = self.hayday_items.get(item_name, {})
        unlock_level = item_data.get('unlock_level', 1)
        return unlock_level <= self.player_level
    
    def _get_base_quantity_for_layer(self, layer: ItemLayer) -> int:
        """레이어별 기본 수량 (플레이어 레벨 기반 조정)"""
        # 플레이어 레벨에 따른 기본 승수 계산
        level_multiplier = 1.0 + (self.player_level - 1) * 0.02  # 레벨당 2% 증가
        level_multiplier = max(1.0, min(level_multiplier, 3.0))  # 1.0-3.0배 제한
        
        base_quantities = {
            ItemLayer.CROPS: max(3, int(8 * level_multiplier)),   # 최소 3개
            ItemLayer.MID: max(2, int(4 * level_multiplier)),     # 최소 2개  
            ItemLayer.TOP: max(1, int(2 * level_multiplier))      # 최소 1개
        }
        return base_quantities.get(layer, max(2, int(4 * level_multiplier)))
    
    def _apply_scarcity_algorithm(self, selected_items: Dict[str, int]) -> Dict[str, int]:
        """8단계: 희소성 알고리즘 적용 (PDF: RH-희소성 알고리즘 구현)"""
        adjusted_items = selected_items.copy()
        
        for item_name, quantity in selected_items.items():
            resource = self.resource_states[item_name]
            
            # Near-miss 상태 생성 (재고가 요구량보다 약간 부족한 상황)
            if resource.current_stock < quantity:
                deficit = quantity - resource.current_stock
                
                # 부족분이 적을 때 Near-miss 효과 극대화
                if deficit <= 3:
                    # 수량을 현재 재고 + 1로 조정하여 긴장감 조성
                    adjusted_items[item_name] = resource.current_stock + random.randint(1, 2)
                else:
                    # 부족분이 클 때는 원래 수량의 70-90%로 조정 (최소 2개)
                    reduction_factor = random.uniform(0.7, 0.9)
                    adjusted_items[item_name] = max(2, int(quantity * reduction_factor))
            
            # 풍부한 아이템의 경우 수량 증가로 밸런스 조정
            elif resource.stock_ratio > 0.8:
                multiplier = 1.0 + (resource.stock_ratio - 0.8) * 2.0
                adjusted_items[item_name] = int(quantity * multiplier)
        
        return adjusted_items
    
    def _calculate_struggle_score(self, items: Dict[str, int], pattern: DeliveryPattern) -> float:
        """9단계: 스트러글 스코어 계산 (PDF: 스코어 계산 및 보상 책정 완전 구현)"""
        base_score = 0.0
        item_count = len(items)
        
        for item_name, quantity in items.items():
            resource = self.resource_states[item_name]
            item_data = self.hayday_items.get(item_name, {})
            
            # PDF 기반 CraftTimeScore 계산 (생산 시간 → 난이도 스코어)
            craft_time_score = self._calculate_craft_time_score(item_data.get('production_time', 300))
            
            # PDF 기반 LayerScore 계산 (계층별 보정)
            layer_score = self._calculate_layer_score(resource, craft_time_score)
            
            # 레벨 언락 보정 (높은 레벨 아이템일수록 더 어려움)
            unlock_level = item_data.get('unlock_level', 1)
            level_modifier = 1.0 + (unlock_level - self.player_level) * 0.05 if unlock_level > self.player_level else 1.0
            
            # 희소성 점수 (PDF: 희소성 알고리즘)
            scarcity_bonus = 0.0
            if resource.is_deficit:
                scarcity_bonus = 20.0 * level_modifier
            elif resource.stock_ratio < 0.5:
                scarcity_bonus = 10.0 * level_modifier
            
            # 생산 필요성 점수
            production_penalty = 0.0
            if resource.current_stock < quantity:
                deficit = quantity - resource.current_stock
                production_penalty = deficit * 5.0 * level_modifier
            
            # PDF 수식: 최종 아이템 스코어 = (기본 + 희소성 + 생산압박) * 레이어 스코어 * 레벨 보정
            item_score = (craft_time_score + scarcity_bonus + production_penalty) * layer_score * level_modifier
            base_score += item_score
        
        # PDF: 패턴 난이도 반영 및 아이템 수량 정규화
        pattern_modifier = pattern.struggle_modifier
        final_score = base_score * pattern_modifier / max(item_count, 1)
        
        # 0-100 범위로 정규화
        normalized_score = max(0.0, min(100.0, final_score))
        
        return normalized_score
    
    def _calculate_craft_time_score(self, production_time_seconds: int) -> float:
        """PDF: CraftTimeScore 시트 구현 - 생산 시간을 난이도 스코어로 변환"""
        minutes = production_time_seconds / 60.0
        
        # PDF 구간별 다항식 적용
        if minutes <= 5:  # 1구간: 5분 이하
            # 다항식: 4t
            return 4.0 * minutes
        elif minutes <= 20:  # 2구간: 5-20분
            # 다항식: 12.1608 + 1.8241 * t - 0.0191 * t * t
            t = minutes
            return 12.1608 + 1.8241 * t - 0.0191 * t * t
        elif minutes <= 60:  # 3구간: 20-60분
            # 다항식: 15 + 0.5 * t
            return 15.0 + 0.5 * minutes
        else:  # 4구간: 60분 이상
            # 다항식: 20 + 0.3 * t
            return 20.0 + 0.3 * minutes
    
    def _calculate_layer_score(self, resource: ResourceState, base_craft_score: float) -> float:
        """PDF: LayerScore 시트 구현 - 계층별 보정 계수 적용"""
        # 기본 레이어별 계수
        base_multiplier = {
            ItemLayer.CROPS: 1.0,   # 작물 기본
            ItemLayer.MID: 1.5,     # 중급품 1.5배
            ItemLayer.TOP: 2.0      # 최고급품 2.0배
        }[resource.layer]
        
        # PDF: 하위 재료의 스코어가 높으면 계층 계수 추가 적용
        layer_multiplier = base_multiplier
        
        # 재료별 스코어에 따른 계층 계수 추가
        if base_craft_score > 50:  # 50점 이상 (20~50 구간 상위)
            layer_multiplier += 0.2
        elif base_craft_score > 20:  # 20-50 구간
            layer_multiplier += 0.1
        # 0-20 구간은 추가 계수 없음
        
        # PDF 예외 처리: 사료는 1/3 곱셈
        if 'feed' in resource.item_name.lower():
            layer_multiplier *= 0.33
        
        # PDF 예외 처리: 병렬 생산은 슬롯 수로 나누지 않음 (여기서는 생략)
        
        return layer_multiplier
    
    def _create_final_order(self, items: Dict[str, int], struggle_score: float, 
                          pattern: DeliveryPattern, delivery_type: DeliveryType) -> DeliveryOrder:
        """10단계: 최종 주문 생성"""
        
        # 난이도 등급 결정 (기차는 더 높은 기준)
        if delivery_type == DeliveryType.TRAIN:
            if struggle_score < 35:
                difficulty = DeliveryDifficulty.EASY
            elif struggle_score < 60:
                difficulty = DeliveryDifficulty.NORMAL  
            elif struggle_score < 85:
                difficulty = DeliveryDifficulty.HARD
            else:
                difficulty = DeliveryDifficulty.VERY_HARD
        else:
            if struggle_score < 25:
                difficulty = DeliveryDifficulty.EASY
            elif struggle_score < 50:
                difficulty = DeliveryDifficulty.NORMAL
            elif struggle_score < 75:
                difficulty = DeliveryDifficulty.HARD
            else:
                difficulty = DeliveryDifficulty.VERY_HARD
        
        # 총 가치 계산 (기차는 1.5-2.0배 보너스)
        total_value = 0
        total_production_time = 0
        
        for item_name, quantity in items.items():
            item_value = self.hayday_items.get(item_name, {}).get('sell_price', 100)
            production_time = self.hayday_items.get(item_name, {}).get('production_time', 300)
            
            total_value += item_value * quantity
            total_production_time += production_time * quantity
        
        # 기차 납품 가치 보너스
        if delivery_type == DeliveryType.TRAIN:
            value_multiplier = random.uniform(1.5, 2.2)
            total_value = int(total_value * value_multiplier)
        
        # 평균 생산 시간 계산
        avg_production_time = total_production_time / len(items) if items else 0
        
        # 만료 시간 계산 (기차는 더 오래)
        if delivery_type == DeliveryType.TRAIN:
            expiry_time = random.randint(180, 300)  # 3-5시간
        else:
            expiry_time = random.randint(60, 120)   # 1-2시간
        
        # 레벨 요구사항 (실제 아이템 언락 레벨 기반)
        level_requirement = self.player_level
        for item_name in items.keys():
            item_data = self.hayday_items.get(item_name, {})
            item_unlock_level = item_data.get('unlock_level', 1)
            level_requirement = max(level_requirement, item_unlock_level)
        
        # 기차 납품은 레벨 요구사항이 더 높음 (Township 특성)
        if delivery_type == DeliveryType.TRAIN:
            level_requirement = max(level_requirement, self.player_level + random.randint(2, 8))
        
        # 주문 생성
        order_id_prefix = "TRAIN" if delivery_type == DeliveryType.TRAIN else "TRUCK" 
        order_id = f"SUNGDAE_{order_id_prefix}_{len(self.delivery_history) + 1:04d}"
        
        order = DeliveryOrder(
            order_id=order_id,
            delivery_type=delivery_type,
            items=items,
            difficulty=difficulty,
            total_value=total_value,
            struggle_score=struggle_score,
            level_requirement=level_requirement,
            avg_production_time=avg_production_time,
            total_production_time=total_production_time,
            expiry_time=expiry_time,
            generation_metadata={
                'pattern_id': pattern.pattern_id,
                'player_level': self.player_level,
                'delivery_type': delivery_type.value,
                'generation_timestamp': json.dumps(None, default=str),
                'resource_deficit_ratio': len([r for r in self.resource_states.values() if r.is_deficit]) / len(self.resource_states),
                'layer_distribution': {
                    layer.value: len([item for item in items.keys() 
                                    if self.resource_states.get(item, ResourceState('', ItemLayer.CROPS, 0, 0, 0, [], False, False)).layer == layer])
                    for layer in ItemLayer
                },
                # Township 기차 전용 메타데이터
                'township_train_cars': getattr(pattern, 'train_cars', 3) if delivery_type == DeliveryType.TRAIN else None,
                'car_distribution': self._get_car_distribution_info(items) if delivery_type == DeliveryType.TRAIN else None,
                'township_algorithm_version': '2.1' if delivery_type == DeliveryType.TRAIN else '1.0',
                # PDF 분석 기반 추가 메타데이터
                'craft_time_analysis': self._generate_craft_time_analysis(items),
                'balance_impact': self._calculate_balance_impact(items, struggle_score),
                'production_complexity': self._calculate_production_complexity_metadata(items)
            }
        )
        
        # 리소스 상태 업데이트 (아이템 소비 시뮬레이션)
        self._update_resource_states_after_order(items)
        
        return order
    
    def _update_resource_states_after_order(self, consumed_items: Dict[str, int]):
        """주문 완료 후 리소스 상태 업데이트"""
        for item_name, quantity in consumed_items.items():
            if item_name in self.resource_states:
                resource = self.resource_states[item_name]
                resource.current_stock = max(0, resource.current_stock - quantity)
                
                # 생산 압박 증가 (해당 아이템의 생산 건물)
                for building_name in resource.production_buildings:
                    if building_name in self.production_pressures:
                        pressure = self.production_pressures[building_name]
                        pressure.current_load = min(1.0, pressure.current_load + 0.1)
                        pressure.items_in_queue.append(item_name)
    
    def _get_car_distribution_info(self, items: Dict[str, int]) -> Dict:
        """Township 기차 칸별 분배 정보 생성"""
        car_info = {
            'total_items': len(items),
            'estimated_cars_needed': 0,
            'layer_distribution': {'CROPS': 0, 'MID': 0, 'TOP': 0},
            'quantity_per_layer': {'CROPS': 0, 'MID': 0, 'TOP': 0}
        }
        
        for item_name, quantity in items.items():
            resource = self.resource_states.get(item_name)
            if resource:
                layer_name = resource.layer.value
                car_info['layer_distribution'][layer_name] += 1
                car_info['quantity_per_layer'][layer_name] += quantity
                
                # Township 칸 수 계산 (평균 칸당 5개 기준)
                cars_for_item = math.ceil(quantity / 5)
                car_info['estimated_cars_needed'] += cars_for_item
        
        # Township 최대 5칸 제한
        car_info['estimated_cars_needed'] = min(car_info['estimated_cars_needed'], 5)
        car_info['car_efficiency'] = sum(items.values()) / max(car_info['estimated_cars_needed'], 1)
        
        return car_info
    
    def adjust_user_struggle_score(self, new_score: float) -> Dict:
        """사용자 스트러글 스코어 조정 (수동 모드)"""
        old_score = self.current_struggle_score
        self.current_struggle_score = max(0.0, min(100.0, new_score))
        
        # 조정 기록
        adjustment = {
            'timestamp': json.dumps(None, default=str),
            'old_score': old_score,
            'new_score': self.current_struggle_score,
            'difference': self.current_struggle_score - old_score,
            'adjustment_type': 'manual'
        }
        
        self.balance_adjustments.append(adjustment)
        
        return adjustment
    
    def get_system_status(self) -> Dict:
        """시스템 상태 조회"""
        deficit_items = [name for name, resource in self.resource_states.items() if resource.is_deficit]
        high_pressure_buildings = [name for name, pressure in self.production_pressures.items() if pressure.pressure_level > 0.8]
        
        return {
            'current_struggle_score': self.current_struggle_score,
            'total_orders_generated': len(self.delivery_history),
            'deficit_items_count': len(deficit_items),
            'deficit_items': deficit_items,
            'high_pressure_buildings': high_pressure_buildings,
            'auto_generation_mode': self.auto_generation,
            'average_struggle_score': sum(self.struggle_history[-10:]) / min(10, len(self.struggle_history)) if self.struggle_history else 0,
            'last_pattern_used': self.delivery_history[-1].generation_metadata['pattern_id'] if self.delivery_history else None,
            'resource_health': {
                'healthy': len([r for r in self.resource_states.values() if 0.3 <= r.stock_ratio <= 0.8]),
                'deficit': len([r for r in self.resource_states.values() if r.stock_ratio < 0.3]),
                'abundant': len([r for r in self.resource_states.values() if r.stock_ratio > 0.8])
            }
        }
    
    def simulate_time_progression(self, hours: int = 1):
        """시간 경과 시뮬레이션 (생산 완료, 재고 회복 등)"""
        for _ in range(hours):
            # 생산 완료 처리
            for building_name, pressure in self.production_pressures.items():
                if pressure.items_in_queue:
                    # 시간당 1개 아이템 생산 완료
                    completed_item = pressure.items_in_queue.pop(0)
                    if completed_item in self.resource_states:
                        resource = self.resource_states[completed_item]
                        resource.current_stock = min(resource.max_capacity, 
                                                   resource.current_stock + random.randint(2, 5))
                
                # 생산 압박 감소
                pressure.current_load = max(0.1, pressure.current_load - 0.15)
            
            # 진열대/마켓 상태 랜덤 변경
            for resource in self.resource_states.values():
                if random.random() < 0.1:  # 10% 확률로 변경
                    resource.shelf_available = not resource.shelf_available
    
    def export_simulation_data(self) -> Dict:
        """시뮬레이션 데이터 내보내기 (PDF 분석 결과 포함)"""
        return {
            'delivery_history': [
                {
                    'order_id': order.order_id,
                    'delivery_type': order.delivery_type.value,
                    'items': order.items,
                    'difficulty': order.difficulty.value,
                    'total_value': order.total_value,
                    'struggle_score': order.struggle_score,
                    'level_requirement': order.level_requirement,
                    'avg_production_time': order.avg_production_time,
                    'total_production_time': order.total_production_time,
                    'expiry_time': order.expiry_time,
                    'metadata': order.generation_metadata,
                    # 추가된 분석 데이터
                    'comprehensive_analysis': self.generate_comprehensive_analysis(order),
                    'reward_system': self.calculate_advanced_reward_system(order)
                }
                for order in self.delivery_history
            ],
            'struggle_history': self.struggle_history,
            'balance_adjustments': self.balance_adjustments,
            'final_system_status': self.get_system_status(),
            'dynamic_balancing_data': self.get_dynamic_balancing_display_data(),
            # PDF 분석 기반 추가 데이터
            'ui_optimization_report': self.generate_ui_optimization_report(),
            'township_comparison': self._generate_township_comparison(),
            'craft_time_analysis': self._generate_overall_craft_time_analysis(),
            'layer_score_summary': self._generate_layer_score_summary()
        }
    
    def get_dynamic_balancing_display_data(self) -> Dict:
        """
        UI/UX에 다이나믹 밸런싱 표시를 위한 데이터 생성
        
        납품, 다이나믹밸런싱 시뮬레이터로서의 정점 표현
        """
        current_status = self.get_system_status()
        
        return {
            # 1. 시스템 상태 오버뷰
            'system_overview': {
                'struggle_score': {
                    'current': self.current_struggle_score,
                    'trend': self._get_struggle_trend(),
                    'target_range': [40, 70],
                    'status': self._get_struggle_status()
                },
                'resource_health': current_status['resource_health'],
                'active_patterns': self._get_active_patterns_summary()
            },
            
            # 2. 실시간 밸런싱 지표
            'balancing_metrics': {
                'pressure_index': self._calculate_overall_pressure(),
                'scarcity_index': self._calculate_scarcity_index(),
                'diversity_score': self._calculate_item_diversity(),
                'efficiency_rating': self._calculate_system_efficiency()
            },
            
            # 3. 진행 중인 주문 분석
            'order_analysis': self._get_recent_orders_analysis(),
            
            # 4. 다이나믹 조정 로그
            'adjustment_log': self._get_recent_adjustments(),
            
            # 5. 예측 및 추천
            'predictions': {
                'next_struggle_prediction': self._predict_next_struggle_score(),
                'recommended_actions': self._get_balancing_recommendations(),
                'risk_alerts': self._get_risk_alerts()
            },
            
            # 6. Township 기차 전용 데이터
            'township_train_data': self._get_township_display_data(),
            
            # 7. 성능 대시보드
            'performance_dashboard': {
                'orders_per_hour': len(self.delivery_history) / max(1, len(self.struggle_history) * 0.1),
                'average_value': sum(order.total_value for order in self.delivery_history[-10:]) / min(10, len(self.delivery_history)) if self.delivery_history else 0,
                'success_rate': self._calculate_success_rate(),
                'balance_stability': self._calculate_balance_stability()
            }
        }
    
    def generate_ui_optimization_report(self) -> Dict:
        """
        UI/UX 최적화 보고서 생성
        납품, 다이나믹밸런싱 시뮬레이터로서의 정점을 보여주는 최적의 방식
        """
        return {
            'executive_summary': {
                'total_orders': len(self.delivery_history),
                'current_balance_score': self._calculate_overall_balance_score(),
                'system_health': self._assess_system_health(),
                'optimization_level': self._calculate_optimization_level()
            },
            'visual_indicators': self._generate_visual_indicators(),
            'real_time_metrics': self._generate_real_time_metrics(),
            'interactive_elements': self._generate_interactive_elements(),
            'performance_insights': self._generate_performance_insights()
        }
    
    @classmethod
    def create_from_hayday_simulator(cls, hayday_simulator, player_level: int = 20):
        """HayDay 시뮬레이터에서 SungDae 시뮬레이터 생성"""
        # HayDay 아이템 데이터 변환
        hayday_items = {}
        
        # Orders 데이터에서 아이템 추출
        if hasattr(hayday_simulator, 'orders') and not hayday_simulator.orders.empty:
            for _, row in hayday_simulator.orders.iterrows():
                name = row.get('Name', '')
                if name and isinstance(name, str) and name.strip():
                    hayday_items[name] = {
                        'sell_price': int(row.get('Value', 100)),
                        'production_time': int(row.get('Time', 300)),
                        'buildings': [row.get('Building', 'farm')],
                        'unlock_level': int(row.get('UnlockLevel', 1))
                    }
        
        # 실제 헤이데이 아이템들로 교체 (orders 데이터가 올바르지 않은 경우)
        if not hayday_items or any('Order ' in item for item in hayday_items.keys()):
            # 기존 잘못된 데이터 클리어
            hayday_items.clear()
            
            # 실제 헤이데이 아이템들
            real_hayday_items = {
                # 기본 작물들 (CROPS 레이어)
                'Wheat': {'sell_price': 1, 'production_time': 120, 'buildings': ['field'], 'unlock_level': 1},
                'Corn': {'sell_price': 2, 'production_time': 300, 'buildings': ['field'], 'unlock_level': 1},
                'Carrot': {'sell_price': 3, 'production_time': 600, 'buildings': ['field'], 'unlock_level': 8},
                'Soybean': {'sell_price': 4, 'production_time': 1200, 'buildings': ['field'], 'unlock_level': 15},
                'Sugarcane': {'sell_price': 2, 'production_time': 240, 'buildings': ['field'], 'unlock_level': 5},
                'Cocoa': {'sell_price': 3, 'production_time': 480, 'buildings': ['field'], 'unlock_level': 13},
                'Coffee Bean': {'sell_price': 4, 'production_time': 960, 'buildings': ['field'], 'unlock_level': 23},
                'Tomato': {'sell_price': 5, 'production_time': 1440, 'buildings': ['field'], 'unlock_level': 20},
                'Potato': {'sell_price': 4, 'production_time': 720, 'buildings': ['field'], 'unlock_level': 18},
                'Cotton': {'sell_price': 3, 'production_time': 480, 'buildings': ['field'], 'unlock_level': 7},
                'Indigo': {'sell_price': 5, 'production_time': 1800, 'buildings': ['field'], 'unlock_level': 25},
                'Pumpkin': {'sell_price': 6, 'production_time': 2160, 'buildings': ['field'], 'unlock_level': 30},
                'Chili Pepper': {'sell_price': 7, 'production_time': 2400, 'buildings': ['field'], 'unlock_level': 35},
                
                # 동물 제품들 (MID 레이어)
                'Egg': {'sell_price': 12, 'production_time': 1200, 'buildings': ['chicken_coop'], 'unlock_level': 6},
                'Milk': {'sell_price': 25, 'production_time': 3600, 'buildings': ['cow_pasture'], 'unlock_level': 11},
                'Bacon': {'sell_price': 73, 'production_time': 2400, 'buildings': ['pig_pen'], 'unlock_level': 14},
                'Wool': {'sell_price': 52, 'production_time': 14400, 'buildings': ['sheep_pasture'], 'unlock_level': 9},
                
                # 베이커리 제품들 (MID 레이어)
                'Bread': {'sell_price': 27, 'production_time': 300, 'buildings': ['bakery'], 'unlock_level': 3},
                'Cookie': {'sell_price': 67, 'production_time': 1800, 'buildings': ['bakery'], 'unlock_level': 8},
                'Brown Sugar': {'sell_price': 50, 'production_time': 900, 'buildings': ['sugar_mill'], 'unlock_level': 19},
                'White Sugar': {'sell_price': 72, 'production_time': 1200, 'buildings': ['sugar_mill'], 'unlock_level': 26},
                'Syrup': {'sell_price': 98, 'production_time': 2400, 'buildings': ['sugar_mill'], 'unlock_level': 31},
                
                # 데어리 제품들 (MID 레이어)
                'Butter': {'sell_price': 87, 'production_time': 1800, 'buildings': ['dairy'], 'unlock_level': 13},
                'Cheese': {'sell_price': 165, 'production_time': 3600, 'buildings': ['dairy'], 'unlock_level': 17},
                'Cream': {'sell_price': 234, 'production_time': 5400, 'buildings': ['dairy'], 'unlock_level': 22},
                'Goat Cheese': {'sell_price': 382, 'production_time': 7200, 'buildings': ['dairy'], 'unlock_level': 38},
                
                # 패브릭 제품들 (MID-TOP 레이어)
                'Fabric': {'sell_price': 122, 'production_time': 1200, 'buildings': ['loom'], 'unlock_level': 15},
                'Sweater': {'sell_price': 308, 'production_time': 4800, 'buildings': ['knitting'], 'unlock_level': 21},
                'Dress': {'sell_price': 432, 'production_time': 7200, 'buildings': ['tailoring'], 'unlock_level': 25},
                'Violet Dress': {'sell_price': 747, 'production_time': 10800, 'buildings': ['tailoring'], 'unlock_level': 33},
                'Tuxedo': {'sell_price': 973, 'production_time': 14400, 'buildings': ['tailoring'], 'unlock_level': 41},
                
                # 주얼리 (TOP 레이어)
                'Silver Ore': {'sell_price': 7, 'production_time': 1800, 'buildings': ['mine'], 'unlock_level': 24},
                'Gold Ore': {'sell_price': 8, 'production_time': 2400, 'buildings': ['mine'], 'unlock_level': 28},
                'Platinum Ore': {'sell_price': 9, 'production_time': 3000, 'buildings': ['mine'], 'unlock_level': 39},
                'Silver Bar': {'sell_price': 27, 'production_time': 1800, 'buildings': ['smelter'], 'unlock_level': 24},
                'Gold Bar': {'sell_price': 36, 'production_time': 2400, 'buildings': ['smelter'], 'unlock_level': 28},
                'Platinum Bar': {'sell_price': 45, 'production_time': 3000, 'buildings': ['smelter'], 'unlock_level': 39},
                'Silver Ring': {'sell_price': 180, 'production_time': 1800, 'buildings': ['jeweler'], 'unlock_level': 24},
                'Gold Ring': {'sell_price': 270, 'production_time': 2700, 'buildings': ['jeweler'], 'unlock_level': 28},
                'Platinum Ring': {'sell_price': 360, 'production_time': 3600, 'buildings': ['jeweler'], 'unlock_level': 39},
                'Silver Necklace': {'sell_price': 522, 'production_time': 5400, 'buildings': ['jeweler'], 'unlock_level': 27},
                'Gold Necklace': {'sell_price': 783, 'production_time': 8100, 'buildings': ['jeweler'], 'unlock_level': 32},
                'Platinum Necklace': {'sell_price': 1044, 'production_time': 10800, 'buildings': ['jeweler'], 'unlock_level': 42},
                'Silver Bracelet': {'sell_price': 900, 'production_time': 7200, 'buildings': ['jeweler'], 'unlock_level': 29},
                'Gold Bracelet': {'sell_price': 1350, 'production_time': 10800, 'buildings': ['jeweler'], 'unlock_level': 34},
                'Platinum Bracelet': {'sell_price': 1800, 'production_time': 14400, 'buildings': ['jeweler'], 'unlock_level': 44},
                
                # 피드밀 제품들 (MID 레이어)
                'Chicken Feed': {'sell_price': 36, 'production_time': 1200, 'buildings': ['feed_mill'], 'unlock_level': 6},
                'Cow Feed': {'sell_price': 72, 'production_time': 2400, 'buildings': ['feed_mill'], 'unlock_level': 11},
                'Pig Feed': {'sell_price': 108, 'production_time': 3600, 'buildings': ['feed_mill'], 'unlock_level': 14},
                'Sheep Feed': {'sell_price': 144, 'production_time': 4800, 'buildings': ['feed_mill'], 'unlock_level': 16},
                'Goat Feed': {'sell_price': 216, 'production_time': 7200, 'buildings': ['feed_mill'], 'unlock_level': 38},
                
                # BBQ 그릴 제품들 (MID-TOP 레이어)
                'Hamburger': {'sell_price': 272, 'production_time': 3600, 'buildings': ['bbq_grill'], 'unlock_level': 18},
                'Pizza': {'sell_price': 350, 'production_time': 4800, 'buildings': ['bbq_grill'], 'unlock_level': 29},
                'Bacon and Eggs': {'sell_price': 170, 'production_time': 2400, 'buildings': ['bbq_grill'], 'unlock_level': 14},
                'Fish Burger': {'sell_price': 432, 'production_time': 6000, 'buildings': ['bbq_grill'], 'unlock_level': 44},
                
                # 음료 및 디저트 (TOP 레이어)
                'Apple Juice': {'sell_price': 117, 'production_time': 1800, 'buildings': ['juice_press'], 'unlock_level': 12},
                'Carrot Juice': {'sell_price': 162, 'production_time': 2700, 'buildings': ['juice_press'], 'unlock_level': 16},
                'Tomato Juice': {'sell_price': 243, 'production_time': 4200, 'buildings': ['juice_press'], 'unlock_level': 22},
                'Blackberry Muffin': {'sell_price': 648, 'production_time': 7200, 'buildings': ['cake_oven'], 'unlock_level': 48},
                'Carrot Cake': {'sell_price': 504, 'production_time': 5400, 'buildings': ['cake_oven'], 'unlock_level': 36},
                'Red Berry Cake': {'sell_price': 756, 'production_time': 8100, 'buildings': ['cake_oven'], 'unlock_level': 50}
            }
            hayday_items.update(real_hayday_items)
        
        return cls(hayday_items, player_level)
    
    # Helper methods for UI display data
    def _get_struggle_trend(self) -> str:
        if len(self.struggle_history) < 5:
            return 'insufficient_data'
        recent = self.struggle_history[-5:]
        if recent[-1] > recent[0] + 10:
            return 'increasing'
        elif recent[-1] < recent[0] - 10:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_struggle_status(self) -> str:
        score = self.current_struggle_score
        if 40 <= score <= 70:
            return 'optimal'
        elif 25 <= score < 40 or 70 < score <= 85:
            return 'acceptable'
        else:
            return 'needs_adjustment'
    
    def _get_active_patterns_summary(self) -> Dict:
        if not self.delivery_history:
            return {}
        recent_patterns = [order.generation_metadata.get('pattern_id', 'unknown') 
                         for order in self.delivery_history[-10:]]
        pattern_counts = {}
        for pattern in recent_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return {
            'most_used': max(pattern_counts, key=pattern_counts.get) if pattern_counts else 'none',
            'pattern_distribution': pattern_counts,
            'diversity_score': len(pattern_counts) / max(len(recent_patterns), 1) * 100
        }
    
    def _calculate_overall_pressure(self) -> float:
        total_pressure = sum(p.pressure_level for p in self.production_pressures.values())
        return (total_pressure / len(self.production_pressures)) * 100
    
    def _calculate_scarcity_index(self) -> float:
        deficit_count = len([r for r in self.resource_states.values() if r.is_deficit])
        return (deficit_count / len(self.resource_states)) * 100
    
    def _calculate_item_diversity(self) -> float:
        if not self.delivery_history:
            return 0
        recent_items = set()
        for order in self.delivery_history[-5:]:
            recent_items.update(order.items.keys())
        return min(100, len(recent_items) / len(self.hayday_items) * 200)
    
    def _calculate_system_efficiency(self) -> float:
        """시스템 효율성 계산"""
        if not self.delivery_history:
            return 50.0
        
        # 최근 10개 주문의 효율성 지표 계산
        recent_orders = self.delivery_history[-10:]
        
        # 1. 주문 완료 비율
        completion_rate = len(recent_orders) / 10 * 100 if len(recent_orders) > 0 else 0
        
        # 2. 평균 가치 효율성 (실제 가치 vs 최대 가치)
        avg_value = sum(o.total_value for o in recent_orders) / len(recent_orders) if recent_orders else 0
        max_possible_value = max((o.total_value for o in recent_orders), default=100)
        value_efficiency = (avg_value / max_possible_value * 100) if max_possible_value > 0 else 50
        
        # 3. 리소스 활용도
        healthy_resources = len([r for r in self.resource_states.values() if not r.is_deficit])
        total_resources = len(self.resource_states)
        resource_efficiency = (healthy_resources / total_resources * 100) if total_resources > 0 else 50
        
        # 가중 평균 계산
        efficiency = (completion_rate * 0.3 + value_efficiency * 0.4 + resource_efficiency * 0.3)
        
        return min(100, max(0, efficiency))
    
    def _get_recent_orders_analysis(self) -> Dict:
        if not self.delivery_history:
            return {'total_orders': 0, 'analysis': 'no_data'}
        recent = self.delivery_history[-10:]
        return {
            'total_orders': len(self.delivery_history),
            'recent_count': len(recent),
            'difficulty_distribution': {difficulty.value: len([o for o in recent if o.difficulty == difficulty]) for difficulty in DeliveryDifficulty},
            'delivery_type_distribution': {dtype.value: len([o for o in recent if o.delivery_type == dtype]) for dtype in DeliveryType},
            'average_struggle': sum(o.struggle_score for o in recent) / len(recent),
            'average_value': sum(o.total_value for o in recent) / len(recent)
        }
    
    def _get_recent_adjustments(self) -> List[Dict]:
        return self.balance_adjustments[-5:] if self.balance_adjustments else []
    
    def _predict_next_struggle_score(self) -> Dict:
        if len(self.struggle_history) < 3:
            return {'predicted_score': self.current_struggle_score, 'confidence': 0}
        recent = self.struggle_history[-5:]
        trend = (recent[-1] - recent[0]) / len(recent)
        predicted = self.current_struggle_score + trend
        variance = sum((x - sum(recent)/len(recent))**2 for x in recent) / len(recent)
        confidence = max(0, 100 - variance)
        
        return {
            'predicted_score': max(0, min(100, predicted)),
            'confidence': confidence,
            'trend_direction': 'up' if trend > 2 else 'down' if trend < -2 else 'stable'
        }
    
    def _get_balancing_recommendations(self) -> List[str]:
        recommendations = []
        if self.current_struggle_score > 80:
            recommendations.append("스트러글 스코어가 너무 높습니다. 더 쉬운 패턴을 사용하세요.")
        elif self.current_struggle_score < 20:
            recommendations.append("스트러글 스코어가 낮습니다. 더 도전적인 패턴을 시도해보세요.")
        deficit_count = len([r for r in self.resource_states.values() if r.is_deficit])
        if deficit_count > len(self.resource_states) * 0.3:
            recommendations.append("부족한 아이템이 많습니다. 생산 효율성을 높이거나 재고를 보충하세요.")
        return recommendations or ["현재 밸런스 상태가 양호합니다."]
    
    def _get_risk_alerts(self) -> List[Dict]:
        alerts = []
        if self.current_struggle_score > 90:
            alerts.append({'level': 'critical', 'message': '매우 높은 스트레스 상태입니다.', 'action': 'reduce_difficulty'})
        elif self.current_struggle_score < 10:
            alerts.append({'level': 'warning', 'message': '도전 요소가 부족합니다.', 'action': 'increase_difficulty'})
        return alerts
    
    def _get_township_display_data(self) -> Dict:
        train_orders = [o for o in self.delivery_history if o.delivery_type == DeliveryType.TRAIN]
        if not train_orders:
            return {'status': 'no_train_orders', 'total_trains': 0}
        return {
            'status': 'active',
            'total_trains': len(train_orders),
            'train_performance': {
                'avg_value': sum(o.total_value for o in train_orders[-5:]) / min(5, len(train_orders)),
                'avg_struggle': sum(o.struggle_score for o in train_orders[-5:]) / min(5, len(train_orders)),
                'success_rate': len([o for o in train_orders[-10:] if o.struggle_score >= 40]) / min(10, len(train_orders)) * 100 if train_orders else 0
            }
        }
    
    def _calculate_success_rate(self) -> float:
        if not self.delivery_history:
            return 0
        recent = self.delivery_history[-20:]
        successes = len([o for o in recent if o.struggle_score >= 40])
        return (successes / len(recent)) * 100
    
    def _calculate_balance_stability(self) -> float:
        if len(self.struggle_history) < 5:
            return 50
        recent = self.struggle_history[-10:]
        mean_score = sum(recent) / len(recent)
        variance = sum((score - mean_score) ** 2 for score in recent) / len(recent)
        return max(0, 100 - variance)
    
    def _calculate_overall_balance_score(self) -> float:
        factors = [
            self._get_struggle_balance_score(),
            self._get_resource_balance_score(),
            self._get_production_balance_score(),
            self._get_diversity_balance_score()
        ]
        return sum(factors) / len(factors)
    
    def _get_struggle_balance_score(self) -> float:
        ideal_range = (40, 70)
        if ideal_range[0] <= self.current_struggle_score <= ideal_range[1]:
            return 100
        distance = min(abs(self.current_struggle_score - ideal_range[0]), 
                      abs(self.current_struggle_score - ideal_range[1]))
        return max(0, 100 - distance * 2)
    
    def _get_resource_balance_score(self) -> float:
        healthy_count = len([r for r in self.resource_states.values() if 0.3 <= r.stock_ratio <= 0.8])
        return (healthy_count / len(self.resource_states)) * 100
    
    def _get_production_balance_score(self) -> float:
        balanced_buildings = len([p for p in self.production_pressures.values() if 0.3 <= p.pressure_level <= 0.7])
        return (balanced_buildings / len(self.production_pressures)) * 100
    
    def _get_diversity_balance_score(self) -> float:
        if not self.delivery_history:
            return 50
        recent_items = set()
        for order in self.delivery_history[-10:]:
            recent_items.update(order.items.keys())
        diversity_ratio = len(recent_items) / len(self.hayday_items)
        return min(100, diversity_ratio * 200)
    
    def _assess_system_health(self) -> str:
        balance_score = self._calculate_overall_balance_score()
        if balance_score >= 85:
            return 'Excellent'
        elif balance_score >= 70:
            return 'Good'
        elif balance_score >= 55:
            return 'Fair'
        else:
            return 'Needs Attention'
    
    def _calculate_optimization_level(self) -> str:
        factors = {
            'balance': self._calculate_overall_balance_score(),
            'efficiency': self._calculate_system_efficiency(),
            'stability': self._calculate_balance_stability(),
            'performance': min(100, len(self.delivery_history) * 5)
        }
        overall = sum(factors.values()) / len(factors)
        if overall >= 90:
            return 'Peak Performance'
        elif overall >= 80:
            return 'Highly Optimized'
        elif overall >= 70:
            return 'Well Optimized'
        elif overall >= 60:
            return 'Moderately Optimized'
        else:
            return 'Needs Optimization'
    
    def _generate_visual_indicators(self) -> Dict:
        return {
            'struggle_gauge': {
                'value': self.current_struggle_score,
                'color': self._get_struggle_color(),
                'zones': {'optimal': (40, 70), 'acceptable': (25, 85)}
            },
            'resource_status_grid': self._generate_resource_grid(),
            'production_heatmap': self._generate_production_heatmap(),
            'trend_charts': self._generate_trend_data()
        }
    
    def _get_struggle_color(self) -> str:
        score = self.current_struggle_score
        if 40 <= score <= 70:
            return 'success'
        elif 25 <= score < 40 or 70 < score <= 85:
            return 'warning'
        else:
            return 'danger'
    
    def _generate_resource_grid(self) -> List[Dict]:
        grid_data = []
        for item_name, resource in self.resource_states.items():
            grid_data.append({
                'item': item_name,
                'layer': resource.layer.value,
                'stock_ratio': resource.stock_ratio,
                'status': 'deficit' if resource.is_deficit else 'abundant' if resource.stock_ratio > 0.8 else 'normal',
                'current_stock': resource.current_stock,
                'max_capacity': resource.max_capacity
            })
        return sorted(grid_data, key=lambda x: x['stock_ratio'])
    
    def _generate_production_heatmap(self) -> Dict:
        heatmap_data = {}
        for building_name, pressure in self.production_pressures.items():
            heatmap_data[building_name] = {
                'load': pressure.pressure_level,
                'intensity': 'high' if pressure.pressure_level > 0.8 else 'medium' if pressure.pressure_level > 0.5 else 'low',
                'queue_length': len(pressure.items_in_queue),
                'capacity': pressure.max_capacity
            }
        return heatmap_data
    
    def _generate_trend_data(self) -> Dict:
        return {
            'struggle_trend': self.struggle_history[-20:] if len(self.struggle_history) >= 20 else self.struggle_history,
            'value_trend': [order.total_value for order in self.delivery_history[-20:]] if len(self.delivery_history) >= 20 else [order.total_value for order in self.delivery_history],
            'difficulty_trend': [order.difficulty.value for order in self.delivery_history[-20:]] if len(self.delivery_history) >= 20 else [order.difficulty.value for order in self.delivery_history]
        }
    
    def _generate_real_time_metrics(self) -> Dict:
        return {
            'orders_per_minute': self._calculate_order_rate(),
            'average_completion_time': self._calculate_avg_completion_time(),
            'success_streak': self._calculate_current_streak(),
            'efficiency_index': self._calculate_current_efficiency()
        }
    
    def _calculate_order_rate(self) -> float:
        if len(self.delivery_history) < 2:
            return 0
        return len(self.delivery_history) / max(1, len(self.struggle_history) * 0.1)
    
    def _calculate_avg_completion_time(self) -> float:
        if not self.delivery_history:
            return 0
        recent_orders = self.delivery_history[-10:]
        return sum(order.total_production_time for order in recent_orders) / len(recent_orders)
    
    def _calculate_current_streak(self) -> int:
        if not self.delivery_history:
            return 0
        streak = 0
        for order in reversed(self.delivery_history):
            if order.struggle_score >= 40:
                streak += 1
            else:
                break
        return streak
    
    def _calculate_current_efficiency(self) -> float:
        if not self.delivery_history:
            return 50
        recent_order = self.delivery_history[-1]
        time_efficiency = recent_order.total_value / max(recent_order.total_production_time, 1) * 60
        return min(100, time_efficiency)
    
    def _generate_interactive_elements(self) -> Dict:
        return {
            'adjustable_parameters': {
                'struggle_target': {
                    'current': self.current_struggle_score,
                    'min': 0,
                    'max': 100,
                    'optimal_range': [40, 70]
                },
                'auto_generation': {
                    'enabled': self.auto_generation,
                    'description': 'Automatic order generation based on dynamic balancing'
                }
            },
            'quick_actions': [
                {'action': 'generate_truck_order', 'label': '트럭 주문 생성', 'icon': 'truck'},
                {'action': 'generate_train_order', 'label': '기차 주문 생성', 'icon': 'train'},
                {'action': 'simulate_time', 'label': '시간 경과 시뮬레이션', 'icon': 'clock'},
                {'action': 'reset_balance', 'label': '밸런스 초기화', 'icon': 'refresh'}
            ],
            'detailed_views': [
                {'view': 'resource_detail', 'label': '리소스 상세 보기'},
                {'view': 'production_analysis', 'label': '생산 분석'},
                {'view': 'pattern_analysis', 'label': '패턴 분석'},
                {'view': 'township_comparison', 'label': 'Township 비교 분석'}
            ]
        }
    
    def _generate_performance_insights(self) -> Dict:
        insights = []
        if self.current_struggle_score > 80:
            insights.append({'type': 'warning', 'title': '높은 스트레스 상태', 'message': '현재 스트러글 스코어가 높습니다.', 'priority': 'high'})
        elif self.current_struggle_score < 20:
            insights.append({'type': 'info', 'title': '도전 요소 부족', 'message': '현재 난이도가 낮습니다.', 'priority': 'medium'})
        
        return {
            'insights': insights,
            'key_metrics': {
                'balance_score': self._calculate_overall_balance_score(),
                'efficiency_score': self._calculate_system_efficiency(),
                'stability_score': self._calculate_balance_stability()
            },
            'improvement_suggestions': self._generate_improvement_suggestions()
        }
    
    def _generate_improvement_suggestions(self) -> List[str]:
        suggestions = []
        balance_score = self._calculate_overall_balance_score()
        if balance_score < 70:
            suggestions.append("전체적인 밸런스 개선이 필요합니다.")
        efficiency = self._calculate_system_efficiency()
        if efficiency < 60:
            suggestions.append("시스템 효율성이 낮습니다.")
        if not suggestions:
            suggestions.append("현재 시스템이 잘 최적화되어 있습니다.")
        return suggestions
    
    def _generate_township_comparison(self) -> Dict:
        truck_orders = [o for o in self.delivery_history if o.delivery_type == DeliveryType.TRUCK]
        train_orders = [o for o in self.delivery_history if o.delivery_type == DeliveryType.TRAIN]
        return {
            'design_philosophy': {
                'hayday_approach': 'Low stress, cooperative gameplay',
                'township_approach': 'Intentional friction, challenge-based progression',
                'sungdae_implementation': 'Hybrid system with configurable difficulty'
            },
            'performance_comparison': {
                'truck_orders': {'count': len(truck_orders), 'avg_value': sum(o.total_value for o in truck_orders) / max(1, len(truck_orders)), 'avg_struggle': sum(o.struggle_score for o in truck_orders) / max(1, len(truck_orders))},
                'train_orders': {'count': len(train_orders), 'avg_value': sum(o.total_value for o in train_orders) / max(1, len(train_orders)), 'avg_struggle': sum(o.struggle_score for o in train_orders) / max(1, len(train_orders))},
                'value_multiplier': (sum(o.total_value for o in train_orders) / max(1, len(train_orders))) / max(1, sum(o.total_value for o in truck_orders) / max(1, len(truck_orders)))
            }
        }
    
    def _generate_overall_craft_time_analysis(self) -> Dict:
        all_items_analysis = {}
        for item_name, item_data in self.hayday_items.items():
            production_time = item_data.get('production_time', 300)
            craft_score = self._calculate_craft_time_score(production_time)
            all_items_analysis[item_name] = {
                'production_time_seconds': production_time,
                'production_time_minutes': production_time / 60,
                'craft_time_score': craft_score,
                'complexity_tier': self._get_complexity_tier(production_time),
                'unlock_level': item_data.get('unlock_level', 1)
            }
        return {
            'item_analysis': all_items_analysis,
            'complexity_distribution': self._get_complexity_distribution(),
            'time_efficiency_ranking': self._get_time_efficiency_ranking()
        }
    
    def _generate_layer_score_summary(self) -> Dict:
        layer_summary = {}
        for layer in ItemLayer:
            layer_items = [item for item, resource in self.resource_states.items() if resource.layer == layer]
            if layer_items:
                avg_stock = sum(self.resource_states[item].stock_ratio for item in layer_items) / len(layer_items)
                deficit_count = len([item for item in layer_items if self.resource_states[item].is_deficit])
                layer_summary[layer.value] = {
                    'total_items': len(layer_items),
                    'avg_stock_ratio': avg_stock,
                    'deficit_items': deficit_count,
                    'deficit_ratio': deficit_count / len(layer_items),
                    'base_multiplier': {ItemLayer.CROPS: 1.0, ItemLayer.MID: 1.5, ItemLayer.TOP: 2.0}[layer]
                }
        return layer_summary
    
    def _get_complexity_tier(self, production_time: int) -> str:
        if production_time < 600:
            return 'Simple'
        elif production_time < 3600:
            return 'Moderate'
        elif production_time < 7200:
            return 'Complex'
        else:
            return 'Advanced'
    
    def _get_complexity_distribution(self) -> Dict:
        distribution = {'Simple': 0, 'Moderate': 0, 'Complex': 0, 'Advanced': 0}
        for item_data in self.hayday_items.values():
            tier = self._get_complexity_tier(item_data.get('production_time', 300))
            distribution[tier] += 1
        return distribution
    
    def _get_time_efficiency_ranking(self) -> List[Dict]:
        efficiency_data = []
        for item_name, item_data in self.hayday_items.items():
            value = item_data.get('sell_price', 100)
            time = item_data.get('production_time', 300)
            efficiency = value / max(time, 1) * 3600
            efficiency_data.append({
                'item': item_name,
                'efficiency': efficiency,
                'value': value,
                'time': time,
                'unlock_level': item_data.get('unlock_level', 1)
            })
        return sorted(efficiency_data, key=lambda x: x['efficiency'], reverse=True)[:10]
    
    def get_available_items(self) -> List[str]:
        """사용 가능한 아이템 목록"""
        return list(self.hayday_items.keys())
    
    def get_item_info(self, item_name: str) -> Dict:
        """특정 아이템의 정보 조회"""
        if item_name not in self.hayday_items:
            return {}
        
        resource = self.resource_states.get(item_name)
        item_data = self.hayday_items[item_name]
        
        return {
            'name': item_name,
            'sell_price': item_data.get('sell_price', 100),
            'production_time': item_data.get('production_time', 300),
            'buildings': item_data.get('buildings', []),
            'unlock_level': item_data.get('unlock_level', 1),
            'current_stock': resource.current_stock if resource else 0,
            'max_capacity': resource.max_capacity if resource else 100,
            'stock_ratio': resource.stock_ratio if resource else 0.5,
            'layer': resource.layer.value if resource else ItemLayer.MID.value,
            'is_deficit': resource.is_deficit if resource else False,
            'shelf_available': resource.shelf_available if resource else False,
            'market_available': resource.market_available if resource else True
        }
    
    def batch_generate_orders(self, count: int, delivery_types: List[DeliveryType] = None) -> List[DeliveryOrder]:
        """배치 주문 생성 (테스트 및 분석용) - 각 주문마다 희소성/다양성 지수 재계산"""
        if delivery_types is None:
            delivery_types = [DeliveryType.TRUCK, DeliveryType.TRAIN]
        
        orders = []
        for i in range(count):
            delivery_type = random.choice(delivery_types)
            order = self.generate_delivery_order(delivery_type, use_struggle_adjustment=True)
            orders.append(order)
            
            # 각 주문 생성 후 리소스 상태 업데이트 (희소성/다양성 지수 변화 반영)
            self._update_resource_state_after_order(order)
            
            # 시간 경과 시뮬레이션 (랜덤)
            if random.random() < 0.3:
                self.simulate_time_progression(random.randint(1, 3))
        
        return orders
    
    def _update_resource_state_after_order(self, order: DeliveryOrder):
        """주문 생성 후 리소스 상태 업데이트 (배치 생성시 희소성/다양성 지수 변화 반영)"""
        for item_name, quantity in order.items.items():
            if item_name in self.resources:
                # 재고 감소 시뮬레이션 (실제 완료는 아니지만 시장 압력 반영)
                resource = self.resources[item_name]
                reduction = min(quantity, resource.current_stock // 2)  # 실제 재고의 절반까지만 감소
                resource.current_stock = max(0, resource.current_stock - reduction)
                
                # 진열대/마켓 가용성 랜덤 업데이트 (시장 변동성 시뮬레이션)
                if random.random() < 0.1:  # 10% 확률로 가용성 변경
                    resource.shelf_available = random.choice([True, False])
                    resource.market_available = random.choice([True, False])
    
    def calculate_advanced_reward_system(self, order: DeliveryOrder) -> Dict:
        """
        고급 보상 계산 시스템 (PDF: RH-스코어 계산 및 보상 책정)
        
        다층 구조의 보상 시스템:
        1. 기본 보상 (아이템 가치 기준)
        2. 난이도 보너스 (스트러글 스코어 기준)
        3. 레이어 배수 (TOP/MID/CROPS 별 차등)
        4. 완성도 보너스 (생산 시간 대비)
        5. 연속 성공 보너스
        """
        
        base_reward = order.total_value
        layer_multipliers = {'TOP': 3.0, 'MID': 2.0, 'CROPS': 1.5}
        
        # 1. 레이어별 가중 보상 계산
        layer_weighted_reward = 0
        layer_distribution = order.generation_metadata.get('layer_distribution', {})
        
        for layer_name, count in layer_distribution.items():
            if count > 0:
                multiplier = layer_multipliers.get(layer_name, 1.0)
                layer_weighted_reward += base_reward * (count / sum(layer_distribution.values())) * multiplier
        
        # 2. 스트러글 기반 난이도 보너스
        struggle_bonus_rate = self._calculate_struggle_bonus_rate(order.struggle_score)
        struggle_bonus = base_reward * struggle_bonus_rate
        
        # 3. 기차 납품 특별 보너스
        delivery_bonus = 0
        if order.delivery_type == DeliveryType.TRAIN:
            delivery_bonus = base_reward * 0.5  # 50% 추가 보너스
        
        # 4. 완성도 보너스 (생산 시간 대비 가치)
        time_efficiency = base_reward / max(order.total_production_time, 1)
        efficiency_bonus = min(base_reward * 0.3, time_efficiency * 100)  # 최대 30% 보너스
        
        # 5. 연속 성공 보너스 (최근 10개 주문의 성공률 기준)
        streak_bonus = self._calculate_streak_bonus(base_reward)
        
        # 6. 희소성 보너스 (부족한 아이템 포함 시)
        scarcity_bonus = self._calculate_scarcity_bonus(order, base_reward)
        
        # 총 보상 계산
        total_reward = (
            layer_weighted_reward +
            struggle_bonus +
            delivery_bonus +
            efficiency_bonus +
            streak_bonus +
            scarcity_bonus
        )
        
        return {
            'base_reward': base_reward,
            'layer_weighted_reward': layer_weighted_reward,
            'struggle_bonus': struggle_bonus,
            'delivery_bonus': delivery_bonus,
            'efficiency_bonus': efficiency_bonus,
            'streak_bonus': streak_bonus,
            'scarcity_bonus': scarcity_bonus,
            'total_reward': total_reward,
            'bonus_rate': ((total_reward - base_reward) / base_reward * 100) if base_reward > 0 else 0,
            'struggle_bonus_rate': struggle_bonus_rate,
            'time_efficiency': time_efficiency
        }
    
    def _calculate_struggle_bonus_rate(self, struggle_score: float) -> float:
        """스트러글 스코어에 따른 보너스 비율 계산 (PDF 수식 기반)"""
        if struggle_score < 20:
            return 0.1  # 10% 보너스
        elif struggle_score < 40:
            return 0.2  # 20% 보너스
        elif struggle_score < 60:
            return 0.35  # 35% 보너스
        elif struggle_score < 80:
            return 0.5  # 50% 보너스
        else:
            return 0.75  # 75% 보너스
    
    def _calculate_streak_bonus(self, base_reward: int) -> float:
        """연속 성공 보너스 계산"""
        if len(self.delivery_history) < 5:
            return 0
        
        # 최근 10개 주문의 성공률 계산 (가정: 높은 스트러글 스코어 = 성공)
        recent_orders = self.delivery_history[-10:]
        success_count = sum(1 for order in recent_orders if order.struggle_score > 50)
        success_rate = success_count / len(recent_orders)
        
        if success_rate >= 0.8:
            return base_reward * 0.2  # 20% 연속 성공 보너스
        elif success_rate >= 0.6:
            return base_reward * 0.1  # 10% 연속 성공 보너스
        else:
            return 0
    
    def _calculate_scarcity_bonus(self, order: DeliveryOrder, base_reward: int) -> float:
        """희소성 보너스 계산 (부족한 아이템 사용 시 추가 보상)"""
        scarcity_bonus = 0
        
        for item_name in order.items.keys():
            resource = self.resource_states.get(item_name)
            if resource and resource.is_deficit:
                # 부족한 아이템 하나당 5% 보너스
                scarcity_bonus += base_reward * 0.05
        
        return scarcity_bonus
    
    def generate_comprehensive_analysis(self, order: DeliveryOrder) -> Dict:
        """
        종합적인 주문 분석 (PDF: 다이나믹 밸런싱 수식도 기반)
        
        분석 항목:
        1. 경제적 효율성
        2. 생산 복잡도
        3. 리소스 압박도
        4. 밸런스 기여도
        """
        
        reward_analysis = self.calculate_advanced_reward_system(order)
        
        # 1. 경제적 효율성 분석
        coin_per_minute = order.total_value / max(order.total_production_time, 1) * 60
        efficiency_rating = self._rate_efficiency(coin_per_minute)
        
        # 2. 생산 복잡도 분석
        complexity_score = self._calculate_production_complexity(order)
        complexity_rating = self._rate_complexity(complexity_score)
        
        # 3. 리소스 압박도 분석
        resource_pressure = self._calculate_resource_pressure_impact(order)
        pressure_rating = self._rate_pressure(resource_pressure)
        
        # 4. 밸런스 기여도 분석
        balance_contribution = self._calculate_balance_contribution(order)
        balance_rating = self._rate_balance_contribution(balance_contribution)
        
        # 5. 전체 평가 점수 계산
        overall_score = (
            efficiency_rating * 0.3 +
            complexity_rating * 0.25 +
            pressure_rating * 0.25 +
            balance_rating * 0.2
        )
        
        return {
            'order_id': order.order_id,
            'delivery_type': order.delivery_type.value,
            'reward_analysis': reward_analysis,
            'economic_efficiency': {
                'coin_per_minute': coin_per_minute,
                'rating': efficiency_rating,
                'grade': self._get_grade(efficiency_rating)
            },
            'production_complexity': {
                'complexity_score': complexity_score,
                'rating': complexity_rating,
                'grade': self._get_grade(complexity_rating)
            },
            'resource_pressure': {
                'pressure_score': resource_pressure,
                'rating': pressure_rating,
                'grade': self._get_grade(pressure_rating)
            },
            'balance_contribution': {
                'contribution_score': balance_contribution,
                'rating': balance_rating,
                'grade': self._get_grade(balance_rating)
            },
            'overall_assessment': {
                'overall_score': overall_score,
                'grade': self._get_grade(overall_score),
                'recommendation': self._get_recommendation(overall_score)
            }
        }
    
    def _rate_efficiency(self, coin_per_minute: float) -> float:
        """효율성 점수 산정 (0-100)"""
        if coin_per_minute < 50:
            return 20
        elif coin_per_minute < 100:
            return 40
        elif coin_per_minute < 200:
            return 60
        elif coin_per_minute < 400:
            return 80
        else:
            return 100
    
    def _calculate_production_complexity(self, order: DeliveryOrder) -> float:
        """생산 복잡도 계산"""
        complexity = 0
        
        # 아이템 종류별 복잡도
        for item_name, quantity in order.items.items():
            resource = self.resource_states.get(item_name)
            if resource:
                # 레이어별 복잡도 가중치
                layer_weight = {'TOP': 3.0, 'MID': 2.0, 'CROPS': 1.0}[resource.layer.value]
                # 생산 시간 기반 복잡도
                time_weight = resource.production_time / 3600  # 시간 단위로 변환
                # 수량 기반 복잡도
                quantity_weight = quantity / 10
                
                complexity += layer_weight * time_weight * quantity_weight
        
        return complexity
    
    def _rate_complexity(self, complexity_score: float) -> float:
        """복잡도 점수 산정 (0-100)"""
        if complexity_score < 5:
            return 20
        elif complexity_score < 15:
            return 40
        elif complexity_score < 30:
            return 60
        elif complexity_score < 50:
            return 80
        else:
            return 100
    
    def _calculate_resource_pressure_impact(self, order: DeliveryOrder) -> float:
        """리소스 압박 영향도 계산"""
        pressure_impact = 0
        
        for item_name, quantity in order.items.items():
            resource = self.resource_states.get(item_name)
            if resource:
                # 재고 부족도에 따른 압박
                if resource.is_deficit:
                    pressure_impact += 3.0
                elif resource.stock_ratio < 0.5:
                    pressure_impact += 1.5
                
                # 생산 건물 압박도
                for building_name in resource.production_buildings:
                    building_pressure = self.production_pressures.get(building_name)
                    if building_pressure and building_pressure.pressure_level > 0.7:
                        pressure_impact += 2.0
        
        return pressure_impact
    
    def _rate_pressure(self, pressure_score: float) -> float:
        """압박도 점수 산정 (0-100, 높을수록 더 압박적)"""
        if pressure_score < 2:
            return 20
        elif pressure_score < 5:
            return 40
        elif pressure_score < 10:
            return 60
        elif pressure_score < 15:
            return 80
        else:
            return 100
    
    def _calculate_balance_contribution(self, order: DeliveryOrder) -> float:
        """밸런스 기여도 계산"""
        contribution = 0
        
        # 스트러글 스코어가 적정 범위(40-70)에 있으면 좋은 밸런스
        target_struggle = 55  # 이상적인 스트러글 스코어
        struggle_deviation = abs(order.struggle_score - target_struggle)
        
        if struggle_deviation < 10:
            contribution += 3.0  # 이상적인 범위
        elif struggle_deviation < 20:
            contribution += 2.0  # 양호한 범위
        else:
            contribution += 1.0  # 개선이 필요한 범위
        
        # 레이어 다양성 기여도
        layer_distribution = order.generation_metadata.get('layer_distribution', {})
        layer_diversity = len([count for count in layer_distribution.values() if count > 0])
        contribution += layer_diversity * 0.5
        
        return contribution
    
    def _rate_balance_contribution(self, contribution_score: float) -> float:
        """밸런스 기여도 점수 산정 (0-100)"""
        if contribution_score < 2:
            return 20
        elif contribution_score < 3.5:
            return 40
        elif contribution_score < 5:
            return 60
        elif contribution_score < 6.5:
            return 80
        else:
            return 100
    
    def _get_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
    
    def _get_recommendation(self, overall_score: float) -> str:
        """전체 점수에 따른 권장사항"""
        if overall_score >= 85:
            return "매우 우수한 밸런스! 현재 설정을 유지하세요."
        elif overall_score >= 70:
            return "좋은 밸런스입니다. 약간의 조정으로 더 개선할 수 있습니다."
        elif overall_score >= 55:
            return "보통 수준의 밸런스입니다. 일부 영역에서 개선이 필요합니다."
        elif overall_score >= 40:
            return "밸런스 개선이 필요합니다. 스트러글 스코어나 아이템 구성을 조정해보세요."
        else:
            return "심각한 밸런스 문제가 있습니다. 전면적인 조정이 필요합니다."
    
    def _generate_craft_time_analysis(self, items: Dict[str, int]) -> Dict:
        """제작 시간 분석 생성 (UI/UX 표시용)"""
        analysis = {
            'total_production_time': 0,
            'avg_production_time': 0,
            'complexity_distribution': {'simple': 0, 'moderate': 0, 'complex': 0},
            'bottleneck_items': [],
            'time_efficiency_score': 0
        }
        
        total_time = 0
        complex_items = []
        
        for item_name, quantity in items.items():
            item_data = self.hayday_items.get(item_name, {})
            production_time = item_data.get('production_time', 300)
            item_total_time = production_time * quantity
            total_time += item_total_time
            
            # 복잡도 분류
            if production_time < 600:  # 10분 미만
                analysis['complexity_distribution']['simple'] += 1
            elif production_time < 3600:  # 1시간 미만
                analysis['complexity_distribution']['moderate'] += 1
            else:  # 1시간 이상
                analysis['complexity_distribution']['complex'] += 1
                complex_items.append({
                    'item': item_name,
                    'time': production_time,
                    'quantity': quantity,
                    'total_time': item_total_time
                })
        
        analysis['total_production_time'] = total_time
        analysis['avg_production_time'] = total_time / len(items) if items else 0
        analysis['bottleneck_items'] = sorted(complex_items, key=lambda x: x['total_time'], reverse=True)[:3]
        
        # 시간 효율성 점수 (0-100)
        if total_time < 3600:  # 1시간 미만
            analysis['time_efficiency_score'] = 90
        elif total_time < 7200:  # 2시간 미만
            analysis['time_efficiency_score'] = 70
        elif total_time < 14400:  # 4시간 미만
            analysis['time_efficiency_score'] = 50
        else:
            analysis['time_efficiency_score'] = 30
        
        return analysis
    
    def _calculate_balance_impact(self, items: Dict[str, int], struggle_score: float) -> Dict:
        """밸런스 영향도 계산 (UI/UX 표시용)"""
        impact = {
            'resource_impact': 'neutral',  # positive, neutral, negative
            'struggle_impact': 'neutral',   # increases, maintains, decreases
            'market_impact': 'balanced',    # oversupply, balanced, shortage
            'recommendations': []
        }
        
        # 리소스 영향 분석
        deficit_items = 0
        abundant_items = 0
        
        for item_name, quantity in items.items():
            resource = self.resource_states.get(item_name)
            if resource:
                if resource.is_deficit:
                    deficit_items += 1
                elif resource.stock_ratio > 0.8:
                    abundant_items += 1
        
        if deficit_items > abundant_items:
            impact['resource_impact'] = 'negative'
            impact['recommendations'].append('"부족한 자원이 많습니다. 생산 효율성을 높이는 것이 좋겠습니다."')
        elif abundant_items > deficit_items:
            impact['resource_impact'] = 'positive'
            impact['recommendations'].append('"풍부한 자원을 활용한 좋은 밸런스입니다."')
        else:
            impact['resource_impact'] = 'neutral'
        
        # 스트러글 영향 분석
        if struggle_score > 70:
            impact['struggle_impact'] = 'increases'
            impact['recommendations'].append('"높은 난이도로 인해 스트레스가 증가할 수 있습니다."')
        elif struggle_score < 30:
            impact['struggle_impact'] = 'decreases'
            impact['recommendations'].append('"난이도가 낮아 더 도전적인 주문을 시도해볼 수 있습니다."')
        else:
            impact['struggle_impact'] = 'maintains'
        
        # 시장 영향 분석
        total_value = sum(self.hayday_items.get(item, {}).get('sell_price', 100) * qty for item, qty in items.items())
        if total_value > 2000:
            impact['market_impact'] = 'shortage'
            impact['recommendations'].append('"고가치 아이템들로 인한 시장 부족 예상."')
        elif total_value < 500:
            impact['market_impact'] = 'oversupply'
        else:
            impact['market_impact'] = 'balanced'
        
        return impact
    
    def _calculate_production_complexity_metadata(self, items: Dict[str, int]) -> Dict:
        """생산 복잡도 메타데이터 (UI/UX 표시용)"""
        metadata = {
            'building_load': {},
            'resource_chains': [],
            'bottleneck_analysis': {},
            'automation_score': 0
        }
        
        # 건물별 부하 분석
        building_loads = defaultdict(int)
        
        for item_name, quantity in items.items():
            resource = self.resource_states.get(item_name)
            if resource:
                for building in resource.production_buildings:
                    building_loads[building] += quantity
        
        metadata['building_load'] = dict(building_loads)
        
        # 자동화 점수 계산 (낮을수록 자동화 가능)
        total_items = len(items)
        complex_items = sum(1 for item in items.keys() 
                          if self.resource_states.get(item, ResourceState('', ItemLayer.TOP, 0, 0, 0, [], False, False)).layer == ItemLayer.TOP)
        
        automation_score = max(0, 100 - (complex_items / total_items * 100))
        metadata['automation_score'] = automation_score
        
        return metadata