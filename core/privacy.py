import numpy as np

class PrivacyModule:
    """
    2.1 隐私保护层：K-匿名可视化支持
    """
    def __init__(self, k=5):
        self.k = k

    def get_k_anonymity_box(self, center_lat, center_lon):
        """
        根据 K 值生成覆盖 K 个潜在用户的矩形框坐标
        K 越大，矩形框越大 (模拟位置模糊化)
        返回: [min_lon, min_lat, max_lon, max_lat]
        """
        # 简单模拟：K值每增加1，模糊半径增加 0.0005 度 (约50米)
        base_radius = 0.0002
        radius = base_radius + (self.k * 0.0002)
        
        # 加入一点随机偏移，让框不总是以老人为中心（更真实的匿名）
        offset_lat = np.random.uniform(-radius/2, radius/2)
        offset_lon = np.random.uniform(-radius/2, radius/2)
        
        sim_center_lat = center_lat + offset_lat
        sim_center_lon = center_lon + offset_lon
        
        return [
            sim_center_lon - radius, # min_lon
            sim_center_lat - radius, # min_lat
            sim_center_lon + radius, # max_lon
            sim_center_lat + radius  # max_lat
        ]