# core/truth_discovery.py
import numpy as np
from config import KL_SENSITIVITY

class TruthDiscovery:
    """
    实现基于 KL 散度的跨模态真值发现
    对应文档：2.2 多源异构数据的真值发现
    """
    def __init__(self, sensitivity=KL_SENSITIVITY):
        self.lambda_param = sensitivity
        self.states = ["Normal", "Risk", "Fall"] # 状态空间

    def _sensor_to_prob(self, hr_val):
        """
        将连续传感器数值映射为概率分布 P(x)
        逻辑：利用高斯分布思想，偏离正常值越远，风险概率越高
        """
        if 60 <= hr_val <= 100:
            return np.array([0.90, 0.08, 0.02]) # 正常
        elif 50 < hr_val < 60 or 100 < hr_val < 120:
            return np.array([0.30, 0.60, 0.10]) # 亚健康
        else:
            return np.array([0.05, 0.35, 0.60]) # 极度危险/跌倒倾向

    def _crowd_to_prob(self, labels):
        """
        将离散文本标签映射为概率分布 Q(x)
        """
        counts = {s: 0 for s in self.states}
        for l in labels:
            if l in counts: counts[l] += 1
        
        # 拉普拉斯平滑
        raw = np.array([counts[s] + 0.1 for s in self.states])
        return raw / np.sum(raw)

    def compute_trust_score(self, sensor_val, crowd_labels):
        """
        [旧接口] 使用标签列表计算
        """
        P = self._sensor_to_prob(sensor_val)
        Q = self._crowd_to_prob(crowd_labels)
        
        epsilon = 1e-9
        kl_value = np.sum(P * np.log((P + epsilon) / (Q + epsilon)))
        confidence = 1.0 / (1.0 + self.lambda_param * kl_value)
        
        return confidence, kl_value

    # ==========================================
    # 👇 必须补上这个新方法 👇
    # ==========================================
    def compute_trust_with_distribution(self, sensor_val, Q_distribution):
        """
        [新接口] 直接使用 BERT/NLP 输出的概率分布 Q 计算 KL 散度
        """
        # 1. 获取传感器分布 P
        P = self._sensor_to_prob(sensor_val)
        
        # 2. 获取传入的 NLP 分布 Q
        Q = Q_distribution
        
        # 3. 计算 KL 散度
        epsilon = 1e-9
        kl_value = np.sum(P * np.log((P + epsilon) / (Q + epsilon)))
        
        # 4. 计算置信度
        confidence = 1.0 / (1.0 + self.lambda_param * kl_value)
        
        return confidence, kl_value