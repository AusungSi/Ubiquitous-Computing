# core/privacy.py
import numpy as np
from config import BASE_BLUR_RADIUS

class PrivacyModule:
    """
    实现基于位置的 K-匿名算法
    对应文档：3.2节（二）基于K-匿名的身份隐私脱敏需求
    """
    def __init__(self, k=5):
        self.k = k

    def get_k_anonymity_box(self, lat, lon):
        """
        输入真实坐标，输出覆盖K个潜在用户的矩形区域
        """
        # 1. 计算泛化半径 (K值越大，半径越大)
        radius = BASE_BLUR_RADIUS * self.k
        
        # 2. 引入随机偏移 (防止矩形中心即为真实坐标)
        noise_lat = np.random.uniform(-radius/2, radius/2)
        noise_lon = np.random.uniform(-radius/2, radius/2)
        
        center_lat = lat + noise_lat
        center_lon = lon + noise_lon
        
        # 3. 构建矩形坐标 [min_lon, min_lat, max_lon, max_lat]
        return {
            "bbox": [
                center_lon - radius,
                center_lat - radius,
                center_lon + radius,
                center_lat + radius
            ],
            "privacy_cost": radius * 1e5  # 模拟隐私损失指标
        }