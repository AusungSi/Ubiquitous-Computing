# simulation/generator.py
import numpy as np
import random
from .actors import HolographicState

class RealTimeSimulator:
    """
    全维生理信号生成器 (2.0 Enhanced)
    支持6种医学/生活场景：Normal, Arrhythmia, Fall, Exercise, Hypoglycemia, Infarction
    """
    def __init__(self):
        self.t = 0
        
    def stream_generator(self, scenario_mode="Normal"):
        # === 0. 初始化基准值 (健康态) ===
        base_hr = 75.0
        base_spo2 = 98.0
        base_sys = 120.0
        base_dia = 80.0
        base_temp = 36.6
        base_rr = 16.0
        base_gsr = 2.0 # 基线皮肤电
        
        while True:
            self.t += 1
            
            # === 1. 生成基础波动 (高斯噪声) ===
            curr_hr = base_hr + np.random.normal(0, 2)
            curr_spo2 = base_spo2 + np.random.normal(0, 0.5)
            curr_sys = base_sys + np.random.normal(0, 3)
            curr_dia = base_dia + np.random.normal(0, 2)
            curr_temp = base_temp + np.random.normal(0, 0.1)
            curr_rr = base_rr + np.random.normal(0, 1)
            curr_gsr = base_gsr + np.random.normal(0, 0.2)
            
            curr_shock = 0
            curr_loc = "Bedroom" # 默认位置
            
            # === 2. 场景注入逻辑 (六大场景) ===
            
            # --- A. 基础场景 ---
            if scenario_mode == "Arrhythmia": 
                # [心律失常]: 心率波动大，体温微升
                if (self.t % 40) > 20:
                    curr_hr += np.random.normal(20, 10) # 熵增来源
                    curr_sys += 10
                    curr_temp += 0.4
                curr_loc = "LivingRoom"
                
            elif scenario_mode == "Fall_Bathroom": 
                # [浴室跌倒]: 冲击 -> 剧痛(GSR/BP高) -> 休克(BP低)
                curr_loc = "Bathroom"
                if self.t > 20:
                    if self.t == 21: curr_shock = 1
                    if self.t <= 30: # 剧痛期
                        curr_hr = 125 + np.random.normal(0, 5)
                        curr_sys = 165 + np.random.normal(0, 5)
                        curr_gsr = 15.0 + np.random.normal(0, 2) # 痛
                    else: # 昏迷期
                        curr_sys = 85 + np.random.normal(0, 5) # 低血压
                        curr_spo2 = 88 + np.random.normal(0, 2)
            
            # --- B. 新增高级场景 (Context-Aware) ---
            
            elif scenario_mode == "Exercise":
                # [D. 高强度运动]: 假报警测试
                # 特征: HR极高, BP高, 但 GSR低(无痛), SpO2好
                curr_loc = "Park" # 关键上下文
                if self.t > 10:
                    curr_hr = 135 + np.random.normal(0, 5) # 看起来很危险
                    curr_sys = 155 + np.random.normal(0, 5) # 运动性高血压
                    curr_rr = 28 + np.random.normal(0, 2)   # 气喘吁吁
                    curr_spo2 = 99.0 # 深呼吸供氧极好
                    curr_gsr = 3.0   # 只是出汗，没有痛感尖峰
            
            elif scenario_mode == "Hypoglycemia":
                # [E. 夜间低血糖]: 代谢危机
                # 特征: 冷汗(GSR高+体温低), 心悸
                curr_loc = "Bedroom"
                if self.t > 15:
                    curr_gsr = 12.0 + np.random.normal(0, 1) # 冷汗 (关键特征)
                    curr_temp = 35.8 + np.random.normal(0, 0.1) # 体表湿冷
                    curr_hr = 115 + np.random.normal(0, 5) # 心悸
                    curr_sys = 110 # 血压甚至略低
            
            elif scenario_mode == "Infarction":
                # [F. 急性心梗]: 最高危
                # 特征: 濒死感(GSR极高), 休克(BP低), 缺氧
                curr_loc = "LivingRoom"
                if self.t > 20:
                    curr_gsr = 25.0 + np.random.normal(0, 3) # 剧烈胸痛 (爆表)
                    curr_sys = 80 + np.random.normal(0, 5)   # 心源性休克
                    curr_spo2 = 91 + np.random.normal(0, 1)  # 缺氧
                    curr_rr = 30 # 呼吸急促
                    curr_hr = 100 + np.random.normal(0, 20) # 极度不稳定
            
            # === 3. 边界限制 ===
            curr_spo2 = min(100, max(60, curr_spo2))
            curr_gsr = max(0, curr_gsr)
            curr_sys = max(50, curr_sys)
            
            # === 4. 群智感知 (志愿者) ===
            # 志愿者更容易发现“显性风险”(如跌倒、剧烈疼痛表情)
            crowd_labels = []
            # 显性风险判定逻辑：有冲击 或 极度疼痛(GSR>18) 或 位于高危区且异常
            visible_risk = (curr_shock == 1) or (curr_gsr > 18) or (curr_loc=="Bathroom" and curr_sys < 90)
            
            for _ in range(3):
                if random.random() < 0.6:
                    report = "Risk" if visible_risk else "Normal"
                    if random.random() > 0.95: report = "Normal" if report == "Risk" else "Risk" # 误报
                    crowd_labels.append(report)
            
            # === 5. 封装 ===
            state = HolographicState(
                base_score=95,
                hr=curr_hr, spo2=curr_spo2, 
                bp_sys=curr_sys, bp_dia=curr_dia,
                temp=curr_temp, resp_rate=curr_rr, gsr=curr_gsr,
                location=curr_loc, crowd_labels=crowd_labels, shock=curr_shock
            )
            
            yield state, self.t