# app.py
import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pydeck as pdk
from plotly.subplots import make_subplots

# 引入自定义核心模块
from config import *
from core import PrivacyModule, TruthDiscovery, StabilityAnalyzer, CareDecision
from core.nlp_bert import BertSemanticAnalyzer
from simulation import RealTimeSimulator
from simulation.actors import UserProfile

# ============================
# 1. 页面配置与样式 (Cyberpunk UI)
# ============================
st.set_page_config(
    page_title="ACAS 2.0 AI Pro Command Center",
    layout="wide",
    page_icon="🛡️"
)

# 初始化 Session State (防止按钮交互导致重置)
if "running" not in st.session_state:
    st.session_state.running = False

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
st.markdown("Context-Aware Multi-modal Crowdsensing Assessment (Powered by BERT)")

# ============================
# 2. 侧边栏：控制台
# ============================

# --- 2.1 权威基准 (D_prof) ---
st.sidebar.header("1. 权威基准 ($D_{prof}$)")
profile_options = {
    "张三 (健康, 65岁)": UserProfile("张三", 65, "Healthy"),
    "李四 (高血压, 72岁)": UserProfile("李四", 72, "Hypertension"),
    "王五 (阿兹海默, 78岁)": UserProfile("王五", 78, "Alzheimer")
}
selected_profile_key = st.sidebar.selectbox("选择电子健康档案 (EHR)", list(profile_options.keys()))
current_profile = profile_options[selected_profile_key]
st.sidebar.info(f"用户: {current_profile.name} | 状态: {current_profile.condition} | 基准分: {current_profile.base_score}")

st.sidebar.markdown("---")

# --- 2.2 仿真控制 ---
st.sidebar.header("🔧 仿真控制台")
scenario = st.sidebar.selectbox(
    "2. 仿真场景",
    [
        "Normal (日常监测)", 
        "Arrhythmia (心律失常)", 
        "Fall_Bathroom (浴室跌倒)", 
        "Exercise (高强度运动-抗误报)", 
        "Hypoglycemia (夜间低血糖)", 
        "Infarction (急性心梗-高危)"
    ],
    index=0
)
selected_scenario_key = scenario.split(" ")[0]

st.sidebar.subheader("3. 算法参数")
k_val = st.sidebar.slider("K-匿名隐私等级", 1, 20, DEFAULT_K)
kl_lam = st.sidebar.slider("真值敏感度 (λ)", 0.1, 5.0, KL_SENSITIVITY)
ent_th = st.sidebar.slider("熵阈值 (H_th)", 0.5, 3.0, ENTROPY_THRESHOLD)

st.sidebar.markdown("---")

# --- 2.3 启动/停止按钮 (Session State控制) ---
col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("🚀 启动系统", type="primary"):
        st.session_state.running = True
        st.rerun()
with col_b2:
    if st.button("⏹️ 停止仿真"):
        st.session_state.running = False
        st.rerun()

# --- 2.4 志愿者注入 (D_crowd) ---
st.sidebar.markdown("---")
st.sidebar.header("4. 志愿者语义注入")
manual_crowd_text = st.sidebar.text_input("志愿者描述 (BERT)", placeholder="e.g. He looks dizzy")

# ============================
# 3. 主界面布局
# ============================

# --- 3.1 高优中断 ($D_{self}$) ---
with st.container():
    c_sos1, c_sos2 = st.columns([1, 4])
    with c_sos1:
        # 即使重新运行，在逻辑中也会捕捉到这次点击
        is_sos_btn = st.button("🆘 SOS 按键", type="primary", use_container_width=True)
    with c_sos2:
        self_voice_text = st.text_input("🎤 老人语音自述 (BERT情感分析)", placeholder="输入如: 'My chest hurts' 或 'I feel good'")

st.markdown("---")

# --- 3.2 核心状态栏 ---
col_top1, col_top2, col_top3 = st.columns([1, 1, 2])
ph_status = col_top1.empty()
ph_score = col_top2.empty()
ph_trust = col_top3.empty()

st.markdown("---")

# --- 3.3 全维生命体征 ---
st.markdown("##### 🧬 实时生命体征 (Bio-Metrics)")
c1, c2, c3, c4, c5, c6 = st.columns(6)
m_hr, m_bp, m_spo2, m_resp, m_temp, m_gsr = [c.empty() for c in [c1, c2, c3, c4, c5, c6]]

st.markdown("---")

# --- 3.4 图表与地图 ---
row3_c1, row3_c2 = st.columns([2, 1])
with row3_c1:
    tab1, tab2 = st.tabs(["📈 循环系统 (HR/BP/SpO2)", "⚡ 神经系统 (GSR/Pain)"])
    with tab1: chart_cardio = st.empty()
    with tab2: chart_neuro = st.empty()
with row3_c2:
    st.markdown("##### 📍 隐私监控 (K-Box)")
    map_ph = st.empty()

# --- 3.5 日志 ---
st.markdown("##### 📝 决策与异常日志")
log_ph = st.empty()

# ============================
# 4. 辅助渲染函数
# ============================
def render_metric(placeholder, label, value, unit, level="low"):
    color_map = {"low": "val-low", "mid": "val-mid", "high": "val-high"}
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
# 5. 仿真主循环 (状态持久化 + BERT缓存)
# ============================
if st.session_state.running:
    
    # --- 初始化核心模块 ---
    sim = RealTimeSimulator()
    privacy = PrivacyModule(k=k_val)
    truth = TruthDiscovery(sensitivity=kl_lam)
    stability = StabilityAnalyzer()
    decision = CareDecision()
    
    # 缓存加载 BERT
    with st.spinner("正在加载 BERT 认知模型..."):
        bert_engine = BertSemanticAnalyzer()
    
    # 数据容器
    hist = {k: [] for k in ['time','hr','sys','dia','spo2','gsr','score','entropy']}
    logs = []
    base_lat, base_lon = 31.939, 118.790
    
    stream = sim.stream_generator(selected_scenario_key)

    # --- 状态缓存 (BERT 防抖动) ---
    last_crowd_text = None
    cached_crowd_dist = None
    last_self_text = None
    cached_voice_penalty = 0.0
    cached_voice_interrupt = False
    
    # --- 实时数据流循环 ---
    for state, t in stream:
        
        # 1. 覆盖基准分 ($D_{prof}$)
        state.base_score = current_profile.base_score
        
        # 2. BERT 语义感知 (带缓存)
        
        # A. 志愿者通道
        current_crowd_dist = None
        if manual_crowd_text:
            if manual_crowd_text != last_crowd_text:
                cached_crowd_dist = bert_engine.predict_crowd_distribution(manual_crowd_text)
                st.toast(f"BERT解析志愿者: Risk Probability: {cached_crowd_dist[1]:.2f}", icon="🤖")
                last_crowd_text = manual_crowd_text
            current_crowd_dist = cached_crowd_dist
        else:
            last_crowd_text = None
            cached_crowd_dist = None
            
        # B. 老人自述通道
        if self_voice_text:
            if self_voice_text != last_self_text:
                cached_voice_penalty, cached_voice_interrupt = bert_engine.predict_self_score(self_voice_text)
                st.toast(f"BERT解析语音: 罚分={cached_voice_penalty:.1f}, 中断={cached_voice_interrupt}", icon="🗣️")
                last_self_text = self_voice_text
        else:
            last_self_text = None
            cached_voice_penalty = 0.0
            cached_voice_interrupt = False

        # 3. 算法计算
        
        # A. 隐私保护 (升级版: 全栈脱敏)
        # 传入当前的 system level，如果已经是L4，自动降级隐私保护
        # 注意: 这里我们在计算 score 之前就需要知道 level，这在逻辑上是个闭环。
        # 工程上通常取“上一帧的 level”或者预判断。这里我们使用当前计算出的 level (先算后脱敏) 或者简单处理。
        # 为了演示效果，我们先按 L3 算隐私，如果触发中断则在日志里显示隐私“破碎”。
        
        # 调用新接口获取脱敏包
        sanitized_pkg = privacy.apply_privacy_policy(
            current_profile, base_lat, base_lon, system_level=level
        )
        bbox = sanitized_pkg['bbox'] # 用于地图绘图
        
        # [新增] 在侧边栏或Expander展示隐私数据对比 (非常直观)
        with st.sidebar.expander("🔒 隐私保护视图 (Data View)", expanded=False):
            st.write("**原始数据 (Raw)**")
            st.json({
                "Name": current_profile.name,
                "Age": current_profile.age,
                "Condition": current_profile.condition,
                "Loc": f"{base_lat:.4f}, {base_lon:.4f}"
            })
            st.write(f"**发布数据 (Public - {sanitized_pkg['privacy_mode']})**")
            st.json({
                "Name": sanitized_pkg['uid'],
                "Age": sanitized_pkg['age_group'],
                "Cond": sanitized_pkg['condition_category'], # 这里展示 Level 1
                "K-Val": sanitized_pkg['k_level']
            })
        
        # B. 稳定性
        entropy, ent_pen = stability.update_and_calculate(state.hr)
        
        # C. 真值发现 (BERT 增强)
        if current_crowd_dist is not None:
            conf, _ = truth.compute_trust_with_distribution(state.hr, current_crowd_dist)
        else:
            conf, _ = truth.compute_trust_score(state.hr, state.crowd_labels)
            
        # D. 决策 (融合语音罚分)
        total_penalty_input = ent_pen + cached_voice_penalty
        score, level, changed = decision.evaluate(state, conf, total_penalty_input)
        
        # E. 高优中断 ($D_{self}$)
        # 注意：即使点击按钮导致重运行，is_sos_btn 在该帧仍为 True
        if is_sos_btn or cached_voice_interrupt:
            level = "L4"
            score = 0.0
            changed = True
            if is_sos_btn: st.toast("物理 SOS 按键触发！", icon="🚨")
        
        # 4. 记录历史
        for k, v in zip(hist.keys(), [t, state.hr, state.bp_sys, state.bp_dia, state.spo2, state.gsr, score, entropy]):
            hist[k].append(v)
        
        if len(hist['time']) > 60:
            for k in hist: hist[k].pop(0)
            
        # 5. UI 渲染
        
        # 顶部状态
        st_class = "status-normal" if level == "L3" else "status-alert"
        ph_status.markdown(f"""
        <div class="metric-card" style="padding:5px;">
            <div class="metric-label">SYSTEM LEVEL</div>
            <div class="{st_class}" style="font-size:32px; font-weight:bold;">{level}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ph_score.metric("AI 综合评分", f"{score:.1f}", delta=f"{score-state.base_score:.1f}")
        ph_trust.metric("群智置信度", f"{conf:.2f}")
        
        # 指标卡片
        hr_lvl = "high" if state.hr > 110 or state.hr < 50 else "mid" if state.hr > 100 else "low"
        render_metric(m_hr, "HEART RATE", int(state.hr), "BPM", hr_lvl)
        
        bp_lvl = "high" if state.bp_sys > 150 or state.bp_sys < 90 else "low"
        render_metric(m_bp, "BP (SYS/DIA)", f"{int(state.bp_sys)}/{int(state.bp_dia)}", "mmHg", bp_lvl)
        
        spo2_lvl = "high" if state.spo2 < 90 else "mid" if state.spo2 < 95 else "low"
        render_metric(m_spo2, "SpO2", int(state.spo2), "%", spo2_lvl)
        
        rr_lvl = "high" if state.resp_rate > 25 else "low"
        render_metric(m_resp, "RESP RATE", int(state.resp_rate), "RPM", rr_lvl)
        
        temp_lvl = "mid" if state.temp > 37.5 else "low"
        render_metric(m_temp, "TEMP", f"{state.temp:.1f}", "°C", temp_lvl)
        
        gsr_lvl = "high" if state.gsr > 8.0 else "low"
        render_metric(m_gsr, "GSR (PAIN)", f"{state.gsr:.1f}", "µS", gsr_lvl)
        
        # 图表 (Tab 1)
        fig_c = make_subplots(specs=[[{"secondary_y": True}]])
        fig_c.add_trace(go.Scatter(x=hist['time'], y=hist['hr'], name='HR', line=dict(color='#00BFFF', width=2)), secondary_y=False)
        fig_c.add_trace(go.Scatter(x=hist['time'], y=hist['sys'], name='Sys BP', line=dict(color='#FF4444', width=1, dash='dot')), secondary_y=True)
        fig_c.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), template="plotly_dark", legend=dict(orientation="h", y=1.1))
        chart_cardio.plotly_chart(fig_c, use_container_width=True)
        
        # 图表 (Tab 2)
        fig_n = make_subplots(specs=[[{"secondary_y": True}]])
        fig_n.add_trace(go.Scatter(x=hist['time'], y=hist['gsr'], name='GSR (Pain)', fill='tozeroy', line=dict(color='#FFA500')), secondary_y=False)
        fig_n.add_trace(go.Scatter(x=hist['time'], y=hist['score'], name='Score', line=dict(color='#00FF00', dash='dash')), secondary_y=True)
        fig_n.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0), template="plotly_dark", legend=dict(orientation="h", y=1.1))
        chart_neuro.plotly_chart(fig_n, use_container_width=True)
        
        # 地图
        box_coords = [[
            [bbox[0], bbox[1]], [bbox[2], bbox[1]], 
            [bbox[2], bbox[3]], [bbox[0], bbox[3]],
            [bbox[0], bbox[1]]
        ]]
        layer_box = pdk.Layer("PolygonLayer", data=[{"coords": box_coords}], get_polygon="coords", get_fill_color=[0, 255, 100, 30], get_line_color=[0, 255, 100, 200], get_line_width=3)
        layer_pt = pdk.Layer("ScatterplotLayer", data=[{"lat": base_lat, "lon": base_lon}], get_position="[lon, lat]", get_color=[255, 0, 0, 200], get_radius=20)
        view_state = pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=14.5, pitch=30)
        map_ph.pydeck_chart(pdk.Deck(layers=[layer_box, layer_pt], initial_view_state=view_state, map_style="dark"))
        
        # 日志
        if changed or state.shock or score < 70 or state.gsr > 10:
            icon = "🔴" if level == "L4" else "⚠️"
            extra = []
            if state.bp_sys > 150: extra.append(f"BP:{int(state.bp_sys)}")
            if state.gsr > 10: extra.append(f"PAIN:{state.gsr:.1f}")
            if state.shock: extra.append("FALL!")
            if is_sos_btn: extra.append("SOS_BTN")
            if cached_voice_interrupt: extra.append("VOICE_SOS")
            
            msg = f"{icon} T={t} | {level} | {state.location} | Score:{score:.1f} | {' '.join(extra)}"
            logs.insert(0, msg)
            log_ph.text_area("System Logs", "\n".join(logs[:8]), height=150)
            
        time.sleep(0.3)
else:
    st.info("👋 请在侧边栏点击【🚀 启动系统】开始实时仿真")