# core/privacy.py
import numpy as np
from config import BASE_BLUR_RADIUS

class PrivacyModule:
    """
    全栈隐私保护模块 (Privacy 2.0)
    特性：
    1. 属性泛化 (Attribute Generalization): 年龄、病史脱敏
    2. 位置 K-匿名 (Location K-Anonymity): 动态地理围栏
    3. 动态博弈 (Break-glass): L3隐私优先 vs L4生命优先
    """
    def __init__(self, k=5):
        self.default_k = k
        
        # 定义疾病泛化树 (Generalization Hierarchy)
        # Level 0 (Key) -> Level 1 (Value)
        # 策略：保留临床大类，避免过度模糊导致无法针对性急救
        self.disease_hierarchy = {
            "Healthy":      "No Significant History",
            "Hypertension": "Cardiovascular (Circulatory)", # 高血压 -> 心血管(循环)
            "Arrhythmia":   "Cardiovascular (Heart Rhythm)",# 心律失常 -> 心血管(节律)
            "Diabetes":     "Endocrine (Metabolic)",        # 糖尿病 -> 内分泌(代谢)
            "Alzheimer":    "Neurological (Cognitive)",     # 阿兹海默 -> 神经(认知)
            "Infarction":   "Cardiovascular (Acute)"        # 心梗 -> 心血管(急性)
        }

    def apply_privacy_policy(self, user_profile, lat, lon, system_level="L3"):
        """
        核心方法：根据当前系统等级(L3/L4)动态应用隐私策略
        返回：脱敏后的数据字典 (Sanitized Profile)
        """
        
        # --- 策略决策逻辑 ---
        if system_level == "L4":
            # [场景B: 紧急救援] -> Break-glass 机制
            # 策略：生命优先。K值降为1，极低泛化，暴露精确位置和病史
            effective_k = 1
            show_precise_disease = True # 暴露 Level 0
            show_precise_age = True
            
        else:
            # [场景A: 日常监测] -> 隐私优先
            # 策略：K-匿名保护。K=default，泛化病史和年龄
            effective_k = self.default_k
            show_precise_disease = False # 暴露 Level 1
            show_precise_age = False
            
        # --- 1. 属性泛化 (Attribute Generalization) ---
        
        # [Age] 年龄泛化
        if show_precise_age:
            sanitized_age = str(user_profile.age)
        else:
            # 泛化为 5岁区间 (e.g., 72 -> "70-75")
            floor_age = (user_profile.age // 5) * 5
            sanitized_age = f"[{floor_age}-{floor_age + 5}]"
            
        # [Disease] 病史泛化
        raw_disease = user_profile.condition
        if show_precise_disease:
            sanitized_disease = raw_disease # Level 0
        else:
            # Level 1: 映射到大类，如果没有匹配则显示 "General Chronic"
            # 既保护了隐私(不知道是具体哪种病)，又保留了急救类别信息
            sanitized_disease = self.disease_hierarchy.get(raw_disease, "General Chronic Condition")
            
        # --- 2. 位置 K-匿名 (Location K-Anonymity) ---
        
        # 计算泛化半径
        # L4时 K=1，半径极小(精确)；L3时 K=5，半径大(模糊)
        radius = BASE_BLUR_RADIUS * effective_k
        
        # 引入随机噪声 (中心偏移)
        noise_lat = np.random.uniform(-radius/2, radius/2)
        noise_lon = np.random.uniform(-radius/2, radius/2)
        
        # 构建匿名框
        center_lat = lat + noise_lat
        center_lon = lon + noise_lon
        
        bbox = [
            center_lon - radius, center_lat - radius,
            center_lon + radius, center_lat + radius
        ]
        
        # --- 3. 输出脱敏数据包 ---
        sanitized_data = {
            "uid": self._mask_id(user_profile.name), # 姓名脱敏
            "age_group": sanitized_age,
            "condition_category": sanitized_disease,
            "k_level": effective_k,
            "bbox": bbox,
            "privacy_mode": "EMERGENCY (Break-glass)" if system_level == "L4" else "PROTECTED (K-Anon)"
        }
        
        return sanitized_data

    def get_k_anonymity_box(self, lat, lon):
        """
        [兼容旧接口] 仅计算位置框，用于单纯的地图绘图
        """
        radius = BASE_BLUR_RADIUS * self.default_k
        bbox = [
            lon - radius, lat - radius,
            lon + radius, lat + radius
        ]
        return {"bbox": bbox}

    def _mask_id(self, name):
        """简单姓名脱敏: 张三 -> 张**"""
        if len(name) > 0:
            return name[0] + "**"
        return "***"