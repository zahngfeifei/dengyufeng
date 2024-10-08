import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 读取CSV文件
csv_file = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\数据预处理版本二分类数据信息.csv'
df = pd.read_csv(csv_file)

# 统计每种特征提取方法的出现次数
method_counts = df['特征提取方法'].value_counts()

# 统计“特征提取方法”列中的唯一值数量
unique_method_count = df['特征提取方法'].nunique()

# 找出最常见的特征提取方法
most_common_method = df['特征提取方法'].mode()[0]

# 1. 绘制出现次数的柱状图并保存
plt.figure(figsize=(10, 6))
method_counts.plot(kind='bar', color='skyblue')
plt.title('特征提取方法的出现次数统计', fontsize=16)
plt.xlabel('特征提取方法', fontsize=14)
plt.ylabel('出现次数', fontsize=14)
output_image_1 = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\2.特征提取的方法的统计分析\特征提取方法_出现次数统计.png'
plt.tight_layout()
plt.savefig(output_image_1)
plt.close()  # 关闭图表

# 2. 绘制唯一值数量图并保存
plt.figure(figsize=(10, 6))
plt.text(0.5, 0.5, f'唯一特征提取方法种类数量: {unique_method_count}',
         fontsize=16, ha='center', va='center', bbox=dict(facecolor='orange', alpha=0.5))
plt.title('唯一特征提取方法种类数量', fontsize=16)
plt.axis('off')  # 关闭坐标轴
output_image_2 = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\2.特征提取的方法的统计分析\特征提取方法_唯一值数量.png'
plt.tight_layout()
plt.savefig(output_image_2)
plt.close()  # 关闭图表

# 3. 绘制最常见的特征提取方法图并保存
plt.figure(figsize=(10, 6))
plt.text(0.5, 0.5, f'最常见的特征提取方法: {most_common_method}',
         fontsize=16, ha='center', va='center', bbox=dict(facecolor='lightgreen', alpha=0.5))
plt.title('最常见的特征提取方法', fontsize=16)
plt.axis('off')  # 关闭坐标轴
output_image_3 = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\2.特征提取的方法的统计分析\特征提取方法_最常见方法.png'
plt.tight_layout()
plt.savefig(output_image_3)
plt.close()  # 关闭图表

print(f"三个图表已分别保存到指定路径：\n1. {output_image_1}\n2. {output_image_2}\n3. {output_image_3}")
