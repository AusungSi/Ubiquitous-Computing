# ==========================================
# 系统全局配置文件
# ==========================================

# 1. 仿真设置
SIMULATION_DURATION = 100  # 仿真总时长 (单位：步长)
WINDOW_SIZE = 10           # 滑动窗口大小

# 2. 评分模型参数 (System Model)
BASE_HEALTH_SCORE = 85.0   # 基础健康分 (S_base)
ALPHA = 0.5                # 传感器冲击系数 (预留)
BETA = 20.0                # 群智反馈权重
DELTA = 15.0               # 熵值惩罚系数

# 3. 算法阈值
KL_SENSITIVITY = 2.0       # KL散度敏感系数 (Lambda)
ENTROPY_THRESHOLD = 1.8    # 健康熵阈值 (H_th)

# 4. 迟滞比较器阈值 (Hysteresis)
LEVEL_UP_THRESHOLD = 60.0  # 降级阈值 (L3 -> L4, 分数过低)
LEVEL_DOWN_THRESHOLD = 65.0 # 升级阈值 (L4 -> L3, 分数恢复)

# 5. 隐私参数
K_ANONYMITY_VAL = 5        # K-匿名参数