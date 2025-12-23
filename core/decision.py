# core/decision.py
from config import BASE_SCORE, CONTEXT_WEIGHTS, HYSTERESIS_UP, HYSTERESIS_DOWN, VITAL_RANGES

class CareDecision:
    def __init__(self):
        self.current_level = "L3"
        
    def evaluate(self, state, trust_conf, entropy_penalty):
        # 1. 获取基础权重
        w = CONTEXT_WEIGHTS.get(state.location, CONTEXT_WEIGHTS["Bedroom"])
        
        # 2. 计算各维度罚分 (Loss Calculation)
        
        # [A] 冲击与熵 (原有)
        loss_shock = w["w_shock"] * state.shock
        loss_entropy = entropy_penalty * w["w_entropy"]
        
        # [B] 群智 (原有)
        loss_crowd = w["w_crowd"] * (1.0 - trust_conf)
        
        # [C] 关键生理指标罚分 (新增)
        loss_vital = 0.0
        
        # C1. 血氧 (低于95开始扣分，低于90重罚)
        if state.spo2 < VITAL_RANGES["spo2_min"]:
            loss_vital += (VITAL_RANGES["spo2_min"] - state.spo2) * 3.0
            
        # C2. 血压 (非线性: 仅针对高危的高压>160 或 低压<90/60)
        # 休克判定 (高压 < 90)
        if state.bp_sys < VITAL_RANGES["bp_sys_min"]: 
            loss_vital += (VITAL_RANGES["bp_sys_min"] - state.bp_sys) * 2.0
        # 高血压危象 (高压 > 160)
        elif state.bp_sys > 160: 
            loss_vital += (state.bp_sys - 160) * 1.0
            
        # C3. 皮肤电 (GSR) - 疼痛/压力指示器
        # 只有在 GSR 显著高于基线时扣分
        if state.gsr > VITAL_RANGES["gsr_baseline"] * 2:
            loss_vital += (state.gsr - VITAL_RANGES["gsr_baseline"]) * 1.5
            
        # C4. 体温 (发烧仅轻微扣分，除非极高)
        if state.temp > 38.0:
            loss_vital += (state.temp - 38.0) * 5.0
            
        # 3. 总分
        total_loss = loss_shock + loss_entropy + loss_crowd + loss_vital
        score = max(0, min(100, state.base_score - total_loss))
        
        # 4. 迟滞比较器状态机
        old_level = self.current_level
        if self.current_level == "L3":
            if score < HYSTERESIS_DOWN: self.current_level = "L4"
        elif self.current_level == "L4":
            if score > HYSTERESIS_UP: self.current_level = "L3"
            
        return score, self.current_level, (old_level != self.current_level)