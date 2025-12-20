import matplotlib.pyplot as plt
import os

class Visualizer:
    def __init__(self):
        # 设置绘图风格
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except:
            plt.style.use('ggplot')

    def plot_dashboard(self, log):
        """
        绘制论文/报告所需的三张关键图表
        """
        time = log['time']
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        
        # Plot 1: Sensor Data & Entropy (展示对隐蔽风险的捕捉)
        ax1.plot(time, log['hr'], color='#1f77b4', label='Heart Rate (Sensor)', alpha=0.7)
        ax1.set_ylabel('Heart Rate (bpm)')
        ax1.set_title('A. 4D Perception: Temporal Sensor Data vs. Information Entropy')
        ax1.legend(loc='upper left')
        
        ax1_twin = ax1.twinx()
        ax1_twin.plot(time, log['entropy'], color='#ff7f0e', label='Shannon Entropy', linewidth=2)
        ax1_twin.fill_between(time, 0, log['entropy'], color='#ff7f0e', alpha=0.1)
        ax1_twin.set_ylabel('Entropy (Bits)')
        ax1_twin.legend(loc='upper right')

        # Plot 2: Health Score & Thresholds (展示评分逻辑)
        ax2.plot(time, log['score'], color='#2ca02c', label='Health Score ($H_{score}$)', linewidth=2)
        ax2.axhline(y=60, color='red', linestyle='--', label='Emergency Threshold (<60)')
        ax2.set_ylabel('Score (0-100)')
        ax2.set_ylim(30, 100)
        ax2.set_title('B. Dynamic Assessment: Score Degradation under Risk')
        ax2.legend()

        # Plot 3: Decision Level (展示迟滞比较器效果)
        # 将 0/1 转换为 L3/L4 标签
        ax3.step(time, log['level'], where='post', color='#d62728', linewidth=2)
        ax3.set_yticks([0, 1])
        ax3.set_yticklabels(['L3 (Monitor)', 'L4 (Emergency)'])
        ax3.set_ylabel('Care Level')
        ax3.set_xlabel('Simulation Time Step')
        ax3.set_title('C. Decision Making: Hysteresis Comparator Output')
        ax3.fill_between(time, log['level'], color='#d62728', alpha=0.2)

        plt.tight_layout()
        
        # 保存图片用于报告
        save_path = 'simulation_result.png'
        plt.savefig(save_path, dpi=300)
        print(f"Figure saved to {os.path.abspath(save_path)}")
        plt.show()