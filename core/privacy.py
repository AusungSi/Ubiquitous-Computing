import numpy as np

class PrivacyModule:
    """
    2.1 隐私保护层：基于位置的 K-匿名
    """
    def __init__(self, k=5):
        self.k = k

    def generalize_location(self, exact_loc, active_user_pool_size=100):
        """
        模拟 K-匿名算法。
        实际上应该查询数据库寻找最近的k-1个用户，
        这里为了仿真，模拟生成覆盖k个用户的矩形区域面积。
        """
        # 模拟周围 k-1 个随机用户的位置
        sigma = 0.05 # 密度分布参数
        other_users_x = np.random.normal(exact_loc[0], sigma, self.k - 1)
        other_users_y = np.random.normal(exact_loc[1], sigma, self.k - 1)
        
        all_x = np.append(other_users_x, exact_loc[0])
        all_y = np.append(other_users_y, exact_loc[1])
        
        # 计算最小覆盖矩形面积
        width = np.max(all_x) - np.min(all_x)
        height = np.max(all_y) - np.min(all_y)
        area = width * height
        
        return area