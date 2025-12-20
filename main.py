import sys
import os
import numpy as np
from config import *
from simulation.generator import DataGenerator
from core.truth_discovery import TruthDiscovery
from core.stability import StabilityAnalyzer
from core.decision import CareDecision
from core.privacy import PrivacyModule
from utils.visualization import Visualizer

def main():
    print(f"Starting ACAS Simulation (Duration: {SIMULATION_DURATION})...")
    
    # 1. 初始化模块
    gen = DataGenerator(duration=SIMULATION_DURATION)
    truth_finder = TruthDiscovery(sensitivity=KL_SENSITIVITY)
    stability_analyzer = StabilityAnalyzer(threshold=ENTROPY_THRESHOLD, delta=DELTA)
    decision_maker = CareDecision(base_score=BASE_HEALTH_SCORE)
    privacy_module = PrivacyModule(k=K_ANONYMITY_VAL)
    
    # 2. 生成仿真数据 (D_sensor)
    # 设定：中间时段(40-70)发生心律失常风险
    hr_stream = gen.generate_heart_rate_stream(risk_period=(40, 70))
    
    # 存储结果用于分析
    simulation_log = {
        'time': [], 'hr': [], 'entropy': [], 'kl_div': [], 
        'q_val': [], 'score': [], 'level': [], 'privacy_area': []
    }
    
    # 3. 时间步循环
    for t in range(len(hr_stream)):
        current_hr = hr_stream[t]
        
        # --- A. 隐私保护层 (Privacy Layer) ---
        # 模拟位置泛化，计算匿名区域面积
        anon_area = privacy_module.generalize_location((0, 0)) # 假设原点为中心
        
        # --- B. 数据清洗层 (Truth Discovery) ---
        # 模拟志愿者数据 (D_crowd)：在风险时段，真实状态为1(Risk)
        real_status = 1 if (40 <= t <= 70) else 0
        crowd_labels = gen.generate_crowd_data(t, real_status)
        
        # 计算分布与KL散度
        P = truth_finder.sensor_to_distribution(current_hr)
        Q = truth_finder.labels_to_distribution(crowd_labels)
        kl_div, q_val = truth_finder.compute_confidence(P, Q)
        
        # --- C. 状态评估层 (Stability Assessment) ---
        # 获取滑动窗口数据
        start_idx = max(0, t - WINDOW_SIZE)
        window_data = hr_stream[start_idx : t+1]
        
        entropy_val = stability_analyzer.compute_shannon_entropy(window_data)
        penalty = stability_analyzer.calculate_penalty(entropy_val)
        
        # --- D. 决策层 (Decision Making) ---
        score = decision_maker.calculate_total_score(q_val, penalty)
        level = decision_maker.apply_hysteresis(score)
        
        # 记录日志
        simulation_log['time'].append(t)
        simulation_log['hr'].append(current_hr)
        simulation_log['entropy'].append(entropy_val)
        simulation_log['kl_div'].append(kl_div)
        simulation_log['q_val'].append(q_val)
        simulation_log['score'].append(score)
        simulation_log['level'].append(1 if level == "L4" else 0)
        simulation_log['privacy_area'].append(anon_area)

    # 4. 结果可视化
    print("Simulation finished. Generating report figures...")
    viz = Visualizer()
    viz.plot_dashboard(simulation_log)
    print("Done.")

if __name__ == "__main__":
    main()