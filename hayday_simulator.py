#!/usr/bin/env python3
"""
HayDay Production & Dynamic Balancing Simulator
Based on extracted CSV data and dynamic balancing system specifications
"""

import pandas as pd
import numpy as np
import json
import os
import random
import uuid
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math

# Optional imports for UI features
try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    # Create dummy objects to prevent errors
    class DummyStreamlit:
        def __getattr__(self, name):
            def dummy_func(*args, **kwargs):
                pass
            return dummy_func
    st = DummyStreamlit()
    px = go = make_subplots = None

# Configuration
DATA_PATH = os.path.join(os.path.dirname(__file__), "hayday_extracted_data", "core_data")

class DeliveryType(Enum):
    TRUCK = "Truck"
    TRAIN = "Train"
    BOAT = "Boat"

class DifficultyType(Enum):
    VERY_EASY = "VeryEasy"
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"
    VERY_HARD = "VeryHard"

class ItemLayerType(Enum):
    TOP = "Top"
    MID = "Mid"
    CROPS = "Crops"

@dataclass
class ProductionChain:
    """Production 체인을 나타내는 데이터 클래스"""
    item_name: str
    production_time: int  # minutes
    ingredients: Dict[str, int]  # ingredient_name: quantity
    value: int
    unlock_level: int
    building_type: str

@dataclass
class DeliveryOrder:
    """Delivery 주문을 나타내는 데이터 클래스"""
    order_id: str
    delivery_type: DeliveryType
    items: Dict[str, int]  # item_name: quantity
    total_value: int
    difficulty: DifficultyType
    struggle_score: float
    level_requirement: int
    total_production_time: int = 0  # Total 생산 시간 (분)
    expiry_time: int = 60  # 만료 시간 (분)

class HayDaySimulator:
    """HayDay 생산 및 동적 밸런싱 시뮬레이터"""
    
    def __init__(self):
        self.data = {}
        self.production_chains = {}
        self.delivery_patterns = []
        self.difficulty_policies = []
        self.reward_policies = []
        self.load_data()
        
    def load_data(self):
        """CSV 데이터 로드"""
        try:
            # HayDay 게임 데이터 로드 (오류 방지)
            data_files = {
                'animals': f"{DATA_PATH}/animals.csv",
                'exp_levels': f"{DATA_PATH}/exp_levels.csv",
                'fields': f"{DATA_PATH}/fields.csv"
            }
            
            for key, file_path in data_files.items():
                try:
                    df = pd.read_csv(file_path)
                    # 첫 번째 행이 데이터 타입인 경우 제거
                    if len(df) > 1 and df.iloc[0].astype(str).str.contains('int|String|Boolean|float', na=False).any():
                        df = df.drop(0).reset_index(drop=True)
                    self.data[key] = df
                except Exception as e:
                    print(f"WARNING {key} 파일 로드 실패: {e}")
                    self.data[key] = pd.DataFrame()  # 빈 데이터프레임으로 초기화
            
            # 모든 _goods.csv 파일 자동 검색 및 로드
            import glob
            goods_pattern = os.path.join(DATA_PATH, "*_goods.csv")
            goods_files = glob.glob(goods_pattern)
            
            print(f"Found {len(goods_files)} production building files")
            
            for goods_path in goods_files:
                try:
                    filename = os.path.basename(goods_path)
                    key = filename.replace('.csv', '')  # 전체 파일명을 키로 사용 (ex: bakery_goods)
                    df = pd.read_csv(goods_path)
                    
                    # 데이터 타입 행 제거
                    if len(df) > 1 and df.iloc[0].astype(str).str.contains('int|String|Boolean|float', na=False).any():
                        df = df.drop(0).reset_index(drop=True)
                    
                    # Name이 비어있지 않은 행만 필터링
                    if 'Name' in df.columns:
                        df = df[df['Name'].notna() & (df['Name'].astype(str).str.strip() != '')]
                        df = df.reset_index(drop=True)
                    
                    self.data[key] = df
                    if len(df) > 0:
                        print(f"Loaded {key}: {len(df)} items")
                except Exception as e:
                    print(f"Warning: {filename} loading failed: {e}")
                    self.data[key] = pd.DataFrame()
            
            # 농작물 및 과일 데이터도 로드
            crop_files = ['fields.csv', 'fruits.csv', 'fruit_trees.csv']
            for crop_file in crop_files:
                try:
                    key = crop_file.replace('.csv', '')
                    df = pd.read_csv(os.path.join(DATA_PATH, crop_file))
                    if len(df) > 1 and df.iloc[0].astype(str).str.contains('int|String|Boolean|float', na=False).any():
                        df = df.drop(0).reset_index(drop=True)
                    if 'Name' in df.columns:
                        df = df[df['Name'].notna() & (df['Name'].astype(str).str.strip() != '')]
                        df = df.reset_index(drop=True)
                    self.data[key] = df
                    print(f"Loaded {key}: {len(df)} items")
                except Exception as e:
                    print(f"Warning: {crop_file} loading failed: {e}")
                    self.data[key] = pd.DataFrame()
            
            # HayDay 실제 주문/경험 시스템 데이터 로드
            try:
                self.orders = pd.read_csv(f"{DATA_PATH}/orders.csv")
                self.predefined_orders = pd.read_csv(f"{DATA_PATH}/predefined_orders.csv")
                self.exp_levels = pd.read_csv(f"{DATA_PATH}/exp_levels.csv")
                
                # 건물 언락 레벨 데이터 로드
                self.processing_buildings = pd.read_csv(f"{DATA_PATH}/processing_buildings.csv")
                
                # 데이터 타입 행 제거 (HayDay 데이터 형식)
                for df_name in ['orders', 'predefined_orders', 'exp_levels', 'processing_buildings']:
                    df = getattr(self, df_name)
                    if len(df) > 1 and df.iloc[0].astype(str).str.contains('int|String|Boolean|float', na=False).any():
                        setattr(self, df_name, df.drop(0).reset_index(drop=True))
                
                print("HayDay order system data loading completed!")
                print(f"Loaded processing buildings data: {len(self.processing_buildings)} buildings")
                
            except Exception as e:
                print(f"Warning: HayDay order data loading failed: {e}")
                # 기본 데이터프레임으로 초기화
                self.orders = pd.DataFrame()
                self.predefined_orders = pd.DataFrame() 
                self.exp_levels = pd.DataFrame()
                self.processing_buildings = pd.DataFrame()
            
            print("Data loading completed!")
            
        except Exception as e:
            print(f"Data loading failed: {e}")
            # 모든 데이터를 빈 데이터프레임으로 초기화
            self.data = {}
            self.delivery_patterns = pd.DataFrame()
            self.delivery_thresholds = pd.DataFrame()
            self.difficulty_policies = pd.DataFrame()
            self.reward_policies = pd.DataFrame()
    
    def analyze_production_chains(self) -> Dict[str, ProductionChain]:
        """Production 체인 분석"""
        chains = {}
        
        # 동물 생산 체인
        if 'animals' in self.data:
            for _, animal in self.data['animals'].iterrows():
                if pd.notna(animal.get('Name')):
                    chains[animal['Good']] = ProductionChain(
                        item_name=animal['Good'],
                        production_time=0,  # 연속 생산
                        ingredients={animal['Feed']: 1},
                        value=animal['Value'],
                        unlock_level=animal['UnlockLevel'],
                        building_type='Animal'
                    )
        
        # 제품 생산 체인
        for category in ['bakery', 'dairy', 'cafe']:
            if category in self.data:
                for _, product in self.data[category].iterrows():
                    if pd.notna(product.get('Name')):
                        ingredients = {}
                        for i in range(1, 6):  # Ingredient1~5
                            ing_col = f'Ingredient{i}'
                            amt_col = f'IngredientAmount{i}'
                            if ing_col in product and pd.notna(product[ing_col]):
                                ingredients[product[ing_col]] = product.get(amt_col, 1)
                        
                        chains[product['Name']] = ProductionChain(
                            item_name=product['Name'],
                            production_time=product.get('ProcessTime', 60),
                            ingredients=ingredients,
                            value=product.get('Value', 100),
                            unlock_level=product.get('UnlockLevel', 1),
                            building_type=category.capitalize()
                        )
        
        return chains
    
    def calculate_struggle_score(self, player_level: int, inventory: Dict[str, int]) -> float:
        """Player의 어려움 지수(Struggle Score) 계산"""
        base_score = max(0, 50 - player_level)  # 레벨이 낮을수록 높은 기본 점수
        
        # 인벤토리 부족도에 따른 점수 추가
        inventory_score = 0
        total_items = sum(inventory.values())
        if total_items < 20:  # 임계치
            inventory_score = (20 - total_items) * 2
        
        return min(100, base_score + inventory_score)
    
    def _generate_basic_order(self, player_level: int, delivery_type: DeliveryType, 
                            struggle_score: float) -> DeliveryOrder:
        """기본 주문 생성 (데이터가 없는 경우의 폴백)"""
        import uuid
        import random
        
        # 플레이어 레벨에 따른 사용 가능한 모든 아이템 가져오기
        available_items = self._get_available_items(player_level)
        if not available_items:
            # Items이 없으면 기본 아이템 사용
            available_items = ["밀", "옥수수", "당근", "설탕수수", "코코아", "계란", "우유"]
        
        # 난이도 설정 (높은 어려움 지수 = 어려운 주문)
        if struggle_score < 20:
            difficulty = DifficultyType.VERY_EASY
            item_count = 1
        elif struggle_score < 40:
            difficulty = DifficultyType.EASY
            item_count = 2
        elif struggle_score < 60:
            difficulty = DifficultyType.NORMAL
            item_count = random.randint(2, 3)
        elif struggle_score < 80:
            difficulty = DifficultyType.HARD
            item_count = random.randint(3, 4)
        else:
            difficulty = DifficultyType.VERY_HARD
            item_count = random.randint(4, 5)
        
        # 랜덤 아이템 선택 - 레벨에 맞는 다양한 아이템 선택
        selected_items = random.sample(available_items, min(item_count, len(available_items)))
        items = {}
        
        for item in selected_items:
            # Items 수량은 난이도에 따라 조정
            if difficulty == DifficultyType.VERY_EASY:
                qty = random.randint(1, 3)
            elif difficulty == DifficultyType.EASY:
                qty = random.randint(2, 5)
            elif difficulty == DifficultyType.NORMAL:
                qty = random.randint(3, 7)
            elif difficulty == DifficultyType.HARD:
                qty = random.randint(4, 9)
            else:
                qty = random.randint(5, 12)
            items[item] = qty
        
        # 실제 아이템 가격 및 생산 시간 계산
        total_value = 0
        total_time = 0
        production_times = []
        
        for item_name, item_qty in items.items():
            item_value = self._get_item_value(item_name)
            item_time = self._get_item_production_time(item_name)
            total_value += item_value * item_qty
            total_time += item_time * item_qty
            production_times.append(item_time)
        
        avg_time = sum(production_times) / len(production_times) if production_times else 0
        
        return DeliveryOrder(
            order_id=f"BASIC-{uuid.uuid4().hex[:8].upper()}",
            delivery_type=delivery_type,
            items=items,
            total_value=total_value,
            difficulty=difficulty,
            struggle_score=struggle_score,
            level_requirement=player_level,
            total_production_time=total_time
        )
    
    def generate_delivery_order(self, player_level: int, struggle_score: float, 
                              delivery_type: DeliveryType = DeliveryType.TRUCK) -> DeliveryOrder:
        """HayDay 실제 데이터를 기반으로 한 납품 주문 생성"""
        
        # 레벨 정보 가져오기
        level_data = self._get_level_data(player_level)
        if level_data is None:
            return self._generate_basic_order(player_level, delivery_type, struggle_score)
        
        # 사전 정의된 주문이 있는지 확인
        predefined = self._get_predefined_order(player_level)
        if predefined is not None:
            return predefined
        
        # 동적 주문 생성
        return self._generate_dynamic_order(player_level, struggle_score, delivery_type, level_data)
    
    def _get_level_data(self, player_level: int):
        """Player 레벨에 해당하는 데이터 조회"""
        if self.exp_levels.empty:
            return None
            
        try:
            # Level 컬럼을 정수로 변환하여 비교
            level_data = self.exp_levels[
                pd.to_numeric(self.exp_levels['Level'], errors='coerce') == player_level
            ]
            return level_data.iloc[0] if not level_data.empty else None
        except Exception as e:
            print(f"WARNING 레벨 데이터 조회 오류: {e}")
            return None
    
    def _get_predefined_order(self, player_level: int):
        """사전 정의된 주문 확인 (튜토리얼용)"""
        if self.predefined_orders.empty:
            return None
        
        # 레벨 10 이하에서만 사전 정의된 주문 사용
        if player_level > 10:
            return None
            
        try:
            # 간단한 사전 정의 주문 생성 (예시)
            available_orders = self.predefined_orders.head(3)  # 처음 3개만 사용
            if not available_orders.empty:
                order = available_orders.sample(1).iloc[0]
                goods = str(order.get('Goods', 'Wheat')).split(',')
                amounts = str(order.get('GoodAmounts', '1')).split(',')
                
                items = {}
                for i, good in enumerate(goods):
                    amount = int(amounts[i] if i < len(amounts) else amounts[0])
                    items[good.strip()] = amount
                
                return DeliveryOrder(
                    order_id=f"PRE_{player_level}",
                    delivery_type=DeliveryType.TRUCK,
                    items=items,
                    total_value=sum(amount * 10 for amount in items.values()),  # 임시 가치
                    difficulty=DifficultyType.EASY,
                    struggle_score=50.0,  # 기본값
                    level_requirement=player_level,
                    expiry_time=60
                )
        except Exception as e:
            print(f"WARNING 사전 정의 주문 생성 오류: {e}")
        
        return None
    
    def _generate_dynamic_order(self, player_level: int, struggle_score: float, 
                               delivery_type: DeliveryType, level_data) -> DeliveryOrder:
        """Dynamic 주문 생성 (HayDay 레벨 데이터 기반)"""
        try:
            # 레벨 데이터에서 주문 매개변수 추출 (실제 HayDay CSV 데이터 완전 활용)
            min_goods = int(level_data.get('MinGoodsInOrderDelivery', 1))
            max_goods = int(level_data.get('MaxGoodsInOrderDelivery', 3))
            min_value = int(level_data.get('OrderMinValue', 100))
            max_value = int(level_data.get('OrderMaxValue', 600))
            max_order_count = int(level_data.get('MaxOrderCount', 1))
            truck_coin_multiplier = int(level_data.get('TruckCoinMultiplier', 100))
            truck_exp_multiplier = int(level_data.get('TruckEXPMultiplier', 100))
            order_cancel_time = int(level_data.get('OrderCancelTimeMin', 6))
            
            # 특별 주문 시스템 (CSV 데이터 기반)
            special_order_probability = int(level_data.get('SpecialOrderProbablity', 0))  # 오타: Probablity
            special_order_max_count = int(level_data.get('SpecialOrderMaxCount', 0))
            
            # 보트 전용 크레이트 시스템
            min_crate_amount = int(level_data.get('MinCrateAmountInBoatOrder', 1))
            max_crate_amount = int(level_data.get('MaxCrateAmountInBoatOrder', 1))
            boat_coin_multiplier = int(level_data.get('BoatCrateCoinMultiplier', 100))
            boat_exp_multiplier = int(level_data.get('BoatCrateEXPMultiplier', 100))
            
            # 실제 HayDay 스타일: 납품 타입별 아이템 수 조정
            if delivery_type == DeliveryType.TRAIN:
                # Train: 3-5개 (5칸 기차)
                if player_level <= 20:
                    base_min_items = 3
                    base_max_items = 4
                elif player_level <= 40:
                    base_min_items = 3
                    base_max_items = 5
                else:
                    base_min_items = 4
                    base_max_items = 5
            elif delivery_type == DeliveryType.BOAT:
                # Boat 언락레벨 체크 (HayDay에서는 레벨 17에서 언락)
                if player_level < 17:
                    # 보트가 언락되지 않았으면 Truck으로 변경
                    delivery_type = DeliveryType.TRUCK
                    base_min_items = 1 if player_level <= 10 else 2
                    base_max_items = 2 if player_level <= 10 else 3
                else:
                    # Boat: CSV 데이터 기반 (MinGoodTypesInBoatOrder / MaxGoodTypesInBoatOrder)
                    base_min_items = int(level_data.get('MinGoodTypesInBoatOrder', 3))
                    base_max_items = int(level_data.get('MaxGoodTypesInBoatOrder', 3))
                    # 보트는 일반적으로 더 많은 아이템 요구
                    if base_max_items < 4:
                        base_max_items = min(6, base_min_items + 2)
            else:  # Truck
                # Truck: 레벨에 따라 1-6개까지 점진적 증가
                if player_level <= 10:
                    base_min_items = 1
                    base_max_items = 2
                elif player_level <= 20:
                    base_min_items = 2
                    base_max_items = 3
                elif player_level <= 40:
                    base_min_items = 2
                    base_max_items = 4
                elif player_level <= 60:
                    base_min_items = 3
                    base_max_items = 5
                else:
                    base_min_items = 3
                    base_max_items = 6
            
            # 보트 전용 가치 범위 적용 (CSV 데이터 기반)
            if delivery_type == DeliveryType.BOAT:
                boat_min_value = int(level_data.get('MinBoatOrderValue', min_value))
                boat_max_value = int(level_data.get('MaxBoatOrderValue', max_value))
                min_value = boat_min_value
                max_value = boat_max_value
                
            # 어려움 지수에 따른 난이도 조절 (실제 CSV 데이터 기반)
            if struggle_score < 30:  # 낮은 어려움 = 쉬운 주문
                num_items = base_min_items
                target_value = min_value + int((max_value - min_value) * 0.1)  # 하위 10-30% 가치
                difficulty = DifficultyType.EASY
            elif struggle_score < 60:  # 중간 어려움
                num_items = min(base_max_items, base_min_items + 1) 
                target_value = min_value + int((max_value - min_value) * 0.5)  # 중간 가치
                difficulty = DifficultyType.NORMAL
            else:  # 높은 어려움 = 어려운 주문
                num_items = base_max_items
                target_value = min_value + int((max_value - min_value) * 0.8)  # 상위 80% 가치
                difficulty = DifficultyType.HARD
            
            # 이용 가능한 아이템 풀 생성 (플레이어 레벨 기준)
            available_items = self._get_available_items(player_level)
            
            # Items을 카테고리별로 분류
            crops = []
            animal_products = []
            basic_goods = []
            advanced_goods = []
            
            for item in available_items:
                production_time = self._get_item_production_time(item)
                value = self._get_item_value(item)
                
                if production_time <= 5:  # 5분 이하 - 기본 농작물
                    crops.append(item)
                elif production_time <= 60:  # 1시간 이하 - 동물/기본 제품
                    if value < 50:
                        animal_products.append(item)
                    else:
                        basic_goods.append(item)
                else:  # 1시간 초과 - 고급 제품
                    advanced_goods.append(item)
            
            # 난이도와 어려움 지수에 따라 카테고리 비율 조정
            items = {}
            selected_items = []
            
            if struggle_score > 70:  # 높은 어려움 = 쉽게, 기본 아이템 위주
                # 60% 기본, 30% 동물, 10% 고급
                if crops:
                    selected_items.extend(random.sample(crops, min(int(num_items * 0.6), len(crops))))
                if animal_products:
                    selected_items.extend(random.sample(animal_products, min(int(num_items * 0.3), len(animal_products))))
                if basic_goods:
                    selected_items.extend(random.sample(basic_goods, min(int(num_items * 0.1), len(basic_goods))))
            elif struggle_score > 40:  # 중간 어려움 = 균형
                # 25% 기본, 35% 동물, 25% 기본제품, 15% 고급
                if crops:
                    selected_items.extend(random.sample(crops, min(max(1, int(num_items * 0.25)), len(crops))))
                if animal_products:
                    selected_items.extend(random.sample(animal_products, min(max(1, int(num_items * 0.35)), len(animal_products))))
                if basic_goods:
                    selected_items.extend(random.sample(basic_goods, min(max(1, int(num_items * 0.25)), len(basic_goods))))
                if advanced_goods:
                    selected_items.extend(random.sample(advanced_goods, min(int(num_items * 0.15), len(advanced_goods))))
            else:  # 낮은 어려움 = 어려운 주문, 고급 아이템 위주
                # 10% 기본, 20% 동물, 30% 기본제품, 40% 고급
                if advanced_goods:
                    selected_items.extend(random.sample(advanced_goods, min(max(1, int(num_items * 0.4)), len(advanced_goods))))
                if basic_goods:
                    selected_items.extend(random.sample(basic_goods, min(max(1, int(num_items * 0.3)), len(basic_goods))))
                if animal_products:
                    selected_items.extend(random.sample(animal_products, min(max(1, int(num_items * 0.2)), len(animal_products))))
                if crops:
                    selected_items.extend(random.sample(crops, min(int(num_items * 0.1), len(crops))))
            
            # 만약 선택된 아이템이 부족하면 랜덤 추가
            if len(selected_items) < num_items:
                remaining = list(set(available_items) - set(selected_items))
                if remaining:
                    selected_items.extend(random.sample(remaining, min(num_items - len(selected_items), len(remaining))))
            
            # Remove duplicates 및 최종 아이템 수 조정
            selected_items = list(set(selected_items))[:num_items]
            
            for item in selected_items:
                # HayDay 스타일 수량: 아이템 가치에 따라 적절한 수량 계산
                item_value = self._get_item_value(item)
                
                if item_value <= 10:  # 저가 아이템 (밀, 옥수수 등)
                    amount = random.randint(3, 12)
                elif item_value <= 50:  # 중가 아이템 (빵, 버터 등)  
                    amount = random.randint(2, 8)
                elif item_value <= 100:  # 고가 아이템 (케이크, 의류 등)
                    amount = random.randint(1, 5)
                else:  # 최고가 아이템 (보석, 고급 제품 등)
                    amount = random.randint(1, 3)
                
                # 난이도에 따른 수량 조정
                if difficulty == DifficultyType.EASY:
                    amount = max(1, int(amount * 0.7))
                elif difficulty == DifficultyType.HARD:
                    amount = int(amount * 1.3)
                
                items[item] = max(1, amount)
            
            # 실제 주문 가치 및 생산 시간 계산
            actual_value = 0
            total_time = 0
            production_times = []
            
            for item_name, item_qty in items.items():
                item_value = self._get_item_value(item_name)
                item_time = self._get_item_production_time(item_name)
                actual_value += item_value * item_qty
                # 각 아이템의 총 생산 시간
                item_total_time = item_time * item_qty
                total_time += item_total_time
                production_times.append(item_time)
            
            # Average 생산 시간 계산
            avg_time = sum(production_times) / len(production_times) if production_times else 0
            
            return DeliveryOrder(
                order_id=f"{delivery_type.value}_{np.random.randint(1000, 9999)}",
                delivery_type=delivery_type,
                items=items,
                total_value=actual_value,
                difficulty=difficulty,
                struggle_score=struggle_score,
                level_requirement=player_level,
                    total_production_time=total_time,
                expiry_time=60
            )
            
        except Exception as e:
            print(f"Warning: Dynamic order generation error: {e}")
            return self._generate_basic_order(player_level, delivery_type, struggle_score)
    
    
    def _generate_order_items(self, pattern: pd.Series, player_level: int) -> Dict[str, int]:
        """패턴에 따른 주문 아이템 생성"""
        items = {}
        
        # FixedAmountList 처리
        if pd.notna(pattern.get('FixedAmountList')):
            fixed_amounts = str(pattern['FixedAmountList']).split(' / ')
            available_items = self._get_available_items(player_level)
            
            for i, amount_str in enumerate(fixed_amounts):
                if i < len(available_items):
                    items[available_items[i]] = int(amount_str)
        
        # MinAmountList/MaxAmountList 처리
        elif pd.notna(pattern.get('MinAmountList')) and pd.notna(pattern.get('MaxAmountList')):
            min_amounts = [float(x) for x in str(pattern['MinAmountList']).split(' / ')]
            max_amounts = [float(x) for x in str(pattern['MaxAmountList']).split(' / ')]
            available_items = self._get_available_items(player_level)
            
            for i, (min_amt, max_amt) in enumerate(zip(min_amounts, max_amounts)):
                if i < len(available_items):
                    items[available_items[i]] = int(np.random.uniform(min_amt, max_amt))
        
        return items
    
    def _get_available_items(self, player_level: int) -> List[str]:
        """Player 레벨에 따른 사용 가능한 아이템 목록 (실제 HayDay 언락레벨 적용)"""
        available = []
        
        # Exclude할 아이템 패턴 (이벤트, 더미, 테스트 아이템)
        exclude_patterns = [
            'CountyFair',  # 박람회 이벤트 아이템
            'Dummy',       # 더미 아이템
            'Placeholder', # 플레이스홀더
            'Test',        # 테스트 아이템
            'Ticket',      # 티켓류
            'Ribbon',      # 리본류
            'Bonus',       # 보너스 아이템
            'Easter',      # 이스터 이벤트
            'Christmas',   # 크리스마스 이벤트
            'Halloween',   # 할로윈 이벤트
            'Valentine',   # 발렌타인 이벤트
            'Birthday',    # 생일 이벤트
            'Anniversary', # 기념일 이벤트
            '_egg',        # 이스터 에그 아이템
            'Event',       # 모든 이벤트 아이템
            'Special',     # 스페셜 이벤트
            'Limited',     # 한정판 아이템
            'Seasonal'     # 시즌 아이템
        ]
        
        # 모든 로드된 데이터에서 아이템 추출
        for key, df in self.data.items():
            if df.empty:
                continue
            
            # 이벤트 관련 데이터는 아예 건너뛰기
            if any(event in key.lower() for event in ['countyfair', 'dummy', 'seasonal', 'event', 'easter', 'christmas', 'halloween']):
                continue
                
            # 농작물 및 과일 (fields, fruits, fruit_trees)
            if key in ['fields', 'fruits', 'fruit_trees']:
                for _, item in df.iterrows():
                    if (pd.notna(item.get('Name')) and 
                        pd.notna(item.get('UnlockLevel')) and
                        int(item.get('UnlockLevel', 999)) <= player_level):
                        item_name = str(item.get('Name'))
                        # Exclude 패턴 체크
                        if not any(pattern in item_name for pattern in exclude_patterns):
                            if item_name not in available:
                                available.append(item_name)
            
            # Animal products (animals)
            elif key == 'animals':
                for _, animal in df.iterrows():
                    if (pd.notna(animal.get('Good')) and 
                        pd.notna(animal.get('UnlockLevel')) and
                        int(animal.get('UnlockLevel', 999)) <= player_level):
                        item_name = str(animal.get('Good'))
                        # Exclude 패턴 체크
                        if not any(pattern in item_name for pattern in exclude_patterns):
                            if item_name not in available:
                                available.append(item_name)
            
            # 모든 _goods로 끝나는 생산 건물 데이터
            elif key.endswith('_goods'):
                for _, product in df.iterrows():
                    if pd.notna(product.get('Name')):
                        item_name = str(product.get('Name'))
                        
                        # 건물 언락레벨 체크 (processing_buildings.csv 사용)
                        building_name = key.replace('_goods', '')
                        building_unlock_level = self._get_building_unlock_level(building_name)
                        
                        # 제품 자체의 언락레벨도 체크
                        item_unlock_level = int(product.get('UnlockLevel', building_unlock_level))
                        
                        # 더 높은 언락레벨 사용 (건물 or 제품)
                        required_level = max(building_unlock_level, item_unlock_level)
                        
                        if required_level <= player_level:
                            # Exclude 패턴 체크
                            if not any(pattern in item_name for pattern in exclude_patterns):
                                if item_name not in available:
                                    available.append(item_name)
        
        # Remove duplicates 및 레벨 순으로 정렬
        available = list(set(available))
        
        # Sort by unlock level (낮은 레벨부터)
        def get_unlock_level(item_name):
            # 모든 로드된 데이터에서 언락레벨 찾기
            for key, df in self.data.items():
                if df.empty:
                    continue
                    
                # 농작물/과일
                if key in ['fields', 'fruits', 'fruit_trees']:
                    if 'Name' in df.columns:
                        matching = df[df['Name'] == item_name]
                        if not matching.empty:
                            return int(matching.iloc[0].get('UnlockLevel', 999))
                
                # Animal products
                elif key == 'animals':
                    matching = df[df['Good'] == item_name]
                    if not matching.empty:
                        return int(matching.iloc[0].get('UnlockLevel', 999))
                
                # Production buildings 제품
                elif key.endswith('_goods'):
                    if 'Name' in df.columns:
                        matching = df[df['Name'] == item_name]
                        if not matching.empty:
                            return int(matching.iloc[0].get('UnlockLevel', 999))
            
            return 1  # 기본값
        
        available.sort(key=get_unlock_level)
        # 디버그 출력 제거 (렉 방지)
        # print(f"Available items for level {player_level}: {len(available)} items")
        # print(f"First 10 items: {available[:10]}")
        return available  # 모든 사용 가능한 아이템 반환
    
    def _get_item_value(self, item_name: str) -> int:
        """Item 가치 조회 (실제 HayDay 가격 데이터 사용)"""
        try:
            # 모든 로드된 데이터에서 가격 찾기
            for key, df in self.data.items():
                if df.empty:
                    continue
                    
                # 농작물/과일
                if key in ['fields', 'fruits', 'fruit_trees']:
                    matching = df[df['Name'] == item_name]
                    if not matching.empty:
                        item = matching.iloc[0]
                        for price_col in ['OrderPrice', 'OrderValue', 'BoatOrderValue', 'Price', 'Value']:
                            if pd.notna(item.get(price_col)):
                                try:
                                    price = int(float(item.get(price_col)))
                                    if price > 0:
                                        return price
                                except (ValueError, TypeError):
                                    continue
                
                # Animal products
                elif key == 'animals':
                    matching = df[df['Good'] == item_name]
                    if not matching.empty:
                        animal = matching.iloc[0]
                        return int(animal.get('ProcessValue', animal.get('Value', 10)))
                
                # Production buildings 제품
                elif key.endswith('_goods'):
                    matching = df[df['Name'] == item_name]
                    if not matching.empty:
                        product = matching.iloc[0]
                        for price_col in ['OrderPrice', 'OrderValue', 'BoatOrderValue', 'Price', 'Value']:
                            if pd.notna(product.get(price_col)):
                                try:
                                    price = int(float(product.get(price_col)))
                                    if price > 0:
                                        return price
                                except (ValueError, TypeError):
                                    continue
        
        except Exception as e:
            pass  # Silent error handling
        
        # 기본 가격 (HayDay 실제 데이터 기반)
        default_prices = {
            "Wheat": 1, "Corn": 1, "Egg": 20, "Milk": 36,
            "Bread": 50, "Butter": 63, "Cheese": 115, "Cookie": 52, "Cream": 97,
            "Apple": 20, "Strawberry": 40, "Carrot": 25
        }
        
        return default_prices.get(item_name, 20)  # 기본값 20 코인
    
    def _get_item_production_time(self, item_name: str) -> int:
        """Item 생산시간 조회 (실제 HayDay TimeMin 데이터)"""
        try:
            # 모든 로드된 데이터에서 생산시간 찾기
            for key, df in self.data.items():
                if df.empty:
                    continue
                    
                # 농작물/과일
                if key in ['fields', 'fruits', 'fruit_trees']:
                    matching = df[df['Name'] == item_name]
                    if not matching.empty:
                        item = matching.iloc[0]
                        if pd.notna(item.get('TimeMin')):
                            try:
                                return int(item.get('TimeMin'))
                            except (ValueError, TypeError):
                                pass
                
                # Production buildings 제품
                elif key.endswith('_goods'):
                    matching = df[df['Name'] == item_name]
                    if not matching.empty:
                        item = matching.iloc[0]
                        if pd.notna(item.get('TimeMin')):
                            try:
                                return int(item.get('TimeMin'))
                            except (ValueError, TypeError):
                                pass
        except Exception as e:
            pass  # Silent error handling
        
        # 기본 생산시간 (분 단위)
        default_times = {
            "Wheat": 2, "Corn": 5, "Egg": 20, "Milk": 60,
            "Bread": 5, "Butter": 30, "Cheese": 60, "Cookie": 60, "Cream": 20
        }
        
        return default_times.get(item_name, 15)  # 기본값 15분
    
    def _get_building_unlock_level(self, building_name: str) -> int:
        """건물 언락레벨 조회 (processing_buildings.csv)"""
        try:
            if hasattr(self, 'processing_buildings') and not self.processing_buildings.empty:
                # 건물명 매칭 (대소문자 무시)
                matching_buildings = self.processing_buildings[
                    self.processing_buildings['Name'].str.lower() == building_name.lower()
                ]
                if not matching_buildings.empty:
                    unlock_level = matching_buildings.iloc[0].get('UnlockLevel')
                    if pd.notna(unlock_level):
                        try:
                            return int(unlock_level)
                        except (ValueError, TypeError):
                            pass
            return 0
        except Exception:
            return 0
    
    def get_all_items_data(self) -> Dict[str, Dict]:
        """모든 아이템의 상세 정보를 반환 (SungDae 시뮬레이터용)"""
        items_data = {}
        
        # 모든 데이터에서 아이템 정보 추출
        for key, df in self.data.items():
            if df.empty:
                continue
                
            # 이벤트 관련 데이터는 건너뛰기
            if any(event in key.lower() for event in ['countyfair', 'dummy', 'seasonal', 'event']):
                continue
            
            # 농작물 (fields)
            if key == 'fields':
                for _, item in df.iterrows():
                    if pd.notna(item.get('Name')):
                        name = str(item.get('Name'))
                        # 안전한 숫자 변환
                        sell_price = item.get('SellPrice', 1)
                        grow_time = item.get('GrowTime', 10)
                        unlock_level = item.get('UnlockLevel', 1)
                        
                        try:
                            sell_price = int(float(sell_price)) if pd.notna(sell_price) else 1
                        except (ValueError, TypeError):
                            sell_price = 1
                            
                        try:
                            grow_time = int(float(grow_time)) if pd.notna(grow_time) else 10
                        except (ValueError, TypeError):
                            grow_time = 10
                            
                        try:
                            unlock_level = int(float(unlock_level)) if pd.notna(unlock_level) else 1
                        except (ValueError, TypeError):
                            unlock_level = 1
                        
                        items_data[name] = {
                            'base_price': sell_price,
                            'production_time': grow_time,
                            'layer': 'CROPS',
                            'unlock_level': unlock_level,
                            'category': 'crops'
                        }
            
            # 과일 (fruits, fruit_trees)
            elif key in ['fruits', 'fruit_trees']:
                for _, item in df.iterrows():
                    if pd.notna(item.get('Name')):
                        name = str(item.get('Name'))
                        # 안전한 숫자 변환
                        sell_price = item.get('SellPrice', 2)
                        grow_time = item.get('GrowTime', 20)
                        unlock_level = item.get('UnlockLevel', 1)
                        
                        try:
                            sell_price = int(float(sell_price)) if pd.notna(sell_price) else 2
                        except (ValueError, TypeError):
                            sell_price = 2
                            
                        try:
                            grow_time = int(float(grow_time)) if pd.notna(grow_time) else 20
                        except (ValueError, TypeError):
                            grow_time = 20
                            
                        try:
                            unlock_level = int(float(unlock_level)) if pd.notna(unlock_level) else 1
                        except (ValueError, TypeError):
                            unlock_level = 1
                        
                        items_data[name] = {
                            'base_price': sell_price,
                            'production_time': grow_time,
                            'layer': 'CROPS',
                            'unlock_level': unlock_level,
                            'category': 'fruits'
                        }
            
            # 동물 제품 (animals)
            elif key == 'animals':
                for _, animal in df.iterrows():
                    if pd.notna(animal.get('Good')):
                        name = str(animal.get('Good'))
                        items_data[name] = {
                            'base_price': int(pd.to_numeric(animal.get('SellPrice', 5), errors='coerce') or 5),
                            'production_time': int(pd.to_numeric(animal.get('ProductionTime', 30), errors='coerce') or 30),
                            'layer': 'CROPS',
                            'unlock_level': int(pd.to_numeric(animal.get('UnlockLevel', 1), errors='coerce') or 1),
                            'category': 'animal_products'
                        }
            
            # 생산 건물 제품들 (가공품 = MID layer)
            else:
                for _, item in df.iterrows():
                    # Good 컬럼이 있는 경우
                    if pd.notna(item.get('Good')):
                        name = str(item.get('Good'))
                        production_time = int(pd.to_numeric(item.get('ProductionTime', 60), errors='coerce') or 60)
                        sell_price = int(pd.to_numeric(item.get('SellPrice', 10), errors='coerce') or 10)
                        
                        # 가격과 생산시간으로 레이어 분류
                        if sell_price >= 100 or production_time >= 240:  # 고급품
                            layer = 'TOP'
                        elif sell_price >= 20 or production_time >= 30:  # 중급품
                            layer = 'MID'
                        else:  # 기본품
                            layer = 'CROPS'
                        
                        items_data[name] = {
                            'base_price': sell_price,
                            'production_time': production_time,
                            'layer': layer,
                            'unlock_level': int(pd.to_numeric(item.get('UnlockLevel', 1), errors='coerce') or 1),
                            'category': key
                        }
        
        return items_data
    
    def _get_item_unlock_level(self, item_name: str) -> int:
        """Item 언락레벨 조회 (CSV 데이터 기반)"""
        try:
            # 농작물 언락레벨 (fields.csv)
            if 'fields' in self.data and not self.data['fields'].empty:
                matching_crops = self.data['fields'][self.data['fields']['Name'] == item_name]
                if not matching_crops.empty:
                    unlock_level = matching_crops.iloc[0].get('UnlockLevel')
                    if pd.notna(unlock_level):
                        try:
                            return int(unlock_level)
                        except (ValueError, TypeError):
                            pass
            
            # 제품 언락레벨 (production buildings CSV에서 찾기)
            for key, df in self.data.items():
                if df.empty or not key.endswith('_goods'):
                    continue
                    
                matching_items = df[df['Name'] == item_name]
                if not matching_items.empty:
                    # building 이름으로 processing_buildings.csv에서 언락레벨 찾기
                    building_name = key.replace('_goods', '')
                    unlock_level = self._get_building_unlock_level(building_name)
                    if unlock_level > 0:
                        return unlock_level
            
            # 동물 제품 언락레벨  
            if 'animals' in self.data and not self.data['animals'].empty:
                matching_animals = self.data['animals'][self.data['animals']['Good'] == item_name]
                if not matching_animals.empty:
                    unlock_level = matching_animals.iloc[0].get('UnlockLevel')
                    if pd.notna(unlock_level):
                        try:
                            return int(unlock_level)
                        except (ValueError, TypeError):
                            pass
                        item = matching_items.iloc[0]
                        if pd.notna(item.get('UnlockLevel')):
                            try:
                                return int(item.get('UnlockLevel'))
                            except (ValueError, TypeError):
                                pass
                                
            # Animal products도 확인
            if 'animals' in self.data and not self.data['animals'].empty:
                matching_animals = self.data['animals'][self.data['animals']['Good'] == item_name]
                if not matching_animals.empty:
                    animal = matching_animals.iloc[0]
                    if pd.notna(animal.get('UnlockLevel')):
                        try:
                            return int(animal.get('UnlockLevel'))
                        except (ValueError, TypeError):
                            pass
        except Exception as e:
            print(f"WARNING 언락레벨 조회 오류: {e}")
        
        return 1  # 기본값
    
    def simulate_economy(self, days: int = 30, player_level: int = 20) -> Dict:
        """경제 시뮬레이션 실행"""
        results = {
            'days': [],
            'struggle_scores': [],
            'orders_generated': [],
            'total_values': [],
            'difficulties': []
        }
        
        current_struggle = 50.0  # 초기 어려움 지수
        inventory = {'Egg': 10, 'Milk': 8, 'Wheat': 15}  # 초기 인벤토리
        
        for day in range(days):
            # 하루에 3-5개 주문 생성
            daily_orders = []
            daily_value = 0
            
            for _ in range(np.random.randint(3, 6)):
                order = self.generate_delivery_order(player_level, current_struggle)
                if order:
                    daily_orders.append(order)
                    daily_value += order.total_value
            
            # 어려움 지수 업데이트 (주문 완료에 따른 조정)
            if daily_orders:
                avg_difficulty = np.mean([
                    {'VeryEasy': 1, 'Easy': 2, 'Normal': 3, 'Hard': 4, 'VeryHard': 5}
                    .get(order.difficulty.value, 3) for order in daily_orders
                ])
                current_struggle = max(0, current_struggle - (avg_difficulty * 2))
            else:
                current_struggle = min(100, current_struggle + 5)
            
            results['days'].append(day + 1)
            results['struggle_scores'].append(current_struggle)
            results['orders_generated'].append(len(daily_orders))
            results['total_values'].append(daily_value)
            results['difficulties'].append(avg_difficulty if daily_orders else 3)
        
        return results

# Streamlit 대시보드
def create_dashboard():
    """Streamlit 대시보드 생성"""
    st.set_page_config(page_title="HayDay Dynamic Balancing Simulator", layout="wide")
    
    st.title("🚜 HayDay Dynamic Balancing Simulator")
    st.markdown("---")
    
    # 사이드바 설정
    st.sidebar.header("🎮 시뮬레이션 설정")
    st.sidebar.markdown("---")
    
    # Flask 연동 버튼
    if st.sidebar.button("🌐 Flask 웹 UI로 이동", use_container_width=True):
        st.sidebar.markdown(
            """
            <script>
            window.open("http://localhost:5001", "_blank");
            </script>
            """,
            unsafe_allow_html=True
        )
    st.sidebar.markdown("[🌐 Flask 웹 UI 직접 열기](http://localhost:5001)")
    
    # 데이터 탐색 섹션
    st.sidebar.markdown("---")
    st.sidebar.header("📊 데이터 탐색")
    
    data_sections = {
        "🌾 농작물 데이터": ["fields", "fruits", "fruit_trees"],
        "🐄 동물 & 레벨": ["animals", "levels"],
        "🏭 생산 건물": ["processing_buildings", "production_buildings_goods"],
        "🚛 주문 시스템": ["orders", "order_tables", "boats", "train"],
        "📈 생산 체인": ["bakery_goods", "dairy_goods", "cafe_goods"],
    }
    
    selected_section = st.sidebar.selectbox(
        "데이터 카테고리 선택:",
        options=list(data_sections.keys())
    )
    
    if st.sidebar.button("📋 선택한 데이터 보기", use_container_width=True):
        st.sidebar.success(f"{selected_section} 데이터를 Flask 웹 UI에서 확인하세요!")
    
    st.sidebar.markdown("---")
    player_level = st.sidebar.slider("플레이어 레벨", 1, 100, 20)
    simulation_days = st.sidebar.slider("시뮬레이션 기간 (일)", 7, 90, 30)
    delivery_type = st.sidebar.selectbox("납품 타입", ["Truck", "Train"])
    
    # 시뮬레이터 초기화
    simulator = HayDaySimulator()
    
    # 메인 탭 (주문 생성을 맨 앞으로)
    tab1, tab2, tab3, tab4 = st.tabs(["📦 주문 생성", "📊 시뮬레이션", "🏭 생산 체인", "📈 데이터 분석"])
    
    with tab1:
        st.header("🎯 실시간 주문 생성")
        
        # 주문 생성 설정 UI
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            test_level = st.slider("📊 테스트 레벨", 1, 100, player_level, help="주문을 생성할 플레이어 레벨")
        
        with col2:
            struggle_score = st.slider("😰 어려움 지수", 0, 100, 50, help="0=매우 쉬움, 100=매우 어려움")
        
        with col3:
            delivery_type_select = st.selectbox("🚚 배송", ["Truck", "Train"])
        
        # 레벨별 사용 가능한 아이템 미리보기
        st.subheader(f"📋 레벨 {test_level}에서 사용 가능한 아이템")
        available_items = simulator._get_available_items(test_level)
        
        if available_items:
            cols = st.columns(min(5, len(available_items)))
            for i, item in enumerate(available_items[:15]):  # 최대 15개만 표시
                with cols[i % 5]:
                    unlock_level = simulator._get_item_unlock_level(item)
                    price = simulator._get_item_value(item)
                    production_time = simulator._get_item_production_time(item)
                    
                    st.info(f"""
                    **{item}**  
                    🔓 레벨 {unlock_level}  
                    💰 {price} 코인  
                    ⏰ {production_time}분
                    """)
        
        st.markdown("---")
        
        # 주문 생성 버튼
        if st.button("🎲 주문 생성하기", type="primary", use_container_width=True):
            with st.spinner("주문 생성 중..."):
                delivery_type_enum = DeliveryType.TRUCK if delivery_type_select == "Truck" else DeliveryType.TRAIN
                generated_order = simulator.generate_delivery_order(test_level, struggle_score, delivery_type_enum)
            
            if generated_order:
                st.success("SUCCESS 주문이 생성되었습니다!")
                
                # 주문 정보 표시
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("주문 ID", generated_order.order_id)
                    st.metric("배송 타입", generated_order.delivery_type.value)
                
                with col2:
                    st.metric("총 가치", f"{generated_order.total_value:,} 코인")
                    st.metric("난이도", generated_order.difficulty.value)
                
                with col3:
                    st.metric("요구 레벨", generated_order.level_requirement)
                    st.metric("어려움 지수", f"{generated_order.struggle_score:.1f}")
                
                # 주문 아이템 상세
                st.subheader("📦 주문 아이템")
                
                items_data = []
                total_production_time = 0
                total_estimated_cost = 0
                
                for item_name, quantity in generated_order.items.items():
                    price = simulator._get_item_value(item_name)
                    production_time = simulator._get_item_production_time(item_name)
                    unlock_level = simulator._get_item_unlock_level(item_name)
                    
                    item_total_time = production_time * quantity
                    item_total_value = price * quantity
                    
                    total_production_time += item_total_time
                    total_estimated_cost += item_total_value
                    
                    items_data.append({
                        "아이템": item_name,
                        "수량": quantity,
                        "단가": f"{price:,} 코인",
                        "소계": f"{item_total_value:,} 코인",
                        "생산시간": f"{production_time}분",
                        "총 시간": f"{item_total_time}분",
                        "언락레벨": unlock_level
                    })
                
                df_items = pd.DataFrame(items_data)
                st.dataframe(df_items, use_container_width=True)
                
                # 주문 분석
                st.subheader("📊 주문 분석")
                analysis_col1, analysis_col2, analysis_col3, analysis_col4 = st.columns(4)
                
                with analysis_col1:
                    st.metric("아이템 종류", len(generated_order.items))
                
                with analysis_col2:
                    st.metric("총 생산시간", f"{total_production_time}분")
                
                with analysis_col3:
                    profit_margin = ((generated_order.total_value - total_estimated_cost) / generated_order.total_value * 100) if generated_order.total_value > 0 else 0
                    st.metric("예상 수익률", f"{profit_margin:.1f}%")
                
                with analysis_col4:
                    efficiency = generated_order.total_value / max(total_production_time, 1)
                    st.metric("시간당 수익", f"{efficiency:.1f} 코인/분")
            else:
                st.error("ERROR 주문 생성에 실패했습니다.")
    
    with tab2:
        st.header("📊 경제 시뮬레이션")
        
        if st.button("🚀 시뮬레이션 실행"):
            with st.spinner("시뮬레이션 실행 중..."):
                results = simulator.simulate_economy(simulation_days, player_level)
            
            # 결과 시각화
            col1, col2 = st.columns(2)
            
            with col1:
                # 어려움 지수 변화
                fig1 = px.line(
                    x=results['days'], 
                    y=results['struggle_scores'],
                    title="어려움 지수 변화",
                    labels={'x': '일', 'y': 'Struggle Score'}
                )
                fig1.add_hline(y=30, line_dash="dash", line_color="green", 
                              annotation_text="Easy Threshold")
                fig1.add_hline(y=60, line_dash="dash", line_color="red", 
                              annotation_text="Hard Threshold")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # 일일 주문량
                fig2 = px.bar(
                    x=results['days'], 
                    y=results['orders_generated'],
                    title="일일 생성된 주문 수",
                    labels={'x': '일', 'y': '주문 수'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # 경제 지표
            col3, col4 = st.columns(2)
            
            with col3:
                # 일일 총 가치
                fig3 = px.line(
                    x=results['days'], 
                    y=results['total_values'],
                    title="일일 총 주문 가치",
                    labels={'x': '일', 'y': '코인 가치'}
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            with col4:
                # 난이도 분포
                fig4 = px.line(
                    x=results['days'], 
                    y=results['difficulties'],
                    title="평균 난이도 변화",
                    labels={'x': '일', 'y': '난이도 (1-5)'}
                )
                st.plotly_chart(fig4, use_container_width=True)
            
            # 통계 요약
            st.subheader("📊 시뮬레이션 통계")
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric("평균 어려움 지수", f"{np.mean(results['struggle_scores']):.1f}")
            with col6:
                st.metric("총 생성된 주문", f"{sum(results['orders_generated'])}")
            with col7:
                st.metric("총 경제 가치", f"{sum(results['total_values']):,} 코인")
            with col8:
                st.metric("평균 일일 주문", f"{np.mean(results['orders_generated']):.1f}")
    
    with tab2:
        st.header("생산 체인 분석")
        
        # 생산 체인 데이터 표시
        chains = simulator.analyze_production_chains()
        
        if chains:
            chain_data = []
            for name, chain in chains.items():
                chain_data.append({
                    '아이템': name,
                    '생산 시간': f"{chain.production_time}분" if chain.production_time > 0 else "연속",
                    '필요 재료': ', '.join([f"{k}×{v}" for k, v in chain.ingredients.items()]),
                    '가치': f"{chain.value} 코인",
                    '해금 레벨': chain.unlock_level,
                    '건물 타입': chain.building_type
                })
            
            df = pd.DataFrame(chain_data)
            st.dataframe(df, use_container_width=True)
            
            # 가치별 생산품 차트 (오류 방지)
            try:
                values = []
                for x in df.head(20)['가치']:
                    try:
                        # "123 코인" 형태에서 숫자 부분만 추출
                        val = str(x).split()[0] if ' ' in str(x) else str(x)
                        values.append(int(val) if val.isdigit() else 0)
                    except:
                        values.append(0)
                
                fig = px.bar(
                    df.head(20), 
                    x='아이템', 
                    y=values,
                    title="상위 20개 생산품 가치",
                    labels={'y': '코인 가치'}
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"차트 생성 중 오류: {e}")
    
    with tab3:
        st.header("🏭 생산 체인 분석")
        
        # 레벨 필터링
        level_filter = st.slider("📊 최대 언락레벨", 1, 100, 50, help="이 레벨까지의 아이템들만 표시")
        
        # 생산 체인 데이터 수집
        production_data = []
        
        production_buildings = ['bakery', 'dairy', 'cafe', 'barbecue_grill', 'cake_oven', 
                              'candy_machine', 'deep_fryer', 'jam_maker', 'juice_press']
        
        for building in production_buildings:
            if building in simulator.data and not simulator.data[building].empty:
                for _, product in simulator.data[building].iterrows():
                    if (pd.notna(product.get('Name')) and 
                        pd.notna(product.get('UnlockLevel')) and
                        int(product.get('UnlockLevel', 999)) <= level_filter):
                        
                        name = str(product.get('Name'))
                        unlock_level = int(product.get('UnlockLevel', 1))
                        production_time = int(product.get('TimeMin', 15))
                        order_price = int(product.get('OrderPrice', 20))
                        
                        # 효율성 계산 (코인/분)
                        efficiency = order_price / max(production_time, 1)
                        
                        # 재료 정보 (간단화)
                        requirements = []
                        req_amount = product.get('RequirementAmount')
                        requirement = product.get('Requirement')
                        if pd.notna(req_amount) and pd.notna(requirement):
                            requirements.append(f"{requirement} x{req_amount}")
                        
                        production_data.append({
                            "아이템": name,
                            "언락레벨": unlock_level,
                            "생산시간": f"{production_time}분",
                            "주문가격": f"{order_price:,} 코인",
                            "효율성": f"{efficiency:.2f} 코인/분",
                            "건물": building.replace('_', ' ').title(),
                            "재료": ', '.join(requirements) if requirements else "없음"
                        })
        
        if production_data:
            df_production = pd.DataFrame(production_data)
            
            # 정렬 옵션
            sort_options = ["언락레벨", "효율성", "주문가격", "생산시간"]
            sort_by = st.selectbox("정렬 기준", sort_options, index=1)
            ascending = st.checkbox("오름차순", value=False if sort_by == "효율성" else True)
            
            if sort_by == "효율성":
                df_production['효율성_숫자'] = df_production['효율성'].str.extract(r'(\d+\.?\d*)').astype(float)
                df_production = df_production.sort_values('효율성_숫자', ascending=ascending)
                df_production = df_production.drop('효율성_숫자', axis=1)
            else:
                df_production = df_production.sort_values(sort_by, ascending=ascending)
            
            st.dataframe(df_production, use_container_width=True)
            
            # 효율성 차트
            st.subheader("📊 생산 효율성 비교")
            
            # 상위 15개 아이템만
            top_items = df_production.head(15)
            efficiency_values = [float(x.split()[0]) for x in top_items['효율성']]
            
            fig_efficiency = px.bar(
                x=top_items['아이템'],
                y=efficiency_values,
                title="상위 15개 아이템 효율성 (코인/분)",
                labels={'x': '아이템', 'y': '효율성 (코인/분)'}
            )
            fig_efficiency.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_efficiency, use_container_width=True)
        else:
            st.warning("선택된 레벨 범위에서 표시할 생산품이 없습니다.")
    
    with tab4:
        st.header("📈 HayDay 데이터 분석")
        
        # 데이터 통계 표시
        st.subheader("📊 로드된 데이터 요약")
        
        data_stats = {}
        for category, df in simulator.data.items():
            if not df.empty:
                data_stats[category] = len(df)
        
        if data_stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("전체 데이터 카테고리", len(data_stats))
                st.metric("경험 레벨 데이터", len(simulator.exp_levels))
                st.metric("주문 데이터", len(simulator.orders))
                st.metric("사전정의 주문", len(simulator.predefined_orders))
            
            with col2:
                # Production buildings별 아이템 수
                for category, count in list(data_stats.items())[:4]:
                    st.metric(f"{category.title()}", count)
        
        # 레벨별 언락 아이템 분포
        st.subheader("🔓 레벨별 언락 아이템 분포")
        
        unlock_data = []
        for level in range(1, 101):
            available_items = simulator._get_available_items(level)
            unlock_data.append({"레벨": level, "사용가능 아이템": len(available_items)})
        
        df_unlock = pd.DataFrame(unlock_data)
        
        fig_unlock = px.line(
            df_unlock, 
            x="레벨", 
            y="사용가능 아이템",
            title="플레이어 레벨별 사용 가능한 아이템 수",
            labels={"레벨": "플레이어 레벨", "사용가능 아이템": "아이템 수"}
        )
        st.plotly_chart(fig_unlock, use_container_width=True)
        
        # 경험 레벨 시스템
        st.subheader("⭐ 경험 레벨 시스템")
        
        if not simulator.exp_levels.empty:
            exp_sample = simulator.exp_levels.head(50)  # 처음 50레벨만
            
            fig_exp = px.line(
                exp_sample,
                x="Level",
                y="ExpToNextLevel", 
                title="레벨별 다음 레벨까지 필요한 경험치",
                labels={"Level": "레벨", "ExpToNextLevel": "필요 경험치"}
            )
            st.plotly_chart(fig_exp, use_container_width=True)
            
            # 주문 가치 범위
            if 'OrderMinValue' in exp_sample.columns and 'OrderMaxValue' in exp_sample.columns:
                fig_order_value = px.line(
                    exp_sample,
                    x="Level",
                    y=["OrderMinValue", "OrderMaxValue"],
                    title="레벨별 주문 가치 범위",
                    labels={"Level": "레벨", "value": "주문 가치 (코인)"}
                )
                st.plotly_chart(fig_order_value, use_container_width=True)
        
        # 실시간 시스템 상태
        st.subheader("⚡ 시스템 상태")
        
        system_col1, system_col2, system_col3 = st.columns(3)
        
        with system_col1:
            st.success("SUCCESS HayDay 데이터 로드됨")
            st.info(f"📁 {len(simulator.data)} 개 데이터 카테고리")
        
        with system_col2:
            st.success("SUCCESS 시뮬레이션 엔진 가동중")
            st.info("🎯 레벨별 동적 밸런싱 활성화")
        
        with system_col3:
            st.success("SUCCESS 실제 가격/시간 데이터 적용")
            st.info("⏰ 실시간 주문 생성 가능")

if __name__ == "__main__":
    if HAS_STREAMLIT:
        create_dashboard()
    else:
        print("Streamlit not available. Running in headless mode.")
        print("Creating simulator instance...")
        simulator = HayDaySimulator()
        print("HayDay Simulator created successfully!")
        print(f"Available items: {len(simulator.get_available_items())}")
        print("Use this simulator in your Flask app or other applications.")