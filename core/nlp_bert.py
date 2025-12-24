# core/nlp_bert.py
import numpy as np
from transformers import pipeline
import streamlit as st

class BertSemanticAnalyzer:
    """
    基于 Transformer (BERT/BART) 的语义认知引擎
    利用 Zero-Shot Classification 实现文本到概率分布的映射
    """
    def __init__(self):
        # 使用 Streamlit 缓存加载模型，防止每次刷新页面重载 (模型约 400MB-1GB)
        self.classifier = self._load_model()
        
        # 定义标签空间
        self.crowd_labels = ["Normal", "Risk", "Fall"]
        self.self_labels = ["Urgent", "Pain", "Safe"]

    @st.cache_resource
    def _load_model(_self):
        # 使用轻量级的高效模型 (distilbart-mnli) 用于零样本分类
        # 第一次运行会自动下载模型
        print("Loading BERT/BART Model...")
        return pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1",use_safetensors=True,)

    def predict_crowd_distribution(self, text):
        """
        [BERT] 输入志愿者文本 -> 输出 Q(x) 概率分布
        """
        if not text:
            # 默认不可知分布
            return np.array([0.33, 0.33, 0.34])
            
        # 让模型预测该文本属于 Normal, Risk, Fall 的概率
        result = self.classifier(text, self.crowd_labels, multi_label=False)
        
        # result['scores'] 是按照 result['labels'] 顺序排列的
        # 我们需要将其对齐到固定的 [Normal, Risk, Fall] 顺序
        label_score_map = {l: s for l, s in zip(result['labels'], result['scores'])}
        
        # 构建有序分布向量 Q(x)
        distribution = np.array([
            label_score_map.get("Normal", 0.0),
            label_score_map.get("Risk", 0.0),
            label_score_map.get("Fall", 0.0)
        ])
        
        # 归一化 (防止精度误差)
        return distribution / np.sum(distribution)

    def predict_self_score(self, text):
        """
        [BERT] 输入老人语音 -> 预测严重程度罚分 & 中断信号
        """
        if not text:
            return 0.0, False
            
        # 预测文本的紧急程度
        result = self.classifier(text, self.self_labels, multi_label=True)
        scores = {l: s for l, s in zip(result['labels'], result['scores'])}
        
        # 提取特征分数
        urgent_score = scores.get("Urgent", 0.0) # 0.0 - 1.0
        pain_score = scores.get("Pain", 0.0)     # 0.0 - 1.0
        
        # 逻辑：
        # 1. 计算罚分：基于痛苦和紧急程度 (BERT score * 系数)
        penalty = (urgent_score * 40.0) + (pain_score * 30.0)
        
        # 2. 判断中断：如果 "Urgent" 概率 > 0.8，触发 L4 中断
        is_interrupt = urgent_score > 0.85
        
        return penalty, is_interrupt