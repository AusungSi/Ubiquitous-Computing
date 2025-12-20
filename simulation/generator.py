import numpy as np
import random

class DataGenerator:
    """
    数据生成器：D_sensor, D_crowd
    """
    def __init__(self, duration):
        self.duration = duration

    def generate_heart_rate_stream(self, risk_period=(40, 70)):
        """
        生成心率时序数据。
        risk_period: (start, end) 区间内模拟心律失常
        """
        data = []
        for t in range(self.duration):
            base = 75
            
            if risk_period[0] <= t <= risk_period[1]:
                # 异常模式：高频波动，熵值高
                noise = np.random.normal(0, 15)
                trend = 5 * np.sin(t/2.0)
            else:
                # 正常模式
                noise = np.random.normal(0, 3)
                trend = 0
                
            val = base + trend + noise
            data.append(val)
        return np.array(data)

    def generate_crowd_data(self, t, true_status_code):
        """
        模拟 5 个志愿者的反馈
        true_status_code: 0=Normal, 1=Risk
        """
        labels = []
        status_map = {0: "Normal", 1: "Risk", 2: "Fall"}
        
        for _ in range(5):
            # 模拟志愿者准确率 80%
            if random.random() < 0.8:
                report_code = true_status_code
            else:
                # 20% 概率瞎报
                report_code = random.choice([0, 1, 2])
            
            labels.append(status_map[report_code])
        return labels