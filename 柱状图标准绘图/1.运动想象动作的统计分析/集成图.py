import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 读取CSV文件
csv_file = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\数据预处理版本二分类数据信息.csv'
df = pd.read_csv(csv_file)

# 统计每种运动想象动作的出现次数
action_counts = df['运动想象动作'].value_counts()

# 统计“运动想象动作”列中的唯一值数量
unique_action_count = df['运动想象动作'].nunique()

# 找出最常见的运动想象动作
most_common_action = df['运动想象动作'].mode()[0]

# 创建一个包含三张子图的图表
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# 1. 绘制出现次数的柱状图
action_counts.plot(kind='bar', color='skyblue', ax=axes[0])
axes[0].set_title('运动想象动作的出现次数统计', fontsize=16)
axes[0].set_xlabel('运动想象动作', fontsize=14)
axes[0].set_ylabel('出现次数', fontsize=14)

# 2. 绘制唯一值数量图
axes[1].text(0.5, 0.5, f'唯一运动想象动作种类数量: {unique_action_count}',
             fontsize=16, ha='center', va='center', bbox=dict(facecolor='orange', alpha=0.5))
axes[1].set_title('唯一运动想象动作种类数量', fontsize=16)
axes[1].axis('off')  # 关闭坐标轴

# 3. 绘制最常见的运动想象动作图
axes[2].text(0.5, 0.5, f'最常见的运动想象动作: {most_common_action}',
             fontsize=16, ha='center', va='center', bbox=dict(facecolor='lightgreen', alpha=0.5))
axes[2].set_title('最常见的运动想象动作', fontsize=16)
axes[2].axis('off')  # 关闭坐标轴

# 保存集成图
output_image = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\1.运动想象动作的统计分析\运动想象动作_集成图.png'
plt.tight_layout()
plt.savefig(output_image)
plt.close()  # 关闭图表

print(f"集成图已保存到指定路径：\n{output_image}")