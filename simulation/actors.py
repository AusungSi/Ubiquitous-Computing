# simulation/actors.py

class HolographicState:
    """
    四维全息感知数据模型 (2.0 Enhanced)
    对应文档：摘要及1.3节
    """
    def __init__(self, base_score, hr, spo2, bp_sys, bp_dia, temp, resp_rate, gsr, location, crowd_labels, shock):
        # --- 1. Profile ---
        self.base_score = base_score
        
        # --- 2. Sensor (Physiological Multi-modal) ---
        self.hr = hr                  # 心率 (bpm)
        self.spo2 = spo2              # 血氧 (%)
        self.bp_sys = bp_sys          # 收缩压 (mmHg)
        self.bp_dia = bp_dia          # 舒张压 (mmHg)
        self.temp = temp              # 体温 (°C)
        self.resp_rate = resp_rate    # 呼吸率 (rpm)
        self.gsr = gsr                # 皮肤电 (μS) - 疼痛/压力指标
        
        # --- 2. Sensor (Context) ---
        self.location = location      # 环境语义
        
        # --- 3. Crowd ---
        self.crowd_labels = crowd_labels 
        
        # --- 4. Interrupt ---
        self.shock = shock            # 加速度冲击

class Elderly:
    """用户实体类"""
    def __init__(self, uid, name, chronic_diseases):
        self.uid = uid
        self.name = name
        self.diseases = chronic_diseases
        # 简单计算基准分
        self.base_score = 90 - (len(chronic_diseases) * 5)

class UserProfile:
    """
    用户健康画像 (权威基准 D_prof)
    """
    def __init__(self, name, age, condition, base_score_override=None):
        self.name = name
        self.age = age
        self.condition = condition # 健康/高血压/阿兹海默
        
        # 根据画像设定基准分 S_base
        if base_score_override:
            self.base_score = base_score_override
        else:
            if condition == "Healthy":
                self.base_score = 95.0
            elif condition == "Hypertension":
                self.base_score = 85.0 # 起评分低
            elif condition == "Alzheimer":
                self.base_score = 80.0
            else:
                self.base_score = 90.0