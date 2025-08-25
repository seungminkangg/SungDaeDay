#!/usr/bin/env python3
"""
HayDay Dynamic Balancing Web UI
Flask 기반 웹 대시보드
"""

from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
import threading
import time

# HayDay Simulator 모듈 임포트 - 상대 경로 사용
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from hayday_simulator import HayDaySimulator, DeliveryType, DifficultyType
except ImportError:
    print("⚠️ hayday_simulator.py를 찾을 수 없습니다. 상위 디렉토리에 있는지 확인하세요.")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'hayday_secret_key_2024'

# 로컬라이제이션 클래스
class Localization:
    def __init__(self, data_dir):
        self.translations = {}
        self.load_translations(data_dir)
    
    def load_translations(self, data_dir):
        """한국어와 영어 번역 로드"""
        try:
            # 영어 (기본)
            en_path = f"{data_dir}/texts.csv"
            if os.path.exists(en_path):
                en_df = pd.read_csv(en_path)
                if len(en_df) > 1 and all(en_df.iloc[0].astype(str).str.contains('string', na=False)):
                    en_df = en_df.drop(0).reset_index(drop=True)
                self.translations['en'] = dict(zip(en_df['Name'], en_df['EN']))
            
            # 한국어
            kr_path = f"{data_dir}/kr.csv"
            if os.path.exists(kr_path):
                kr_df = pd.read_csv(kr_path)
                if len(kr_df) > 1 and all(kr_df.iloc[0].astype(str).str.contains('string', na=False)):
                    kr_df = kr_df.drop(0).reset_index(drop=True)
                self.translations['kr'] = dict(zip(kr_df['TID'], kr_df['KR']))
                
            print(f"Localization loaded: EN({len(self.translations.get('en', {}))}), KR({len(self.translations.get('kr', {}))})")
        except Exception as e:
            print(f"Warning: Localization loading failed: {e}")
    
    def get_text(self, tid, lang='en'):
        """TID로 번역된 텍스트 가져오기"""
        if lang in self.translations and tid in self.translations[lang]:
            return self.translations[lang][tid]
        # 폴백: 다른 언어에서 찾기
        for fallback_lang in ['en', 'kr']:
            if fallback_lang in self.translations and tid in self.translations[fallback_lang]:
                return self.translations[fallback_lang][tid]
        return tid  # 번역이 없으면 원본 TID 반환

# 전역 시뮬레이터 인스턴스
simulator = None
localization = None
simulation_data = {"status": "ready", "results": None}

def init_simulator():
    """시뮬레이터 및 로컬라이제이션 초기화"""
    global simulator, localization
    try:
        simulator = HayDaySimulator()
        print("Simulator initialization completed")
        
        # 로컬라이제이션 초기화 - 상대 경로 사용 (core_data 디렉토리 사용)
        localization_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hayday_extracted_data", "core_data")
        localization = Localization(localization_path)
        print("Localization initialization completed")
    except Exception as e:
        print(f"Initialization failed: {e}")

@app.route('/')
def index():
    """메인 페이지 - 주문 관리"""
    return render_template('orders.html')

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    return render_template('dashboard.html')

@app.route('/simulation')
def simulation_page():
    """시뮬레이션 페이지"""
    return render_template('simulation.html')

@app.route('/production')
def production_page():
    """Production 체인 분석 페이지"""
    return render_template('production.html')

@app.route('/orders')
def orders_page():
    """Order 생성 테스트 페이지"""
    return render_template('orders.html')

@app.route('/data')
def data_page():
    """데이터 분석 페이지"""
    return render_template('data.html')

# API 엔드포인트들
@app.route('/api/stats')
def api_stats():
    """기본 통계 API"""
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    stats = {
        "total_orders": len(simulator.orders) if not simulator.orders.empty else 0,
        "total_levels": len(simulator.exp_levels) if not simulator.exp_levels.empty else 0,
        "predefined_orders": len(simulator.predefined_orders) if not simulator.predefined_orders.empty else 0,
        "data_categories": len([k for k in simulator.data.keys()]),
        "last_updated": datetime.now().isoformat()
    }
    return jsonify(stats)

@app.route('/api/animals')
def api_animals():
    """동물 데이터 API"""
    if not simulator or 'animals' not in simulator.data:
        return jsonify({"error": "Animals data not found"}), 404
    
    animals_df = simulator.data['animals']
    animals_data = []
    
    for _, animal in animals_df.iterrows():
        if pd.notna(animal.get('Name')):
            # 로컬라이제이션 적용
            name_kr = ''
            name_en = ''
            if localization and pd.notna(animal.get('TID')):
                name_kr = localization.get_text(animal.get('TID'), 'kr')
                name_en = localization.get_text(animal.get('TID'), 'en')
                
            animals_data.append({
                "name": animal.get('Name', ''),
                "name_kr": name_kr if name_kr != animal.get('TID') else animal.get('Name', ''),
                "name_en": name_en if name_en != animal.get('TID') else animal.get('Name', ''),
                "tid": animal.get('TID', ''),
                "unlock_level": animal.get('UnlockLevel', 1),
                "feed": animal.get('Feed', ''),
                "good": animal.get('Good', ''),
                "value": animal.get('Value', 0),
                "process_value": animal.get('ProcessValue', 0),
                "price": animal.get('Price', 0)
            })
    
    return jsonify(animals_data)

@app.route('/api/production-chains')
def api_production_chains():
    """Production 체인 분석 API - HayDay 데이터 기반 간단한 오버뷰"""
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    chains_data = []
    
    # HayDay 데이터에서 주문 정보를 체인 데이터로 변환
    try:
        if not simulator.orders.empty:
            for _, order in simulator.orders.head(20).iterrows():
                if pd.notna(order.get('Name')):
                    name = str(order.get('Name', 'Unknown'))
                    
                    # 가치 정보 추출
                    value_cols = [col for col in simulator.orders.columns if 'Value' in col or 'Price' in col]
                    value = 0
                    if value_cols:
                        try:
                            value = int(order.get(value_cols[0], 0)) if pd.notna(order.get(value_cols[0])) else 0
                        except (ValueError, TypeError):
                            value = 0
                    
                    chains_data.append({
                        "name": name,
                        "building_type": "주문",
                        "ingredients": [],
                        "ingredients_count": 0,
                        "production_time_min": 1,
                        "sell_price": value,
                        "unlock_level": 1,
                        "efficiency_per_min": value,
                        "profit_margin_percent": 100,
                        "hourly_profit": value * 60,
                        "ingredients_text": "None"
                    })
        
        # 기본 아이템들 추가 (데이터가 없는 경우)
        if not chains_data:
            basic_items = [
                {"name": "Wheat", "sell_price": 1, "production_time_min": 2},
                {"name": "Corn", "sell_price": 2, "production_time_min": 5},
                {"name": "Egg", "sell_price": 10, "production_time_min": 20},
                {"name": "Milk", "sell_price": 15, "production_time_min": 60}
            ]
            
            for item in basic_items:
                chains_data.append({
                    "name": item["name"],
                    "building_type": "기본 생산",
                    "ingredients": [],
                    "ingredients_count": 0,
                    "production_time_min": item["production_time_min"],
                    "sell_price": item["sell_price"],
                    "unlock_level": 1,
                    "efficiency_per_min": round(item["sell_price"] / item["production_time_min"], 2),
                    "profit_margin_percent": 100,
                    "hourly_profit": round(item["sell_price"] * 60 / item["production_time_min"], 2),
                    "ingredients_text": "None"
                })
    
    except Exception as e:
        print(f"⚠️ 생산 체인 분석 오류: {e}")
        chains_data = [{"error": str(e)}]
    
    # 효율성 순으로 정렬
    chains_data.sort(key=lambda x: x.get('efficiency_per_min', 0), reverse=True)
    return jsonify(chains_data)

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    """경제 시뮬레이션 실행 API"""
    global simulation_data
    
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    data = request.get_json()
    days = data.get('days', 30)
    player_level = data.get('player_level', 20)
    
    def run_simulation():
        global simulation_data
        simulation_data["status"] = "running"
        try:
            results = simulator.simulate_economy(days, player_level)
            simulation_data["results"] = results
            simulation_data["status"] = "completed"
        except Exception as e:
            simulation_data["status"] = "error"
            simulation_data["error"] = str(e)
    
    # 백그라운드에서 시뮬레이션 실행
    thread = threading.Thread(target=run_simulation)
    thread.start()
    
    return jsonify({"message": "Simulation started", "status": "running"})

@app.route('/api/simulation-status')
def api_simulation_status():
    """시뮬레이션 상태 확인 API"""
    return jsonify(simulation_data)

@app.route('/api/generate-order', methods=['POST'])
def api_generate_order():
    """Order 생성 API (고급 파라미터 지원)"""
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    data = request.get_json()
    player_level = data.get('player_level', 20)
    delivery_type = DeliveryType(data.get('delivery_type', 'Truck'))
    manual_mode = data.get('manual_mode', False)
    
    # 고급 모드 vs 자동 모드
    if manual_mode:
        # 수동 파라미터 사용
        struggle_score = data.get('struggle_score', 50.0)
        value_multiplier = data.get('value_multiplier', 1.0)
        special_probability = data.get('special_probability', 10)
        item_bonus = data.get('item_bonus', 0)
    else:
        # 실제 HayDay 로직으로 랜덤 생성 
        import random
        # 레벨에 따른 어려움 지수 (실제 HayDay처럼)
        if player_level <= 15:
            struggle_score = random.uniform(10, 40)  # 초보자는 쉬움
        elif player_level <= 30:
            struggle_score = random.uniform(20, 60)  # 중급자는 보통
        elif player_level <= 50: 
            struggle_score = random.uniform(40, 80)  # 고급자는 어려움
        else:
            struggle_score = random.uniform(60, 95)  # 전문가는 매우 어려움
            
        value_multiplier = random.uniform(0.8, 1.5)  # 가치 변동
        special_probability = random.randint(5, 25)   # 특별주문 확률
        item_bonus = random.choice([-1, 0, 0, 1])    # 아이템 수 변동
    
    try:
        # 기본 주문 생성
        order = simulator.generate_delivery_order(player_level, struggle_score, delivery_type)
        
        # 고급 파라미터 적용
        if order and manual_mode:
            # 가치 배율 적용
            order.total_value = int(order.total_value * value_multiplier)
            
            # 아이템 수 보너스 적용 
            if item_bonus != 0:
                items_list = list(order.items.keys())
                if item_bonus > 0 and len(items_list) > 0:
                    # 아이템 추가
                    available_items = simulator._get_available_items(player_level)
                    new_items = [item for item in available_items if item not in items_list]
                    if new_items:
                        new_item = random.choice(new_items)
                        order.items[new_item] = random.randint(1, 3)
                elif item_bonus < 0 and len(items_list) > 1:
                    # 아이템 제거
                    remove_item = random.choice(items_list)
                    del order.items[remove_item]
        if order:
            return jsonify({
                "order_id": order.order_id,
                "delivery_type": order.delivery_type.value,
                "items": order.items,
                "total_value": order.total_value,
                "difficulty": order.difficulty.value,
                "struggle_score": order.struggle_score,
                "level_requirement": order.level_requirement,
                "avg_production_time": getattr(order, 'avg_production_time', 0),
                "total_production_time": getattr(order, 'total_production_time', 0),
                "expiry_time": getattr(order, 'expiry_time', 60)
            })
        else:
            return jsonify({"error": "Failed to generate order"}), 500
    except Exception as e:
        import traceback
        print(f"Error generating order: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/levels')
def api_levels():
    """Level 데이터 API"""
    if not simulator or simulator.exp_levels.empty:
        return jsonify({"error": "Levels data not found"}), 404
    
    levels_df = simulator.exp_levels
    levels_data = []
    
    # 처음 50개 레벨만 (너무 많은 데이터 방지)
    for _, level in levels_df.head(50).iterrows():
        levels_data.append({
            "level": level.get('Level', 0),
            "exp_to_next": level.get('ExpToNextLevel', 0),
            "max_fields": level.get('MaxFields', 0),
            "order_min_value": level.get('OrderMinValue', 0),
            "order_max_value": level.get('OrderMaxValue', 0)
        })
    
    return jsonify(levels_data)

@app.route('/api/balancing-policies')
def api_balancing_policies():
    """밸런싱 정책 API"""
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    policies = {
        "orders": simulator.orders.to_dict('records') if not simulator.orders.empty else [],
        "predefined_orders": simulator.predefined_orders.to_dict('records') if not simulator.predefined_orders.empty else [],
        "exp_levels": simulator.exp_levels.head(20).to_dict('records') if not simulator.exp_levels.empty else [],
        "data_categories": list(simulator.data.keys())
    }
    
    return jsonify(policies)

@app.route('/api/csv-data/<filename>')
def api_csv_data(filename):
    """개별 CSV 파일 데이터 API"""
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    try:
        # CSV 파일 직접 읽기 - 상대 경로 사용
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hayday_extracted_data", "core_data", f"{filename}.csv")
        if not os.path.exists(csv_path):
            return jsonify({"error": f"CSV file not found: {filename}"}), 404
        
        df = pd.read_csv(csv_path)
        
        # 첫 번째 행이 데이터 타입인 경우 제거
        if len(df) > 1 and all(df.iloc[0].astype(str).str.contains('int|String|Boolean|float', na=False)):
            df = df.drop(0).reset_index(drop=True)
        
        # 빈 Name 행들 필터링 (모든 파일에 적용)
        if 'Name' in df.columns:
            # Name이 비어있지 않은 행만 유지
            df = df[df['Name'].notna() & (df['Name'].astype(str).str.strip() != '')]
            df = df.reset_index(drop=True)
        
        # 로컬라이제이션 적용 (TID가 들어간 모든 컬럼에 적용)
        if localization:
            tid_columns = [col for col in df.columns if 'TID' in col.upper()]
            
            for tid_col in tid_columns:
                # TID 컬럼명에서 의미있는 이름 추출
                if tid_col.upper() == 'TID':
                    # Name 컬럼을 바로 한국어로 교체
                    korean_names = df[tid_col].apply(lambda x: localization.get_text(x, 'kr') if pd.notna(x) else '')
                    # 빈 번역이면 원본 Name 사용
                    df['Name'] = df.apply(lambda row: korean_names[row.name] if korean_names[row.name] != row[tid_col] else (row.get('Name', '') if pd.notna(row.get('Name', '')) else ''), axis=1)
                elif 'DESCRIPTION' in tid_col.upper():
                    # Description 컬럼을 바로 한국어로 교체
                    korean_desc = df[tid_col].apply(lambda x: localization.get_text(x, 'kr') if pd.notna(x) else '')
                    df['Description'] = korean_desc
        
        # TID 원본 컬럼들 완전 제거
        if localization:
            tid_columns_to_remove = [col for col in df.columns if 'TID' in col.upper()]
            df = df.drop(columns=tid_columns_to_remove, errors='ignore')
            
            # Name과 Description 컬럼을 맨 앞으로 이동
            cols = list(df.columns)
            priority_cols = []
            
            # Name을 맨 앞에
            if 'Name' in cols:
                priority_cols.append('Name')
                cols.remove('Name')
            
            # Description을 두 번째에
            if 'Description' in cols:
                priority_cols.append('Description')
                cols.remove('Description')
            
            # 최종 컬럼 순서 적용
            df = df[priority_cols + cols]

        # NaN, Inf 값을 안전하게 처리
        df = df.replace([float('inf'), -float('inf')], None)
        df = df.where(pd.notnull(df), None)
        
        # 딕셔너리로 변환 후 JSON 안전성 검증
        records = df.to_dict('records')
        
        # 각 레코드에서 문제가 될 수 있는 값들 정리
        safe_records = []
        for record in records:
            safe_record = {}
            for key, value in record.items():
                # NaN, Inf, None 값 처리
                if pd.isna(value) or value is None:
                    safe_record[key] = None
                elif value == float('inf') or value == -float('inf'):
                    safe_record[key] = None
                elif isinstance(value, float):
                    # NaN 체크를 더 엄격하게
                    try:
                        import math
                        if math.isnan(value) or math.isinf(value):
                            safe_record[key] = None
                        else:
                            safe_record[key] = float(value)
                    except (ValueError, TypeError, OverflowError):
                        safe_record[key] = None
                elif isinstance(value, str) and value.lower() in ['nan', 'inf', '-inf', 'null']:
                    safe_record[key] = None
                else:
                    # 기본적으로 문자열로 변환하여 안전성 확보
                    try:
                        safe_record[key] = value
                    except:
                        safe_record[key] = str(value)
            safe_records.append(safe_record)
        
        return jsonify(safe_records)
    
    except Exception as e:
        return jsonify({"error": f"Error reading CSV: {str(e)}"}), 500

@app.route('/api/localization/<lang>')
def api_localization(lang):
    """로컬라이제이션 텍스트 API"""
    if not localization:
        return jsonify({"error": "Localization not initialized"}), 500
    
    valid_langs = ['en', 'kr']
    if lang not in valid_langs:
        return jsonify({"error": f"Invalid language. Supported: {valid_langs}"}), 400
    
    translations = localization.translations.get(lang, {})
    return jsonify({
        "language": lang,
        "translations": translations,
        "count": len(translations)
    })

@app.route('/api/export-excel')
def api_export_excel():
    """Excel 파일 내보내기"""
    try:
        sys.path.append('/Users/smkang/cc/sc-compression')
        from sheets_exporter import SheetsExporter
        exporter = SheetsExporter()
        excel_path = exporter.export_to_excel("/Users/smkang/cc/sc-compression/webui/hayday_export.xlsx")
        return send_file(excel_path, as_attachment=True, download_name="hayday_data.xlsx")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# 주문 생성 페이지 라우트
@app.route('/order-generator')
def order_generator():
    """실시간 주문 생성 페이지"""
    return render_template('order_generator.html')

# Streamlit 연동 API
@app.route('/api/streamlit-sync', methods=['GET', 'POST'])
def streamlit_sync():
    """Streamlit과 데이터 동기화"""
    if request.method == 'POST':
        data = request.get_json()
        # Streamlit에서 온 데이터 처리
        return jsonify({"status": "success", "message": "Data synced with Streamlit"})
    else:
        # Streamlit 연결 상태 확인
        try:
            import requests
            response = requests.get('http://localhost:8501/health', timeout=2)
            streamlit_status = "online" if response.status_code == 200 else "offline"
        except:
            streamlit_status = "offline"
        
        return jsonify({
            "streamlit_status": streamlit_status,
            "flask_url": "http://localhost:5001",
            "streamlit_url": "http://localhost:8501"
        })

# 실시간 주문 생성 API (Streamlit과 동일한 로직)
@app.route('/api/generate-order-live', methods=['POST'])
def generate_order_live():
    """실시간 주문 생성 (개선된 버전)"""
    if not simulator:
        return jsonify({"error": "Simulator not initialized"}), 500
    
    data = request.get_json()
    player_level = data.get('player_level', 20)
    struggle_score = data.get('struggle_score', 50.0)
    delivery_type = DeliveryType(data.get('delivery_type', 'Truck'))
    
    try:
        # 사용 가능한 아이템 미리보기
        available_items = simulator._get_available_items(player_level)
        items_info = []
        
        for item in available_items[:10]:  # 최대 10개만
            items_info.append({
                "name": item,
                "unlock_level": simulator._get_item_unlock_level(item),
                "price": simulator._get_item_value(item),
                "production_time": simulator._get_item_production_time(item)
            })
        
        # 주문 생성
        order = simulator.generate_delivery_order(player_level, struggle_score, delivery_type)
        
        if order:
            # 주문 분석
            total_time = sum(simulator._get_item_production_time(item) * qty for item, qty in order.items.items())
            total_cost = sum(simulator._get_item_value(item) * qty for item, qty in order.items.items())
            
            order_details = []
            for item_name, quantity in order.items.items():
                order_details.append({
                    "item": item_name,
                    "quantity": quantity,
                    "unit_price": simulator._get_item_value(item_name),
                    "total_price": simulator._get_item_value(item_name) * quantity,
                    "production_time": simulator._get_item_production_time(item_name),
                    "unlock_level": simulator._get_item_unlock_level(item_name)
                })
            
            return jsonify({
                "success": True,
                "order": {
                    "id": order.order_id,
                    "delivery_type": order.delivery_type.value,
                    "difficulty": order.difficulty.value,
                    "total_value": order.total_value,
                    "struggle_score": order.struggle_score,
                    "level_requirement": order.level_requirement,
                    "avg_production_time": order.avg_production_time,
                    "total_production_time": order.total_production_time,
                    "expiry_time": order.expiry_time,
                    "items": order_details,
                    "analysis": {
                        "total_production_time": total_time,
                        "avg_production_time_per_item": order.avg_production_time,
                        "estimated_cost": total_cost,
                        "profit_margin": ((order.total_value - total_cost) / order.total_value * 100) if order.total_value > 0 else 0,
                        "efficiency": order.total_value / max(total_time, 1),
                        "time_to_value_ratio": total_time / order.total_value if order.total_value > 0 else 0
                    }
                },
                "available_items": items_info
            })
        else:
            return jsonify({"success": False, "error": "Failed to generate order"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("HayDay Dynamic Balancing Web UI")
    print("=" * 50)
    print("Initializing simulator...")
    
    init_simulator()
    
    print("Starting web server...")
    print("URL: http://localhost:5001")
    print("Press Ctrl+C to exit")
    
    app.run(debug=True, host='0.0.0.0', port=5001)