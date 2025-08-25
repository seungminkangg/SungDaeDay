# 🚜 SungDaeDay - HayDay Dynamic Balancing Simulator

**Real HayDay game data analysis and dynamic balancing simulation system**

## 🌟 Features

### 📊 Streamlit Dashboard (http://localhost:8501)
- **🎯 Real-time Order Generation**: Level-based dynamic order creation with actual HayDay data
- **📈 Economic Simulation**: 30-day economy simulation with struggle score balancing
- **🏭 Production Chain Analysis**: Efficiency analysis of all production buildings
- **📋 HayDay Data Explorer**: Interactive data visualization with unlock levels, prices, and production times

### 🌐 Flask Web UI (http://localhost:5001)
- **📊 Interactive Data Viewer**: Korean/English localized data with Tabulator.js
- **🎲 Live Order Generator**: Real-time order generation with detailed analysis
- **🔗 Streamlit Integration**: Seamless data synchronization between both interfaces
- **📱 Collapsible Sidebar**: Clean, responsive interface design

## 🚀 Quick Start

### 1. Installation
```bash
git clone git@github.com:seungminkangg/SungDaeDay.git
cd SungDaeDay
pip install -r requirements.txt
```

### 2. Run Streamlit Dashboard
```bash
streamlit run hayday_simulator.py --server.port 8501
```

### 3. Run Flask Web UI
```bash
cd webui
python app.py
```

### 4. Access the Applications
- 📊 **Streamlit Dashboard**: http://localhost:8501
- 🌐 **Flask Web UI**: http://localhost:5001  
- 🎲 **Order Generator**: http://localhost:5001/order-generator

## 📂 Project Structure

```
SungDaeDay/
├── hayday_simulator.py          # 📊 Main Streamlit dashboard
├── requirements.txt             # 📦 Python dependencies
├── hayday_extracted_data/       # 🗃️ Original HayDay game data
│   └── core_data/              # 📋 CSV files with game mechanics
│       ├── animals.csv         # 🐄 Animal data
│       ├── bakery_goods.csv    # 🍞 Bakery products
│       ├── dairy_goods.csv     # 🥛 Dairy products
│       ├── exp_levels.csv      # ⭐ Level progression
│       └── ...                 # 🏗️ All production buildings
└── webui/                      # 🌐 Flask web interface
    ├── app.py                  # 🚀 Flask application
    ├── templates/              # 🎨 HTML templates
    │   ├── base.html           # 📄 Base template
    │   ├── data.html           # 📊 Data viewer
    │   └── order_generator.html # 🎲 Order generator
    └── static/                 # 🎨 CSS/JS assets
```

## 🎯 Key Features

### 🧠 Dynamic Balancing System
- **Struggle Score**: Adaptive difficulty based on player performance
- **Level-based Unlocks**: Accurate item availability by player level
- **Real HayDay Data**: Production times, prices, and unlock levels from actual game

### 📊 Data-Driven Analysis
- **20+ Production Buildings**: Complete analysis of all HayDay production chains
- **8,606 Localized Texts**: Korean/English translations for all game items
- **Economic Modeling**: Revenue optimization and efficiency calculations

### 🔗 Dual Interface System
- **Streamlit**: Advanced analytics and simulation visualization  
- **Flask**: Data exploration and real-time order generation
- **Bidirectional Sync**: Seamless data sharing between interfaces

## 🛠️ Technical Stack

- **Backend**: Python, Pandas, NumPy
- **Streamlit**: Plotly, Interactive widgets, Real-time simulation
- **Flask**: Jinja2 templates, Bootstrap 5, Tabulator.js
- **Data**: CSV-based HayDay game data extraction

## 📈 Usage Examples

### Generate Orders by Level
```python
# Level 10 player - only basic items available
simulator.generate_delivery_order(player_level=10, struggle_score=50)
# Returns: Bread, Butter, Corn (appropriate for level 10)

# Level 50 player - advanced items available  
simulator.generate_delivery_order(player_level=50, struggle_score=30)
# Returns: Pizza, Sushi, Complex items (unlocked at higher levels)
```

### Economic Simulation
```python
# Run 30-day economy simulation
results = simulator.simulate_economy(days=30, player_level=25)
# Returns: Daily struggle scores, order values, difficulty progression
```

## 🤝 Contributing

This project analyzes HayDay game mechanics for educational purposes. All data is extracted from publicly available game files.

## 📄 License

MIT License - see LICENSE file for details.

---

**🎮 Made for HayDay fans who love data-driven gameplay optimization! 🚜**
