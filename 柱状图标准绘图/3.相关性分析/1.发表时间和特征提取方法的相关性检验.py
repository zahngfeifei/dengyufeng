import pandas as pd
from sklearn.preprocessing import LabelEncoder
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei'] # 使用黑体
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
# 1. 加载CSV文件
file_path = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\数据预处理版本二分类数据信息.csv'
df = pd.read_csv(file_path)

# 2. 数据预处理
# 检查并处理缺失值
df['发表时间'].fillna(df['发表时间'].mode()[0], inplace=True)  # 使用众数填充缺失值

# 将“发表时间”转换为数值（去掉“年”字，转换为整数）
df['发表时间'] = df['发表时间'].str.replace('年', '').astype(int)

# 对“特征提取方法”进行编码（用于相关性分析，但绘图时不使用编码）
label_encoder = LabelEncoder()
df['特征提取方法编码'] = label_encoder.fit_transform(df['特征提取方法'].fillna('未知'))  # 填充空缺值为“未知”

# 3. 相关性检验（使用卡方检验）
# 创建交叉表
contingency_table = pd.crosstab(df['发表时间'], df['特征提取方法'])  # 使用特征提取方法的名称

# 计算卡方检验的统计量和p值
chi2, p, dof, ex = chi2_contingency(contingency_table)

# 输出结果
print(f"卡方统计量: {chi2}")
print(f"p值: {p}")
if p < 0.05:
    print("结论: 存在显著相关性")
else:
    print("结论: 没有显著相关性")

# 4. 绘制统计图
plt.figure(figsize=(16, 10))  # 增加画布的宽度和高度
sns.heatmap(contingency_table, annot=True, cmap='Blues', fmt='g')
plt.title('发表时间与特征提取方法的交叉表热力图')
plt.xlabel('特征提取方法')
plt.ylabel('发表时间')

# 旋转横轴的标签，防止文字被截断
plt.xticks(rotation=45, ha='right')

# 保存统计图到指定路径
save_path = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\3.相关性分析'
if not os.path.exists(save_path):
    os.makedirs(save_path)  # 如果目录不存在，创建目录

plt.tight_layout()  # 自动调整布局，防止文字重叠
plt.savefig(os.path.join(save_path, '相关性分析热力图_具体方法_优化.png'))
plt.show()
