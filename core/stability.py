import numpy as np

class StabilityAnalyzer:
    """
    2.3 状态评估层：基于信息熵的稳定性量化
    """
    def __init__(self, threshold=1.5, delta=10):
        self.h_th = threshold
        self.delta = delta

    def compute_shannon_entropy(self, data_window):
        """
        计算时间窗口内的香农熵
        """
        if len(data_window) < 2: 
            return 0.0
        
        # 1. 离散化 (Discretization)
        # 将连续的心率值映射到直方图 bin 中
        hist, _ = np.histogram(data_window, bins=10, range=(40, 140), density=True)
        
        # 2. 计算熵
        # H(Z) = - sum p(z) log2 p(z)
        hist = hist[hist > 0] # 移除0值
        entropy = -np.sum(hist * np.log2(hist))
        
        return entropy

    def calculate_penalty(self, entropy):
        """
        计算稳定性罚分
        """
        excess_entropy = max(0, entropy - self.h_th)
        return self.delta * excess_entropy