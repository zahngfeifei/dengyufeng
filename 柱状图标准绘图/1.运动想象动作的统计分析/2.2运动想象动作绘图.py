import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置字体为 New Roman
plt.rcParams['font.family'] = 'Times New Roman'  # 设置字体为 New Roman
plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示
class MotorImageryAnalyzer:
    def __init__(self, csv_file):
        # 初始化类，读取CSV文件
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)  # 读取数据
        self.action_counts = self.df['运动想象动作'].value_counts()  # 统计运动想象动作出现次数
        # 定义动作名称映射
        self.top_actions_names = {
            '左手运动想象-右手运动想象': 'LH-RH',
            '右手运动想象-右脚运动想象': 'RH-RF',
            '右手运动想象-脚部运动想象': 'RH-F',
            '左手运动想象-右脚运动想象': 'LH-RF',
            '左手运动想象-脚部运动想象': 'LH-F'
        }

    def _get_top_actions(self):
        # 获取前五个动作及其出现次数，并将其他动作合并
        top_actions = self.action_counts.head(5)  # 获取前五个动作
        other_count = self.action_counts[5:].sum()  # 统计其他动作的总数
        top_actions.index = top_actions.index.map(self.top_actions_names)  # 重命名
        other_series = pd.Series({'Other': other_count})  # 创建“其他”系列
        return pd.concat([top_actions, other_series])  # 合并数据

    def plot_action_counts(self, output_image):
        # 绘制运动想象动作出现次数的柱状图
        all_actions = self._get_top_actions()  # 获取动作数据

        plt.figure(figsize=(10, 6))  # 设置图形尺寸

        # 定义颜色列表，确保与动作数量一致
        colors = ['skyblue', 'lightgreen', 'salmon', 'gold', 'lightcoral', 'lightblue']

        bars = all_actions.plot(kind='bar', color=colors[:len(all_actions)])  # 绘制柱状图

        plt.title('Frequency of Motor Imagery Actions', fontsize=16, weight='bold')  # 设置标题
        plt.xlabel('Motor Imagery Actions', fontsize=14)  # 设置X轴标签
        plt.ylabel('Count', fontsize=14)  # 设置Y轴标签
        plt.xticks(rotation=45, ha='right', fontsize=12)  # 设置X轴刻度旋转和字体

        # 在每个柱上方显示计数
        for index, value in enumerate(all_actions):
            plt.text(index, value, str(value), ha='center', va='bottom', fontsize=12)

        # 添加图例，说明每种动作对应的颜色
        legend_labels = [
            'Left Hand - Right Hand',
            'Right Hand - Right Foot',
            'Right Hand - Foot',
            'Left Hand - Right Foot',
            'Left Hand - Foot',
            'Other'
        ]
        custom_legend = [plt.Line2D([0], [0], marker='o', color='w', label=legend_labels[i],
                                    markerfacecolor=colors[i], markersize=10) for i in range(len(legend_labels))]
        plt.legend(handles=custom_legend, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=12,
                   markerscale=1.5)  # 调整图例位置和大小

        plt.tight_layout()  # 调整布局
        plt.savefig(output_image)  # 保存图像
        plt.close()  # 关闭图形
        print(f"出现次数统计图已保存到：{output_image}")  # 输出保存路径


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示

# 使用示例
if __name__ == "__main__":
    csv_file = r'C:\Users\pc\Desktop\cjh 10.8\数据预处理版本二分类数据信息.csv'
    output_image = r'C:\Users\pc\Desktop\cjh 10.8\1.运动想象动作的统计分析\10运动想象动作_出现次数统计.png'

    analyzer = MotorImageryAnalyzer(csv_file)  # 创建分析器实例
    analyzer.plot_action_counts(output_image)  # 绘制并保存图像
