# 🛡️ ACAS-Sim: 面向移动群智感知的智慧社区养老自适应照护评估系统

> **Adaptive Care Assessment System (ACAS 2.0)**
> 基于普适计算 (Pervasive Computing) 与人机物融合的智慧养老数字孪生仿真平台。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow)](https://huggingface.co/)

## 📖 项目简介 (Introduction)

随着老龄化社会的加剧，独居老人的健康安全监测面临巨大挑战。传统的单一传感器监测往往存在误报率高、语义理解能力弱的问题。

**ACAS-Sim** 是一个集成了**多模态生理感知**、**AI 语义认知**与**动态隐私保护**的仿真系统。它构建了一个“人-机-物”融合的四维全息感知模型，旨在通过群智感知（Crowdsensing）技术解决多源异构数据的冲突处理与隐私泄露难题。

本系统不仅模拟了心率、血压、皮肤电等**全维生命体征**，还引入了 **BERT 模型** 处理非结构化的志愿者反馈与老人语音自述，实现了真正的认知智能。

## ✨ 核心特性 (Key Features)

### 1. 🧬 全维生命体征数字孪生
模拟真实的生理信号发生器，支持多种医学与生活场景：
- **基础指标**：心率 (HR)、血氧 (SpO2)、呼吸率 (RR)、体温 (Temp)。
- **高级指标**：**收缩压/舒张压 (BP)**（关联休克检测）、**皮肤电反应 (GSR)**（关联痛感与惊吓）。
- **情境模拟**：支持 `正常`、`心律失常`、`浴室跌倒`、`高强度运动`（抗误报测试）、`夜间低血糖`、`急性心梗` 等六大场景。

### 2. 🧠 BERT 驱动的语义认知 ($D_{crowd}$ & $D_{self}$)
告别死板的关键词匹配，利用 **Zero-Shot Classification (Transformer)** 实现真正的语义理解：
- **志愿者反馈**：将自然语言（如 "He is stumbling"）自动映射为风险概率分布 $Q(x)$。
- **老人自述**：对语音转写的文本进行紧急程度量化，动态计算罚分或触发高优中断。

### 3. 🛡️ 下一代隐私保护策略 (Privacy 2.0)
- **K-匿名位置泛化**：基于地理围栏的动态 K 值模糊。
- **任务导向的语义置换 (Semantic Transformation)**：
    - **L3 日常模式**：隐藏具体病名（如“糖尿病”），仅输出照护指令（如“需防低血糖”），实现信息零损失的同时保护隐私。
    - **L4 紧急模式**：基于 **Break-glass** 机制，生命优先，自动降级隐私保护以辅助急救。

### 4. ⚖️ 鲁棒的决策算法
- **真值发现**：基于 **KL 散度 (Kullback-Leibler Divergence)** 计算传感器分布 $P(x)$ 与志愿者分布 $Q(x)$ 的一致性，自动过滤虚假情报。
- **稳定性分析**：引入 **信息熵 (Shannon Entropy)** 监测生理时序数据的混乱度，敏锐捕捉亚健康波动。
- **迟滞决策**：双阈值状态机，有效防止因数据噪点导致的报警震荡。

## 🏗️ 系统架构 (Architecture)

本系统基于 **四维全息感知模型** 构建：

1.  **权威基准 ($D_{prof}$)**: 基于 EHR (电子健康档案) 的动态用户画像 (UserProfile)。
2.  **客观真值 ($D_{sensor}$)**: IoT 设备生成的多维概率分布。
3.  **主观语义 ($D_{crowd}$)**: BERT 解析的志愿者观测分布。
4.  **高优中断 ($D_{self}$)**: SOS 按键与 NLP 语音分析的最高优先级触发。

## 🚀 快速开始 (Getting Started)

### 环境要求
- Python 3.8+
- PyTorch (建议 GPU 版本，CPU 亦可)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone [https://github.com/your-username/ACAS-Sim.git](https://github.com/your-username/ACAS-Sim.git)
   cd ACAS-Sim
### 安装依赖

```bash
pip install -r requirements.txt
requirements.txt 内容参考: streamlit, pandas, numpy, plotly, pydeck, torch, transformers

运行系统
Bash

streamlit run app.py
⚠️ 注意事项 (Hugging Face 模型)
首次运行时，系统会自动下载 valhalla/distilbart-mnli-12-1 模型（约 1GB）。 如果遇到下载网络错误，请在终端设置国内镜像：

Linux / Mac

Bash

export HF_ENDPOINT=[https://hf-mirror.com](https://hf-mirror.com)
Windows PowerShell

PowerShell

$env:HF_ENDPOINT = "[https://hf-mirror.com](https://hf-mirror.com)"
📂 目录结构 (Directory Structure)
Plaintext

ACAS-Sim/
├── app.py                  # 系统入口 (Streamlit UI 主逻辑)
├── config.py               # 全局参数配置文件 (阈值、权重)
├── core/                   # 核心算法层
│   ├── decision.py         # 决策与迟滞比较器
│   ├── nlp_bert.py         # BERT 语义认知引擎
│   ├── privacy.py          # K-匿名与隐私语义置换
│   ├── stability.py        # 信息熵稳定性分析
│   └── truth_discovery.py  # KL 散度真值发现
├── simulation/             # 仿真层
│   ├── actors.py           # 数据模型 (UserProfile, HolographicState)
│   └── generator.py        # 多模态生理数据生成器
└── requirements.txt        # 依赖列表
📸 演示截图 (Screenshots)
<img width="1919" height="910" alt="Dashboard View" src="https://github.com/user-attachments/assets/f144313c-df69-499a-8584-1cc2c0c1f6fa" />


<img width="901" height="555" alt="Map View" src="https://github.com/user-attachments/assets/4b09a6be-3bfd-41d2-9059-ad01570fb1e7" />

🤝 贡献与致谢
本项目是普适计算课程设计成果。 核心算法参考了群智感知、差分隐私与情感计算领域的相关研究。

Author: [鲁贇涛]

Institution: Nanjing University of Aeronautics and Astronautics (NUAA)
