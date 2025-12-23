# config.py

# --- 仿真设置 ---
SIMULATION_FREQ = 1.0
WINDOW_SIZE = 10

# --- 2.1 隐私参数 ---
DEFAULT_K = 5
BASE_BLUR_RADIUS = 0.0001

# --- 2.2 真值发现参数 ---
KL_SENSITIVITY = 2.0
DEFAULT_TRUST = 0.5

# --- 2.3 稳定性参数 ---
ENTROPY_THRESHOLD = 1.5
ENTROPY_PENALTY_COEF = 15.0

# --- 2.4 决策模型参数 (2.0 全维升级版) ---
BASE_SCORE = 95.0       # 基础分提高，给扣分留出空间
HYSTERESIS_UP = 75.0    # 严格的恢复标准
HYSTERESIS_DOWN = 65.0  # 报警触发线

# 上下文权重 (Context-Aware Weights)
# 结构: [Shock, Entropy, Crowd] (传感器单独计算罚分)
CONTEXT_WEIGHTS = {
    "Bedroom":  {"w_shock": 20.0, "w_entropy": 1.0, "w_crowd": 20.0},
    "Bathroom": {"w_shock": 50.0, "w_entropy": 1.2, "w_crowd": 15.0}, # 浴室跌倒权重极高
    "LivingRoom": {"w_shock": 30.0, "w_entropy": 0.8, "w_crowd": 20.0},
}

# 生理指标正常范围 (用于计算罚分)
VITAL_RANGES = {
    "spo2_min": 95.0,
    "bp_sys_max": 140.0, "bp_sys_min": 90.0,
    "bp_dia_max": 90.0,  "bp_dia_min": 60.0,
    "temp_max": 37.5,    "temp_min": 36.0,
    "rr_max": 20.0,      "rr_min": 12.0,
    "gsr_baseline": 5.0  # 皮肤电基线
}