import numpy as np
import random

class DataGenerator:
    """
    ACAS 2.0 数据生成器
    新增维度: SpO2, Temperature, Semantic Location
    """
    def __init__(self, duration=100):
        self.duration = duration

    def generate_extended_scenario(self, scenario_type):
        """
        生成多源异构数据流
        返回: (hr, spo2, temp, location_type, true_status, acc_shock)
        """
        steps = self.duration
        hr_data = []
        spo2_data = []
        temp_data = []
        loc_types = []   # 语义标签: Bedroom, Bathroom, Park
        true_status = [] # 0:Normal, 1:Risk
        acc_shock = []   # 0 or 1
        
        # 基础参数
        base_hr = 75
        base_spo2 = 98
        base_temp = 26.0

        if scenario_type == "SCENARIO_1_CONTEXT_FILTER":
            # === 剧本 1: 运动干扰排除 (Park) ===
            # 特征：心率高，但 SpO2 正常，位置在公园 -> 系统应判定为“锻炼”而非风险
            for t in range(steps):
                # 模拟运动心率 (110-120)
                hr_val = 115 + np.random.normal(0, 5)
                # 血氧正常 (运动时供氧充足)
                spo2_val = 98 + np.random.normal(0, 1)
                # 户外温度稍高
                temp_val = 28.0 + np.random.normal(0, 0.5)
                
                hr_data.append(hr_val)
                spo2_data.append(min(100, spo2_val))
                temp_data.append(temp_val)
                loc_types.append("Park") # 关键语义
                true_status.append(0)    # 真实状态是正常的
                acc_shock.append(0)

        elif scenario_type == "SCENARIO_2_CRITICAL_FALL":
            # === 剧本 2: 浴室跌倒危机 (Bathroom) ===
            # 特征：浴室 + 冲击 + 血氧下降 -> 极度危险
            for t in range(steps):
                if t < 60:
                    # 正常洗澡
                    hr_data.append(85 + np.random.normal(0, 3))
                    spo2_data.append(97 + np.random.normal(0, 1))
                    acc_shock.append(0)
                    status = 0
                else:
                    # t=60 跌倒
                    hr_data.append(120 + np.random.normal(0, 10)) # 疼痛导致心率升
                    spo2_data.append(88 + np.random.normal(0, 2)) # 呼吸困难，血氧降
                    acc_shock.append(1 if t == 60 else 0)         # 瞬间冲击
                    status = 1
                
                temp_data.append(35.0) # 浴室高温
                loc_types.append("Bathroom")
                true_status.append(status)

        elif scenario_type == "SCENARIO_3_PRIVACY_TRADE":
            # === 剧本 3: 隐私博弈 (Bedroom) ===
            # 特征：心率波动，需要志愿者介入。用于演示调节 K 值的影响。
            for t in range(steps):
                # 心律不齐
                hr_data.append(75 + np.random.normal(0, 15)) 
                spo2_data.append(96 + np.random.normal(0, 1))
                temp_data.append(25.0)
                loc_types.append("Bedroom")
                
                # 真实确实有风险，看志愿者能否发现
                true_status.append(1) 
                acc_shock.append(0)

        return (np.array(hr_data), np.array(spo2_data), np.array(temp_data), 
                loc_types, np.array(true_status), np.array(acc_shock))

    def generate_crowd_reports(self, true_status_code, k_val):
        """
        模拟志愿者反馈。
        关键逻辑：K 值越大(隐私越强)，位置越模糊，志愿者误判率越高，响应越慢。
        """
        labels = []
        status_map = {0: "Normal", 1: "Risk"}
        
        # K值对准确率的惩罚 (K越大，志愿者越看不清，准确率下降)
        # K=1 -> acc=0.95; K=20 -> acc=0.6
        accuracy = max(0.6, 0.95 - (k_val * 0.015))
        
        for _ in range(5):
            if random.random() < accuracy:
                report_code = true_status_code
            else:
                report_code = 1 - true_status_code # 误判
            labels.append(status_map[report_code])
        return labels