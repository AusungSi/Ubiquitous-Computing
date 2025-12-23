# core/stability.py
import numpy as np
from collections import deque
from config import ENTROPY_THRESHOLD, ENTROPY_PENALTY_COEF, WINDOW_SIZE

class StabilityAnalyzer:
    """
    基于信息熵的时序稳定性分析
    对应文档：2.4 基于信息熵的时序稳定性分析
    """
    def __init__(self, threshold=ENTROPY_THRESHOLD):
        self.window = deque(maxlen=WINDOW_SIZE)
        self.threshold = threshold

    def update_and_calculate(self, new_value):
        """
        更新窗口并计算熵值
        """
        self.window.append(new_value)
        
        if len(self.window) < 5:
            return 0.0, 0.0 # 数据不足，不计算
            
        # 1. 动态离散化 (Dynamic Binning)
        # 捕捉微小波动，而不是使用固定的全局 bin
        d_min, d_max = min(self.window), max(self.window)
        if d_max == d_min: return 0.0, 0.0
        
        # 将数据分为 5 个区间计算分布
        hist, _ = np.histogram(self.window, bins=5, density=True)
        probs = hist / np.sum(hist)
        probs = probs[probs > 0] # 去除 0 值
        
        # 2. 香农熵计算
        entropy = -np.sum(probs * np.log2(probs))
        
        # 3. 罚分计算
        excess = max(0, entropy - self.threshold)
        penalty = excess * ENTROPY_PENALTY_COEF
        
        return entropy, penalty