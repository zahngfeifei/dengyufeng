import pandas as pd

# 读取CSV文件
csv_file = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\数据预处理版本二分类数据信息.csv'
df = pd.read_csv(csv_file)

# 只保留“运动想象动作”列
df_motion_imagery = df[['运动想象动作']]

# 保存为新的CSV文件
output_file = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\运动想象动作数据.csv'
df_motion_imagery.to_csv(output_file, index=False)

print(f"已保留运动想象动作相关列，并保存为：{output_file}")
