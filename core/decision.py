class CareDecision:
    """
    ACAS 2.0 决策层
    特性：上下文感知 (Context-Aware) 的自适应线性评分模型
    """
    def __init__(self, base_score=85):
        self.base_score = base_score
        self.current_level = "L3"

    def calculate_total_score(self, q_val, entropy_penalty, shock_signal, spo2_val, location):
        """
        增强版线性公式：
        H_score = S_base - (w1*Shock) - (w2*Entropy) - (w3*Crowd) - (w4*SpO2_Loss)
        其中 w 参数根据 location 动态调整
        """
        # 1. 默认权重
        w_shock = 20.0
        w_entropy = 1.0 # entropy_penalty 内部已经乘过系数，这里保持1
        w_crowd = 15.0  # 基于置信度的扣分
        
        # 2. 上下文感知：权重自适应调整 (Context Adaptation)
        if location == "Park":
            # 场景：在公园运动
            # 策略：调低熵的敏感度（允许心率波动），忽略轻微冲击
            w_entropy = 0.3 
            w_shock = 10.0 
        
        elif location == "Bathroom":
            # 场景：在浴室
            # 策略：跌倒极其危险，大幅提升冲击权重
            w_shock = 40.0 
            
        # 3. 计算各分项扣分
        loss_shock = w_shock * shock_signal
        loss_entropy = w_entropy * entropy_penalty
        loss_crowd = w_crowd * (1.0 - q_val) # 置信度越低(风险越大)，扣分越多
        
        # 新增：血氧扣分 (非线性急剧扣分)
        loss_spo2 = 0
        if spo2_val < 95:
            loss_spo2 = (95 - spo2_val) * 2.5 # 每低1%扣2.5分
            
        # 4. 总分计算
        total_loss = loss_shock + loss_entropy + loss_crowd + loss_spo2
        score = self.base_score - total_loss
        
        return max(0, min(100, score))

    def apply_hysteresis(self, score):
        # 迟滞比较器保持不变
        if self.current_level == "L3":
            if score < 60: self.current_level = "L4"
        elif self.current_level == "L4":
            if score > 65: self.current_level = "L3"
        return self.current_level