ACAS-Sim/
├── core/                   # 核心算法层 (对应技术方案第2章)
│   ├── __init__.py
│   ├── privacy.py          # 2.1 隐私保护 (K-Anonymity)
│   ├── truth_discovery.py  # 2.2 真值发现 (KL Divergence)
│   ├── stability.py        # 2.3 稳定性评估 (Entropy)
│   └── decision.py         # 2.4 决策与迟滞比较 (Hysteresis)
├── simulation/             # 数据生成与模拟层 (对应技术方案第1章)
│   ├── __init__.py
│   ├── generator.py        # 生成传感器数据(D_sensor)、志愿者数据(D_crowd)
│   └── actors.py           # 定义 Elderly, Volunteer 类
├── utils/                  # 工具类
│   ├── visualization.py    # 绘图模块 (为报告生成图片)
│   └── metrics.py          # 计算准确率、灵敏度
├── main.py                 # 程序入口 (运行仿真实验)
├── config.py               # 配置文件 (阈值、权重系数)
├── app.py
└── requirements.txt        # 依赖库