class Elderly:
    def __init__(self, id, chronic_disease):
        self.id = id
        self.disease = chronic_disease
        self.base_score = self._get_base_score()
    
    def _get_base_score(self):
        # 模拟医疗知识图谱 Base(u)
        mapping = {"Hypertension": 85, "Diabetes": 80}
        return mapping.get(self.disease, 90)

class Volunteer:
    def __init__(self, id, reliability):
        self.id = id
        self.reliability = reliability # 0.0 - 1.0