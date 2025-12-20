import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import pydeck as pdk

# 引用核心模块
from simulation.generator import DataGenerator
from core.truth_discovery import TruthDiscovery
from core.stability import StabilityAnalyzer
from core.decision import CareDecision
from core.privacy import PrivacyModule

# ==========================================
# 1. 页面配置 (Dark Mode Command Center)
# ==========================================
st.set_page_config(
    page_title="ACAS 2.0 Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自定义 CSS 实现赛博朋克风格
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .metric-card {
        background-color: #262730;
        border: 1px solid #4F4F4F;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #00FF00; }
    .metric-label { font-size: 14px; color: #A0A0A0; }
    .status-normal { color: #00FF00 !important; }
    .status-warn { color: #FFA500 !important; }
    .status-alert { color: #FF0000 !important; animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0.5; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 侧边栏：控制台
# ==========================================
st.sidebar.title("🛡️ ACAS 2.0 控制台")
st.sidebar.markdown("Adaptive Care Assessment System")
st.sidebar.markdown("---")

# 场景选择
scenario_map = {
    "场景 A: 运动干扰排除 (Context-Aware)": "SCENARIO_1_CONTEXT_FILTER",
    "场景 B: 浴室跌倒危机 (Critical Fall)": "SCENARIO_2_CRITICAL_FALL",
    "场景 C: 隐私博弈演示 (Privacy Trade)": "SCENARIO_3_PRIVACY_TRADE"
}
selected_scenario_label = st.sidebar.selectbox("1. 选择仿真剧本", list(scenario_map.keys()))
selected_scenario = scenario_map[selected_scenario_label]

st.sidebar.markdown("---")
st.sidebar.subheader("2. 系统参数动态调优")

# 交互式参数
k_val = st.sidebar.slider("K-匿名等级 (Privacy)", 1, 20, 5, help="K值越大，定位越模糊，但志愿者响应越慢")
lambda_val = st.sidebar.slider("KL散度敏感度 (Truth)", 0.1, 5.0, 2.0)
entropy_th = st.sidebar.slider("熵阈值 (Stability)", 0.5, 3.0, 1.8)

start_btn = st.sidebar.button("🚀 启动数字孪生仿真", type="primary")

# ==========================================
# 3. 主界面布局
# ==========================================

# 顶部状态栏
col1, col2, col3, col4 = st.columns(4)
status_ph = col1.empty()
score_ph = col2.empty()
loc_ph = col3.empty()
env_ph = col4.empty()

# 中间区域：左侧人体图，右侧数据流
row2_col1, row2_col2 = st.columns([1, 2])

with row2_col1:
    st.markdown("### 🧬 数字孪生体征")
    # 使用 SVG 绘制简单的人体状态 Mockup
    human_body_ph = st.empty()
    st.markdown("---")
    st.markdown("### 📝 决策日志")
    log_ph = st.empty()

with row2_col2:
    # Tab页签
    tab_chart, tab_map = st.tabs(["📈 多维时序分析", "🗺️ K-匿名地理监控"])
    
    with tab_chart:
        chart_ph = st.empty()
    
    with tab_map:
        map_ph = st.empty()

# ==========================================
# 4. 仿真逻辑
# ==========================================

if start_btn:
    # --- 初始化 ---
    gen = DataGenerator(duration=100)
    truth_finder = TruthDiscovery(sensitivity=lambda_val)
    stab_analyzer = StabilityAnalyzer(threshold=entropy_th, delta=15)
    decision_maker = CareDecision(base_score=85)
    privacy_module = PrivacyModule(k=k_val)
    
    # --- 获取全量数据 ---
    (hr_all, spo2_all, temp_all, loc_types, 
     true_status_all, acc_all) = gen.generate_extended_scenario(selected_scenario)
    
    # 历史数据容器
    history = {
        'time': [], 'hr': [], 'spo2': [], 'entropy': [], 'score': []
    }
    
    logs = []
    
    # 东京坐标基准
    lat_base, lon_base = 35.6895, 139.6917
    
    # 进度条
    progress = st.progress(0)
    
    # --- 循环仿真 ---
    for t in range(len(hr_all)):
        # 1. 提取当前帧数据
        curr_hr = hr_all[t]
        curr_spo2 = spo2_all[t]
        curr_temp = temp_all[t]
        curr_loc = loc_types[t]
        curr_acc = acc_all[t]
        
        # 2. 算法计算
        # A. 熵计算
        win_data = hr_all[max(0, t-10):t+1]
        entropy = stab_analyzer.compute_shannon_entropy(win_data)
        entropy_pen = stab_analyzer.calculate_penalty(entropy)
        
        # B. 真值发现
        crowd_reports = gen.generate_crowd_reports(true_status_all[t], k_val)
        P = truth_finder.sensor_to_distribution(curr_hr)
        Q = truth_finder.labels_to_distribution(crowd_reports)
        _, q_val = truth_finder.compute_confidence(P, Q)
        
        # C. 决策融合 (核心线性公式)
        score = decision_maker.calculate_total_score(
            q_val, entropy_pen, curr_acc, curr_spo2, curr_loc
        )
        level = decision_maker.apply_hysteresis(score)
        
        # D. 隐私位置计算
        sim_lat = lat_base + (t * 0.0001) + np.random.normal(0, 0.0001)
        sim_lon = lon_base + (t * 0.0001) + np.random.normal(0, 0.0001)
        # 获取 K-匿名矩形 [min_lon, min_lat, max_lon, max_lat]
        bbox = privacy_module.get_k_anonymity_box(sim_lat, sim_lon)
        
        # --- 更新历史 ---
        history['time'].append(t)
        history['hr'].append(curr_hr)
        history['spo2'].append(curr_spo2)
        history['entropy'].append(entropy)
        history['score'].append(score)
        
        # --- UI 更新渲染 ---
        
        # 1. 顶部指标卡片
        status_color = "status-normal" if level == "L3" else "status-alert"
        status_text = "🟢 MONITORING" if level == "L3" else "🔴 EMERGENCY SOS"
        
        status_ph.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SYSTEM STATUS</div>
            <div class="{status_color}" style="font-size:20px; font-weight:bold;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        score_ph.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">HEALTH SCORE</div>
            <div class="metric-value" style="color: {'#00FF00' if score>60 else '#FF0000'}">{score:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        loc_ph.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SEMANTIC LOC</div>
            <div class="metric-value" style="color: #00BFFF">{curr_loc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        env_ph.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ENV TEMP</div>
            <div class="metric-value" style="color: #FFA500">{curr_temp:.1f}°C</div>
        </div>
        """, unsafe_allow_html=True)

        # 2. 人体数字孪生 (SVG 动态着色)
        heart_color = "red" if curr_hr > 100 or curr_hr < 50 else "#333"
        lung_color = "red" if curr_spo2 < 90 else "#333"
        body_svg = f"""
        <svg height="300" width="150" xmlns="http://www.w3.org/2000/svg">
          <!-- Body Outline -->
          <rect x="50" y="20" width="50" height="60" rx="15" fill="#444" /> <!-- Head -->
          <rect x="25" y="85" width="100" height="120" rx="10" fill="#222" /> <!-- Torso -->
          <rect x="35" y="210" width="35" height="80" rx="5" fill="#222" /> <!-- Leg L -->
          <rect x="80" y="210" width="35" height="80" rx="5" fill="#222" /> <!-- Leg R -->
          
          <!-- Organs (Indicators) -->
          <circle cx="75" cy="120" r="15" fill="{heart_color}" stroke="white" stroke-width="2">
            <animate attributeName="opacity" values="1;0.5;1" dur="{60/curr_hr}s" repeatCount="indefinite" />
          </circle> <!-- Heart -->
          
          <rect x="40" y="100" width="25" height="40" rx="5" fill="{lung_color}" opacity="0.7" /> <!-- Lung L -->
          <rect x="85" y="100" width="25" height="40" rx="5" fill="{lung_color}" opacity="0.7" /> <!-- Lung R -->
          
          <text x="75" y="290" font-size="12" fill="white" text-anchor="middle">Digital Twin</text>
        </svg>
        """
        human_body_ph.markdown(body_svg, unsafe_allow_html=True)

        # 3. 动态图表 (Plotly)
        fig = go.Figure()
        # 心率线
        fig.add_trace(go.Scatter(x=history['time'], y=history['hr'], name='Heart Rate', 
                                 line=dict(color='#00BFFF', width=2)))
        # 分数线
        fig.add_trace(go.Scatter(x=history['time'], y=history['score'], name='Health Score', 
                                 line=dict(color='#00FF00', width=2, dash='dot')))
        # 熵背景区域
        fig.add_trace(go.Scatter(x=history['time'], y=np.array(history['entropy'])*30, name='Entropy (Scaled)',
                                 fill='tozeroy', line=dict(color='rgba(255, 165, 0, 0.5)', width=0)))
        
        fig.update_layout(
            template="plotly_dark", 
            margin=dict(l=0, r=0, t=10, b=0),
            height=350,
            xaxis_title="Time Step",
            yaxis_title="Value"
        )
        chart_ph.plotly_chart(fig, use_container_width=True)

        # 4. 地图监控 (PyDeck)
        # 构造矩形数据
        polygon_data = [{
            "coordinates": [
                [bbox[0], bbox[1]], [bbox[2], bbox[1]], 
                [bbox[2], bbox[3]], [bbox[0], bbox[3]], 
                [bbox[0], bbox[1]] # 闭合
            ],
            "name": "K-Anonymity Box"
        }]
        
        view_state = pdk.ViewState(latitude=sim_lat, longitude=sim_lon, zoom=14, pitch=45)
        
        layer_box = pdk.Layer(
            "PolygonLayer",
            data=polygon_data,
            get_polygon="coordinates",
            get_fill_color=[0, 100, 255, 50], # 蓝色半透明
            get_line_color=[0, 255, 255, 200],
            get_line_width=20,
            pickable=True,
        )
        
        layer_point = pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": sim_lat, "lon": sim_lon}],
            get_position="[lon, lat]",
            get_color=[255, 0, 0, 255], # 真实位置红点
            get_radius=30,
        )
        
        deck = pdk.Deck(layers=[layer_box, layer_point], initial_view_state=view_state, map_style="dark")
        map_ph.pydeck_chart(deck)

        # 5. 日志更新
        if level == "L4" or curr_spo2 < 90 or curr_acc == 1:
            msg = f"[ALERT] t={t} | Loc: {curr_loc} | Score: {score:.1f} | SpO2: {curr_spo2:.0f}%"
            logs.append(msg)
            log_ph.text_area("System Log", "\n".join(logs[-8:]), height=150)
        
        time.sleep(0.05)
        progress.progress((t+1)/100)

    st.success("仿真实验结束")