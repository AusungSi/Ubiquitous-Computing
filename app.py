# app.py
import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk
from plotly.subplots import make_subplots

# 引入核心模块
from config import *
from core import PrivacyModule, TruthDiscovery, StabilityAnalyzer, CareDecision
from simulation import RealTimeSimulator

# ============================
# 1. 页面与样式配置 (Cyberpunk UI)
# ============================
st.set_page_config(
    page_title="ACAS 2.0 Pro Command Center",
    layout="wide",
    page_icon="🛡️"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* 指标卡片样式 */
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-label { font-size: 12px; color: #888; letter-spacing: 1px; text-transform: uppercase; }
    .metric-value { font-size: 24px; font-weight: bold; color: #EEE; margin: 5px 0; }
    .metric-unit { font-size: 14px; color: #666; font-weight: normal; }
    
    /* 状态指示灯 */
    .status-normal { color: #00FF00 !important; text-shadow: 0 0 10px rgba(0,255,0,0.5); }
    .status-alert { color: #FF0000 !important; animation: blink 1s infinite; text-shadow: 0 0 10px rgba(255,0,0,0.8); }
    
    /* 关键数值高亮 */
    .val-high { color: #FF4444 !important; }
    .val-mid { color: #FFA500 !important; }
    .val-low { color: #00FF00 !important; }

    @keyframes blink { 50% { opacity: 0.5; } }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ ACAS 2.0 全维自适应照护系统")
st.markdown("Context-Aware Multi-modal Crowdsensing Assessment")

# ============================
# 2. 侧边栏：恢复完整的控制参数
# ============================
st.sidebar.header("🔧 仿真控制台")

# 场景选择
scenario = st.sidebar.selectbox(
    "1. 仿真场景",
    [
        "Normal (日常监测)", 
        "Arrhythmia (心律失常)", 
        "Fall_Bathroom (浴室跌倒)", 
        "Exercise (高强度运动-抗误报)",    # 新增
        "Hypoglycemia (夜间低血糖)",       # 新增
        "Infarction (急性心梗-高危)"       # 新增
    ],
    index=0
)

selected_scenario_key = scenario.split(" ")[0]

st.sidebar.markdown("---")
st.sidebar.subheader("2. 算法参数调优")

# [恢复] 完整的参数滑块
k_val = st.sidebar.slider("K-匿名隐私等级 (K)", 1, 20, DEFAULT_K, help="K值越大，地图上的绿框越大")
kl_lam = st.sidebar.slider("真值发现敏感度 (λ)", 0.1, 5.0, KL_SENSITIVITY, help="值越大，对冲突数据越敏感")
ent_th = st.sidebar.slider("熵阈值 (H_th)", 0.5, 3.0, ENTROPY_THRESHOLD, help="越低越容易触发波动报警")

st.sidebar.markdown("---")
start_btn = st.sidebar.button("🚀 启动实时监控", type="primary")

# ============================
# 3. 主界面布局 (增量融合版)
# ============================

# --- 第一行：核心状态与置信度 (保留您觉得好的顶部布局) ---
col_top1, col_top2, col_top3 = st.columns([1, 1, 2])
ph_status = col_top1.empty()
ph_score = col_top2.empty()
ph_trust = col_top3.empty()

st.markdown("---")

# --- 第二行：全维生命体征舱 (新功能，但排版更整齐) ---
st.markdown("##### 🧬 实时生命体征 (Bio-Metrics)")
c1, c2, c3, c4, c5, c6 = st.columns(6)
m_hr, m_bp, m_spo2, m_resp, m_temp, m_gsr = [c.empty() for c in [c1, c2, c3, c4, c5, c6]]

st.markdown("---")

# --- 第三行：图表与地图 (恢复原来的左图右图布局) ---
row3_c1, row3_c2 = st.columns([2, 1])

with row3_c1:
    # [优化] 使用 Tab 避免图表太多太丑
    tab1, tab2 = st.tabs(["📈 循环系统 (HR/BP/SpO2)", "⚡ 神经系统 (GSR/Pain)"])
    with tab1:
        chart_cardio = st.empty()
    with tab2:
        chart_neuro = st.empty()

with row3_c2:
    st.markdown("##### 📍 隐私监控 (K-Box)")
    # [恢复] 地图组件位置
    map_ph = st.empty()

# --- 第四行：系统日志 (恢复底部日志) ---
st.markdown("##### 📝 决策与异常日志")
log_ph = st.empty()


# ============================
# 4. 辅助函数：渲染漂亮的指标卡片
# ============================
def render_metric(placeholder, label, value, unit, level="low"):
    color_map = {
        "low": "val-low",      # 绿色 (正常)
        "mid": "val-mid",      # 橙色 (警告)
        "high": "val-high"     # 红色 (危险)
    }
    color_class = color_map.get(level, "val-low")
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)

# ============================
# 5. 仿真主逻辑
# ============================
if start_btn:
    # 1. 实例化核心模块
    sim = RealTimeSimulator()
    privacy = PrivacyModule(k=k_val)
    truth = TruthDiscovery(sensitivity=kl_lam)
    stability = StabilityAnalyzer(threshold=ent_th)
    decision = CareDecision()
    
    # 2. 数据缓存 (扩充了字段)
    hist = {k: [] for k in ['time','hr','sys','dia','spo2','gsr','score','entropy']}
    logs = []
    
    # 3. 基础坐标 (南航)
    base_lat, base_lon = 31.939, 118.790
    
    stream = sim.stream_generator(selected_scenario_key)
    
    # 4. 实时循环
    for state, t in stream:
        # --- 算法计算 ---
        
        # A. 隐私 (计算框)
        anon_res = privacy.get_k_anonymity_box(base_lat, base_lon)
        bbox = anon_res['bbox']
        
        # B. 稳定性
        entropy, ent_pen = stability.update_and_calculate(state.hr)
        
        # C. 真值发现
        conf, _ = truth.compute_trust_score(state.hr, state.crowd_labels)
        
        # D. 决策
        score, level, changed = decision.evaluate(state, conf, ent_pen)
        
        # --- 记录历史 ---
        for k, v in zip(hist.keys(), [t, state.hr, state.bp_sys, state.bp_dia, state.spo2, state.gsr, score, entropy]):
            hist[k].append(v)
        
        # 保持窗口长度 (60帧)
        if len(hist['time']) > 60:
            for k in hist: hist[k].pop(0)
            
        # --- UI 渲染 ---
        
        # 1. 顶部状态栏 (恢复)
        st_class = "status-normal" if level == "L3" else "status-alert"
        ph_status.markdown(f"""
        <div class="metric-card" style="padding:5px;">
            <div class="metric-label">SYSTEM LEVEL</div>
            <div class="{st_class}" style="font-size:32px; font-weight:bold;">{level}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ph_score.metric("综合健康分", f"{score:.1f}", delta=f"{score-95:.1f}")
        ph_trust.metric("群智置信度", f"{conf:.2f}", help="基于KL散度的可信度评估")
        
        # 2. 六大指标卡片 (判断颜色等级)
        # 心率
        hr_lvl = "high" if state.hr > 110 or state.hr < 50 else "mid" if state.hr > 100 else "low"
        render_metric(m_hr, "HEART RATE", int(state.hr), "BPM", hr_lvl)
        
        # 血压
        bp_lvl = "high" if state.bp_sys > 150 or state.bp_sys < 90 else "low"
        render_metric(m_bp, "BP (SYS/DIA)", f"{int(state.bp_sys)}/{int(state.bp_dia)}", "mmHg", bp_lvl)
        
        # 血氧
        spo2_lvl = "high" if state.spo2 < 90 else "mid" if state.spo2 < 95 else "low"
        render_metric(m_spo2, "SpO2", int(state.spo2), "%", spo2_lvl)
        
        # 呼吸
        rr_lvl = "high" if state.resp_rate > 25 else "low"
        render_metric(m_resp, "RESP RATE", int(state.resp_rate), "RPM", rr_lvl)
        
        # 体温
        temp_lvl = "mid" if state.temp > 37.5 else "low"
        render_metric(m_temp, "TEMP", f"{state.temp:.1f}", "°C", temp_lvl)
        
        # 皮肤电
        gsr_lvl = "high" if state.gsr > 8.0 else "low"
        render_metric(m_gsr, "GSR (PAIN)", f"{state.gsr:.1f}", "µS", gsr_lvl)
        
        # 3. 左侧：图表 (Tab 1 & Tab 2)
        # Tab 1: 循环系统
        fig_c = make_subplots(specs=[[{"secondary_y": True}]])
        fig_c.add_trace(go.Scatter(x=hist['time'], y=hist['hr'], name='HR', line=dict(color='#00BFFF', width=2)), secondary_y=False)
        fig_c.add_trace(go.Scatter(x=hist['time'], y=hist['sys'], name='Sys BP', line=dict(color='#FF4444', width=1, dash='dot')), secondary_y=True)
        fig_c.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), template="plotly_dark", legend=dict(orientation="h", y=1.1))
        chart_cardio.plotly_chart(fig_c, use_container_width=True)
        
        # Tab 2: 神经/痛感
        fig_n = make_subplots(specs=[[{"secondary_y": True}]])
        fig_n.add_trace(go.Scatter(x=hist['time'], y=hist['gsr'], name='GSR (Pain)', fill='tozeroy', line=dict(color='#FFA500')), secondary_y=False)
        fig_n.add_trace(go.Scatter(x=hist['time'], y=hist['score'], name='Score', line=dict(color='#00FF00', dash='dash')), secondary_y=True)
        fig_n.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), template="plotly_dark", legend=dict(orientation="h", y=1.1))
        chart_neuro.plotly_chart(fig_n, use_container_width=True)
        
        # 4. 右侧：地图 (恢复 K-Box 显示)
        # 构造 K-匿名框 Polygon
        box_coords = [[
            [bbox[0], bbox[1]], [bbox[2], bbox[1]], 
            [bbox[2], bbox[3]], [bbox[0], bbox[3]],
            [bbox[0], bbox[1]] # 闭合
        ]]
        
        layer_box = pdk.Layer(
            "PolygonLayer",
            data=[{"coords": box_coords, "name": "K-Region"}],
            get_polygon="coords",
            get_fill_color=[0, 255, 100, 30], # 绿色半透明
            get_line_color=[0, 255, 100, 200],
            get_line_width=3,
        )
        
        # 真实位置 (红点)
        layer_point = pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": base_lat, "lon": base_lon}],
            get_position="[lon, lat]",
            get_color=[255, 0, 0, 200],
            get_radius=20,
        )
        
        view_state = pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=14.5, pitch=30)
        map_ph.pydeck_chart(pdk.Deck(layers=[layer_box, layer_point], initial_view_state=view_state, map_style="dark"))
        
        # 5. 底部：日志 (恢复)
        if changed or state.shock or score < 70 or state.gsr > 10:
            icon = "🔴" if level == "L4" else "⚠️"
            # 根据场景判断日志内容
            extra_info = ""
            if state.bp_sys > 150: extra_info = f"BP_HIGH:{int(state.bp_sys)}"
            if state.gsr > 10: extra_info = f"PAIN_DETECTED(GSR:{state.gsr:.1f})"
            if state.shock: extra_info = "FALL_IMPACT!"
            
            msg = f"{icon} T={t} | {level} | {state.location} | Score:{score:.1f} | {extra_info} | Crowd:{state.crowd_labels}"
            logs.insert(0, msg)
            # 限制日志条数
            log_ph.text_area("System Logs (Real-time)", "\n".join(logs[:8]), height=150)
            
        time.sleep(0.3)