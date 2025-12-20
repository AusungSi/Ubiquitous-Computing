import numpy as np

class TruthDiscovery:
    """
    2.2 数据清洗层：基于 KL 散度的真值发现
    """
    def __init__(self, sensitivity=1.0):
        self.lambda_param = sensitivity
        self.states = ["Normal", "Risk", "Fall"] # 状态空间

    def _normalize(self, dist):
        total = sum(dist)
        if total == 0: return [1/3, 1/3, 1/3]
        return [x/total for x in dist]

    def sensor_to_distribution(self, value):
        """
        D_sensor -> P(x)
        简单的规则映射：心率 > 100 或 < 50 视为高风险
        """
        if 50 <= value <= 100:
            # 正常概率高
            return [0.8, 0.15, 0.05]
        else:
            # 风险概率高
            return [0.2, 0.5, 0.3]

    def labels_to_distribution(self, labels):
        """
        D_crowd -> Q(x)
        将自然语言标签统计为概率分布
        """
        counts = {s: 0 for s in self.states}
        for l in labels:
            if l in counts: counts[l] += 1
        
        # Add-one smoothing (拉普拉斯平滑)
        raw_dist = [counts[s] + 0.1 for s in self.states]
        return self._normalize(raw_dist)

    def compute_confidence(self, P, Q):
        """
        计算 KL 散度与置信度 Q_val
        """
        epsilon = 1e-9 # 防止 log(0)
        kl_value = 0
        for p_i, q_i in zip(P, Q):
            # D_KL(P||Q)
            kl_value += p_i * np.log((p_i + epsilon) / (q_i + epsilon))
        
        # 置信度映射函数
        q_val = 1.0 / (1.0 + self.lambda_param * kl_value)
        return kl_value, q_val