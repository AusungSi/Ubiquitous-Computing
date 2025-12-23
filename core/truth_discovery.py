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
        # 简单的高斯模拟逻辑
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
        
        # 拉普拉斯平滑 (Add-one smoothing) 防止概率为0
        raw = np.array([counts[s] + 0.1 for s in self.states])
        return raw / np.sum(raw)

    def compute_trust_score(self, sensor_val, crowd_labels):
        """
        计算 KL 散度及最终置信度
        """
        P = self._sensor_to_prob(sensor_val)
        Q = self._crowd_to_prob(crowd_labels)
        
        # 计算 KL 散度: D_KL(P||Q)
        epsilon = 1e-9
        kl_value = np.sum(P * np.log((P + epsilon) / (Q + epsilon)))
        
        # 映射公式: Conf = 1 / (1 + lambda * KL)
        confidence = 1.0 / (1.0 + self.lambda_param * kl_value)
        
        return confidence, kl_value