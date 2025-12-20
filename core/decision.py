from config import *

class CareDecision:
    """
    2.4 决策层：综合评分与迟滞比较器
    """
    def __init__(self, base_score=85):
        self.base_score = base_score
        self.current_level = "L3" # 初始状态: 关注级

    def calculate_total_score(self, q_val, penalty):
        """
        H_score = S_base - Beta * (1 - Q_val) - Penalty
        注：这里简化了 Risk(Tag) 项，假设风险越高 Q_val 导致的分数扣除越多
        """
        # 如果 Q_val 很低（即 P 和 Q 差异大，或者 Q 指向风险），扣分
        # 这里的逻辑主要体现：不确定性越高，分数越低；或者熵越高，分数越低
        
        # 修正逻辑：
        # 如果 Q_val 接近 1 (一致)，扣分少？不对。
        # 应该是：如果传感器显示风险(P)，且志愿者确认风险(Q)，则 Q_val 高，但因为是风险，要扣分。
        # 此处简化仿真逻辑：仅利用熵罚分和置信度权重。
        
        trust_loss = BETA * (1.0 - q_val) # 置信度越低，扣分越多（不确定性惩罚）
        
        score = self.base_score - trust_loss - penalty
        return max(0, min(100, score))

    def apply_hysteresis(self, score):
        """
        双阈值迟滞比较器
        """
        if self.current_level == "L3":
            # 只有分数极低时才升级到 L4 (避免误报)
            if score < LEVEL_UP_THRESHOLD:
                self.current_level = "L4"
                
        elif self.current_level == "L4":
            # 只有分数显著回升时才降级回 L3 (避免反复震荡)
            if score > LEVEL_DOWN_THRESHOLD:
                self.current_level = "L3"
                
        return self.current_level